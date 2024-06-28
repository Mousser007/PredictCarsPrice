from selenium import webdriver
from bs4 import BeautifulSoup
import time
import Config
from Cleaning.ColumnStandardiser import ColumnsStandardiser
from selenium.common.exceptions import WebDriverException
from Cleaning.BrandModelExtraction import ExtractionMarqueModele
import pandas as pd 
from Cleaning.Cleaner import *
from Config import *
# import logging
# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger()
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import sessionmaker


class AutomobileTnPostScrapping(Base):
    __tablename__ = 'AutomobileTnPostScrapping'
    id = Column(Integer, primary_key=True)
    Marque = Column(String)
    Modele = Column(String)
    Annee = Column(String)
    BoiteVitesse = Column(String)
    Kilometrage = Column(String)
    Energie = Column(String)
    PuissanceFiscale = Column(String)
    datedelannonce = Column(String)
    Prix = Column(String)
    Transmission = Column(String)
    Carrosserie = Column(String)
    Gouvernorat = Column(String)
    Couleur = Column(String)
    Generation = Column(String)
    Nombredeportes = Column(String)
    Nombredeplaces = Column(String)
    Couleurinterieure = Column(String)
    Sellerie = Column(String)



class ScrapperAutomobileTnOcc:
    
    def __init__(self):
        self.driver = Config.driverConfig
        self.baseUrl = Config.baseUrlAutomobileTn
        self.pageInitiale = 1
        self.pageFinale = 2
        
    def parsing_page_source(self, url):
        try:
            self.driver.get(url)
            time.sleep(25)
        except WebDriverException:
            self.driver.refresh()
            time.sleep(25)
        return BeautifulSoup(self.driver.page_source,'html.parser') if BeautifulSoup(self.driver.page_source,'html.parser') else None
    
    def extract_cars_urls(self, pageUrl):
        soup = self.parsing_page_source(pageUrl)
        atags = soup.find_all('a', {'class': 'occasion-link-overlay'}) if soup.find_all('a', {'class': 'occasion-link-overlay'}) else None
        return [a.get('href')[12:] for a in atags]
    
    def extract_data(self, soup):
        data = {}
        atags = soup.find('div', {'class': 'box d-none d-md-block'}) if soup.find('div', {'class': 'box d-none d-md-block'}) else None
        listeDescCaract = atags.find_all('li')
        for li_tag in listeDescCaract:
            spec_name = li_tag.find('span', {'class': 'spec-name'}).text.strip()
            spec_value = li_tag.find('span', {'class': 'spec-value'}).text.strip()
            data[spec_name] = spec_value
        
        # Modele = soup.find('h1').text.strip()
        Prix = soup.find('div', {'class': 'price'}).text.strip() if soup.find('div', {'class': 'price'}).text.strip() else None
        # data['Modele'] = Modele #Modele=Marque+Modele
        data['Prix'] = Prix
        
        atagsSpec = soup.find('div', {'class': 'col-md-6 mb-3 mb-md-0'}) if soup.find('div', {'class': 'col-md-6 mb-3 mb-md-0'}) else None
        listeDesSpecification = atagsSpec.find_all('li')
        for li_tag in listeDesSpecification:
            spec_name = li_tag.find('span', {'class': 'spec-name'}).text.strip()
            spec_value = li_tag.find('span', {'class': 'spec-value'}).text.strip()
            data[spec_name] = spec_value
        
        return data
    
    def scrape(self, pageInit, pageFinal):
        urls = []
        try:
            # for i in range(pageInit,pageFinal+1):
            for i in range(1, 135):
                urls.extend(self.extract_cars_urls(self.baseUrl+'/'+str(i)+'?sort=date'))
            all_Data={}
            for index, url in enumerate(urls, start = 1):
                soup = self.parsing_page_source(self.baseUrl+url)
                data = self.extract_data(soup)
                all_Data[f'dict{index}'] = data
        finally:
            self.driver.quit()
        return all_Data
    
    def automobile_tn_scrapper_runner(self):
        standardize = ColumnsStandardiser()
        data = self.scrape(self.pageInitiale, self.pageFinale)
        dataStandardized = standardize.column_standardize(data)
        Base.metadata.create_all(engine)
        # Créer une session
        Session = sessionmaker(bind=engine)
        session = Session()
        for key, item in dataStandardized.items():
            automobiletnpostscrapping = AutomobileTnPostScrapping(
                Energie=item['Énergie'], Annee=item['Mise en circulation'], Kilometrage=item['Kilométrage'],
                PuissanceFiscale=item['Puissance fiscale'], Marque=item['Marque'], Modele=item['Modèle'],
                BoiteVitesse=item['Boite vitesse'], datedelannonce=item["Date de l'annonce"],
                Sellerie=item['Sellerie'], Prix=item['Prix'],
                Transmission=item['Transmission'], Carrosserie=item['Carrosserie'], Couleur=item['Couleur extérieure'],
                Generation=item['Génération'], Nombredeportes=item['Nombre de portes'], Nombredeplaces=item['Nombre de places'],
                Couleurinterieure=item['Couleur intérieure'], Gouvernorat=item['Gouvernorat'])
            session.add(automobiletnpostscrapping)
        # Commit les transactions
        session.commit()
        # Fermer la session
        session.close()

    def automobile_tn_columns_standardise(self, dataframe):
        dataframe = dataframe[['id', 'Kilometrage', 'Annee', 'Energie', 'BoiteVitesse',
                               'PuissanceFiscale', 'Marque', 'Modele', 'Prix', 'Couleur','Carrosserie']]
        # dataframe = dataframe.rename(columns={"Modèle": "Modele"})
        cln = cleaner()
        dataframe = cln.eliminate_unnamed_columns(dataframe)
        return dataframe
    
    def run_whole_process(self):
        self.pageInitiale = 1
        self.pageFinale = 2
        self.automobile_tn_scrapper_runner()
        AutomobileTnDf = pd.read_sql('AutomobileTnPostScrapping', con=engine)
        AutomobileTnDataStandardised = self.automobile_tn_columns_standardise(AutomobileTnDf)
        AutomobileTnDataStandardised.to_sql('DataStandardised', con=engine, if_exists='append', index=False)



class ScrapperAutomobileTnNeuf:

    def __init__(self):
        self.scrapOcc = ScrapperAutomobileTnOcc()
        self.driver = Config.driverConfig
        self.baseUrl = Config.baseUrlAutomobileTnNeuf

    def automobile_tn_columns_standardise(self, dataframe):
        dataframe = dataframe.rename(columns={"Boîte": "BoiteVitesse",
                                              "Puissance fiscale": "PuissanceFiscale",
                                              "prix": "Prix",
                                              "Nombre de places": "NombreDePlaces",
                                              "Nombre de portes": "NombreDePortes",
                                              "Nombre de cylindres": "NombreDeCylindres"
                                              })
        dataframe = dataframe[
            ["BoiteVitesse", "PuissanceFiscale", "Prix", "NombreDePlaces", "NombreDePortes", "description", "Cylindrée",
             "Energie", "NombreDeCylindres", "Carrosserie"]]
        extraction = ExtractionMarqueModele()
        dataframe = extraction.extraire_marque_modele_neuf(dataframe)
        dataframe = dataframe.drop(columns=['description'])
        cln = cleaner()
        dataframe = cln.eliminate_unnamed_columns(dataframe)
        return dataframe

    def extract_brands_url(self, soup):
        brandsListDiv = soup.find('div', {'class': 'brands-list'})
        links = brandsListDiv.find_all('a')
        return [link.get('href')[8:] for link in links]

    def extract_cars_url(self, soup):
        brandsListDiv = soup.find('div', {'class': 'articles'})
        links = brandsListDiv.find_all('a')
        return [link.get('href')[8:] for link in links]

    def extract_data(self, soup):
        data = {}
        description = soup.find('h3', {'class': 'page-title'}).text.strip() if soup.find('h3', {'class': 'page-title'}) else None
        prix = soup.find('div', {'class': 'buttons'}).span.text.strip() if soup.find('div',
                                                                            {'class': 'buttons'}) else None
        atags = soup.find('div', {'class': 'technical-details'})
        listeDestbody = atags.find_all('tbody')
        listeDesTr = atags.find_all('tr')
        for tbody in listeDestbody:
            for tr in listeDesTr:
                cells = tr.find_all(['th', 'td'])
                if len(cells) == 2:
                    spec_name = cells[0].get_text(strip=True)
                    spec_value = cells[1].get_text(strip=True)
                    data[spec_name] = spec_value
        data['prix'] = prix
        data['description'] = description
        return data

    def ExtractVersionList(self, soup):
        listeTd = soup.find_all('td', {'class': 'version'})
        href_list = []
        for a in listeTd:
            version_link = a.find('a')
            if version_link:
                href_value = version_link.get('href')
                href_list.append(href_value[8:]) if href_value else None
        return (href_list)

    def automobile_tn_scrapper_runner(self, OutputFileName):
        standardize = ColumnsStandardiser()
        data_directory = os.path.join(path_to_DataPostScraping, "AutomobileTn", "Neuf")
        file_path = os.path.join(data_directory, OutputFileName + '.csv')
        data = self.scrapeNeuf()
        dataStandardized = standardize.column_standardize(data)
        standardize.load_data_in_csv_file(dataStandardized, file_path)

    def scrapeNeuf(self):
        versionCarList = []
        all_Data = {}
        listCarsUrls = []
        soupBaseUrl = self.scrapOcc.parsing_page_source(self.baseUrl)
        listBrandsUrls = self.extract_brands_url(soupBaseUrl)
        try:
            for brandUrl in listBrandsUrls[:5]:
                soupBrandPage = self.scrapOcc.parsing_page_source(self.baseUrl + brandUrl)
                listCarsUrls.extend(self.extract_cars_url(soupBrandPage))
            all_Data = {}
            for index, carUrl in enumerate(listCarsUrls[:7], start=1):
                soup = self.scrapOcc.parsing_page_source(self.baseUrl + carUrl)
                if soup.find('table', {'class': 'versions'}):
                    listeDesVersion = self.ExtractVersionList(soup)
                    versionCarList.extend(listeDesVersion)
                else:
                    data = self.extract_data(soup)
                    all_Data[f'dict{index}'] = data
            for index, car in enumerate(versionCarList, start=len(all_Data)):
                soup = self.scrapOcc.parsing_page_source(self.baseUrl + car)
                data = self.extract_data(soup)
                all_Data[f'dict{index}'] = data
        finally:
            self.driver.quit()
        return all_Data

    def run_whole_process(self):
        self.automobile_tn_scrapper_runner('AutomobileTnFilePostScrap')
        data_directory = os.path.join(path_to_DataPostScraping, "AutomobileTn", "Neuf",
                                      "AutomobileTnFilePostScrap")
        AutomobileTnData = pd.read_csv(data_directory + '.csv', sep=',')
        AutomobileTnDataPostStandardise = self.automobile_tn_columns_standardise(AutomobileTnData)
        os.makedirs(path_to_DataPostColumnsStandardisedNeuf, exist_ok=True)
        data_directory = os.path.join(path_to_DataPostColumnsStandardisedNeuf,
                                      "AutomobileTnFilePostColumnsStandardised")
        AutomobileTnDataPostStandardise.to_csv(data_directory + ".csv")


## MAIN ##
if __name__ == "__main__":
    pass
    # test = ScrapperAutomobileTnOcc()
    # test.run_whole_process()



    # dataframe = pd.read_excel("D:\\PredictCarsPrice\\Data\\DataPostScraping\\AutomobileTnNeuf.xlsx")
    # test = ScrapperAutomobileTnNeuf()
    # dataframe = test.automobile_tn_columns_standardise(dataframe)
    # dataframe.to_excel("D:\\PredictCarsPrice\\Data\\DataPostScraping\\testautomobiletn.xlsx")
    # test = ScrapperAutomobileTnNeuf()
    # test.run_whole_process()
