import csv
import requests
import glob
import os
import xml.etree.ElementTree as ET
from datetime import date, timedelta, datetime

def c_to_f(celsius):
    return (celsius * 9/5) + 32

def dohighandlowtemps(yesterdayFiles):
    outsideTemps = []
    insideTemps = []
    for filename in glob.glob(yesterdayFiles):
        try: 
            tree = ET.parse(filename)
            root = tree.getroot()

            ##outside temp stuff
            temp_element = root.find(".//OutsideTemperature")
            if temp_element is not None:
                temp = float(temp_element.text)
                outsideTemps.append(temp)
                
            ##inside temp stuff
            temp_element = root.find(".//AverageTemperature")
            if temp_element is not None:
                temp = float(temp_element.text)
                insideTemps.append(temp)
        except Exception as e:
            print(f"Failed to process {filename}: {e}")

    if outsideTemps:
        outsideHigh = max(outsideTemps)
        outsideLow = min (outsideTemps)

    else:
        print(f"Something failed in Outside!")

    if insideTemps:
        insideHigh = max(insideTemps)
        insideLow = min (insideTemps)

    else:
        print(f"Something failed in Inside!")

    return outsideHigh, outsideLow, insideHigh, insideLow
   
def everythingfromlastfile(last_yesterdayFile):
        datawesendback = []
        try: 
            tree = ET.parse(last_yesterdayFile)
            root = tree.getroot()

            ##mortality stuff
            temp_element = root.find(".//TotalDailyFemaleMortality")
            if temp_element is not None:
                temp = int(temp_element.text)
                datawesendback.append(temp)
                
            ##feed consumption stuff
            temp_element = root.find(".//DailyFeed")
            if temp_element is not None:
                temp = int(temp_element.text)
                datawesendback.append(temp)

            ##water consumption stuff
            temp_element = root.find(".//DailyWater")
            if temp_element is not None:
                temp = int(temp_element.text)
                datawesendback.append(temp)
                
            ##avg weight stuff
            temp_element = root.find(".//AverageWeight")
            if temp_element is not None:
                temp = float(temp_element.text)
                datawesendback.append(temp)

            return datawesendback
                
        except Exception as e:
            print(f"Failed to process {last_yesterdayFile}: {e}")

def deleteOldFiles(howmany):
    if howmany == 0:
        print("File Deletion shut off!")
    else:
       day2Delete = (date.today() - timedelta(days=howmany)).strftime("%Y%m%d")
       howManyDeleted = 0
       print(f"Deleting files!")
       for filename in os.listdir(xmlFolder):
           if filename.endswith(".xml") and filename[:8] <= day2Delete:
               howManyDeleted = howManyDeleted + 1
               filepath = os.path.join(xmlFolder, filename)
               #print(f"Deleting: {filepath}")
               os.remove(filepath)
    return howManyDeleted
        
#folder where XML files are stored (change if needed)
xmlFolder = "../upload"

#days. 0 never deletes
howLongToSaveOldFiles = 2

#start figuring various things we need to know

#get yesterday's date, as formatted in the xml filename I.E. YYYYMMDD(20250722)
yesterday = (date.today() - timedelta(days=1)).strftime("%Y%m%d")
#yesterday = date.today().strftime("%Y%m%d")

#print("Yesterday:" + yesterday)

#file pattern to yesterday's files
yesterdayFiles = os.path.join(xmlFolder, (yesterday+"*.xml"))

matches = glob.glob(yesterdayFiles)

if matches:
    last_yesterdayFile = max(matches, key=lambda f: datetime.strptime(os.path.basename(f)[:14], "%Y%m%d%H%M%S"))
    #print("Last file from yesterday:", last_yesterdayFile)
else:
    print("No files found for yesterday. Exiting...")
    exit()

#end figuring various things we need to know

#parse all files from yesterday and average the outside temp
#return outsideHigh, outsideLow, insideHigh, insideLow !!What gets returned!!
databack = dohighandlowtemps(yesterdayFiles)
print(databack)

#returns mortality, feed consumption, water consumption, average weight
databack = everythingfromlastfile(last_yesterdayFile)
print(databack)

#delete all old files, so file doesn't fill up.
howmanydeleted = deleteOldFiles(howLongToSaveOldFiles)
#print(howmanydeleted)
