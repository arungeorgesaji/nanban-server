from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import shutil
import uuid
from pathlib import Path
from gtts import gTTS
from voice_assistant import *
from object_detection import * 

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_methods=["*"],  
    allow_headers=["*"],  
)

TEMP_DIR = Path("temp")
TEMP_DIR.mkdir(exist_ok=True)

MODEL_DIR = Path("models")
MODEL_DIR.mkdir(exist_ok=True) 
model = YOLO(MODEL_dir + "yolov8m-seg.pt")

object_widths = load_object_widths("object_widths.yaml")

def text_to_speech(text, lang='en', output_file):
    tts = gTTS(text=text, lang=lang)
    tts.save(output_file)

@app.post("/object-detection/")
async def process_image(file: UploadFile = File(...)):
    picture_file_path = TEMP_DIR / f"{uuid.uuid4()}.jpg"
    with picture_file_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
   
    detected_description = detect_objects(picture_file_path)

    speech_file_path = TEMP_DIR / f"{uuid.uuid4()}.mp3"
    text_to_speech(detected_description, speech_file_path)
    
    return FileResponse(voice_file_path, media_type="audio/mpeg", filename=voice_file_path.name)

async def process_voice(query: str):
    assistant_response = voice_mode(query)  
    response_audio_path = TEMP_DIR / f"{uuid.uuid4()}.mp3"
    text_to_speech(assistant_response, response_audio_path)

    return FileResponse(response_audio_path, media_type="audio/mpeg", filename=unique_filename)
