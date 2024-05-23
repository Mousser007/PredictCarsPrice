import tkinter as tk
from tkinter import ttk
import os
import pandas as pd
from ML.Predicter import Prediction
import joblib
from Config import *

data = pd.read_excel(os.path.join(path_to_DataPourSimulateur,"DataForSimulateur.xlsx"))
df = pd.read_excel(os.path.join(path_to_DataPostCleaning,"data3.xlsx"))
MarqueList = data.Marque.drop_duplicates().tolist()
ModeleList = data.Modele.drop_duplicates().tolist()
CouleurList = df.Couleur.drop_duplicates().tolist()
CarrosserieList = df.Carrosserie.drop_duplicates().tolist()
EnergieList = data.Energie.drop_duplicates().tolist()
BoiteVitesseList = data.BoiteVitesse.drop_duplicates().tolist()

def reset_fields():
    dropdown1.set('')
    dropdown2.set('')
    dropdown3.delete(0, 'end')
    dropdown4.delete(0, 'end')
    dropdown5.set('')
    dropdown6.delete(0, 'end')
    dropdown7.set('')
    dropdown8.set('')
    dropdown9.set('')
    calculation_result.config(text="Calculation result will appear here", anchor="center", font=("Arial", 12, "bold"))
def get_caracteristique():
    marque = dropdown1.get()
    modele = dropdown2.get()
    kilometrage = int(dropdown3.get())
    puissanceFiscale = int(dropdown4.get())
    boiteVitesse = dropdown5.get()
    annee = int(dropdown6.get())
    energie = dropdown7.get()
    test = Prediction()
    imputValuesForLabeling = {'Energie': energie,
                    'BoiteVitesse': boiteVitesse,
                    'Modele': modele,
                    'Marque': marque
                    }
    dataframe = test.preprocess_input(imputValuesForLabeling)
    dataframe['PuissanceFiscale'] = puissanceFiscale
    dataframe['Annee'] = annee
    dataframe['Kilometrage'] = kilometrage
    dataframe['Kilometrage_par_Annee'] = (dataframe['Kilometrage'] / (2024 - dataframe['Annee'])).astype(int)
    dataframe = dataframe[['Energie', 'Annee', 'Kilometrage', 'PuissanceFiscale', 'BoiteVitesse', 'Marque', 'Modele',
                           'Kilometrage_par_Annee']]
    prediction = test.make_prediction(dataframe)
    predDataframe = pd.DataFrame({"PrixNormalisé": prediction})
    scaler = joblib.load('D:\\PredictCarsPrice\\ML\\RequirementsFiles\\scaler.joblib')
    prix = scaler.inverse_transform(predDataframe.PrixNormalisé.to_numpy().reshape(-1, 1))
    resultat = int((prix[0])[0])
    calculation_result.config(text=str(resultat) + " dt")
    print(prix)



def update_modele_options(event):
    # Récupérer la marque sélectionnée
    marque = dropdown1.get()
    # Mettre à jour les options du deuxième dropdown en fonction de la marque sélectionnée
    modele_options = data.loc[(data["Marque"] == marque, "Modele")].drop_duplicates().to_list()
    dropdown2['values'] = modele_options


# Create main application window
root = tk.Tk()
root.title("Estimateur prix voiture")

# Create dropdowns


dropdown1_label = ttk.Label(root, text="Marque:")
dropdown1_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")
dropdown1 = ttk.Combobox(root, values=MarqueList)
dropdown1.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
dropdown1.bind("<<ComboboxSelected>>", update_modele_options)

dropdown2_label = ttk.Label(root, text="Modele:")
dropdown2_label.grid(row=1, column=0, padx=5, pady=5, sticky="w")
dropdown2 = ttk.Combobox(root)
dropdown2.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

dropdown3_label = ttk.Label(root, text="Kilometrage:")
dropdown3_label.grid(row=2, column=0, padx=5, pady=5, sticky="w")
dropdown3 = ttk.Entry(root)
dropdown3.grid(row=2, column=1, padx=5, pady=5, sticky="ew")

dropdown4_label = ttk.Label(root, text="PuissanceFiscale:")
dropdown4_label.grid(row=3, column=0, padx=5, pady=5, sticky="w")
dropdown4 = ttk.Entry(root)
dropdown4.grid(row=3, column=1, padx=5, pady=5, sticky="ew")

dropdown5_label = ttk.Label(root, text="BoiteVitesse:")
dropdown5_label.grid(row=4, column=0, padx=5, pady=5, sticky="w")
dropdown5 = ttk.Combobox(root, values=["AUTOMATIQUE", "MANUELLE"])
dropdown5.grid(row=4, column=1, padx=5, pady=5, sticky="ew")

dropdown6_label = ttk.Label(root, text="Annee:")
dropdown6_label.grid(row=5, column=0, padx=5, pady=5, sticky="w")
dropdown6 = ttk.Entry(root)
dropdown6.grid(row=5, column=1, padx=5, pady=5, sticky="ew")

dropdown7_label = ttk.Label(root, text="Energie:")
dropdown7_label.grid(row=6, column=0, padx=5, pady=5, sticky="w")
dropdown7 = ttk.Combobox(root, values=EnergieList)
dropdown7.grid(row=6, column=1, padx=5, pady=5, sticky="ew")

dropdown8_label = ttk.Label(root, text="Carrosserie:")
dropdown8_label.grid(row=7, column=0, padx=5, pady=5, sticky="w")
dropdown8 = ttk.Combobox(root, values=CarrosserieList)
dropdown8.grid(row=7, column=1, padx=5, pady=5, sticky="ew")

dropdown9_label = ttk.Label(root, text="Couleur:")
dropdown9_label.grid(row=8, column=0, padx=5, pady=5, sticky="w")
dropdown9 = ttk.Combobox(root, values=CouleurList)
dropdown9.grid(row=8, column=1, padx=5, pady=5, sticky="ew")


# Create button to trigger reset
reset_button = ttk.Button(root, text="Reset", command=reset_fields)
reset_button.grid(row=9, column=2, padx=5, pady=5, sticky="ew")
# Create scroll
scrollbar = ttk.Scrollbar(root)
scrollbar.grid(row=0, column=3, rowspan=9, sticky="ns")

# Create button to trigger calculation
calculate_button = ttk.Button(root, text="Calculate", command=get_caracteristique)
calculate_button.grid(row=9, column=0, columnspan=2, padx=5, pady=5, sticky="ew")

# Create space for calculation result
calculation_result = ttk.Label(root, text="Calculation result will appear here", anchor="center", font=("Arial", 12, "bold"))
calculation_result.grid(row=10, columnspan=2, padx=5, pady=5, sticky="ew")

# Configure resizing behavior
root.columnconfigure(0, weight=1)
root.columnconfigure(1, weight=1)
root.rowconfigure(4, weight=1)

root.mainloop()
