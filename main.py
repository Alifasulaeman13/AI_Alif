import google.generativeai as genai
import base64
import mimetypes

# Konfigurasi API Key
genai.configure(api_key="AIzaSyBt3RA9JK7KLOSJeC05q-gKxbzrQmsGB8c")  

# Tambahkan fungsi untuk list model yang tersedia
def list_available_models():
    """List semua model yang tersedia"""
    try:
        models = genai.list_models()
        available_models = []
        for model in models:
            if 'generateContent' in model.supported_generation_methods:
                available_models.append(model.name)
        return available_models
    except Exception as e:
        print(f"Error listing models: {e}")
        return ["gemini-pro", "gemini-pro-vision"]  # Default fallback

# Pilih model - gunakan model yang tersedia dan stabil
text_model = genai.GenerativeModel('gemini-2.5-flash')  # Model teks terbaru
vision_model = genai.GenerativeModel('gemini-2.5-flash')  # Model vision terbaru

def format_ai_text(text):
    """Format teks AI agar lebih rapih dan terstruktur"""
    import re
    
    # Hapus multiple spaces dan newlines
    text = re.sub(r'\n{3,}', '\n\n', text)
    text = re.sub(r'[ \t]+', ' ', text)
    
    # Konversi markdown-like formatting
    text = re.sub(r'\*\*(.*?)\*\*', r'**\1**', text)  # Bold
    text = re.sub(r'\*(.*?)\*', r'*\1*', text)        # Italic
    text = re.sub(r'`(.*?)`', r'`\1`', text)          # Code
    
    # Konversi angka dengan titik menjadi format yang lebih rapih
    text = re.sub(r'^\s*(\d+)\.\s*(.+)$', r'\1. \2', text, flags=re.MULTILINE)
    
    # Konversi bullet points
    text = re.sub(r'^\s*[-•]\s*(.+)$', r'• \1', text, flags=re.MULTILINE)
    
    # Konversi quotes
    text = re.sub(r'^>\s*(.+)$', r'> \1', text, flags=re.MULTILINE)
    
    # Tambahkan spacing yang konsisten antara paragraf
    paragraphs = text.split('\n\n')
    formatted_paragraphs = []
    
    for para in paragraphs:
        para = para.strip()
        if para:
            # Identifikasi headers
            if re.match(r'^(Opsi|Langkah|Poin|Perhatian|Catatan|Tips)', para, re.IGNORECASE):
                formatted_paragraphs.append(f"\n**{para}**\n")
            elif re.match(r'^\*\*', para):
                formatted_paragraphs.append(f"\n{para}\n")
            else:
                formatted_paragraphs.append(para)
    
    return '\n\n'.join(formatted_paragraphs)

def generate_text(prompt: str):
    response = text_model.generate_content(prompt)
    return format_ai_text(response.text)

def generate_text_with_image(prompt: str, image_base64: str, filename: str):
    """Generate text dengan input gambar"""
    try:
        # Decode base64 ke bytes
        image_bytes = base64.b64decode(image_base64)
        
        # Tentukan MIME type
        mime_type, _ = mimetypes.guess_type(filename)
        if not mime_type:
            mime_type = 'image/jpeg'
        
        # Buat Part dari gambar
        image_part = {
            "mime_type": mime_type,
            "data": image_bytes
        }
        
        # Generate content dengan gambar dan text
        response = vision_model.generate_content([prompt, image_part])
        return format_ai_text(response.text)
    except Exception as e:
        error_msg = str(e)
        if "quota" in error_msg.lower() or "429" in error_msg:
            return "⚠️ Maaf, kuota Google AI Vision telah habis untuk hari ini.\n\n💡 Solusi:\n1. Coba lagi besok setelah kuota reset\n2. Gunakan fitur chat teks saja (masih berfungsi)\n3. Setup billing di Google Cloud untuk kuota lebih besar\n\n📱 Chat teks tetap bisa digunakan normal!"
        elif "billing" in error_msg.lower():
            return "⚠️ Akun Google AI Anda perlu setup billing. Silakan aktifkan billing di Google Cloud Console untuk menggunakan fitur upload gambar."
        else:
            return f"❌ Maaf, terjadi kesalahan saat memproses gambar: {error_msg}"

def analyze_image(image_base64: str, filename: str):
    """Analisis gambar tanpa prompt"""
    try:
        # Decode base64 ke bytes
        image_bytes = base64.b64decode(image_base64)
        
        # Tentukan MIME type
        mime_type, _ = mimetypes.guess_type(filename)
        if not mime_type:
            mime_type = 'image/jpeg'
        
        # Buat Part dari gambar
        image_part = {
            "mime_type": mime_type,
            "data": image_bytes
        }
        
        # Generate content hanya dengan gambar
        response = vision_model.generate_content(["Jelaskan gambar ini secara detail", image_part])
        return response.text
    except Exception as e:
        error_msg = str(e)
        if "quota" in error_msg.lower() or "429" in error_msg:
            return "⚠️ Maaf, kuota Google AI Vision telah habis untuk hari ini.\n\n💡 Solusi:\n1. Coba lagi besok setelah kuota reset\n2. Gunakan fitur chat teks saja (masih berfungsi)\n3. Setup billing di Google Cloud untuk kuota lebih besar\n\n📱 Chat teks tetap bisa digunakan normal!"
        elif "billing" in error_msg.lower():
            return "⚠️ Akun Google AI Anda perlu setup billing. Silakan aktifkan billing di Google Cloud Console untuk menggunakan fitur upload gambar."
        else:
            return f"❌ Maaf, terjadi kesalahan saat menganalisis gambar: {error_msg}"

# Flask App
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import os
import tempfile

app = Flask(__name__)
CORS(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    try:
        # Cek apakah request datang sebagai FormData (untuk file upload)
        if request.files:
            # Handle FormData untuk file upload
            file = request.files.get('file')
            prompt = request.form.get('prompt', '')
            
            if not file:
                return jsonify({'error': 'No file provided'}), 400
            
            if not prompt:
                return jsonify({'error': 'No prompt provided'}), 400
            
            # Baca file dan convert ke base64
            file_content = file.read()
            image_base64 = base64.b64encode(file_content).decode('utf-8')
            filename = file.filename
            
            # Tentukan MIME type untuk return response
            mime_type, _ = mimetypes.guess_type(filename)
            if not mime_type:
                mime_type = 'image/jpeg'
            
            # Gunakan vision model untuk file upload
            result = generate_text_with_image(prompt, image_base64, filename)
            
            # Return hasil dengan URL gambar untuk ditampilkan kembali
            return jsonify({
                'result': result,
                'image_url': f"data:{mime_type};base64,{image_base64}"
            })
            
        else:
            # Handle JSON untuk text-only
            data = request.get_json()
            
            if not data:
                return jsonify({'error': 'No data provided'}), 400
            
            prompt = data.get('prompt', '')
            
            if not prompt:
                return jsonify({'error': 'No prompt provided'}), 400
            
            # Gunakan text model untuk text-only
            result = generate_text(prompt)
            return jsonify({'result': result})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)