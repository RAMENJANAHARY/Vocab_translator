import os
from flask import Flask, jsonify, render_template, request, redirect, url_for, session, flash, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from googletrans import Translator, LANGUAGES

# Initialize Flask app and configuration
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY', 'd1f5bfc4237f4832a1e6b97fdd3a7ef2f63acbc233587de9c9a1a597f6b8f474')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URI', 'sqlite:///users.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Load Google API key from environment variable
GOOGLE_API_KEY = os.getenv('AIzaSyC_tDHXYvaLgiunnTqivATD4cps_NpxeH8')

# Initialize database and Google Translator
db = SQLAlchemy(app)
translator = Translator()

# Serve the favicon
@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.ico', mimetype='image/vnd.microsoft.icon')

# Define User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    subscription_status = db.Column(db.String(20), default='free')  # 'free' or 'premium'

# Ensure database is created
with app.app_context():
    db.create_all()

# Define the translation function
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
                app.logger.error(f"Error translating from {source_language} to {lang}: {e}")
                results[LANGUAGES[lang].capitalize()] = f"Error: {str(e)}"
    return results

# User registration route
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = generate_password_hash(request.form['password'], method='pbkdf2:sha256')

        if User.query.filter_by(username=username).first():
            flash("Username already exists")
            return redirect(url_for('register'))

        new_user = User(username=username, password=password)
        db.session.add(new_user)
        db.session.commit()
        flash("Registration successful, please log in.")
        return redirect(url_for('login'))
    return render_template('register.html')

# User login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'username' in session and session['username'] == 'Elys':
        flash("Welcome back, Elys!")
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if username == "Elys" and password == "jghd14":
            session['username'] = 'Elys'
            session['user_id'] = 1
            flash("Login successful!")
            return redirect(url_for('index'))

        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['username'] = user.username
            session['subscription_status'] = user.subscription_status
            flash("Login successful!")
            return redirect(url_for('index'))
        else:
            flash("Invalid username or password")
    return render_template('login.html')

# User logout route
@app.route('/logout')
def logout():
    session.clear()
    flash("You have been logged out")
    return redirect(url_for('index'))

# PayPal payment route
@app.route('/pay')
def pay():
    if 'user_id' not in session:
        flash("Please log in to access the PayPal payment page.")
        return redirect(url_for('login'))
    
    if session['username'] == 'Elys':
        flash("Admin does not need to pay.")
        return redirect(url_for('index'))
    
    return render_template('pay.html')

# After PayPal payment (simulated for now)
@app.route('/payment_success')
def payment_success():
    if 'user_id' not in session:
        flash("You must be logged in to access this page.")
        return redirect(url_for('login'))
    
    user = User.query.filter_by(id=session['user_id']).first()
    user.subscription_status = 'premium'
    db.session.commit()
    flash("Payment successful! You now have access to the translation service.")
    return redirect(url_for('index'))

# Define the homepage route
@app.route('/')
def index():
    if 'user_id' not in session:
        flash("Please log in to access translations.")
        return redirect(url_for('login'))
    
    return render_template('index.html', subscription_status=session.get('subscription_status', 'free'))

# Define the search route to handle translation queries
@app.route('/search', methods=['POST'])
def search():
    if 'user_id' not in session:
        flash("Please log in to use the translation service.")
        return redirect(url_for('login'))

    if session['username'] == 'Elys' or session['subscription_status'] == 'premium':
        query = request.form['query']
        direction = request.form['direction']
        
        source_language = direction.split('_')[0] if '_' in direction else direction
        results = translate(query, source_language)

        return render_template('index.html', results=results)
    else:
        flash("You must be a premium user to use the translation service.")
        return redirect(url_for('pay'))

# Privacy Policy route
@app.route('/privacy-policy')
def privacy_policy():
    return render_template('privacy-policy.html')

@app.route('/terms-of-use')
def terms_of_use():
    return render_template('terms-of-use.html')

# Run the app
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
