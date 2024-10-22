from flask import Flask, render_template, request, redirect, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = '731d8fb1e51c0a88a3340c7a4bb4a404'

# Configuring the SQLite database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///document_wallet.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Import models AFTER db initialization to avoid circular import
from models import User, Document

# User login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            return redirect('/dashboard')
        return 'Invalid username or password'
    return render_template('login.html')

# Route to upload document
@app.route('/upload', methods=['GET', 'POST'])
def upload_document():
    if 'user_id' not in session:
        return redirect('/login')

    if request.method == 'POST':
        title = request.form['title']
        file = request.files['document']
        # Here, you would upload the file to IPFS and save the hash in SQLite
        # For now, we'll simulate storing the file locally and save a "fake" hash
        file.save(f'static/{file.filename}')
        document_hash = file.filename  # This would be the IPFS hash in a real app
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
    db.create_all()
    app.run(debug=True)
