import datetime
import os.path
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
import matplotlib.pyplot as plt
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import mean_squared_error
import joblib
from sklearn.preprocessing import MinMaxScaler
from xgboost import XGBRegressor
from Config import *
from Cleaning.Cleaner import cleaner


class datapreparation:

    def __init__(self) -> None:
        pass

    def extraire_top_car_per_column_name(self,dataframe,columnName,n):
        category_counts = dataframe[columnName].value_counts().to_dict()
        column = list(category_counts.keys())
        filtered_category_counts = {column: count for column, count in category_counts.items() if count > n}
        column = list(filtered_category_counts.keys())
        dataexp = dataframe.loc[dataframe[columnName].isin(column),:]
        cln = cleaner()
        dataexp = cln.eliminate_unnamed_columns(dataexp)
        return dataexp

    def remove_outliers(self, group, min_value, max_value):
        lower_bound = group['Prix'].quantile(min_value)
        upper_bound = group['Prix'].quantile(max_value)
        return group[(group['Prix'] >= lower_bound) & (group['Prix'] <= upper_bound)]

    def Boxplot_figure(self, dataframe):
        plt.figure(figsize=(20, 6))
        dataframe.boxplot(column=["Prix"],by="Marque")
        plt.ylabel('Valeurs')
        # plt.show()
        plt.xticks(rotation=90);

class Prediction:

    def __init__(self) -> None:
        pass

    def apply_label_encoder(self, dataframe, ListOfcolumnsToDrop, targetColumnName):
        output_values = dataframe[targetColumnName]
        input_values = dataframe.drop(columns=ListOfcolumnsToDrop)
        dict={}
        filePath = os.path.join(path_to_RequirementsFiles, "label_encoder")
        # Apply label encoding to each column
        for col in input_values.columns:
            if input_values[col].dtype == 'object':  # Check if the column contains strings
                label_encoder = joblib.load(filePath + col + '.pkl')
                input_values[col] = label_encoder.fit_transform(input_values[col])
                dict[col] = label_encoder
        return input_values, output_values, dict
    
    def label_encoder_columns(self,dataframe, ListOfcolumnsToDrop, targetColumnName):
        # Initialize LabelEncoder 
        output_values = dataframe[targetColumnName]
        input_values = dataframe.drop(columns=ListOfcolumnsToDrop)
        dict={}
        # Apply label encoding to each column
        for col in input_values.columns:
            if input_values[col].dtype == 'object':  # Check if the column contains strings
                label_encoder = LabelEncoder()
                input_values[col] = label_encoder.fit_transform(input_values[col])
                dict[col] = label_encoder
        return input_values, output_values, dict
    
    def train_test_split(self,input_values, output_values):
        X_train, X_test, y_train, y_test = train_test_split(input_values, output_values, test_size=0.2, random_state=42)
        return X_train, X_test, y_train, y_test
    
    def predict_algo(self, X_train, y_train, X_test, y_test, regressor):
        regressor.fit(X_train, y_train)
        # Make predictions on the testing data
        y_pred = regressor.predict(X_test)
        # Calculate mean squared error
        mse = mean_squared_error(y_test, y_pred)
        # print("Mean Squared Error:", mse)
        X_test["Target"] = y_test
        X_test["Prediction"] = y_pred
        X_test["AbsError"] = np.abs(y_test-y_pred)
        mae = np.mean(X_test["AbsError"])
        # print("Mean Absolute Error:", mae)
        return X_test,mse,mae, regressor

    def eliminer_les_valeur_null(self, dataframe):
        dataframe = dataframe.loc[dataframe.Kilometrage != 0]
        dataframe = dataframe.loc[dataframe.Annee != 0]
        dataframe = dataframe.loc[dataframe.PuissanceFiscale != 0]
        dataframe = dataframe.loc[dataframe.Prix != 0]
        dataframe = dataframe.loc[dataframe['Annee'] != 2024]
        return dataframe
    
    def eliminer_les_marque_luxe(self, dataframe):
        dataframe =dataframe.loc[(dataframe.Marque != "PORSCHE") &
                                 (dataframe.Marque != "MINI") &
                                 (dataframe.Marque != "LAND ROVER") &
                                 (dataframe.Marque != "JAGUAR") &
                                 (dataframe.Marque != "JEEP")]
        return dataframe
    
    def optimize_prediction_runner(self, data):
        data = self.eliminer_les_valeur_null(data)
        data = self.eliminer_les_marque_luxe(data)
        data = data.drop(columns={"Couleur", "Carrosserie"})
        data = data.loc[(data.Modele != "GOLF") & (data.Modele != "POLO") & (data.Modele != "CLIO")]
        data['Kilometrage_par_Annee'] = (data['Kilometrage'] / (2024 - data['Annee'])).astype(int)
        regressor = XGBRegressor(max_depth=5, n_estimators=700, eta=0.09999)
        prepare = datapreparation()
        data = prepare.extraire_top_car_per_column_name(data, "Marque", 15)
        data = prepare.extraire_top_car_per_column_name(data, "Modele", 6)
        data = data.groupby('Marque').apply(prepare.remove_outliers, min_value=0.01, max_value=0.98).reset_index(drop= True)
        scaler = MinMaxScaler()
        data['Prix_normalisé'] = scaler.fit_transform(data[['Prix']])
        joblib.dump(scaler, os.path.join(path_to_RequirementsFiles, "scaler.joblib"))
        listOfColumnToDrop = ["Prix", "Prix_normalisé"]
        targetColumnName = "Prix_normalisé"
        inputValue, outputValue, dict = self.label_encoder_columns(data, listOfColumnToDrop, targetColumnName)
        for key, value in dict.items():
            joblib.dump(value, os.path.join(path_to_RequirementsFiles, ('label_encoder' + key + '.pkl')))
        X_train, X_test, y_train, y_test = self.train_test_split(inputValue, outputValue)
        predictedDf, mse, mae, trainedRegressor = self.predict_algo(X_train, y_train, X_test, y_test, regressor)
        joblib.dump(trainedRegressor, os.path.join(path_to_RequirementsFiles, "modele_xgboost.pkl"))
        return ("Mise à jours du modéle avec succées")

    # "Date du mise à jour du modele: ", datetime.datetime.now() + "/n" +
    # "Mean squarred error:",mse
    # "Mean absolute error:",mae

    def preprocess_input(self, input_values):
        df = pd.DataFrame([input_values])
        filePath = os.path.join(path_to_RequirementsFiles, "label_encoder")
        for col in df.columns:
            label_encoder = joblib.load(filePath + col + '.pkl')
            df[col] = label_encoder.transform(df[col])
        return df
    
    def make_prediction(self, input_values):
        filePath = os.path.join(path_to_RequirementsFiles, "modele_xgboost.pkl")
        model = joblib.load(filePath)
        prediction = model.predict(input_values)
        return prediction
    

if __name__ == "__main__":
    pass
