import sqlite3

def init_db():
    connection = sqlite3.connect("data/students.db")
    cursor = connection.cursor()

    # Öğrenciler tablosu
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            student_number TEXT NOT NULL,
            image_path TEXT NOT NULL
        )
    ''')

    # Yoklama geçmişi tablosu
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER,
            status TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (student_id) REFERENCES students (id)
        )
    ''')

    connection.commit()
    connection.close()

if __name__ == "__main__":
    init_db()
    print("Veritabanı başlatıldı.")
