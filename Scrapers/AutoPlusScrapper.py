from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from bs4 import BeautifulSoup
import time
from math import ceil
import Config
from Cleaning.ColumnStandardiser import ColumnsStandardiser
from Cleaning.Cleaner import *
from Cleaning.BrandModelExtraction import *
from Config import *
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import sessionmaker


class AutoPlusPostScrapping(Base):
    __tablename__ = 'AutoPlusPostScrapping'
    id = Column(Integer, primary_key=True)
    Marque = Column(String)
    Modele = Column(String)
    Annee = Column(String)
    BoiteVitesse = Column(String)
    Kilometrage = Column(String)
    Energie = Column(String)
    PuissanceFiscale = Column(String)
    datedelannonce = Column(String)
    desc = Column(String)
    Prix = Column(String)
    description = Column(String)
    etatduvehicule = Column(String)
    Couleur = Column(String)


class ScrappAutoPlusTnOccasion:

    def __init__(self):
        self.driver = Config.driverConfig
        self.baseUrl = Config.baseUrlAutoplus
        self.nativeUrl = Config.nativeUrlAutoplus
        
    def parsing_page_source(self, url: str):
        try:
            self.driver.get(url)
            time.sleep(4)
        except WebDriverException:
            self.driver.refresh()
            time.sleep(8)
        return BeautifulSoup(self.driver.page_source, 'html.parser') if BeautifulSoup(self.driver.page_source, 'html.parser') else None
    
    def nextPage(self, soup):
        ul = soup.find('ul', {'class':'pagination'})
        lasthref = ul.find_all('a')
        return lasthref[-1]['href']
    
    def extract_cars_urls(self, pageUrl):
        soup = self.parsing_page_source(pageUrl)
        atags = soup.find('div', {'id': 'lastadslistbox'})
        links = atags.find_all('a')
        return list(set([a.get('href')[44:] for a in links])) 
    
    def extract_data(self, soup):
        data = {}
        description = soup.find('h1',{'class':'col-md-8 adstitle'}).text.strip()  
        dateDeLannonce = soup.find('div',{'class':'col-md-3 pull-right'}).span.text.strip()
        prix = soup.find('div',{'class':'col-md-3 prixUsed'}).text.strip()
        desc = soup.find('div',{'class':'content'}).text.strip()
        listUl = soup.find('ul',{'class':'optionsCont'})
        listLi = listUl.find_all('li')
        for li in listLi:
            spec_name = li.find('b').text.strip()
            spec_value = li.find('span').text.strip()
            data[spec_name] = spec_value
        data['description'] = description
        data['desc'] = desc
        data['prix'] = prix
        data['date de l"annonce'] = dateDeLannonce
        return data
    
    def scrape(self):
        all_Data = {}
        soup = self.parsing_page_source(self.baseUrl)
        nbreDannonce = int(soup.find('span', {'class': 'total'}).text.strip()[:-23])
        nbreDePage = ceil(nbreDannonce/10)
        listeDesVoitures = []
        # for i in range(1, nbreDePage+1):
        for i in range(1,2):
            listeDesVoitures.extend(self.extract_cars_urls(self.baseUrl[:len(self.baseUrl)-1]+str(i))) 
        try:
            
            for index, voiture in enumerate(listeDesVoitures, start = 1):
                soup = self.parsing_page_source(self.nativeUrl + voiture)
                data = self.extract_data(soup)
                all_Data[f'dict{index}']=data       
        finally: 
            self.driver.quit()
        return all_Data

    def auto_plus_scrapper_runner(self):
        standardize = ColumnsStandardiser()
        data = self.scrape()
        dataStandardized = standardize.column_standardize(data)
        Base.metadata.create_all(engine)
        # Créer une session
        Session = sessionmaker(bind=engine)
        session = Session()
        for key, item in dataStandardized.items():
            autopluspostscrapping = AutoPlusPostScrapping(
                Energie=item['Energie :'], Annee=item['Mise en circulation :'], Kilometrage=item['kilométrage:'],
                PuissanceFiscale=item['Puissance fiscal:'], Marque=item['Marque :'], Modele=item['Modèle :'],
                BoiteVitesse=item['Boite vitesse :'], datedelannonce=item['date de l"annonce'],
                desc=item['desc'],description=item['description'], Prix=item['prix'], etatduvehicule=item['Etat du véhicule :'])
            session.add(autopluspostscrapping)
        # Commit les transactions
        session.commit()
        # Fermer la session
        session.close()

    def auto_plus_columns_standardise(self, dataframe):
        dataframe = dataframe.drop(columns={"etatduvehicule", "description",
                                            "desc", 'datedelannonce'})
        cln = cleaner()
        dataframe = cln.eliminate_unnamed_columns(dataframe)
        return dataframe  
      
    def run_whole_process(self):
        self.auto_plus_scrapper_runner()
        AutoPlusDf = pd.read_sql('AutoPlusPostScrapping', con=engine)
        AutoPlusDataStandardised = self.auto_plus_columns_standardise(AutoPlusDf)
        AutoPlusDataStandardised.to_sql('DataStandardised', con=engine, if_exists='append', index=False)


class ScrappAutoPlusTnNeuf:

    def __init__(self):
        self.scrapOcc = ScrappAutoPlusTnOccasion()
        self.driver = Config.driverConfig
        self.baseUrl = Config.baseUrlAutoplusNeuf

    def extract_brands_url(self, soup):
        brandsListDiv = soup.find('div', {'class': 'marq_listbox_wrapper'})
        links = brandsListDiv.find_all('a')
        return list(set([link.get('href')[44:] for link in links]))

    def extract_cars_url(self, soup):
        brandsListDiv = soup.find('div', {'class': 'panel-body minheight'})
        links = brandsListDiv.find_all('a')
        return [link.get('data-link')[44:] for link in links if link.get('data-link') is not None]

    def extract_data(self, soup):
        data = {}
        description = soup.find('div', {'class': 'marq_header clearfix'}).text.strip() if soup.find('div', {'class': 'marq_header clearfix'}) else None
        prix = soup.find('div', {'class': 'prix_marge'}).b.text.strip().replace("\u202f", "") if soup.find('div', {
            'class': 'prix_marge'}).b else None
        atags = soup.find('div', {'class': 'panel-group panel-group-lists', 'id': 'accordion2'})
        listeDesCaract = atags.find_all('li')
        for li_tag in listeDesCaract:
            spec_name = li_tag.find('span', {'class': 'tCh'}).text.strip()
            spec_value = li_tag.find('span', {'class': 'tChValue'}).text.strip()
            data[spec_name] = spec_value
        data['prix'] = prix
        data['description'] = description
        return data

    def ExtractVersionList(self, soup):
        listeBaliseALinkFini = soup.find_all('a', {'class': 'linkfini'})
        href_list = []
        for a in listeBaliseALinkFini:
            version_link = a.get('href')
            href_list.append(version_link)
        return (href_list)

    def Scrape(self, baseUrl):
        versionCarList = []
        all_Data = {}
        listCarsUrls = []
        soupBaseUrl = self.scrapOcc.parsing_page_source(baseUrl)
        listBrandsUrls = self.extract_brands_url(soupBaseUrl)
        try:
            for brandUrl in listBrandsUrls[:5]:
                soupBrandPage = self.scrapOcc.parsing_page_source(baseUrl + brandUrl)
                listCarsUrls.extend(self.extract_cars_url(soupBrandPage))
            for index, carUrl in enumerate(listCarsUrls[:8], start=1):
                soup = self.scrapOcc.parsing_page_source(baseUrl + carUrl)
                if soup.find('div', {'class': 'list_finition'}):
                    listeDesVersion = self.ExtractVersionList(soup)
                    versionCarList.extend(listeDesVersion)
                else:
                    data = self.extract_data(soup)
                    all_Data[f'dict{index}'] = data
            for index, car in enumerate(versionCarList, start=len(all_Data)):
                soup = self.scrapOcc.parsing_page_source(baseUrl + car)
                data = self.extract_data(soup)
                all_Data[f'dict{index}'] = data
        finally:
            self.driver.quit()
        return all_Data
    def auto_plus_columns_standardise(self, dataframe):
        dataframe = dataframe.rename(columns={"Boîte": "BoiteVitesse",
                                            "Puissance fiscale": "PuissanceFiscale",
                                            "prix": "Prix",
                                            "Nombre de places":"NombreDePlaces",
                                            "Nombre de portes":"NombreDePortes",
                                            "Nombre de cylindres":"NombreDeCylindres"
                                              })
        dataframe =dataframe[["BoiteVitesse","PuissanceFiscale","Prix","NombreDePlaces","NombreDePortes","description","Cylindrée",
        "Energie","NombreDeCylindres","Carrosserie"]]
        extraction = ExtractionMarqueModele()
        dataframe = extraction.extraire_marque_modele_neuf(dataframe)
        dataframe= dataframe.drop(columns={'description'})
        cln = cleaner()
        dataframe = cln.eliminate_unnamed_columns(dataframe)
        return dataframe

    def auto_plus_scrapper_runner(self, OutputFileName):
        standardize = ColumnsStandardiser()
        data_directory = os.path.join(path_to_DataPostScraping, "AutoPlus", "Neuf")
        file_path = os.path.join(data_directory, OutputFileName + '.csv')
        data = self.Scrape(self.baseUrl)
        dataStandardized = standardize.column_standardize(data)
        standardize.load_data_in_csv_file(dataStandardized, file_path)

    def run_whole_process(self):
        self.auto_plus_scrapper_runner('AutoPlusFilePostScrap')
        os.makedirs(os.path.join(path_to_DataPostScraping, "AutoPlus", "Neuf"), exist_ok=True)
        data_directory = os.path.join(path_to_DataPostScraping, "AutoPlus", "Neuf", "AutoPlusFilePostScrap")
        AutoPlusData = pd.read_csv(data_directory + '.csv',sep=',')
        AutoPlusDataPostStandardise = self.auto_plus_columns_standardise(AutoPlusData)
        os.makedirs(path_to_DataPostColumnsStandardisedNeuf, exist_ok=True)
        data_directory = os.path.join(path_to_DataPostColumnsStandardisedNeuf, "AutoPlusFilePostColumnsStandardised")
        AutoPlusDataPostStandardise.to_csv(data_directory + ".csv")


## MAIN ##
if __name__ == "__main__":
    pass













    # test = ScrappAutoPlusTnOccasion()
    # test.run_whole_process()
    # parent_directory = os.path.dirname(os.getcwd())
    # path_to_AutoPlus_Neuf = os.path.join(parent_directory, 'Data', 'DataPostScraping', 'AutoPlus', 'Neuf')
    # dataframe = pd.read_excel("D:\\PredictCarsPrice\\Data\\DataPostScraping\\AutoPlusNeuf.xlsx")
    # test = ScrappAutoPlusTnNeuf()
    # dataframe = test.auto_plus_columns_standardise(dataframe)
    # dataframe.to_excel(path_to_AutoPlus_Neuf + "\\test.xlsx")
    # test = ScrappAutoPlusTnNeuf()
    # test.run_whole_process()

# dataframe = dataframe.rename(columns={"kilométrage:": "Kilometrage",
#                                       "Mise en circulation :": "Annee",
#                                       "Energie :": "Energie",
#                                       "Boite vitesse :": "BoiteVitesse",
#                                       "Puissance fiscal:": "PuissanceFiscale",
#                                       "prix": "Prix",
#                                       "Marque :": "Marque",
#                                       "Modèle :": "Modele"})