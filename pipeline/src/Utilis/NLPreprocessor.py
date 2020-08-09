import pandas as pd

from collections import Counter

import nltk
import spacy
from gensim.utils import simple_preprocess
from nltk.corpus import stopwords

nltk.download('stopwords')

PATH_TO_BRAND = r'../data/elc_brands.csv'
PATH_TO_CATALOGUE = r'../data/elc_catalogue.csv'


class NLPreprocessor:
    """
    Class that does all of the NLP pre-processing on the reviews.
    """
    def __init__(self) -> None:
        """
        Initializes a new instance of NLPreprocessor.
        """
        self.stop_words = None
        self.get_stop_words()

    def get_stop_words(self) -> None:
        """
        Updates the attribute stop_words.

        This function adds the Brands, Categories, Applications, Category and
        Subcategories to the stop words. Consequently, all of these words won't be featured in the pre-processed
        reviews. Our final goal is to apply Topic Modeling on the reviews, and we don't want to get topics on the
        type of product that the reviews are about. Instead, we want topics about customer sentiment and satisfaction
        or about

        :return Counter self.stop_words: a hashtable (Counter) containing the stopwords.
        """
        # Adding product related words to the stop words
        self.stop_words = stopwords.words('english')
        self.stop_words.extend(['from'])

        brands = pd.read_csv(PATH_TO_BRAND, encoding='ISO-8859-1')
        catalogue = pd.read_csv(PATH_TO_CATALOGUE, encoding='ISO-8859-1')

        self.stop_words.extend(list(set(str(w).lower() for w in ' '.join(brands['ELC_Brand'].unique().tolist() +
                                                                         catalogue['Major_Category'].unique().tolist() +
                                                                         catalogue['Application'].unique().tolist() +
                                                                         catalogue['Category'].unique().tolist() +
                                                                         catalogue['SubCategory'].unique().tolist()
                                                                         ).replace('/', ' ').split())))

        # Initialize spacy 'en' model, keeping only tagger component (for efficiency)
        nlp = spacy.load("en_core_web_sm", disable=['parser', 'ner'])
        stop_words_nlp = nlp(
            ' '.join([' '.join(simple_preprocess(str(word), deacc=True)) for word in self.stop_words]))
        self.stop_words = [token.lemma_ for token in stop_words_nlp]

        # Cache self.stop_words into hash
        self.stop_words = Counter(self.stop_words)
        return self.stop_words

    def preprocess(self, sentences, allowed_postags=['NOUN', 'ADJ', 'VERB', 'ADV']):
        nlp = spacy.load("en_core_web_sm", disable=['parser', 'ner'])
        for sentence in sentences:
            doc = nlp(' '.join([token for token in simple_preprocess(str(sentence), deacc=True)]))
            yield ([token.lemma_ for token in doc if
                    (token.pos_ in allowed_postags) and (not (token.lemma_ in self.stop_words))])
