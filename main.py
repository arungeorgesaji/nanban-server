from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import shutil
import uuid
from pathlib import Path

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_methods=["*"],  
    allow_headers=["*"],  
)

TEMP_DIR = Path("temp")
TEMP_DIR.mkdir(exist_ok=True)  

@app.post("/object-detection/")
async def upload_picture(file: UploadFile = File(...)):
    unique_filename = f"{uuid.uuid4()}.jpg"
    
    picture_path = TEMP_DIR / unique_filename
    with picture_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    voice_file_path = TEMP_DIR / f"{uuid.uuid4()}.mp3"
    with voice_file_path.open("wb") as buffer:
        buffer.write(b"Dummy voice data")
    
    return FileResponse(voice_file_path, media_type="audio/mpeg", filename=voice_file_path.name)

@app.post("/voice-assistant/")
async def upload_voice(file: UploadFile = File(...)):
    unique_filename = f"{uuid.uuid4()}.mp3"
    
    voice_input_path = TEMP_DIR / unique_filename
    with voice_input_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    processed_voice_path = TEMP_DIR / f"{uuid.uuid4()}.mp3"
    with processed_voice_path.open("wb") as buffer:
        buffer.write(b"Processed voice data")
    
    return FileResponse(processed_voice_path, media_type="audio/mpeg", filename=processed_voice_path.name)

