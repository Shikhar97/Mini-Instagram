from flask import url_for, send_from_directory,Flask, flash, redirect, render_template, request, session, abort
from pymongo import MongoClient
from flask_cors import CORS
from werkzeug import secure_filename
from werkzeug.security import check_password_hash,generate_password_hash
from flask_pymongo import PyMongo
import os

app = Flask(__name__)
CORS(app)
app.config['MONGO_URI']="mongodb://localhost:27017/photothief"

mongo = PyMongo(app)

app.config['UPLOAD_FOLDER'] = 'uploads/'
app.config['ALLOWED_EXTENSIONS'] = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])



def validate_login(password_hash, password):
	return check_password_hash(password_hash, password)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in app.config['ALLOWED_EXTENSIONS']

@app.route('/')
def home():
    if not session.get('logged_in'):
        return render_template('login.html')
    else:
        return index()

def index():
    users = []
    path = './uploads/'
    photos = []
    for name in os.listdir(path):
        if os.path.isfile(os.path.join(path, name)):
            b=name[:len(session['user'])]
            if b==session['user']:
                photos.append(name)
    for file in photos:
        mongo.db.data.find_one_and_update({'_id':session['user'] },{'$addToSet':{'photo':file}})
    img = mongo.db.data.find_one_or_404({"_id":session['user']})
    userTo = list(set(img['to']))
    userFrom = list(set(img['from']))
    userfriend = list(set(img['friend']))
    a=mongo.db.data.find({},{"_id":1})
    for name in a:
        if name['_id'] not in userTo and name['_id'] != session['user'] and name['_id'] not in userFrom and name['_id'] not in userfriend:
            users.append(name['_id'])
    print(users)
    return render_template('home.html', photos = img['photo'],users=list(set(users)))


@app.route('/contact')
def contact():
    return render_template('contact.html')


@app.route('/about')
def about():
       return render_template('about.html')

@app.route('/friends')
def friend():
    img = mongo.db.data.find_one_or_404({"_id":session['user']})
    userFrom = list(set(img['from']))
    print(userFrom)
    return render_template('friends.html',users=userFrom)

@app.route('/acceptfriend',methods = ['POST'])
def accept():
    clicked = request.form['requested']
    mongo.db.data.find_one_and_update({'_id':session['user'] },{'$pull':{'from':clicked}})
    mongo.db.data.find_one_and_update({'_id':clicked },{'$pull':{'to':session['user']}})
    mongo.db.data.find_one_and_update({'_id':session['user'] },{'$push':{'friend':clicked}})
    mongo.db.data.find_one_and_update({'_id':clicked },{'$push':{'friend':session['user']}})
    return friend()

@app.route('/rejectfriend',methods = ['POST'])
def reject():
    clicked = request.form['requested']
    print(clicked)
    mongo.db.data.find_one_and_update({'_id':session['user'] },{'$pull':{'from':clicked}})
    mongo.db.data.find_one_and_update({'_id':clicked },{'$pull':{'to':session['user']}})
    return friend()

@app.route('/upload', methods=['POST'])
def upload():
    # Get the name of the uploaded file
    file = request.files['file']
    # Check if the file is one of the allowed types/extensions
    if file and allowed_file(file.filename):
        # Make the filename safe, remove unsupported chars
        filename = secure_filename(file.filename)
        # Move the file form the temporal folder to
        # the upload folder we setup
        temp=session['user'] + filename
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], temp))
        # Redirect the user to the uploaded_file route, which
        # will basicaly show on the browser the uploaded file
        return redirect(url_for('home'))

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                               filename)

@app.route('/signup', methods=['POST'])
def main():
    arr=[]
    frnd=[]
    to=[]
    frm=[]
    user = request.form['username']
    password = request.form['password']
    pass_hash = generate_password_hash(password, method='pbkdf2:sha256')

    # Insert the user in the DB
    try:
        mongo.db.data.insert({"_id": user, "password": pass_hash,"photo":arr,"friend":frnd,"from":frm,"to":to})
        print ("User created.")
        session['logged_in']=True
        session['user']=user
        session['pass']=password
    except DuplicateKeyError:
        print ("User already present in DB.")
        session['logged_in']=True
        session['user']=user
        session['pass']=password
        return render_template('login.html')
    return home()



@app.route('/login', methods=['POST'])
def do_admin_login():
	user = mongo.db.data.find_one_or_404({"_id":request.form['username']})
	session['logged_in']=False
	if user and validate_login(user['password'],request.form['password']):
		 session['logged_in']=True
		 session['user']=request.form['username']
		 session['pass']=request.form['password']
	else:
		flash('wrong password')
		return redirect(url_for('home'))
	return home()
	

@app.route("/logout")
def logout():
    session['logged_in'] = False
    session['user'] = "guest"
    return home()

@app.route('/user',methods=['GET','POST'])
def add():
    t=[]
    a=request.form['name']
    users = []
    img = mongo.db.data.find_one_or_404({"_id":session['user']})
    t.append(a)
    print(request.form)
    mongo.db.data.find_one_and_update({'_id':session['user'] },{'$push':{'to':a}})
    mongo.db.data.find_one_and_update({'_id':a },{'$addToSet':{'from':session['user']}})
    return index()

@app.route('/frndphoto')
def photo():
    users = []
    path = './uploads/'
    photos = []
    data={}
    img = mongo.db.data.find_one_or_404({"_id":session['user']})
    userfriend=img['friend']
    for frnd in userfriend:
        data[frnd]=[]
    for name in os.listdir(path):
        if os.path.isfile(os.path.join(path, name)):
            for frnd in userfriend:
                b=name[:len(frnd)]
                if b==frnd:
                    data[frnd].append(name)
                    photos.append(name)
    print(photos)
    print(data)
    return render_template('about.html', data=data)


if __name__ == '__main__':
	app.secret_key = os.urandom(12)
	app.run(debug=True,host='0.0.0.0',port=5000)       # host='0.0.0.0'