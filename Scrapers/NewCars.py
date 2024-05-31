from AutomobileTnScrapper import ScrapperAutomobileTnNeuf
from AutomobileTnScrapper import ScrapperAutomobileTnOcc
from AutoPlusScrapper import ScrappAutoPlusTnNeuf
from CleaningProcess import CleaningNewCars


if __name__ == "__main__":
    # test = ScrapperAutomobileTnNeuf()
    # test.run_whole_process()
    # test = ScrappAutoPlusTnNeuf()
    # test.run_whole_process()
    cleaningNewCars = CleaningNewCars()
    cleaningNewCars.cleaning()
