# Test Suite - Gamified Python Learner AI

Bu klasör projenin tüm testlerini içermektedir.

## 📁 Klasör Yapısı

```
tests/
├── authentication/       # Authentication sistemi testleri
│   ├── test_auth.py          # Login/Register testleri
│   └── test_gamification.py  # XP, Level, Leaderboard testleri
├── learning/            # Learning modülü testleri
│   └── test_lessons.py       # Ders completion, progress tracking
├── coding/              # Coding modülü testleri
│   └── test_code_execution.py # Code execution, test cases
├── integration/         # Integration testleri
│   └── test_user_journey.py  # End-to-end user flow testleri
├── ui_automation/       # UI automation testleri (Selenium)
│   └── test_selenium_ui.py   # Browser automation testleri
├── fixtures/            # Test fixtures
│   └── base_fixtures.py      # Ortak test verileri
├── conftest.py          # pytest global configuration
└── README.md           # Bu dosya
```

## 🚀 Kurulum

```bash
# Test paketlerini kur
pip install pytest pytest-django coverage selenium

# Veya requirements.txt'ten kur
pip install -r requirements.txt
```

## ▶️ Testleri Çalıştırma

### Tüm Testleri Çalıştır

```bash
# Standart Django test runner
python manage.py test tests

# pytest ile
pytest

# Verbose output
pytest -v

# Daha detaylı output
pytest -vv
```

### Belirli Test Kategorilerini Çalıştır

```bash
# Sadece unit testler
pytest -m unit

# Sadece integration testler
pytest -m integration

# Sadece UI testler (yavaş)
pytest -m ui

# UI testler hariç hepsi
pytest -m "not ui"
```

### Belirli Test Dosyalarını Çalıştır

```bash
# Authentication testleri
pytest tests/authentication/

# Sadece login testleri
pytest tests/authentication/test_auth.py

# Belirli bir test class'ı
pytest tests/authentication/test_auth.py::TestUserLogin

# Belirli bir test fonksiyonu
pytest tests/authentication/test_auth.py::TestUserLogin::test_user_login_success
```

## 📊 Coverage Raporu

### Coverage Ölç

```bash
# pytest-cov ile
pytest --cov=apps --cov-report=html

# Veya coverage.py ile
coverage run --source='.' manage.py test
coverage report
coverage html

# HTML rapor açmak için
# Windows:
start htmlcov/index.html
# Linux/Mac:
open htmlcov/index.html
```

### Coverage Hedefi

- **Mevcut coverage:** ~85%
- **Hedef coverage:** >90%

## 🧪 Test Kategorileri

### Unit Tests (`@pytest.mark.unit`)

**Lokasyon:** `authentication/`, `learning/`, `coding/`

**Test edilen:**
- User registration/login
- Password validation
- XP calculation
- Level progression
- Leaderboard ranking
- Lesson completion
- Progress tracking
- Code execution
- Test case evaluation

**Çalıştırma:**
```bash
pytest -m unit
```

### Integration Tests (`@pytest.mark.integration`)

**Lokasyon:** `integration/`

**Test edilen:**
- Complete user journeys
- Register → Login → Learn → Complete → Earn XP
- Register → Login → Code → Submit → Pass → Earn XP
- Gamification integration (XP → Level → Leaderboard)

**Çalıştırma:**
```bash
pytest -m integration
```

### UI Automation Tests (`@pytest.mark.ui`)

**Lokasyon:** `ui_automation/`

**Test edilen:**
- Login flow (Selenium)
- Code editor interaction
- Form validation
- Responsive design (mobile, tablet, desktop)
- Browser compatibility (Chrome, Firefox, Edge)

**Çalıştırma:**
```bash
pytest -m ui

# Headless mode (background)
pytest -m ui --headed=false
```

**Not:** Selenium testleri için Chrome/Firefox driver gerekli.

## 🔧 Test Fixtures

Test fixtures `tests/fixtures/base_fixtures.py` dosyasında tanımlıdır.

**Mevcut fixtures:**
- `test_user` - Basit test kullanıcısı
- `test_user_with_xp` - XP'si olan test kullanıcısı
- `test_module` - Test modülü
- `test_lesson` - Test dersi
- `test_exercise` - Test egzersizi
- `test_testcase` - Test senaryosu
- `authenticated_client` - Giriş yapmış client

**Kullanım:**
```python
def test_something(test_user, test_module):
    # test_user ve test_module otomatik oluşturulur
    assert test_user.username == 'testuser'
```

## 📝 Yeni Test Ekleme

### 1. Unit Test Ekle

```python
# tests/authentication/test_auth.py
@pytest.mark.unit
@pytest.mark.django_db
def test_my_new_feature(test_user):
    # Test kodun buraya
    assert True
```

### 2. Integration Test Ekle

```python
# tests/integration/test_user_journey.py
@pytest.mark.integration
@pytest.mark.django_db
def test_new_user_flow(client):
    # Test kodun buraya
    pass
```

### 3. Selenium Test Ekle

```python
# tests/ui_automation/test_selenium_ui.py
@pytest.mark.ui
@pytest.mark.slow
def test_new_ui_feature(browser, live_server):
    browser.get(f'{live_server.url}/')
    # Test kodun buraya
```

## 🐛 Debugging Testleri

### Test'i debug modda çalıştır

```bash
# Hata mesajlarını göster
pytest -vv

# İlk hatada dur
pytest -x

# Hangi testlerin çalışacağını göster (gerçekten çalıştırmadan)
pytest --collect-only

# Print statements göster
pytest -s
```

### Belirli bir testi debug et

```python
# Test içine breakpoint ekle
def test_something():
    import pdb; pdb.set_trace()
    # veya
    breakpoint()
```

## 📊 Test İstatistikleri

**Toplam Test Sayısı:** 50+

**Kategori Dağılımı:**
- Unit Tests: ~30
- Integration Tests: ~10
- UI Automation Tests: ~10

**Ortalama Çalıştırma Süresi:**
- Unit Tests: ~10 saniye
- Integration Tests: ~30 saniye
- UI Tests: ~2 dakika

## ✅ Başarı Kriterleri

Test suite'in başarılı sayılması için:
- ✅ Tüm testler pass olmalı
- ✅ Coverage >85% olmalı
- ✅ Linter hataları olmamalı
- ✅ Security testleri pass olmalı

## 🎯 TODO

- [ ] Mock Gemini API responses (AI testleri için)
- [ ] GitHub Actions CI/CD entegrasyonu
- [ ] Performance benchmarking testleri
- [ ] Load testing (100+ concurrent users)
- [ ] Accessibility testing (WCAG 2.1)

## 📚 Kaynaklar

- [pytest documentation](https://docs.pytest.org/)
- [pytest-django](https://pytest-django.readthedocs.io/)
- [Selenium documentation](https://www.selenium.dev/documentation/)
- [Coverage.py](https://coverage.readthedocs.io/)

---

**Yazar:** Yusuf Hakan Kılıç (Tester & QA Engineer)  
**Son Güncelleme:** 12 Kasım 2025

