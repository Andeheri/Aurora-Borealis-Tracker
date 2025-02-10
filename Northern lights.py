from matplotlib import pyplot as plt
from bs4 import BeautifulSoup
import pandas as pd
import requests
import re

city = "Sandnessjøen"


class NorthernLightSample:
    def __init__(self, city: str):
        self.city = city
        self.yr_forecast_url, self.yr_other_warnings_url, self.yr_city_code = self.get_yr_url()
        self.time, self.kpIndex, self.auroraValue, self.condition, self.sunlight, self.cloud_cover, self.forecast_json = self.get_northern_lights_data()
        
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


    def plot_data(self, data: list[float]) -> None:
        time_series = pd.to_datetime(self.time)

        # Identify midnight timestamps for vertical lines
        midnights = [t for t in time_series if t.hour == 0 and t.minute == 0]

        # Plot the shape
        plt.figure(figsize=(8, 4))
        plt.plot(time_series, data, linestyle='-', marker='o', markersize=3, color='black')
        plt.fill_between(time_series, data, color='turquoise', alpha=0.3)  # Fill the shape

        # Add vertical lines at midnight
        for midnight in midnights:
            plt.axvline(midnight, color='red', linestyle='--', alpha=0.7)

        # Add labels for Low and High levels
        plt.text(time_series[-1] + pd.Timedelta(minutes=200), 0.1, 'Low', verticalalignment='center', color='black')
        plt.text(time_series[-1] + pd.Timedelta(minutes=200), 0.5, 'High', verticalalignment='center', color='black')

        # Format x-axis to show only time, with fewer labels
        plt.title("Northern Lights Activity")
        plt.xlabel("Time")
        plt.xticks(time_series[::4], [t.strftime("%H:%M") for t in time_series[::4]], rotation=45)
        plt.ylim([0, 1])
        plt.grid(True)

        # Show the plot
        plt.show()


def main() -> None:
    city = "Sandnessjøen"
    northern_light_sample = NorthernLightSample(city)
    northern_light_sample.plot_data(northern_light_sample.auroraValue)


if __name__ == '__main__':
    main()