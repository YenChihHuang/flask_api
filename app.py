from flask import Flask, request, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_marshmallow import Marshmallow
from helpers.token_required import token_required
from models.user import User, UserSchema
from models.todo import Todo, TodoSchema
from config import app_setting
import jwt
import datetime
import uuid

app = Flask(__name__)

app.config['SECRET_KEY'] = app_setting.secret_key
app.config['SQLALCHEMY_DATABASE_URI'] = app_setting.sqlalchemy_database_uri
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = app_setting.sqlalchemy_track_modifications

db = SQLAlchemy(app)

ma = Marshmallow(app)


@app.route('/users', methods=['GET'])
@token_required
def get_users(current_user):
    if not current_user.admin:
        return jsonify({'message': 'Cannot perform that function!'})

    return jsonify(UserSchema(many=True).dump(User.query.all()))


@app.route('/users/<public_id>', methods=['GET'])
@token_required
def get_user(current_user, public_id):
    if not current_user.admin:
        return jsonify({'message': 'Cannot perform that function!'})

    user = User.query.filter_by(public_id=public_id).first()

    if not user:
        return jsonify({'message': 'No user found'})

    return UserSchema().jsonify(user)


@app.route('/users', methods=['POST'])
def create_users():
    new_user = User(
        public_id=str(uuid.uuid4()),
        name=request.json['name'],
        password=generate_password_hash(request.json['password'], method='sha256'),
        admin=True
    )

    db.session.add(new_user)
    db.session.commit()

    return jsonify({'message': 'Created'})


@app.route('/users/<public_id>', methods=['PUT'])
@token_required
def update_user(current_user, public_id):
    if not current_user.admin:
        return jsonify({'message': 'Cannot perform that function!'})

    user = User.query.filter_by(public_id=public_id).first()

    if not user:
        return jsonify({'message': 'No user found'})

    user.name = request.json['name']
    user.admin = request.json['admin']

    db.session.commit()

    return UserSchema().jsonify(user)


@app.route('/users/<public_id>', methods=['DELETE'])
@token_required
def delete_user(current_user, public_id):
    if not current_user.admin:
        return jsonify({'message': 'Cannot perform that function!'})

    user = User.query.filter_by(public_id=public_id).first()

    if not user:
        return jsonify({'message': 'No user found'})

    db.session.delete(user)
    db.session.commit()

    return jsonify({'message': 'Deleted'})


@app.route('/todos', methods=['GET'])
@token_required
def get_todos(current_user):
    return TodoSchema(many=True).jsonify(Todo.query.filter_by(user_id=current_user.id))


@app.route('/todos/<todo_id>', methods=['GET'])
@token_required
def get_todo(current_user, todo_id):
    todo = Todo.query.filter_by(id=todo_id, user_id=current_user.id).first()

    if not todo:
        return jsonify({'message': 'No todo found'})

    return TodoSchema().jsonify(todo)


@app.route('/todos', methods=['POST'])
@token_required
def create_todos(current_user):
    new_todo = Todo(
        text=request.json['text'],
        complete=request.json['complete'],
        user_id=current_user.id
    )

    db.session.add(new_todo)
    db.session.commit()

    return TodoSchema().jsonify(new_todo)


@app.route('/todos/<todo_id>', methods=['PUT'])
@token_required
def update_todo(current_user, todo_id):
    todo = Todo.query.filter_by(id=todo_id, user_id=current_user.id).first()

    if not todo:
        return jsonify({'message': 'No todo found'})

    todo.text = request.json['text']
    todo.complete = request.json['complete']

    db.session.commit()

    return TodoSchema().jsonify(todo)


@app.route('/todos/<todo_id>', methods=['DELETE'])
@token_required
def delete_todo(current_user, todo_id):
    todo = Todo.query.filter_by(id=todo_id, user_id=current_user.id).first()

    if not todo:
        return jsonify({'message': 'No todo found'})

    db.session.delete(todo)
    db.session.commit()

    return jsonify({'message': 'Deleted'})


@app.route('/login')
def login():
    auth = request.authorization

    if not auth or not auth.username or not auth.password:
        return make_response('Could not verify', 401, {'WWW-Authenticat': 'Basic realm="Login required!"'})

    user = User.query.filter_by(name=auth.username).first()

    if not user:
        return make_response('Could not verify', 401, {'WWW-Authenticat': 'Basic realm="Login required!"'})

    if check_password_hash(user.password, auth.password):
        token = jwt.encode({
            'public_id': user.public_id,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
        }, app.config['SECRET_KEY'])

        return jsonify({'token': token})

    return make_response('Could not verify', 401, {'WWW-Authenticat': 'Basic realm="Login required!"'})


if __name__ == '__main__':
    app.run()
