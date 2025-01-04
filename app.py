import sqlite3
import cv2
import face_recognition
from flask import Flask, render_template, request, redirect, jsonify, url_for, session
from flask_cors import CORS
import os
import json

# Flask uygulaması tanımı
app = Flask(__name__)
CORS(app)
app.secret_key = "bu-cok-gizli-bir-anahtardir"

UPLOAD_FOLDER = "static/images/uploads"
KNOWN_FACES_DIR = "static/images/known_faces"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(KNOWN_FACES_DIR, exist_ok=True)

# JSON dönüştürme için özel bir fonksiyon
def custom_json_converter(obj):
    if isinstance(obj, sqlite3.Row):
        return dict(obj)
    raise TypeError("Type not serializable")

# Veritabanı bağlantı fonksiyonu
def get_db_connection():
    connection = sqlite3.connect("data/students.db")
    connection.row_factory = sqlite3.Row
    return connection

# Veritabanından öğrenci bilgilerini getirme fonksiyonu
def get_student(student_id):
    with get_db_connection() as connection:
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM students WHERE id = ?", (student_id,))
        row = cursor.fetchone()
        return dict(row) if row else None

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/upload", methods=["POST"])
def upload_image():
    if "image" in request.files:
        file = request.files["image"]
        file_path = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(file_path)

        results = process_image(file_path)
        session["results"] = json.dumps(results, default=custom_json_converter)

        return redirect(url_for("show_result"))

    return redirect(url_for("index"))

@app.route("/show_result")
def show_result():
    results = session.get("results")
    if results:
        results = json.loads(results)
    return render_template("result.html", results=results)

@app.route("/student/<int:student_id>")
def student_detail(student_id):
    student = get_student(student_id)
    if not student:
        return jsonify({"status": "error", "message": "\u00d6\u011frenci bulunamad\u0131"}), 404

    return render_template("student_detail.html", student=student)

@app.route("/student/<int:student_id>/json")
def student_detail_json(student_id):
    student = get_student(student_id)
    if not student:
        return jsonify({"status": "error", "message": "\u00d6\u011frenci bulunamad\u0131"}), 404

    return jsonify({"status": "success", "student": student})

@app.route("/add-student", methods=["GET", "POST"])
def add_student_page():
    if request.method == "POST":
        name = request.form["name"]
        student_number = request.form["student_number"]
        file = request.files["image"]

        if not file or not file.filename.lower().endswith((".jpg", ".jpeg", ".png")):
            return render_template("add_student.html", error="Ge\u00e7erli bir resim dosyas\u0131 y\u00fckleyin.")

        file_path = os.path.join(KNOWN_FACES_DIR, f"{name}.jpg")
        file.save(file_path)

        with get_db_connection() as connection:
            cursor = connection.cursor()
            cursor.execute("INSERT INTO students (name, student_number, image_path) VALUES (?, ?, ?)", (name, student_number, file_path))
            connection.commit()

        return redirect(url_for("index"))
    return render_template("add_student.html")

@app.route("/update-attendance/<int:student_id>/<action>", methods=["POST"])
def update_attendance(student_id, action):
    new_status = "present" if action == "mark-present" else "absent" if action == "mark-absent" else None
    if not new_status:
        return jsonify({"status": "error", "message": "Ge\u00e7ersiz i\u015flem"}), 400

    with get_db_connection() as connection:
        cursor = connection.cursor()
        cursor.execute("INSERT OR REPLACE INTO attendance (student_id, status) VALUES (?, ?)", (student_id, new_status))
        connection.commit()

    return jsonify({"status": "success", "updated_status": new_status})

def process_image(image_path):
    known_encodings, known_students = load_known_faces_and_names()
    test_image = cv2.imread(image_path)
    rgb_image = cv2.cvtColor(test_image, cv2.COLOR_BGR2RGB)

    face_locations = face_recognition.face_locations(rgb_image)
    face_encodings = face_recognition.face_encodings(rgb_image, face_locations)

    results = {"present": [], "absent": []}
    present_ids = []

    for face_encoding in face_encodings:
        matches = face_recognition.compare_faces(known_encodings, face_encoding)
        if True in matches:
            matched_idx = matches.index(True)
            present_ids.append(known_students[matched_idx]['id'])
            results["present"].append(known_students[matched_idx])

            with get_db_connection() as connection:
                cursor = connection.cursor()
                cursor.execute("INSERT OR REPLACE INTO attendance (student_id, status) VALUES (?, ?)", (known_students[matched_idx]['id'], "present"))
                connection.commit()

    with get_db_connection() as connection:
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM students")
        all_students = cursor.fetchall()

    for student in all_students:
        if student["id"] not in present_ids:
            results["absent"].append(student)
            with get_db_connection() as connection:
                cursor = connection.cursor()
                cursor.execute("INSERT OR REPLACE INTO attendance (student_id, status) VALUES (?, ?)", (student["id"], "absent"))
                connection.commit()

    return results

def load_known_faces_and_names():
    with get_db_connection() as connection:
        cursor = connection.cursor()
        cursor.execute("SELECT id, name, image_path FROM students")
        students = cursor.fetchall()

    known_encodings = []
    known_students = []

    for student in students:
        image = face_recognition.load_image_file(student['image_path'])
        encoding = face_recognition.face_encodings(image)
        if encoding:
            known_encodings.append(encoding[0])
            known_students.append({"id": student['id'], "name": student['name'], "image_path": student['image_path']})

    return known_encodings, known_students

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5001)
