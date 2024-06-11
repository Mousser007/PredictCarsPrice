import os
from selenium import webdriver


##Affare Config
baseUrlAffare = "https://www.affare.tn/petites-annonces/tunisie/voiture-neuve-occassion-prix-tayara-a-vendre?o=1&t=prix-moins-cher&prix=3000-max"
nativeUrlAffare = "https://www.affare.tn"
##AutoMax Config
baseUrlAutomax = "https://www.automax.tn/voitures-occasion/?prix-from=3000&page=1&trier-par=recent"
nativeUrlAutomax = "https://www.automax.tn"
##Automobile.tn Config
baseUrlAutomobileTn = 'https://www.automobile.tn/fr/occasion/s=sort!date'
baseUrlAutomobileTnNeuf = 'https://www.automobile.tn/fr/neuf'
##AutoPlus Config
baseUrlAutoplus = "https://www.auto-plus.tn/voitures-d-occasion/1/p/1"
baseUrlAutoplusNeuf = 'https://www.auto-plus.tn/les-voitures-neuves'
nativeUrlAutoplus = "https://www.auto-plus.tn/voitures-d-occasion"
##AutoPrix Config
baseUrlAutoprix = "https://www.autoprix.tn/recherche?min_price=4000&max_price=200000&cp=1&sortby=date&is_sold=true&is_price=true&nb=1"
nativeUrlAutoprix = "https://www.autoprix.tn"
##Tayara Config
baseUrlTayara = "https://www.tayara.tn/ads/c/V%C3%A9hicules/Voitures/t/Occasion/?minPrice=10000&maxPrice=1000000000&page=1"
nativeUrlTayara = "https://www.tayara.tn"
##Path Config
path_to_DataPostColumnsStandardisedNeuf = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Data', 'DataPostColumnsStandardised', 'Neuf')
path_to_DataPostColumnsStandardisedOccasion = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Data', 'DataPostColumnsStandardised', 'Occasion')
path_to_NewCarsReady = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Data', 'DataNewCarsReady')
path_to_CarsDatabase = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Data', 'CarsDatabase')
path_to_DataPostCleaning = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Data', 'DataPostCleaning')
path_to_DataPostMl = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Data', 'DataPostMl')
path_to_DataPostScraping = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Data', 'DataPostScraping')
path_to_DataPourSimulateur = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Data', 'DataPourSimulateur')
path_to_RequirementsFiles = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ML', 'RequirementsFiles')
##Web driver Config
options = webdriver.ChromeOptions()
options.add_argument('--headless')  # Run in headless mode
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
options.add_argument('--disable-gpu')
options.add_argument("--disable-javascript")
options.add_argument('--window-size=1920x1080')
options.add_argument(
"user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
driverConfig = webdriver.Chrome(options=options)