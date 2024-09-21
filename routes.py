from flask import Flask, render_template, session, request, redirect, url_for, send_from_directory
import sqlite3
from hashlib import sha256
from random import choice
from gc import collect
import os

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


def set_fortnut_value():
    if "user_id" in session:
        # User is logged in, fetch 'cheese' from the User table
        user_id = session["user_id"]
        conn = sqlite3.connect(db)
        cursor = conn.cursor()
        cursor.execute("SELECT cheese FROM User WHERE User_id = ?", (user_id,))
        cheese_result = cursor.fetchone()
        conn.close()
        if cheese_result is not None:
            session["fortnut"] = cheese_result[0]  # Set fortnut to the value of the cheese column
        else:
            session["fortnut"] = 0  # In case the cheese value doesn't exist
    else:
        # User is not logged in, set fortnut to 0
        session["fortnut"] = 0


# Function to return a random image from the static/images folder
def get_random_image():
    image_folder = os.path.join(app.root_path, 'static', 'cheeseImages')
    image_files = [f for f in image_folder if f.endswith(('.jpg'))]
    if image_files:
        return choice(image_files)
    else:
        return None


@app.route("/")
def home():
    set_fortnut_value()  # Set the correct fortnut value based on whether the user is logged in
    session["answered"] = 1
    # Get a random image to display
    rand_image = get_random_image()
    if rand_image:
        image_path = f'/static/cheeseImages{rand_image}'
    else:
        image_path = None  # Handle the case where there are no images
    return render_template("cheeseFead.html", image_path=image_path)

# Route to serve images
@app.route('/static/images/<filename>')
def serve_image(filename):
    return send_from_directory(cheeseImages, filename)


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.route("/questions")
def questions():
    # Ensure fortnut is initialized
    if "fortnut" not in session:
        set_fortnut_value()
    if session.get('answered', 1) <= 9:
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
        return redirect(url_for('theCHeeseKenews'))
    return render_template("questions.html", q=questions)


@app.route("/yes")
def yes():
    # Ensure fortnut is initialized
    if "fortnut" not in session:
        set_fortnut_value()
    elif session["fortnut"] is None:
        session["fortnut"] = 0
    session["fortnut"] += 1
    session['answered'] += 1
    return redirect(url_for("questions"))


@app.route("/no")
def no():
    # Ensure fortnut is initialized
    if "fortnut" not in session:
        set_fortnut_value()
    elif session["fortnut"] is None:
        session["fortnut"] = 0
    session["fortnut"] += 8
    session['answered'] += 1
    return redirect(url_for("questions"))


@app.route("/maybe")
def maybe():
    # Ensure fortnut is initialized
    if "fortnut" not in session:
        set_fortnut_value()
    elif session["fortnut"] is None:
        session["fortnut"] = 0
    session["fortnut"] += 98
    session['answered'] += 1
    return redirect(url_for("questions"))


@app.route("/theCHeeseKenews")
def theCHeeseKenews():
    # Display the final result based on the quiz outcome
    if "fortnut" not in session:
        session["fortnut"] = 654
    id = session["fortnut"]
    conn = sqlite3.connect("CheeseFeed.db")
    cursor = conn.cursor()
    if "user_id" in session:
        user_id = session["user_id"]
        cursor.execute("SELECT cheese FROM User WHERE User_id = ?", (user_id,))
        cheese_result = cursor.fetchone()
        if cheese_result is None:
            cursor.execute("INSERT INTO User (User_id , cheese) VALUES (?, ?)", (user_id, id))
        else:
            cursor.execute("UPDATE User SET cheese = ? WHERE User_id = ?", (id, user_id))
        conn.commit()
    cursor.execute("SELECT cheese FROM CheesePersonalty WHERE id = ?", (id,))
    cheese = cursor.fetchone()  # Get the cheese type
    if cheese is None:
        cheese = "you need to anwer the questions"
    else:
        cheese = cheese[0]
    cursor.execute("SELECT discriptionOfPersoality FROM CheesePersonalty WHERE id = ?", (id,))
    discription = cursor.fetchone()  # Get the personality description
    filePATH = f"/static/cheeseImages/{cheese}.jpg"
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
    # Check for if password or username failed, and pass that on to the html pages
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
                return redirect('/')
        session['failed'] = True
        return redirect(url_for('login'))


@app.route('/logout')
def logout():
    session.clear()  # Clear session on logout
    return render_template('logout.html')


if __name__ == "__main__":

    app.run()
