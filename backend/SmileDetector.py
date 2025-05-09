import base64
from LocalDBConnection import LocalDBConnection
import time
import copy
import cv2
import threading

class SmileDetector:

    # two colorblind friendly colors
    smiles_color = (213, 94, 0)
    faces_color = (34, 113, 178)
    # Future work: it sets of alarm bells that I have so many essentially global variables existing, likely solution is to
    # move this entire file within a single class
    image_data = {'image': '',
                  'coordinates': ''}  # Stores latest frame (in base 64 as a json string ready to display in react,
    # and the coordinates of the last detected smile
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    smile_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_smile.xml')
    currently_capturing = False

    def __init__(self):
        self.db_connection = LocalDBConnection()
        self.stop_event = threading.Event()

    def close(self):
        self.stop_event.set()
        self.db_connection.close()

    def start_detection_thread(self, testing_locally=False):
        self.stop_event.clear()
        thread = threading.Thread(target=self.primary_detection_thread, daemon=True, args=[testing_locally])
        thread.start()

    def stop_detection_thread(self):
        self.stop_event.set()

    def primary_detection_thread(self, display):
        self.currently_capturing = True
        cap = cv2.VideoCapture(
            0)  # 0 = default camera (future work: check available cameras and offer options to frontend)

        if not cap.isOpened():
            print("Could not open webcam.")
            self.currently_capturing = False
            return

        while True:
            ret, frame = cap.read()
            if not ret:
                continue
            # detecting then adding the faces and smiles
            [faces, smiles] = self.find_faces_and_smiles(frame)
            bounded_image = copy.copy(frame)
            self.add_boxes_to_image(bounded_image, faces, self.faces_color)
            self.add_boxes_to_image(bounded_image, smiles, self.smiles_color)
            if display:
                cv2.imshow('testing_backend', bounded_image)
                if cv2.waitKey(1) == 32:  # space bar
                    break
            ret, jpeg = cv2.imencode('.jpg', bounded_image)
            if ret:
                # storing the frame in base 64 was necessary to get it from Python to react
                b64 = base64.b64encode(jpeg.tobytes()).decode('utf-8')
                self.image_data['image'] = f'data:image/jpeg;base64,{b64}'
                current_coordinates = 'smiles found at - '
                for (x, y, w, h) in smiles:
                    current_coordinates = current_coordinates + f'x:{x}y:{y} '
                if len(smiles) == 0:
                    current_coordinates = 'no current smiles'
                self.image_data['coordinates'] = current_coordinates
                self.db_connection.add_smiles(smiles, frame)
            if self.stop_event.is_set():
                break
            time.sleep(0.03)
        cap.release()
        cv2.destroyAllWindows()
        self.currently_capturing = False

    def find_faces_and_smiles(self, frame):
        grayscale_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        equalized_frame = cv2.equalizeHist(grayscale_frame)
        faces = self.face_cascade.detectMultiScale(equalized_frame, 1.25, 5)
        full_smiles = []
        for (x, y, w, h) in faces:
            grayscale_face = grayscale_frame[y:y + h, x:x + w]
            local_smiles = self.smile_cascade.detectMultiScale(grayscale_face, 1.8, 20)
            for (x_smile, y_smile, w_smile, h_smile) in local_smiles:
                full_smiles.append((x_smile + x, y_smile + y, w_smile, h_smile))
        return faces, tuple(full_smiles)

    def add_boxes_to_image(self, image, boxes, color):
        for (x, y, w, h) in boxes:
            cv2.rectangle(image, (x, y), ((x + w), (y + h)), color, 2)
        return image