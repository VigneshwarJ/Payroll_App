from flask import Flask, render_template,request,url_for,redirect,flash,session
from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, validators, PasswordField
from passlib.hash import sha256_crypt
from functools import wraps
import pymysql
import gc
import array

pymysql.install_as_MySQLdb()

from MySQLdb import escape_string as thwart
from . import dbconnect1
app = Flask(__name__)
app.secret_key="12373727"
@app.route("/")
def hello():
    return render_template("main.html")
if __name__ == "__main__":
    app.run()
    

@app.route('/dashboard/',methods=["GET","POST"])
def dashboard():
    error = ''
    c, conn = dbconnect1.connection()
    c.execute("SELECT * FROM Employee")
    data = c.fetchall()
   
    try:
        
        if request.method == "POST":
            if "Report" in request.form:
            # if request.form['Report']:
                flash("whyyyyyy")
                return render_template("report.html",data=data)
            elif "Add" in request.form:
            # if request.form['Add']:
                c.execute("INSERT INTO Employee (EmpName, Salary) VALUES (%s, %s)",
                          (request.form['EmpName'], request.form['Salary']))
                conn.commit()
                c.close()
                conn.close()            
                flash("row added")
                return redirect(url_for("dashboard"))
            
        # if request.form['Add'] and request.method == "POST":    
        #     c.execute("INSERT INTO Employee (EmpName, Salary) VALUES (%s, %s)",
        #                   (request.form['EmpName'], request.form['Salary']))
        #     conn.commit()
        #     c.close()
        #     conn.close()            
        #     flash("row added")
        #     return redirect(url_for("dashboard"))
        # if request.form['Report'] and request.method == "POST":
        #     return render_template(url_for("report"),data=data)
        

            
        gc.collect()
        return render_template("dashboard.html",data=data)

    except Exception as e:
        
        flash(e)
        c.close()
        conn.close()
        return render_template("dashboard.html",data=data)

# @app.route("/report/")
# def report():
#     return render_template("report.html")

class RegistrationForm(FlaskForm):
    username = StringField('Username', [validators.Length(min=4, max=20)])
    #email = TextField('Email Address', [validators.Length(min=6, max=50)])
    password = PasswordField('New Password', [
        validators.Required(),
        validators.EqualTo('confirm', message='Passwords must match')
    ])
    confirm = PasswordField('Repeat Password')
    #accept_tos = BooleanField('I accept the Terms of Service and Privacy Notice (updated Jan 22, 2015)', [validators.Required()])

@app.route("/register/",methods=["GET","POST"])
def register_page():
    try:
        form = RegistrationForm(request.form)
        # c1, conn1 = dbconnect1.connection()
        # x = c1.execute("SELECT * FROM users ")
        # return str(x)
        # c1.close()
        # conn1.close()
        form.validate()
        if request.method == "POST":
            username  = form.username.data
        
            password = sha256_crypt.encrypt((str(form.password.data)))
            c, conn = dbconnect1.connection()
            flash("flash test!!!!")
            x = c.execute("SELECT * FROM users WHERE username = (%s)",
                          [(thwart(username))])
            #return str(x)
            if int(x) > 0:
                flash("That username is already taken, please choose another")
                return render_template('register.html', form=form)

            else:
                c.execute("INSERT INTO users (username, password) VALUES (%s, %s)",
                          (thwart(username), thwart(password)))
                
                
                conn.commit()
                flash("Thanks for registering!")
                c.close()
                conn.close()
                gc.collect()

                # session['logged_in'] = True
                # session['username'] = username
                
                return redirect(url_for('dashboard'))

        return render_template("register.html", form=form)
        #return "errrrrrrrrrr"#,password

        flash("flash test!!!!")

    except Exception as e:
        return(str(e))

@app.route('/login/', methods=["GET","POST"])
def login_page():
    error = ''
    try:
        c, conn = dbconnect1.connection()
        if request.method == "POST":

            data = c.execute("SELECT * FROM users WHERE username = (%s)",
                             thwart(request.form['username']))
            
            data = c.fetchone()[2]

            if sha256_crypt.verify(request.form['password'], data):
                session['logged_in'] = True
                session['username'] = request.form['username']

                flash("You are now logged in")
                return redirect(url_for("dashboard"))

            else:
                error = "Invalid credentials, try again."

        gc.collect()

        return render_template("login.html", error=error)

    except Exception as e:
        #flash(e)
        error = "Invalid credentials, try again."
        return render_template("login.html", error = error)  

@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html")
if __name__ == "__main__":
    app.run()

def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash("You need to login first")
            return redirect(url_for('login_page'))

    return wrap
@app.route("/logout/")
@login_required
def logout():
    session.clear()
    flash("You have been logged out!")
    gc.collect()
    return redirect(url_for('dashboard'))
		     
