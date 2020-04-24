import os
import json
from flask import Flask, render_template, url_for, session, request, redirect
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from os import path
if path.exists("env.py"):
    import env

app = Flask(__name__)

# Defining variables database and MongoDB url
app.config["MONGO_DBNAME"] = os.getenv('MONGO_DBNAME')
app.config["MONGO_URI"] = os.getenv('MONGO_URI')

mongo = PyMongo(app)

# First page - index.html where user is asked to enter their email address to access their schedule
@app.route('/')
def index():
    if 'email' in session:
        return redirect(url_for('modules'))

    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    users = mongo.db.users
    login_user = users.find_one({'email' : request.form['email']})

    if login_user:
        session['email'] = request.form['email']
        return redirect(url_for('modules'))

    return 'email address not found! Try signing up!'

@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        users = mongo.db.users
        existing_user = users.find_one({'email' : request.form['email']})

        if existing_user is None:
            users.insert({'email' : request.form['email']})
            session['email'] = request.form['email']
            return redirect(url_for('modules'))
        
        return 'That email already exists!'

    return render_template('register.html')
@app.route('/logout')
def logout():
    session['email'] = None
    return render_template('login.html')

@app.route('/modules')
def modules():
    return render_template("modules.html", 
                           lessons=mongo.db.lessons.find())
                           
@app.route('/add_lesson', methods=['POST'])
def add_lesson():
    mongo.db.lessons.insert({'module' : request.form['module'], 'lesson' : request.form['lesson'], 'email' : session['email']})
    return redirect(url_for('modules'))

@app.route('/delete_lesson/<lesson_id>')
def delete_lesson(lesson_id):
    mongo.db.lessons.remove({'_id': ObjectId(lesson_id)})
    return redirect(url_for('modules'))

@app.route('/notes')
def notes():
    return render_template("notes.html", 
                           notes=mongo.db.notes.find())

@app.route('/add_notes', methods=['POST'])
def add_notes():
    mongo.db.notes.insert({'note' : request.form['note'], 'title' : request.form['title'], 'email' : session['email']})
    return redirect(url_for('notes'))

@app.route('/delete_note/<note_id>')
def delete_notes(note_id):
    mongo.db.notes.remove({'_id': ObjectId(note_id)})
    return redirect(url_for('notes'))

@app.route('/edit_note/<note_id>')
def edit_notes(note_id):
    this_note =  mongo.db.notes.find_one({"_id": ObjectId(note_id)})
    return render_template('editnote.html', note=this_note)

@app.route('/update_notes/<note_id>', methods=["POST"])
def update_notes(note_id):
    notes = mongo.db.notes
    notes.update( {'_id': ObjectId(note_id)},
    {
        'title':request.form.get('title'),
        'note':request.form.get('note'),
    })
    return redirect(url_for('notes'))


if __name__ == '__main__':
    app.secret_key = 'mysecret'
    app.run(host=os.environ.get('IP'),
            port=int(os.environ.get('PORT')),
            debug=True)



