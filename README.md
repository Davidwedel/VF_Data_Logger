### Disclaimer 1:
This script is for demonstrational purposes only and is not designed to be used in real life. Use at your own risk. I am not responsible for any incorrectly logged data, or any loss, monetary or otherwise, resulting from it. 
### Disclaimer 2: 
The following ReadMe is ChatGPT generated. 

## 🐓 Rotem To Spreadsheet Uploader

This script processes XML files exported from Rotem controllers (used in poultry houses), extracts key environmental and performance data (temperature, light status, feed/water consumption, mortality, etc.), and appends it to a Google Spreadsheet for daily recordkeeping.
### 📦 Features

 Automatically detects yesterday’s files and parses:

* Inside/Outside temperature highs/lows

* Cooler room temperatures (AM/PM)

* Light on/off times

* Mortality, feed, water usage, and average weight

Cleans up old XML files after a set number of days

Uses Google Sheets API to log a daily summary to Google Sheets

### 🔧 Setup
1. Clone the Repository

    ```git clone https://github.com/Davidwedel/rotem--spreadsheet.git```<br>
    ```cd rotem--spreadsheet```

2. Install Dependencies

    Use pip to install required Python packages:

    ```pip install -r requirements.txt```

3. Set Up Google API Credentials

   * Go to the Google Cloud Console

   * Enable the Google Sheets API

   * Create a Service Account

   * Download the credentials.json file into the project root(Note that this file may not be named credentials.json. It will be a JSON file. Rename it.

   * Open your spreadsheet and give editor permissions to the service account’s email (e.g., your-service-account@project.iam.gserviceaccount.com).
## 🔐 Configure secrets.json

1. Copy the data in examplesecrets.json to a file called secrets.json
   * Explanation of Fields
        * spreadsheet_id:                  The ID from thje URL of your Google Sheet<br>
        * range_name:                      The sheet and starting cell to append data (e.g., "Sheet1!A1")<br>
        * path_to_xmls:                    Full path to the folder containing .xml files<br>
        * how_long_to_save_old_files:     Number of days to keep XMLs (0 disables deletion)<br>
        * get_cooler_temp_AM:             Target time to get cooler room temp in the morning (HH:MM:SS format)<br>
        * get_cooler_temp_PM:             Target time for cooler temp in the evening<br>
        * cooler_temp_time_tolerance:     How far from the target time to search for readings (e.g., "00:30")<br>
        * time_zone:                      Your local timezone in IANA format (e.g., "America/Chicago")<br>
        
## ✅ Running the Script

Make sure credentials.json and secrets.json are present, then simply run:

```python nightly_bot.py```

This will:

    Parse yesterday’s XML files

    Append data to your Google Sheet

    Delete old files if enabled

## Information
You will need to set your Rotem to log XML files to your FTP server. <br>
Add the script to cron to run sometime after midnight.

## License

This project is licensed under the GNU GPLv3 License. See the [LICENSE](./LICENSE) file for details.
