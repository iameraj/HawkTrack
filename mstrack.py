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
        self.start_time = None

    def start_session(self):
        today_date = datetime.now(timezone_obj).strftime("%d %b %Y")
        if self.session_id == today_date:
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

            with open(self.session_file, "w") as file:
                json.dump(
                    {
                        "session_id": self.session_id,
                        "recording": self.recording,
                        "start_time": self.start_time,
                        "keystrokes": self.keystrokes,
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

    def end_session(self):
        if self.recording:
            self.recording = False
            self.display_session_info()
            self.save_session_info()
        else:
            print("No active session.")

    def save_session_info(self):
        session_info = {
            "session_id": self.session_id,
            "recording": self.recording,
            "start_time": self.start_time,
            "keystrokes": self.keystrokes,
        }
        with open(self.session_file, "w") as file:
            json.dump(session_info, file)

    def on_key_event(self, event):
        if event.event_type == keyboard.KEY_DOWN:
            window_name = self.get_active_window_name()
            if window_name:
                self.keystrokes[window_name] = self.keystrokes.get(window_name, 0) + 1

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

            # If no match found, return the original window title
            return active_window

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
                [window_name, keystrokes_count, self.format_time(self.start_time)]
            )

        print("Window-wise keystrokes count:")
        print(table)

    def format_time(self, start_time):
        elapsed_time = int(time.time() - start_time)
        return str(timedelta(seconds=elapsed_time))


def run_background(hawk_track):
    # This function runs in the background
    while hawk_track.recording:
        os.system("cls")
        hawk_track.info_session()
        hawk_track.save_session_info()
        print("session info saved...")
        time.sleep(2)  # Save session info every 6 seconds


def monitor_keystrokes(hawk_track):
    keyboard.hook(hawk_track.on_key_event)
    keyboard.wait("esc")  # Wait for the user to press the escape key
    keyboard.unhook_all()


def main():
    hawk_track = HawkTrack()
    hawk_track.load_session_info()
    hawk_track.start_session()

    background_thread = threading.Thread(
        target=run_background, args=(hawk_track,), daemon=True
    )
    background_thread.start()

    # Monitor keystrokes in the main thread
    monitor_keystrokes(hawk_track)

    # hawk_track.info_session()
    # hawk_track.end_session()


if __name__ == "__main__":
    main()
