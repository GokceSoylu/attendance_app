# attendance_app
napıyorum ben de bilmiyorum

attendance_app/
├── app.py                 # Flask uygulaması
├── templates/             # HTML dosyaları
│   ├── index.html         # Ana sayfa
│   ├── result.html        # Yoklama sonuçları
│   ├── student_detail.html # Öğrenci detayı
│   └── add_student.html   # Yeni öğrenci ekleme
├── static/                # CSS, JS ve resim dosyaları
│   ├── css/
│   │   └── style.css      # Stil dosyaları
│   └── images/
│       ├── known_faces/   # Kayıtlı öğrenci yüzleri
│       ├── uploads/       # Yüklenen resimler
│       └── result_images/ # Sonuç görüntüleri
├── utils/                 # Yardımcı fonksiyonlar
│   ├── face_recognition.py # Yüz tanıma işlemleri
│   └── db_utils.py        # Veritabanı işlemleri
├── data/
│   └── students.db        # SQLite veritabanı
└── requirements.txt        # Python bağımlılıkları
