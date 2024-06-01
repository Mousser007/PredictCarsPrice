from AffareScrapper import *
import os
import pandas as pd
from AutoMaxScrapper import *
from AutomobileTnScrapper import *
from AutoPlusScrapper import *
from AutoPrixScrapper import *
from TayaraScrapper import *
from FilesImport.fileImporter import *
from Cleaning.Cleaner import *
from FilesImport import fileImporter
from Config import *


class CleaningUseCars:
    def __init__(self):
        self.importer = fileImporter.Importer()
        self.cln = cleaner()

    # def testPipeline(self):
    #     # Nettoyage des données phase 1
    #     imp = Importer()
    #     ParentPath = os.path.dirname(os.getcwd())
    #     destination = os.path.join(ParentPath, 'Data', 'DataPostCleaning')
        # Affare
        # testAffare = ScrappOccasionAffareTn()
        # affarePostScrapping = pd.read_csv("C:\\Users\\Mousser\\Desktop\\PfeStarAssurance\\AffareTn\\AffareTnOcc.csv")
        # affarePostCleaning = testAffare.affare_columns_standardise(affarePostScrapping)
        # affarePostCleaning.to_excel(destination + '\\' + "affarePostCleaning.xlsx")
    #     # # AutoMax
    #     # testAutomax = ScrappOccasionAutoMaxTn()
    #     # automaxPostScrapping = pd.read_excel("C:\\Users\\Mousser\\Desktop\\PfeStarAssurance\\AutoMaxTn\\AutoMaxTnOcc.xlsx")
    #     # automaxPostCleaning = testAutomax.auto_max_columns_standardise(automaxPostScrapping)
    #     # automaxPostCleaning.to_excel(destination +'\\' + "automaxPostCleaning.xlsx")
    #     # # AutomobileTn
    #     # testAutomobileTn = ScrapperAutomobileTnOcc()
    #     # automobileTnPostScrapping = pd.read_csv("C:\\Users\\Mousser\\Desktop\\PfeStarAssurance\\AutomobileTn\\"
    #     #                                         +"AutomobileTnOccasion\\FinalResult.csv")
    #     # automobileTnPostCleaning = testAutomobileTn.automobile_tn_columns_standardise(automobileTnPostScrapping)
    #     # automobileTnPostCleaning.to_excel(destination + '\\' + "automobileTnPostCleaning.xlsx")
    #     # # AutoPlusScrapper
    #     # testAutoPlus = ScrappAutoPlusTnOccasion()
    #     # autoPlusPostScrapping = pd.read_csv("C:\\Users\\Mousser\\Desktop\\PfeStarAssurance\\AutoPlusTn"+
    #     #                                         "\\AutoPlusOccasion\\ScrappingDataVoitOccasionAutoPlus.csv")
    #     # autoPlusPostCleaning = testAutoPlus.auto_plus_columns_standardise(autoPlusPostScrapping)
    #     # autoPlusPostCleaning.to_excel(destination + '\\' + "autoPlusPostCleaning.xlsx")
    #     # # AutoPrix
    #     # testAutoPrix = ScrappAutoPrixOccasion()
    #     # autoPrixPostScrapping = pd.read_csv("C:\\Users\\Mousser\\Desktop\\PfeStarAssurance\\AutoPrixTn"+
    #     #                                         "\\AutoPirxOccasion\\AutoPrixOccFinal.csv")
    #     # autoPrixPostCleaning = testAutoPrix.auto_prix_columns_standardise(autoPrixPostScrapping)
    #     # autoPrixPostCleaning.to_excel(destination + '\\' + "autoPrixPostCleaning.xlsx")
    #     # #Tayara
    #     # testTayaraTn = ScrappOccasionTayaraTn()
    #     # TayaraTnPostScrapping = imp.merge_csv_files("C:\\Users\\Mousser\\Desktop\\PfeStarAssurance\\TayaraTn2\\")
    #     # TayaraTnPostCleaning = testTayaraTn.tayara_columns_standardise(TayaraTnPostScrapping)
    #     # TayaraTnPostCleaning.to_excel(destination + '\\' + "TayaraTnPostCleaning.xlsx")
    #
        # Nettoyage des données phase 2
    def cleaning(self):
        dataframe = self.importer.merge_excel_files(os.path.join(path_to_DataPostColumnsStandardisedOccasion, ""))
        dataframe = self.cln.eliminate_unnamed_columns(dataframe)
        dataframe.to_csv(os.path.join(path_to_DataPostCleaning, "dataMerged.csv"), sep=';')
        dataframe = pd.read_csv(os.path.join(path_to_DataPostCleaning, "dataMerged.csv"), sep=';', index_col=0)
        dataframe = self.cln.nettoyer_marque(dataframe)
        dataframe = self.cln.nettoyer_modele(dataframe)
        dataframe = self.cln.nettoyer_col_annee(dataframe)
        dataframe = self.cln.nettoyer_boite_vitesse(dataframe)
        dataframe = self.cln.nettoyer_energie(dataframe)
        dataframe = self.cln.nettoyer_puissance_fiscale(dataframe)
        dataframe = self.cln.nettoyer_col_kilometrage(dataframe)
        dataframe = self.cln.nettoyer_prix(dataframe)
        # dataframe = self.cln.nettoyer_couleur(dataframe)
        # dataframe = self.cln.nettoyer_carrosserie(dataframe)
        dataframe.drop_duplicates(inplace=True)
        dataframe.drop_duplicates(inplace=True)
        dataframe.to_csv(os.path.join(path_to_DataPostCleaning, 'dataMergedAndCleaned.csv'),sep=';')
        return dataframe

class CleaningNewCars:

    def __init__(self):
        self.importer = fileImporter.Importer()
        self.cln = cleaner()

    def cleaning(self):
        # data_merged = self.importer.merge_csv_files(path_to_DataPostColumnsStandardisedNeuf + '\\') en windows
        data_merged = self.importer.merge_csv_files(os.path.join(path_to_DataPostColumnsStandardisedNeuf,''))

        data_merged = self.importer.removeUnnamed(data_merged)
        # data_merged = data_merged.drop(columns=['description'])
        print(data_merged)
        data_merged = self.cln.nettoyer_marque(data_merged)
        data_merged = self.cln.nettoyer_puissance_fiscale(data_merged)
        data_merged = self.cln.nettoyer_prix(data_merged)
        data_merged = self.cln.nettoyer_boite_vitesse(data_merged)
        data_merged = self.cln.nettoyer_energie(data_merged)
        data_merged = self.cln.nettoyer_carrosserie(data_merged)
        data_merged = self.cln.nettoyer_modele_voiture_neuf(data_merged)
        data_merged = data_merged.dropna(subset=['NombreDePlaces', 'NombreDePortes'])
        os.makedirs(path_to_NewCarsReady, exist_ok=True)
        data_merged.to_excel(os.path.join(path_to_NewCarsReady, "testMergeNeuf.xlsx"))


if __name__ == "__main__":
    # cleaningNewCars = CleaningNewCars()
    # cleaningNewCars.cleaning()
    pass
