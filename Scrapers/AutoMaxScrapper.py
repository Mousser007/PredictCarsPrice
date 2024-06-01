from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from bs4 import BeautifulSoup
import time
from math import ceil 
import pandas as pd 
from Cleaning.ColumnStandardiser import ColumnsStandardiser
from Cleaning.BrandModelExtraction import ExtractionMarqueModele
import os
from Cleaning.Cleaner import *
from Config import *


class ScrappOccasionAutoMaxTn:

    def __init__(self):
        self.driver = webdriver.Chrome()
        self.baseUrl = "https://www.automax.tn/voitures-occasion/?prix-from=3000&page=1&trier-par=recent"
        self.nativeUrl = "https://www.automax.tn"

    def parsing_page_source(self, url):
        try:
            self.driver.get(url)
            time.sleep(7)
        except WebDriverException:
            self.driver.refresh()
            time.sleep(7)
        return BeautifulSoup(self.driver.page_source, 'html.parser') if BeautifulSoup(self.driver.page_source, 'html.parser') else None
    
    def nbre_de_page(self, soup):
        div = soup.find('div',{'class':'vehica-inventory-v1__title'}).text.strip()
        nbreDAnnonce = int(div[:-9])
        nbreDePage = ceil(nbreDAnnonce/12)
        return nbreDePage
    
    def extract_cars_urls(self, pageUrl):
        soup = self.parsing_page_source(pageUrl)
        links = soup.find_all('a', {'class': 'vehica-car-card-link'})
        return list(set([a.get('href') for a in links ]))
    
    def extract_data(self, soup):
        data={}
        try: 
            dateDeLannonce = soup.find('div', {'class':'vehica-car-date'}).text.strip() if soup.find('div', {'class':'vehica-car-date'}) else None 
            prix = soup.find('div', {'class':'vehica-car-price'}).text.strip() if soup.find('div', {'class':'vehica-car-price'}) else None 
            desc= soup.find('div',{'class':'vehica-car-description'}).text.strip() if soup.find('div', {'class':'vehica-car-description'}) else None
            listCarac = soup.find_all('div',{'class':'vehica-grid'})
            # listdiv=listCarac.find_all('div',{'class':'Annonce_flx785550__AnK7v'})
            for div in listCarac:
                spec_name = div.find('div', {'class':'vehica-car-attributes__name vehica-grid__element--1of2'}).text.strip() if div.find('div',{'class':'vehica-car-attributes__name vehica-grid__element--1of2'}) else None
                spec_value = div.find('div', {'class':'vehica-car-attributes__values vehica-grid__element--1of2'}).text.strip() if div.find('div',{'class':'vehica-car-attributes__values vehica-grid__element--1of2'}) else None
                data[spec_name] = spec_value
            data["date de l'annonce"] = dateDeLannonce
            data['desc'] = desc
            data['prix'] = prix
           
        except AttributeError as e:
            print(f"An error occurred while extracting data: {e}")
        return data
    
    def scrape(self):
        all_Data= {}
        soup = self.parsing_page_source(self.baseUrl)
        nbreDePage= self.nbre_de_page(soup)
        listeDesVoitures=[]
        # for i in range(nbreDePage+1):
        for i in range(2):
            listeDesVoitures.extend(self.extract_cars_urls(self.baseUrl[:62] + str(i) + self.baseUrl[63:]))
        try:
            
            for index, voiture in enumerate(listeDesVoitures, start = 1):
                soup = self.parsing_page_source(voiture)
                data = self.extract_data(soup)
                all_Data[f'dict{index}']=data
                
        finally: 
            self.driver.quit()
        return all_Data
    
    def auto_max_scrapper_runner(self, OutputFileName):
        standardize = ColumnsStandardiser()
        data_directory = os.path.abspath(os.path.join(path_to_DataPostScraping, "AutoMax"))
        file_path = os.path.join(data_directory, OutputFileName + '.csv')
        data = self.scrape()
        dataStandardized = standardize.column_standardize(data)
        standardize.load_data_in_csv_file(dataStandardized, file_path)

    def automax_missing_marque_modele(self, dataframe):
        modelesList = ["CLIO", "GOLF", "POLO"]
        extraction = ExtractionMarqueModele()
        for modele in modelesList:
            maskModele = dataframe['Modele'].str.upper() == modele
            dataframe.loc[maskModele, 'Modele'] = dataframe.loc[maskModele, ['desc', 'Marque']].apply(
                lambda row: extraction.extraire_modele(row['desc'], row['Marque']), axis=1)
        return dataframe
    def auto_max_columns_standardise(self, dataframe):
        dataframe = dataframe.rename(columns={"Kilométrage:": "Kilometrage",
                                              "Année:": "Annee",
                                              "Energie:": "Energie",
                                              "Boite:":"BoiteVitesse",
                                              "Puissance fiscale:": "PuissanceFiscale",
                                              "prix":"Prix",
                                              "Marque:":"Marque",
                                              "Modèle:":"Modele"})
        dataframe = dataframe.drop(columns={"Gouvernorat:", "date de l'annonce"})
        dataframe = dataframe.dropna(how='all')
        dataframe['Marque'] = dataframe['Marque'].str.upper()
        dataframe['Modele'] = dataframe['Modele'].str.upper()
        dataframe = self.automax_missing_marque_modele(dataframe)
        cln = cleaner()
        dataframe = cln.eliminate_unnamed_columns(dataframe)
        dataframe = dataframe.drop(columns={"desc"})
        return dataframe
    
    def run_whole_process(self):
        self.auto_max_scrapper_runner("FileAutoMaxPostScrapTest")
        data_directory = os.path.join(path_to_DataPostScraping, "AutoMax", "FileAutoMaxPostScrapTest.csv")
        AutoMaxFile = pd.read_csv(data_directory)
        AutoMaxData = self.auto_max_columns_standardise(AutoMaxFile)
        data_directory = os.path.join(path_to_DataPostColumnsStandardisedOccasion, "FileAutoMaxPostColumnStandardised.xlsx")
        AutoMaxData.to_excel(data_directory)


## MAIN ##
if __name__ == "__main__":
    # AutoMax = ScrappOccasionAutoMaxTn()
    # AutoMax.run_whole_process()
    pass


