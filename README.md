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

Automatically fills out the data in the Unitas Website, so all the User has to do is look over the data and Save.

### 🔧 Setup
Requirements:
* You will need to have computer with a screen, running a Linux distro (I recommend Fedora XFCE, it's what I'm using, so it's most likely to work) , on the same local network as your Rotem Communicator. This software may (will) not work on Windows.
* You will need to have Git installed on the computer.
1. Set up FTP Client on RotemNet Web<br>

    Click the gear icon and go to Farm Settings.<br>
    ![Error](./README_imgs/farm_stuff.png)<br>
    <br>
    Go to the "General Settings" page.
    <br>
    <br>
    ![Error](./README_imgs/general.png)<br>
    Configure it like the above image. Then save it.<br>

    Then go to the "Data Collection" page<br>

    ![Error](./README_imgs/data_collection.png)<br>
    Configure it like the above image. Then save it.<br>

    If you run into trouble, try consulting the Rotem Communicator Manual. The FTP Client settings are on page 88.<br>
    https://munters.zendesk.com/hc/en-us/article_attachments/21308920512156<br>

2. Install Git.

    This section, and the next section are all commands run in the Terminal, or Command Line. <br>
    Open the Terminal. Most times, this is done by typing ctrl-alt-t.<br>
    If using Fedora: ```sudo dnf install git```

    If using Ubuntu/Debian/Mint: ```sudo apt install git```
        


3. Clone the Repository

    ```cd ~```<br>
    ```git clone https://github.com/Davidwedel/VF_Data_Logger.git```<br>
    ```cd VF_Data_Logger```
    ```bash install.sh```

4. Set Up Google API Credentials

   * Go to the [Google Cloud Console](https://console.cloud.google.com/)

   * Enable the Google Sheets API

   * Create a Service Account

   * Download the credentials.json file into the project root(Note that this file may not be named credentials.json. It will be a JSON file. Rename it.

   * Open your spreadsheet and give editor permissions to the service account’s email (e.g., your-service-account@project.iam.gserviceaccount.com).
        
## ✅ Running the Script

Make sure credentials.json and secrets.json are present, then simply run:

```.venv/bin/python main.py```

## License

This project is licensed under the GNU GPLv3 License. See the [LICENSE](./LICENSE) file for details.
