from selenium.common.exceptions import WebDriverException
from bs4 import BeautifulSoup
import time
import Config
from Cleaning.ColumnStandardiser import ColumnsStandardiser
from Cleaning.BrandModelExtraction import ExtractionMarqueModele
import pandas as pd
from Cleaning.Cleaner import *
from Config import *
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import sessionmaker



class AutoPrixPostScrapping(Base):
    __tablename__ = 'AutoPrixPostScrapping'
    id = Column(Integer, primary_key=True)
    Annee = Column(String)
    BoiteVitesse = Column(String)
    Kilometrage = Column(String)
    Energie = Column(String)
    PuissanceFiscale = Column(String)
    datedelannonce = Column(String)
    desc = Column(String)
    Prix = Column(String)
    description = Column(String)
    Couleur = Column(String)
    Carrosserie = Column(String)


class ScrappAutoPrixOccasion:

    def __init__(self):
        self.driver = Config.driverConfig
        self.baseUrl = Config.baseUrlAutoprix
        self.nativeUrl = Config.nativeUrlAutoprix
        self.PageInitiale = 1
        self.PageFinale = 2

    def parsing_page_source(self, url):
        try:
            self.driver.get(url)
            time.sleep(25)
        except WebDriverException:
            self.driver.refresh()
            time.sleep(25)
        return BeautifulSoup(self.driver.page_source, 'html.parser') if BeautifulSoup(self.driver.page_source,'html.parser') else None
    
    def extract_cars_urls(self, pageUrl):
        soup = self.parsing_page_source(pageUrl)
        links = soup.find_all('a', {'class': 'black--text'})
        return list(set([a.get('href') for a in links if a.get('href')!='/estimation']))
    
    def extract_data(self, soup):
        data = {}
        try: 
            MarqueModele = soup.find('h1',{'class':'font-weight- title mb-1'}).text.strip() if soup.find('h1',{'class':'font-weight- title mb-1'}) else None  
            dateDeLannonce = soup.find('div',{'class':'col col-6'}).b.text.strip() if soup.find('div',{'class':'col col-6'}) and soup.find('div',{'class':'col col-6'}).b else None
            prix = soup.find('span',{'class':'font-weight-black headline'}).text.strip() if soup.find('span',{'class':'font-weight-black headline'}) else None 
            desc = soup.find('p',{'class':'body-2 black--text px-2 pb-1'}).text.strip() if soup.find('p',{'class':'body-2 black--text px-2 pb-1'}) else None
            listCarac = soup.find('div',{'class':'row elevation-0 row_4 transparent'})
            listdiv = listCarac.find_all('div')
            for h5b in listdiv:
                spec_name = h5b.find('h5', {'class': 'caption'}).text.strip() if h5b.find('h5', {'class': 'caption'}).text.strip() else None
                spec_value = h5b.find('b', {'class': 'body-1 font-weight-bold'}).text.strip() if h5b.find('b',{'class':'body-1 font-weight-bold'}) else None
                data[spec_name] = spec_value
            data['description']=MarqueModele
            data['desc'] = desc
            data['prix'] = prix
            data['date de l"annonce'] = dateDeLannonce
        except AttributeError as e:
            print(f"An error occurred while extracting data: {e}")
        return data
    
    def scrape(self, pageInitiale, pageFinale):
        all_Data = {}
        # soup = self.parsing_page_source(baseUrl)
        listeDesVoitures=[]
        # for i in range(pageInitiale,pageFinale+1):
        for i in range(1, 2):
            listeDesVoitures.extend(self.extract_cars_urls(self.baseUrl[:69]+str(i)+self.baseUrl[70:]))
        try:
            for index, voiture in enumerate(listeDesVoitures, start=1):
                soup = self.parsing_page_source(self.nativeUrl+voiture)
                data = self.extract_data(soup)
                all_Data[f'dict{index}']=data       
        finally: 
            self.driver.quit()
        return all_Data


    def auto_prix_scrapper_runner(self):
        standardize = ColumnsStandardiser()
        data = self.scrape(self.PageInitiale, self.PageFinale)
        dataStandardized = standardize.column_standardize(data)
        Base.metadata.create_all(engine)
        # Créer une session
        Session = sessionmaker(bind=engine)
        session = Session()
        for key, item in dataStandardized.items():
            autoprixpostscrapping = AutoPrixPostScrapping(
                Energie=item['Carburant'], Annee=item['Année'], Kilometrage=item['Kilométrage'],
                PuissanceFiscale=item['Puissance'], Carrosserie=item['Carrosserie'],
                BoiteVitesse=item['Boite'], datedelannonce=item['date de l"annonce'],
                desc=item['desc'], description=item['description'], Prix=item['prix'])
            session.add(autoprixpostscrapping)
        # Commit les transactions
        session.commit()
        # Fermer la session
        session.close()

    def auto_prix_columns_standardise(self, dataframe):
        extraction = ExtractionMarqueModele()
        dataframe = dataframe.drop(columns={'datedelannonce'})
        dataframe = dataframe.dropna(how='all')
        dataframe = extraction.extraire_marque_modele(dataframe)
        dataframe = dataframe.drop(columns={'description', 'desc'})
        cln = cleaner()
        dataframe = cln.eliminate_unnamed_columns(dataframe)
        return dataframe
    
    def run_whole_process(self):
        self.auto_prix_scrapper_runner()
        AutoPrixDf = pd.read_sql('AutoPrixPostScrapping', con=engine)
        AutoPrixDataStandardised = self.auto_prix_columns_standardise(AutoPrixDf)
        AutoPrixDataStandardised.to_sql('DataStandardised', con=engine, if_exists='append', index=False)


## MAIN ##
if __name__ == "__main__":
    pass


    # autoPrixScrapper = ScrappAutoPrixOccasion()
    # autoPrixScrapper.PageInitiale = 1
    # autoPrixScrapper.PageFinale = 2
    # autoPrixScrapper.run_whole_process()
