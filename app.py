from flask import Flask, request, jsonify, render_template
from werkzeug.utils import secure_filename
import os
import base64
import main

app = Flask(__name__)

# Konfigurasi upload
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp', 'pdf', 'txt', 'doc', 'docx'}
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size

app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH

# Buat folder upload jika belum ada
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")  # tampilkan UI

@app.route("/generate", methods=["POST"])
def generate():
    try:
        # Handle form data (for file upload)
        if request.content_type and 'multipart/form-data' in request.content_type:
            prompt = request.form.get('prompt', '')
            
            # Handle file upload
            if 'file' in request.files:
                file = request.files['file']
                if file and file.filename != '' and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    file_path = os.path.join(UPLOAD_FOLDER, filename)
                    file.save(file_path)
                    
                    # Convert image to base64 for processing
                    with open(file_path, 'rb') as img_file:
                        img_base64 = base64.b64encode(img_file.read()).decode('utf-8')
                    
                    # Clean up uploaded file
                    os.remove(file_path)
                    
                    # Process with image
                    if prompt:
                        result = main.generate_text_with_image(prompt, img_base64, filename)
                    else:
                        result = main.analyze_image(img_base64, filename)
                    
                    return jsonify({"prompt": prompt, "result": result, "has_file": True})
            
            # No file, just text
            if not prompt:
                return jsonify({"error": "prompt tidak boleh kosong"}), 400
            
            result = main.generate_text(prompt)
            return jsonify({"prompt": prompt, "result": result, "has_file": False})
        
        # Handle JSON data (for text-only requests)
        else:
            data = request.get_json()
            prompt = data.get('prompt', '')
            
            if not prompt:
                return jsonify({"error": "prompt tidak boleh kosong"}), 400
            
            result = main.generate_text(prompt)
            return jsonify({"prompt": prompt, "result": result, "has_file": False})
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)