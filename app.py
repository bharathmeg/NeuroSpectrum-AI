from flask import Flask, render_template, request, redirect, session
import os
import pickle
import numpy as np
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
import bcrypt
from profiler import generateProfile

app = Flask(__name__)
port = int(os.getenv('PORT', 5000))

app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///Model.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = '1A2bc4s'

db = SQLAlchemy(app)

# ===============================
# DATABASE MODEL
# ===============================
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(128), unique=True, nullable=False)
    email = db.Column(db.String(128), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)

with app.app_context():
    db.create_all()

# ===============================
# ROUTES
# ===============================
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/model')
def model_page():
    return render_template("model.html")

@app.route('/about')
def about():
    return render_template("about.html")

@app.route('/result')
def result():
    return render_template("result_train.html")

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

@app.route('/predict', methods=['GET'])
def predict():
    return render_template('predict.html')

# ===============================
# MAIN OUTPUT ROUTE (UPDATED)
# ===============================
@app.route('/output', methods=['POST'])
def output():
    model = pickle.load(open('./static/Models/autism_model.pkl', 'rb'))

    int_features = [int(x) for x in request.form.values()]
    final_features = np.array(int_features).reshape(1, -1)

    probability = model.predict_proba(final_features)[0][1]

    if probability < 0.20:
        status = "No Autism"
        risk = "Very Low"
        precautions = [
            "Monitor social and communication development",
            "Encourage interactive play and storytelling",
            "Maintain regular pediatric check-ups",
            "Ensure healthy sleep and nutrition",
            "No immediate clinical intervention required"
        ]

    elif probability < 0.40:
        status = "No Autism"
        risk = "Low "
        precautions = [
            "Observe speech and social milestones",
            "Encourage group play and communication",
            "Limit excessive screen time",
            "Consult pediatrician if concerns persist",
            "Periodic behavioral monitoring recommended"
        ]

    elif probability < 0.70:
        status = "Autism Detected"
        risk = "Medium "
        precautions = [
            "Consult a pediatric specialist",
            "Speech and language therapy assessment",
            "Monitor behavior at home and school",
            "Maintain structured daily routines",
            "Early intervention programs recommended"
        ]

    else:
        status = "Autism Detected"
        risk = "High"
        precautions = [
            "Immediate consultation with child psychologist",
            "Comprehensive autism diagnostic evaluation",
            "Begin early intervention therapies",
            "Parent counseling and caregiver training",
            "Continuous developmental monitoring"
        ]

    confidence = round(probability * 100, 2)

    data = request.form.to_dict()
    profile = generateProfile(data)

    return render_template(
        'output.html',
        status=status,
        risk=risk,
        confidence=confidence,
        precautions=precautions,
        profile=profile
    )

# ===============================
# REGISTER
# ===============================
@app.route('/register', methods=['POST'])
def register():
    username = request.form.get('name')
    email = request.form.get('email')
    newPass = request.form.get('newPass')
    confPass = request.form.get('confPass')

    if not username or not email or not newPass or not confPass:
        return render_template('login.html', error="Please fill all fields")

    if newPass != confPass:
        return render_template('login.html', regError="Passwords do not match")

    try:
        salt = bcrypt.gensalt()
        password_hash = bcrypt.hashpw(newPass.encode('utf-8'), salt)
        new_user = User(username=username, email=email, password=password_hash)
        db.session.add(new_user)
        db.session.commit()
        return redirect('/login')
    except IntegrityError:
        return render_template('login.html', regError="Username or email already exists")

# ===============================
# LOGIN
# ===============================
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')

    username = request.form.get('username')
    password = request.form.get('password')

    if not username or not password:
        return render_template('login.html', loginError="Enter all fields")

    user = User.query.filter_by(username=username).first()
    if not user:
        return render_template('login.html', loginError="User not found")

    if bcrypt.checkpw(password.encode('utf-8'), user.password):
        session['logged'] = True
        session['userId'] = user.id
        return redirect('/predict')
    else:
        return render_template('login.html', loginError="Incorrect password")

# ===============================
# RUN APP
# ===============================
if __name__ == '__main__':
    app.run(debug=True, port=port)
