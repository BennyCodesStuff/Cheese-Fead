from flask import Flask, render_template, session, request, redirect, url_for
from flask import send_from_directory
import sqlite3
from hashlib import sha256
from random import choice
from gc import collect
import os

app = Flask(__name__)
app.secret_key = "sigmakey.py"
# Secret key used for session management and security


# Database file path
db = "CheeseFeed.db"


def generate_salt(length):
    # Generate a random string of characters to be used as a salt for hashing
    # passwords
    letters = "qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM1234567890"
    # Create a random string of given length
    result_str = "".join(choice(letters) for _ in range(length))
    return result_str


def resetSession():
    # Reset session data while preserving the user ID
    placeholder = session["user_id"]  # Save the user ID
    session.clear()
    collect()
    session["user_id"] = placeholder  # Restore the user ID


def set_cheeseNUM_value():
    # Set the cheeseNUM value based on whether the user is logged in or not
    if "user_id" in session:
        # User is logged in, fetch 'cheese' from the User table
        user_id = session["user_id"]
        conn = sqlite3.connect(db)
        cursor = conn.cursor()
        cursor.execute("SELECT cheese FROM User WHERE User_id = ?", (user_id,))
        cheese_result = cursor.fetchone()
        conn.close()
        if cheese_result is not None:
            session["cheeseNUM"] = cheese_result[0]
            # Set cheeseNUM to value in database
        else:
            session["cheeseNUM"] = 0  # In case the cheese value doesn't exist
    else:
        # If not logged in, default cheeseNUM to 0
        session["cheeseNUM"] = 0
        session["answered"] = 1  # Reset answered question counter


# Function to return a random image from the static/images folder
def get_random_image():
    image_folder = os.path.join(app.root_path, 'static', 'cheeseImages')
    image_files = [f for f in os.listdir(image_folder) if f.endswith('.jpg')]
    if image_files:
        return choice(image_files)  # Randomly select an image file
    else:
        return None  # Return None if no images are found


# Route to serve images
@app.route('/static/images/<filename>')
def serve_image(filename):
    return send_from_directory(filename)
    # Serve the requested image from static/images directory


# Custom 404 error page
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404  # Render a custom 404 error page


@app.route("/")
def home():
    # Home route sets cheeseNUM and loads a random image
    set_cheeseNUM_value()
    # Set the cheeseNUM based on user status (logged in or not)
    session["answered"] = 1  # Initialize the question-answering session
    # Get a random image to display
    rand_image = get_random_image()
    if rand_image:
        image_path = f'/static/cheeseImages/{rand_image}'
        # Fix the path with correct slash
    else:
        image_path = None  # Handle the case where there are no images
    return render_template("cheeseFead.html", image_path=image_path)
    # Render home page with the random image


@app.route('/signUP')
def sign_up():
    # Sign up page with error handling for failed username or password
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
    # Handle the sign-up confirmation
    if request.method == 'POST':
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')
        # Check if passwords match
        if password1 == password2:
            username = request.form.get('username')
            conn = sqlite3.connect(db)
            cur = conn.cursor()
            # Ensure that no other users have the same name, if not,
            # return sign up with username error
            cur.execute('SELECT User_Id FROM User WHERE Username = ?', (username,))
            if len(cur.fetchall()) == 0:
                # Salt and hash the password,
                # then store the user info in the database
                salt = generate_salt(6)
                password1 += salt
                hasher = sha256()
                hasher.update(password1.encode())
                hashed = hasher.hexdigest()
                cur.execute('INSERT INTO User (Username, Hash, Salt) VALUES (?, ?, ?)', (username, hashed, salt,))
                conn.commit()
                # Clear sensitive information from memory(paswords)
                del password1
                del password2
                collect()
                session.clear()
                return redirect(url_for('login'))  # Redirect to login page
            session['usernameFailed'] = True
            return redirect(url_for('sign_up'))
        session['passwordFailed'] = True
        return redirect(url_for('sign_up'))


@app.route('/login')
def login():
    # Check for if password or username failed,
    # and pass that on to the html pages
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
            # Hash password with salt added,
            # and if successful, redirect to account page
            hasher = sha256()
            password += data[2]
            hasher.update(password.encode())
            hashed = hasher.hexdigest()
            # If the hashed password matches, log the user in
            if hashed == data[1]:
                session['user_id'] = data[0]
                # Delete password to avoid it staying in memory
                del password  # Clear password from memory
                collect()
                return redirect('/')  # Redirect to home page
        session['failed'] = True
        return redirect(url_for('login'))


@app.route("/questions")
def questions():
    # Ensure cheeseNUM is initialized
    if "cheeseNUM" not in session:
        set_cheeseNUM_value()
    if session.get('answered', 1) <= 9:
        # Retrieve the next question if
        # less than 9 have allready done the questions
        conn = sqlite3.connect("CheeseFeed.db")
        cursor = conn.cursor()
        cursor.execute("SELECT theQuestion FROM questions WHERE id = ?", (session['answered'],))
        questions = cursor.fetchone()  # Get the current question
        conn.close()
    else:
        # Calculate a score and redirect to the results page
        session['cheeseNUM'] = abs(session['cheeseNUM'])
        if session["cheeseNUM"] > 653:
            session["cheeseNUM"] = 35
        return redirect(url_for('theCHeeseKenews'))  # Redirect to results page
    return render_template("questions.html", q=questions)


@app.route("/yes")
def yes():
    # Route for when the user selects "yes" for a question
    if "cheeseNUM" not in session:
        set_cheeseNUM_value()  # Make sure cheeseNUM is initialized
    elif session["cheeseNUM"] is None:
        session["cheeseNUM"] = 0  # 0 if user did not input yes
    session["cheeseNUM"] += 1  # Move to the next question
    session['answered'] += 1
    return redirect(url_for("questions"))  # Redirect back to the next question


@app.route("/no")
def no():
    # Route for when the user selects "no" for a question
    if "cheeseNUM" not in session:
        set_cheeseNUM_value()
    elif session["cheeseNUM"] is None:
        session["cheeseNUM"] = 0
    session["cheeseNUM"] += 8  # add 8 to cheeseNUM
    session['answered'] += 1  # Move to the next question
    return redirect(url_for("questions"))


@app.route("/maybe")
def maybe():
    # Route for when the user selects "maybe" for a question
    if "cheeseNUM" not in session:
        set_cheeseNUM_value()
    elif session["cheeseNUM"] is None:
        session["cheeseNUM"] = 0
    session["cheeseNUM"] += 98
    session['answered'] += 1
    return redirect(url_for("questions"))


@app.route("/theCHeeseKenews")
def theCHeeseKenews():
    # Results page based on questions
    if "cheeseNUM" not in session:
        return render_template('404.html')
    id = session["cheeseNUM"]
    conn = sqlite3.connect("CheeseFeed.db")
    cursor = conn.cursor()
    # Update the user's 'cheese' value in the User table
    if "user_id" in session:
        user_id = session["user_id"]
        cursor.execute("SELECT cheese FROM User WHERE User_id = ?", (user_id,))
        cheese_result = cursor.fetchone()
        if cheese_result is None:
            cursor.execute("INSERT INTO User (User_id , cheese) VALUES (?, ?)", (user_id, id))
        else:
            cursor.execute("UPDATE User SET cheese = ? WHERE User_id = ?", (id, user_id))
        conn.commit()
    # Fetch cheese type and description based on quiz outcome
    cursor.execute("SELECT cheese FROM CheesePersonalty WHERE id = ?", (id,))
    cheese = cursor.fetchone()  # Get the cheese type
    if cheese is None:
        cheese = "you need to anwer the questions"
    else:
        cheese = cheese[0]
    cursor.execute("SELECT discriptionOfPersoality FROM CheesePersonalty WHERE id = ?", (id,))
    discription = cursor.fetchone()  # Get the personality description
    if discription is None:
        discription = "the questions are still not anserd"
    else:
        discription = discription[0]
    filePATH = f"/static/cheeseImages/{cheese}.jpg"
    # Image path for the cheese
    conn.close()
    return render_template("theCHeeseKenews.html", c=cheese, d=discription, p=filePATH)


@app.route('/logout')
def logout():
    # Logout route to clear session and reset the cheeseNUM value
    session.clear()   # Clear all session data
    set_cheeseNUM_value()  # Reinitialize cheeseNUM value after logout
    return render_template('logout.html')


if __name__ == "__main__":

    app.run()
