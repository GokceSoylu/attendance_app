import sqlite3
from datetime import datetime

# Öğrenci ekleme fonksiyonu
def add_student(name, student_number, image_path):
    connection = sqlite3.connect("data/students.db")
    cursor = connection.cursor()
    cursor.execute('''
        INSERT INTO students (name, student_number, image_path)
        VALUES (?, ?, ?)
    ''', (name, student_number, image_path))

    # Son eklenen öğrencinin ID'sini al
    student_id = cursor.lastrowid

    # Attendance tablosuna "present" kaydı ekle
    mark_attendance(student_id, status="present")

    connection.commit()
    connection.close()


# Öğrenci bilgilerini getirme fonksiyonu
def get_student(student_id):
    connection = sqlite3.connect("data/students.db")
    connection.row_factory = sqlite3.Row  # Row nesnelerini sözlük gibi almak için
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM students WHERE id=?", (student_id,))
    student = cursor.fetchone()
    connection.close()

    # Eğer öğrenci bulunduysa, tuple'ı bir sözlüğe çeviriyoruz
    if student:
        return dict(student)  # Row nesnesini dict'e dönüştürüyoruz
    return None

# Tüm öğrencileri getirme fonksiyonu
def get_all_students():
    connection = sqlite3.connect("data/students.db")
    connection.row_factory = sqlite3.Row  # Row nesnelerini sözlük gibi almak için
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM students")
    students = cursor.fetchall()
    connection.close()

    # Row nesnelerini dict'e dönüştürme
    return [dict(student) for student in students]


# Öğrencilerin yoklama geçmişini getirme fonksiyonu
def get_attendance_history():
    connection = sqlite3.connect("data/students.db")
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM attendance")
    history = cursor.fetchall()
    connection.close()

    # Yoklama geçmişini daha anlamlı bir formatta döndür
    return [{"id": record[0], "student_id": record[1], "status": record[2], "timestamp": record[3]} for record in history]

def update_student_image(student_id, image_path):
    connection = sqlite3.connect("data/students.db")
    cursor = connection.cursor()
    cursor.execute('''
        UPDATE students
        SET image_path = ?
        WHERE id = ?
    ''', (image_path, student_id))

    # Attendance tablosuna "present" kaydı ekle
    mark_attendance(student_id, status="present")

    connection.commit()
    connection.close()


# Yoklama kaydını ekleme fonksiyonu
def mark_attendance(student_id, status):
    connection = sqlite3.connect("data/students.db")
    cursor = connection.cursor()
    
    cursor.execute('''
        INSERT INTO attendance (student_id, status, timestamp)
        VALUES (?, ?, ?)
    ''', (student_id, status, datetime.now()))
    
    connection.commit()
    connection.close()

