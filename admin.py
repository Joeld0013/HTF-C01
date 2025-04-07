from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv
from datetime import datetime
import os

load_dotenv()

app = Flask(__name__)
CORS(app)

# MySQL connection
def get_connection():
    return mysql.connector.connect(
        host=os.getenv("MYSQL_HOST"),
        user=os.getenv("MYSQL_USER"),
        password=os.getenv("MYSQL_PASSWORD"),
        database=os.getenv("MYSQL_DATABASE")
    )

# API: Add Employee
@app.route('/api/employees', methods=['POST'])
def add_employee():
    data = request.json
    join_date = datetime.now().strftime('%Y-%m-%d')

    try:
        connection = get_connection()
        cursor = connection.cursor()

        query = """
        INSERT INTO users (email, password, role, status, joinDate)
        VALUES (%s, %s, %s, %s, %s)
        """
        values = (data['email'], data['password'], data['role'], 'Active', join_date)
        cursor.execute(query, values)
        connection.commit()

        return jsonify({
            "message": "Employee added successfully",
            "employee": {
                "email": data['email'],
                "role": data['role'],
                "status": "Active",
                "joinDate": join_date
            }
        }), 201

    except Error as e:
        return jsonify({"error": str(e)}), 500

    finally:
        if cursor: cursor.close()
        if connection: connection.close()

# API: Get Employees
@app.route('/api/employees', methods=['GET'])
def get_employees():
    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)

        cursor.execute("SELECT email, role, status, joinDate FROM users")
        employees = cursor.fetchall()

        return jsonify(employees)

    except Error as e:
        return jsonify({"error": str(e)}), 500

    finally:
        if cursor: cursor.close()
        if connection: connection.close()

# Admin UI
@app.route('/')
def serve_admin_page():
    return render_template('admin.html')

# Run Server
if __name__ == '__main__':
    app.run(debug=True, port=5000)
