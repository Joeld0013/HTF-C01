from flask import Flask, render_template, send_from_directory
import os
from Dashboard.workforce_dashboard import create_dash_app

# Initialize Flask app
app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Needed for session management

# Configuration
app.config['STATIC_FOLDER'] = 'static'
app.config['TEMPLATES_FOLDER'] = 'templates'

# Serve admin panel
@app.route('/admin')
def admin_panel():
    """Render the main admin HTML interface"""
    return render_template('admin.html')

# Serve static files (CSS/JS)
@app.route('/static/<path:filename>')
def static_files(filename):
    """Serve static files for the admin panel"""
    return send_from_directory(app.config['STATIC_FOLDER'], filename)

# Initialize Dash app
dash_app = create_dash_app(app)

# Health check endpoint
@app.route('/health')
def health_check():
    return {'status': 'healthy'}, 200

if __name__ == '__main__':
    app.run(debug=True, port=8050)