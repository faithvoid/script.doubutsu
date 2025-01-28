import xbmc
import xbmcgui
import os
import time

# Path to the directory containing your audio files
AUDIO_DIR = "Q:/scripts/script.doubutsu/audio"

def get_current_hour():
    """Get the current hour in 12-hour format."""
    return time.strftime("%I%p")

def get_audio_file(hour):
    """Get the corresponding audio file for the current hour."""
    return os.path.join(AUDIO_DIR, "{}.mp3".format(hour))

def play_audio(file_path):
    """Play the audio file in a loop."""
    player = xbmc.Player()
    player.play(file_path)
    while player.isPlaying():
        xbmc.sleep(1000)  # Sleep for 1 second

def main():
    last_hour = None
    while not xbmc.abortRequested:
        current_hour = get_current_hour()
        if current_hour != last_hour:
            last_hour = current_hour
            audio_file = get_audio_file(current_hour)
            if os.path.exists(audio_file):
                play_audio(audio_file)
            else:
                xbmc.log("Audio file not found: {}".format(audio_file), xbmc.LOGERROR)
        xbmc.sleep(1000)  # Sleep for 1 second before checking the time again

if __name__ == "__main__":
    main()
