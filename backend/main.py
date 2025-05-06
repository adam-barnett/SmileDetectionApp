from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import threading
import base64
import cv2

app = FastAPI()

# need to use cors to give frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


image_data = []  # Stores latest frame (in base 64)

def primary_backend_loop():
    cap = cv2.VideoCapture(0)  # 0 = default camera

    if not cap.isOpened():
        print("Could not open webcam.")
        return

    while True:
        ret, frame = cap.read()
        if not ret:
            continue

        ret, jpeg = cv2.imencode('.jpg', frame)
        if ret:
            # storing the frame in base 64 was necessary to get it from Python to react
            b64 = base64.b64encode(jpeg.tobytes()).decode('utf-8')
            image_data.clear()
            image_data.append(f"data:image/jpeg;base64,{b64}")
    cap.release()

""" note this is a deprecated method, kept for now, hopefully will have time to replace it
correct thing to use is lifespan events, though there may also be some logic to shifting the code in
 this file over to a class and using __init__ and __del__"""
@app.on_event("startup")
def start_backend_thread():
    thread = threading.Thread(target=primary_backend_loop, daemon=True)
    thread.start()

@app.get("/images")
def get_current_image():
    # future work: might be worth using a lock on this data here and above where it is accessed
    return JSONResponse(content=image_data.copy())
