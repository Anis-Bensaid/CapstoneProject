from src.Wranglers.ReviewsWrangler import *
from src.Utilis.GUI import *

if __name__ == '__main__':
    # Creates the GUI
    root = Tk()
    my_gui = GUI(root)
    # Run the GUI
    root.mainloop()
    # Get inputs from the GUI
    month = my_gui.month
    year = my_gui.year
    reviews_paths_file_types = my_gui.reviews_paths
    products_paths_files_types = my_gui.product_paths
    # Wrangle Ratings and Reviews
    reviews_wrangler = ReviewsWrangler(reviews_paths_file_types, products_paths_files_types)
    # Get the wrangled data
    reviews = reviews_wrangler.reviews
    print(reviews)


