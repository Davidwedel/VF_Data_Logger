import csv
import requests
import glob
import os
import xml.etree.ElementTree as ET
from datetime import date, timedelta

def c_to_f(celsius):
    return (celsius * 9/5) + 32

def getthetemps(yesterdayFiles):
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

    if outsideTemps and insideTemps:
        avg_outsideTemp = sum(outsideTemps) / len(outsideTemps)
        avg_insideTemps = sum(insideTemps) / len(insideTemps)
        #print(f"Average OutsideTemperature for day: {avg_temp:.2f}°C from {len(temperatures)} file(s)")
        return avg_outsideTemp, avg_insideTemps
    else:
        print(f"Something failed!")
        return None

#folder where XML files are stored (change if needed)
xmlFolder = "../upload"

#start figuring various things we need to know
today = date.today()

#get yesterday's date, as formatted in the xml filename I.E. YYYYMMDD(20250722)
yesterday = (date.today() - timedelta(days=1)).strftime("%Y%m%d")

#print("Yesterday:" + yesterday)

#file pattern to yesterday's files
yesterdayFiles = os.path.join(xmlFolder, (yesterday+"*.xml"))
#end figuring various things we need to know

#parse all files from yesterday and average the outside temp
#avg_outside_tempF = c_to_f(average_outside_temp(yesterdayFiles))
avg_outside_tempF = getthetemps(yesterdayFiles)

print(avg_outside_tempF)

