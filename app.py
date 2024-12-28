from flask import Flask, render_template, request, redirect, jsonify, url_for
from utils.face_recognition import process_image, load_known_faces_and_names
from utils.db_utils import get_student, add_student, mark_attendance, get_attendance_history
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
    if "image" not in request.files or not request.files["image"].filename:
        return render_template("index.html", error="Lütfen bir resim dosyası seçin.")

    file = request.files["image"]
    if not file.filename.lower().endswith((".jpg", ".jpeg", ".png", ".webp")):
        return render_template("index.html", error="Desteklenmeyen dosya türü.")

    file_name = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{file.filename}"
    file_path = os.path.join(UPLOAD_FOLDER, file_name)
    file.save(file_path)

    try:
        results = process_image(file_path, KNOWN_FACES_DIR)
        return render_template("result.html", results=results)
    except Exception as e:
        return render_template("index.html", error="Yüz tanıma işlemi başarısız oldu. " + str(e))

@app.route("/student/<name>")
def student_detail(name):
    student = get_student(name)
    if not student:
        return redirect(url_for("index"))
    attendance_history = get_attendance_history(name)
    return render_template("student_detail.html", student=student, attendance_history=attendance_history)

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

if __name__ == "__main__":
    app.run(debug=True)
