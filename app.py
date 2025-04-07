from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from pymongo import MongoClient

app = Flask(__name__)
CORS(app)

# MongoDB connection
client = MongoClient("mongodb://localhost:27017/")
db = client["admin"]
users_collection = db["users"]

@app.route('/')
def index():
    return render_template("index.html")  # Serve login page

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    print("✅ Received data:", data)

    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({"success": False, "message": "❌ Missing email or password"}), 400

    # Insert into MongoDB
    result = users_collection.insert_one({
        "email": email,
        "password": password,
        "role": "admin"
    })

    print(f"✅ Inserted to DB with ID: {result.inserted_id}")
    return jsonify({"success": True, "message": "✅ Admin credentials stored in MongoDB"})

if __name__ == '__main__':
    app.run(debug=True)
