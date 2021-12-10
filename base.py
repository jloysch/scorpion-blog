from flask import Flask, render_template , json, redirect, url_for, request, flash, session
from flask_wtf import FlaskForm
from datetime import datetime
from wtforms import BooleanField, PasswordField, StringField, SubmitField, ValidationError
from wtforms.validators import EqualTo, DataRequired, Email, Length
from wtforms import DateField
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user, logout_user
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from wtforms.widgets import TextArea
from flask_recaptcha import ReCaptcha
from itsdangerous import URLSafeTimedSerializer
from decimal import Decimal
import smtplib
import os
import sys


app = Flask(__name__ , template_folder="Templates", static_folder='res')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SECRET_KEY'] = "please feed us Sarah Mangelsdorf"
app.config['RECAPTCHA_SITE_KEY'] = '6Le6an4dAAAAAGq2i0cGerF9vhPuH90KAUauDAc0'
app.config['RECAPTCHA_SECRET_KEY'] = '6Le6an4dAAAAAPshXg_PB29nH3EmWg3sYoGN-zrj'
recaptcha = ReCaptcha(app)
db = SQLAlchemy(app)



loginManager = LoginManager()
loginManager.init_app(app)
loginManager.login_view = 'login'

ts = URLSafeTimedSerializer(app.config["SECRET_KEY"])


@loginManager.user_loader
def load_user(user_id):
	return Users.query.get(int(user_id))

class Users(db.Model, UserMixin):
	#ID autogenerated upon user sign up
	id = db.Column(db.Integer, primary_key = True)
	username = db.Column(db.String(18), nullable = False, unique = True)
	name = db.Column(db.String(80), nullable = False)
	email = db.Column(db.String(80), nullable = False, unique = True)
	dateOfRegistration = db.Column(db.DateTime, default = datetime.utcnow)
	passwordHash = db.Column(db.String(128))

	@property
	def password(self):
		raise AttributeError('Attribute Error')

	@password.setter
	def password(self, password):
		self.passwordHash = generate_password_hash(password)

	def verify_password(self, password):
		return check_password_hash(self.passwordHash, password)

	def __repr__(self):
		return '<Name %r>' % self.name


class SignUpForm(FlaskForm):
	email = StringField("Email Address", validators=[DataRequired(), Email()])
	passwordHash = PasswordField("Password", validators=[DataRequired(), EqualTo('passwordHashConfirm')])
	passwordHashConfirm = PasswordField("Re-enter your Password", validators=[DataRequired()])
	name = StringField("Name", validators=[DataRequired()])
	username = StringField("Username", validators=[DataRequired()])
	submit = SubmitField("Submit")

class LoginForm(FlaskForm):
	email = StringField("Email Address", validators=[DataRequired(), Email()])
	password = PasswordField("Password", validators=[DataRequired()])
	submit = SubmitField("Log In")

class UpdateForm(FlaskForm):
	email = StringField("Email Address", validators=[DataRequired(), Email()])
	name = StringField("Name", validators=[DataRequired()])
	username = StringField("Username", validators=[DataRequired()])
	submit = SubmitField("Update")

class BlogPost(db.Model):
	id = db.Column(db.Integer, primary_key = True)
	postTitle = db.Column(db.String(300))
	article = db.Column(db.Text)
	name = db.Column(db.String(80))
	date = db.Column(db.DateTime, default = datetime.utcnow)

class StoreMerch(db.Model):
	id = db.Column(db.Integer, primary_key = True)
	name = db.Column(db.String(300))
	cost = db.Column(db.Numeric(3,2))

class Cart(db.Model):
	uid = db.Column(db.Integer, primary_key = True)
	items = db.Column(db.String(300))
	quantities = db.Column(db.String(300))
	sizes = db.Column(db.String(300))

class CartItem():
	itemId = -1
	itemName = "shirt"
	quantity = -1
	size = -1
	cost = 0.00

class BlogPostForm(FlaskForm):
	postTitle = StringField("Title", validators = [DataRequired()])
	name = StringField("Name", validators = [DataRequired()])
	article = StringField("Body", validators = [DataRequired()], widget = TextArea())
	submit = SubmitField("Publish Post")

class EmailList(db.Model):
	id = db.Column(db.Integer, primary_key = True)
	fname = db.Column(db.String(80))
	lname = db.Column(db.String(80))
	email = db.Column(db.String(80))

class EmailListForm(FlaskForm):
	fname = StringField("First Name", validators=[DataRequired()])
	lname = StringField("Last Name", validators=[DataRequired()])
	email = StringField("Email Address", validators=[DataRequired(), Email()])
	submit = SubmitField("Subscribe")

@app.route('/signup', methods = ['GET', 'POST'])
def signup():
	name = None
	form = SignUpForm()

	if form.validate_on_submit():

		if recaptcha.verify():
			#checks to make sure the user's email is not in the database, should return None if the email is unique
			user = Users.query.filter_by(email = form.email.data).first()

			if user is None:
			#line below is hashing the password with sha256 and returning the hash to the database
				hashedPassword = generate_password_hash(form.passwordHash.data, "sha256")
				user = Users(username = form.username.data, passwordHash = hashedPassword, name = form.name.data, email = form.email.data)
				
				db.session.add(user)
				db.session.commit()
				flash("Sign-Up Successful. Go to the Login In page to acces your account.")
				return redirect(url_for('login'))
			else:
				flash("There is already a user with this email. Try again.")
			name = form.name.data
			form.name.data = ''
			form.passwordHash.data = ''
			form.email.data = ''
			form.username.data = ''
		else:
			flash("Please fill out the captcha and try again.")
	else:
		flash("!form.validate_..")

	allUsers = Users.query.order_by(Users.dateOfRegistration)
	return render_template("signup.html", name = name, form = form, allUsers = allUsers, signupHeader=("Dashboard" if current_user.is_authenticated else "Login/Sign-Up"))

@app.route('/login', methods = ['GET', 'POST'])
def login():
	error = None
	form = LoginForm()
	#flash("HEHE")

	if request.method == 'POST':
		if form.validate_on_submit():

		#returns the first result of a user with the email entered (should be only one instance though), if user doesn't exist then returns nothing'
			user = Users.query.filter_by(email = form.email.data).first()

			if user:
				if check_password_hash(user.passwordHash, form.password.data):
					login_user(user)
					print('Logging in', file=sys.stdout)
					return redirect(url_for('dashboard'))
				else:
					print('Password wrong', file=sys.stdout)
					flash("Wrong Password")
			else:
				print('Bad email', file=sys.stdout)
				flash("Email not linked to an account")
		else:
			print('Bad mix', file=sys.stdout)
			flash("Invalid information. Please try again.")

	if current_user.is_authenticated:
		return redirect(url_for("dashboard"))
	else:
		return render_template("login.html", form = form, signupHeader=("Dashboard" if current_user.is_authenticated else "Login/Sign-Up"))

@app.route('/dashboard', methods = ['GET', 'POST'])
@login_required
def dashboard():
	return render_template("dashboard.html", signupHeader=("Dashboard" if current_user.is_authenticated else "Login/Sign-Up"))

@app.route('/updateinfo/<int:id>', methods = ['GET', 'POST'])
@login_required
def updateinfo(id):
	form = UpdateForm()
	user = Users.query.get_or_404(id)

	if form.validate_on_submit():
		user.name = request.form['name']
		user.email = request.form['email']
		user.username = request.form['username']
		db.session.commit()
		flash("User Updated Successfully")
		return render_template("updateinfo.html", form = form, user = user, signupHeader=("Dashboard" if current_user.is_authenticated else "Login/Sign-Up"))
	else:
		flash("Invalid Form. Please Try Again.")
		return render_template("updateinfo.html", form = form, user = user, signupHeader=("Dashboard" if current_user.is_authenticated else "Login/Sign-Up"))

@app.route('/publish', methods = ['GET', 'POST'])
@login_required
def publish():
	form = BlogPostForm()
	if form.validate_on_submit():
		if recaptcha.verify():
			blogPost = BlogPost(postTitle = form.postTitle.data, name = form.name.data, article = form.article.data)
			form.postTitle.data = ''
			form.name.data = ''
			form.article.data = ''
			db.session.add(blogPost)
			db.session.commit()
			flash("Your Post was Successfully Published")
			return redirect(url_for('allposts'))
		else:
			flash("Please fill out the captcha.")
	else:
		flash("Post not published, please try fill in all information.")
	return render_template("createpostform.html", form = form, signupHeader=("Dashboard" if current_user.is_authenticated else "Login/Sign-Up"))

@app.route('/allposts')
def allposts():
	allPosts = BlogPost.query.order_by(BlogPost.date)
	return render_template("allposts.html", allPosts = allPosts, signupHeader=("Dashboard" if current_user.is_authenticated else "Login/Sign-Up"))

@app.route('/userpost/<int:id>')
def userpost(id):
	blogPost = BlogPost.query.get_or_404(id)
	return render_template('userpost.html', blogPost = blogPost, signupHeader=("Dashboard" if current_user.is_authenticated else "Login/Sign-Up"))

@app.route('/aboutus')
def aboutus():
	return render_template('aboutus.html')

@app.route('/subscribe', methods = ['GET', 'POST'])
def subscribe():
	form = EmailListForm()

	if form.validate_on_submit():
		recipient = EmailList(fname = form.fname.data, lname = form.lname.data, email = form.email.data)
		form.fname.data = ''
		form.lname.data = ''
		form.email.data = ''
		db.session.add(recipient)
		db.session.commit()
		flash("Successfully Subscribed to Email List")
	else:
		flash("Information Invalid")
	return render_template('subscribe.html', form = form, signupHeader=("Dashboard" if current_user.is_authenticated else "Login/Sign-Up"))


@app.route('/', methods = ['GET', 'POST'])
def generateLandingPage():
	return render_template("home.html", signupHeader=("Dashboard" if current_user.is_authenticated else "Login/Sign-Up"))

@app.route('/giles', methods = ['GET', 'POST'])
def generateStaticGiles():
	return render_template("giles.html", signupHeader=("Dashboard" if current_user.is_authenticated else "Login/Sign-Up"))

@app.route('/loysch', methods = ['GET', 'POST'])
def generateStaticLoysch():
	return render_template("loysch.html", signupHeader=("Dashboard" if current_user.is_authenticated else "Login/Sign-Up"))

@app.route('/emersyn', methods = ['GET', 'POST'])
def generateStaticEmersyn():
	return render_template("emersyn.html", signupHeader=("Dashboard" if current_user.is_authenticated else "Login/Sign-Up"))

@app.route('/posts', methods = ['GET', 'POST'])
def generatePostsPage():
	posts = BlogPost.query.order_by(BlogPost.date)
	return render_template("member.html", posts = posts, signupHeader=("Dashboard" if current_user.is_authenticated else "Login/Sign-Up"))

'''
@app.route('/store', methods = ['GET', 'POST'])
def generateStorePage():
	return render_template("store.html")
'''


def wrapDelimitedStr(strArray, delim):
	t = ""
	for n in strArray:
		t+=n
		t+=delim
	return t

def out(str):
	print(str, file=sys.stdout)
	
@app.route('/store', methods = ['GET', 'POST'])
def generateStorePage():

	if request.method == 'POST':
		#Add to the database 
		#print('POSTED!', file=sys.stdout)
		#flash("OK")
		#return render_tempalte("home.html")

		#checks to make sure the user's email is not in the database, should return None if the email is unique
		#print(current_user.id, file=sys.stdout)

		items = StoreMerch.query.order_by(StoreMerch.id)

		if not current_user.is_authenticated:
			flash("Please log in to save your cart!", 'store')
			return render_template("store.html", items = items, signupHeader=("Dashboard" if current_user.is_authenticated else "Login/Sign-Up"))

		cart = Cart.query.filter_by(uid=current_user.id).first()

		

		out(request.form.get('quantity'))
		out(request.form.get('size'))

		

		if cart is not None:

			#trim extra comma
			
			newItems = cart.items.split(',')
			newItems = newItems[0:len(newItems)-1]
			newQuantities = cart.quantities.split(',')
			newQuantities = newQuantities[0:len(newQuantities)-1]
			sizes = cart.sizes.split(',')
			sizes = sizes[0:len(sizes)-1]

			newItems.append(request.values.get('merchId').strip("}"))
			newQuantities.append(request.form.get('quantity'))
			sizes.append(request.form.get('size'))

			#print("\n\n\n\n", file=sys.stdout)
			#print(request.form.get('quantity'), file=sys.stdout)
			#print("\n\n\n\n", file=sys.stdout)

			cart.items = wrapDelimitedStr(newItems, ',')
			cart.quantities = wrapDelimitedStr(newQuantities, ',')
			cart.sizes = wrapDelimitedStr(sizes, ',')
			#out("")
			#out("")
			#out(request.values.get('merchId'))
			#out(request.values.get('quantity'))
			#out(request.values.get('size'))
			#out("")
			#out("")

			#out(request.values)
			#db.sesion.update()

		else:

			na = request.values.get('merchId').strip("}")
			nb = request.form.get('quantity')
			nc = request.form.get('size')
			na += ','
			nb += ','
			nc += ','

			
			if request.form.get('size') == "0":
				out("ZERO SIZE")
				flash("Please enter a size!", 'store')
				return render_template("store.html", items = items, signupHeader=("Dashboard" if current_user.is_authenticated else "Login/Sign-Up"))

			if request.form.get('quantity') == "0":
				out("ZERO QUANTITY")
				flash("Please enter a quantity!", 'store')
				return render_template("store.html", items = items, signupHeader=("Dashboard" if current_user.is_authenticated else "Login/Sign-Up"))

			


			cart = Cart(uid = current_user.id, items=na, quantities=nb, sizes=nc)

			db.session.add(cart)
			
		

		#db.session.add(cart)
		#db.session.commit()
		#flash("Sign-Up Successful. Go to the Login In page to acces your account.")
		#return redirect(url_for('generateCartPage'))
				


	items = StoreMerch.query.order_by(StoreMerch.id)

	if request.form.get('size') == "0":
		out("ZERO SIZE")
		flash("Please enter a size!", 'store')
		return render_template("store.html", items = items, signupHeader=("Dashboard" if current_user.is_authenticated else "Login/Sign-Up"))

	if request.form.get('quantity') == "0":
		out("ZERO QUANTITY")
		flash("Please enter a quantity!", 'store')
		return render_template("store.html", items = items, signupHeader=("Dashboard" if current_user.is_authenticated else "Login/Sign-Up"))

	db.session.commit()

	return render_template("store.html", items = items, signupHeader=("Dashboard" if current_user.is_authenticated else "Login/Sign-Up"))

'''

class Cart(db.Model):
	uid = db.Column(db.Integer, primary_key = True)
	items = db.Column(db.String(300))
	quantities = db.Column(db.String(300))
	sizes = db.Column(db.String(300))

class CartItem():
	itemId = -1
	quantity = -1
	size = -1


'''

@app.route('/mycart', methods = ['GET', 'POST'])
def generateCartPage():

	cart = Cart.query.filter_by(uid=current_user.id).first()

	displayItems = []

	#pretrim extra delimiter

	if cart is not None:

		#out(cart.items)
		#out(cart.quantities)

		#trim extra comma
		items = cart.items.split(',')
		items = items[0:len(items)-1]
		quantities = cart.quantities.split(',')
		quantities=quantities[0:len(quantities)-1]
		sizes = cart.sizes.split(',')
		sizes = sizes[0:len(sizes)-1]

		#[x,o,o]
		#[x,o,o]
		#[x,o,o]

		if len(items) > 0:

			for i in range(len(items)):

				ct = CartItem()

				if items[i] is not None:

					queriedMerch = StoreMerch.query.filter_by(id=items[i]).first()

					ct.itemId = items[i]
					ct.quantity = quantities[i]
					ct.size = sizes[i]
					#ct.cost = float(str(float(StoreMerch.query.filter_by(id=items[i]).first().cost) * float(quantities[i])).format())
					
					#out("")
					#out("-->\n\n")
					#out(items[i])
					#out("\n")
					#out((StoreMerch.query.filter_by(id=items[i]).first()))
					#out("<--\n\n")

					ct.cost = queriedMerch.cost * Decimal(quantities[i])

					ct.itemName = queriedMerch.name

					displayItems.append(ct)


	if request.method == 'POST':
		out('Request from -->')
		out(request.form.get('itemIdentifier'))
		out("\n---")

		#userRemoveItemFromCart(request.form.get('itemIdentifier'))

		itemId = request.form.get('itemIdentifier')

		cart = Cart.query.filter_by(uid=current_user.id).first()

		#trim extra comma
		items = cart.items.split(',')
		items = items[0:len(items)-1]
		quantities = cart.quantities.split(',')
		quantities=quantities[0:len(quantities)-1]
		sizes = cart.sizes.split(',')
		sizes = sizes[0:len(sizes)-1]

		newItems = []
		newQuantities = []
		newSizes = []

		cartDisplayItems = []

		for i in range(len(items)):

			
			if itemId != (str(items[i]+""+quantities[(i)]+""+sizes[(i)])):

				out(items[int(i)])
				out("^\n")
				queriedMerch = StoreMerch.query.filter_by(id=items[int(i)]).first()

				ct = CartItem()

				newItems.append(items[i])
				newQuantities.append(quantities[(i)])
				newSizes.append(sizes[(i)])

				ct.itemId = items[i]
				ct.quantity = quantities[(i)]
				ct.size = sizes[(i)]

				ct.cost = queriedMerch.cost * Decimal(quantities[(i)])

				ct.itemName = queriedMerch.name

				cartDisplayItems.append(ct)


		if (len(newItems) == 0):
			Cart.query.filter(Cart.uid == current_user.id).delete()
			db.session.commit()
			out("OKAY ALL DELETED!")
			return redirect(url_for('generateStorePage'))


		a = wrapDelimitedStr(newItems, ',')
		b = wrapDelimitedStr(newQuantities, ',')
		c = wrapDelimitedStr(newSizes, ',')

		cart.items = a
		cart.quantities = b
		cart.sizes = c

		db.session.commit()

		return render_template('cart.html', displayItems = cartDisplayItems, signupHeader=("Dashboard" if current_user.is_authenticated else "Login/Sign-Up"))


			

	if cart is not None:
		return render_template("cart.html", displayItems=displayItems, signupHeader=("Dashboard" if current_user.is_authenticated else "Login/Sign-Up"))
	else:
		flash("Your cart is empty! Please add some items.", 'store')
		return redirect(url_for('generateStorePage'))



#Error Handlers
@app.errorhandler(404)
def page_not_found(e):
	return render_template('error404.html'), 404

@app.errorhandler(500)
def page_not_found(e):
	return render_template('error500.html'), 500