from src.Wranglers.ReviewsWrangler import *

if __name__ == '__main__':
    rev_paths_file_types = [('../data/cosmetics_reviews_20200101-20200131_processed.csv', 'Cosmetics')]
    rw=ReviewsWrangler(rev_paths_file_types)
    r = rw.reviews