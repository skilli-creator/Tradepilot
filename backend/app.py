from flask import Flask, request, jsonify
from flask_cors import CORS
from extensions import db, bcrypt

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})   # allow all origins

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://Tonny:%40Babingah91@localhost/tradepilot'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
bcrypt.init_app(app)

from models.user import User

@app.route("/")
def home():
    return {"message": "Backend running with MySQL!"}

# Signup route
@app.route("/signup", methods=["POST"])
def signup():
    data = request.get_json()
    username = data.get("username")
    email = data.get("email")
    password = data.get("password")

    if User.query.filter_by(email=email).first():
        return jsonify({"error": "Email already registered"}), 400

    new_user = User(username=username, email=email)
    new_user.set_password(password)

    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": "User registered successfully"}), 201

# Login route
@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    user = User.query.filter_by(email=email).first()

    if user and user.check_password(password):
        return jsonify({"message": "Login successful"}), 200
    else:
        return jsonify({"error": "Invalid email or password"}), 401

with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(debug=True, port=5000)
