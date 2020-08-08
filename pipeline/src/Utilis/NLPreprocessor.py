from collections import Counter

import nltk
import pandas as pd
import spacy
from gensim.utils import simple_preprocess
from nltk.corpus import stopwords

nltk.download('stopwords')

PATH_TO_BRAND = r'../data/elc_brands.csv'
PATH_TO_CATALOGUE = r'../data/elc_catalogue.csv'


class NLPreprocessor:
    def __init__(self):
        self.stop_words = None
        self.get_stop_words()

    def get_stop_words(self):
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

    def preprocess(self, sentences, allowed_postags=['NOUN', 'ADJ', 'VERB', 'ADV']):
        nlp = spacy.load("en_core_web_sm", disable=['parser', 'ner'])
        for sentence in sentences:
            doc = nlp(' '.join([token for token in simple_preprocess(str(sentence), deacc=True)]))
            yield ([token.lemma_ for token in doc if
                    (token.pos_ in allowed_postags) and (not (token.lemma_ in self.stop_words))])
