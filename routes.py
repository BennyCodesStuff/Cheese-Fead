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
    # Render the homepage
    return render_template("cheeseFead.html")


@app.route("/questions/<int:id>/<int:no>/<int:yes>/<int:maybe>")
def questions(id, no, yes, maybe):
    # Handle the questions flow in the quiz
    if id <= 9:
        # Decrease the count of no, yes, maybe responses for each question
        no -= 1
        yes -= 1
        maybe -= 1
        conn = sqlite3.connect("CheeseFeed.db")
        cursor = conn.cursor()
        cursor.execute("SELECT theQuestion FROM questions WHERE id = ?", (id,))
        questions = cursor.fetchone()  # Get the current question
        conn.close()
        id += 1  # Move to the next question
    else:
        # Calculate a score and redirect to the results page
        session["fortnut"] = no*100 + yes*10 + maybe
        id = abs(id)
        if session["fortnut"] > 653:
            session["fortnut"] = 35
        return render_template("goToCHeeseKeNeWS.html", n=no, y=yes, m=maybe)
    return render_template("questions.html", q=questions, idd=id, n=no, y=yes,
                           m=maybe)


@app.route("/theCHeeseKenews/<int:id>")
def theCHeeseKenews(id):
    # Display the final result based on the quiz outcome
    id = session["fortnut"]
    conn = sqlite3.connect("CheeseFeed.db")
    cursor = conn.cursor()
    cursor.execute("SELECT cheese FROM CheesePersonalty WHERE id = ?", (id,))
    cheese = cursor.fetchone()[0]  # Get the cheese type
    cursor.execute("SELECT discriptionOfPersoality FROM CheesePersonalty WHERE id = ?", (id,))
    discription = cursor.fetchone()  # Get the personality description
    filePATH = f"../static/cheese/{cheese}.jpg"  # Path to the cheese image
    conn.close()
    return render_template("theCHeeseKenews.html", c=cheese, d=discription,
                           p=filePATH)


@app.route("/signUP")
def sign_up():
    # Render the signup page
    return render_template("SignUp.html")


@app.route("/signupConfirm", methods=["POST"])
def signupConfirm():
    if request.method == "POST":
        # Handle the signup form submission
        password1 = request.form.get("password1")
        password2 = request.form.get("password2")
        if password1 == password2:
            # If passwords match, proceed with user registration
            username = request.form.get("username")
            conn = sqlite3.connect(db)
            cursor = conn.cursor()
            # Check if the username is already taken
            cursor.execute("SELECT User_Id FROM User WHERE Username = ?",
                           (username,))
            if len(cursor.fetchall()) == 0:
                # If the username is available, hash the password with a salt
                salt = generate_salt(6)
                password1 += salt
                hasher = sha256()
                hasher.update(password1.encode())
                hashed = hasher.hexdigest()
                # Insert the new user into the database
                cursor.execute
                ("INSERT INTO User (Username, Hash, Salt) VALUES (?, ?, ?)",
                 (username, hashed, salt,))
                conn.commit()
                # Clear sensitive information from memory
                del password1
                del password2
                collect()
                session.clear()
                return redirect(url_for("login"))  # Redirect to the login page
            session["usernameFailed"] = True  # Username already exists
            return redirect(url_for("sign_up"))  # Redirect back to signup
        session["passwordFailed"] = True  # Passwords did not match
        return redirect(url_for("sign_up"))  # Redirect back to signup


@app.route("/login")
def login():
    # Render the login page
    return render_template("login.html")


@app.route("/loginConfirm", methods=["POST"])
def loginConfirm():
    if request.method == "POST":
        # Handle the login form submission
        password = request.form.get("password")
        username = request.form.get("username")
        conn = sqlite3.connect(db)
        cursor = conn.cursor()
        cursor.execute
        ("SELECT User_Id, Hash, Salt FROM User WHERE Username = ?", (username,)
         )
        data = cursor.fetchone()
        if data is not None:
            # If the user exists, validate the password
            hasher = sha256()
            password += data[2]  # Add the salt to the password before hashing
            hasher.update(password.encode())
            hashed = hasher.hexdigest()
            if hashed == data[1]:
                session["user_id"] = data[0]  # Store the user ID in session
                del password  # Clear password from memory
                collect()
                return redirect("/theCHeeseKenews/0")
            # Redirect to the result page
        session["failed"] = True  # Login failed
        return redirect(url_for("login"))  # Redirect back to login


if __name__ == "__main__":
    # Run the Flask application in debug mode
    app.run(debug=True)

# dont touch me
# old code i dont need anymore
# @app.route("/ansers/<int:idd>")
# def answers(idd):
#   if idd == 10:
#     conn = sqlite3.connect("CheeseFeed.db")
#     cursor = conn.cursor()
#     cursor.execute("SELECT cheese
# FROM CheesePersonalty WHERE id = ?",(id,10))# ? = id
#     answers = cursor.fetchone()
#     conn.close()
#   else:
#     answers = []
#     answers.append("borken")
#   return render_template("theCHeeseKenews.html", a=answers)
