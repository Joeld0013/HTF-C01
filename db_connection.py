import mysql.connector
from mysql.connector import Error

# Database configuration
DB_HOST = "localhost"      # Change to your database host
DB_USER = "root"           # Change to your database username
DB_PASS = ""       # Change to your database password
DB_NAME = "workforce"  # Change to your database name

def create_db_connection(host_name, user_name, user_password, db_name):
    """
    Creates and returns a connection to the MySQL database
    """
    connection = None
    try:
        connection = mysql.connector.connect(
            host=host_name,
            user=user_name,
            passwd=user_password,
            database=db_name
        )
        print("MySQL Database connection successful")
    except Error as err:
        print(f"Error: '{err}'")

    return connection

def execute_query(connection, query, params=None):
    """
    Execute SQL queries (INSERT, UPDATE, DELETE)
    """
    cursor = connection.cursor()
    try:
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        connection.commit()
        print("Query successful")
        return True
    except Error as err:
        print(f"Error: '{err}'")
        return False
    finally:
        cursor.close()

def execute_read_query(connection, query, params=None):
    """
    Execute SQL read queries (SELECT)
    """
    cursor = connection.cursor(dictionary=True)
    result = None
    try:
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        result = cursor.fetchall()
        return result
    except Error as err:
        print(f"Error: '{err}'")
        return None
    finally:
        cursor.close()