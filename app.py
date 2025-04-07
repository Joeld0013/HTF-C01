from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from pymongo import MongoClient

app = Flask(__name__)
CORS(app)

@app.route('/')
def index():
    return render_template("admin.html")  # Serve login page


if __name__ == '__main__':
    app.run(debug=True)
