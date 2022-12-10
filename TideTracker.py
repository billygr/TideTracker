"""
****************************************************************
****************************************************************

                TideTracker for E-Ink Display

                        by Sam Baker

****************************************************************
****************************************************************
"""

import logging
import config
import sys
import os
import time
import requests
import json
import datetime as dt
from astral import sun, LocationInfo, moon

sys.path.append('lib')
#from waveshare_epd import epd7in5_V2
from waveshare_epd import epd7in5
from PIL import Image, ImageDraw, ImageFont

picdir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'images')
icondir = os.path.join(picdir, 'icon')
fontdir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'font')
moondir = os.path.join(picdir, 'moon')

FORMAT = "[%(asctime)s %(filename)s->%(funcName)s():%(lineno)s]%(levelname)s: %(message)s"
logging.basicConfig(level=logging.DEBUG, format=FORMAT)

'''
****************************************************************

Location specific info required

****************************************************************
'''

# Optional, displayed on top left
LOCATION = config.location

# For weather data
# Create Account on openweathermap.com and get API key
API_KEY = config.api_key
# Get LATITUDE and LONGITUDE of location
LATITUDE = config.latitude
LONGITUDE = config.longitude
UNITS = config.units

TIMEZONE = config.timezone

# Create URL for API call
BASE_URL = 'http://api.openweathermap.org/data/2.5/onecall?'
URL = BASE_URL + 'lat=' + LATITUDE + '&lon=' + LONGITUDE + '&units=' + UNITS + '&appid=' + API_KEY

'''
****************************************************************

Functions and defined variables

****************************************************************
'''


def sleep(sleep_seconds):
    print('Sleeping for ' + str(sleep_seconds) + ' seconds.')
    time.sleep(sleep_seconds)  # Determines refresh rate on data
    epd.init()  # Re-Initialize screen

# define function for writing image
def write_to_screen(image):
    print('Writing to screen.')  # for debugging
    # Create new blank image template matching screen resolution
    h_image = Image.new('1', (epd.width, epd.height), 255)
    # Open the template
    screen_output_file = Image.open(os.path.join(picdir, image))
    # Initialize the drawing context with template as background
    h_image.paste(screen_output_file, (0, 0))
    epd.display(epd.getbuffer(h_image))
    # Close the open file
    screen_output_file.close()
    # Sleep
    epd.sleep()  # Put screen to sleep to prevent damage


# define function for displaying error
def display_error(error_source):
    # Display an error
    print('Error in the', error_source, 'request.')
    # Initialize drawing
    error_image = Image.new('1', (epd.width, epd.height), 255)
    # Initialize the drawing
    draw = ImageDraw.Draw(error_image)
    draw.text((100, 150), error_source + ' ERROR', font=font50, fill=black)
    draw.text((100, 300), 'Retrying in 30 seconds', font=font22, fill=black)
    current_time = dt.datetime.now().strftime('%H:%M')
    draw.text((300, 365), 'Last Refresh: ' + str(current_time), font=font22, fill=black)
    # Save the error image
    error_image_file = 'error.png'
    error_image.save(os.path.join(picdir, error_image_file))
    # Close error image
    error_image.close()
    # Write error to screen
    write_to_screen(error_image_file, 30)


# define function for getting weather data
def getWeather(URL):
    # Ensure there are no errors with connection
    error_connect = True
    while error_connect == True:
        try:
            # HTTP request
            print('Attempting to connect to OWM.')
            response = requests.get(URL)
            print('Connection to OWM successful.')
            error_connect = None
        except:
            # Call function to display connection error
            print('Connection error.')
            display_error('CONNECTION')

    # Check status of code request
    if response.status_code == 200:
        print('Connection to Open Weather successful.')
        # get data in jason format
        data = response.json()
        # Close the connection
        response.close()
        with open('data.txt', 'w') as outfile:
            json.dump(data, outfile)

        return data

    else:
        # Call function to display HTTP error
        display_error('HTTP Error: ' + str(response.status_code))


#From https://github.com/PanderMusubi/lunar-phase-calendar
def moon_phase_to_inacurate_code(phase):
    '''Converts moon phase code to inacurate code.'''
    phase = int(phase)
    if phase == 0:
        return 0
    if 0 < phase < 7:
        return 1
    if phase == 7:
        return 2
    if 7 < phase < 14:
        return 3
    if phase == 14:
        return 4
    if 14 < phase < 21:
        return 5
    if phase == 21:
        return 6
    return 7

#From https://github.com/PanderMusubi/lunar-phase-calendar
def day_to_moon_phase_and_accurate_code(day):
    '''Converts day to moon phase and accurate code.'''
    phase_today = moon.phase(day)
    code_today = moon_phase_to_inacurate_code(phase_today)

    if code_today % 2 != 0:
        return phase_today, code_today

    phase_yesterday = moon.phase(day - dt.timedelta(days=1))
    code_yesterday = moon_phase_to_inacurate_code(phase_yesterday)

    if code_today == code_yesterday:
        return phase_today, code_today + 1

    return phase_today, code_today


moon_phases = ["New Moon",
               "Waxing Crescent",
               "First Quarter",
               "Waxing Gibbous",
               "Full Moon",
               "Waning Gibbous",
               "Last Quarter",
               "Waning Crescent"]

# Set the font sizes
font15 = ImageFont.truetype(os.path.join(fontdir, 'Font.ttc'), 15)
font20 = ImageFont.truetype(os.path.join(fontdir, 'Font.ttc'), 20)
font22 = ImageFont.truetype(os.path.join(fontdir, 'Font.ttc'), 22)
font30 = ImageFont.truetype(os.path.join(fontdir, 'Font.ttc'), 30)
font35 = ImageFont.truetype(os.path.join(fontdir, 'Font.ttc'), 35)
font50 = ImageFont.truetype(os.path.join(fontdir, 'Font.ttc'), 50)
font60 = ImageFont.truetype(os.path.join(fontdir, 'Font.ttc'), 60)
font100 = ImageFont.truetype(os.path.join(fontdir, 'Font.ttc'), 100)
font160 = ImageFont.truetype(os.path.join(fontdir, 'Font.ttc'), 160)

# Set the colors
black = 'rgb(0,0,0)'
white = 'rgb(255,255,255)'
grey = 'rgb(235,235,235)'

'''
****************************************************************

Main Loop

****************************************************************
'''

# Initialize and clear screen
print('Initializing and clearing screen.')
#epd = epd7in5_V2.EPD()  # Create object for display functions
epd = epd7in5.EPD()  # Create object for display functions
epd.init() # Initialize e-Paper or wakeup e-Paper from sleep mode
epd.Clear()

# Find a way to put screen to sleep to prevent damage in case the below code failes (happened and it burned the display)
while True:
    # The display is on and powered !!!
    # Get weather data
    data = getWeather(URL)

    print("Retrieved weather data from OWM")
    # get current dict block
    current = data['current']
    # get current
    temp_current = current['temp']
    # get feels like
    feels_like = current['feels_like']
    # get humidity
    humidity = current['humidity']
    # get pressure
    pressure = current['pressure']
    # get wind speed
    wind = current['wind_speed']
    # get description
    weather = current['weather']
    report = weather[0]['description']
    # get icon url
    icon_code = weather[0]['icon']

    # get daily dict block
    daily = data['daily']
    # get daily precip
    daily_precip_float = daily[0]['pop']
    # format daily precip
    daily_precip_percent = daily_precip_float * 100
    # get min and max temp
    daily_temp = daily[0]['temp']
    temp_max = daily_temp['max']
    temp_min = daily_temp['min']

    # Set strings to be printed to screen
    string_location = LOCATION
    string_temp_current = format(temp_current, '.0f') + u'\N{DEGREE SIGN}C'
    string_feels_like = 'Feels like: ' + format(feels_like, '.0f') + u'\N{DEGREE SIGN}C'
    string_humidity = 'Humidity: ' + str(humidity) + '%'
    string_wind = 'Wind: ' + format(wind, '.1f') + ' m/s'
    string_report = 'Now: ' + report.title()
    string_temp_max = 'High: ' + format(temp_max, '>.0f') + u'\N{DEGREE SIGN}C'
    string_temp_min = 'Low:  ' + format(temp_min, '>.0f') + u'\N{DEGREE SIGN}C'
    string_precip_percent = 'Precip: ' + str(format(daily_precip_percent, '.0f')) + '%'

    # get min and max temp
    nx_daily_temp = daily[1]['temp']
    nx_temp_max = nx_daily_temp['max']
    nx_temp_min = nx_daily_temp['min']
    # get daily precip
    nx_daily_precip_float = daily[1]['pop']
    # format daily precip
    nx_daily_precip_percent = nx_daily_precip_float * 100

    # get min and max temp
    nx_nx_daily_temp = daily[2]['temp']
    nx_nx_temp_max = nx_nx_daily_temp['max']
    nx_nx_temp_min = nx_nx_daily_temp['min']
    # get daily precip
    nx_nx_daily_precip_float = daily[2]['pop']
    # format daily precip
    nx_nx_daily_precip_percent = nx_nx_daily_precip_float * 100

    # Tomorrow Forcast Strings
    nx_day_high = 'High: ' + format(nx_temp_max, '>.0f') + u'\N{DEGREE SIGN}C'
    nx_day_low = 'Low: ' + format(nx_temp_min, '>.0f') + u'\N{DEGREE SIGN}C'
    nx_precip_percent = 'Precip: ' + str(format(nx_daily_precip_percent, '.0f')) + '%'
    nx_weather_icon = daily[1]['weather']
    nx_icon = nx_weather_icon[0]['icon']

    # Overmorrow Forcast Strings
    nx_nx_day_high = 'High: ' + format(nx_nx_temp_max, '>.0f') + u'\N{DEGREE SIGN}C'
    nx_nx_day_low = 'Low: ' + format(nx_nx_temp_min, '>.0f') + u'\N{DEGREE SIGN}C'
    nx_nx_precip_percent = 'Precip: ' + str(format(nx_nx_daily_precip_percent, '.0f')) + '%'
    nx_nx_weather_icon = daily[2]['weather']
    nx_nx_icon = nx_nx_weather_icon[0]['icon']

    # Last updated time
    now = dt.datetime.now()
    current_time = now.strftime("%d/%m/%Y, %H:%M")
    last_update_string = 'Last Updated: ' + current_time

    # Open template file
    template = Image.open(os.path.join(picdir, 'template.png'))
    # Initialize the drawing context with template as background
    draw = ImageDraw.Draw(template)

    # Current weather
    ## Open icon file
    icon_file = icon_code + '.png'
    icon_image = Image.open(os.path.join(icondir, icon_file))
    icon_image = icon_image.resize((130, 130))
    icon_image.close
    template.paste(icon_image, (50, 50))

    draw.text((125, 10), LOCATION, font=font35, fill=black)

    # Center current weather report
    w, h = draw.textsize(string_report, font=font20)
    if w > 250:
        string_report = 'Now:\n' + report.title()

    center = int(120 - (w / 2))
    draw.text((center, 175), string_report, font=font20, fill=black)

    # Data
    draw.text((250, 55), string_temp_current, font=font35, fill=black)
    y = 100
    draw.text((250, y), string_feels_like, font=font15, fill=black)
    draw.text((250, y + 20), string_humidity, font=font15, fill=black)
    draw.text((250, y + 40), string_wind, font=font15, fill=black)
    draw.text((250, y + 60), string_precip_percent, font=font15, fill=black)
    draw.text((250, y + 80), string_temp_max, font=font15, fill=black)
    draw.text((250, y + 100), string_temp_min, font=font15, fill=black)

    draw.text((125, 218), last_update_string, font=font15, fill=black)

    # Weather Forcast
    # Tomorrow
    icon_file = nx_icon + '.png'
    icon_image = Image.open(os.path.join(icondir, icon_file))
    icon_image = icon_image.resize((130, 130))
    template.paste(icon_image, (435, 50))
    icon_image.close
    draw.text((450, 20), 'Tomorrow', font=font22, fill=black)
    draw.text((415, 180), nx_day_high, font=font15, fill=black)
    draw.text((515, 180), nx_day_low, font=font15, fill=black)
    draw.text((460, 200), nx_precip_percent, font=font15, fill=black)

    # Next Next Day Forcast
    # Center day of week
    nx_nx_day_of_week = (now + dt.timedelta(days=2)).strftime('%A')
    w, h = draw.textsize(nx_nx_day_of_week, font=font22)
    center = int(700 - (w / 2))
    icon_file = nx_nx_icon + '.png'
    icon_image = Image.open(os.path.join(icondir, icon_file))
    icon_image = icon_image.resize((130, 130))
    template.paste(icon_image, (635, 50))
    icon_image.close
    draw.text((center, 20), nx_nx_day_of_week, font=font22, fill=black)
    draw.text((615, 180), nx_nx_day_high, font=font15, fill=black)
    draw.text((715, 180), nx_nx_day_low, font=font15, fill=black)
    draw.text((660, 200), nx_nx_precip_percent, font=font15, fill=black)

    ## Dividing lines
    draw.line((400, 10, 400, 220), fill='black', width=3)
    draw.line((600, 20, 600, 210), fill='black', width=2)

    # Large horizontal dividing line
    h = 240
    draw.line((25, h, 775, h), fill='black', width=3)
    # Daily tide times
    draw.text((30, 260), "Today's News font 22", font=font22, fill=black)
    draw.text((30, 300), "Line 1 font 15", font=font15, fill=black)
    draw.text((30, 320), "Line 2 font 15", font=font15, fill=black)
    draw.text((30, 340), "Line 3 font 15", font=font15, fill=black)
    draw.text((30, 360), "Line 4 font 15", font=font15, fill=black)
    draw.text((30, 380), "Line 5 font 15", font=font15, fill=black)
    draw.text((30, 400), "Line 6 font 15", font=font15, fill=black)
    draw.text((30, 420), "Line 7 font 15", font=font15, fill=black)
    draw.text((30, 440), "Line 8 font 15", font=font15, fill=black)

    # Lunar Phase Info
    current_phase = moon.phase(now)
    phase_today, current_phase_index = day_to_moon_phase_and_accurate_code(now)
    current_phase_name = moon_phases[current_phase_index]
    city = LocationInfo(LOCATION, LOCATION, TIMEZONE, LATITUDE, LONGITUDE)
    sun_info = sun.sun(city.observer, dt.datetime.now(), tzinfo=city.tzinfo)

    string_sunrise = "Sunrise: " + sun_info["sunrise"].strftime("%H:%M")
    string_sunset = "Sunset:  " + sun_info["sunset"].strftime("%H:%M")

    ## Open icon file
    moon_icon = str(current_phase_index) + '.png'
    moon_image = Image.open(os.path.join(moondir, moon_icon))
    moon_image = moon_image.resize((150, 150))

    # Vertical Dividing Line
    draw.line((600, 250, 600, 460), fill='black', width=2)
    # Add moon phase image
    template.paste(moon_image, (625, 265), moon_image)
    moon_image.close
    draw.text((640, 255), "Lunar Phase", font=font22, fill=black)
    w, h = draw.textsize(current_phase_name, font=font15)
    center = int(700 - (w / 2))
    draw.text((center, 390), current_phase_name, font=font15, fill=black)
    draw.text((635, 420), string_sunrise, font=font20, fill=black)
    draw.text((635, 440), string_sunset, font=font20, fill=black)

    # Save the image template for display as PNG
    screen_output_file = os.path.join(picdir, 'screen_output.png')
    template.save(screen_output_file)

    resized_img = template.resize((640,384), Image.ANTIALIAS)
    screen_output_file = os.path.join(picdir, 'screen_output_resized.png')
    resized_img.save(screen_output_file)

    # Close the template file
    template.close()
    write_to_screen(screen_output_file)
    sleep(600)
    epd.init()  # Re-Initialize screen
