import glob
import os
import xml.etree.ElementTree as ET
from datetime import date, timedelta

#folder where XML files are stored (change if needed)
xmlFolder = "../upload"

#start figuring various things we need to know
today = date.today()

#get yesterday's date, as formatted in the xml filename I.E. YYYYMMDD(20250722)
#comment out this line to search for any day other than yesterday
daytolook = (date.today() - timedelta(days=1)).strftime("%Y%m%d")
#uncomment this line to search for any day other than yesterday
#daytolook = 20250722


#file pattern to day's files
dayFiles = os.path.join(xmlFolder, (daytolook+"*.xml"))
#end figuring various things we need to know


for filename in glob.glob(dayFiles):
    try:
        tree = ET.parse(filename)
        root = tree.getroot()
        temp_element = root.find(".//OutsideTemperature")
        if temp_element is not None:
            temp = float(temp_element.text)
            print(temp)
    except Exception as e:
         print(f"Failed to process {filename}: {e}")
