import face_recognition
import cv2
import numpy as np
import pickle
from imutils import paths
import os
from paho_mqtt import Publisher
from dataset import Dataset
import json

class Recognizer:
    def __init__(self,publisher:Publisher,dataset:Dataset,led=None):
        super().__init__()
        if led:
            from led_controller import Led_controller
            self.LED = True
            self.led = led
        else:
            self.LED = False
        self.publisher = publisher
        self.dataset= dataset
        self.topic_detection = "{}".format(f"/v2.0/devices/camera-detection/detections")
        self.topic_user = "{}".format(f"/v2.0/devices/camera-detection/users")
        p = os.getcwd()
        if 'src' in p:
            p.removesuffix(str)
        p = os.path.join(p,"encodings.pickle")
        print("[INFO] loading encodings...")
        with open(p, "rb") as f:
            data = pickle.loads(f.read())
        self.known_face_encodings = data["encodings"]
        self.known_face_names = data["names"]
        self.cv_scaler = 4
        self.face_locations = []
        self.face_encodings = []
        self.face_names:list[str] = []

    def train_model(self):
        imagePaths = list(paths.list_images("dataset"))
        knownEncodings = []
        knownNames = []

        for (i, imagePath) in enumerate(imagePaths):
            name = imagePath.split(os.path.sep)[-2]
            image = cv2.imread(imagePath)
            rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            boxes = face_recognition.face_locations(rgb, model="hog")
            encodings = face_recognition.face_encodings(rgb, boxes)

            for encoding in encodings:
                knownEncodings.append(encoding)
                knownNames.append(name)

        data = {"encodings": knownEncodings, "names": knownNames}
        with open("encodings.pickle", "wb") as f:
            f.write(pickle.dumps(data))
        self.known_face_names=knownNames
        self.known_face_encodings=knownEncodings

    def analyse(self,frame):
        frame_l = self.process_frame(frame)
        frame_d = self.draw_results(frame_l)
        return frame_d
    
    def verifica_rosto(self,nome):
        nomes_permitidos = self.dataset.data['users'].__contains__(nome)
        return nomes_permitidos
    
    def process_frame(self,l_frame):
        # Resize the frame using cv_scaler to increase performance (less pixels processed, less time spent)
        resized_frame = cv2.resize(l_frame, (0, 0), fx=(1/self.cv_scaler), fy=(1/self.cv_scaler))
        
        # Convert the image from BGR to RGB colour space, the facial recognition library uses RGB, OpenCV uses BGR
        rgb_resized_frame = cv2.cvtColor(resized_frame, cv2.COLOR_BGR2RGB)
        
        # Find all the faces and face encodings in the current frame of video
        self.face_locations = face_recognition.face_locations(rgb_resized_frame, model = "hog")
        #print(face_locations)
        self.face_encodings = face_recognition.face_encodings(rgb_resized_frame, self.face_locations, model='small')

        self.face_names = []
        rosto_autorizado = False
        
        for face_encoding in self.face_encodings:

            # See if the face is a match for the known face(s)
            matches = face_recognition.compare_faces(self.known_face_encodings, face_encoding)
            name = "Unknown"
            
            # Use the known face with the smallest distance to the new face
            face_distances = face_recognition.face_distance(self.known_face_encodings, face_encoding)
            best_match_index = np.argmin(face_distances)
            if matches[best_match_index]:
                name = self.known_face_names[best_match_index]
            self.face_names.append(name)
        
            rosto_autorizado = self.verifica_rosto(name)

        
        if rosto_autorizado:
            if self.LED:
                self.led.green()
        else:
            if self.LED:
                self.led.red()


        for name in self.face_names:
            if name == "Unknown":
                payload = json.dumps({"value": -1,"context":{"type":"desconhecido"}})
                self.publisher.publish(topic=self.topic_detection,payload=payload)
            else:
                payload_detection = json.dumps({"value": 1,"context":{"type":"conhecido"}})
                payload_user = json.dumps({"value": name,"context":{"id":name,"name":self.dataset.data['users'][name]}})
                self.publisher.publish(topic=self.topic_detection,payload=payload_detection)
                self.publisher.publish(topic=self.topic_user,payload=payload_user)

        return l_frame
    
    def draw_results(self,l_frame):
        # Display the results
        for (top, right, bottom, left), name in zip(self.face_locations, self.face_names):
            # Scale back up face locations since the frame we detected in was scaled
            top *= self.cv_scaler
            right *= self.cv_scaler
            bottom *= self.cv_scaler
            left *= self.cv_scaler
            
            # Draw a box aroeund the face
            cv2.rectangle(l_frame, (left, top), (right, bottom), (244, 42, 3), 3)
            
            # Draw a label with a name below the face
            cv2.rectangle(l_frame, (left -3, top - 35), (right+3, top), (244, 42, 3), cv2.FILLED)
            font = cv2.FONT_HERSHEY_DUPLEX
            cv2.putText(l_frame, name, (left + 6, top - 6), font, 1.0, (255, 255, 255), 1)
        
        return l_frame