"""
Vulnerable Flask Application - For Security Testing Demo
WARNING: This application contains intentional vulnerabilities for educational purposes.
DO NOT deploy this in production!
"""

from flask import Flask, request, render_template_string, redirect
import sqlite3
import os
import subprocess
import hashlib

app = Flask(__name__)

# VULNERABILITY: Hardcoded credentials (Bandit B105, B106)
DATABASE_PASSWORD = "admin123"
SECRET_KEY = "super_secret_key_12345"
API_KEY = "sk-1234567890abcdef"

app.secret_key = SECRET_KEY

def get_db_connection():
    """Create database connection"""
    conn = sqlite3.connect('users.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize database with sample data"""
    conn = get_db_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            username TEXT NOT NULL,
            password TEXT NOT NULL,
            email TEXT
        )
    ''')
    conn.execute("INSERT OR IGNORE INTO users (id, username, password, email) VALUES (1, 'admin', 'admin123', 'admin@example.com')")
    conn.execute("INSERT OR IGNORE INTO users (id, username, password, email) VALUES (2, 'user', 'password', 'user@example.com')")
    conn.commit()
    conn.close()

@app.route('/')
def index():
    """Home page"""
    html = '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Vulnerable App - Security Demo</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; background: #1a1a2e; color: #eee; }
            .container { max-width: 800px; margin: 0 auto; }
            h1 { color: #e94560; }
            .warning { background: #ff6b6b; color: white; padding: 15px; border-radius: 5px; margin: 20px 0; }
            a { color: #0f3460; background: #e94560; padding: 10px 20px; text-decoration: none; border-radius: 5px; display: inline-block; margin: 5px; }
            a:hover { background: #ff6b6b; }
            .endpoint { background: #16213e; padding: 20px; margin: 10px 0; border-radius: 10px; }
            code { background: #0f3460; padding: 2px 8px; border-radius: 3px; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🔓 Vulnerable Application</h1>
            <div class="warning">
                ⚠️ WARNING: This application contains intentional security vulnerabilities for testing purposes only!
            </div>
            <h2>Available Endpoints:</h2>
            <div class="endpoint">
                <h3>1. SQL Injection</h3>
                <p>Try: <code>/user?id=1 OR 1=1</code></p>
                <a href="/user?id=1">Test User Lookup</a>
            </div>
            <div class="endpoint">
                <h3>2. Command Injection</h3>
                <p>Try: <code>/ping?host=localhost; whoami</code></p>
                <a href="/ping?host=localhost">Test Ping</a>
            </div>
            <div class="endpoint">
                <h3>3. XSS (Cross-Site Scripting)</h3>
                <p>Try: <code>/search?q=&lt;script&gt;alert('XSS')&lt;/script&gt;</code></p>
                <a href="/search?q=test">Test Search</a>
            </div>
            <div class="endpoint">
                <h3>4. Weak Password Hashing</h3>
                <p>Uses MD5 instead of bcrypt</p>
                <a href="/hash?password=test123">Test Hash</a>
            </div>
            <div class="endpoint">
                <h3>5. Debug Information</h3>
                <a href="/debug">View Debug Info</a>
            </div>
        </div>
    </body>
    </html>
    '''
    return html


@app.route('/user')
def get_user():
    """
    VULNERABILITY: SQL Injection (Bandit B608)
    User input is directly concatenated into SQL query
    """
    user_id = request.args.get('id', '1')
    conn = get_db_connection()
    
    # VULNERABLE: Direct string concatenation in SQL query
    query = f"SELECT * FROM users WHERE id = {user_id}"
    
    try:
        result = conn.execute(query).fetchone()
        conn.close()
        
        if result:
            return f'''
            <html><body style="background:#1a1a2e;color:#eee;font-family:Arial;padding:40px;">
            <h2>User Found</h2>
            <p>ID: {result['id']}</p>
            <p>Username: {result['username']}</p>
            <p>Email: {result['email']}</p>
            <a href="/" style="color:#e94560;">Back</a>
            </body></html>
            '''
        else:
            return '<html><body style="background:#1a1a2e;color:#eee;padding:40px;">User not found <a href="/" style="color:#e94560;">Back</a></body></html>'
    except Exception as e:
        return f'<html><body style="background:#1a1a2e;color:#eee;padding:40px;">Error: {str(e)} <a href="/" style="color:#e94560;">Back</a></body></html>'


@app.route('/ping')
def ping():
    """
    VULNERABILITY: Command Injection (Bandit B602, B605)
    User input is passed directly to shell command
    """
    host = request.args.get('host', 'localhost')
    
    # VULNERABLE: Shell injection via subprocess
    command = f"ping -n 1 {host}"
    
    try:
        # Using shell=True with user input - dangerous!
        result = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT, timeout=5)
        output = result.decode('utf-8', errors='ignore')
    except subprocess.TimeoutExpired:
        output = "Command timed out"
    except Exception as e:
        output = f"Error: {str(e)}"
    
    return f'''
    <html><body style="background:#1a1a2e;color:#eee;font-family:Arial;padding:40px;">
    <h2>Ping Result for: {host}</h2>
    <pre style="background:#0f3460;padding:20px;border-radius:10px;overflow:auto;">{output}</pre>
    <a href="/" style="color:#e94560;">Back</a>
    </body></html>
    '''


@app.route('/search')
def search():
    """
    VULNERABILITY: Cross-Site Scripting (XSS)
    User input is rendered without escaping
    """
    query = request.args.get('q', '')
    
    # VULNERABLE: Rendering user input directly in HTML
    html = f'''
    <html><body style="background:#1a1a2e;color:#eee;font-family:Arial;padding:40px;">
    <h2>Search Results</h2>
    <p>You searched for: {query}</p>
    <p>No results found for your query.</p>
    <a href="/" style="color:#e94560;">Back</a>
    </body></html>
    '''
    return render_template_string(html)


@app.route('/hash')
def weak_hash():
    """
    VULNERABILITY: Weak cryptographic hash (Bandit B303, B324)
    Using MD5 for password hashing instead of bcrypt/argon2
    """
    password = request.args.get('password', 'default')
    
    # VULNERABLE: Using MD5 for password hashing
    hashed = hashlib.md5(password.encode()).hexdigest()
    
    # Also demonstrating SHA1 (also weak for passwords)
    sha1_hashed = hashlib.sha1(password.encode()).hexdigest()
    
    return f'''
    <html><body style="background:#1a1a2e;color:#eee;font-family:Arial;padding:40px;">
    <h2>Password Hash Demo</h2>
    <p>Original: {password}</p>
    <p>MD5 Hash: <code style="background:#0f3460;padding:5px;">{hashed}</code></p>
    <p>SHA1 Hash: <code style="background:#0f3460;padding:5px;">{sha1_hashed}</code></p>
    <p style="color:#ff6b6b;">⚠️ Warning: MD5 and SHA1 are NOT suitable for password hashing!</p>
    <a href="/" style="color:#e94560;">Back</a>
    </body></html>
    '''


@app.route('/debug')
def debug_info():
    """
    VULNERABILITY: Information disclosure
    Exposing sensitive debug information
    """
    # VULNERABLE: Exposing sensitive configuration
    debug_data = {
        'database_password': DATABASE_PASSWORD,
        'secret_key': SECRET_KEY,
        'api_key': API_KEY,
        'environment': dict(os.environ),
        'python_path': os.sys.path,
    }
    
    env_html = '<br>'.join([f'{k}: {v}' for k, v in list(debug_data['environment'].items())[:10]])
    
    return f'''
    <html><body style="background:#1a1a2e;color:#eee;font-family:Arial;padding:40px;">
    <h2>🔧 Debug Information</h2>
    <div style="background:#ff6b6b;color:white;padding:15px;border-radius:5px;margin:20px 0;">
        ⚠️ DANGER: Sensitive information exposed!
    </div>
    <h3>Credentials:</h3>
    <pre style="background:#0f3460;padding:20px;border-radius:10px;">
Database Password: {DATABASE_PASSWORD}
Secret Key: {SECRET_KEY}
API Key: {API_KEY}
    </pre>
    <h3>Environment (first 10):</h3>
    <pre style="background:#0f3460;padding:20px;border-radius:10px;overflow:auto;">{env_html}</pre>
    <a href="/" style="color:#e94560;">Back</a>
    </body></html>
    '''


@app.route('/admin')
def admin_panel():
    """Admin panel without authentication"""
    return '''
    <html><body style="background:#1a1a2e;color:#eee;font-family:Arial;padding:40px;">
    <h2>🔐 Admin Panel</h2>
    <p>Welcome, Administrator!</p>
    <p style="color:#ff6b6b;">⚠️ No authentication required - vulnerability!</p>
    <a href="/" style="color:#e94560;">Back</a>
    </body></html>
    '''


if __name__ == '__main__':
    init_db()
    # VULNERABILITY: Debug mode enabled in production (Bandit B201)
    app.run(host='0.0.0.0', port=5000, debug=True)
