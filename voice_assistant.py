import subprocess
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import requests
from bs4 import BeautifulSoup
import datetime
import json
import io
from pytube import YouTube
from youtube_search import YoutubeSearch
from pydub import AudioSegment
from pydub.playback import play
import speech_recognition as sr
import keyboard
from gtts import gTTS
import os
from huggingface_hub import login
from langchain.llms import HuggingFaceHub
from dotenv import load_dotenv

load_dotenv()
IPDATA_API_KEY = os.getenv("IPDATA_API_KEY")
SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
HUGGINGFACEHUB_API_TOKEN = os.getenv("HUGGINGFACEHUB_API_TOKEN") 

gemma7b = HuggingFaceHub(repo_id='google/gemma-1.1-7b-it')

client_credentials_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

def text_to_speech(text, lang='en', output_file):
    tts = gTTS(text=text, lang=lang)
    tts.save(output_file)

def remove_unwanted_characters(input_text):
    characters_to_remove = ["*", "_", "?", ">", "<", "=", "^", "(", ")", "{", "}", "[", "]", "#", "'", "#", "`"]
    for char in characters_to_remove:
        input_text = input_text.replace(char, "")
    return input_text

def get_time():
    return datetime.datetime.now().strftime("%H:%M")

def search_google(query, num_results=10):
    search_url = f"https://www.google.com/search?q={query}&num={num_results}"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }
    response = requests.get(search_url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    snippets = []
    for result in soup.find_all('div', class_='tF2Cxc'):
        snippet = result.find('span', class_='aCOpRe')
        if snippet:
            snippets.append(snippet.text)
    
    return '\n'.join(snippets)

def get_location(ipdata_api_key):
    url = f'https://api.ipdata.co?api-key={ipdata_api_key}'
    return requests.get(url).json()

def gemma7b_response(input_text, context, length):
    search_results = search_google(input_text)
    location = get_location(IPDATA_API_KEY)
    city = location.get('city', 'Unknown')
    country = location.get('country_name', 'Unknown')
    local_time = get_time()
    
    template = f"""
    ###context:{context},
    ###instruction:Provide the complete answer,also you can use the search results which I have got for the same query but I cannot confirm its related please carefully access if its need and if its needed you can assist in providing the response to the user.Also make sure to use proper grammer and other characters as this is being read by a text to speech program also you are allowed to your own answer its not necessary you use the google results but for information like time and stuff which changes like you might not exactly know of right now please refer the search results and using that please provide trhe approprita answer in a human friendly way.Also you can use all the other informatioh provided if necessary.Please dont use unnecessary information and just respond with the information the user asked for 
    ###Search Results from Google for the Same Query: {search_results}
    ###Users country of origin : {country}
    ###Users city of origin : {city}
    ###Users local time: {local_time}
    ###length: {length}
    ###question:{input_text},
    ###answer:
    """
    response = gemma7b(template).split("###answer:")[1].split("**Answer:**")[0]
    return response

def get_response(input_text):
    context = """
    The guy who is asking the question is a blind person who is using you inside the product Nanban.
    You are being used as a voice assistant to answer his queries please answer fully and carefully.
    Please dont leave out any point even though its needs to be if its needed the answer can always
    be long also make sure to respond every question with words only avoid using symbols and numbers
    if needed the numbers and symbols should be expressed in word form.
    """
    length = "as long as possible"
    response = gemma7b_response(input_text, context, length)
    clean_response = remove_unwanted_characters(response)
    speak(clean_response)

def search_song():
    while True:
        speak("please confirm the song you want to hear or use exit to exit")
        video = takecommand().lower()
    
        if video == "error":
            continue
        elif video == "exit":
            speak("Exiting music mode")
            break

        results = YoutubeSearch(video, max_results=1).to_dict()
        if results:
            video_id = results[0]['id']
            url = f"https://www.youtube.com/watch?v={video_id}"
            speak("Downloading song from youtube...")
            download_audio(url)
            speak("Playing song...")
            play_song()
        else:
            speak("song not found")

def download_audio(url):
    yt = YouTube(url)
    audio_stream = yt.streams.filter(only_audio=True).first()
    audio_stream.download(output_path=".", filename="temp_song")

def play_song():
    song = AudioSegment.from_file("temp_song")
    play(song)

def helpline(input_text):
    speak("please ask the questions you want and use exit to exit whenever you want")
    context = """
    [Your existing helpline context here]
    """
    instruction = """
    Please use the context to help you answer the question, the user is a blind person 
    who is using nanban which a device running on the raspberry pi 5. You are being used in the nanban
    helpline to help the use remember this guy is a blind person he might not be able to do a lot of things
    he might not even know that a raspberry pi is inside dont go like display nanban doesnt have a display 
    the complete communication is through voice remember you can use questions outside the context
    these you could consider as some examples to get an idea of how to answer and if a similar 
    question pops up you can easily answer. Please answer to just what the user asks dont try to do anything else
    """
    
    while True:
        query = takecommand().lower()
        if query == "exit":
            speak("Exiting help mode")
            break
        else:
            template = f"""
            ###context:{context},
            ###Instruction: {instruction},
            ###length: as long as possible never stop in between this will cause confuse the blind person
            ###question:{query},
            ###answer:
            """
            response = gemma7b(template).split("###answer:")[1].split("**Answer:**")[0]
            clean_response = remove_unwanted_characters(response)
            speak(clean_response)

def voice_mode():
    query = takecommand().lower()
    
    if query == 'error':
        return
        
    if query in ["music mode", "music mod"]:
        search_song() 
    elif query in ["help mode", "help mod"]:
        helpline(query)
    else:
        get_response(query)

