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

### Modele 3D

- `GET /api/models` - pobiera listę wszystkich modeli
- `GET /api/models/<id>` - pobiera szczegóły modelu o podanym ID
- `POST /api/models/upload` - uploaduje nowy model 3D
- `DELETE /api/models/<id>` - usuwa model o podanym ID
- `GET /models/<filename>` - pobiera plik modelu 3D

### Tekstury

- `GET /api/textures` - pobiera listę wszystkich tekstur
- `POST /api/textures/upload` - uploaduje nową teksturę
- `DELETE /api/textures/<id>` - usuwa teksturę o podanym ID
- `GET /textures/<filename>` - pobiera plik tekstury

## Obsługiwane formaty

### Modele 3D

- OBJ
- GLTF
- GLB
- FBX

### Tekstury

- JPG/JPEG
- PNG
- BMP
- TGA
- TIFF
