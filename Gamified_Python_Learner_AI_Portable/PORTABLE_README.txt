================================================================================
    GAMIFIED PYTHON LEARNER AI - PORTABLE VERSION
================================================================================

Bu portable versiyon, sadece Python yuklu olan herhangi bir Windows 
bilgisayarda calisacak sekilde hazirlanmistir.

================================================================================
                          KURULUM TALIMATLARI
================================================================================

1. ZIP DOSYASINI CIKARIN
   - ZIP dosyasini herhangi bir klasore cikarin
   - Ornek: C:\PythonLearnerAI\

2. PYTHON KONTROLU
   - Python 3.8 veya uzeri yuklu olmalidir
   - Kontrol etmek icin: python --version
   - Python yoksa: https://www.python.org/downloads/

3. SERVERI BASLATIN
   - START_SERVER.bat dosyasina cift tiklayin
   - Ilk calistirmada:
     * Virtual environment olusturulacak
     * Gerekli paketler yuklenecek
     * Database olusturulacak
     * Server baslatilacak

4. TARAYICIDA ACIN
   - Otomatik olarak acilmazsa:
   - http://127.0.0.1:8000 adresine gidin
   - Admin paneli: http://127.0.0.1:8000/admin/

================================================================================
                          ILK KULLANIM
================================================================================

1. SUPERUSER OLUSTURMA
   - Ilk kullanimda admin hesabi olusturmaniz gerekir
   - Terminalde (START_SERVER.bat acikken):
     python manage.py createsuperuser
   - Kullanici adi, email ve sifre girin

2. VERITABANI
   - SQLite veritabani otomatik olusturulur (db.sqlite3)
   - Bu dosya proje klasorunde yer alir

================================================================================
                          YAPILANDIRMA
================================================================================

.env DOSYASI
   - Tum API keyler ve ayarlar .env dosyasinda
   - GEMINI_API_KEY: Google Gemini AI icin
   - EMAIL ayarlari: Email gonderimi icin
   - SECRET_KEY: Django guvenlik anahtari

EMAIL AYARLARI (Sifremi Unuttum icin GEREKLI):
   - BREVO_API_KEY: Brevo API anahtari (xsmtpsib- veya xkeysib- ile baslar)
   - EMAIL_HOST_USER: Brevo SMTP kullanici adi (genelde ...@smtp-brevo.com)
   - EMAIL_HOST_PASSWORD: Brevo SMTP sifresi veya API key
   
   NOT: Eger "Sifremi Unuttum" butonuna tikladiginizda email gelmiyorsa:
   1. .env dosyasini acin
   2. BREVO_API_KEY ve EMAIL_HOST_PASSWORD degerlerini doldurun
   3. Serveri yeniden baslatin

AYARLARI DEGISTIRMEK ICIN:
   - .env dosyasini bir metin editoru ile acin
   - Degisikliklerden sonra serveri yeniden baslatin

================================================================================
                          SORUN GIDerme
================================================================================

1. "Python bulunamadi" HATASI
   - Python yuklu oldugundan emin olun
   - PATH ortam degiskenine eklendi mi kontrol edin

2. "Paket yuklenemedi" HATASI
   - Internet baglantinizi kontrol edin
   - Firewall/antivirus paket yuklemeyi engelliyor olabilir

3. "Port zaten kullaniliyor" HATASI
   - 8000 portu baska bir program tarafindan kullaniliyor
   - O programi kapatin veya farkli bir port kullanin
   - Farkli port: python manage.py runserver 8001

4. DATABASE HATALARI
   - db.sqlite3 dosyasini silip tekrar deneyin
   - python manage.py migrate komutunu calistirin

================================================================================
                          DURDURMA
================================================================================

Serveri durdurmak icin:
   - Terminal penceresinde Ctrl+C tuslarina basin
   - Veya terminal penceresini kapatin

================================================================================
                          NOTLAR
================================================================================

- Bu portable versiyon development (gelistirme) modunda calisir
- Production (canli) kullanim icin ek yapilandirma gerekir
- Tum veriler db.sqlite3 dosyasinda saklanir
- .env dosyasini paylasmayin (API keyler icerir)

================================================================================
                          DESTEK
================================================================================

Sorun yasarsaniz:
1. README.md dosyasini okuyun
2. Hata mesajlarini kontrol edin
3. Log dosyalarini inceleyin

================================================================================
