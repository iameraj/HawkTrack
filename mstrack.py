import threading
import time
import json
import keyboard
import pygetwindow as gw
from datetime import datetime, timedelta
from prettytable import PrettyTable
import os
import pytz

timezone_obj = pytz.timezone("America/Chicago")



class HawkTrack:
    def __init__(self):
        self.session_id = None
        self.recording = False
        self.session_file = "session_info.json"
        self.keystrokes = {}
        self.durations = {}
        self.start_time = None

    def start_session(self):
        os.system("cls")
        today_date = datetime.now(timezone_obj).strftime("%d %b %Y")
        if self.session_id == today_date:
            print("Continuing sessions ", self.session_id)
            password = input("Enter password: ")
            # Validate password and start recording if valid
            if self.validate_password(password):
                self.recording = True
                print("Session is being recorded...")
                self.save_session_info()
        else:
            os.system("cls")
            print(
                "\nYour previous session ",
                self.session_id,
                "- UTC-6 has expired starting a new session.\n",
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
                "\nYour session for ",
                today_date,
                " - Central Time Zone (CT)/UTC-6  has started",
            )
            _ = input("press ENTER To proceed...")

    def validate_password(self, password):
        return True

    def info_session(self):
        if self.recording:
            self.display_session_info()
            self.display_window_info()
        else:
            print("No active session.")

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

    def set_window_duration(self, window_name, duration):
        self.durations[window_name] = self.durations.get(window_name, 0) + duration

    def get_active_window_name(self):
        try:
            active_window = gw.getActiveWindow().title
            application_mapping = {
                "Teams": "Teams",
                "Visual Studio Code": "Visual Studio Code",
                "Google Chrome": "Google Chrome",
                "Keying": "Keying",
                "Microsoft Edge": "Microsoft Edge",
            }

            for key, value in application_mapping.items():
                if key in active_window:
                    return value

            # If no match found, return the other window title
            return "Other"

        except Exception as e:
            print(f"Error getting active window: {e}")
            return None

    def load_session_info(self):
        try:
            with open(self.session_file, "r") as file:
                session_info = json.load(file)
                self.session_id = session_info.get("session_id")
                self.recording = session_info.get("recording", False)
                self.start_time = session_info.get("start_time")
                self.keystrokes = session_info.get("keystrokes", {})
                self.durations = session_info.get("durations", {})
        except FileNotFoundError:
            pass  # Ignore if the file is not found

    def display_session_info(self):
        elapsed_time = timedelta(seconds=int(time.time() - self.start_time))
        print(f"Session info for {self.session_id}:")
        print(f"Elapsed Time: {str(elapsed_time)}")
        print("")

    def display_window_info(self):
        if not self.keystrokes:
            print("No keystrokes recorded.")
            return

        table = PrettyTable()
        table.field_names = ["Window Name", "Keystrokes Count", "Time Spent"]

        for window_name, keystrokes_count in self.keystrokes.items():
            table.add_row(
                [
                    window_name,
                    keystrokes_count,
                    self.format_time(self.durations.get(window_name,1)),
                ]
            )

        print("Window-wise keystrokes count:")
        print(table)

    def format_time(self, duration):
        if None:
            return 0
        else:
            return timedelta(seconds=duration)


def run_background(hawk_track):
    """
    This function runs in the background
    to save the session keystrokes info  and
    duration info, it also maintains the
    time record of each window
    """
    time_start = time.time()

    active_window = hawk_track.get_active_window_name()

    while hawk_track.recording:
        new_active_window = hawk_track.get_active_window_name()

        if new_active_window != active_window:
            time_spent_in_prev_window = time.time() - time_start
            hawk_track.set_window_duration(active_window, time_spent_in_prev_window)
            # Update start time and active window
            time_start = time.time()
        os.system("cls")
        hawk_track.info_session()
        hawk_track.save_session_info()
        print("session info saved...")
        active_window = new_active_window
        time.sleep(1)


def monitor_keystrokes(hawk_track):
    keyboard.hook(hawk_track.on_key_event)
    keyboard.wait("ctrl+esc")  # Wait for the user to press the escape key
    keyboard.unhook_all()


def main():
    hawk_track = HawkTrack()
    hawk_track.load_session_info()
    hawk_track.start_session()

    background_thread = threading.Thread(target=run_background, args=(hawk_track,))
    background_thread.start()

    monitor_keystrokes(hawk_track)

    hawk_track.info_session()


if __name__ == "__main__":
    main()
