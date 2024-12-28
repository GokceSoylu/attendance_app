# utils/db_utils.py

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
    connection.commit()
    connection.close()

# Öğrenci bilgilerini getirme fonksiyonu
def get_student(student_id):
    connection = sqlite3.connect("data/students.db")
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM students WHERE id=?", (student_id,))
    student = cursor.fetchone()
    connection.close()
    return student

# Tüm öğrencileri getirme fonksiyonu
def get_all_students():
    connection = sqlite3.connect("data/students.db")
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM students")
    students = cursor.fetchall()
    connection.close()
    return students

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

# Öğrencilerin yoklama geçmişini getirme fonksiyonu
def get_attendance_history():
    connection = sqlite3.connect("data/students.db")
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM attendance")
    history = cursor.fetchall()
    connection.close()
    return history
