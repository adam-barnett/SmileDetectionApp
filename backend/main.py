import base64
import threading
import time

import cv2
import keyboard
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from LocalDBConnection import LocalDBConnection

app = FastAPI()

# need to use cors to give frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Future work: it sets of alarm bells that I have so many essentially global variables existing, likely solution is to
    # move this entire file within a single class
image_data = {'image': '', 'coordinates': ''}  # Stores latest frame (in base 64 as a json string ready to display in react,
    # and the coordinates of the last detected smile
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades +'haarcascade_frontalface_default.xml')
smile_cascade = cv2.CascadeClassifier(cv2.data.haarcascades +'haarcascade_smile.xml')
stop_event = threading.Event()
currently_capturing = False
# two colorblind friendly colors
smiles_col = (213, 94, 0)
faces_col = (34, 113, 178)

def primary_backend_loop(display):
    global currently_capturing
    global image_data
    db_connection = LocalDBConnection()
    currently_capturing = True
    cap = cv2.VideoCapture(0)  # 0 = default camera (future work: check available cameras and offer options to frontend)

    if not cap.isOpened():
        print("Could not open webcam.")
        currently_capturing = False
        return

    while True:
        ret, frame = cap.read()
        if not ret:
            continue
        # detecting then adding the faces and smiles
        [faces, smiles] = find_faces_and_smiles(frame)
        faces_image = add_boxes_to_image(frame, faces, faces_col)
        smiles_image = add_boxes_to_image(faces_image, smiles, smiles_col)
        if display:
            cv2.imshow('testing_backend', smiles_image)
            if cv2.waitKey(1) == 32: #space bar
                break
        ret, jpeg = cv2.imencode('.jpg', smiles_image)
        if ret:
            # storing the frame in base 64 was necessary to get it from Python to react
            b64 = base64.b64encode(jpeg.tobytes()).decode('utf-8')
            image_data['image'] = f'data:image/jpeg;base64,{b64}'
            current_coordinates = 'smiles found at - '
            for (x, y, w, h) in smiles:
                current_coordinates = current_coordinates + f'x:{x}y:{y} '
            if len(smiles) == 0:
                current_coordinates = 'no current smiles'
            image_data['coordinates'] = current_coordinates
            db_connection.save_smile_data(smiles, frame)
        if stop_event.is_set():
            break
        time.sleep(0.03)
    cap.release()
    cv2.destroyAllWindows()
    currently_capturing = False

def start_backend_thread(testing_locally=False):
    thread = threading.Thread(target=primary_backend_loop, daemon=True, args=[testing_locally])
    thread.start()

@app.get("/image")
def get_current_image():
    # future work: might be worth using a lock on this data here and above where it is accessed
    return image_data

@app.post("/start_stop")
async def start_stop():
    print("start_stop called")
    if currently_capturing:
        if not stop_event.is_set():
            stop_event.set()
        # else we do nothing and just wait for it to end
        return {"state": "stopped"}
    else:
        stop_event.clear()
        start_backend_thread()
        return {"state": "running"}

""" notes of things to try in here:
- different input values to the different cascade detections
- the official documents recommend equalising the histogram of the image:
   equ = cv2.equalizeHist(img)
   but they are very old, test the usefulness of this
- do some verification and testing of the scale factor and minNeighbours input options"""
def find_faces_and_smiles(frame):
    grayscale_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(grayscale_frame, 1.3, 5)
    full_smiles = []
    for (x, y, w, h) in faces:
        grayscale_face = grayscale_frame[y:y + h, x:x + w]
        local_smiles = smile_cascade.detectMultiScale(grayscale_face, 1.8, 20)
        for (x_smile, y_smile, w_smile, h_smile) in local_smiles:
            full_smiles.append((x_smile + x, y_smile + y, w_smile, h_smile))
    return faces, tuple(full_smiles)

def add_boxes_to_image(image, boxes, color):
    for (x, y, w, h) in boxes:
        cv2.rectangle(image, (x, y), ((x + w), (y + h)), color, 2)
    return image

def local_testing():
    start_backend_thread(True)
    # Need to start primary backend loop (AND stop it when we exit)
    while True:
        if keyboard.read_key() == 'space':
            print('exiting')
            stop_event.set()
            break


if __name__ == "__main__":
    # then we are testing this with no frontend so we run it locally
    local_testing()