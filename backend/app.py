from flask import Flask, request, jsonify, url_for
from flask_cors import CORS
from backend.extensions import db, bcrypt, mail
import itsdangerous
from flask_mail import Message

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})   # allow all origins

# Database config
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://Tonny:%40Babingah91@localhost/tradepilot'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Secret key for tokens
app.secret_key = "supersecretkey"   # change this to a secure random key

# Mail config (using Gmail SMTP as example)
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['Tonny Kyalo'] = 'tonnykyalo054@gmail.com'        # replace with your Gmail
app.config['MAIL_PASSWORD'] = 'your-app-password'          # use Gmail App Password
app.config['MAIL_DEFAULT_SENDER'] = 'yourgmail@gmail.com'  # sender address

# Init extensions
db.init_app(app)
bcrypt.init_app(app)
mail.init_app(app)

from backend.models.user import User

# Serializer for email confirmation tokens
serializer = itsdangerous.URLSafeTimedSerializer(app.secret_key)

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

    new_user = User(username=username, email=email, verified=False)
    new_user.set_password(password)

    db.session.add(new_user)
    db.session.commit()

    # Generate confirmation token
    token = serializer.dumps(email, salt="email-confirm")
    confirm_url = url_for("confirm_email", token=token, _external=True)

    # Send confirmation email
    msg = Message("Confirm Your Tradepilot Account", recipients=[email])
    msg.body = f"Hi {username},\n\nPlease confirm your account by clicking this link:\n{confirm_url}\n\nThanks!"
    mail.send(msg)

    return jsonify({
        "message": "User registered successfully. Please check your email to confirm your account."
    }), 201

# Email confirmation route
@app.route("/confirm/<token>")
def confirm_email(token):
    try:
        email = serializer.loads(token, salt="email-confirm", max_age=3600)
    except:
        return jsonify({"error": "Invalid or expired token"}), 400

    user = User.query.filter_by(email=email).first()
    if user:
        user.verified = True
        db.session.commit()
        return jsonify({"message": "Email verified successfully!"}), 200
    else:
        return jsonify({"error": "User not found"}), 404

# Login route
@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    user = User.query.filter_by(email=email).first()

    if not user:
        return jsonify({"error": "Invalid email or password"}), 401

    if not user.verified:
        return jsonify({"error": "Email not verified"}), 403

    if user.check_password(password):
        return jsonify({
            "message": "Login successful",
            "username": user.username
        }), 200
    else:
        return jsonify({"error": "Invalid email or password"}), 401

with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(debug=True, port=5000, host="0.0.0.0")
