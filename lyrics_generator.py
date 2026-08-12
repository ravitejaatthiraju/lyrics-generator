import os
import sys
import time
import pygame
from faster_whisper import WhisperModel


# ============================================================
# SONG PATH
# ============================================================

SONG_PATH = r"Aint Nobody - Masstamilan.MY.mp3"


# ============================================================
# SETTINGS
# ============================================================

MODEL_SIZE = "base"

# Use None for automatic language detection.
# If your song is definitely English, change to "en".
LANGUAGE = None


# ============================================================
# CHECK FILE
# ============================================================

if not os.path.exists(SONG_PATH):
    print("❌ Song file not found!")
    print(f"Path: {SONG_PATH}")
    sys.exit()


# ============================================================
# LOAD WHISPER
# ============================================================

print("🎵 Loading Whisper model...")

model = WhisperModel(
    MODEL_SIZE,
    device="cpu",
    compute_type="int8"
)

print("✅ Whisper model loaded.")
print("🎤 Analyzing song...")
print("Please wait...\n")


# ============================================================
# TRANSCRIBE SONG
# ============================================================
#
# IMPORTANT:
# We intentionally DO NOT use vad_filter=True.
# VAD is designed for normal speech and can remove singing.
#
# ============================================================

segments, info = model.transcribe(
    SONG_PATH,
    language=LANGUAGE,
    beam_size=5,
    word_timestamps=True,
    vad_filter=False,
    condition_on_previous_text=True
)


# Convert generator to list
segments = list(segments)


# ============================================================
# EXTRACT WORD TIMESTAMPS
# ============================================================

words = []

for segment in segments:

    if segment.words is None:
        continue

    for word in segment.words:

        text = word.word.strip()

        if text:

            words.append({
                "text": text,
                "start": word.start,
                "end": word.end
            })


# ============================================================
# CHECK TRANSCRIPTION
# ============================================================

print(f"✅ Detected {len(words)} words.")

if len(words) == 0:
    print("\n❌ No lyrics were detected.")
    print("Try changing MODEL_SIZE from 'base' to 'small'.")
    sys.exit()


# ============================================================
# INITIALIZE AUDIO PLAYER
# ============================================================

pygame.mixer.init()

pygame.mixer.music.load(SONG_PATH)


# ============================================================
# TERMINAL DISPLAY
# ============================================================

def clear_line():
    """
    Clears the current terminal line.
    """
    sys.stdout.write("\r" + " " * 120 + "\r")


def show_lyrics(current_time):

    # Find current word
    current_index = -1

    for i, word in enumerate(words):

        if word["start"] <= current_time:
            current_index = i
        else:
            break

    if current_index == -1:
        return

    # --------------------------------------------------------
    # Show approximately 8 words around current position
    # --------------------------------------------------------

    start_index = max(0, current_index - 4)

    end_index = min(
        len(words),
        start_index + 9
    )

    visible_words = words[start_index:end_index]

    output = ""

    for i, word in enumerate(visible_words):

        actual_index = start_index + i

        if actual_index == current_index:

            # Highlight current word
            output += f"  >>> {word['text'].upper()} <<<"

        else:

            output += f" {word['text']}"

    clear_line()

    sys.stdout.write(output)
    sys.stdout.flush()


# ============================================================
# START SONG
# ============================================================

print("\n" + "=" * 100)
print("                         🎵 NOW PLAYING")
print("=" * 100)

print("\n▶ Song started...\n")


pygame.mixer.music.play()


# ============================================================
# SYNCHRONIZE LYRICS WITH SONG
# ============================================================

while pygame.mixer.music.get_busy():

    # Current playback position in seconds
    current_time = pygame.mixer.music.get_pos() / 1000.0

    show_lyrics(current_time)

    # Update approximately 30 times per second
    time.sleep(0.03)


# ============================================================
# FINISHED
# ============================================================

clear_line()

print("\n\n" + "=" * 100)
print("                         ✅ SONG FINISHED")
print("=" * 100)

pygame.mixer.quit()