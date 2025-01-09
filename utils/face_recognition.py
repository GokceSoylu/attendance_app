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
            image_path = os.path.join(known_faces_path, file_name)
            image = face_recognition.load_image_file(image_path)
            encoding = face_recognition.face_encodings(image)
            if encoding:  # Eğer yüz bulunmuşsa
                known_encodings.append(encoding[0])  # İlk yüzü alıyoruz
                known_names.append(os.path.splitext(file_name)[0])  # Dosya adı isim olarak kullanılır
    return known_encodings, known_names


# 2. Yoklama kaydı
def mark_attendance(name, attendance_file_path, attendance_list):
    if name not in attendance_list:
        try:
            with open(attendance_file_path, "a") as file:
                now = datetime.now()
                dt_string = now.strftime("%Y-%m-%d %H:%M:%S")
                file.write(f"{name},{dt_string}\n")
            attendance_list.add(name)
            print(f"Yoklama kaydedildi: {name}")
        except Exception as e:
            print(f"Yoklama kaydı sırasında hata oluştu: {e}")


# Görüntüyü yeniden boyutlandırma
def resize_image(image, scale=1.5):
    width = int(image.shape[1] * scale)
    height = int(image.shape[0] * scale)
    return cv2.resize(image, (width, height))


def main():
    # Klasör ve dosya yolları
    base_path = "/Users/gokcesoylu/AttendanceSystem"
    known_faces_path = os.path.join(base_path, "known_faces")
    test_image_path = os.path.join(base_path, "test_images/class2.jpeg")
    attendance_file_path = os.path.join(base_path, "class_attendance.csv")

    # Yüz bilgilerini yükleme
    known_encodings, known_names = load_known_faces_and_names(known_faces_path)
    print(f"{len(known_encodings)} yüz bilgisi yüklendi.")

    # Test görüntüsünü yükleme ve işleme
    test_image = cv2.imread(test_image_path)
    resized_image = resize_image(test_image, scale=1.5)
    rgb_test_image = cv2.cvtColor(resized_image, cv2.COLOR_BGR2RGB)

    # Yoklama listesi
    attendance_list = set()

    # Görüntüdeki yüzleri algılama
    face_locations = face_recognition.face_locations(rgb_test_image, model="cnn")
    face_encodings = face_recognition.face_encodings(rgb_test_image, face_locations)

    print(f"{len(face_locations)} yüz algılandı.")

    # Yüz tanıma işlemi
    for face_encoding, face_location in zip(face_encodings, face_locations):
        matches = face_recognition.compare_faces(known_encodings, face_encoding)
        face_distances = face_recognition.face_distance(known_encodings, face_encoding)
        name = "Bilinmeyen"

        if len(face_distances) > 0:
            best_match_index = np.argmin(face_distances)
            if matches[best_match_index]:
                name = known_names[best_match_index]

        # Yoklama listesine ekleme
        if name != "Bilinmeyen":
            mark_attendance(name, attendance_file_path, attendance_list)

    #     # Yüzlerin üzerine etiket ekleme
    #     top, right, bottom, left = [int(coord / 1.5) for coord in face_location]
    #     color = (0, 255, 0) if name != "Bilinmeyen" else (0, 0, 255)
    #     cv2.rectangle(test_image, (left, top), (right, bottom), color, 2)
    #     cv2.putText(test_image, name, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)

    # # İşlenmiş görüntüyü gösterme
    # test_image_bgr = cv2.cvtColor(test_image, cv2.COLOR_BGR2RGB)
    # plt.imshow(test_image_bgr)
    # plt.axis("off")
    # plt.show()


if __name__ == "__main__":
    main()
