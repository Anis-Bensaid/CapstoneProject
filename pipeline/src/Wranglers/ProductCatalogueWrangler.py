import pandas as pd

import ntpath
from typing import List


class ProductCatalogueWrangler:
    """
    Wrangles the Product Catalogue files.
    """
    def __init__(self, paths_file_types) -> None:
        """
        Initializes a new instance of ProductCatalogueWrangler.

        :param List[(str, str)] paths_file_types: list of tuples. Each tuple contains the paths to a product catalogue
        file and the type of the file (Cosmetics, Skincare).
        """
        self.paths_file_types = paths_file_types
        self.products = pd.DataFrame()
        self.cols = ['type',
                     'source_product_identifier',
                     'channel',
                     'product',
                     'brand_id',
                     'elc_brand',
                     'item_description',
                     'itemid_4',
                     # 'major_category_id',
                     'major_category',
                     # 'application_id',
                     'application',
                     # 'category_id',
                     'category',
                     # 'sub_category_id',
                     'sub_category']
        self.read_and_concatenate()
        self.wrangle()

    def read_and_concatenate(self) -> None:
        """
        Reads and concatenates all the selected files.
        """
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
                self.products = pd.concat([self.products, temp], ignore_index=True)

    def wrangle(self):
        """
        Drops missing data.
        """
        self.products.dropna(inplace=True)

    def get_product_catalogue(self):
        """
        Returns the products catalogue.

        :return: pd.DataFrame: products catalogue.
        """
        return self.products
