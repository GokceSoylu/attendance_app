import cv2
import face_recognition
import numpy as np
import os
import matplotlib.pyplot as plt
from datetime import datetime

# 1. Öğrencilerin yüz bilgilerini yükleme
def load_known_faces_and_names(known_faces_path):
    known_encodings = []
    known_names = []
    for file_name in os.listdir(known_faces_path):
        if file_name.endswith((".jpg", ".png", ".jpeg", ".webp")):
            image = face_recognition.load_image_file(f"{known_faces_path}/{file_name}")
            encoding = face_recognition.face_encodings(image)
            if encoding:  # Eğer yüz bulunmuşsa
                known_encodings.append(encoding[0])  # İlk yüzü alıyoruz
                known_names.append(os.path.splitext(file_name)[0])  # Dosya adı isim olarak kullanılır
    return known_encodings, known_names

# 2. Yoklama kaydı
def mark_attendance(name, attendance_list):
    if name not in attendance_list:
        with open("/Users/gokcesoylu/AttendanceSystem/class_attendance.csv", "a") as file:
            now = datetime.now()
            dt_string = now.strftime("%Y-%m-%d %H:%M:%S")
            file.write(f"{name},{dt_string}\n")
        attendance_list[name] = True
        print(f"Yoklama kaydedildi: {name}")

# Görüntüyü yeniden boyutlandırma (büyütmek için kullanılıyor)
def resize_image(image, scale=1.5):
    width = int(image.shape[1] * scale)
    height = int(image.shape[0] * scale)
    return cv2.resize(image, (width, height))

# Histogram eşitleme (görüntü netliğini artırır)
def enhance_image(image):
    image_yuv = cv2.cvtColor(image, cv2.COLOR_BGR2YUV)
    image_yuv[:, :, 0] = cv2.equalizeHist(image_yuv[:, :, 0])
    return cv2.cvtColor(image_yuv, cv2.COLOR_YUV2BGR)

def main():
    known_faces_path = "/Users/gokcesoylu/AttendanceSystem/known_faces"
    known_encodings, known_names = load_known_faces_and_names(known_faces_path)

    test_image_path = "/Users/gokcesoylu/AttendanceSystem/test_images/class2.jpeg"
    test_image = cv2.imread(test_image_path)

    # Görüntüyü büyüt ve netliğini artır
    enhanced_image = enhance_image(test_image)
    resized_test_image = resize_image(enhanced_image, scale=1.5)
    rgb_test_image = cv2.cvtColor(resized_test_image, cv2.COLOR_BGR2RGB)

    # Yoklama listesi
    attendance_list = {}

    # Görüntüdeki yüzleri tanıma
    face_locations = face_recognition.face_locations(rgb_test_image, model="cnn")  # CNN modeli ile algılama
    face_encodings = face_recognition.face_encodings(rgb_test_image, face_locations)

    # Tanınan yüz bilgilerini takip etmek için sözlük
    detected_faces = {}

    # Yüz tanıma işlemi
    for face_encoding, face_location in zip(face_encodings, face_locations):
        matches = face_recognition.compare_faces(known_encodings, face_encoding)
        face_distances = face_recognition.face_distance(known_encodings, face_encoding)
        name = "X"

        if len(face_distances) > 0:
            best_match_index = np.argmin(face_distances)
            if matches[best_match_index]:
                name = known_names[best_match_index]

        # Eğer kişi daha önce tespit edildiyse:
        if name in detected_faces:
            # Yeni tespit daha düşük mesafeli (daha iyi eşleşen) ise, eski tespiti "X" olarak değiştir
            previous_distance, _ = detected_faces[name]
            if face_distances[best_match_index] < previous_distance:
                detected_faces[name] = (face_distances[best_match_index], face_location)
            else:
                name = "X"  # Yeni tespit daha kötü eşleşiyorsa "X" olarak işaretle
        else:
            # Yeni kişiyi kaydet
            detected_faces[name] = (face_distances[best_match_index], face_location)

        # Yoklama listesine ekleme
        if name != "X" and name not in attendance_list:
            mark_attendance(name, attendance_list)
        elif name == "X" and name not in attendance_list:
            # Tanınmayan kişiyi kaydet
            mark_attendance(name, attendance_list)
            print(f"Tanınmayan yüz kaydedildi: X")

        # Tanınan yüzlerin üzerine etiket ekleme
        (top, right, bottom, left) = [int(coord / 1.5) for coord in face_location]  # Koordinatları eski boyuta uyarla
        color = (0, 255, 0) if name != "X" else (0, 0, 255)  # Tanınanlar yeşil, tanınmayanlar kırmızı
        cv2.rectangle(test_image, (left, top), (right, bottom), color, 2)
        cv2.putText(test_image, name, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)

    # Test görüntüsünü gösterme
    test_image_bgr = cv2.cvtColor(test_image, cv2.COLOR_BGR2RGB)
    plt.imshow(test_image_bgr)
    plt.axis("off")
    plt.show()

if __name__ == "__main__":
    main()
