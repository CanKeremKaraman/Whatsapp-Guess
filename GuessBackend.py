from fastapi import FastAPI, File, UploadFile, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import shutil
from main import *
from typing import Optional
from fastapi.responses import FileResponse
from pathlib import Path


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

class MessageData(BaseModel):
    message: str
    user: str
    time: str
    image: Optional[str] = None

@app.get("/")
async def root():
    return {"message": "Legalize Nucleer Bombs - Backend is running!"}

@app.get("/message", response_model=MessageData)
async def GetMessage(
    merge: bool = True,
    min_words: int = Query(MIN_MESSAGE_WORDS, ge=0, le=30),
    merge_window: int = Query(MERGE_WINDOW_MINUTES, ge=0, le=60),
    balance_users: bool = False,
):
    data = GetRandomMessage(
        merge_window_minutes=merge_window,
        min_words=min_words,
        merge_bursts=merge,
        balance_users=balance_users,
    )

    image_file = ExtractMediaFilename(data["message"])
    message_text = NormalizeMessageForDisplay(data["message"])
    if image_file:
        return MessageData(
            message=message_text,
            user=data["user"],
            time=data["time"],
            image=f"/media/{image_file}"
        )

    # If it is just a normal text message
    return MessageData(
        message=message_text,
        user=data["user"],
        time=data["time"]
    )

@app.post("/upload")
async def UploadFiles(file: UploadFile = File(...)):
    # This endpoint receives the file from the frontend and saves it
    upload_dir = UPLOAD_DIR
    upload_dir.mkdir(parents=True, exist_ok=True)
    file_location = upload_dir / file.filename
    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    if ".zip" in file.filename:
        ExtractZipFile(file_location)

    return {"info": f"file '{file.filename}' saved at '{file_location}'"}

@app.get("/user")
async def GetUser():
    data = GetUserNames()
    return data

@app.get("/media/{filename}")
async def GetImage(filename: str):
    return FileResponse(Path("Uploads") / filename)


@app.post("/clear-uploads")
async def ClearUploads():
    upload_dir = Path("Uploads")
    if not upload_dir.exists() or not upload_dir.is_dir():
        return {"cleared": 0, "info": "Uploads folder does not exist"}

    cleared = 0
    for entry in upload_dir.iterdir():
        if entry.is_dir():
            shutil.rmtree(entry)
            cleared += 1
        else:
            entry.unlink(missing_ok=True)
            cleared += 1

    return {"cleared": cleared}

@app.get("/mostmessages")
async def GetMostMessages():
    data = MessagesCountList()
    data = dict(data)
    return data
