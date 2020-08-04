from src.Utilis.NLPreprocessor import *
from src.Wranglers.TopicModeller import *
from src.Wranglers.ProductCatalogueWrangler import *

import pandas as pd
import numpy as np
import ntpath
import tqdm

prod_paths_file_types = [('../data/Cosmetics_Product_20200116_w_SAP.csv', 'Cosmetics'),
                         ('../data/products_cosmetics_w_SAP.csv', 'Cosmetics')]
rev_paths_file_types = [('../data/cosmetics_reviews_20200101-20200131_processed.csv', 'Cosmetics')]

# os.chdir('src')
preprocessor = NLPreprocessor()
topic_modeller = TopicModeller()
product_wrangler = ProductCatalogueWrangler(prod_paths_file_types)


class ReviewsWrangler:
    def __init__(self, paths_file_types):
        self.paths_file_types = paths_file_types
        self.reviews = pd.DataFrame()
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
        self.read_and_concatenate()
        self.wrangle()
        self.add_product_catalogue()
        self.get_tokens()
        self.add_topics()
        self.aggregate_by_subcategories()

    def read_and_concatenate(self):
        for path_file_type in self.paths_file_types:
            path, file_type = path_file_type
            file_name = ntpath.basename(path)
            if '.csv' in path.lower():
                print(f'\nReading {file_name}...')
                temp = pd.read_csv(path, low_memory=False)
                temp['type'] = file_type
                temp.columns = [colname.lower().replace(' ', '_') for colname in temp.columns]
                temp = temp[self.cols]
                print('Concatenating', path)
                self.reviews = pd.concat([self.reviews, temp], ignore_index=True)

    def wrangle(self):
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

        # Aggregating RR data by OnlinePost_ID

        # Creating a column to count the number of statements by review once aggreagtion happens
        self.reviews['nb_statements'] = self.reviews['sentiment']

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

        # Normalize the one hot sentiment encoding counts (sentiment_negative, sentiment_neutral, sentiment_positive) by the nb_statement.
        self.reviews[['sentiment_negative', 'sentiment_neutral', 'sentiment_positive']] = self.reviews[
            ['sentiment_negative', 'sentiment_neutral', 'sentiment_positive']].div(self.reviews['nb_statements'],
                                                                                   axis=0)

    def add_product_catalogue(self):
        self.reviews = self.reviews.merge(product_wrangler.get_product_catalogue())

    def get_tokens(self):
        self.reviews['tokens'] = list(tqdm.tqdm(preprocessor.preprocess(self.reviews['description'].values.tolist()),
                                                position=0,
                                                leave=True,
                                                total=len(self.reviews)))

    def add_topics(self):
        self.reviews = topic_modeller.add_topics(reviews=self.reviews)

    def aggregate_by_subcategories(self):
        # Aggregating RR data by channel + source_product_identifier

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
                                                           }).reset_index()
