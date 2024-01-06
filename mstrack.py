import threading
import time
import json
import keyboard
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

        os.system("cls")
        print(Style.BRIGHT + Fore.GREEN + Header + Style.RESET_ALL)
        print(Style.DIM + "\tYour personal performance tracker :)\n" + Style.RESET_ALL)
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

    def info_session(self):
        self.display_window_info()

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
        if event.event_type == keyboard.KEY_UP:
            window_name = self.get_active_window_name()
            if window_name:
                self.keystrokes[window_name] = self.keystrokes.get(window_name, 0) + 1
                print("Registered ", event, "for window - ",window_name)

    def set_window_duration(self, window_name, duration):
        self.durations[window_name] = self.durations.get(window_name, 0) + duration

    def get_active_window_name(self):
        try:
            active_window = gw.getActiveWindow().title

            keying_applications = [
                "OCR",
                "Classification",
                "Credit Card",
                "Handprint",
                "Easy",
                "Email",
                "MICR",
                "Mark Sense",
                "Checks",
                "COFA",
                "Address",
            ]
            application_mapping = [
                "Teams",
                "Google Chrome",
                "Microsoft Edge",
                "Sticky",
            ]

            for window_name in application_mapping:
                if window_name in active_window:
                    return "Essentials"

            if "Keying" in active_window:
                for app in keying_applications:
                    if app in active_window:
                        return app + " Keying"
                return "N/A Keying"
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
        os.system("cls")
        print(Style.DIM + f"Session info for {self.session_id}:" + Style.RESET_ALL)
        print(Style.DIM + f"Elapsed Time: {str(elapsed_time)}" + Style.RESET_ALL)
        print("")

    def display_window_info(self):
        if not self.keystrokes:
            print("No keystrokes recorded.")
            return

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
        if None:
            return 0
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
    Saves and displays sessions till the application is running
    """
    while True:
        hawk_track.info_session()
        hawk_track.save_session_info()
        print(Style.DIM + "session info saved...")
        time.sleep(2)


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
    keyboard.hook(hawk_track.on_key_event)
    keyboard.wait("ctrl+esc")
    keyboard.unhook_all()


def main():
    hawk_track = HawkTrack()
    hawk_track.load_session_info()
    hawk_track.start_session()

    background_thread = threading.Thread(target=run_background, args=(hawk_track,))
    duration_updating = threading.Thread(target=update_duration, args=(hawk_track,))
    duration_updating.start()
    background_thread.start()

    monitor_keystrokes(hawk_track)

    hawk_track.info_session()


if __name__ == "__main__":
    main()
