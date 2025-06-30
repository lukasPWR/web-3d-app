# Instrukcja Obsługi - Web 3D Application

## 🛠️ Aplikacje do Pobrania

### 1. Node.js (wymagany)

- **Pobierz z**: [https://nodejs.org/](https://nodejs.org/)
- **Wersja**: Pobierz wersję LTS (Long Term Support)
- **Instalacja**:
  - Uruchom pobrany plik instalacyjny
  - Zaznacz opcję "Add to PATH" podczas instalacji
  - Restart komputera po instalacji

### 2. Git (wymagany)

- **Pobierz z**: [https://git-scm.com/downloads](https://git-scm.com/downloads)
- **Instalacja**:
  - Uruchom pobrany plik instalacyjny
  - Zostaw domyślne ustawienia podczas instalacji
  - Zaznacz opcję "Add Git to PATH"

### 3. Blender (wymagany do tworzenia modeli 3D)

- **Pobierz z**: [https://www.blender.org/download/](https://www.blender.org/download/)
- **Wersja**: 3.0 lub nowsza
- **Instalacja**:
  - Uruchom pobrany plik instalacyjny
  - **WAŻNE**: Podczas instalacji zaznacz opcję dodania Blender do PATH
  - Jeśli nie było tej opcji, dodaj ręcznie folder Blender do zmiennej PATH systemu

## 🔧 Sprawdzenie Instalacji

Otwórz wiersz poleceń (Command Prompt/Terminal) i wykonaj poniższe komendy:

```bash
# Sprawdź Python
python --version
# Powinno zwrócić wersję Python 3.8+

# Sprawdź Node.js
node --version
# Powinno zwrócić wersję v14+

# Sprawdź npm
npm --version
# Powinno zwrócić numer wersji

# Sprawdź Git
git --version
# Powinno zwrócić wersję Git

# Sprawdź Blender
blender --version
# Powinno zwrócić wersję Blender 3.0+
```

## 🐍 Konfiguracja Backend (Python)

### 1. Tworzenie Środowiska Wirtualnego

```bash
# Przejdź do folderu backend
cd backend

# Utwórz środowisko wirtualne
python -m venv venv
```

### 3. Instalacja Bibliotek Python

```bash
# Zainstaluj wszystkie wymagane biblioteki
pip install -r requirements.txt
```

**Jeśli plik requirements.txt nie istnieje, zainstaluj ręcznie:**

```bash
pip install flask flask-cors werkzeug pydantic
```

### 4. Sprawdzenie Instalacji Backend

```bash
# Uruchom serwer Flask
python app.py run
```

**Nie zamykaj tego okna terminala!**

## 🌐 Konfiguracja Frontend (Node.js)

### 1. Otwórz Nowy Terminal

### 2. Przejdź do Folderu Frontend

```bash
# Z głównego folderu projektu
cd frontend
```

### 3. Instalacja Bibliotek Node.js

```bash
# Zainstaluj wszystkie zależności
npm install
```

Instalacja może potrwać kilka minut.

### 4. Uruchomienie Frontend

```bash
# Uruchom serwer deweloperski
npm run dev
```

Zobaczysz komunikat podobny do:

```
Local:   http://localhost:5173/
Network: http://192.168.1.xxx:5173/
```

## 🚀 Uruchamianie Aplikacji

### Proces Startowy (za każdym razem)

1. **Terminal 1 - Backend:**

   ```bash
   cd backend
   python app.py run
   ```

2. **Terminal 2 - Frontend:**

   ```bash
   cd frontend
   npm run dev
   ```

3. **Otwórz przeglądarkę** i wejdź na: `http://localhost:5173`
