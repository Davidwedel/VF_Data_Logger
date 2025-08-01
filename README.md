### Disclaimer 1:
This script is for demonstrational purposes only and is not designed to be used in real life. Use at your own risk. I am not responsible for any incorrectly logged data, or any loss, monetary or otherwise, resulting from it. 
### Disclaimer 2: 
The following ReadMe is ChatGPT generated. 

### Disclaimer 3:
I am not a "good" programmer. If it works, I assume it is right. If you know your stuff, and improve the code structure/readeability, I will be happy to merge any Pull Requests.

### Disclaimer 4: 
This whole project is in development stage.

## 🐓 Rotem To Unitas

This project is designed to streamline recordkeeping on a Vital Farms Chicken barn. It processes XML files exported from the Rotem controller, extracts key environmental and performance data (temperature, light status, feed/water consumption, mortality, etc.), and appends it to a Google Spreadsheet for daily recordkeeping. Then, sends the data to Unitas website, and autofills the values so the User just needs to look over the data, and save.
### 📦 Features

 Automatically detects yesterday’s files and parses:

* Inside/Outside temperature highs/lows

* Cooler room temperatures (AM/PM)

* Light on/off times

* Mortality, feed, water usage, and average weight

Cleans up old XML files after a set number of days

Uses Google Sheets API to log a daily summary to Google Sheets

Allows the User to enter data not contained in the Rotem into the spreadsheet.

### 🔧 Setup
Requirements:
* You will need to have computer with a screen, running a Linux distro, on the same local network as your Rotem Communicator. This software may not work on Windows.
* You will need to have Python, Git, vsftpd, and Pip installed on the computer. There are better guides elsewhere on the internet than I can write up here.
1. Set up FTP Server/Client<br>
    * Set up FTP server on your computer:<br>
        * Coming soon...<br>

    * Set up FTP client on RotemWeb.<br>
        Consult the Rotem Communicator Manual, and go to page 88.<br>
        https://munters.zendesk.com/hc/en-us/article_attachments/21308920512156<br>
        Using that, fill out the General Settings tab on RotemWeb.<br>
        Farm Code: Leave this one blank.<br>
        Integrator Name: Other<br>
        Dealer: Other<br>
        Data Provider: Other<br>
        Accept the license and Save.<br>

        Navigate to Data Collection page.<br>
        Select "FTP", not "SFTP"<br>
        Host Address: IP Address of your server computer.<br>
        Port Number: 21<br>
        Target Folder: /upload<br>
        User Name: ftp<br>
        Password: Use your email address<br>

2. Clone the Repository

    ```cd /srv/ftp```<br>
    ```sudo mkdir VF_Data_Logger```<br>
    ```sudo chown -R (yourusername) VF_Data_Logger```<br>
    ```git clone https://github.com/Davidwedel/VF_Data_Logger.git```<br>
    ```cd VF_Data_Logger```<br>
    ```python3 -m venv .venv```<br>

3. Install Dependencies

    Use pip to install required Python packages:

    ```.venv/bin/pip install -r requirements.txt```

4. Set Up Google API Credentials

   * Go to the Google Cloud Console

   * Enable the Google Sheets API

   * Create a Service Account

   * Download the credentials.json file into the project root(Note that this file may not be named credentials.json. It will be a JSON file. Rename it.

   * Open your spreadsheet and give editor permissions to the service account’s email (e.g., your-service-account@project.iam.gserviceaccount.com).
## 🔐 Configure secrets.json

1. Copy the data in examplesecrets.json to a file called secrets.json
   * Explanation of Fields
        * spreadsheet_id:                  The ID from the URL of your Google Sheet<br>
        * range_name:                      The sheet and starting cell to append data (e.g., "Sheet1!A1")<br>
        * path_to_xmls:                    Full path to the folder containing .xml files<br>
        * how_long_to_save_old_files:     Number of days to keep XMLs (0 disables deletion)<br>
        * get_cooler_temp_AM:             Target time to get cooler room temp in the morning (HH:MM:SS format)<br>
        * get_cooler_temp_PM:             Target time for cooler temp in the evening<br>
        * cooler_temp_time_tolerance:     How far from the target time to search for readings (e.g., "00:30")<br>
        * time_zone:                      Your local timezone in IANA format (e.g., "America/Chicago")<br>
        
## ✅ Running the Script

Make sure credentials.json and secrets.json are present, then simply run:

```.venv/bin/python nightly_bot.py```

This will:

    Parse yesterday’s XML files

    Append data to your Google Sheet

    Delete old files if enabled

## Information
You will need to set your Rotem to log XML files to your FTP server. <br>
Add the script to cron to run sometime after midnight.

## License

This project is licensed under the GNU GPLv3 License. See the [LICENSE](./LICENSE) file for details.
