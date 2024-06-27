from Predicter import *
import pandas as pd
from Cleaning import Cleaner

if __name__ == "__main__":
    optimize = Prediction()
    cln = Cleaner.cleaner()
    data = pd.read_sql('DataCleaned', con=engine)
    data = data.drop(columns=['id'])
    data = cln.eliminate_unnamed_columns(data)
    optimize.optimize_prediction_runner(data)

