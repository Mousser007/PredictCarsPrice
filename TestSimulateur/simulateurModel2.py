import os
import os
os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = 'C:\\Users\\Mousser\\anaconda3\\Lib\\site-packages\\PySide2\\plugins\\platforms'
from PySide2.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton, QComboBox, QLineEdit, QVBoxLayout, QWidget
from PySide2.QtCore import Slot
import os
import pandas as pd
from ML.Predicter import Prediction
import joblib

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setWindowTitle("Estimateur prix voiture")
        self.parent_directory = os.path.dirname(os.getcwd())
        self.path = os.path.join(self.parent_directory, "Data")
        self.data = pd.read_excel(os.path.join(self.path, "DataPourSimulateur\\DataForSimulateur.xlsx"))
        self.df = pd.read_excel(os.path.join(self.path, "DataPostCleaning\\data3.xlsx"))
        self.MarqueList = self.data.Marque.drop_duplicates().tolist()
        self.ModeleList = self.data.Modele.drop_duplicates().tolist()
        self.CouleurList = self.df.Couleur.drop_duplicates().tolist()
        self.CarrosserieList = self.df.Carrosserie.drop_duplicates().tolist()
        self.EnergieList = self.data.Energie.drop_duplicates().tolist()
        self.BoiteVitesseList = self.data.BoiteVitesse.drop_duplicates().tolist()

        self.init_ui()

    def init_ui(self):
        central_widget = QWidget()
        layout = QVBoxLayout()

        # Labels et widgets pour les champs de saisie
        self.dropdown1_label = QLabel("Marque:")
        layout.addWidget(self.dropdown1_label)
        self.dropdown1 = QComboBox()
        self.dropdown1.addItems(self.MarqueList)
        self.dropdown1.currentIndexChanged.connect(self.update_modele_options)
        layout.addWidget(self.dropdown1)

        self.dropdown2_label = QLabel("Modele:")
        layout.addWidget(self.dropdown2_label)
        self.dropdown2 = QComboBox()
        layout.addWidget(self.dropdown2)

        self.dropdown3_label = QLabel("Kilometrage:")
        layout.addWidget(self.dropdown3_label)
        self.dropdown3 = QLineEdit()
        layout.addWidget(self.dropdown3)

        self.dropdown4_label = QLabel("PuissanceFiscale:")
        layout.addWidget(self.dropdown4_label)
        self.dropdown4 = QLineEdit()
        layout.addWidget(self.dropdown4)

        self.dropdown5_label = QLabel("BoiteVitesse:")
        layout.addWidget(self.dropdown5_label)
        self.dropdown5 = QComboBox()
        self.dropdown5.addItems(["AUTOMATIQUE", "MANUELLE"])
        layout.addWidget(self.dropdown5)

        self.dropdown6_label = QLabel("Annee:")
        layout.addWidget(self.dropdown6_label)
        self.dropdown6 = QLineEdit()
        layout.addWidget(self.dropdown6)

        self.dropdown7_label = QLabel("Energie:")
        layout.addWidget(self.dropdown7_label)
        self.dropdown7 = QComboBox()
        self.dropdown7.addItems(self.EnergieList)
        layout.addWidget(self.dropdown7)

        self.dropdown8_label = QLabel("Carrosserie:")
        layout.addWidget(self.dropdown8_label)
        self.dropdown8 = QComboBox()
        self.dropdown8.addItems(self.CarrosserieList)
        layout.addWidget(self.dropdown8)

        self.dropdown9_label = QLabel("Couleur:")
        layout.addWidget(self.dropdown9_label)
        self.dropdown9 = QComboBox()
        self.dropdown9.addItems(self.CouleurList)
        layout.addWidget(self.dropdown9)

        # Boutons pour réinitialiser et calculer
        self.reset_button = QPushButton("Reset")
        self.reset_button.clicked.connect(self.reset_fields)
        layout.addWidget(self.reset_button)

        self.calculate_button = QPushButton("Calculate")
        self.calculate_button.clicked.connect(self.get_caracteristique)
        layout.addWidget(self.calculate_button)

        # Résultat du calcul
        self.calculation_result = QLabel("Calculation result will appear here", anchor="center", font=("Arial", 12, "bold"))
        layout.addWidget(self.calculation_result)

        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

    @Slot()
    def update_modele_options(self, index):
        # Récupérer la marque sélectionnée
        marque = self.dropdown1.currentText()
        # Filtrer les modèles en fonction de la marque sélectionnée
        modele_options = self.data.loc[self.data["Marque"] == marque, "Modele"].drop_duplicates().tolist()
        # Effacer et mettre à jour les options du deuxième dropdown
        self.dropdown2.clear()
        self.dropdown2.addItems(modele_options)

    @Slot()
    def reset_fields(self):
        # Réinitialiser tous les champs à leur état initial
        self.dropdown1.setCurrentIndex(-1)
        self.dropdown2.clear()
        self.dropdown3.clear()
        self.dropdown4.clear()
        self.dropdown5.setCurrentIndex(-1)
        self.dropdown6.clear()
        self.dropdown7.setCurrentIndex(-1)
        self.dropdown8.setCurrentIndex(-1)
        self.dropdown9.setCurrentIndex(-1)
        self.calculation_result.setText("Calculation result will appear here", anchor="center", font=("Arial", 12, "bold"))

    @Slot()
    def get_caracteristique(self):
        marque = self.dropdown1.currentText()
        modele = self.dropdown2.currentText()
        kilometrage = int(self.dropdown3.text())
        puissanceFiscale = int(self.dropdown4.text())
        boiteVitesse = self.dropdown5.currentText()
        annee = int(self.dropdown6.text())
        energie = self.dropdown7.currentText()
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
        self.calculation_result.setText(str(resultat) + " dt")

if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec_()

