from flask import Flask, request, jsonify
from functools import wraps
from models.user import User
import jwt
from config import app_setting

app = Flask(__name__)

app.config['SECRET_KEY'] = app_setting.secret_key


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']

        if not token:
            return jsonify({'message': 'Token is missing'}), 401

        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])

            current_user = User.query.filter_by(public_id=data['public_id']).first()
        except:
            return jsonify({'message': 'Token is invalid'}), 401

        return f(current_user, *args, **kwargs)

    return decorated


if __name__ == '__main__':
    app.run(debug=True)
