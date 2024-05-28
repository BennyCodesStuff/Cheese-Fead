from flask import Flask, render_template
import sqlite3

app = Flask(__name__)


@app.route('/home')
def home():
  return render_template('cheeseFead.html')

@app.route('/login')
def login():
  return render_template('loginSignUp.html')

if __name__ == "__main__":
  app.run(debug=True)

