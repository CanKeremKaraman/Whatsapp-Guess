import random
import re
import shutil
import zipfile
from datetime import datetime, timedelta
from pathlib import Path
from collections import defaultdict


BASE_DIR = Path(__file__).resolve().parent
UPLOAD_DIR = BASE_DIR / "Uploads"
NEW_MESSAGE_RE = re.compile(r"^\d{1,2}/\d{1,2}/\d{2,4}, \d{1,2}:\d{2}")
DATE_PART_RE = re.compile(r"^(\d{1,2})/(\d{1,2})/(\d{2,4}),\s*(.+)$")
WORD_RE = re.compile(r"\b[\w']+\b")

MERGE_WINDOW_MINUTES = 2
MIN_MESSAGE_WORDS = 3

_CACHED_CHAT_KEY = None
_CACHED_MESSAGES = None
_CACHED_PLAYABLE = {}
_CACHED_GROUPED = {}
_CACHED_USER_LIST = None
_CACHED_MESSAGE_COUNTS = None


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


def InvalidateDerivedCaches():
    global _CACHED_PLAYABLE, _CACHED_GROUPED, _CACHED_USER_LIST, _CACHED_MESSAGE_COUNTS
    _CACHED_PLAYABLE = {}
    _CACHED_GROUPED = {}
    _CACHED_USER_LIST = None
    _CACHED_MESSAGE_COUNTS = None


def BuildTimeFormats(day_first: bool):
    date_fmt = "%d/%m" if day_first else "%m/%d"
    return [
        f"{date_fmt}/%y, %H:%M",
        f"{date_fmt}/%Y, %H:%M",
        f"{date_fmt}/%y, %I:%M %p",
        f"{date_fmt}/%Y, %I:%M %p",
    ]


def ParseMessageTime(time_part: str):
    if not time_part:
        return None

    time_part = time_part.strip()
    match = DATE_PART_RE.match(time_part)
    day_first = False
    if match:
        first = int(match.group(1))
        second = int(match.group(2))
        if first > 12 and second <= 12:
            day_first = True
        elif second > 12 and first <= 12:
            day_first = False

    formats = BuildTimeFormats(day_first)
    formats += BuildTimeFormats(not day_first)

    for fmt in formats:
        try:
            return datetime.strptime(time_part, fmt)
        except ValueError:
            continue

    return None


def CountWords(text: str):
    if not text:
        return 0

    return len(WORD_RE.findall(text))


def ExtractMediaFilename(message: str):
    if not message:
        return None

    msg = message.strip()
    if not msg:
        return None

    first_line = msg.splitlines()[0].strip()
    if first_line.lower() == "<media omitted>":
        return None

    if first_line.startswith("<attached:") and first_line.endswith(">"):
        inner = first_line[len("<attached:"):-1].strip()
        return inner or None

    marker = " (file attached)"
    if marker in first_line:
        name = first_line.split(marker, 1)[0].strip()
        return name or None

    return None


def NormalizeMessageForDisplay(message: str):
    if not message:
        return ""

    lines = message.splitlines()
    if not lines:
        return ""

    first_line = lines[0].strip()
    rest = "\n".join(lines[1:]).strip()

    if first_line.lower() == "<media omitted>":
        return rest or first_line

    if first_line.startswith("<attached:") and first_line.endswith(">"):
        return rest

    marker = " (file attached)"
    if first_line.endswith(marker):
        return rest

    return message.strip()


def ShouldKeepMessage(message: str, min_words: int):
    if ExtractMediaFilename(message):
        return True

    if min_words <= 0:
        return True

    text = NormalizeMessageForDisplay(message)
    return CountWords(text) >= min_words


def MergeBurstMessages(messages, window_minutes):
    if not messages:
        return []

    merged = []
    current = dict(messages[0])
    current_has_media = ExtractMediaFilename(current["message"]) is not None
    last_time = current.get("time_dt") or ParseMessageTime(current["time"])

    for msg in messages[1:]:
        msg_time = msg.get("time_dt") or ParseMessageTime(msg["time"])
        msg_has_media = ExtractMediaFilename(msg["message"]) is not None

        can_merge = (
            msg["user"] == current["user"]
            and last_time is not None
            and msg_time is not None
            and msg_time >= last_time
            and msg_time - last_time <= timedelta(minutes=window_minutes)
            and not current_has_media
            and not msg_has_media
        )

        if can_merge:
            current["message"] += "\n" + msg["message"]
            last_time = msg_time
        else:
            merged.append(current)
            current = dict(msg)
            current_has_media = msg_has_media
            last_time = msg_time

    merged.append(current)
    return merged


def GroupMessagesByUser(messages):
    grouped = defaultdict(list)
    for message in messages:
        grouped[message["user"]].append(message)
    return grouped


def GetChatMessages():
    chat_path = GetChatFilePath()
    if not chat_path.exists():
        return []

    global _CACHED_CHAT_KEY, _CACHED_MESSAGES
    stat = chat_path.stat()
    cache_key = (str(chat_path), stat.st_mtime, stat.st_size)
    if _CACHED_CHAT_KEY == cache_key and _CACHED_MESSAGES is not None:
        return _CACHED_MESSAGES

    with open(chat_path, encoding="utf-8") as f:
        lines = f.read().splitlines()

    messages = []
    current = None

    for line in lines:
        parsed = ParseChatLine(line)
        if parsed:
            if current:
                messages.append(current)
            time, user, message = parsed
            current = {
                "time": time,
                "time_dt": ParseMessageTime(time),
                "user": user,
                "message": message,
            }
        elif current is not None:
            if " - " in line and NEW_MESSAGE_RE.match(line):
                messages.append(current)
                current = None
            else:
                current["message"] += "\n" + line

    if current:
        messages.append(current)

    _CACHED_CHAT_KEY = cache_key
    _CACHED_MESSAGES = messages
    InvalidateDerivedCaches()
    return _CACHED_MESSAGES


def GetPlayableMessages(
    merge_window_minutes=MERGE_WINDOW_MINUTES,
    min_words=MIN_MESSAGE_WORDS,
    merge_bursts=True,
):
    messages = GetChatMessages()
    if not messages:
        return []

    cache_key = (_CACHED_CHAT_KEY, merge_window_minutes, min_words, merge_bursts)
    cached = _CACHED_PLAYABLE.get(cache_key)
    if cached is not None:
        return cached

    merged = (
        MergeBurstMessages(messages, merge_window_minutes)
        if merge_bursts and merge_window_minutes > 0
        else messages
    )
    playable = [msg for msg in merged if ShouldKeepMessage(msg["message"], min_words)]
    _CACHED_PLAYABLE[cache_key] = playable
    _CACHED_GROUPED.pop(cache_key, None)
    return playable

def GetRandomMessage(
    merge_window_minutes=MERGE_WINDOW_MINUTES,
    min_words=MIN_MESSAGE_WORDS,
    merge_bursts=True,
    balance_users=False,
):
    messages = GetPlayableMessages(merge_window_minutes, min_words, merge_bursts)
    used_fallback = False
    if not messages:
        messages = GetChatMessages()
        used_fallback = True
    if not messages:
        return {"time": "", "user": "", "message": ""}

    if balance_users:
        if used_fallback:
            grouped = GroupMessagesByUser(messages)
        else:
            cache_key = (_CACHED_CHAT_KEY, merge_window_minutes, min_words, merge_bursts)
            grouped = _CACHED_GROUPED.get(cache_key)
            if grouped is None:
                grouped = GroupMessagesByUser(messages)
                _CACHED_GROUPED[cache_key] = grouped
        if grouped:
            user = random.choice(list(grouped.keys()))
            return random.choice(grouped[user])

    return random.choice(messages)


def GetChatFilePath():
    upload_dir = UPLOAD_DIR
    if upload_dir.exists() and upload_dir.is_dir():
        txt_files = sorted(upload_dir.rglob("*.txt"))
        if txt_files:
            return txt_files[0]
    return BASE_DIR / "_chat.txt"


def GetUserNames():
    global _CACHED_USER_LIST
    if _CACHED_USER_LIST is not None:
        return _CACHED_USER_LIST

    unique_users = set()
    for message in GetChatMessages():
        user = message["user"]
        if user != "Meta AI":
            unique_users.add(user)

    _CACHED_USER_LIST = sorted(unique_users)
    return _CACHED_USER_LIST


def ExtractZipFile(FilePath):
    upload_dir = UPLOAD_DIR
    upload_dir.mkdir(parents=True, exist_ok=True)

    zip_path = Path(FilePath)
    extract_dir = upload_dir / zip_path.stem
    if extract_dir.exists():
        shutil.rmtree(extract_dir)
    extract_dir.mkdir(parents=True, exist_ok=True)

    with zipfile.ZipFile(zip_path, "r") as zipref:
        zipref.extractall(extract_dir)


def MessagesCountList():
    global _CACHED_MESSAGE_COUNTS
    if _CACHED_MESSAGE_COUNTS is not None:
        return _CACHED_MESSAGE_COUNTS

    user_message_count = defaultdict(int)
    for message in GetChatMessages():
        user = message["user"]
        if user != "Meta AI":
            user_message_count[user] += 1

    _CACHED_MESSAGE_COUNTS = user_message_count
    return _CACHED_MESSAGE_COUNTS