import os
from threading import Thread
from flask import Flask, render_template, session, redirect, url_for
from datetime import datetime
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from wtforms import RadioField
from flask_mail import Mail, Message

import requests

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SECRET_KEY'] = 'hard to guess string'
app.config['SQLALCHEMY_DATABASE_URI'] =\
    'sqlite:///' + os.path.join(basedir, 'data.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['MAIL_SERVER'] = 'smtp.zoho.com'


app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True

app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
app.config['FLASKY_MAIL_SUBJECT_PREFIX'] = '[Flasky]'
app.config['FLASKY_MAIL_SENDER'] = 'flaskaulasweb@zohomail.com'
app.config['FLASKY_ADMIN'] = os.environ.get('FLASKY_ADMIN')

bootstrap = Bootstrap(app)
moment = Moment(app)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
mail = Mail(app)


class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    users = db.relationship('User', backref='role', lazy='dynamic')

    def __repr__(self):
        return '<Role %r>' % self.name


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))

    def __repr__(self):
        return '<User %r>' % self.username
    
class Disciplina(db.Model):
    __tablename__ = 'disciplinas'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(64), unique=True, nullable=False)
    semestre = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f'<Disciplina {self.nome}>'



def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)


def send_email(to, subject, template, **kwargs):
    msg = Message(app.config['FLASKY_MAIL_SUBJECT_PREFIX'] + ' ' + subject,
                  sender=app.config['FLASKY_MAIL_SENDER'], recipients=[to])    
    msg.html = render_template(template + '.html', **kwargs)
    thr = Thread(target=send_async_email, args=[app, msg])
    thr.start()
    return thr

def send_simple_message():
  	return requests.post(
  		"https://api.mailgun.net/v3/sandboxac1a400f6f814141b8b87a5c3d287cc5.mailgun.org/messages",
  		auth=("api", "YOUR_API_KEY"),
  		data={"from": "Excited User <mailgun@sandboxac1a400f6f814141b8b87a5c3d287cc5.mailgun.org>",
  			"to": ["bar@example.com", "YOU@sandboxac1a400f6f814141b8b87a5c3d287cc5.mailgun.org"],
  			"subject": "Hello",
  			"text": "Testing some Mailgun awesomeness!"})


class NameForm(FlaskForm):
    name = StringField('What is your name?', validators=[DataRequired()])
    submit = SubmitField('Submit')

class DisciplinaForm(FlaskForm):
    nome = StringField('Nome da disciplina:', validators=[DataRequired()])
    semestre = RadioField(
        'Semestre',
        choices=[
            ('1', '1º semestre'),
            ('2', '2º semestre'),
            ('3', '3º semestre'),
            ('4', '4º semestre'),
            ('5', '5º semestre'),
            ('6', '6º semestre'),
        ],
        validators=[DataRequired()]
    )
    submit = SubmitField('Cadastrar')


@app.shell_context_processor
def make_shell_context():
    return dict(db=db, User=User, Role=Role)


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500


@app.route('/')
def index():
    return render_template('index.html', current_time=datetime.utcnow())

@app.route('/disciplinas', methods=['GET', 'POST'])
def disciplinas():
    form = DisciplinaForm()

    if form.validate_on_submit():
        nova = Disciplina(nome=form.nome.data, semestre=int(form.semestre.data))
        db.session.add(nova)
        db.session.commit()
        return redirect(url_for('disciplinas'))

    lista = Disciplina.query.order_by(Disciplina.semestre).all()
    return render_template('disciplinas.html', form=form, disciplinas=lista)

@app.route('/professores')
def professores():
    return render_template('nao_disponivel.html', current_time=datetime.utcnow())

@app.route('/alunos')
def alunos():
    return render_template('nao_disponivel.html', current_time=datetime.utcnow())

@app.route('/cursos')
def cursos():
    return render_template('nao_disponivel.html', current_time=datetime.utcnow())

@app.route('/ocorrencias')
def ocorrencias():
    return render_template('nao_disponivel.html', current_time=datetime.utcnow())
