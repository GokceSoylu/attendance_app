import sqlite3
from datetime import datetime


# Veritabanı bağlantısını sağlayan yardımcı fonksiyon
def get_connection():
    return sqlite3.connect("data/students.db")


# Öğrenci ekleme fonksiyonu
def add_student(name, student_number, image_path):
    try:
        with get_connection() as connection:
            cursor = connection.cursor()
            cursor.execute('''
                INSERT INTO students (name, student_number, image_path)
                VALUES (?, ?, ?)
            ''', (name, student_number, image_path))
            
            student_id = cursor.lastrowid  # Son eklenen öğrencinin ID'si
            mark_attendance(student_id, "present")  # Varsayılan yoklama durumu
        print(f"Öğrenci başarıyla eklendi: {name}")
    except Exception as e:
        print(f"Öğrenci eklerken hata oluştu: {e}")


# Tek bir öğrencinin bilgilerini alma
def get_student(student_id):
    try:
        with get_connection() as connection:
            connection.row_factory = sqlite3.Row
            cursor = connection.cursor()
            cursor.execute("SELECT * FROM students WHERE id=?", (student_id,))
            student = cursor.fetchone()
            return dict(student) if student else None
    except Exception as e:
        print(f"Öğrenci bilgileri alınırken hata oluştu: {e}")
        return None


# Tüm öğrencileri listeleme
def get_all_students():
    try:
        with get_connection() as connection:
            connection.row_factory = sqlite3.Row
            cursor = connection.cursor()
            cursor.execute("SELECT * FROM students")
            students = cursor.fetchall()
            return [dict(student) for student in students]
    except Exception as e:
        print(f"Tüm öğrenciler alınırken hata oluştu: {e}")
        return []


# Yoklama geçmişini alma
def get_attendance_history():
    try:
        with get_connection() as connection:
            cursor = connection.cursor()
            cursor.execute("SELECT * FROM attendance")
            history = cursor.fetchall()
            return [
                {"id": record[0], "student_id": record[1], "status": record[2], "timestamp": record[3]}
                for record in history
            ]
    except Exception as e:
        print(f"Yoklama geçmişi alınırken hata oluştu: {e}")
        return []


# Öğrenci resmi güncelleme
def update_student_image(student_id, image_path):
    try:
        with get_connection() as connection:
            cursor = connection.cursor()
            cursor.execute('''
                UPDATE students
                SET image_path = ?
                WHERE id = ?
            ''', (image_path, student_id))
        print(f"Öğrenci resmi başarıyla güncellendi: ID {student_id}")
    except Exception as e:
        print(f"Öğrenci resmi güncellenirken hata oluştu: {e}")


# Yoklama kaydı ekleme
def mark_attendance(student_id, status):
    try:
        with get_connection() as connection:
            cursor = connection.cursor()
            cursor.execute('''
                INSERT INTO attendance (student_id, status, timestamp)
                VALUES (?, ?, ?)
            ''', (student_id, status, datetime.now()))
        print(f"Yoklama kaydı başarıyla eklendi: Öğrenci ID {student_id}, Durum: {status}")
    except Exception as e:
        print(f"Yoklama kaydı eklerken hata oluştu: {e}")
