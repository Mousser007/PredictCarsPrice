from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from bs4 import BeautifulSoup
import time
from math import ceil 
import re
import Config
from Cleaning.ColumnStandardiser import ColumnsStandardiser
from Cleaning.BrandModelExtraction import ExtractionMarqueModele
import pandas as pd 
from Cleaning.Cleaner import *
from Config import *
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import sessionmaker



class AffarePostScrapping(Base):
    __tablename__ = 'AffarePostScrapping'
    id = Column(Integer, primary_key=True)
    Energie = Column(String)
    Annee = Column(String)
    Kilometrage = Column(String)
    PuissanceFiscale= Column(String)
    Miseencirculation = Column(String)
    BoiteVitesse = Column(String)
    datedelannonce = Column(String)
    desc = Column(String)
    Prix = Column(String)
    description = Column(String)


class ScrappOccasionAffareTn:

    def __init__(self):
        self.driver = Config.driverConfig
        self.baseUrl = Config.baseUrlAffare
        self.nativeUrl = Config.nativeUrlAffare
        
    def parsing_page_source(self, url):
        try:
            self.driver.get(url)
            time.sleep(27)
        except WebDriverException:
            self.driver.refresh()
            time.sleep(25)
        return BeautifulSoup(self.driver.page_source,'html.parser') if BeautifulSoup(self.driver.page_source,'html.parser') else None
    
    def nbre_de_page(self, soup):
        h2 = soup.find('h2',{'class':'one-line'}).text.strip()
        nbreDAnnonce = int(re.search(r'\((.*?)\)',h2).group(1))
        nbreDePage = ceil(nbreDAnnonce/30)
        return nbreDePage, nbreDAnnonce
    
    def extract_cars_urls(self, pageUrl):
        soup = self.parsing_page_source(pageUrl)
        links = soup.find_all('a', {'class': 'AnnoncesList_saz__RXM7e'})
        return list(set([a.get('href') for a in links ]))
    
    def extract_data(self, soup):
        data={}
        try: 
            dateDeLannonce = soup.find_all('div', {'class': 'Annonce_f201510__BNC4l'})[-1].text.strip() if  soup.find_all('div', {'class': 'Annonce_f201510__BNC4l'}) else None
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
        nbreDePageTotale, nbreDAnnonceTotale = self.nbre_de_page(soup)
        # nbre_de_page_a_scrapper = ceil((nbreDAnnonceTotale - Config.nbre_annonce_site_affare)/30)
        # Config.nbre_annonce_site_affare = nbreDAnnonceTotale
        listeDesVoitures = []
        # for i in range(nbreDePageTotale+1):
        for i in range(1, 3):
            listeDesVoitures.extend(self.extract_cars_urls(self.baseUrl[:94]+str(i)+self.baseUrl[95:]))
        #l3 = [element for element in listeDesVoitures if element not in Config.liste_de_voiture_affare]
        try:
            for index, voiture in enumerate(listeDesVoitures, start=1):
                soup = self.parsing_page_source(self.nativeUrl+voiture)
                data = self.extract_data(soup)
                all_Data[f'dict{index}'] = data
        finally: 
            self.driver.quit()
        return all_Data
    
    def affare_scrapper_runner(self):
        standardize = ColumnsStandardiser()
        # os.makedirs(os.path.join(path_to_DataPostScraping, 'Affare'), exist_ok=True)
        # data_directory = os.path.join(path_to_DataPostScraping, "Affare")
        # file_path = os.path.join(data_directory, OutputFileName + '.csv')
        data = self.scrape()
        dataStandardized = standardize.column_standardize(data)
        Base.metadata.create_all(engine)
        # Créer une session
        Session = sessionmaker(bind=engine)
        session = Session()
        for key, item in dataStandardized.items():
            affarepostscrapping = AffarePostScrapping(
                Energie=item['Energie'], Annee=item['Année'], Kilometrage=item['Kilométrage'],
                PuissanceFiscale=item['Puissance'], Miseencirculation=item['Mise en circulation'],
                BoiteVitesse=item['Boîte'], datedelannonce=item["date de l'annonce"],
                desc=item['desc'],Prix=item['prix'])
            session.add(affarepostscrapping)
        # Commit les transactions
        session.commit()
        # Fermer la session
        session.close()

    def affare_columns_standardise(self, dataframe):   
        extraction = ExtractionMarqueModele()
        dataframe = dataframe.drop(columns={"Miseencirculation", "datedelannonce"})
        dataframe['description'] = dataframe['desc']
        dataframe = dataframe.drop(columns={'desc'})
        dataframe = extraction.extraire_marque_modele(dataframe)
        cln = cleaner()
        dataframe = cln.eliminate_unnamed_columns(dataframe)
        dataframe = dataframe.drop(columns={"description"})
        return dataframe

    def run_whole_process(self):
        self.affare_scrapper_runner()
        AffareFile =pd.read_sql('AffarePostScrapping', con=engine)
        AffareData = self.affare_columns_standardise(AffareFile)
        AffareData.to_sql('DataStandardised', con=engine, if_exists='append', index=False)


if __name__ == "__main__":
    pass
    # test = ScrappOccasionAffareTn()
    # test.run_whole_process()
    # # Phase cleaning
    # # test = CleaningProcess.CleaningUseCars()
    # # test.cleaning()
# dataframe = dataframe.rename(columns={"Kilométrage": "Kilometrage",
#                                               "Année": "Annee",
#                                               "Boite": "BoiteVitesse",
#                                               "prix":"Prix",
#                                               "Puissance":"PuissanceFiscale"})