from AutomobileTnScrapper import ScrapperAutomobileTnNeuf
from AutomobileTnScrapper import ScrapperAutomobileTnOcc
from AutoPlusScrapper import ScrappAutoPlusTnNeuf
from CleaningProcess import CleaningNewCars


if __name__ == "__main__":
    # test = ScrapperAutomobileTnNeuf()
    test2 = ScrapperAutomobileTnOcc()
    soup = test2.parsing_page_source('https://www.automobiles.tn/fr/neuf/audi/s')
    print(soup)
    # test.run_whole_process()
    # test = ScrappAutoPlusTnNeuf()
    # test.run_whole_process()
    # cleaningNewCars = CleaningNewCars()
    # cleaningNewCars.cleaning()
