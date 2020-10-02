from flask import Flask,url_for,render_template,redirect,flash,request,flash,session
from flask_sqlalchemy import SQLAlchemy
	
import os
import pandas as pd

app = Flask('__name__',
            static_url_path='', 
            static_folder='static')

app.secret_key = '7311920049'

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@localhost/spectre?unix_socket=/opt/lampp/var/mysql/mysql.sock'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.config['UPLOAD_FOLDER'] = 'uploads'

db=SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    username = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    priv = db.Column(db.String(80))

    def __init__(self, username, password, priv):
 
        self.username = username
        self.password = password
        self.priv = priv  



class Data(db.Model):
    id = db.Column(db.Integer, primary_key = True, autoincrement=True)
    name = db.Column(db.String(100))
    grade = db.Column(db.String(100))
    section = db.Column(db.String(100))
    email = db.Column(db.String(100))
    phone = db.Column(db.String(100))
 
    def __init__(self, name, grade, section, email, phone):
 
        self.name = name
        self.grade = grade
        self.section = section
        self.email = email
        self.phone = phone


class Test_Data(db.Model):
    t_id = db.Column(db.Integer, primary_key = True, autoincrement=True)
    t_grade = db.Column(db.String(100))
    t_name = db.Column(db.String(100))
    t_code = db.Column(db.String(100), unique=True)

    def __init__(self, t_grade, t_name, t_code):
        self.t_grade = t_grade
        self.t_name = t_name
        self.t_code = t_code

app.debug = True









@app.route('/Dashboard_home')
def dhome():
    if 'ROLE' in session:
        return render_template('d_home.html')
    else:
        flash("You are not logged in")
        return redirect(url_for('login'))



@app.route('/insert', methods = ['POST'])
def insert():
 
    if request.method == 'POST':

 
        name = request.form['name']
        grade = request.form['grade']
        section = request.form['section']
        email = request.form['email']
        phone = request.form['phone']
 
 
        my_data = Data(name, grade, section, email, phone)
        db.session.add(my_data)
        db.session.commit()
 
        flash("Student Data Inserted Successfully")
 
        return redirect(url_for('manage_student'))





@app.route('/update', methods=['GET', 'POST'])
def update():
    if request.method == 'POST':
        my_data = Data.query.get(request.form.get('id'))
 
        my_data.name = request.form['name']
        my_data.grade = request.form['grade']
        my_data.section = request.form['section']
        my_data.email = request.form['email']
        my_data.phone = request.form['phone']
 
        db.session.commit()
        flash("Student Data Updated Successfully")
 
        return redirect(url_for('manage_student'))





@app.route('/delete/<id>/', methods = ['GET', 'POST'])
def delete(id):
    my_data = Data.query.get(id)
    db.session.delete(my_data)
    db.session.commit()
    flash("Student Data Deleted Successfully")
 
    return redirect(url_for('manage_student'))





@app.route('/ManageStudent')
def manage_student():
    if 'ROLE' in session:
        role = session.get('ROLE')
        if role == 'Teacher' or role == 'Administrator':
            all_data = Data.query.all()
            return render_template('manage_student.html', students=all_data)
        else:
            return render_template('forbidden_teacher.html')





@app.route('/searchByName/',methods=['GET','POST'])
def searchByName():
    if 'ROLE' in session:
        if request.method=='POST':
            student_name = request.form['student_name']
            search_data = Data.query.filter(Data.name.contains(student_name))
            return render_template('search_name.html',results=search_data)
        else:
            return render_template('search_name.html')


@app.route('/uploadScore', methods=['GET','POST'])
def uploadScore():
    if 'ROLE' in session:
        role = session.get('ROLE')
        if role == 'Teacher' or role == 'Administrator':
            if request.method == 'POST':
                t_grade = request.form['t_grade']
                t_name = request.form['t_name']
                t_code = request.form['t_code']
                t_file = request.files['t_file']
                t_fname = t_file.filename
                if t_fname != '' :
                    my_data = Test_Data(t_grade,t_name,t_code)
                    db.session.add(my_data)
                    db.session.commit()

                    t_file.save(os.path.join(app.config['UPLOAD_FOLDER'], t_code+".xlsx"))
                    flash("Score Uploaded Successfully")
                    return redirect(url_for('uploadScore'))
                    
                else:
                    flash('No file attached')

            if request.method == 'GET':
                return render_template('upload_score.html')
        else:
            return render_template('forbidden_teacher.html')


@app.route('/viewScore')
def viewScore():
    if 'ROLE' in session:
        all_data = Test_Data.query.all()
        return render_template('view_score.html', tests = all_data)


@app.route('/renderScore', methods=['POST'])
def renderScore():
    if request.method == 'POST':
        t_code = request.form['t_code']

        src = os.path.join(app.config['UPLOAD_FOLDER']) + '/' + t_code+'.xlsx'
        
        df = pd.read_excel(src)

        return render_template('render_score.html', column_names = df.columns.values, row_data = list(df.values.tolist()), zip=zip)

@app.route('/createUser', methods=['GET','POST'])
def createUser():
    if 'ROLE' in session:
        role = session.get('ROLE')
        if role == 'Administrator':
            if request.method == 'POST':
                username = request.form['uname']
                password = request.form['pass']
                priv = request.form['privs']

                new_data = User(username, password, priv)
                db.session.add(new_data)
                db.session.commit()

                flash("User Created Successfully")
                return redirect(url_for('createUser'))
            elif request.method == 'GET':
                user_data = User.query.all()
                return render_template('user_creation.html',users = user_data)
        else:
            return render_template('forbidden_admin.html')

@app.route("/", methods=['GET','POST'])
def login():
    if request.method == "POST":
        fname = request.form['uname']
        fpass = request.form['pass']

        ch_user = User.query.filter_by(username = fname).first()

        if not ch_user:
            flash("User Doesn't exist")
            return redirect(url_for('login'))
        elif ch_user:
            password = ch_user.password
            role = ch_user.priv
            if password == fpass:
                session['ROLE'] = role
                return redirect(url_for('dhome'))
            else:
                flash("Wrong Username or Password")
                return redirect(url_for('login'))
                
        else:

            flash("Unknown error. Contact Admin")
    if request.method == 'GET':
        return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop("ROLE", None)
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.run()