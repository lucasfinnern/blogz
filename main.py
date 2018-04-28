from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:password@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'randomString'

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(15), unique=True)
    password = db.Column(db.String(15))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password

    '''def __repr__(self):
        return '<User %r>' % self.username'''

class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(30))
    body = db.Column(db.String(120))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner

@app.route('/blog', methods=['POST', 'GET'])
def display_blog_entries():
    blog_id = request.args.get("id")
    user_id = request.args.get("user")
    
    
    if blog_id:
        blog_entry = Blog.query.get(blog_id)
        userId2 = User.query.filter_by(id=blog_id).all()
        return render_template('blog_post.html', blog = blog_entry)

    elif user_id:
        userId = User.query.get(user_id)
        ownerId = Blog.query.filter_by(owner=userId).all()
        return render_template('singleUser.html', ownerId=ownerId, userId=userId)
    
    else:
        blogs = Blog.query.all()
        return render_template("blog.html", blogs=blogs, title='Build a Blog')

@app.route('/newpost', methods=['POST', 'GET'])
def new_post():
    gate_lock = 0
    if request.method == "POST":
        body = request.form['blog_body']
        title = request.form['blog_title']
        owner = User.query.filter_by(username=session['user']).first()
        #error
        if body == '':
            flash("There needs to be a blog entry", 'error')
            gate_lock = 1
        #error
        if title == '':
            flash("There needs to be a title", 'error')
            gate_lock = 1
        #if there is an error this will run
        if gate_lock == 1:
            return redirect('/newpost')
        new_blog = Blog(title, body, owner)
        db.session.add(new_blog)
        db.session.commit()
        #return render_template("blog_post.html", blog = new_blog)
        return redirect("/blog?id=" + str(new_blog.id))
    return render_template('newpost.html', title='Add A Blog Entry')

@app.route('/signup', methods=['POST', 'GET'])
def signup():
    lock = 0
    if request.method == 'POST':
        user_name = request.form['username']
        password = request.form['password']
        verify = request.form['verify']
        existing_user = User.query.filter_by(username=user_name).first()
        if existing_user:
            flash('Username already taken', 'error')
            lock = 1
        if password != verify:
            lock = 1
            flash("Passwords don't match", 'error')
        if user_name == '' or password == '':
            flash('All fields must be filled', 'error')
            lock = 1
        if len(user_name) < 3:
            flash("Username must be longer than 3 characters", 'error')
            lock = 1
        if len(password) < 3:
            flash('Password must be longer than 3 characters', 'error')       
        if lock == 1:
            return redirect('/signup')
        else:
            new_user = User(user_name, password)
            db.session.add(new_user)
            db.session.commit()
            session['user'] = new_user.username
            return redirect("/newpost")
    return render_template('signup.html')

@app.route('/login', methods=['POST', 'GET'])
def login():
    lock = 0
    if request.method == 'POST':
        user_name = request.form['username']
        password = request.form['password']
        existing_user = User.query.filter_by(username=user_name).first()
        if not existing_user:
            flash('Username does not exist', 'error')
            lock = 1
            return render_template('login.html')
        if password != existing_user.password:
            flash('Username or password incorrect', 'error')
            lock = 1
            return render_template('login.html')
        else:
            session['user'] = existing_user.username
            return redirect('/newpost')
    return render_template('login.html')

@app.route("/")
def index():
    userList = User.query.all()
    return render_template('index.html', userList=userList, title='Home')

@app.route('/logout', methods=['POST'])
def logout():
    del session['user']
    return redirect('/blog')

@app.before_request
def require_login():
    allowed_pages = ['signup', 'login', 'index', 'display_blog_entries']
    if 'user' not in session and request.endpoint not in allowed_pages:
        return redirect('/login')

if __name__ == '__main__':
    app.run()