from flask import Flask , render_template , json, redirect, url_for, request
from flask_wtf import FlaskForm
from datetime import datetime
from wtforms import BooleanField, PasswordField, StringField, SubmitField, ValidationError
from wtforms.validators import EqualTo, DataRequired, Email, Length
from wtforms.fields.html5 import DateField
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__ , template_folder="Templates")
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SECRET_KEY'] = "please feed us Sarah Mangelsdorf"
db = SQLAlchemy(app)

class Users(db.Model):
	id = db.Column(db.Integer, primary_key = True)
	name = db.Column(db.String(80), nullable = False)
	password = db.Column(db.String(30), nullable = False)
	email = db.Column(db.String(80), nullable = False, unique = True)
	dateOfRegistration = db.Column(db.DateTime, default = datetime.utcnow)
	passwordHash = db.Column(db.String(128))

	@property
	def password(self):
		raise AttributeError('Attribute Error')

	@password.setter
	def password(self, password):
		self.password_hash = generate_password_hash(password)

	def verify_password(self, password):
		return check_password_hash(self.password_hash, password)

class SignUpForm(FlaskForm):
	email = StringField("Email Address", validators=[DataRequired(), Email()])
	passwordHash = PasswordField('Password', validators=[DataRequired(), EqualTo('passwordHashConfirm')])
	passwordHashConfirm = PasswordField('Re-enter your Password', validators=[DataRequired()])
	name = StringField("Name", validators=[DataRequired()])
	submit = SubmitField("Submit")

@app.route('/signup', methods = ['GET', 'POST'])
def signup():
	email = None
	name = None
	form = SignUpForm()
	if form.validate_on_submit():
		user = Users.query.filter_by(email = form.email.data).first()
		if user is None:
			User = users(passwordHash = form.passwordHash.data, name = form.name.data, email = form.email.data)
			db.session.add(user)
			db.session.commit()
		name = form.name.data
		form.name.data = ''
		form.passwordHash.data = ''
		form.email.data = ''
		flash("Sign-Up Successful. Go to the Login In page to acces your account.")
	allUsers = Users.query.order_by(Users.dateOfRegistration)
	return render_template("signup.html", name = name, email = email, form = form, allUsers = allUsers)

