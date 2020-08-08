from src.Wranglers.ReviewsWrangler import *
from src.Utilis.GUI import *

if __name__ == '__main__':
    root = Tk()
    my_gui = GUI(root)
    root.mainloop()
    month = my_gui.month
    year = my_gui.year
    reviews_paths_file_types = my_gui.reviews_paths_file_types
    products_paths_files_types = my_gui.products_paths_files_types
    reviews_wrangler = ReviewsWrangler(reviews_paths_file_types, products_paths_files_types)



