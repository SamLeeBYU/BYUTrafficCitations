import pandas as pd
import threading
import time
import re
import os
import datetime

#import selenium libraries
from selenium import webdriver
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

DATA = pd.DataFrame()
def save_data(data, save=False):
    global DATA
    if DATA.empty:
        DATA = data
    else:
        DATA = pd.concat([DATA, data]).reset_index(drop=True)
    
    if save:
        #Clean the data before saving it to the file
        DATA["Officer"] = DATA["Citation"].apply(lambda x: re.search(r'P(\d)', x).group(1))
        DATA["Fine"] = DATA["Fine"].apply(lambda x: float(x.replace('$', '').replace(',', '')) if isinstance(x, str) else x)
        DATA["Residence"] = DATA["License Plate/Vin"].str.split().str[0]
        DATA["IssuedDate"] = pd.to_datetime(DATA["Issued"], format='%b %d, %Y %I:%M %p').dt.strftime('%Y-%m-%d')
        DATA["IssuedTime"] = pd.to_datetime(DATA["Issued"], format='%b %d, %Y %I:%M %p').dt.strftime('%I:%M %p')
        
        if os.path.exists("ParkingCitations.csv"):
            DATA.to_csv("ParkingCitations.csv", mode='a', index=False, header=False)
        else:
            DATA.to_csv("ParkingCitations.csv", index=False)

        DATA = pd.DataFrame()

PATH = "Driver/chromedriver.exe"

def selenium_driver():
    
    service = Service(PATH) #Service(ChromeDriverManager().install())

    options = Options()
    driver = webdriver.Chrome(service=service, options=options)
    return driver

def measure_time(start_time, s, threshold=10.1):
    counting = True
    while counting and not s.citation_loaded:
        current = time.perf_counter() - start_time
        if current >= threshold:
            counting = False
            s.flag = True
        time.sleep(0.1)

#Create the chrome driver that can be referred to globally
driver = None

class Scraper():
    
    def __init__(self, url):
        #Define the url to scrape
        self._url = url

        #Starting time
        self.start_time = time.perf_counter()
        
        #Some properties that will help us see if the citation has been found
        self._citation_loaded = False
        self._flag = False
        
        #Define parameters of loop
        self.officers = range(1, 10+1)
        self.index = range(1, 99999+1)

    def go(self):
        driver.get(self._url)

    def calculateTime(self):
        self.end_time = time.perf_counter()
        total_seconds = self.end_time - self.start_time

        hours = total_seconds // 3600
        remaining_seconds = total_seconds % 3600
        minutes = remaining_seconds // 60
        seconds = remaining_seconds % 60

        print(f"\nTotal seconds elapsed: {total_seconds:.4f}")
        print(f"That's {hours} hours, {minutes} minutes, and {seconds:.4f} seconds.\n")

        return total_seconds
        
    @property
    def url(self):
        return self._url
    
    @property
    def citation_loaded(self):
        return self._citation_loaded
    
    @property
    def flag(self):
        return self._flag
    
    @flag.setter
    def flag(self, change):
        self._flag = change
    
    @staticmethod
    def find_citation():
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CLASS_NAME, "v-btn__content"))
        )
        find_citation_btn = driver.find_elements(By.CLASS_NAME, "v-btn__content")[0]
        find_citation_btn.click()
    
    @staticmethod
    def send_keys(data={"officer": 1, "index": 0}):
        index = "0"*(5-len(str(data["index"])))+str(data["index"])
        key = f"P{data['officer']}-{index}"
        #print(key)
        
        #Search the key into the search bar
        
        #Sometimes dynamically loaded websites will spoof the identifiers of their web elements
        #This makes it harder to consistently identify.
        
        #One solution is to use XPATH
        #Another solution is to find the unique combination of nested HTML tags and target that.
        
        #i.e. if I know the link (<a> tag) I want to target is always the first link in the p tags of every
        #div that can be identified with a positional or classical identifier, then I can identify the <a> tag
        #even if the <a> isn't explicitly identifiable through other identifiers.
        
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, ".v-text-field__slot input"))
        )
        input_field = driver.find_elements(By.CSS_SELECTOR, ".v-text-field__slot input")[0]
        driver.execute_script("arguments[0].value = '';", input_field)
        input_field.send_keys(key)
        
        #Search the citation
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, ".v-input__append-inner button"))
        )
        search_btn = driver.find_elements(By.CSS_SELECTOR, ".v-input__append-inner button")[0]
        search_btn.click()
    
    def get_data(self):
        citation_data = driver.find_elements(By.CSS_SELECTOR, ".v-card__text .col")
        no_data_text = driver.find_elements(By.CSS_SELECTOR, ".v-card__text .text-center h4")
        while not self.flag and len(citation_data) < 1 and len(no_data_text) < 1:
            citation_data = driver.find_elements(By.CSS_SELECTOR, ".v-card__text .col")
            no_data_text = driver.find_elements(By.CSS_SELECTOR, ".v-card__text .text-center h4")
            time.sleep(0.1)
        
        if len(no_data_text) >= 1:
            return pd.DataFrame()
        else:
            #Now we need to parse the data into a pandas data frame
            
            #Additional information about the citation if it exists and whether or not they paid the ticket
            additionalInfo = self.checkPayment()
            
            return pd.concat([self.format_text([el.text for el in citation_data]), additionalInfo], axis=1)
    
    @staticmethod
    def format_text(text_arr):
        #Takes the text data and returns a formatted pandas frame
        cols = [x.split(":")[0] for x in text_arr]
        data = [x.split(":", 1)[1].strip() if ":" in x else x.strip() for x in text_arr]
        
        row = pd.DataFrame(data, cols).transpose()
        return row

    @staticmethod
    def checkPayment():
        #Check to see if the payment is available
        #We can assume that the buttons to appeal and pay have loaded when the citation has loaded so we don't need to load again
        buttons = driver.find_elements(By.CSS_SELECTOR, ".v-card__text .text-center button")
        
        citationInfo = {"CitationText": None,
                        "Unpaid": False}
        if len(buttons) > 0:
            if len(buttons) > 1:
                citationInfo = {"CitationText": buttons[0].text,
                                "Unpaid": True}
            elif len(buttons) == 0:
                #We have to determine what kind of information is left to be scraped
                if "APPEAL" in buttons[0].text.upper():
                    citationInfo = {"CitationText": buttons[0].text,
                                    "Unpaid": False}
                elif "PAY" in buttons[0].text.upper():
                    citationInfo = {"CitationText": None,
                                    "Unpaid": True}
        #Two columns to be merged with the row that scrapes the general information
        return pd.DataFrame.from_dict(citationInfo, orient='index').T

    def main_loop(self):
        self.go()
        self.find_citation()
        for i in self.officers:
            j = 0
            while j < len(self.index):
                self._citation_loaded = False

                #Reset the flag:
                if self._flag == True:
                    self._flag = False
                    self.go()
                    self.find_citation()

                #Time how long it takes to scrape each citation
                start_time = time.perf_counter()

                # Create and start the thread for measuring time
                time_thread = threading.Thread(target=measure_time, args=(start_time,self))
                time_thread.start()

                try:
                    self.send_keys({"officer": i, "index": j})
                    
                    #Store the data in the RAM
                    #Save it to a file when it is the last index
                    #i.e. save it to a file when we are done scraping each officer's citations
                    scraped_data = self.get_data()
                    if not scraped_data.empty:
                        save_data(scraped_data, save = j == len(self.index)-1)
                    else:
                        print("No data")
                    self._citation_loaded = True
                except Exception as e:
                    now = datetime.datetime.now()
                    index = "0"*(5-len(str(i)))+str(j)
                    key = f"P{i}-{index}"
                    error_message = f"{now}: {str(e)};\nThere was an error sending the keys or scraping the data: {key}"
                    with open("errors.txt", "a") as f:
                        f.write(error_message + "\n\n")
                    #self._flag = True

                #Join the current thread
                time_thread.join()
                print(f"Execution time: {time.perf_counter()-start_time:.6f}\n")

                print("Most recent data scraped:")
                print(DATA.tail(5))

                if j % 10 == 0:
                    self.calculateTime()

                if self._flag:
                    #This property can only be set true by the measure_time thread
                    j -= 1

                #Generally increase the jth index after each iteration
                j += 1

        print("Finished scraping all the data.")
        self.calculateTime()

if __name__ == "__main__":
    driver = selenium_driver()

    scraper = Scraper("https://cars.byu.edu/citations/")
    scraper.go()

    user_input = input("Are you logged in yet? (y/n): ").rstrip().upper()

    while user_input != "Y":
        print("Waiting for user to log in...")
        input("Press any key to continue...")
        user_input = input("Are you logged in yet? (y/n): ").rstrip().upper()
    
    scraper.main_loop()