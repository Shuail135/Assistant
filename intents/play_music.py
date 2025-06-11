from youtubesearchpython import VideosSearch
import webbrowser
import urllib.parse

# YouTube Music handler
#basically search it from youtube(youtubesearchpython) and copy it to youtube music
def play_youtube_music(song):
    search_song = song + " song"
    print(song)
    videosSearch = VideosSearch(search_song, limit=1)
    result = videosSearch.result()
    first_result = result['result'][0]
    video_id = first_result['id']

    music_url = f"https://music.youtube.com/watch?v={video_id}"
    webbrowser.open(music_url)

    return f"Playing '{song}' on YouTube Music..."


# YouTube handler
def play_youtube(song):
    query = urllib.parse.quote(song)
    url = f"https://www.youtube.com/results?search_query={query}"
    webbrowser.open(url)
    return f"Searching for '{song}' on YouTube..."


# Placeholder for Spotify
def play_spotify(song):
    return f"Spotify integration not implemented yet'."


# Placeholder for Tidal
def play_tidal(song):
    return f"Tidal integration not implemented'."

music_dispatch = {
    0: play_youtube_music,
    1: play_youtube,
    2: play_spotify, # not implemented
    3: play_tidal # not implemented
}

music_application=0

def run(request_input):
    song = request_input("What song would you like to play ")
    play_func = music_dispatch.get(music_application)

    if play_func:
        return play_func(song)
    else:
        return "Unknown music application selected."

#Test case

if __name__ == "__main__":
    def dummy_request_input(prompt):
        return "Mozart"

    run(dummy_request_input)
