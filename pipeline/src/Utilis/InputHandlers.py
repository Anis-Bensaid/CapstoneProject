import pandas as pd

import os, sys
os.chdir(os.getcwd() + '/src/Utilis')
sys.path.append(os.getcwd())

class InputHandler:
    def __init__(self):
        self.topics_model_path = None
        self.ratings_paths = None
        self.products_paths = None

    def get_gensim_models(self, path):
        

    def get_reviews(self, path):
        reviews = pd.read_csv('../../data/cosmetics_reviews_20200101-20200131_processed.csv', low_memory=False)


reviews = pd.read_csv('../../data/cosmetics_reviews_20200101-20200131_processed.csv', low_memory=False)
products = pd.read_csv('../../data/Cosmetics_Product_20200116_w_SAP.csv', low_memory=False)

m = reviews.merge(products, left_on=['Source_Product_Identifier', 'Channel'], right_on=['Source_Product_Identifier', 'Channel'])

