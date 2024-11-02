import os  # Add this import for environment variables
from flask import Flask, render_template, request
from googletrans import Translator, LANGUAGES

app = Flask(__name__)
translator = Translator()

# Retrieve the API key and port from environment variables
GOOGLE_API_KEY = os.getenv("AIzaSyC_tDHXYvaLgiunnTqivATD4cps_NpxeH8")

# Function to handle translations across multiple languages
def translate(query, source_language):
    languages = {
        "en": ["mg", "es", "de", "nl", "it"],
        "mg": ["en", "es", "de", "nl", "it"],
        "es": ["en", "mg", "de", "nl", "it"],
        "de": ["mg", "en", "es", "nl", "it"],
        "nl": ["mg", "en", "es", "de", "it"],
        "it": ["mg", "en", "es", "de", "nl"]
    }

    results = {}
    if source_language in languages:
        for lang in languages[source_language]:
            try:
                translation = translator.translate(query, src=source_language, dest=lang)
                results[LANGUAGES[lang].capitalize()] = translation.text
            except Exception as e:
                results[LANGUAGES[lang].capitalize()] = f"Error: {str(e)}"
    return results

@app.route('/')
def index():
    lessons = [
        {
            "date": "2024-11-02",
            "malagasy": "Manao ahoana ianao?",
            "english": "How are you?",
            "examples": ["How are you feeling today?", "Manao ahoana ianao androany?"],
            "notes": "This phrase is commonly used to inquire about someone’s well-being and is a friendly way to start a conversation."
        }
    ]

    contacts = {
        "WhatsApp": "+261 34 23 215 36",
        "Phone": "+261 32 60 277 11",
        "Email": "ramenjanahary129@gmail.com",
        "Facebook": "Daphane Hsaa"
    }

    return render_template('index.html', lessons=lessons, contacts=contacts)

@app.route('/search', methods=['POST'])
def search():
    query = request.form['query']
    direction = request.form['direction']
    
    # Map direction to source language code
    source_language = direction.split('_')[0] if '_' in direction else direction
    results = translate(query, source_language)

    # Re-render the index.html with the translation results, lessons, and contacts
    lessons = [
        {
            "date": "2024-11-02",
            "malagasy": "Manao ahoana ianao?",
            "english": "How are you?",
            "examples": ["How are you feeling today?", "Manao ahoana ianao androany?"],
            "notes": "This phrase is commonly used to inquire about someone’s well-being and is a friendly way to start a conversation."
        }
    ]

    contacts = {
        "WhatsApp": "+261 34 23 215 36",
        "Phone": "+261 32 60 277 11",
        "Email": "ramenjanahary129@gmail.com",
        "Facebook": "Daphane Hsaa"
    }

    return render_template('index.html', results=results, lessons=lessons, contacts=contacts)

@app.route('/register', methods=['POST'])
def register():
    name = request.form['name']
    surname = request.form['surname']
    email = request.form['email']

    print(f"New Registration:\nName: {name}\nSurname: {surname}\nEmail: {email}\n")

    return "Registration received! Thank you!."

if __name__ == '__main__':
    # Use the PORT environment variable or default to 5000 for local testing
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
