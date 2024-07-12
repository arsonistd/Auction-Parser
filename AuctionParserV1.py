## Auction Parser V1
## 5/25/24

#Run each auction in its own thread

from bs4 import BeautifulSoup
from selenium.webdriver import Chrome
from selenium.webdriver import ChromeOptions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
import tkinter as tk
import customtkinter as ctk
import requests
import time
import re
import subprocess
import threading


resultFile = "Result.txt"
resultFilePath = "C:/Users/Alianware/Documents/Python Projects/Auction HTML Parser/Result.txt"
filteredResultFile = "FilteredResult.txt"
filteredResultFilePath = "C:/Users/Alianware/Documents/Python Projects/Auction HTML Parser/FilteredResult.txt"
filtersFile = "Filters.txt"
url = "https://www.quarterpriceauction.com"
filter_words = ['dewalt', "anker", "elegoo", "3D Printer"]
ScanAllAuctions = False

mainPage = requests.get(url)
doc = BeautifulSoup(mainPage.text, "html.parser")
auctions = doc.find_all("a", class_ = "enterAuction")
testAuction = auctions[0] 

# Create a regular expression pattern to match any of the filter words
pattern = re.compile(r'\b(?:' + '|'.join(map(re.escape, filter_words)) + r')\b', re.IGNORECASE)





def filter_text(text):
    # Find all matches of filter words in the text
    matches = pattern.findall(text)
    return matches

def checkFilter(text):
    return any(word.lower() in filter_words for word in filter_text(text))

# Scrapes target webpage that uses specific auction web setup
def scrapeWebPage(TargetUrl):

    chrome_options = ChromeOptions()

    statusLabel.configure(text="Status: Parsing...")
    statusLabel.update()


    # Opening the page with selenium because its loaded with javascript
    driver = Chrome(options=chrome_options)
    driver.get(TargetUrl)

    driver.set_window_position(-10000, 0, windowHandle='current')

    delay = 3 # seconds
    try:
        print("Testing for object")
        myElem = WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.CLASS_NAME, 'title')))
        print("Found object")
    except TimeoutException:
        print("Website exhausted too much time")

    driver.set_window_position(-10000, 0, windowHandle='current')

    #Search the loaded HTML with BeatifulSoup
    auctionDoc = BeautifulSoup(driver.page_source, "html.parser")
    lots = auctionDoc.find_all("span", class_ = "title")

    #Write all the lots onto a text doccument
    file = open(resultFile, "a", encoding="utf-8")
    filteredFile = open(filteredResultFile, "a", encoding="utf-8")
    for lot in lots:
        file.write(lot.text+"\n")
        if checkFilter(lot.text):
            print("Adding to the filter text doccument")
            filteredFile.write(lot.text+"\n")
    file.close
    filteredFile.close

    print("Successfully scraped " + TargetUrl)
    statusLabel.configure(text="Status: Successfully parsed all auctions")
    statusLabel.update()

    return lots

def scrapeAllAuctions():
    print("Scraping all auctions!")

    #Clear both text files
    open(resultFile, 'w').close()
    open(filteredResultFile, 'w').close()

    statusLabel.configure(text="Status: Initializing to parse all auctions!")
    statusLabel.update()

    time.sleep(0.5)

    for auction in auctions:
        newUrl = url + auction["href"]

        #Cycle through the pages to make sure you have all the lots
        ScrapingPages: bool = True
        PageNumber: int = 1

        #Will loop through pages till a empty page is recieved
        while ScrapingPages: 
            print("Starting to scrape")
            ReturnedLots = scrapeWebPage(newUrl+"?page="+str(PageNumber))

            if len(ReturnedLots) == 0: #Page has lots theirfor is not empty
                ScrapingPages = False
            
            PageNumber = PageNumber + 1
            if ScrapingPages == False:
                print("All the pages have been scraped")
                break

    print("All auctions have been scraped")




#GUI


ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

root = ctk.CTk()
root.geometry("900x450")
root.minsize(900,450)
root.maxsize(900,450)
root.title("Auction Parser V1")
root.grid_columnconfigure((0,1,2), weight=1, uniform="column")

mainTitle = ctk.CTkLabel(master=root, text="Auction Parser V1", font=ctk.CTkFont(size=30, weight="bold"))
mainTitle.grid(row = 0, column = 1,  pady = 10, padx = 10, sticky="snew")

statusLabel = ctk.CTkLabel(master=root, text="Status : Idle", font=ctk.CTkFont(size=13))
statusLabel.grid(row = 0, column = 0,  pady = 10, padx = 10, sticky="snew")

Buttonframe = ctk.CTkFrame(master=root)
Buttonframe.grid(row = 1, column = 0,  pady = 10, padx = 10, rowspan = 12, sticky="snew")
Buttonframe.grid_rowconfigure(0, weight=1)
Buttonframe.grid_columnconfigure(0, weight=1)

FilterOptionsFrame = ctk.CTkFrame(master=root)
FilterOptionsFrame.grid(row = 1, column = 1, pady = 10, padx = 10, rowspan = 3, sticky="snew")
FilterOptionsFrame.grid_rowconfigure(0, weight=1)
FilterOptionsFrame.grid_columnconfigure(0, weight=1)

FilterFrame = ctk.CTkFrame(master=root)
FilterFrame.grid(row = 4, column = 1, pady = 10, padx = 10, rowspan = 3, sticky="snew")
FilterFrame.grid_rowconfigure(0, weight=1)
FilterFrame.grid_columnconfigure(0, weight=1)

class ScrollableFrame(ctk.CTkScrollableFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        # add widgets onto the frame...
        self.label = ctk.CTkLabel(self)
        self.label.grid(row=0, column=0, padx=20)

FilterScrollableFrame = ScrollableFrame(master=FilterFrame, width=300, height=200)
FilterScrollableFrame.grid(row=0, column=0, padx=20, pady=20)

ResultFrame = ctk.CTkFrame(master=root)
ResultFrame.grid(row = 1, column = 2, pady = 10, padx = 10, rowspan = 12, sticky="snew")

parseAuctionsButton = ctk.CTkButton(Buttonframe, text="Parse Auctions", width = 200, height = 30, command=threading.Thread(target=scrapeAllAuctions).start)
parseAuctionsButton.grid(row = 0, column = 0,  pady = 10, padx = 20)

clearResultsButton = ctk.CTkButton(Buttonframe, text="Clear Results", width = 200, height = 30, fg_color="red", command=(lambda:open(resultFile, 'w').close()))
clearResultsButton.grid(row = 1, column = 0,  pady = 10, padx = 20)
clearfilteredResultsButton = ctk.CTkButton(Buttonframe, text="Clear Filtered Results", width = 200, height = 30, fg_color="red", command=(lambda:open(filteredResultFile, 'w').close()))
clearfilteredResultsButton.grid(row = 2, column = 0, pady = 10, padx = 20)

filterResultsButton = ctk.CTkButton(Buttonframe, text="Filter Results", width = 200, height = 30)
filterResultsButton.grid(row = 3, column = 0, pady = 10, padx = 20)

openResultsButton = ctk.CTkButton(Buttonframe, text="Open Results", width = 200, height = 30, fg_color="green", command=(lambda:subprocess.Popen(['notepad.exe', resultFile])))
openResultsButton.grid(row = 4, column = 0, pady = 10, padx = 20)
openFilteredResultsButton = ctk.CTkButton(Buttonframe, text="Open Filtered Results", width = 200, height = 30, fg_color="green", command=(lambda:subprocess.Popen(['notepad.exe', filteredResultFile])))
openFilteredResultsButton.grid(row = 5, column = 0, pady = 10, padx = 20)

addFilterEntry = ctk.CTkEntry(FilterOptionsFrame)
addFilterEntry.grid(row = 0, column = 0, pady = 10, padx = 20, sticky="snew")
addFilterButton = ctk.CTkButton(FilterOptionsFrame, text="Add Filter", width = 200, height = 30, fg_color="green", command=(lambda:subprocess.Popen(['notepad.exe', filteredResultFile])))
addFilterButton.grid(row = 1, column = 0, pady = 10, padx = 20, sticky="snew")



root.mainloop()


