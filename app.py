from email.mime import image
from mimetypes import init

from flask import Flask, render_template , request,redirect,session,flash
import sqlite3 ,os
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key= "secret123"
upload_folder = 'static/images'
os.makedirs(upload_folder, exist_ok=True)
app.config['UPLOAD_FOLDER'] = upload_folder

def get_db():
    conn = sqlite3.connect('database.db')
    conn.row_factory=sqlite3.Row
    return conn
def init_db():
    conn=get_db()
    conn.execute("CREATE TABLE IF NOT EXISTS users( id INTEGER PRIMARY KEY, username TEXT UNIQUE, password TEXT)")
    conn.execute("CREATE TABLE IF NOT EXISTS posts(id INTEGER PRIMARY KEY, title TEXT,author TEXT,content TEXT, image TEXT)")
    conn.execute("CREATE TABLE IF NOT EXISTS contacts(id INTEGER PRIMARY KEY, name TEXT,email TEXT,message TEXT)")
    conn.commit()
    conn.close()
init_db()
@app.route('/')
def home():
    posts = get_db().execute("SELECT * FROM posts ORDER BY id DESC").fetchall()
    return render_template('index.html', posts=posts )
@app.route('/post')
def post():
    if 'user' not in session:
        return redirect('/login')
    return render_template('post.html')
@app.route('/create_post',methods=['POST'])
def create_post():
    title=request.form['title']
    content=request.form['content']
    author=session['user']
    image=request.files['image']
    filename=""
    if image and image.filename:
       filename=secure_filename(image.filename)
       image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    db=get_db()
    db.execute("INSERT into posts (title,author,content,image) VALUES (?,?,?,?)",(title,author,content,image))
    db.commit()
    return redirect('/')
@app.route('/about')
def about():
    return render_template('about.html')
@app.route('/login',methods=['GET','POST'])
def login():
    if request.method == 'POST':
       user= get_db().execute("SELECT * FROM users WHERE username = ?",(request.form['username'],)).fetchone()
       if user and check_password_hash(user['password'],request.form['password']):
            session['user'] = user['username']
            return redirect('/')
       flash('Invalid username or password')

    return render_template('login.html')
@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/')
@app.route('/contact',methods=['GET','POST'])
def contact():
    if request.method == 'POST':
        db= get_db()
        db.execute("INSERT INTO contacts(name,email,message) VALUES (?,?,?)",(request.form['name'],request.form['email'],request.form['message']))

        db.commit()
        flash('Contact added')

    return render_template('contact.html')
@app.route('/admin')
def admin():
    if 'user' not in session:
        return redirect('/login')
    posts = get_db().execute("SELECT * FROM posts").fetchall()
    return render_template('admin.html', posts=posts)


    return render_template('admin.html')
@app.route('/signup', methods=['GET','POST'])
def signup():
    if request.method == 'POST':
        try:
            db=get_db()
            db.execute("INSERT INTO users(username,password) VALUES (?,?)",
                       (request.form['username'],generate_password_hash(request.form['password'])))
            db.commit()
            flash('Account created for ' + request.form['username'])
            return redirect('/login')
        except:
            flash('Invalid username or password')
    return render_template('signup.html')


@app.route('/base')
def base():
    return render_template('base.html')

@app.route('/delete/<int:id>')
def delete_post(id):
    db=get_db()
    db.execute("DELETE FROM posts WHERE id = ?",(id,))
    db.commit()
    flash('Post deleted')
    return redirect('/admin')



if __name__ == '__main__':
    app.run(debug=True)

