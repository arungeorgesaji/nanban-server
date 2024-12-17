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
import os
from huggingface_hub import login
from langchain.llms import HuggingFaceHub
from dotenv import load_dotenv

load_dotenv()
IPDATA_API_KEY = os.getenv("IPDATA_API_KEY")
HUGGINGFACEHUB_API_TOKEN = os.getenv("HUGGINGFACEHUB_API_TOKEN") 

gemma7b = HuggingFaceHub(repo_id='google/gemma-1.1-7b-it')

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
    return clean_response

def voice_mode(query):
    if query == 'error':
        return
    else:
        return get_response(query)
