from flask_pymongo import PyMongo

mongo = PyMongo()

def init_db(app):
    mongo.init_app(app)

    # Check MongoDB connection
    mongo.cx.admin.command("ping")

print("MongoDB connected successfully!")