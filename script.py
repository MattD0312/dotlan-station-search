from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver import Keys, ActionChains
import re

browser = webdriver.Firefox()

#Amarr-related URLs
urlList = [
    "https://evemaps.dotlan.net/svg/Aridia.svg",
    "https://evemaps.dotlan.net/svg/Kor-Azor.svg",
    "https://evemaps.dotlan.net/svg/Kador.svg",
    "https://evemaps.dotlan.net/svg/Tash-Murkon.svg",
    "https://evemaps.dotlan.net/svg/Domain.svg",
    #"https://evemaps.dotlan.net/svg/The_Bleak_Lands.svg",  #does not work if no stations due to occupancy table
    #"https://evemaps.dotlan.net/svg/Devoid.svg",           #does not work if no stations due to occupancy table
    "https://evemaps.dotlan.net/svg/Derelik.svg",
    "https://evemaps.dotlan.net/svg/Khanid.svg"
]

#load up evemaps.dotlan to accept cookies
browser.get("https://evemaps.dotlan.net/")
browser.find_element(By.XPATH, "/html/body/div[19]/div/div/div[2]/div/div/div/button[2]").click() #click Accept

#Required Services
requiredList = ["Refinery (50%)", "Repair", "Factory", "Research"]
acceptable = False #need to make true when services requirements are met

toBeWritten = "The following is a list of stations that have full services minus Cloning, in Amarr regions that don't have any faction warfare systems (meaning not Bleak Lands and Devoid)\n"
toBeWritten += "Created with Selenium webscraping evemaps.dotlan.net\n" 

for url in urlList:
    systemName = " ".join(re.findall(r"([A-Z][a-z]+)", url)) #get system name
    toBeWritten+="\n_____"+systemName+"_____"

    browser.get(url)

    systems = browser.find_element(By.ID, "sysuse")
    for system in systems.find_elements(By.XPATH, "*"):
        ActionChains(browser)\
            .move_to_element(system)\
            .key_down(Keys.CONTROL)\
            .click()\
            .perform()
    
    original_tab = browser.current_window_handle
    empty = False #need to set this to true when a system has no stations (AKA no station table)

    #iterate through each system
    for tab in browser.window_handles:
        if tab != original_tab:
            browser.switch_to.window(tab)
            try: #look at each station
                stationsTable = browser.find_element(By.XPATH, "/html/body/div[1]/div[1]/div[2]/div[2]/table[2]/tbody") #if no stations this fails
                stations = stationsTable.find_elements(By.XPATH, "*")
                empty = False
            except: #no stations
                empty = True
            
            if (not empty):
                header = True
                for station in stations:

                    if (header): #need to skip first <tr>, not actually a station
                        header = False
                        continue

                    stationName = station.find_element(By.XPATH, ".//td[1]").text
                    services = station.find_element(By.XPATH, ".//td[4]").text

                    acceptable = all(service in services for service in requiredList)

                    if (acceptable):
                        toBeWritten+="\n"+stationName
                    
            browser.close()
            browser.switch_to.window(original_tab)
    
    print(systemName + " done!") #logging in console

print("Complete!!")
endFile = open("goodStations.txt", 'w')
endFile.write(toBeWritten)
endFile.close()