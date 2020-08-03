import pandas as pd
from OutputBuilders.ExcelBuilder import ExcelBuilder

if __name__ == '__main__':
    ##test data to make sure everything works
    test = pd.read_csv("C:/Users/cfowle/The Estée Lauder Companies Inc/TeamAnis - General/Data/LDA Results/makeup_eyes_asymmetric_symmetric_4.csv")
    
    eb = ExcelBuilder(test)
    eb.export()