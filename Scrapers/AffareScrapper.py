from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from bs4 import BeautifulSoup
import time
from math import ceil 
import re
from Cleaning.ColumnStandardiser import ColumnsStandardiser
from Cleaning.BrandModelExtraction import ExtractionMarqueModele
import pandas as pd 
import os
from Cleaning.Cleaner import *
from Config import *
import CleaningProcess


class ScrappOccasionAffareTn:

    def __init__(self):
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')  # Run in headless mode
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument("--disable-javascript")
        options.add_argument('--window-size=1920x1080')
        options.add_argument(
            "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
        self.driver = webdriver.Chrome(options=options)
        self.baseUrl = "https://www.affare.tn/petites-annonces/tunisie/voiture-neuve-occassion-prix-tayara-a-vendre?o=1&t=prix-moins-cher&prix=3000-max"
        self.nativeUrl = "https://www.affare.tn"
        
    def parsing_page_source(self, url):
        try:
            self.driver.get(url)
            time.sleep(20)
        except WebDriverException:
            self.driver.refresh()
            time.sleep(20)
        return BeautifulSoup(self.driver.page_source,'html.parser') if BeautifulSoup(self.driver.page_source,'html.parser') else None
    
    def nbre_de_page(self, soup):
        h2 = soup.find('h2',{'class':'one-line'}).text.strip()
        nbreDAnnonce = int(re.search(r'\((.*?)\)',h2).group(1))
        nbreDePage = ceil(nbreDAnnonce/30)
        return nbreDePage
    
    def extract_cars_urls(self, pageUrl):
        soup = self.parsing_page_source(pageUrl)
        links = soup.find_all('a', {'class': 'AnnoncesList_saz__RXM7e'})
        return list(set([a.get('href') for a in links ]))
    
    def extract_data(self, soup):
        data={}
        try: 
            dateDeLannonce = soup.find_all('div', {'class': 'Annonce_f201510__BNC4l'})[-1].text.strip()
            prix = soup.find('span',{'class': 'Annonce_price__tE_l1'}).text.strip() if soup.find('span', {'class': 'Annonce_price__tE_l1'}) else None
            desc= soup.find('div',{'class':'Annonce_product_info__91ryJ Annonce_mozi__0xfZD'}).text.strip() if soup.find('div',{'class':'Annonce_product_info__91ryJ Annonce_mozi__0xfZD'}) else None
            listCarac = soup.find('div',{'class':'Annonce_box_params__nX87s'})
            listdiv=listCarac.find_all('div',{'class':'Annonce_flx785550__AnK7v'})
            for div in listdiv:
                spec_name = div.find('div').text.strip() if div.find('div') else None
                spec_value = div.find('div',{'class':'Annonce_prop_1__OYvkf'}).text.strip() if div.find('div',{'class':'Annonce_prop_1__OYvkf'}) else None
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
            listeDesVoitures.extend(self.extract_cars_urls(self.baseUrl[:94]+str(i)+self.baseUrl[95:]))
        try:
            for index, voiture in enumerate(listeDesVoitures, start=1):
                soup = self.parsing_page_source(self.nativeUrl+voiture)
                data = self.extract_data(soup)
                all_Data[f'dict{index}']=data 
        finally: 
            self.driver.quit()
        return all_Data
    
    def affare_scrapper_runner(self, OutputFileName):
        standardize = ColumnsStandardiser()
        os.makedirs(os.path.join(path_to_DataPostScraping, 'Affare'), exist_ok=True)
        data_directory = os.path.join(path_to_DataPostScraping, "Affare")
        file_path = os.path.join(data_directory, OutputFileName + '.csv')
        data = self.scrape()
        dataStandardized = standardize.column_standardize(data)
        standardize.load_data_in_csv_file(dataStandardized, file_path)
    
    def affare_columns_standardise(self, dataframe):   
        extraction = ExtractionMarqueModele()
        dataframe = dataframe.rename(columns={"Kilométrage": "Kilometrage",
                                              "Année": "Annee",
                                              "Boîte": "BoiteVitesse",
                                              "prix":"Prix",
                                              "Puissance":"PuissanceFiscale"})
        dataframe = dataframe.drop(columns={"Mise en circulation", "date de l'annonce"})
        dataframe['description'] = dataframe['desc']
        dataframe = dataframe.drop(columns={'desc'})
        dataframe = extraction.extraire_marque_modele(dataframe)
        cln = cleaner()
        dataframe = cln.eliminate_unnamed_columns(dataframe)
        dataframe = dataframe.drop(columns={"description"})
        return dataframe

    def run_whole_process(self):
        self.affare_scrapper_runner("AffareFilePostScrapTest")
        os.makedirs(os.path.join(path_to_DataPostScraping, "Affare"), exist_ok=True)
        data_directory = os.path.join(path_to_DataPostScraping, "Affare", "AffareFilePostScrapTest.csv")
        AffareFile = pd.read_csv(data_directory)
        AffareData = self.affare_columns_standardise(AffareFile)
        os.makedirs(path_to_DataPostColumnsStandardisedOccasion, exist_ok=True)
        data_directory = os.path.join(path_to_DataPostColumnsStandardisedOccasion, "AffareFilePostColumnStandardised.xlsx")
        AffareData.to_excel(data_directory)


if __name__ == "__main__":
    # test = ScrappOccasionAffareTn()
    # test.run_whole_process()
    # Phase cleaning
    # test = CleaningProcess.CleaningUseCars()
    # test.cleaning()
    pass
