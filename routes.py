from flask import Flask, render_template, session, request, redirect, url_for
import sqlite3
from hashlib import sha256
from random import choice
from gc import collect

app = Flask(__name__)
app.secret_key = "sigmakey.py"  # Secret key used for session management

# Database file path
db = "CheeseFeed.db"


def generate_salt(length):
    # Generate a random string of characters to be used as a salt for hashing
    # passwords
    letters = "qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM1234567890"
    result_str = "".join(choice(letters) for _ in range(length))
    return result_str


def resetSession():
    # Reset session data while preserving the user ID
    placeholder = session["user_id"]
    session.clear()
    collect()  # Trigger garbage collection to free up memory
    session["user_id"] = placeholder


@app.route("/")
def home():
    session["answered"] = 1
    session["fortnut"] = 0
    # Render the homepage
    return render_template("cheeseFead.html")


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.route("/questions")
def questions():
    # Handle the questions flow in the quiz
    if session['answered'] <= 9:
        # Decrease the count of no, yes, maybe responses for each question
        conn = sqlite3.connect("CheeseFeed.db")
        cursor = conn.cursor()
        cursor.execute("SELECT theQuestion FROM questions WHERE id = ?", (session['answered'],))
        questions = cursor.fetchone()  # Get the current question
        conn.close()
    else:
        # Calculate a score and redirect to the results page
        session['fortnut'] = abs(session['fortnut'])
        if session["fortnut"] > 653:
            session["fortnut"] = 35
        return render_template("goToCHeeseKeNeWS.html")
    return render_template("questions.html", q=questions)


@app.route("/yes")
def yes():
    session["fortnut"] -= 1
    session['answered'] += 1  # Move to the next question
    return redirect(url_for("questions"))


@app.route("/no")
def no():
    session["fortnut"] += 8
    session['answered'] += 1  # Move to the next question
    return redirect(url_for("questions"))


@app.route("/maybe")
def maybe():
    session["fortnut"] += 98
    session['answered'] += 1  # Move to the next question
    return redirect(url_for("questions"))


@app.route("/theCHeeseKenews")
def theCHeeseKenews():
    # Display the final result based on the quiz outcome
    if "fortnut" not in session:
        session["fortnut"] = 654
    id = session["fortnut"]
    conn = sqlite3.connect("CheeseFeed.db")
    cursor = conn.cursor()
    cursor.execute("SELECT cheese FROM CheesePersonalty WHERE id = ?", (id,))
    cheese = cursor.fetchone()  # Get the cheese type
    cursor.execute("SELECT discriptionOfPersoality FROM CheesePersonalty WHERE id = ?", (id,))
    discription = cursor.fetchone()  # Get the personality description
    filePATH = f"../static/cheese/{cheese}.jpg"  # Path to the cheese image
    conn.close()
    return render_template("theCHeeseKenews.html", c=cheese, d=discription, p=filePATH)


@app.route('/signUP')
def sign_up():
    # Check for if password or username failed, and pass that on to the html page
    if 'passwordFailed' in session:
        del session['passwordFailed']
        return render_template('SignUp.html', title="Sign Up:", usernameFailed=False, passwordFailed=True)
    if 'usernameFailed' in session:
        del session['usernameFailed']
        return render_template('SignUp.html', title="Sign Up:", usernameFailed=True, passwordFailed=False)
    else:
        return render_template('SignUp.html', title="Sign Up:", usernameFailed=False, passwordFailed=False)


@app.route('/signupConfirm', methods=['POST'])
def signupConfirm():
    if request.method == 'POST':
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')
        # Check if passwords match
        if password1 == password2:
            username = request.form.get('username')
            conn = sqlite3.connect(db)
            cur = conn.cursor()
            # Ensure that no other users have the same name, if not, return sign up with username error
            cur.execute('SELECT User_Id FROM User WHERE Username = ?', (username,))
            if len(cur.fetchall()) == 0:
                # Generate a salt, add it to password, hash, and then insert this user info into the user table
                salt = generate_salt(6)
                password1 += salt
                hasher = sha256()
                hasher.update(password1.encode())
                hashed = hasher.hexdigest()
                cur.execute('INSERT INTO User (Username, Hash, Salt) VALUES (?, ?, ?)', (username, hashed, salt,))
                conn.commit()
                # Remove passwords immediately instead of letting them stay in memory
                del password1
                del password2
                collect()
                session.clear()
                return redirect(url_for('login'))
            session['usernameFailed'] = True
            return redirect(url_for('sign_up'))
        session['passwordFailed'] = True
        return redirect(url_for('sign_up'))


@app.route('/login')
def login():
    # Check for if password or username failed, and pass that on to the html page
    if 'failed' in session:
        return render_template('login.html', title="Log in to your account:", failed=True)
    else:
        return render_template('login.html', title="Log in to your account:", failed=False)


@app.route('/loginConfirm', methods=['POST'])
def loginConfirm():
    if request.method == 'POST':
        password = request.form.get('password')
        username = request.form.get('username')
        conn = sqlite3.connect(db)
        cur = conn.cursor()
        cur.execute('SELECT User_Id, Hash, Salt FROM User WHERE Username = ?', (username,))
        data = cur.fetchone()
        # Check if user exists, else return page with failed
        if data is not None:
            # Hash password with salt added, and if successful, redirect to account page
            hasher = sha256()
            password += data[2]
            hasher.update(password.encode())
            hashed = hasher.hexdigest()
            if hashed == data[1]:
                session['user_id'] = data[0]
                # Delete password to avoid it staying in memory
                del password
                collect()
                return redirect('/theCHeeseKenews')
        session['failed'] = True
        return redirect(url_for('login'))


if __name__ == "__main__":
    # Run the Flask application in debug mode
    app.run(debug=True)
