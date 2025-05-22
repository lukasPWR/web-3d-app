# Web 3D App Backend

Backend aplikacji do wyświetlania modeli 3D, napisany w języku Python z wykorzystaniem frameworka Flask.

## Instalacja

1. Utwórz wirtualne środowisko Python:

   ```
   python -m venv venv
   ```

2. Aktywuj wirtualne środowisko:

   - Windows: `venv\Scripts\activate`
   - Linux/Mac: `source venv/bin/activate`

3. Zainstaluj zależności:
   ```
   pip install -r requirements.txt
   ```

## Uruchomienie

1. Z aktywowanym wirtualnym środowiskiem uruchom:
   ```
   flask run
   ```
2. Aplikacja będzie dostępna pod adresem: `http://127.0.0.1:5000/`

## Dostępne endpointy API

- `GET /api/models` - pobiera listę wszystkich modeli
- `GET /api/models/<id>` - pobiera szczegóły modelu o podanym ID
- `POST /api/models` - dodaje nowy model
- `GET /models/<filename>` - pobiera plik modelu 3D
