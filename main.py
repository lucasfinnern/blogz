from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:password@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'randomString'

class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(30))
    body = db.Column(db.String(120))

    def __init__(self, title, body):
        self.title = title
        self.body = body

@app.route('/')
def go_to_blog():
    return redirect("/blog")

@app.route('/blog', methods=['POST', 'GET'])
def display_blog_entries():
    blog_id = request.args.get("id")
    
    
    if blog_id:
        blog_entry = Blog.query.get(blog_id)
        return render_template('blog_post.html', blog = blog_entry)
    
    else:
        blogs = Blog.query.all()
        return render_template("blog.html", blogs=blogs, title='Build a Blog')

@app.route('/newpost', methods=['POST', 'GET'])
def new_post():
    gate_lock = 0
    if request.method == "POST":
        body = request.form['blog_body']
        title = request.form['blog_title']
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
        new_blog = Blog(title, body)
        db.session.add(new_blog)
        db.session.commit()
        #return render_template("blog_post.html", blog = new_blog)
        return redirect("/blog?id=" + str(new_blog.id))
    return render_template('newpost.html', title='Add A Blog Entry')

if __name__ == '__main__':
    app.run()