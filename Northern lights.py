from matplotlib import pyplot as plt
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import requests
import re


class NorthernLightSample:
    def __init__(self, city: str, KP_index_minimum: int, observable_northern_lights_minimum: float):
        self.city = city
        self.KP_index_minimum = KP_index_minimum
        self.observable_northern_lights_minimum = observable_northern_lights_minimum

        self.yr_forecast_url, self.yr_other_warnings_url, self.yr_city_code = self.get_yr_url()
        self.time, self.kpIndex, self.auroraValue, self.condition, self.sunlight, self.cloud_coverage, self.forecast_json = self.get_northern_lights_data()
        
    def get_yr_url(self) -> tuple[str, str, str]:
        """
        Returns (yr_forecast_url, yr_other_warnings_url, yr_city_code)
        """
        base_search_url_ = r"https://www.yr.no/nb/s%C3%B8k?q="
        city_code_pattern = r"/([0-9]+-[0-9]+)/"

        search_url = base_search_url_ + self.city

        response = requests.get(search_url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")

            search_results_list = soup.find("ol", {"class": "search-results-list"})
            top_result = soup.find("a", {"class": "search-results-list__item-anchor"})

            if top_result is None:
                print("Failed to find search result.")
                quit()
            else:
                yr_forecast_url = "yr.no" + top_result['href']
                yr_other_warnings_url = yr_forecast_url.replace("v%C3%A6rvarsel/daglig-tabell", "andre-varsler")

                match = re.search(city_code_pattern, yr_forecast_url)
                yr_city_code = match.group(1)

            return yr_forecast_url, yr_other_warnings_url, yr_city_code
        else:
            print(f"Failed to fetch data from '{search_url}'. Status code: {response.status_code}")
            quit()
    
    def aurora_forecast_api_url(self) -> str:
        return fr"https://www.yr.no/api/v0/locations/{self.yr_city_code}/auroraforecast?language=nb"

    def get_northern_lights_data(self) -> tuple:
        aurora_forecast_api_url = fr"https://www.yr.no/api/v0/locations/{self.yr_city_code}/auroraforecast?language=nb"

        response = requests.get(aurora_forecast_api_url)
        if response.status_code == 200:
            data = response.json()
            data_segments = data['shortIntervals']

            time = [data_segment['start'] for data_segment in data_segments]
            kpIndex = [data_segment['kpIndex'] for data_segment in data_segments]
            auroraValue = [data_segment['auroraValue'] for data_segment in data_segments]
            condition = [data_segment['condition']['id'] for data_segment in data_segments]
            sunlight = [data_segment['sunlight']['id'] for data_segment in data_segments]
            cloudCover = [data_segment['cloudCover']['value'] for data_segment in data_segments]
            
            return time, kpIndex, auroraValue, condition, sunlight, cloudCover, data
        else:
            print(f"Failed to fetch data from '{aurora_forecast_api_url}'. Status code: {response.status_code}")
            quit()
    
    def plot_data(self, y_series: list, title: str, y_lim: list[float], fig_size = (8, 4.5), should_plot_midnights = True, y_markings: list[tuple[float, str]] = None, y_lines: list[float] = None) -> None:
        time_series = pd.to_datetime(self.time)

        # Plot the shape
        plt.figure(figsize=fig_size)
        plt.plot(time_series, y_series, linestyle='-', marker='o', markersize=2, color='black')
        plt.fill_between(time_series, y_series, color='turquoise', alpha=0.3)  # Fill the shape

        if should_plot_midnights:
            # Identify midnight timestamps for vertical lines
            midnights = [t for t in time_series if t.hour == 0 and t.minute == 0]
            # Add vertical lines at midnight
            for midnight in midnights:
                plt.axvline(midnight, color='red', linestyle='--', alpha=0.7)
        
        if y_lines:
            for y_line in y_lines:
                plt.axhline(y=y_line, color='gray', linestyle='--', alpha=0.7)

        if y_markings:
            for y_value, marking in y_markings:
                # Add labels for Low and High levels
                plt.text(time_series[-1] + pd.Timedelta(minutes=200), y_value, marking, verticalalignment='center', color='black')

        # Format x-axis to show only time, with fewer labels
        plt.title(title)
        # plt.xlabel("Time")

        # Ensure ticks always include 24:00 while keeping the same delta
        delta = 3  # Step size for ticks
        ticks = time_series[::delta]

        # Shift the tick list forward if 24:00 is not included
        i = 0
        while time_series[-1] not in ticks:
            i += 1
            ticks = time_series[i::delta]  # Shift forward by one step

        plt.xticks(ticks, [t.strftime("%H:%M") for t in ticks], rotation=45)
        plt.ylim(y_lim)
        plt.grid(True)

        # Show the plot
        plt.show()

    def plot_northern_lights_activity(self) -> None:
        y_markings = [(0.1, "Low"), (0.44, "High")]
        self.plot_data(self.auroraValue, title = "Northern Lights Activity", y_lim=[0, 1], y_markings=y_markings, y_lines=[0.1, 0.44])
    
    def plot_cloud_coverage(self) -> None:
        self.plot_data(self.cloud_coverage, title = "Cloud coverage", y_lim=[0, 110])

    def plot_observable_northern_lights_activity(self, filter_active = False) -> None:
        data = np.array(self.auroraValue) * (1 - np.array(self.cloud_coverage) / 100)
        if filter_active:
            data = data * np.array([kpIndex >= self.KP_index_minimum for kpIndex in self.kpIndex])
            self.plot_data(data, "Observable northern lights", y_lim = [0, 1], y_lines=[self.observable_northern_lights_minimum])

def main() -> None:
    city = "Trondheim"
    KP_index_minimum = 4  # https://www.theaurorazone.com/nuts-about-kp/
    observable_northern_lights_minimum = 0.23  # Has to be tweaked

    northern_light_sample = NorthernLightSample(city, KP_index_minimum, observable_northern_lights_minimum)
    # northern_light_sample.plot_northern_lights_activity()
    # northern_light_sample.plot_cloud_coverage()
    northern_light_sample.plot_observable_northern_lights_activity(filter_active=True)


if __name__ == '__main__':
    main()