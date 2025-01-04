import sqlite3
import cv2
import face_recognition
from flask import Flask, render_template, request, redirect, jsonify, url_for
from utils.db_utils import get_all_students, get_student, add_student, mark_attendance, get_attendance_history
import os
from datetime import datetime
from flask import session
import json

from flask import Flask, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
app.secret_key = "bu-cok-gizli-bir-anahtardir" #ernflskjbnfrlkjsef çok komik


UPLOAD_FOLDER = "static/images/uploads"
KNOWN_FACES_DIR = "static/images/known_faces"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route("/")
def index():
    return render_template("index.html")

from flask import session

import json
import sqlite3

# JSON dönüştürme için özel bir fonksiyon
def custom_json_converter(obj):
    if isinstance(obj, sqlite3.Row):
        return dict(obj)  # Row nesnesini dict'e dönüştür
    # Diğer özel nesneler burada ele alınabilir
    raise TypeError("Type not serializable")

@app.route("/upload", methods=["POST"])
def upload_image():
    if "image" in request.files:
        file = request.files["image"]
        file_path = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(file_path)

        # Resmi işleyip sonuçları al
        results = process_image(file_path)

        # 'results' içindeki nesneleri JSON formatına dönüştür
        session["results"] = json.dumps(results, default=custom_json_converter)

        # Yönlendirme ile gösterim
        return redirect(url_for("show_result"))

    return redirect(url_for("index"))



@app.route('/show_result')
def show_result():
    results = session.get("results")
    if results:
        # JSON verisini tekrar bir python veri yapısına dönüştürme
        results = json.loads(results)
    return render_template("result.html", results=results)


def show_result():
    connection = sqlite3.connect("data/students.db")
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM students")
    rows = cursor.fetchall()
    connection.close()

    return [dict(row) for row in rows]


def get_student(student_id):
    connection = sqlite3.connect("data/students.db")
    connection.row_factory = sqlite3.Row  # Sözlük benzeri sonuç döndür
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM students WHERE id=?", (student_id,))
    row = cursor.fetchone()
    connection.close()

    return dict(row) if row else None

# @app.route('/update-attendance/<int:student_id>/<action>', methods=['POST'])
# def update_attendance(student_id, action):
#     try:
#         connection = sqlite3.connect("data/students.db")
#         cursor = connection.cursor()

#         # Geçerli işlem türünü belirleme
#         if action == "mark-present":
#             new_status = "present"
#         elif action == "mark-absent":
#             new_status = "absent"
#         else:
#             return jsonify({"status": "error", "message": "Geçersiz işlem"}), 400

#         # Attendance tablosuna güncelleme yapma
#         cursor.execute(
#             """
#             UPDATE attendance
#             SET status = ?
#             WHERE student_id = ?
#             """,
#             (new_status, student_id)
#         )

#         # Veritabanındaki değişikliklerin kaydedilmesi
#         connection.commit()

#         # Kontrol etmek için yapılan güncellemenin başarılı olup olmadığını kontrol etme
#         cursor.execute(
#             """
#             SELECT status FROM attendance WHERE student_id = ?
#             """, (student_id,)
#         )
#         updated_status = cursor.fetchone()

#         # Eğer güncellenmişse, sonucu döndür
#         if updated_status:
#             connection.close()
#             return jsonify({"status": "success", "updated_status": updated_status[0]})

#         connection.close()
#         return jsonify({"status": "error", "message": "Güncellenemedi."}), 500

#     except Exception as e:
#         connection.rollback()
#         connection.close()
#         return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/student/<int:student_id>")
def student_detail(student_id):
    student = get_student(student_id)
    if not student:
        return jsonify({"status": "error", "message": "Öğrenci bulunamadı"}), 404

    # HTML Şablonuna JSON verisi ile birlikte gönder
    return render_template("student_detail.html", student=student)

@app.route("/student/<int:student_id>/json")
def student_detail_json(student_id):
    student = get_student(student_id)
    if not student:
        return jsonify({"status": "error", "message": "Öğrenci bulunamadı"}), 404

    return jsonify({"status": "success", "student": student})


@app.route("/student/absent/<int:student_id>")
def student_detail_absent(student_id):
    student = get_student(student_id)
    if not student:
        return jsonify({"status": "error", "message": "Öğrenci bulunamadı"}), 404

    # HTML Şablonuna öğrenci verisini gönder
    return render_template("student_detail_absent.html", student=student)

@app.route("/student/absent/<int:student_id>/json")
def student_detail_absent_json(student_id):
    student = get_student(student_id)
    if not student:
        return jsonify({"status": "error", "message": "Öğrenci bulunamadı"}), 404

    return jsonify({"status": "success", "student": student})


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

    # Önceki `results` dictionary'sini session'a kaydet
    session["results"] = {
        "present": [dict(row) for row in results["present"]],
        "absent": [dict(row) for row in results["absent"]]
    }

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
