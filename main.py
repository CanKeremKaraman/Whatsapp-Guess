import random
import zipfile
from pathlib import Path
from collections import defaultdict


BASE_DIR = Path(__file__).resolve().parent
UPLOAD_DIR = BASE_DIR / "Uploads"


def ParseChatLine(line: str):
    if " - " not in line:
        return None

    time_part, rest = line.split(" - ", 1)
    if ": " not in rest:
        return None

    user, message = rest.split(": ", 1)
    user = user.strip()
    if not user or user == "System":
        return None

    return time_part.strip(), user, message.strip()


def ExtractMediaFilename(message: str):
    if not message:
        return None

    msg = message.strip()
    if msg.lower() == "<media omitted>":
        return None

    if msg.startswith("<attached:") and msg.endswith(">"):
        inner = msg[len("<attached:"):-1].strip()
        return inner or None

    marker = " (file attached)"
    if marker in msg:
        name = msg.split(marker, 1)[0].strip()
        return name or None

    return None

def GetRandomMessage():
    chat_path = GetChatFilePath()
    with open(chat_path, encoding="utf-8") as f:
        lines = f.read().rstrip('\n').split('\n')

    parsed = [ParseChatLine(line) for line in lines]
    valid = [item for item in parsed if item]
    if not valid:
        return {"time": "", "user": "", "message": ""}

    time, user, message = random.choice(valid)
    return {
        "time": time,
        "user": user,
        "message": message
    }


def GetChatFilePath():
    upload_dir = UPLOAD_DIR
    if upload_dir.exists() and upload_dir.is_dir():
        txt_files = sorted(upload_dir.rglob("*.txt"))
        if txt_files:
            return txt_files[0]
    return BASE_DIR / "_chat.txt"


def GetUserNames():
    unique_users = set()
    chat_path = GetChatFilePath()
    with open(chat_path, encoding="utf-8") as f:
        lines = f.read().rstrip('\n').split('\n')



    for line in lines:
        parsed = ParseChatLine(line)
        if parsed:
            _, user, _ = parsed
            if user != "Meta AI":
                unique_users.add(user)

    return sorted(unique_users)


def ExtractZipFile(FilePath):
    upload_dir = UPLOAD_DIR
    upload_dir.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(FilePath, "r") as zipref:
        zipref.extractall(upload_dir)


def MessagesCountList():
    chat_path = GetChatFilePath()
    UserMessageCount = defaultdict(int)

    with open(chat_path, encoding="utf-8") as f:
        lines = f.read().rstrip('\n').split('\n')

    for line in lines:
        parsed = ParseChatLine(line)
        if parsed:
            _, user, _ = parsed
            if user != "Meta AI":
                UserMessageCount[user] += 1

    return UserMessageCount