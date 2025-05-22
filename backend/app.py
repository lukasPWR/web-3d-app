from flask import Flask, jsonify, request, send_from_directory
import os

app = Flask(__name__)

models = [
    {
        "id": "1",
        "name": "Model 1",
        "description": "Przykładowy model 3D nr 1",
        "modelUrl": "/models/model1.gltf"
    },
    {
        "id": "2",
        "name": "Model 2",
        "description": "Przykładowy model 3D nr 2",
        "modelUrl": "/models/model2.gltf"
    }
]

# Folder dla plików modeli
MODELS_FOLDER = os.path.join(app.root_path, 'static/models')

@app.route('/api/models', methods=['GET'])
def get_models():
    """Zwraca listę wszystkich dostępnych modeli 3D"""
    return jsonify(models)

@app.route('/api/models/<model_id>', methods=['GET'])
def get_model(model_id):
    """Zwraca szczegóły konkretnego modelu 3D"""
    model = next((model for model in models if model["id"] == model_id), None)
    if model:
        return jsonify(model)
    return jsonify({"error": "Model not found"}), 404

@app.route('/models/<path:filename>')
def serve_model(filename):
    """Serwuje pliki modeli 3D"""
    return send_from_directory(MODELS_FOLDER, filename)

@app.route('/api/models', methods=['POST'])
def add_model():
    """Dodaje nowy model 3D"""
    if not request.json:
        return jsonify({"error": "Invalid request"}), 400
    
    new_model = {
        "id": str(len(models) + 1),
        "name": request.json.get("name", ""),
        "description": request.json.get("description", ""),
        "modelUrl": request.json.get("modelUrl", "")
    }
    models.append(new_model)
    return jsonify(new_model), 201

if __name__ == '__main__':
    app.run(debug=True)
