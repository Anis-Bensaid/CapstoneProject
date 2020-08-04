import pandas as pd
import ntpath


class ProductCatalogueWrangler:
    def __init__(self, paths_file_types):
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
                self.products = pd.concat([self.products, temp], ignore_index=True)

    def get_product_catalogues(self):
        self.read_and_concatenate()
        return self.products
