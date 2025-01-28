import xbmc
import xbmcgui
import os
import time

# Path to the directory containing your audio files
AUDIO_DIR = "Q:/scripts/script.doubutsu/audio"

def get_current_hour():
    """Get the current hour in 12-hour format without leading zero."""
    hour_with_zero = time.strftime("%I%p")  # e.g., "01PM", "02PM"
    return hour_with_zero.lstrip("0")  # Remove leading zero, e.g., "1PM", "2PM"

def get_audio_file(hour):
    """Get the corresponding audio file for the current hour."""
    return os.path.join(AUDIO_DIR, "{}.mp3".format(hour))

def play_audio(file_path, last_hour):
    """Play the audio file in a loop until the hour changes."""
    player = xbmc.Player()
    while True:
        player.play(file_path)
        # Wait for playback to start
        while not player.isPlaying():
            xbmc.sleep(100)  # Sleep briefly to avoid busy-waiting
        # Keep playing until the file ends or the hour changes
        while player.isPlaying():
            xbmc.sleep(1000)  # Sleep for 1 second
            current_hour = get_current_hour()
            if current_hour != last_hour:
                return  # Exit if the hour changes

def main():
    last_hour = None
    while True:
        current_hour = get_current_hour()
        if current_hour != last_hour:
            last_hour = current_hour
            audio_file = get_audio_file(current_hour)
            if os.path.exists(audio_file):
                play_audio(audio_file, last_hour)
            else:
                xbmc.log("Audio file not found: {}".format(audio_file), xbmc.LOGERROR)
        xbmc.sleep(1000)  # Sleep for 1 second before checking the time again

if __name__ == "__main__":
    main()
