from flask import Flask, render_template
import sqlite3

app = Flask(__name__)

@app.route('/')
def home():
  quest = 1
  return render_template('cheeseFead.html', id=quest)

@app.route("/questions/<int:id>")
def questions(id):
  conn = sqlite3.connect("CheeseFeed.db")
  cursor = conn.cursor()
  cursor.execute("SELECT theQuestion FROM questions WHERE id = ?",(id,))# ? = id
  questions = cursor.fetchone()
  answers = []
  for i in range(3):
    cursor.execute("SELECT a1,a2,a3 FROM questions WHERE id = ?",(id,))# selctets the awnsers
    answer = cursor.fetchone()
    answers.append(answer[0])
  conn.close()
  return render_template("questions.html", id=2, q=questions, a=answers)


@app.route('/login')
def login():
  return render_template('loginSignUp.html')

if __name__ == "__main__":
  app.run(debug=True)

