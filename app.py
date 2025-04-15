import os
import logging
from flask import Flask, render_template, request, jsonify
from werkzeug.middleware.proxy_fix import ProxyFix

# Import utility functions
from utils.braille_converter import text_to_braille, braille_to_text
from utils.image_processor import extract_text_from_image
from utils.speech_processor import text_to_speech

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Create the app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "default_secret_key_for_development")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/text-to-braille')
def text_to_braille_page():
    return render_template('text_to_braille.html')

@app.route('/image-to-braille')
def image_to_braille_page():
    return render_template('image_to_braille.html')

@app.route('/braille-to-speech')
def braille_to_speech_page():
    return render_template('braille_to_speech.html')

@app.route('/api/text-to-braille', methods=['POST'])
def convert_text_to_braille():
    data = request.get_json()
    text = data.get('text', '')
    
    if not text:
        return jsonify({'error': 'No text provided'}), 400
    
    braille = text_to_braille(text)
    detailed_mapping = []
    
    for i, char in enumerate(text):
        if char == ' ':
            detailed_mapping.append({
                'original': 'space',
                'braille': '⠀'  # Braille space
            })
        else:
            detailed_mapping.append({
                'original': char,
                'braille': braille[i] if i < len(braille) else '⠿'  # Default in case of mismatch
            })
    
    return jsonify({
        'braille': braille,
        'detailed_mapping': detailed_mapping
    })

@app.route('/api/braille-to-text', methods=['POST'])
def convert_braille_to_text():
    data = request.get_json()
    braille = data.get('braille', '')
    
    if not braille:
        return jsonify({'error': 'No Braille provided'}), 400
    
    text = braille_to_text(braille)
    return jsonify({'text': text})

@app.route('/api/image-to-text', methods=['POST'])
def process_image():
    if 'image' not in request.files:
        return jsonify({'error': 'No image provided'}), 400
    
    image_file = request.files['image']
    if image_file.filename == '':
        return jsonify({'error': 'No image selected'}), 400
    
    try:
        extracted_text = extract_text_from_image(image_file)
        if not extracted_text:
            return jsonify({'error': 'No text detected in the image'}), 400
        
        braille = text_to_braille(extracted_text)
        return jsonify({
            'text': extracted_text,
            'braille': braille
        })
    except Exception as e:
        logging.error(f"Error processing image: {str(e)}")
        return jsonify({'error': f'Error processing image: {str(e)}'}), 500

@app.route('/api/text-to-speech', methods=['POST'])
def convert_text_to_speech():
    data = request.get_json()
    text = data.get('text', '')
    
    if not text:
        return jsonify({'error': 'No text provided'}), 400
    
    try:
        audio_data = text_to_speech(text)
        return jsonify({'audio_data': audio_data})
    except Exception as e:
        logging.error(f"Error converting text to speech: {str(e)}")
        return jsonify({'error': f'Error converting text to speech: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
