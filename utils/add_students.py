import sqlite3

connection = sqlite3.connect("data/students.db")
cursor = connection.cursor()

# Öğrenci ekleme
students = [
    ("Batuhan Yeşilyayla", "0", "/Users/gokcesoylu/attendance_app/static/images/known_faces/batuhan_yesilyayla.jpeg"),
    ("Aylin İrem Acar", "221805025", "/Users/gokcesoylu/attendance_app/static/images/known_faces/aylin_irem_acar.jpeg"),
    ("Berk Oğuz", "201805050", "/Users/gokcesoylu/attendance_app/static/images/known_faces/berk_oguz.jpeg"),
    ("Mustafa Cihan Ayindi", "211805014", "/Users/gokcesoylu/attendance_app/static/images/known_faces/cihan_ayindi.jpeg"),
    ("Enes Demir", "211805042", "/Users/gokcesoylu/attendance_app/static/images/known_faces/enes_demir.jpeg"),
    ("Ezgi Çoban", "221805077", "/Users/gokcesoylu/attendance_app/static/images/known_faces/ezgi_coban.jpeg"),
    ("Gülşen Dülger", "221805005", "/Users/gokcesoylu/attendance_app/static/images/known_faces/gulsen_dulger.jpeg"),
    ("Köksal Kerem Tanil", "211805018", "/Users/gokcesoylu/attendance_app/static/images/known_faces/koksal_kerem_tanil.jpeg"),
    ("Mehmet Yalçın Tağa", "221805018", "/Users/gokcesoylu/attendance_app/static/images/known_faces/mehmet_yalcin_taga.jpeg"),
    ("Rıza Karakaya", "211805021", "/Users/gokcesoylu/attendance_app/static/images/known_faces/riza_karakaya.jpeg"),
    ("Ulaş Ayçiçek", "201805048", "/Users/gokcesoylu/attendance_app/static/images/known_faces/ulas_aycicek.jpeg"),
]

cursor.executemany('''
    INSERT INTO students (name, student_number, image_path)
    VALUES (?, ?, ?)
''', students)

connection.commit()
connection.close()

print("Öğrenciler veritabanına eklendi.")
