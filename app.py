from flask import *
# from flask import Flask, render_template, request
from models import *
from werkzeug.security import *

app = Flask(__name__)
app.secret_key = 'e3a1b4cfe6a74d8a1bbcf78a13b03cc4'



app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

with app.app_context():
    db.create_all()


@app.route('/')
def home():
    return render_template('index.html')

@app.route('/login',methods=['GET','POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = User.query.filter_by(username=username).first()
        # if user and check_password_hash(user.password, password):
        if user and user.password == password:
            session['user_id'] = user.id
            session['username'] = user.username
            return redirect(url_for('dashboard'))
        else:
            flash("Invalid username or password or you're not logged in")
            return redirect(url_for('login'))

    return render_template('index.html')

@app.route('/signup',methods=['GET','POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            return 'Username already exists'
        
        # hashed_password = generate_password_hash(password)
        # new_user = User(username=username, password=hashed_password)
        new_user = User(username=username, password=password)
        db.session.add(new_user)
        db.session.commit()
        flash("Account Created Successfully")
        return redirect(url_for('login'))
    return render_template('signup.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']
    entries = PasswordEntry.query.filter_by(user_id=user_id).all()
    return render_template('dashboard.html', entries=entries, username=session['username'])


@app.route('/add', methods=['GET', 'POST'])
def add_entry():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        site_name = request.form['site_name']
        site_url = request.form['site_url']
        login_username = request.form['login_username']
        login_password = request.form['login_password']

        new_entry = PasswordEntry(
            site_name=site_name,
            site_url=site_url,
            login_username=login_username,
            login_password=login_password,
            user_id=session['user_id']
        )

        db.session.add(new_entry)
        db.session.commit()
        flash("Password Saved Successfully")
        return redirect(url_for('dashboard'))

    return render_template('add_entry.html')

@app.route('/delete/<int:entry_id>', methods=['POST'])
def delete_entry(entry_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    entry = PasswordEntry.query.get_or_404(entry_id)

    # Ensure user owns the entry
    if entry.user_id != session['user_id']:
        flash("Unauthorized action.", "error")
        return redirect(url_for('dashboard'))

    db.session.delete(entry)
    db.session.commit()
    flash('Password entry deleted.', 'success')
    return redirect(url_for('dashboard'))


@app.route('/edit/<int:entry_id>', methods=['GET', 'POST'])
def edit_entry(entry_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    entry = PasswordEntry.query.get_or_404(entry_id)

    # Check ownership
    if entry.user_id != session['user_id']:
        flash("Unauthorized", "error")
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        entry.site_name = request.form['site_name']
        entry.site_url = request.form['site_url']
        entry.login_username = request.form['login_username']
        entry.login_password = request.form['login_password']
        db.session.commit()
        flash("Password entry updated!", "success")
        return redirect(url_for('dashboard'))

    return render_template('edit_entry.html', entry=entry)

if __name__ == '__main__':
    app.run(debug=True)