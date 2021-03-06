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
	articles = db.relationship('BlogPost', backref = 'author')

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
	userID = db.Column(db.Integer, db.ForeignKey('users.id'))

class BlogPostForm(FlaskForm):
	postTitle = StringField("Title", validators = [DataRequired()])
	name = StringField("Name", validators = [DataRequired()])
	article = StringField("Body", validators = [DataRequired()], widget = TextArea())
	submit = SubmitField("Publish Post")

#Emersyn's blog posts
class EmersynPost(db.Model):
	id = db.Column(db.Integer, primary_key = True)
	postTitle = db.Column(db.String(300))
	article = db.Column(db.Text)
	name = db.Column(db.String(80))
	date = db.Column(db.DateTime, default = datetime.utcnow)

class EmersynPostForm(FlaskForm):
	postTitle = StringField("Title", validators = [DataRequired()])
	name = StringField("Name", validators = [DataRequired()])
	article = StringField("Body", validators = [DataRequired()], widget = TextArea())
	submit = SubmitField("Publish Post")

#Giles's blog posts
class GilesPost(db.Model):
	id = db.Column(db.Integer, primary_key = True)
	postTitle = db.Column(db.String(300))
	article = db.Column(db.Text)
	name = db.Column(db.String(80))
	date = db.Column(db.DateTime, default = datetime.utcnow)

class GilesPostForm(FlaskForm):
	postTitle = StringField("Title", validators = [DataRequired()])
	name = StringField("Name", validators = [DataRequired()])
	article = StringField("Body", validators = [DataRequired()], widget = TextArea())
	submit = SubmitField("Publish Post")

#Josh's blog posts
class JoshPost(db.Model):
	id = db.Column(db.Integer, primary_key = True)
	postTitle = db.Column(db.String(300))
	article = db.Column(db.Text)
	name = db.Column(db.String(80))
	date = db.Column(db.DateTime, default = datetime.utcnow)

class JoshPostForm(FlaskForm):
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

class EmailForm(FlaskForm):
	email = StringField("Email Address", validators=[DataRequired(), Email()])
	submit = SubmitField("Submit")

class PasswordResetForm(FlaskForm):
	passwordHash = PasswordField("New Password", validators=[DataRequired(), EqualTo('passwordHashConfirm')])
	passwordHashConfirm = PasswordField("Re-enter your New Password", validators=[DataRequired()])
	submit = SubmitField("Submit")


#Store Stuffs
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



#here starts thee pages

@app.route('/signup', methods = ['GET', 'POST'])
def signup():
	
	if current_user.is_authenticated:
		return redirect(url_for('dashboard'))

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
			
	allUsers = Users.query.order_by(Users.dateOfRegistration)
	return render_template("signup.html", name = name, form = form, allUsers = allUsers)

@app.route('/login', methods = ['GET', 'POST'])
def login():
	form = LoginForm()
	if current_user.is_authenticated:
		return redirect(url_for('dashboard'))
	

	if form.validate_on_submit():

		#returns the first result of a user with the email entered (should be only one instance though), if user doesn't exist then returns nothing'
		user = Users.query.filter_by(email = form.email.data).first()

		if user:
			if check_password_hash(user.passwordHash, form.password.data):
				login_user(user)
				return redirect(url_for('dashboard'))
			else:
				flash("Wrong Password")
		else:
			flash("Email not linked to an account")
	else:
		flash("Invalid information. Please try again.")
	return render_template("login.html", form = form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    if session.get('was_once_logged_in'):
        del session['was_once_logged_in']
    flash('You have successfully logged yourself out.')
    return redirect(url_for('login'))


@app.route('/dashboard', methods = ['GET', 'POST'])
@login_required
def dashboard():
	return render_template("dashboard.html")

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
		return render_template("updateinfo.html", form = form, user = user)
	else:
		flash("Invalid Form. Please Try Again.")
	return render_template("updateinfo.html", form = form, user = user)

@app.route('/publish', methods = ['GET', 'POST'])
@login_required
def publish():
	form = BlogPostForm()
	if form.validate_on_submit():
		if recaptcha.verify():
			author = current_user.id
			blogPost = BlogPost(postTitle = form.postTitle.data, name = form.name.data, article = form.article.data, userID = author)
		
			form.postTitle.data = ''
			form.name.data = ''
			form.article.data = ''

			db.session.add(blogPost)
			db.session.commit()
			flash("Your Post was Successfully Published. Return to the posts page to view.")
			

		else:
			flash("Please fill out the captcha.")

	else:
		flash("Post not published, please try fill in all information.")

	return render_template("createpostform.html", form = form)

@app.route('/publishemersyn', methods = ['GET', 'POST'])
@login_required
def publishe():
	form = EmersynPostForm()
	if form.validate_on_submit():
		if recaptcha.verify():
			blogPost = EmersynPost(postTitle = form.postTitle.data, name = form.name.data, article = form.article.data)
		
			form.postTitle.data = ''
			form.name.data = ''
			form.article.data = ''

			db.session.add(blogPost)
			db.session.commit()
			flash("Your Post was Successfully Published")
			return redirect(url_for('posts'))

		else:
			flash("Please fill out the captcha.")

	else:
		flash("Post not published, please try fill in all information.")

	return render_template("createpostform.html", form = form)

@app.route('/publishgiles', methods = ['GET', 'POST'])
@login_required
def publishg():
	form = GilesPostForm()
	if form.validate_on_submit():
		if recaptcha.verify():
			blogPost = GilesPost(postTitle = form.postTitle.data, name = form.name.data, article = form.article.data)
		
			form.postTitle.data = ''
			form.name.data = ''
			form.article.data = ''

			db.session.add(blogPost)
			db.session.commit()
			flash("Your Post was Successfully Published")
			return redirect(url_for('posts'))

		else:
			flash("Please fill out the captcha.")

	else:
		flash("Post not published, please try fill in all information.")

	return render_template("createpostform.html", form = form)

@app.route('/publishjosh', methods = ['GET', 'POST'])
@login_required
def publishj():
	form = JoshPostForm()
	if form.validate_on_submit():
		if recaptcha.verify():
			blogPost = JoshPost(postTitle = form.postTitle.data, name = form.name.data, article = form.article.data)
		
			form.postTitle.data = ''
			form.name.data = ''
			form.article.data = ''

			db.session.add(blogPost)
			db.session.commit()
			flash("Your Post was Successfully Published")
			return redirect(url_for('posts'))

		else:
			flash("Please fill out the captcha.")

	else:
		flash("Post not published, please try fill in all information.")

	return render_template("createpostform.html", form = form)


@app.route('/posts', methods = ['GET', 'POST'])
def generatePostsPage():

	posts = BlogPost.query.order_by(BlogPost.date)

	return render_template("member.html", posts = posts)

@app.route('/userpost/<int:id>')
def userpost(id):
	blogPost = BlogPost.query.get_or_404(id)
	return render_template('userpost.html', blogPost = blogPost)

@app.route('/userpost/edit/<int:id>', methods = ['GET', 'POST'])
@login_required
def edit(id):
	blogPost = BlogPost.query.get_or_404(id)
	form = BlogPostForm()


	if form.validate_on_submit():
		blogPost.postTitle = form.postTitle.data
		blogPost.name = form.name.data
		blogPost.article = form.article.data
		db.session.add(blogPost)
		db.session.commit()

		return redirect(url_for('userpost', id = blogPost.id))

	if current_user.id == blogPost.userID:

		form.postTitle.data = blogPost.postTitle
		form.name.data = blogPost.name
		form.article.data = blogPost.article

		return render_template("createpostform.html", form = form)

	else:
		
		flash("You cannot edit this post.")

		return redirect(url_for('posts'))

@app.route('/userpost/delete/<int:id>')
@login_required
def delete(id):
	blogPost = BlogPost.query.get_or_404(id)

	userID = current_user.id

	if userID == blogPost.userID:

		db.session.delete(blogPost)
		db.session.commit()

		flash("Post Deleted")

		return redirect(url_for('posts'))

	else:
		
		flash("Cannot delete other user's posts.")

	return redirect(url_for('posts'))
	

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
		message = "You have successfully subscribed to the Scorpion email list."
		server = smtplib.SMTP("smtp.gmail.com", 587)
		server.starttls()
		#had os.getenv("EMAILPASS") in place of the actual password here, but linux is being stubborn so I used actual, not as secure but I was frustrated
		server.login("scorpionblog.roc@gmail.com", "Theswaggiest@7")
		server.sendmail("scorpionblog.roc@gmail.com", recipient.email, message)

		flash("Successfully Subscribed to Email List")

	else:
		flash("Information Invalid")

	return render_template('subscribe.html', form = form)

@app.route('/reset', methods=["GET", "POST"])
def resetpassword():
	form = EmailForm()
	if form.validate_on_submit():
		user = Users.query.filter_by(email = form.email.data).first_or_404()

		token = ts.dumps(user.email, salt='recover-key')
		print(token)
		recoveryURL = url_for('tokenreset', token = token)

		message = recoveryURL
		server = smtplib.SMTP("smtp.gmail.com", 587)
		server.starttls()
		#had os.getenv("EMAILPASS") in place of the actual password here, but linux is being stubborn so I used actual, not as secure but I was frustrated
		server.login("scorpionblog.roc@gmail.com", "Theswaggiest@7")
		server.sendmail("scorpionblog.roc@gmail.com", user.email, message)
		form.email = ''

		flash("Password Reset Link Sent")

		return redirect(url_for('login'))

	else: 

		flash("Please enter your email.")

	return render_template('reset.html', form = form)



@app.route('/tokenreset/<token>', methods=["GET", "POST"])
def tokenreset(token):
    try:
        email = ts.loads(token, salt="recover-key", max_age=86400)

    except:

        abort(404)

    form = PasswordResetForm()

    if form.validate_on_submit():
        user = Users.query.filter_by(email = email).first_or_404()

        hashedPassword = generate_password_hash(form.passwordHash.data, "sha256")
        user.passwordHash = hashedPassword

        db.session.add(user)
        db.session.commit()

        return redirect(url_for('login'))

    else: 
        flash("Passwords do not match, please try again.")

    return render_template('tokenreset.html', form=form, token=token)

@app.route('/', methods = ['GET', 'POST'])
def generateLandingPage():

	return render_template("home.html")

@app.route('/giles', methods = ['GET', 'POST'])
def generateStaticGiles():
	posts = GilesPost.query.order_by(GilesPost.date)
	return render_template("giles.html", posts = posts)



@app.route('/loysch', methods = ['GET', 'POST'])
def generateStaticLoysch():
	posts = JoshPost.query.order_by(JoshPost.date)
	return render_template("loysch.html", posts = posts)



@app.route('/emersyn', methods = ['GET', 'POST'])
def generateStaticEmersyn():
	posts = EmersynPost.query.order_by(EmersynPost.date)
	return render_template("emersyn.html", posts = posts)





#Error Handlers
@app.errorhandler(404)
def page_not_found(e):
    return render_template('error404.html'), 404

@app.errorhandler(500)
def page_not_found(e):
    return render_template('error500.html'), 500



    
	
    

#Store things

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

		print('POSTED!', file=sys.stdout)

		#flash("OK")

		#return render_tempalte("home.html")



		#checks to make sure the user's email is not in the database, should return None if the email is unique

		print(current_user.id, file=sys.stdout)



		cart = Cart.query.filter_by(uid=current_user.id).first()



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



			cart = Cart(uid = current_user.id, items=na, quantities=nb, sizes=nc)



			db.session.add(cart)

		

		db.session.commit()





		#db.session.add(cart)

		#db.session.commit()

		#flash("Sign-Up Successful. Go to the Login In page to acces your account.")

		#return redirect(url_for('generateCartPage'))

				





	items = StoreMerch.query.order_by(StoreMerch.id)

	return render_template("store.html", items = items)



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



		return render_template('cart.html', displayItems = cartDisplayItems)





			



	if cart is not None:

		return render_template("cart.html", displayItems=displayItems)

	else:

		flash("Your cart is empty! Please add some items.", 'store')

		return redirect(url_for('generateStorePage'))



if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80)