from Predicter import *

#data is ready to be applied in ml purpose
if __name__ == "__main__":
    optimize = Prediction()
    data = pd.read_excel(os.path.join(path_to_DataPostCleaning, "data3.xlsx"))
    optimize.optimize_prediction_runner(data)

