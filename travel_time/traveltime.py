"""TravelTime is an app to help figure out how long a commute will be, without needing
to head to a web page or app to check. It will continuously poll live traffic data, and
display the current distance between work and home.
"""
import json
import time
import tkinter as tk
from typing import Any, Dict, Tuple

import requests

JSON = Dict[str, Any]


class TravelTime:
    """Main application class. Handles the application lifecycle (using Tkinter),
    querying map data, and processing it for proper display.
    """

    def __init__(
        self, root: tk.Tk, width: int, height: int, config: JSON,
    ):
        self.root = root
        self.root.title("TravelTime")
        self.root.geometry(f"{width}x{height}")

        self.frame = tk.Frame(root)
        self.frame.pack()

        self.message = tk.StringVar()
        self.label_message = tk.Label(root, textvariable=self.message)
        self.label_message.pack()

        self.time = tk.StringVar()
        self.label_time = tk.Label(root, textvariable=self.time)
        self.label_time.pack()

        self.config = config
        self.update_label()

    def update_label(self) -> None:
        """Update the application display."""
        if self.is_work_hours():
            self._update_label_message(0, True)
        else:
            expected_time, actual_time = self.travel_time_google()
            self._update_label_color(expected_time, actual_time)
            self._update_label_message(actual_time)

        # Schedule the next execution of this method
        self.root.after(1000 * 60 * 5, self.update_label)

    def _update_label_color(self, expected_time: int, actual_time: int) -> None:
        """Update the text color, based on how bad the traffic is."""
        traffic_error = actual_time / expected_time - 1
        if traffic_error <= 0.2:
            self.label_time.config(fg="forest green")
        elif 0.2 < traffic_error <= 0.5:
            self.label_time.config(fg="goldenrod")
        elif traffic_error > 0.5:
            self.label_time.config(fg="red")

    def _update_label_message(self, actual_time: int, work_hours: bool = False) -> None:
        """Display the current travel time, or a work-life balance message!"""
        if not work_hours:
            self.label_message.config(fg="red")
            self.message.set("YOU SHOULD GO HOME")  # type: ignore
            self.time.set("")  # type: ignore
        else:
            self.message.set("Time to home: ")  # type: ignore

            travel_time = time.gmtime(actual_time)
            hours = travel_time.tm_hour
            minutes = travel_time.tm_min
            if hours > 0:
                self.time.set(f"{hours} hours {minutes} minutes")  # type: ignore
            else:
                self.time.set(f"{minutes} minutes")  # type: ignore

    def travel_time_google(self) -> Tuple[int, int]:
        """Gets travel time from Google Maps. Requires a Google Cloud Platform API key,
        which can be provided in the app config file.

        :return: The expected commute duration, and actual duration in traffic, in
        seconds.
        """
        work = self.config["work_address"]
        home = self.config["home_address"]
        api_key = self.config["google_api_key"]
        api_url = "https://www.google.com/maps/api/directions/json"
        api_params = {
            "origin": work,
            "destination": home,
            "key": api_key,
            "departure_time": "now",
        }

        response = requests.get(api_url, api_params)
        route_data = response.json()["routes"][0]["legs"][0]

        duration = route_data["duration"]["value"]
        duration_traffic = route_data["duration_in_traffic"]["value"]

        return duration, duration_traffic

    def is_work_hours(self) -> bool:
        """Check if it is currently reasonable work hours, configured in config file.

        :return: True/False is work hours.
        """
        current_time = time.localtime()
        start_hour: int = self.config["work_start_hour"]
        end_hour: int = self.config["work_end_hour"]
        return start_hour < current_time.tm_hour <= end_hour


def main() -> None:
    """Entry-point to launch app."""
    with open("config/config.json") as config_file:
        config = json.load(config_file)
    app = TravelTime(tk.Tk(), 300, 50, config)
    app.root.mainloop()


if __name__ == "__main__":
    main()
