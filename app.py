from flask import Flask, render_template, request, redirect, session,send_from_directory
from db import db  # Import db from the new file
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__)
app.secret_key = '731d8fb1e51c0a88a3340c7a4bb4a404'

# Configuring the SQLite database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///document_wallet.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the database with the app
db.init_app(app)

# Import models AFTER db initialization
from models import User, Document

@app.route('/')
def home():
    return render_template('home.html')  # This will point to a new home.html file

# User login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['username'] = username  # Store username in session
            return redirect('/dashboard')
        return 'Invalid username or password'
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)  # Remove user ID from session
    session.pop('username', None)  # Remove username from session
    return redirect('/login')  # Redirect to login page

# Delete Document Route
@app.route('/delete/<int:document_id>')
def delete_document(document_id):
    if 'user_id' not in session:
        return redirect('/login')
    
    document = Document.query.get(document_id)
    if document:
        db.session.delete(document)
        db.session.commit()
        # Optionally delete the file from the filesystem
        try:
            os.remove(os.path.join('static', document.document_hash))  # Adjust path as needed
        except Exception as e:
            print(f"Error deleting file: {e}")
    return redirect('/dashboard')

# Download Document Route
@app.route('/download/<int:document_id>')
def download_document(document_id):
    if 'user_id' not in session:
        return redirect('/login')

    document = Document.query.get(document_id)
    if document:
        return send_from_directory('static', document.document_hash, as_attachment=True)  # Adjust path as needed
    return 'Document not found', 404

# User registration route
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Check if username already exists
        if User.query.filter_by(username=username).first():
            return 'Username already exists. Please choose a different one.'
        
        # Create new user and hash the password
        new_user = User(username=username, password=password)
        db.session.add(new_user)
        db.session.commit()
        return redirect('/login')  # Redirect to login after successful registration
    
    return render_template('register.html')

# Route to upload document
@app.route('/upload', methods=['GET', 'POST'])
def upload_document():
    if 'user_id' not in session:
        return redirect('/login')

    if request.method == 'POST':
        title = request.form['title']
        file = request.files['document']
        file.save(f'static/{file.filename}')
        document_hash = file.filename  # Simulating IPFS hash with filename
        new_document = Document(title=title, document_hash=document_hash, user_id=session['user_id'])
        db.session.add(new_document)
        db.session.commit()
        return redirect('/dashboard')

    return render_template('upload.html')

# Route to display dashboard
@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect('/login')

    user_id = session['user_id']
    documents = Document.query.filter_by(user_id=user_id).all()
    return render_template('dashboard.html', documents=documents)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Create the database tables
    app.run(debug=True)
