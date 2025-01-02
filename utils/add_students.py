import sqlite3
import os

# Veritabanı bağlantısını aç
connection = sqlite3.connect("data/students.db")
cursor = connection.cursor()

# Tabloyu sıfırla (varsa mevcut kayıtları sil)
cursor.execute("DROP TABLE IF EXISTS students")
cursor.execute('''
    CREATE TABLE students (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        student_number TEXT NOT NULL,
        image_path TEXT NOT NULL
    )
''')

# Yeni öğrenci verilerini ekleyin
students = [
    ("Batuhan Yeşilyayla", "0", "static/images/known_faces/batuhan_yesilyayla.jpeg"),
    ("Aylin İrem Acar", "221805025", "static/images/known_faces/aylin_irem_acar.jpeg"),
    ("Berk Oğuz", "201805050", "static/images/known_faces/berk_oguz.jpeg"),
    ("Mustafa Cihan Ayindi", "211805014", "static/images/known_faces/cihan_ayindi.jpeg"),
    ("Enes Demir", "211805042", "static/images/known_faces/enes_demir.jpeg"),
    ("Ezgi Çoban", "221805077", "static/images/known_faces/ezgi_coban.jpeg"),
    ("Gülşen Dülger", "221805005", "static/images/known_faces/gulsen_dulger.jpeg"),
    ("Köksal Kerem Tanil", "211805018", "static/images/known_faces/koksal_kerem_tanil.jpeg"),
    ("Mehmet Yalçın Tağa", "221805018", "static/images/known_faces/mehmet_yalcin_taga.jpeg"),
    ("Rıza Karakaya", "211805021", "static/images/known_faces/riza_karakaya.jpeg"),
    ("Ulaş Ayçiçek", "201805048", "static/images/known_faces/ulas_aycicek.jpeg"),
]

# Yeni verileri veritabanına ekleyin
cursor.executemany('''
    INSERT INTO students (name, student_number, image_path)
    VALUES (?, ?, ?)
''', students)

# Değişiklikleri kaydet ve bağlantıyı kapat
connection.commit()
connection.close()

print("Öğrenciler başarıyla veritabanına eklendi.")
