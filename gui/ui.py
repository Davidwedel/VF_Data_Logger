import webbrowser
import tkinter as tk
from tkinter import filedialog, messagebox, Toplevel
import json
import os

CONFIG_FILE = "../secrets.json"
GOOGLE_SHEET_COPY = "https://docs.google.com/spreadsheets/d/1Hkw_o8hdZHK3YLs8V5oBWMliJEVMIa8vcZzKqIVdKF0/copy"
SERVICE_NAME = "vf_data_logger.service"

DEFAULT_CONFIG = {
    "spreadsheet_id": "",
    "xml_to_sheet_range_name": "",
    "path_to_xmls": "",
    "how_long_to_save_old_files": 2,
    "get_cooler_temp_AM": "06:00:00",
    "get_cooler_temp_PM": "18:00:00",
    "cooler_temp_time_tolerance": "00:30:00",
    "time_zone": "America/Chicago",
    "Unitas_Username": "",
    "Unitas_Password": "",
    "Farm_ID": "",
    "House_ID": "",
    "Timeout": "",
    "sheet_to_unitas_range_name": ""
}

FIELD_LABELS = {
    "spreadsheet_id": "Google Spreadsheet ID",
    "how_long_to_save_old_files": "Days to Keep Old Files (0 to disable, 2 recommended)",
    "get_cooler_temp_AM": "Get Cooler Temp Time AM",
    "get_cooler_temp_PM": "Get Cooler Temp Time PM",
    "time_zone": "Time Zone",
    "Unitas_Username": "Unitas Username",
    "Unitas_Password": "Unitas Password",
    "Farm_ID": "Unitas Farm ID",
    "House_ID": "Unitas House Id"
}

TIME_FIELDS = [
    "get_cooler_temp_AM",
    "get_cooler_temp_PM",
    "cooler_temp_time_tolerance"
]

VISIBLE_FIELDS = list(FIELD_LABELS.keys())


class ConfigEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("Configuration Editor")
        self.entries = {}
        self.config = DEFAULT_CONFIG.copy()
        self.load_config()

        # Main frame using grid
        main_frame = tk.Frame(root)
        main_frame.grid(row=0, column=0, padx=10, pady=10)

        # Hamburger menu button at top-right
        menu_button = tk.Menubutton(main_frame, text="☰", relief=tk.RAISED)
        menu_button.grid(row=0, column=0, sticky="nw", padx=5, pady=5)
        menu = tk.Menu(menu_button, tearoff=0)
        menu.add_command(label="Copy Google Sheet", command=self.option1)
        menu.add_command(label="Start Automatic Data Logger Service", command=self.option2)
        menu.add_command(label="Option 3", command=self.option3)
        menu_button.config(menu=menu)

        # Create the form entries below the menu
        self.create_form(main_frame)

        # Buttons frame below form
        btn_frame = tk.Frame(main_frame)
        btn_frame.grid(row=len(VISIBLE_FIELDS), column=0, columnspan=2, pady=10)
        tk.Button(btn_frame, text="Save", command=self.save_config).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Load", command=self.load_config).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Quit", command=root.quit).pack(side=tk.LEFT, padx=5)

    def create_form(self, parent):
        for i, key in enumerate(VISIBLE_FIELDS):
            value = self.config.get(key, "")
            tk.Label(parent, text=FIELD_LABELS.get(key, key)).grid(row=i, column=0, sticky="e", padx=5, pady=3)

            if key in TIME_FIELDS:
                frame = tk.Frame(parent)
                frame.grid(row=i, column=1, sticky="w")
                entry = tk.Entry(frame, width=15)
                entry.insert(0, str(value))
                entry.pack(side=tk.LEFT)
                tk.Button(frame, text="⏱", command=lambda e=entry: self.pick_time(e)).pack(side=tk.LEFT, padx=5)
            else:
                entry = tk.Entry(parent, width=40)
                entry.insert(0, str(value))
                entry.grid(row=i, column=1, padx=5, pady=3)

            self.entries[key] = entry
    # --- Helper methods ---
    def browse_folder(self, entry_widget):
        folder = filedialog.askdirectory()
        if folder:
            entry_widget.delete(0, tk.END)
            entry_widget.insert(0, folder)

    def pick_time(self, entry_widget):
        def set_time():
            h = int(hour_var.get())
            m = int(min_var.get())
            s = int(sec_var.get())
            entry_widget.delete(0, tk.END)
            entry_widget.insert(0, f"{h:02}:{m:02}:{s:02}")
            picker.destroy()

        picker = Toplevel(self.root)
        picker.title("Select Time")
        picker.geometry("200x120")
        picker.transient(self.root)
        picker.grab_set()

        hour_var = tk.StringVar(value="06")
        min_var = tk.StringVar(value="00")
        sec_var = tk.StringVar(value="00")

        tk.Label(picker, text="Hour").grid(row=0, column=0)
        tk.Label(picker, text="Min").grid(row=0, column=1)
        tk.Label(picker, text="Sec").grid(row=0, column=2)

        tk.Spinbox(picker, from_=0, to=23, wrap=True, textvariable=hour_var, width=5, format="%02.0f").grid(row=1, column=0)
        tk.Spinbox(picker, from_=0, to=59, wrap=True, textvariable=min_var, width=5, format="%02.0f").grid(row=1, column=1)
        tk.Spinbox(picker, from_=0, to=59, wrap=True, textvariable=sec_var, width=5, format="%02.0f").grid(row=1, column=2)

        tk.Button(picker, text="OK", command=set_time).grid(row=2, column=0, columnspan=3, pady=5)

    def load_config(self):
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r") as f:
                    self.config = json.load(f)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load config: {e}")
                self.config = DEFAULT_CONFIG.copy()
        else:
            self.config = DEFAULT_CONFIG.copy()

        for key, entry in self.entries.items():
            entry.delete(0, tk.END)
            entry.insert(0, str(self.config.get(key, "")))

    def save_config(self):
        try:
            for key, entry in self.entries.items():
                value = entry.get()
                if key == "how_long_to_save_old_files":
                    value = int(value)
                self.config[key] = value

            with open(CONFIG_FILE, "w") as f:
                json.dump(self.config, f, indent=2)

            messagebox.showinfo("Success", "Configuration saved successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save config: {e}")

    # --- Hamburger menu options ---
    def option1(self):
        webbrowser.get("firefox").open(GOOGLE_SHEET_COPY)
        #messagebox.showinfo("Menu", "Option 1 clicked!")

    def option2(self):
        #messagebox.showinfo("Menu", "Option 2 clicked!")

        try:
            print(f"Service '{SERVICE_NAME}' started successfully.")
        except subprocess.CalledProcessError as e:
            print(f"Failed to start service: {e}")

    def option3(self):
        messagebox.showinfo("Menu", "Option 3 clicked!")


if __name__ == "__main__":
    root = tk.Tk()
    app = ConfigEditor(root)
    root.mainloop()
