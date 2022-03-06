import config
import noaa_coops as nc
import matplotlib.pyplot as plt
import numpy as np

# NOAA Station Code for tide data
StationID = config.station_id

# last 24 hour data, add argument for start/end_date
def past24(StationID):
    # Create Station Object
    stationdata = nc.Station(StationID)

    # Get today date string
    today = dt.datetime.now()
    todaystr = today.strftime("%Y%m%d %H:%M")
    # Get yesterday date string
    yesterday = today - dt.timedelta(days=1)
    yesterdaystr = yesterday.strftime("%Y%m%d %H:%M")

    # Get water level data
    WaterLevel = stationdata.get_data(
        begin_date=yesterdaystr,
        end_date=todaystr,
        product="water_level",
        datum="MLLW",
        units='english' if UNITS == "imperial" else "metric",
        time_zone="lst_ldt")

    return WaterLevel

# Plot last 24 hours of tide
def plotTide(TideData):
    # Adjust data for negative values
    minlevel = TideData['water_level'].min()
    TideData['water_level'] = TideData['water_level'] - minlevel

    # Create Plot
    fig, axs = plt.subplots(figsize=(8, 4))
    TideData['water_level'].plot.area(ax=axs, color='black')
    plt.title('Tide- Past 24 Hours', fontsize=20)
    plt.savefig('images/TideLevel.png', dpi=60)
    plt.close()


# Get High and Low tide info
def HiLo(StationID):
    # Create Station Object
    stationdata = nc.Station(StationID)

    # Get today date string
    today = dt.datetime.now()
    todaystr = today.strftime("%Y%m%d")
    # Get yesterday date string
    tomorrow = today + dt.timedelta(days=1)
    tomorrowstr = tomorrow.strftime("%Y%m%d")

    # Get Hi and Lo Tide info
    TideHiLo = stationdata.get_data(
        begin_date=todaystr,
        end_date=tomorrowstr,
        product="predictions",
        datum="MLLW",
        interval="hilo",
        units='english' if UNITS == "imperial" else "metric",
        time_zone="lst_ldt")

    return TideHiLo

def getwaterlevel():
    # Get water level

    wl_error = True
    while wl_error == True:
        try:
            WaterLevel = past24(StationID)
            wl_error = False
            print("Retrieved Tide Data")
        except:
            print("Error retrieving Tide Data")
            display_error('Tide Data Error')

    plotTide(WaterLevel)

def updatetidegraph():
    tidegraph = Image.open('images/TideLevel.png')
    template.paste(tidegraph, (145, 240))
