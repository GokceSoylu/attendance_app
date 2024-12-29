import sqlite3
import cv2
import face_recognition
from flask import Flask, render_template, request, redirect, jsonify, url_for
from utils.face_recognition import process_image, load_known_faces_and_names
from utils.db_utils import get_all_students, get_student, add_student, mark_attendance, get_attendance_history
import os
from datetime import datetime

app = Flask(__name__)

UPLOAD_FOLDER = "static/images/uploads"
KNOWN_FACES_DIR = "static/images/known_faces"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/upload", methods=["POST"])
def upload_image():
    if "image" in request.files:
        file = request.files["image"]
        file_path = os.path.join("static/images/uploads", file.filename)
        file.save(file_path)

        # Resmi işleyip sonuçları al
        results = process_image(file_path)
        return render_template("result.html", results=results)  # Şablona sonuçları gönder

    return redirect(url_for("index"))


@app.route("/student/<int:student_id>")
def student_detail(student_id):
    from utils.db_utils import get_student
    student = get_student(student_id)
    if not student:
        return "Öğrenci bulunamadı", 404
    return render_template("student_detail.html", student=student)


@app.route("/add-student", methods=["GET", "POST"])
def add_student_page():
    if request.method == "POST":
        name = request.form["name"]
        student_number = request.form["student_number"]
        file = request.files["image"]

        if not file or not file.filename.lower().endswith((".jpg", ".jpeg", ".png")):
            return render_template("add_student.html", error="Geçerli bir resim dosyası yükleyin.")

        file_path = os.path.join(KNOWN_FACES_DIR, f"{name}.jpg")
        file.save(file_path)

        if add_student(name, student_number, file_path):
            return redirect(url_for("index"))
        return render_template("add_student.html", error="Öğrenci eklenirken hata oluştu.")
    return render_template("add_student.html")

def process_image(image_path):
    known_encodings, known_students = load_known_faces_and_names()
    test_image = cv2.imread(image_path)
    rgb_image = cv2.cvtColor(test_image, cv2.COLOR_BGR2RGB)

    face_locations = face_recognition.face_locations(rgb_image)
    face_encodings = face_recognition.face_encodings(rgb_image, face_locations)

    results = {"present": [], "absent": []}
    present_ids = []

    # Yüz tanıma işlemi
    for face_encoding in face_encodings:
        matches = face_recognition.compare_faces(known_encodings, face_encoding)
        if True in matches:
            matched_idx = matches.index(True)
            present_ids.append(known_students[matched_idx]['id'])
            results["present"].append(known_students[matched_idx])

    # Veritabanındaki tüm öğrencileri alın
    all_students = get_all_students()

    # Sınıfta olmayanları belirle
    results["absent"] = [student for student in all_students if student["id"] not in present_ids]

    return results
def load_known_faces_and_names():
    connection = sqlite3.connect("data/students.db")
    cursor = connection.cursor()
    cursor.execute("SELECT id, name, image_path FROM students")
    students = cursor.fetchall()
    connection.close()

    known_encodings = []
    known_students = []

    for student in students:
        student_id, name, image_path = student
        image = face_recognition.load_image_file(image_path)
        encoding = face_recognition.face_encodings(image)
        if encoding:
            known_encodings.append(encoding[0])
            known_students.append({"id": student_id, "name": name, "image_path": image_path})

    return known_encodings, known_students


if __name__ == "__main__":
    app.run(debug=True)
