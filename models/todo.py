from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from config import app_setting

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = app_setting.sqlalchemy_database_uri
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = app_setting.sqlalchemy_track_modifications

db = SQLAlchemy(app)

ma = Marshmallow(app)


class Todo(db.Model):
    __tablename__ = 'todos'
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(50))
    complete = db.Column(db.Boolean)
    user_id = db.Column(db.Integer)


class TodoSchema(ma.Schema):
    class Meta:
        fields = ('id', 'text', 'complete', 'user_id')


db.create_all()


if __name__ == '__main__':
    app.run()
