from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from dotenv import load_dotenv
import os

from db import init_db
from routes.user_routes import user_bp

load_dotenv(override=True)
print("MongoDB URI:", os.getenv("MONGO_URI"))

app = Flask(__name__)

# MongoDB configuration
app.config["MONGO_URI"] = os.getenv("MONGO_URI")

# JWT configuration
app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY")
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = 3600

# Check configuration
if not app.config["MONGO_URI"]:
    raise RuntimeError("MongoDB URI is missing in .env")

if not app.config["JWT_SECRET_KEY"]:
    raise RuntimeError("JWT secret key is missing in .env")

# Initialize extensions
CORS(app)
init_db(app)
jwt = JWTManager(app)

# Register user routes
app.register_blueprint(user_bp, url_prefix="/api/users")

@app.route("/", methods=["GET"])
def home():
    return {
        "message": "IndiaEatZ Authentication Backend is Running!"
    }, 200

if __name__ == "__main__":
    app.run(debug=True, port=5000)