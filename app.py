import sqlite3
import cv2
import face_recognition
from flask import Flask, render_template, request, redirect, jsonify, url_for
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

from flask import session

@app.route("/upload", methods=["POST"])
def upload_image():
    if "image" in request.files:
        file = request.files["image"]
        file_path = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(file_path)

        # Resmi işleyip sonuçları al
        results = process_image(file_path)

        # Sonuçları oturuma kaydet
        session["results"] = results

        return render_template("result.html", results=results)  # Şablona sonuçları gönder

    return redirect(url_for("index"))


@app.route("/result", methods=["GET"])
def show_result():
    # Örneğin, sonuçları bir oturumda (session) saklayabilirsiniz
    from flask import session
    results = session.get("results", None)

    if results:
        return render_template("result.html", results=results)
    else:
        return redirect(url_for("index"))


def get_student(student_id):
    connection = sqlite3.connect("data/students.db")
    connection.row_factory = sqlite3.Row  # Sözlük benzeri sonuç döndür
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM students WHERE id=?", (student_id,))
    student = cursor.fetchone()  # Artık sözlük gibi erişilebilir
    connection.close()
    return student

@app.route("/update-attendance/<int:student_id>/<action>", methods=["POST"])
def update_attendance(student_id, action):
    try:
        if action == "mark-absent":
            mark_attendance(student_id, status="absent")
        elif action == "mark-present":
            mark_attendance(student_id, status="present")
        else:
            return jsonify({"status": "error", "message": "Geçersiz işlem."}), 400

        # Güncel durumu döndür
        updated_status = "absent" if action == "mark-absent" else "present"
        return jsonify({"status": "success", "message": "Durum güncellendi.", "updated_status": updated_status})

    except Exception as e:
        print(f"Veritabanı hatası: {e}")
        return jsonify({"status": "error", "message": "Bir hata oluştu."}), 500



@app.route("/student/<int:student_id>")
def student_detail(student_id):
    student = get_student(student_id)
    if not student:
        return "Öğrenci bulunamadı", 404
    return render_template("student_detail.html", student=student)

@app.route("/student/absent/<int:student_id>")
def student_detail_absent(student_id):
    student = get_student(student_id)
    if not student:
        return "Öğrenci bulunamadı", 404
    return render_template("student_detail_absent.html", student=student)



def check_attendance_status(student_id):
    """Öğrencinin yoklama durumunu kontrol eder."""
    connection = sqlite3.connect("data/students.db")
    cursor = connection.cursor()
    cursor.execute("SELECT status FROM attendance WHERE student_id = ?", (student_id,))
    result = cursor.fetchone()
    connection.close()

    if result and result[0] == "absent":
        return "absent"
    return "present"


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

        add_student(name, student_number, file_path)
        return redirect(url_for("index"))
    return render_template("add_student.html")

def get_all_students():
    connection = sqlite3.connect("data/students.db")
    connection.row_factory = sqlite3.Row  # Sözlük benzeri sonuç döndür
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM students")
    students = cursor.fetchall()
    connection.close()
    return students


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

            # Yoklama tablosuna "present" durumu ekle
            mark_attendance(known_students[matched_idx]['id'], status="present")

    # Veritabanındaki tüm öğrencileri alın
    all_students = get_all_students()

    # Sınıfta olmayanları belirle ve yoklama tablosuna "absent" durumu ekle
    results["absent"] = []
    for student in all_students:
        if student["id"] not in present_ids:
            results["absent"].append(student)
            mark_attendance(student["id"], status="absent")

    return results


def load_known_faces_and_names():
    connection = sqlite3.connect("data/students.db")
    connection.row_factory = sqlite3.Row  # Sözlük benzeri sonuç döndür
    cursor = connection.cursor()
    cursor.execute("SELECT id, name, image_path FROM students")
    students = cursor.fetchall()  # Artık sözlük gibi erişilebilir
    connection.close()

    known_encodings = []
    known_students = []

    for student in students:
        student_id = student['id']
        name = student['name']
        image_path = student['image_path']
        image = face_recognition.load_image_file(image_path)
        encoding = face_recognition.face_encodings(image)
        if encoding:
            known_encodings.append(encoding[0])
            known_students.append({"id": student_id, "name": name, "image_path": image_path})

    return known_encodings, known_students


if __name__ == "__main__":
    app.run(debug=True)
