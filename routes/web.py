from flask import Blueprint, request, jsonify, render_template
from app.views.VoicetoText import render_voice_page

# Create Blueprint
web = Blueprint("web", __name__)

@web.route("/voice")
def voice_page():
    """Halaman CBT Voice"""
    return render_voice_page()

@web.route("/api/score-answer", methods=["POST"])
def score_answer():
    """API endpoint untuk scoring jawaban siswa menggunakan Gemini AI"""
    try:
        # Import here to avoid circular import
        import main
        
        data = request.get_json()
        question = data.get('question', '')
        answer = data.get('answer', '')
        
        if not question or not answer:
            return jsonify({
                "error": "Question dan answer tidak boleh kosong"
            }), 400
        
        # Call Gemini AI untuk scoring
        result = main.score_answer(question, answer)
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

