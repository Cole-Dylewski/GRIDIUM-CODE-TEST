# Write a simple Python web scraper to help us visit the tide pools.
# Go to https://www.tide-forecast.com/ to get tide forecasts for these locations:
#     Half Moon Bay, California
#     Huntington Beach, California
#     Providence, Rhode Island
#     Wrightsville Beach, North Carolina
# Load the tide forecast page for each location and extract information on low tides that occur after sunrise and before sunset. Return the time and height for each daylight low tide.


import pandas as pd
import requests
from bs4 import BeautifulSoup
import re
import json
import datetime as dt
scriptStart = dt.datetime.now()


# returns dataframe of Low tides from list of selections
# NOTE: I prefer readability to elegance, so there are some code lines that could be coupled or combined, but I have left them more simple for readability and update reasons
def get_daylight_low_tides(selections):
    # toggles print statements
    verbose = False

    dayHighs = []
    dayLows = []
    for selection in selections:
        # build URL
        baseUrl = "https://www.tide-forecast.com/locations/"
        location = selection.replace(' ', '-').replace(',', '')
        additionalArg = r'/forecasts/latest/six_day'

        # scrape the page and get content
        URL = baseUrl + location + additionalArg
        page = requests.get(URL)
        soup = BeautifulSoup(page.content, 'html.parser')

        # isolate the tide data and parse into dict
        cdata = soup.find(text=re.compile("CDATA"))

        #from the second line, grab the dictionary of tide data
        cdata = cdata.split('\n')[2][15:-1]
        cdata = json.loads(cdata)

        # loop through days and update output lists
        for day in cdata['tideDays']:

            date = day['date']
            sunrise = day['sunrise']
            sunset = day['sunset']

            # there are some odd cases where there is no defined sunrise or sunset in the data. I have chosen to ignore these in lieu of some kind of default value
            if sunrise != None and sunset != None:
                for tide in day['tides']:
                    if sunrise < tide['timestamp'] < sunset:
                        tempDict = {
                            'Location': selection,
                            'Date': date,
                            'Sunrise': dt.datetime.fromtimestamp(day['sunrise']).time(),
                            'Sunset': dt.datetime.fromtimestamp(day['sunset']).time(),
                            'Time': tide['time'],
                            'Height': tide['height'],
                            'Type': tide['type']
                        }

                        if tide['type'] == 'low':
                            dayLows.append(tempDict)
                        # else:
                        # dayHighs.append(tempDict)

    dayLowsdf = pd.DataFrame(dayLows)
    # requestSpecificFormat = dayLowsdf[['Location','Date','Time','Height']]
    # print(dayLowsdf.to_string())
    return dayLows, dayLowsdf


if __name__ == '__main__':
    # takes a lists of selections, will loop through all and concatenate into final dataframe

    selections = [
        'Half Moon Bay, California',
        'Huntington Beach',  # has divergent static designation
        'Providence, Rhode Island',
        'Wrightsville Beach, North Carolina'
    ]
    # returns list and Dataframe
    dayLows, dayLowsdf = get_daylight_low_tides(selections)
    print(dayLows)
    print(dayLowsdf.to_string())
    ttr = str(dt.timedelta(seconds=(dt.datetime.now() - scriptStart).seconds))
    print("script time to run:", ttr)
