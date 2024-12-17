from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import shutil
import uuid
from pathlib import Path
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

@app.post("/object-detection/")
async def process_image(file: UploadFile = File(...)):
    unique_filename = f"{uuid.uuid4()}.jpg"
    
    picture_path = TEMP_DIR / unique_filename
    with picture_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
   
    detected_description = detect_objects(picture_path)
    voice_file_path = "processed_audio.mp3"
    text_to_speech(detected_description, voice_file_path)
    
    return FileResponse(voice_file_path, media_type="audio/mpeg", filename=voice_file_path.name)

@app.post("/voice-assistant/")
async def process_voice(file: UploadFile = File(...)):
    unique_filename = f"{uuid.uuid4()}.mp3"
    
    voice_input_path = TEMP_DIR / unique_filename
    with voice_input_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return FileResponse(processed_voice_path, media_type="audio/mpeg", filename=processed_voice_path.name)

