import requests
import json
import time
import os
from dotenv import load_dotenv

load_dotenv()

url = os.getenv("VERIFY_API_URL")
if not url:
    raise RuntimeError("VERIFY_API_URL must be configured in backend/.env")

# Create a dummy file
with open("test_audio.wav", "wb") as f:
    # Just some random bytes, ffmpeg might fail but we check if API handles it 
    # Or ideally we write a valid wav header... let's try to be minimal
    # A valid WAV header is 44 bytes.
    # RIFF....WAVEfmt ........data....
    # Hex representation of a minimal valid wav file with silence
    header = bytes.fromhex('524946462400000057415645666d7420100000000100010044ac000088580100020010006461746100000000')
    f.write(header)

files = [
    ('files', ('test_video_1.webm', open('test_audio.wav', 'rb'), 'video/webm')),
    ('files', ('test_video_2.webm', open('test_audio.wav', 'rb'), 'video/webm'))
]

metadata = {
    "questions": [
        "What is your experience effectively?",
        "How do you handle conflict?"
    ],
    "rubrics": [
        "Score 4 if they show good experience.",
        "Score 4 if they resolve conflict peacefully."
    ]
}

data = {
    "metadata": json.dumps(metadata)
}

print("Sleeping 5s to ensure server is up...")
time.sleep(5)

try:
    print("Sending request...")
    response = requests.post(url, files=files, data=data)
    print(f"Status Code: {response.status_code}")
    print("Response JSON:")
    print(json.dumps(response.json(), indent=2))
except Exception as e:
    print(f"Request failed: {e}")
