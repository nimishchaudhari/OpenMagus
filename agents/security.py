import jwt
from functools import wraps
from flask import request, jsonify

# Secret key for JWT encoding/decoding
SECRET_KEY = 'your_secret_key'

# Example capabilities
CAPABILITIES = {
    'read': 'read_access',
    'write': 'write_access',
    'execute': 'execute_access'
}

def generate_token(user_id, capabilities):
    payload = {
        'user_id': user_id,
        'capabilities': capabilities
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
    return token

def decode_token(token):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def has_capability(capability):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            token = request.headers.get('Authorization')
            if not token:
                return jsonify({'message': 'Token is missing'}), 401
            payload = decode_token(token)
            if not payload:
                return jsonify({'message': 'Token is invalid'}), 401
            if capability not in payload['capabilities']:
                return jsonify({'message': 'Insufficient capabilities'}), 403
            return f(*args, **kwargs)
        return decorated_function
    return decorator
