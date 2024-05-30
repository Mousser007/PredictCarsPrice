from selenium import webdriver
from bs4 import BeautifulSoup
import time
from Cleaning.ColumnStandardiser import ColumnsStandardiser
from selenium.common.exceptions import WebDriverException
from Cleaning.BrandModelExtraction import ExtractionMarqueModele
import pandas as pd 
from Cleaning.Cleaner import *
from Config import *
# import logging
#
# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger()


class ScrapperAutomobileTnOcc:
    
    def __init__(self):
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')  # Run in headless mode
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument("--disable-javascript")
        options.add_argument('--window-size=1920x1080')
        options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
        self.driver = webdriver.Chrome(options=options)
        self.baseUrl = 'https://www.automobile.tn/fr/occasion/s=sort!date'
        # self.driver = webdriver.Chrome()
        # self.baseUrl = 'https://www.automobile.tn/fr/occasion/s=sort!date'
        # self.pageInitiale = 1
        # self.pageFinale = 2
        
    def parsing_page_source(self, url):
        try:
            self.driver.get(url)
            time.sleep(20)
        except WebDriverException:
            self.driver.refresh()
            time.sleep(20)
        return BeautifulSoup(self.driver.page_source,'html.parser') if BeautifulSoup(self.driver.page_source,'html.parser') else None
    
    def extract_cars_urls(self, pageUrl):
        soup = self.parsing_page_source(pageUrl)
        atags = soup.find_all('a', {'class': 'occasion-link-overlay'})
        return [a.get('href')[12:] for a in atags]
    
    def extract_data(self, soup):
        data = {}
        atags = soup.find('div', {'class': 'box d-none d-md-block'})
        listeDescCaract = atags.find_all('li')
        for li_tag in listeDescCaract:
            spec_name = li_tag.find('span', {'class': 'spec-name'}).text.strip()
            spec_value = li_tag.find('span', {'class': 'spec-value'}).text.strip()
            data[spec_name] = spec_value
        
        Modele = soup.find('h1').text.strip()
        Prix = soup.find('div', {'class': 'price'}).text.strip()
        data['Modele'] = Modele
        data['Prix'] = Prix
        
        atagsSpec = soup.find('div', {'class': 'col-md-6 mb-3 mb-md-0'})
        listeDesSpecification = atagsSpec.find_all('li')
        for li_tag in listeDesSpecification:
            spec_name = li_tag.find('span', {'class': 'spec-name'}).text.strip()
            spec_value = li_tag.find('span', {'class': 'spec-value'}).text.strip()
            data[spec_name] = spec_value
        
        return data
    
    def scrape(self, pageInit, pageFinal):
        urls=[]
        try:
            for i in range(pageInit,pageFinal+1):
                urls.extend(self.extract_cars_urls(self.baseUrl+'/'+str(i)+'?sort=date'))
            all_Data={}
            for index, url in enumerate(urls, start = 1):
                soup = self.parsing_page_source(self.baseUrl+url)
                data = self.extract_data(soup)
                all_Data[f'dict{index}'] = data
        finally:
            self.driver.quit()
        return all_Data
    
    def automobile_tn_scrapper_runner(self, OutputFileName):
        standardize = ColumnsStandardiser()
        data = self.scrape(self.pageInitiale, self.pageFinale)
        dataStandardized = standardize.column_standardize(data)
        file_path = os.path.join(path_to_DataPostScraping, 'AutomobileTn', 'Occasion', OutputFileName + '.csv' )
        standardize.load_data_in_csv_file(dataStandardized, file_path)
    
    def automobile_tn_columns_standardise(self, dataframe):
        # il faut recoder cette methode car elle comporte des erreur au niveau du modele et modéle
        # supp modele et renommer modéle en modele en faisant le necessaire
        dataframe= dataframe.rename(columns={"Kilométrage":"Kilometrage",
                                             "Mise en circulation":"Annee",
                                             "Énergie":"Energie" ,
                                             "Boite vitesse":"BoiteVitesse",
                                             "Puissance fiscale":"PuissanceFiscale",
                                             "Couleur extérieure":"Couleur"})
        dataframe = dataframe.drop(columns={"Couleur intérieure", "Date de l'annonce",
                                            "Nombre de places","Nombre de portes","Transmission","Sellerie"})
        cln = cleaner()
        dataframe = cln.eliminate_unnamed_columns(dataframe)
        return dataframe
    
    def run_whole_process(self):
        self.pageInitiale = 1
        self.pageFinale = 2
        self.automobile_tn_scrapper_runner("FileAutomobileTnPostScrap")
        file_path = os.path.join(path_to_DataPostScraping, 'AutomobileTn', 'Occasion', 'FileAutomobileTnPostScrap.csv')
        AutomobileTnFile = pd.read_csv(file_path,sep=';')
        AutomobileTnData = self.automobile_tn_columns_standardise(AutomobileTnFile)
        AutomobileTnData.to_csv(path_to_DataPostCleaning+"\\FileAutomobileTnClean.csv")


class ScrapperAutomobileTnNeuf:

    def __init__(self):
        self.scrapOcc = ScrapperAutomobileTnOcc()
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
        self.baseUrl = 'https://www.automobile.tn/fr/neuf'

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
        description = soup.find('h3', {'class': 'page-title'}).text.strip()
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
            for brandUrl in listBrandsUrls:
                soupBrandPage = self.scrapOcc.parsing_page_source(self.baseUrl + brandUrl)
                listCarsUrls.extend(self.extract_cars_url(soupBrandPage))
            all_Data = {}
            for index, carUrl in enumerate(listCarsUrls, start=1):
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
        data_directory = os.path.join(path_to_DataPostColumnsStandardisedNeuf,
                                      "AutomobileTnFilePostColumnsStandardised")
        AutomobileTnDataPostStandardise.to_csv(data_directory + ".csv")


## MAIN ##
if __name__ == "__main__":
    # dataframe = pd.read_excel("D:\\PredictCarsPrice\\Data\\DataPostScraping\\AutomobileTnNeuf.xlsx")
    # test = ScrapperAutomobileTnNeuf()
    # dataframe = test.automobile_tn_columns_standardise(dataframe)
    # dataframe.to_excel("D:\\PredictCarsPrice\\Data\\DataPostScraping\\testautomobiletn.xlsx")
    # test = ScrapperAutomobileTnNeuf()
    # test.run_whole_process()
    pass
