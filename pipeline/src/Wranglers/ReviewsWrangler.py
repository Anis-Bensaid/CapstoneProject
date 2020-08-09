from typing import List

import numpy as np
import tqdm

from src.Utilis.NLPreprocessor import *
from src.Wranglers.ProductCatalogueWrangler import *
from src.Wranglers.TopicModeller import *


class ReviewsWrangler:
    """
    Wrangles the Signals data.

    Performs the following steps:
        1. Reads and concatenates all the selected files.
        2. Performs feature engineering on the reviews dataset
        3. Merges the reviews with the product catalogue
        4. Performs NLP Pre-processing
        5. Applies Topic Modeling
        6. Aggregates date
    """

    def __init__(self, reviews_paths_file_types: List[(str, str)], products_paths_file_types: List[(str, str)]) -> None:
        """
        Initializes an instance of Reviews Wrangler.

        :param List[(str, str)] reviews_paths_file_types: list of tuples. Each tuple contains the paths to a review
        file and the type of the file (Cosmetics, Skincare).
        :param List[(str, str)] products_paths_file_types: list of tuples. Each tuple contains the paths to a product
        catalogue file and the type of the file (Cosmetics, Skincare).
        """
        self.reviews_paths_file_types = reviews_paths_file_types
        self.products_paths_file_types = products_paths_file_types

        # Initializes a ProductCatalogueWrangler which contains the ELC product catalogue for the reviews
        self.product_wrangler = ProductCatalogueWrangler(self.products_paths_file_types)
        # Initializes an NLPreprocessor which will be used to get the pre-preprocess the reviews before LDA
        self.preprocessor = NLPreprocessor()
        # Initializes a TopicModeller which contains the pre-trained Gensim LDA models
        self.topic_modeller = TopicModeller()

        self.reviews = pd.DataFrame()
        # Important columns
        self.cols = ['type',
                     'onlinepost_id',
                     'source_product_identifier',
                     'onlinestatement_id',
                     'review_date',
                     'description',
                     'geography',
                     'channel',
                     'rating',
                     'sentiment']

        # Performs all the steps at initialization
        self.read_and_concatenate()
        self.wrangle()
        self.add_product_catalogue()
        self.get_tokens()
        self.add_topics()
        self.aggregate_by_subcategories()

    def read_and_concatenate(self) -> None:
        """
        Reads and concatenates all the selected files.
        """
        for path_file_type in self.reviews_paths_file_types:
            path, file_type = path_file_type
            file_name = ntpath.basename(path)
            if '.csv' in path.lower():
                print(f'\nReading {file_name}...')
                temp = pd.read_csv(path, low_memory=False)
                temp['type'] = file_type
                # Code friendly column names
                temp.columns = [colname.lower().replace(' ', '_') for colname in temp.columns]
                temp = temp[self.cols]
                print('Concatenating', file_name)
                self.reviews = pd.concat([self.reviews, temp], ignore_index=True)

    def wrangle(self) -> None:
        """
        Wrangles the ratings and reviews data.
        """
        # Filter on USA
        self.reviews = self.reviews[self.reviews['geography'] == 'USA']

        # Creating date columns in the right dtype and dropping the day of the date: 2019-02-24 => 2019-02-01
        self.reviews.loc[:, 'date'] = pd.to_datetime(self.reviews['review_date'], errors='coerce')
        if self.reviews['date'].isna().sum() > 0:
            print('{} rows have been dropped because the date format is wrong.'.format(
                self.reviews['date'].isna().sum()))
            self.reviews = self.reviews.dropna(subset='date')
        self.reviews['date'] = self.reviews['date'].dt.to_period('m')

        # Checking for missing data (NA => -1)
        if self.reviews['rating'].isna().sum() > 0:
            print('{} rows are missing ratings'.format(self.reviews['rating'].isna().sum()))
            self.reviews.loc[:, 'rating'] = self.reviews['rating'].fillna(-1).astype(int)

        if self.reviews['sentiment'].isna().sum() > 0:
            print('{} rows are missing sentiments'.format(self.reviews['sentiment'].isna().sum()))
            self.reviews.loc[:, 'sentiment'] = self.reviews['sentiment'].fillna(-1).astype(int)

        # Transforming rating and sentiment to dummy variables (one-hot encoding)
        self.reviews.loc[:, 'sentiment'] = self.reviews['sentiment'].str.lower()
        self.reviews.loc[:, 'rating'] = self.reviews['rating'].astype(int)
        self.reviews = pd.concat([self.reviews,
                                  pd.get_dummies(data=self.reviews[['rating', 'sentiment']],
                                                 columns=['rating', 'sentiment'],
                                                 dtype=int)], axis=1)

        # Readding NAs data to ratings
        self.reviews.loc[self.reviews['rating'] == -1, 'rating'] = np.nan
        self.reviews.loc[self.reviews['sentiment'] == -1, 'sentiment'] = np.nan

        # Transforming sentiment to integer data (positive:1; netural:0, negative:-1)
        self.reviews.loc[:, 'sentiment'] = self.reviews['sentiment_positive'] - self.reviews['sentiment_negative']

        # Creating a column to count the number of statements by review once aggreagtion happens
        self.reviews['nb_statements'] = self.reviews['sentiment']

        # Aggregating RR data by OnlinePost_ID
        self.reviews = self.reviews.groupby(['type',
                                             'channel',
                                             'source_product_identifier',
                                             'date',
                                             'onlinepost_id']).agg({'description': lambda x: '. '.join(list(x)),
                                                                    'nb_statements': 'count',
                                                                    'rating': 'first',
                                                                    'rating_1': 'first',
                                                                    'rating_2': 'first',
                                                                    'rating_3': 'first',
                                                                    'rating_4': 'first',
                                                                    'rating_5': 'first',
                                                                    'sentiment_negative': 'sum',
                                                                    'sentiment_neutral': 'sum',
                                                                    'sentiment_positive': 'sum',
                                                                    'sentiment': 'mean'
                                                                    }).reset_index()

        # Normalize the one hot sentiment encoding counts (sentiment_negative, sentiment_neutral, sentiment_positive)
        # by the nb_statement.
        self.reviews[['sentiment_negative', 'sentiment_neutral', 'sentiment_positive']] = self.reviews[
            ['sentiment_negative', 'sentiment_neutral', 'sentiment_positive']].div(self.reviews['nb_statements'],
                                                                                   axis=0)

    def add_product_catalogue(self) -> None:
        """
        Merges the Ratings and Reviews file with the Product Catalogue.
        """
        self.reviews = self.reviews.merge(self.product_wrangler.get_product_catalogue())

    def get_tokens(self) -> None:
        """
        Performs NLP pre-processing.
        """
        print('\nPre-processing the reviews...')
        self.reviews['tokens'] = list(
            tqdm.tqdm(self.preprocessor.preprocess(self.reviews['description'].values.tolist()),
                      position=0,
                      leave=True,
                      total=len(self.reviews)))

    def add_topics(self) -> None:
        """
        Adds topics to each of the reviews.
        """
        print('\nAdding topics to the reviews...')
        self.reviews = self.topic_modeller.add_topics(reviews=self.reviews)

    def aggregate_by_subcategories(self) -> None:
        """
        Aggregates Ratings and Reviews by subcategories.
        """
        print("\nAggregating by sub-categories...")
        # Creating a column to count the number of self.reviews once aggreagtion happens
        self.reviews['nb_reviews'] = self.reviews['rating']
        self.reviews['avg_nb_statements'] = self.reviews['nb_statements']

        self.reviews = self.reviews.groupby(['type',
                                             'product',
                                             'brand_id',
                                             'elc_brand',
                                             'item_description',
                                             'itemid_4',
                                             'major_category',
                                             'application',
                                             'category',
                                             'sub_category',
                                             'date']).agg({'avg_nb_statements': 'mean',
                                                           'nb_reviews': 'count',
                                                           'rating': 'mean',
                                                           'rating_1': 'sum',
                                                           'rating_2': 'sum',
                                                           'rating_3': 'sum',
                                                           'rating_4': 'sum',
                                                           'rating_5': 'sum',
                                                           'sentiment': 'mean',
                                                           'sentiment_negative': 'sum',
                                                           'sentiment_neutral': 'sum',
                                                           'sentiment_positive': 'sum',
                                                           'topic_1': 'sum',
                                                           'topic_2': 'sum',
                                                           'topic_3': 'sum',
                                                           'topic_4': 'sum',
                                                           }).reset_index()
