import sys
sys.path.append('D:\\PredictCarsPrice')
from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from bs4 import BeautifulSoup
import time
from math import ceil 
from Cleaning.ColumnStandardiser import ColumnsStandardiser
from Cleaning.Cleaner import *
from Cleaning.BrandModelExtraction import *
from Config import *


class ScrappAutoPlusTnOccasion:

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
        self.baseUrl = "https://www.auto-plus.tn/voitures-d-occasion/1/p/1"
        self.nativeUrl = "https://www.auto-plus.tn/voitures-d-occasion"
        
    def parsing_page_source(self, url: str):
        try:
            self.driver.get(url)
            time.sleep(4)
        except WebDriverException:
            self.driver.refresh()
            time.sleep(2)
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
        for i in range(1, nbreDePage+1):
            listeDesVoitures.extend(self.extract_cars_urls(self.baseUrl[:len(self.baseUrl)-1]+str(i))) 
        try:
            
            for index, voiture in enumerate(listeDesVoitures, start = 1):
                soup = self.parsing_page_source(self.nativeUrl + voiture)
                data = self.extract_data(soup)
                all_Data[f'dict{index}']=data       
        finally: 
            self.driver.quit()
        return all_Data

    def auto_plus_scrapper_runner(self, OutputFileName):
        standardize = ColumnsStandardiser()
        data_directory = os.path.join(path_to_DataPostScraping, "AutoPlus")
        file_path = os.path.join(data_directory, OutputFileName + '.csv')
        data = self.scrape()
        dataStandardized = standardize.column_standardize(data)
        standardize.load_data_in_csv_file(dataStandardized, file_path)

    def auto_plus_columns_standardise(self, dataframe):
        dataframe = dataframe.rename(columns={"kilométrage:": "Kilometrage",
                                              "Mise en circulation :": "Annee",
                                              "Energie :": "Energie",
                                              "Boite vitesse :": "BoiteVitesse",
                                              "Puissance fiscal:": "PuissanceFiscale",
                                              "prix": "Prix",
                                              "Marque :": "Marque",
                                              "Modèle :": "Modele"})
        dataframe = dataframe.drop(columns={"Etat du véhicule :", "description",
                                            "desc", 'date de l"annonce'})
        cln = cleaner()
        dataframe = cln.eliminate_unnamed_columns(dataframe)
        return dataframe  
      
    def run_whole_process(self):
        self.auto_plus_scrapper_runner('AutoPlusFilePostScrap')
        script_directory = os.path.dirname(os.path.abspath(__file__))
        data_directory = os.path.join(path_to_DataPostScraping, "AutoPlus", "AutoPlusFilePostScrap")
        AutoPlusData= pd.read_csv(data_directory + '.csv', sep=';')
        AutoPlusDataPostStandardise = self.auto_plus_columns_standardise(AutoPlusData)
        data_directory =os.path.join(path_to_DataPostCleaning, "AutoPlus", "AutoPlusFilePostClean")
        AutoPlusDataPostStandardise.to_csv(data_directory + ".csv")


class ScrappAutoPlusTnNeuf:

    def __init__(self):
        self.scrapOcc = ScrappAutoPlusTnOccasion()
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
        self.baseUrl = 'https://www.auto-plus.tn/les-voitures-neuves'

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
        description = soup.find('div', {'class': 'marq_header clearfix'}).text.strip()
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
            for brandUrl in listBrandsUrls:
                soupBrandPage = self.scrapOcc.parsing_page_source(baseUrl + brandUrl)
                listCarsUrls.extend(self.extract_cars_url(soupBrandPage))
            for index, carUrl in enumerate(listCarsUrls, start=1):
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
        # self.auto_plus_scrapper_runner('AutoPlusFilePostScrap')
        data_directory = os.path.join(path_to_DataPostScraping, "AutoPlus", "Neuf", "AutoPlusFilePostScrap")
        AutoPlusData = pd.read_csv(data_directory + '.csv',sep=',')
        AutoPlusDataPostStandardise = self.auto_plus_columns_standardise(AutoPlusData)
        data_directory = os.path.join(path_to_DataPostColumnsStandardisedNeuf, "AutoPlusFilePostColumnsStandardised")
        AutoPlusDataPostStandardise.to_csv(data_directory + ".csv")


## MAIN ##
if __name__ == "__main__":
    # parent_directory = os.path.dirname(os.getcwd())
    # path_to_AutoPlus_Neuf = os.path.join(parent_directory, 'Data', 'DataPostScraping', 'AutoPlus', 'Neuf')
    # dataframe = pd.read_excel("D:\\PredictCarsPrice\\Data\\DataPostScraping\\AutoPlusNeuf.xlsx")
    # test = ScrappAutoPlusTnNeuf()
    # dataframe = test.auto_plus_columns_standardise(dataframe)
    # dataframe.to_excel(path_to_AutoPlus_Neuf + "\\test.xlsx")
    # test = ScrappAutoPlusTnNeuf()
    # test.run_whole_process()
    pass
