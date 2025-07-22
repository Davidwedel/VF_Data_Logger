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
   

#folder where XML files are stored (change if needed)
xmlFolder = "../upload"

#start figuring various things we need to know
today = date.today()

#get yesterday's date, as formatted in the xml filename I.E. YYYYMMDD(20250722)
yesterday = (date.today() - timedelta(days=1)).strftime("%Y%m%d")

#print("Yesterday:" + yesterday)

#file pattern to yesterday's files
yesterdayFiles = os.path.join(xmlFolder, (yesterday+"*.xml"))

matches = glob.glob(yesterdayFiles)

if matches:
    last_yesterdayFile = max(matches, key=lambda f: datetime.strptime(os.path.basename(f)[:14], "%Y%m%d%H%M%S"))
    #print("Last file from yesterday:", last_yesterdayFile)
else:
    print("No files found for yesterday.")

#end figuring various things we need to know

#parse all files from yesterday and average the outside temp
#return outsideHigh, outsideLow, insideHigh, insideLow !!What gets returned!!
databack = dohighandlowtemps(yesterdayFiles)
print(databack)

