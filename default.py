# -*- coding: utf-8 -*-
import xbmc
import xbmcaddon
import os
import time
import urllib2
import json

addon = xbmcaddon.Addon('script.doubutsu')
BASE_AUDIO_PATH = addon.getSetting('soundtrack').rstrip('\\') if addon.getSetting('soundtrack') else os.path.join(os.path.dirname(__file__), "audio")
WEATHER_CITY = addon.getSetting('weather_city')
WEATHER_URL = "https://wttr.in/{}?format=j1".format(WEATHER_CITY)
TEMP_UNIT = addon.getSetting('temp_unit') or "C"  # "C" or "F"

def get_weather_state_and_temp():
    try:
        req = urllib2.Request(WEATHER_URL, headers={'User-Agent': 'Mozilla/5.0'})
        response = urllib2.urlopen(req, timeout=5)
        data = response.read()
        weather = json.loads(data)
        main_desc = weather['current_condition'][0]['weatherDesc'][0]['value']
        main_desc_lc = main_desc.lower()
        temp_c = weather['current_condition'][0].get('temp_C', "??")
        temp_f = weather['current_condition'][0].get('temp_F', "??")
        # Defensive check
        if not temp_c or not temp_c.strip() or not temp_c.replace('-','').isdigit():
            temp_c = "??"
        if not temp_f or not temp_f.strip() or not temp_f.replace('-','').isdigit():
            temp_f = "??"
        if 'rain' in main_desc_lc or 'drizzle' in main_desc_lc or 'thunder' in main_desc_lc:
            weather_simple = 'Rainy'
        elif 'snow' in main_desc_lc or 'sleet' in main_desc_lc or 'blizzard' in main_desc_lc:
            weather_simple = 'Snowy'
        elif 'clear' in main_desc_lc or 'sun' in main_desc_lc:
            weather_simple = 'Sunny'
        elif 'cloud' in main_desc_lc or 'overcast' in main_desc_lc:
            weather_simple = 'Cloudy'
        else:
            weather_simple = main_desc.capitalize()
        return weather_simple, main_desc, temp_c, temp_f
    except Exception as e:
        xbmc.log("Failed to fetch weather: {}".format(e), xbmc.LOGERROR)
        return "Clear", "Clear", "??", "??"

def get_season():
    if addon.getSetting('SUMMER') == "true":
        return "summer"
    if addon.getSetting('WINTER') == "true":
        return "winter"
    if addon.getSetting('FALL') == "true":
        return "fall"
    if addon.getSetting('SPRING') == "true":
        return "spring"
    month = int(time.strftime("%m"))
    if month in (12, 1, 2):
        return "winter"
    if month in (3, 4, 5):
        return "spring"
    if month in (6, 7, 8):
        return "summer"
    if month in (9, 10, 11):
        return "fall"
    return "unknown"

def get_audio_dir(season, weather):
    weather_lc = weather.lower()
    if weather_lc in ("rainy", "rain"):
        path = os.path.join(BASE_AUDIO_PATH, season, "rainy")
        if os.path.isdir(path):
            return path
    elif weather_lc in ("snowy", "snow"):
        path = os.path.join(BASE_AUDIO_PATH, season, "snowy")
        if os.path.isdir(path):
            return path
    elif weather_lc in ("clear", "sunny", "cloudy"):
        path = os.path.join(BASE_AUDIO_PATH, season)
        if os.path.isdir(path):
            return path
    path = os.path.join(BASE_AUDIO_PATH, season)
    if os.path.isdir(path):
        return path
    return BASE_AUDIO_PATH

def get_current_hour():
    hour_with_zero = time.strftime("%I%p")
    return hour_with_zero.lstrip("0")  # e.g., "1PM"

def get_audio_file(audio_dir, hour):
    return os.path.join(audio_dir, "{}.mp3".format(hour))

def notify_now_playing(hour, track_path, weather_simple, temp_c, temp_f):
    track_name = os.path.splitext(os.path.basename(track_path))[0]
    if TEMP_UNIT.upper() == "F":
        temp = "{}°F".format(temp_f)
    else:
        temp = "{}°C".format(temp_c)
    xbmc.executebuiltin(
        'Notification("Doubutsu", "{hour} - ({weather}) - {temp}", 5000, "{icon}")'.format(
            hour=hour,
            weather=weather_simple,
            temp=temp,
            track=track_name,
            icon=os.path.join(os.path.dirname(__file__), "default.tbn")
        )
    )

def play_audio_until_next_hour(file_path, this_hour):
    player = xbmc.Player()
    player.play(file_path)
    while not player.isPlaying():
        xbmc.sleep(100)
    while player.isPlaying():
        xbmc.sleep(1000)
        if get_current_hour() != this_hour:
            player.stop()
            break

def main():
    last_hour = None
    while True:
        current_hour = get_current_hour()
        if current_hour != last_hour:
            last_hour = current_hour
            season = get_season()
            weather_simple, weather_verbose, temp_c, temp_f = get_weather_state_and_temp()
            audio_dir = get_audio_dir(season, weather_simple)
            audio_file = get_audio_file(audio_dir, current_hour)
            if os.path.exists(audio_file):
                notify_now_playing(current_hour, audio_file, weather_simple, temp_c, temp_f)
                play_audio_until_next_hour(audio_file, current_hour)
            else:
                xbmc.log("Audio file not found: {}".format(audio_file), xbmc.LOGERROR)
        xbmc.sleep(1000)

if __name__ == "__main__":
    main()
