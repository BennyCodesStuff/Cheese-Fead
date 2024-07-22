from flask import Flask, render_template
import sqlite3
import random
app = Flask(__name__)

@app.route('/')
def home():
  return render_template('cheeseFead.html')

@app.route("/questions/<int:id>/<int:no>/<int:yes>/<int:maybe>")
def questions(id, no, yes, maybe):
  if id <= 9:
    no -= 1
    yes -= 1
    maybe -= 1
    sigma = (no + yes + maybe)
    conn = sqlite3.connect("CheeseFeed.db")
    cursor = conn.cursor()
    cursor.execute("SELECT theQuestion FROM questions WHERE id = ?",(id,))# ? = id
    questions = cursor.fetchone()
    conn.close()
    id += 1
  else:
    return render_template("theCHeeseKenews.html", n=no, y=yes, m=maybe)
  return render_template("questions.html", q=questions, idd=id, n=no, y=yes, m=maybe)

@app.route('/theCHeeseKenews')
def theCHeeseKenews():
  return render_template('theCHeeseKenews.html')

@app.route('/login')
def login():
  return render_template('loginSignUp.html')


if __name__ == "__main__":
  app.run(debug=True)











#dont go down trust









#stop this now











#your evil if you go past this








# @app.route("/ansers/<int:idd>")
# def answers(idd):
#   if idd == 10:
#     conn = sqlite3.connect("CheeseFeed.db")
#     cursor = conn.cursor()
#     cursor.execute("SELECT cheese FROM CheesePersonalty WHERE id = ?",(id,10))# ? = id
#     answers = cursor.fetchone()
#     conn.close()
#   else:
#     answers = []
#     answers.append("borken")
#   return render_template("theCHeeseKenews.html", a=answers)
