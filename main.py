import csv
import requests
import glob
import os
import xml.etree.ElementTree as ET
from datetime import date, timedelta

def c_to_f(celsius):
    return (celsius * 9/5) + 32

def average_outside_temp(yesterdayFiles):
    temperatures = []

    for filename in glob.glob(yesterdayFiles):
        try:
            tree = ET.parse(filename)
            root = tree.getroot()
            temp_element = root.find(".//OutsideTemperature")
            if temp_element is not None:
                temp = float(temp_element.text)
                temperatures.append(temp)
        except Exception as e:
            print(f"Failed to process {filename}: {e}")

    if temperatures:
        avg_temp = sum(temperatures) / len(temperatures)
        #print(f"Average OutsideTemperature for day: {avg_temp:.2f}°C from {len(temperatures)} file(s)")
        return avg_temp
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
avg_outside_tempF = c_to_f(average_outside_temp(yesterdayFiles))

print(avg_outside_tempF)

