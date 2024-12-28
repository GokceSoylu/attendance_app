import face_recognition
import cv2
import os

def load_known_faces_and_names(known_faces_dir):
    known_encodings = []
    known_names = []
    for file_name in os.listdir(known_faces_dir):
        if file_name.endswith((".jpg", ".png", ".jpeg")):
            image = face_recognition.load_image_file(os.path.join(known_faces_dir, file_name))
            encoding = face_recognition.face_encodings(image)
            if encoding:
                known_encodings.append(encoding[0])
                known_names.append(os.path.splitext(file_name)[0])
    return known_encodings, known_names

def process_image(image_path, known_faces_dir):
    known_encodings, known_names = load_known_faces_and_names(known_faces_dir)

    image = cv2.imread(image_path)
    rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    face_locations = face_recognition.face_locations(rgb_image)
    face_encodings = face_recognition.face_encodings(rgb_image, face_locations)

    results = {"present": [], "unknown": []}
    for face_encoding in face_encodings:
        matches = face_recognition.compare_faces(known_encodings, face_encoding)
        if True in matches:
            matched_idx = matches.index(True)
            results["present"].append(known_names[matched_idx])
        else:
            results["unknown"].append("Unknown")
    return results
