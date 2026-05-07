# WhatsApp Guess Game 🕵️‍♂️💬

A fun "Who said it?" trivia game backend built with FastAPI. Upload your exported WhatsApp chat history (`.zip` format) and play a game with your friends guessing who sent which random message, photo, or voice note!

## Features

- **FastAPI Powered:** Fast, lightweight, and modern Python backend.
- **`.zip` Auto-extraction:** Just drop your WhatsApp export zip, and the server automatically unzips it, extracts `_chat.txt`, and saves the media to an `Uploads/` directory.
- **Media Support:** Seamlessly handles text, photos, video, audio (`.opus`), and stickers (`.webp`).
- **Dynamic Distractors:** Automatically scans the chat to find all participants and send them to the frontend for multiple-choice options.
- **Leaderboard Stats:** Tracks who sent the most messages in your group.
- **Session Cleanup:** Securely clear out old chat uploads and media.

## Installation & Setup

1. **Clone the repository**
2. **Install the dependencies:**
   Make sure you have Python installed, then install the required packages:
   ```bash
   pip install fastapi uvicorn pydantic python-multipart
   ```
3. **Run the game:**
   The easiest way to start the game on Windows is to simply double-click the **`run.bat`** file. 
   - This automatically activates the virtual environment, starts the FastAPI server, and launches the frontend `Web\index.html` in your default browser.
   
   *(Alternatively, run `uvicorn GuessBackend:app --reload --host 0.0.0.0 --port 8000` via terminal and open `Web\index.html` manually).*

4. **Access the API:**
   The backend will be running at `http://localhost:8000`. You can view the automatic interactive API documentation at `http://localhost:8000/docs`.

## API Endpoints

- `GET /`: Health check to see if the backend is running.
- `POST /upload`: Upload your WhatsApp `.zip` export file.
- `GET /message`: Fetches a random message, user, and time (and any attached media paths).
- `GET /user`: Returns a list of all unique users in the chat.
- `GET /media/{filename}`: Streams the media files to the frontend.
- `GET /mostmessages`: Returns the count of messages grouped by user.
- `POST /clear-uploads`: Deletes all contents of the `Uploads` folder.
