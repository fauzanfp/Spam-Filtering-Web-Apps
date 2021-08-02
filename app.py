from os import stat
from flask import Flask, render_template, request, session, json
from flask.helpers import flash, url_for
from werkzeug.utils import redirect
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.naive_bayes import MultinomialNB #naivebayes
from sklearn.metrics import confusion_matrix  
from flask_recaptcha import ReCaptcha
import mysql.connector
import pandas as pd 


app = Flask(__name__)
app.secret_key = 'asdasd asdadasd'
#recaptcha = ReCaptcha(app=app)


emailnya = pd.read_csv("D:\Download\Spam_Detection\spam.csv")

app.config.update(dict(
    RECAPTCHA_ENABLED = True,
    RECAPTCHA_SITE_KEY = '6LfE57QbAAAAADZLfwBDlSgawXUXyve5AB-a3PrO',
    RECAPTCHA_SECRET_KEY = '6LfE57QbAAAAAOGPLI-zHWWh4_wFN65OliYxfBls'
))

recaptcha = ReCaptcha()
recaptcha.init_app(app)

#konek ke database
db = mysql.connector.connect(
    host="localhost",
    user="root",
    passwd="",
    database="flask"
)

@app.route('/')
def hello():
    return render_template('index.html')

@app.route('/profile/<username>', methods=['GET','POST'])
def show_profile(username):
    if request.method=='POST':
        X = emailnya.iloc[:, -1] 
        y = emailnya.iloc[:, 0]

        X_train, X_test, y_train, y_test = train_test_split(X, y) 

        vectorizer = TfidfVectorizer()
        X_train = vectorizer.fit_transform(X_train)

        classifier = MultinomialNB() #naive bayes 
        classifier.fit(X_train, y_train) #naive bayes 

        test = [request.form.get('text')]
        test = vectorizer.transform(test)
        prediksi = classifier.predict(test)
        flash(prediksi, 'success')

        X_test = vectorizer.transform(X_test)
        y_pred = classifier.predict(X_test)

        #performa
        cm = confusion_matrix(y_test, y_pred)

    return render_template('profile.html')

@app.route('/login', methods=['GET','POST'])
def show_login():

    if request.method == 'POST':
        
        #captcha_response = request.form['g-recaptcha-response']
        email = request.form.get("email")
        password = request.form.get("password")

        cur = db.cursor()
        cur.execute("SELECT * FROM auth where email='"+ email +"' AND password='"+ password +"' ")
        data = cur.fetchone()
        
        if data is None:
            flash('email/password salah!', category='error')
            return render_template("login.html")

        elif recaptcha.verify():
                flash('New Session Add Success')
                session['username'] = request.form['email']
                flash('berhasil login', 'success')        
                return redirect(url_for('show_profile', username=session['username']))            
        else:
                flash('Error ReCaptcha')
                return redirect(url_for('show_login'))       
        
    if 'username' in session:
        username = session['username']       
        return redirect(url_for('show_profile', username=username))
    
    
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():

    
    if request.method == 'POST':
        email = request.form.get('email')
        firstName = request.form.get('firstName')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')
        
        if len(email) < 4:
            flash('Email harus lebih dari 4 karakter!', category='error')
        elif len(firstName) < 2:
            flash('Firstname harus lebih dari 1 karakter!', category='error')
        elif password1 != password2:
            flash('Password harus sama!', category='error')
        elif len(password1) < 7: 
            flash('Password setidaknya harus 7 karakter!', category='error')
        else:
            cur = db.cursor()
            cur.execute("INSERT INTO auth(email, firstName, password) VALUES (%s, %s, %s)", (email, firstName, password1))
            db.commit()            
            flash('Akun berhasil dibuat!', category='success')

    return render_template("signup.html")

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('show_login'))



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)