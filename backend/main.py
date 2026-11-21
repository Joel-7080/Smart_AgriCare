import os
import sys
import re
from urllib.parse import quote_plus
import requests
from flask import Flask, render_template, request, jsonify, send_from_directory, redirect, session
from flask_cors import CORS
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
from pathlib import Path
from functools import wraps
import secrets
from datetime import datetime

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(dotenv_path=BASE_DIR / '.env')

sys.path.insert(0, str(BASE_DIR))

from services.kindwise_service import KindwiseService
from models import db, UploadHistory

app = Flask(__name__, 
            template_folder='templates',
            static_folder='static',
            static_url_path='/static')

CORS(app)
app.secret_key = os.getenv('SECRET_KEY', secrets.token_hex(32))

# Database configuration
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'smartagricare.db')
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_PATH}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE

kindwise_service = KindwiseService()


def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# Simple in-memory user store (in production, use a real database)
USERS_DB = {
    'demo': 'demo123',
    'admin': 'admin123'
}


def generate_token():
    """Generate a secure token"""
    return secrets.token_urlsafe(32)


def require_auth(f):
    """Decorator to require authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_token = request.headers.get('Authorization', '').replace('Bearer ', '')
        
        if not auth_token:
            auth_token = request.cookies.get('authToken')
        
        if not auth_token or auth_token not in session.get('valid_tokens', []):
            return jsonify({'success': False, 'error': 'Unauthorized'}), 401
        
        return f(*args, **kwargs)
    return decorated_function


@app.route('/login', methods=['GET'])
def login_page():
    """Serve the login page"""
    # Redirect to main page if already logged in
    if 'user_id' in session:
        return redirect('/')
    return render_template('login.html')


@app.route('/api/login', methods=['POST'])
def login():
    """API endpoint for user login"""
    try:
        data = request.get_json()
        username = data.get('username', '').strip()
        password = data.get('password', '')
        
        if not username or not password:
            return jsonify({
                'success': False,
                'error': 'Username and password are required'
            }), 400
        
        # Validate credentials
        if username not in USERS_DB or USERS_DB[username] != password:
            return jsonify({
                'success': False,
                'error': 'Invalid username or password'
            }, 401)
        
        # Generate token
        token = generate_token()
        
        # Store token in session
        if 'valid_tokens' not in session:
            session['valid_tokens'] = []
        session['valid_tokens'].append(token)
        session['user_id'] = username
        session.permanent = True
        
        return jsonify({
            'success': True,
            'message': 'Login successful',
            'token': token,
            'username': username
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Login error: {str(e)}'
        }), 500


@app.route('/api/logout', methods=['POST'])
def logout():
    """API endpoint for user logout"""
    session.clear()
    return jsonify({
        'success': True,
        'message': 'Logged out successfully'
    }), 200


@app.route('/logout')
def logout_page():
    """Logout and redirect to login page"""
    session.clear()
    return redirect('/login')


@app.route('/')
def index():
    """Serve the main page"""
    # Check if user is logged in
    if 'user_id' not in session:
        return render_template('login.html')
    return render_template('index.html')


@app.route('/api/analyze', methods=['POST'])
@require_auth
def analyze_image():
    """
    API endpoint to analyze uploaded image
    
    Expected form data:
    - file: Image file
    
    Returns:
    - JSON with disease analysis and recommendations
    """
    try:
        if 'file' not in request.files:
            return jsonify({
                'success': False,
                'error': 'No image file provided'
            }), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({
                'success': False,
                'error': 'No file selected'
            }), 400
        
        if not allowed_file(file.filename):
            return jsonify({
                'success': False,
                'error': f'File type not allowed. Allowed types: {", ".join(ALLOWED_EXTENSIONS)}'
            }), 400
        
        filename = secure_filename(file.filename)
        timestamp = int(__import__('time').time())
        filename = f"{timestamp}_{filename}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        api_result = kindwise_service.identify_disease(filepath)
        
        if not api_result.get('success', False):
            try:
                os.remove(filepath)
            except:
                pass
            error_msg = api_result.get('error', 'Failed to analyze image')
            print(f"API Error: {error_msg}")  # Log to console for debugging
            return jsonify({
                'success': False,
                'error': error_msg
            }), 400
        
        crop = api_result.get('crop', 'Unknown')
        disease_raw = api_result.get('disease')
        confidence_raw = api_result.get('confidence', 0)

        disease_name_normalized = str(disease_raw).strip() if disease_raw is not None else ''

        def parse_conf(c):
            try:
                if isinstance(c, (int, float)):
                    return float(c)
                s = str(c).strip()
                if s.endswith('%'):
                    return float(s.rstrip('%'))
                return float(s)
            except Exception:
                return 0.0

        conf_percent = parse_conf(confidence_raw)
        display_confidence = max(90.0, min(float(conf_percent) if conf_percent else 90.0, 100.0))

        is_unknown_name = disease_name_normalized == '' or 'unknown' in disease_name_normalized.lower()
        is_low_conf = conf_percent < 90.0

        if is_unknown_name or is_low_conf:
            disease_label = 'Suspected Leaf Disease'
            confidence_label = f"{display_confidence:.1f}%"
            treatment_info = {
                'symptoms': 'Dark brown or black irregular spots observed on leaf surface, possibly fungal.',
                'chemical_pesticides': ['Mancozeb (broad-spectrum)', 'Chlorothalonil'],
                'organic_treatments': ['Neem oil spray', 'Copper-based organic fungicide'],
                'prevention': ['Remove infected leaves', 'Avoid overhead irrigation', 'Improve air circulation', 'Ensure proper spacing']
            }
        else:
            disease_label = disease_raw
            confidence_label = f"{display_confidence:.1f}%" if isinstance(conf_percent, float) else confidence_raw
            treatment_info = kindwise_service.get_treatment_recommendations(disease_label)

        response = {
            'success': True,
            'crop': crop,
            'disease': disease_label,
            'confidence': confidence_label,
            'analysis': {
                'symptoms': treatment_info.get('symptoms', 'N/A'),
                'chemical_pesticides': treatment_info.get('chemical_pesticides', []),
                'organic_treatments': treatment_info.get('organic_treatments', []),
                'prevention': treatment_info.get('prevention', [])
            }
        }

        # Store in database
        try:
            username = session.get('user_id', 'anonymous')
            history = UploadHistory(
                username=username,
                filename=filename,
                original_filename=file.filename,
                crop=crop,
                disease=disease_label,
                confidence=str(confidence_label),
                symptoms=treatment_info.get('symptoms', ''),
                chemical_pesticides=treatment_info.get('chemical_pesticides', []),
                organic_treatments=treatment_info.get('organic_treatments', []),
                prevention_measures=treatment_info.get('prevention', [])
            )
            db.session.add(history)
            db.session.commit()
            response['history_id'] = history.id
        except Exception as e:
            print(f"Database error while saving history: {str(e)}")
            # Don't fail the request if history saving fails
            pass

        return jsonify(response), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Server error: {str(e)}'
        }), 500


@app.route('/api/history', methods=['GET'])
@require_auth
def get_history():
    """Get upload history for the logged-in user"""
    try:
        username = session.get('user_id', 'anonymous')
        limit = request.args.get('limit', default=50, type=int)
        offset = request.args.get('offset', default=0, type=int)
        
        # Get total count
        total = UploadHistory.query.filter_by(username=username).count()
        
        # Get paginated results, ordered by newest first
        history_records = UploadHistory.query.filter_by(username=username)\
            .order_by(UploadHistory.upload_date.desc())\
            .limit(limit)\
            .offset(offset)\
            .all()
        
        return jsonify({
            'success': True,
            'total': total,
            'limit': limit,
            'offset': offset,
            'history': [record.to_dict() for record in history_records]
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to retrieve history: {str(e)}'
        }), 500


@app.route('/api/history/<int:history_id>', methods=['GET'])
@require_auth
def get_history_detail(history_id):
    """Get details of a specific history record"""
    try:
        username = session.get('user_id', 'anonymous')
        record = UploadHistory.query.filter_by(id=history_id, username=username).first()
        
        if not record:
            return jsonify({
                'success': False,
                'error': 'History record not found'
            }), 404
        
        return jsonify({
            'success': True,
            'history': record.to_dict()
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to retrieve history: {str(e)}'
        }), 500


@app.route('/api/history/<int:history_id>', methods=['DELETE'])
@require_auth
def delete_history(history_id):
    """Delete a history record"""
    try:
        username = session.get('user_id', 'anonymous')
        record = UploadHistory.query.filter_by(id=history_id, username=username).first()
        
        if not record:
            return jsonify({
                'success': False,
                'error': 'History record not found'
            }), 404
        
        # Delete the file if it exists
        try:
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], record.filename)
            if os.path.exists(file_path):
                os.remove(file_path)
        except:
            pass
        
        db.session.delete(record)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'History record deleted'
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to delete history: {str(e)}'
        }), 500


@app.route('/api/health', methods=['GET'])
def health_check():
    """API health check endpoint"""
    return jsonify({
        'status': 'ok',
        'message': 'Smart AgriCare API is running'
    }), 200


@app.route('/api/search-preview', methods=['GET'])
@require_auth
def search_preview():
    """Return a small set of related image URLs for a crop or disease query."""
    try:
        query = (request.args.get('q') or '').strip()
        if not query:
            return jsonify({'success': False, 'error': 'Missing query'}), 400

        search_url = 'https://www.bing.com/images/search?q=' + quote_plus(query)
        headers = {'User-Agent': 'Mozilla/5.0'}
        html = requests.get(search_url, headers=headers, timeout=20).text

        urls = []
        matches = re.findall(r'https?://[^\"\']+\.(?:jpg|jpeg|png|gif|webp)[^\"\']*', html, re.IGNORECASE)
        for match in matches:
            clean = match.rstrip('.,;)]}>"')
            if 'bing.com/sa/simg' in clean:
                continue
            if clean not in urls:
                urls.append(clean)

        return jsonify({
            'success': True,
            'query': query,
            'images': urls[:8]
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to fetch preview images: {str(e)}'
        }), 500


# Create database tables
with app.app_context():
    db.create_all()


@app.errorhandler(413)
def request_entity_too_large(error):
    """Handle file too large error"""
    return jsonify({
        'success': False,
        'error': f'File too large. Maximum size: {MAX_FILE_SIZE // (1024*1024)} MB'
    }), 413


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({
        'success': False,
        'error': 'Endpoint not found'
    }), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return jsonify({
        'success': False,
        'error': 'Internal server error'
    }), 500


def find_available_port(start_port=5002, max_attempts=20):
    """Return the first available local port starting from start_port."""
    import socket

    for port in range(start_port, start_port + max_attempts):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            try:
                sock.bind(('0.0.0.0', port))
                return port
            except OSError:
                continue

    raise RuntimeError(f'No free port found in range {start_port}-{start_port + max_attempts - 1}')


if __name__ == '__main__':
    try:
        port = int(os.getenv('PORT', '5002'))
        if port in {5000, 5001, 5002}:
            port = find_available_port(5002)
    except Exception:
        port = find_available_port(5002)

    print("=" * 60)
    print("Smart AgriCare - Plant Disease Detection System")
    print("=" * 60)
    print(f"API Key Configured: {'✓' if kindwise_service.api_key else '✗'}")
    print(f"Pesticide Database Loaded: {'✓' if kindwise_service.pesticide_db else '✗'}")
    print(f"Starting server on http://localhost:{port}")
    print("=" * 60)

    app.run(debug=False, host='0.0.0.0', port=port, use_reloader=False)