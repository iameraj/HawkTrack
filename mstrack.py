import threading
import time
import json
from pynput.keyboard import Listener
import pygetwindow as gw
from datetime import datetime, timedelta
from prettytable import PrettyTable, SINGLE_BORDER
from colorama import Fore, Back, Style
import os
import pytz

timezone_obj = pytz.timezone("America/Chicago")


Header = """

     __  __     ______     __     __     __  __    
    /\ \_\ \   /\  __ \   /\ \  _ \ \   /\ \/ /    
    \ \  __ \  \ \  __ \  \ \ \/ ".\ \  \ \  _"-.  
     \ \_\ \_\  \ \_\ \_\  \ \__/".~\_\  \ \_\ \_\ 
      \/_/\/_/   \/_/\/_/   \/_/   \/_/   \/_/\/_/ 

     ______   ______     ______     ______     __  __    
    /\__  _\ /\  == \   /\  __ \   /\  ___\   /\ \/ /    
    \/_/\ \/ \ \  __<   \ \  __ \  \ \ \____  \ \  _"-.  
       \ \_\  \ \_\ \_\  \ \_\ \_\  \ \_____\  \ \_\ \_\ 
        \/_/   \/_/ /_/   \/_/\/_/   \/_____/   \/_/\/_/ 
"""


class HawkTrack:
    def __init__(self):
        self.session_id = None
        self.recording = False
        self.session_file = "session_info.json"
        self.keystrokes = {}
        self.durations = {}
        self.start_time = None
        self.session_file_path = "?"

        os.system("cls")
        print(Style.BRIGHT + Fore.GREEN + Header + Style.RESET_ALL)
        print(Style.DIM + "\t\t#Your personal performance tracker\n" + Style.RESET_ALL)

        try:
            self.user_name = os.getenv("USERNAME")
            _ = input(f"User: {self.user_name} \nPress enter to procced...")
        except:
            self.user_name = input("\tEnter your name: ") or "User"

    def start_session(self):
        os.system("cls")
        today_date = datetime.now(timezone_obj).strftime("%d %b %Y")
        if self.session_id == today_date:
            print(
                Style.BRIGHT + "\n\nContinuing session ",
                self.session_id + Style.RESET_ALL,
            )
            _ = input("press ENTER To proceed...")
            self.recording = True
            self.save_session_info()
        else:
            os.system("cls")
            print(
                Style.BRIGHT + "\n\nYour previous session ",
                self.session_id,
                "- UTC-6 has expired starting a new session.\n",
                " " + Style.RESET_ALL,
            )

            self.session_id = today_date
            self.start_time = time.time()
            self.recording = True
            self.keystrokes = {}
            self.durations = {}
            
            with open(self.session_file, "w") as file:
                json.dump(
                    {
                        "session_id": self.session_id,
                        "recording": self.recording,
                        "start_time": self.start_time,
                        "keystrokes": self.keystrokes,
                        "durations": self.durations,
                    },
                    file,
                )
            print(
                Style.BRIGHT + "\nYour session for ",
                today_date,
                " - Central Time Zone (CT)/UTC-6  has started",
                " " + Style.RESET_ALL,
            )
            _ = input("press ENTER To proceed...")

        self.session_file_path = os.path.abspath(self.session_file)

    def save_session_info(self):
        session_info = {
            "session_id": self.session_id,
            "recording": self.recording,
            "start_time": self.start_time,
            "keystrokes": self.keystrokes,
            "durations": self.durations,
        }
        with open(self.session_file, "w") as file:
            json.dump(session_info, file)

    def on_key_event(self, event):
        try:
            window_name = self.get_active_window_name(real=True)
            if window_name:
                if window_name == "Account Lookup":
                    pass
                else:
                    self.keystrokes[window_name] = (
                        self.keystrokes.get(window_name, 0) + 1
                    )
                print(
                    Style.DIM + "\t-",
                    event,
                    " was pressed in: ",
                    window_name,
                )
        except:
            print(Fore.RED + "Failed to capture Keystroke" + Style.RESET_ALL)

    def set_window_duration(self, window_name, duration):
        self.durations[window_name] = self.durations.get(window_name, 0) + duration

    def get_active_window_name(self, real=False):
        try:
            active_window = gw.getActiveWindow().title

            keying_applications = {
                "OCR",
                "Classification",
                "Credit Card",
                "Handprint",
                "Easy",
                "Email",
                "MICR",
                "Mark Sense",
                "Check",
                "COFA",
                "Address",
            }
            application_mapping = {"Teams", "Google Chrome", "Microsoft Edge", "Sticky"}

            if "Account Lookup" in active_window:
                if real:
                    return "Account Lookup"
                return "Handprint Keying"

            if "Keying" in active_window:
                for app in keying_applications:
                    if app in active_window:
                        return f"{app} Keying"
                return "N/A Keying"

            for window_name in application_mapping:
                if window_name in active_window:
                    return "Essentials"

            return "Others"

        except:
            return "Others"

    def load_session_info(self):
        try:
            with open(self.session_file, "r") as file:
                session_info = json.load(file)
                self.session_id = session_info.get("session_id")
                self.recording = session_info.get("recording", False)
                self.start_time = session_info.get("start_time")
                self.keystrokes = session_info.get("keystrokes", {})
                self.durations = session_info.get("durations", {})
        except:
            session_info = {
                "session_id": self.session_id,
                "recording": self.recording,
                "start_time": self.start_time,
                "keystrokes": self.keystrokes,
                "durations": self.durations,
            }
        with open(self.session_file, "w") as file:
            json.dump(session_info, file)

    def display_session_info(self):
        elapsed_time = timedelta(seconds=int(time.time() - self.start_time))

        session_info = (
            Style.DIM + f"Session info for {self.session_id}:\n"
            f"Elapsed Time: {elapsed_time}" + Style.RESET_ALL
        )

        os.system("cls")
        print(session_info)
        print()

    def display_window_info(self):
        table = PrettyTable()
        table.title = "State-Wise data of " + self.user_name + " on " + self.session_id

        table.field_names = [
            Style.BRIGHT + Fore.GREEN + "Window Name",
            "Keystrokes Count",
            "Time Spent",
            "Speed" + Style.RESET_ALL,
        ]

        total_keystrokes_count = 0
        total_time = 1

        for window_name, keystrokes_count in self.keystrokes.items():
            if window_name not in ["Others", "Essentials"]:
                col2 = keystrokes_count
                col3 = self.durations.get(window_name, 1)
                col4 = (keystrokes_count / col3) * 3600
                total_keystrokes_count += col2
                total_time += col3

                table.add_row(
                    [
                        Style.BRIGHT + window_name + Style.RESET_ALL,
                        "{:,}".format(col2),
                        self.format_time(col3),
                        round(col4),
                    ]
                )

        table.add_row(
            [
                "Essentials",
                self.keystrokes.get("Essentials", 0),
                self.format_time(self.durations.get("Essentials", 1)),
                round(
                    self.keystrokes.get("Essentials", 0)
                    / self.durations.get("Essentials", 1)
                    * 3600
                ),
            ],
            divider=True,
        )

        avg_speed = str(round(total_keystrokes_count / total_time * 3600))
        table.add_row(
            [
                Style.BRIGHT + Fore.GREEN + "Total",
                total_keystrokes_count,
                self.format_time(total_time),
                avg_speed + Style.RESET_ALL,
            ]
        )
        table.set_style(SINGLE_BORDER)
        self.display_session_info()
        print(table)

    def format_time(self, duration):
        if duration is None:
            return 1
        else:
            hours, remainder = divmod(duration, 3600)
            minutes, seconds = divmod(remainder, 60)

            formatted_time = ""
            if hours > 0:
                formatted_time += f"{int(hours)} hrs "
            if minutes > 0:
                formatted_time += f"{int(minutes)} mins "
            if seconds > 0 or not formatted_time:
                formatted_time += f"{int(seconds)} secs"

            return formatted_time.strip()


def run_background(hawk_track):
    """
    Saves session data till the application is running
    """
    while True:
        hawk_track.save_session_info()
        print(Style.BRIGHT + "\tsession info saved.👍" + Style.RESET_ALL)
        time.sleep(5)


def show_data(hawk_track):
    """
    Displays data on screen
    """
    while True:
        hawk_track.display_window_info()
        print(
            Style.DIM
            + f"session data is being stored at {hawk_track.session_file_path}" 
            + Style.RESET_ALL
        )
        time.sleep(0.9)


def update_duration(hawk_track):
    """
    Updates the period of time for each window
    """
    time_start = time.time()
    active_window = hawk_track.get_active_window_name()

    while True:
        time_spent = time.time() - time_start
        hawk_track.set_window_duration(active_window, time_spent)
        time_start = time.time()
        active_window = hawk_track.get_active_window_name()
        time.sleep(0.1)


def monitor_keystrokes(hawk_track):
    listener = Listener(on_release=hawk_track.on_key_event)

    listener.start()


def main():
    hawk_track = HawkTrack()
    hawk_track.load_session_info()
    hawk_track.start_session()

    background_thread = threading.Thread(target=run_background, args=(hawk_track,))
    duration_updating = threading.Thread(target=update_duration, args=(hawk_track,))
    display_data = threading.Thread(target=show_data, args=(hawk_track,))
    monitor = threading.Thread(target=monitor_keystrokes, args=(hawk_track,))

    monitor.start()
    duration_updating.start()
    background_thread.start()
    display_data.start()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass
