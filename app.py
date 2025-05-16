from flask import Flask, render_template, request, redirect, session, url_for, make_response, abort, flash
from flask_bcrypt import Bcrypt
import functions
from flask_login import LoginManager, UserMixin, login_user, current_user, logout_user, login_required
from flask_pymongo import PyMongo
from flask_pymongo import ObjectId
import random
from functools import wraps

app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb://localhost:27017/ADBMS_Project"

mongo = PyMongo(app)
bcrypt = Bcrypt(app)

app.secret_key = 'MY SECRET KEY'

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


class User(UserMixin):
    def __init__(self, email, password):
        self.id = email
        self.email = email
        self.password = password

    def get_id(self):
        return self.id

    @staticmethod
    def get(user_id):
        user_data = mongo.db.UserDetails.find_one({"email": user_id})
        if user_data:
            return User(user_data["email"], user_data["password"])
        return None


@app.route('/')
def home():
    if current_user.is_authenticated:
        email = current_user.email

        recipes = mongo.db.Recipe.find()
        user_data = mongo.db.UserDetails.find_one({"email": email})

        return render_template('home.html', recipes=recipes, user=current_user, user_data=user_data)
    else:
        recipes = mongo.db.Recipe.find()
        return render_template('home.html', recipes=recipes, user=current_user, title='Home')


@app.route('/create_recipe', methods=['GET', 'POST'])
@login_required
def create_recipe():
    if request.method == 'POST':
        blog_id = functions.generate_user_id()
        title = request.form['title']
        description = request.form['description']
        ingredients = request.form['ingredients']
        instructions = request.form['instructions']
        email = current_user.email

        recipe_data = {
            "blog_id": blog_id,
            "title": title,
            "description": description,
            "ingredients": ingredients,
            "instructions": instructions,
            "email": email
        }

        mongo.db.Recipe.insert_one(recipe_data)

        return redirect(url_for('home', title='Home'))

    return render_template('create_blog.html', user=current_user, title='Share Your Recipe')


@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)


@app.route('/recipe/<blog_id>')
@login_required
def recipe(blog_id):
    blog = mongo.db.Recipe.find_one({"blog_id": blog_id})
    user = mongo.db.UserDetails.find_one({"email": blog["email"]})

    if blog is None:
        abort(404)

    return render_template('blog.html', blog=blog, users=user, user=current_user, title=blog["title"])


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        user_details = request.form
        first_name = user_details['first_name']
        last_name = user_details['last_name']
        email = user_details['email']
        city = user_details['city']
        phone = user_details['phone']
        password = bcrypt.generate_password_hash(
            user_details['password']).decode("utf-8")

        existing_user = mongo.db.UserDetails.find_one({"email": email})
        if existing_user:
            flash("Email already taken")
            return render_template('signup.html', user=current_user, title='Sign Up')

        user_data = {
            "email": email,
            "first_name": first_name,
            "last_name": last_name,
            "city": city,
            "phone": phone,
            "password": password
        }
        mongo.db.UserDetails.insert_one(user_data)

        return redirect('/login')

    return render_template('signup.html', user=current_user, title='Sign Up')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    if request.method == 'POST':
        email = request.form.get('email')
        psw = request.form.get('password')

        user = User.get(email)
        if user and bcrypt.check_password_hash(user.password, psw):
            login_user(user)
            return redirect(url_for('home'))
        else:
            flash("Wrong Email Or Password")
            return render_template('login.html', user=current_user, title='Login')

    return render_template('login.html', user=current_user, title='Login')


@app.route('/view_profile')
@login_required
def view_profile():
    email = current_user.email
    user_data = mongo.db.UserDetails.find_one({"email": email})
    blog_cursor = mongo.db.Recipe.find({"email": email})
    blogs = list(blog_cursor)

    return render_template('view_profile.html', users=user_data, blogs=blogs, user=current_user, title='Profile - ' + user_data["first_name"] + ' ' + user_data["last_name"])


@app.route('/about_us')
def AboutUs():
    return render_template('about_us.html', user=current_user, title='About Us')


@app.route('/developer/<name>')
def developer(name):
    match name:
        case 'mihika':
            return render_template('mihika.html', user=current_user)
        case 'shivam':
            return render_template('shivam.html', user=current_user)
        case 'rutuja':
            return render_template('rutuja.html', user=current_user)
        case 'kedar':
            return render_template('kedar.html', user=current_user)


@app.route('/edit_recipe/<blog_id>', methods=['GET', 'POST'])
@login_required
def edit_recipe(blog_id):
    recipe = mongo.db.Recipe.find_one({"blog_id": blog_id})

    if not recipe:

        return "Recipe not found"

    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        ingredients = request.form['ingredients']
        instructions = request.form['instructions']

        mongo.db.Recipe.update_one({"blog_id": blog_id}, {"$set": {
            "title": title,
            "description": description,
            "ingredients": ingredients,
            "instructions": instructions
        }})

        return redirect(url_for('view_profile'))

    return render_template('edit_recipe.html', user=current_user, blog=recipe, title='Edit Recipe')


@app.route('/delete_recipe/<blog_id>')
@login_required
def delete_recipe(blog_id):
    recipe = mongo.db.Recipe.find_one({"blog_id": blog_id})

    if not recipe:

        return "Recipe not found"

    mongo.db.Recipe.delete_one({"blog_id": blog_id})

    return redirect('/view_profile')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


if __name__ == "__main__":

    app.run(debug=True)
