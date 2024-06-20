from flask import Flask, render_template
import sqlite3
import random
app = Flask(__name__)

@app.route('/')
def home():
  quest += 1
  return render_template('cheeseFead.html', id=quest)

@app.route("/questions/<int:id>")
def questions(id):
  if id <= 9:
    conn = sqlite3.connect("CheeseFeed.db")
    cursor = conn.cursor()
    cursor.execute("SELECT theQuestion FROM questions WHERE id = ?",(id,))# ? = id
    questions = cursor.fetchone()
    conn.close()
    id += 1
  else:
    questions = []
    questions.append("you win")
  return render_template("questions.html", q=questions, idd=id)


@app.route('/login')
def login():
  return render_template('loginSignUp.html')

if __name__ == "__main__":
  app.run(debug=True)

