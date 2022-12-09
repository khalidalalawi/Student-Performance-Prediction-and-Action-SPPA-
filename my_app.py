# -*- coding: utf-8 -*-



########################################### import ################################################################
from flask import Flask
from flask import render_template, request, redirect, url_for, session, flash
from functools import wraps
import mysql.connector as sql
from pandas import DataFrame
import pandas as p
import numpy as np
from sklearn.ensemble import RandomForestClassifier
#from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split

from sklearn.linear_model import LogisticRegression
from sklearn.neural_network import MLPClassifier

import pickle
import csv
from io import TextIOWrapper
from os.path import exists
from sklearn.metrics import f1_score, confusion_matrix, classification_report, precision_score, recall_score, roc_curve, auc
## Import warnings. Supress warnings (for  matplotlib)
import warnings
warnings.filterwarnings("ignore")
from sklearn.neighbors import KNeighborsClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import train_test_split, cross_val_score, KFold, LeaveOneOut, LeavePOut, StratifiedShuffleSplit
#from sklearn.model_selection import cross_val_predict
from sklearn.model_selection import GridSearchCV
#import json
#import re

import os # help me to delete pkl file




from flask import json, jsonify
from flask_mysqldb import MySQL,MySQLdb #pip install flask-mysqldb https://github.com/alexferl/flask-mysqldb


########################################### import ################################################################


#SSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSS


app = Flask(__name__) # application 'app' is object of class 'Flask'


#NNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNN

#SSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSS
#route.py
##############################################################################################
###################################### Home page ############################################################
##################################################################################################

######################################################################################################
######################################################################################################
####################################### Session and enforce login ####################################
# config


app.secret_key = '\xba\xb1+hV_P\x14\xca\xf7\xcf@\xb3)\x12'


app.config['UPLOAD_EXTENSIONS'] = ['.csv']


from datetime import timedelta



@app.before_request
def before_request():
    session.permanent = True
    app.permanent_session_lifetime = timedelta(hours = 1)


# login required decorator
def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('You need to login first.')
            return redirect(url_for('login'))
    return wrap

# login required decorator for std
def login_required_std(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'std' in session:
        #if 'logged_in' and 'std' in session:
            return f(*args, **kwargs)
        else:
            flash('You need to login first.')
            return redirect(url_for('login'))
    return wrap

####################################### End of Session and enforce login ##############################
######################################################################################################
######################################################################################################




@app.route('/')  # root : main page
@login_required
def home_page():
    # by default, 'render_template' looks inside the folder 'template'
    return render_template('home_page.html')


@app.route('/login', methods=['GET', 'POST'])  # root : main page
def login():
    if request.method == 'GET':
        return render_template('login.html')

    else: #POST
        user_name = request.form['user_name']
        password = request.form['password']

        con = sql.connect(host="pythonanywhere_host", user="pythonanywhere_user", password="pythonanywhere_password", database="pythonanywhere$database_name") #this is not the real connections details
        c =  con.cursor() # cursor



        query = "SELECT userName FROM users WHERE userName =%s LIMIT 1"
        query2 = "SELECT password FROM users WHERE userName =%s LIMIT 1"
        query3 = "SELECT teacher_or_std FROM users WHERE userName =%s LIMIT 1"
        values = (user_name)


        user= c.execute(query, (values,))
        #user = c.fetchall()
        user = [ row[0] for row in c.fetchall() if row[0] ] # i used this to return fetch the data without ()

        pas= c.execute(query2, (values,))
        #pas = c.fetchall()
        pas = [ row[0] for row in c.fetchall() if row[0] ] # i used this to return fetch the data without ()

        teacher_or_std= c.execute(query3, (values,))
        #pas = c.fetchall()
        teacher_or_std = [ row[0] for row in c.fetchall() if row[0] ] # i used this to return fetch the data without ()


        #user_array = np.array(user) # i conver list to array #user [0,0] is userName #user [0,1] is Passowrd

        #u=user_array[0,0]
        #p=user_array[0,1]




        if not user or not pas:
            login_error="invalid user name or password"
            #user=None
            return render_template('login.html', login_error=login_error)

        else:
            if (user_name==user[0] and password==pas[0] and teacher_or_std[0]=="std"):
                #session['logged_in'] = True
                session['std'] = True
                flash('You were logged in.')
                session["USERNAME"] = user[0]
                #return render_template('bar_chart.html')
                #return redirect(url_for('bar'))
                return redirect(url_for('std_dashboard1_choose_course'))

            elif (user_name==user[0] and password==pas[0] and teacher_or_std[0]=="teacher"):
                session['logged_in'] = True
                session['std'] = True
                #session['teacher'] = True
                flash('You were logged in.')
                session["USERNAME"] = user[0]
                return render_template('home_page.html')

            else:
                login_error="invalid user name or password"
                #user=None
                return render_template('login.html', login_error=login_error)




@app.route('/logout')
@login_required
def logout():
    session.pop('logged_in', None)
    flash('You were logged out.')
    return redirect(url_for('login'))


@app.route('/about_project')
@login_required
def about_project():
    return render_template('about_project.html')



@app.route('/contact_us')
@login_required
def contact_us():
    return render_template('contact_us.html')


@app.route('/about_project_std')
@login_required_std
def about_project_std():
    return render_template('about_project_std.html')



@app.route('/contact_us_std')
@login_required_std
def contact_us_std():
    return render_template('contact_us_std.html')



@app.route('/register', methods=['GET', 'POST'])  # root : main page
def register():
    if request.method == 'GET':
        return render_template('register.html')

    else: #POST
        user_name = request.form['usrname']
        password = request.form['psw']
        #return render_template('empty3.html', data = password)
        
        con = sql.connect(host="pythonanywhere_host", user="pythonanywhere_user", password="pythonanywhere_password", database="pythonanywhere$database_name") #this is not the real connections details
        c =  con.cursor() # cursor

        query = "SELECT userName FROM users where userName=%s"
        value = (user_name)
        c.execute(query,(value,))
        std_exsist_or_not = [ row[0] for row in c.fetchall() if row[0] ] # i used this to return fetch the data without ()
        #return render_template('empty3.html', data = std_exsist_or_not)

        if  std_exsist_or_not:
            return render_template('login2.html', data = "This username/student ID is already exists. Please log in. If you forgot you login information, please send email to khalid.alalawi@uon.edu.au")

        else:
            query2 = "INSERT IGNORE INTO users (userName, password, teacher_or_std) VALUES (%s, %s, %s)"
            value = (user_name, password, 'std')
            c.execute(query2,(value))
            con.commit() # apply changes

        return render_template('login2.html', data= "You are successfully signed up. Please log in with your credentials")


##############################################################################################
###################################### Map_Course_Offering_and_Assessment2 ############################################################
##################################################################################################





#NNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNN



#SSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSS
#create course

##############################################################################################
###################################### create course ############################################################
##################################################################################################



@app.route('/create_course', methods=['GET', 'POST'])
@login_required
def create_course():
    if request.method == 'GET':
        # send the form
        return render_template('create_course.html')

    else: # request.method == 'POST':
        # read data from the form and save in variable
        course_id = request.form['course_id']
        course_name = request.form['course_name']
        course_description = request.form['course_description']



        try:
            con = sql.connect(host="pythonanywhere_host", user="pythonanywhere_user", password="pythonanywhere_password", database="pythonanywhere$database_name") #this is not the real connections details
            c =  con.cursor() # cursor
            # insert data # REPLACE INTO: do as insert in do does except if the course_id already exist in the database it will replace it with the new record
            c.execute("insert IGNORE INTO course (course_id, course_name, course_description, userName) VALUES (%s,%s,%s,%s)", # REPLACE INTO: do as insert in do does except if the course_id already exist in the database it will replace it with the new record
                (course_id, course_name, course_description, session["USERNAME"]))
            con.commit() # apply changes
            # go to thanks page
            return render_template('createThanks_create_course.html')

        except sql.Error as e: # if error
            # then display the error in 'database_error.html' page
            return render_template('database_error.html', error=e)
        finally:

            con.close()


        return render_template('createThanks_create_course.html')




#NNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNN



#SSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSS
#create assessment.py
#\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\design_course\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
#this is the Get method to aviod two dynamic dropdown lists. Design a Course
@app.route('/create_assessment_choose_course', methods=['GET', 'Post'])
@login_required
def create_assessment_choose_course():
    if request.method == 'GET':
        try:
            con = sql.connect(host="pythonanywhere_host", user="pythonanywhere_user", password="pythonanywhere_password", database="pythonanywhere$database_name") #this is not the real connections details
            c =  con.cursor() # cursor
            query = "Select * from course where userName=%s"
            values = session["USERNAME"]
            cityList = c.execute(query, (values,))
            cityList = c.fetchall()

            return render_template('create_assessment_choose_course.html', cityList=cityList)

        except sql.Error as e: # if error
            # then display the error in 'database_error.html' page
            return render_template('database_error.html', error=e)

        finally:
            con.close() # close the connection

#this is for just to avoid two dynamic dropdown lists. this is the POST method from the Get method above: design_course
@app.route('/create_assessment_first',methods=['POST'])
@login_required
def create_assessment_first():

    courseName = request.form['course_course_id']
    #return render_template('empty3.html', data = courseName)

    try:
        con = sql.connect(host="pythonanywhere_host", user="pythonanywhere_user", password="pythonanywhere_password", database="pythonanywhere$database_name") #this is not the real connections details
        c =  con.cursor() # cursor



        query = "SELECT * FROM clo where userName=%s and course_course_id= %s order by auto_increment"
        values = (session["USERNAME"], courseName)
        clo = c.execute(query, values)
        clo = c.fetchall()



        return render_template('create_assessment.html', course_id=courseName, clo=clo)

    except sql.Error as e: # if error
        # then display the error in 'database_error.html' page
        return render_template('database_error.html', error=e)

    finally:

        con.close() # close the connection


##############################################################################################
###################################### create_assessment ############################################################
##################################################################################################

#create_assessment
@app.route('/create_assessment', methods=['GET', 'POST'])
@login_required
def create_assessment():
    if request.method == 'POST':
        # read data from the form and save in variable
        course_course_id = request.form['course_course_id']

        assessment_name = request.form['assessment_name']
        mark_out = request.form['mark_out']
        mark_worth = request.form['mark_worth']

        clo_checkbox = request.form.getlist('clo_checkbox')
        #return render_template('empty3.html', data = course_course_id)

        # store in database
        try:
            con = sql.connect(host="pythonanywhere_host", user="pythonanywhere_user", password="pythonanywhere_password", database="pythonanywhere$database_name") #this is not the real connections details
            c =  con.cursor() # cursor
            # insert data # REPLACE INTO: do as insert in do does except if the assessment_name (PK) already exist in the database it will replace it with the new record
            c.execute("insert IGNORE INTO assessment (assessment_name, course_course_id, mark_out, mark_worth) VALUES (%s,%s,%s,%s)", # REPLACE INTO: do as insert in do does except if the assessment_name (PK) already exist in the database it will replace it with the new record
                (assessment_name, course_course_id, mark_out, mark_worth))
            con.commit() # apply changes

            query = "SELECT auto_increment FROM assessment where assessment_name=%s and course_course_id=%s"
            values = (assessment_name , course_course_id)
            c.execute(query, values)
            assessment_auto_increment = [ r[0] for r in c.fetchall() if str(r[0]) ]
            #return render_template('empty3.html', data = assessment_auto_increment)


            for user in clo_checkbox:

                query = "SELECT auto_increment FROM clo where clo_name=%s and course_course_id=%s"
                values = (user , course_course_id)
                c.execute(query, values)
                clo_auto_increment = [ r[0] for r in c.fetchall() if str(r[0]) ]
                #return render_template('empty3.html', data = assessment_auto_increment)

                c.execute("insert IGNORE INTO allign_at_to_clo_m_to_m (clo_name, assessment_name, course_id, assessment_auto_increment, clo_auto_increment) VALUES (%s,%s,%s,%s,%s)", # REPLACE INTO: do as insert in do does except if the assessment_name (PK) already exist in the database it will replace it with the new record
                    (user, assessment_name, course_course_id, assessment_auto_increment [0], clo_auto_increment [0]))
                con.commit() # apply changes


            query = "SELECT * FROM clo where userName=%s and course_course_id= %s order by auto_increment"
            values = (session["USERNAME"], course_course_id)
            clo = c.execute(query, values)
            clo = c.fetchall()

            return render_template('create_assessment_after_adding_assessments.html', course_id=course_course_id, clo=clo)


        except sql.Error as e: # if error
            # then display the error in 'database_error.html' page
            return render_template('database_error.html', error=e)

        finally:
            con.close() # close the connection



#con = sql.connect(host="pythonanywhere_host", user="pythonanywhere_user", password="pythonanywhere_password", database="pythonanywhere$database_name") #this is not the real connections details

#the connection details are not real
app.config['MYSQL_HOST'] = 'MYSQL_HOST' 
app.config['MYSQL_USER'] = 'MYSQL_USER'
app.config['MYSQL_PASSWORD'] ='MYSQL_PASSWORD'
app.config['MYSQL_DB'] = 'MYSQL_DB'
app.config['MYSQL_CURSORCLASS'] = 'MYSQL_CURSORCLASS'

mysql = MySQL(app)

#this is for the dropdownlist in the predict_csv_simple_first.html (Javascript) to show assessments order
@app.route('/assessments55/<get_assessments>')
def assessmentsbycourse255(get_assessments):
    c = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    #get all assessments from database
    result = c.execute("SELECT * FROM studentPredictio$prediction.assessment WHERE course_course_id = %s  order by auto_increment", [get_assessments]) #SELECT * FROM prediction.assessment;
    assessments = c.fetchall()

    #to check how many records in this course
    records_in_course = c.execute("SELECT student_id FROM studentPredictio$prediction.student where course_course_id=%s", [get_assessments]) #SELECT * FROM students;
    records_in_course = c.fetchall()
    length_records_in_course = len(records_in_course)

    assessmentsArray = []
    for row in assessments:
        assessmentsObj = {
                'assessment_name': row['assessment_name'],
                'course_course_id': row['course_course_id']}

        assessmentsArray.append(assessmentsObj)
    return jsonify({'assessments_course' : assessmentsArray, 'length_records_in_course' : length_records_in_course })




#this is for the dropdownlist in the create_assessment.html (Javascript)
@app.route('/assessments/<get_assessments>')
def assessmentsbycourse2(get_assessments):
    c = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    #get all assessments from database
    result = c.execute("SELECT * FROM studentPredictio$prediction.assessment WHERE course_course_id = %s  order by auto_increment", [get_assessments]) #SELECT * FROM prediction.assessment;
    assessments = c.fetchall()

    #to check how many records in this course
    records_in_course = c.execute("SELECT student_id FROM studentPredictio$prediction.student where course_course_id=%s", [get_assessments]) #SELECT * FROM students;
    records_in_course = c.fetchall()
    length_records_in_course = len(records_in_course)

    assessmentsArray = []
    for row in assessments:
        assessmentsObj = {
                'assessment_name': row['assessment_name'],
                'course_course_id': row['course_course_id']}

        assessmentsArray.append(assessmentsObj)
    return jsonify({'assessments_course' : assessmentsArray, 'length_records_in_course' : length_records_in_course })



#this is for the dropdownlist in the create_model.html (Javascript)
@app.route('/check_creat_model/<get_assessments>')
def assessmentsbycoursexx(get_assessments):

    c = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    result = c.execute("SELECT * FROM studentPredictio$prediction.course_and_models WHERE course_id = %s", [get_assessments]) #SELECT * FROM prediction.assessment;


    assessments = c.fetchall()

    assessmentsArray = []
    for row in assessments:
        assessmentsObj = {
                'assessment_name': row['course_name'],
                'course_course_id': row['course_id']}

        assessmentsArray.append(assessmentsObj)
    return jsonify({'assessments_course' : assessmentsArray})

#2222222222222222222222222222

#this is for the dropdownlist in the create_clo.html (Javascript)
@app.route('/clo/<get_assessments>')
def assessmentsbycourse3(get_assessments):
    c = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    result = c.execute("SELECT * FROM clo WHERE course_course_id = %s  order by auto_increment", [get_assessments]) #SELECT * FROM prediction.assessment;
    assessments = c.fetchall()

    #to check how many records in this course
    records_in_course = c.execute("SELECT student_id FROM student where course_course_id=%s", [get_assessments]) #SELECT * FROM prediction.students;
    records_in_course = c.fetchall()
    length_records_in_course = len(records_in_course)

    assessmentsArray = []
    for row in assessments:
        assessmentsObj = {
                'assessment_name': row['clo_name'],
                'course_course_id': row['course_course_id']}

        assessmentsArray.append(assessmentsObj)
    return jsonify({'assessments_course' : assessmentsArray, 'length_records_in_course' : length_records_in_course })


#this is for the dropdownlist in the create_tla.html (Javascript)
@app.route('/tla/<get_assessments>')
def assessmentsbycourse4(get_assessments):
    c = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    result = c.execute("SELECT * FROM tla WHERE course_course_id = %s  order by tla_id", [get_assessments]) #SELECT * FROM prediction.assessment;
    assessments = c.fetchall()

    #to check how many records in this course
    records_in_course = c.execute("SELECT student_id FROM student where course_course_id=%s", [get_assessments]) #SELECT * FROM prediction.students;
    records_in_course = c.fetchall()
    length_records_in_course = len(records_in_course)

    assessmentsArray = []
    for row in assessments:
        assessmentsObj = {
                'lecture_or_lab': row['lecture_or_lab'],
                'lecture_lab_number': row['lecture_lab_number'],
                'assessment_name': row['tla_topic'],
                'course_course_id': row['course_course_id']}

        assessmentsArray.append(assessmentsObj)
    return jsonify({'assessments_course' : assessmentsArray, 'length_records_in_course' : length_records_in_course })



#this is for the dropdownlist in the map_ATs_to_TLAs.html (Javascript)
@app.route('/map_ATs_to_TLAs/<get_assessments>')
def assessmentsbycourse5(get_assessments):
    c = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    #result = c.execute("SELECT * FROM at_map_to_tla WHERE course_course_id = %s  order by auto_increment", [get_assessments]) #SELECT * FROM prediction.assessment;

    result = c.execute("SELECT t1.assessment_name,  t2.lecture_or_lab, t2.lecture_lab_number, t2.tla_topic FROM at_map_to_tla t1 INNER JOIN tla t2 ON t1.tla_id = t2.tla_id WHERE t1.course_course_id=%s order by auto_increment;", [get_assessments]) #SELECT * FROM prediction.assessment;
    assessments = c.fetchall()

    #to check how many records in this course
    records_in_course = c.execute("SELECT student_id FROM student where course_course_id=%s", [get_assessments]) #SELECT * FROM prediction.students;
    records_in_course = c.fetchall()
    length_records_in_course = len(records_in_course)

    assessmentsArray = []
    for row in assessments:
        assessmentsObj = {
                'assessment_name': row['assessment_name'],
                'lecture_or_lab': row['lecture_or_lab'],
                'lecture_lab_number': row['lecture_lab_number'],
                'tla_topic': row['tla_topic']}

        assessmentsArray.append(assessmentsObj)
    return jsonify({'assessments_course' : assessmentsArray, 'length_records_in_course' : length_records_in_course })


#NNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNN



#SSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSS
#Delete course.py

@app.route('/delete_course', methods=['GET', 'POST'])
@login_required
def delete_course():
    if request.method == 'GET':
        try:
            con = sql.connect(host="pythonanywhere_host", user="pythonanywhere_user", password="pythonanywhere_password", database="pythonanywhere$database_name") #this is not the real connections details
            c =  con.cursor() # cursor
            query = "Select * from course where userName=%s"
            values = session["USERNAME"]
            cityList = c.execute(query, (values,))
            cityList = c.fetchall()

            return render_template('delete_course.html', cityList=cityList)

        except sql.Error as e: # if error
            # then display the error in 'database_error.html' page
            return render_template('database_error.html', error=e)

        finally:
            con.close() # close the connection


    else: # request.method == 'POST':
        courseName = request.form['course_course_id']
        picklename = courseName

        try:
            con = sql.connect(host="pythonanywhere_host", user="pythonanywhere_user", password="pythonanywhere_password", database="pythonanywhere$database_name") #this is not the real connections details
            c =  con.cursor() # cursor
            c = con.cursor(buffered=True)

            ################################################################################################
            #here i want to know how many assessments in the selected course , so i can loop to delete the pkl file at the end
            #here I want to get all assessment in the selected course
            all_assessments_in_selected_course_query= "SELECT assessment_name  FROM assessment where course_course_id=%s order by auto_increment"
            values = (courseName)

            #here i want to fech all assessments from database for a specefic course [(course_id) from the function (function_create_dataset) parameter
            all_assessments_in_selected_course= c.execute(all_assessments_in_selected_course_query, (values,))
            all_assessments_in_selected_course = c.fetchall()

            # to get the length of all assessments for selected course (to know how many assessment in this course)
            length_all_assessments_in_selected_course= len(all_assessments_in_selected_course)

            ################################################################################################


            #delete  data from allign_at_to_clo_m_to_m table where course is ...
            query_delete_student_data = "DELETE FROM allign_at_to_clo_m_to_m WHERE course_id=%s"
            value_delete_student_data = courseName
            c.execute(query_delete_student_data, (value_delete_student_data,))
            con.commit() # apply changes


            #delete data from allign_tla_to_at_m_to_m table where course is ...
            query_delete_student_data = "DELETE FROM allign_tla_to_at_m_to_m WHERE course_id=%s"
            value_delete_student_data = courseName
            c.execute(query_delete_student_data, (value_delete_student_data,))
            con.commit() # apply changes


            #delete  data from allign_tla_to_clo_m_to_m table where course is ...
            query_delete_student_data = "DELETE FROM allign_tla_to_clo_m_to_m WHERE course_id=%s"
            value_delete_student_data = courseName
            c.execute(query_delete_student_data, (value_delete_student_data,))
            con.commit() # apply changes

            #delete assessment from clo table where course is ...
            query_delete_assessment = "DELETE FROM clo WHERE course_course_id=%s"
            value_delete_assessment = courseName
            c.execute(query_delete_assessment, (value_delete_assessment,))
            con.commit() # apply changes



            #delete assessment from student_prediction_results table where course is ...
            query_delete_assessment = "DELETE FROM student_prediction_results WHERE course_id=%s"
            value_delete_assessment = courseName
            c.execute(query_delete_assessment, (value_delete_assessment,))
            con.commit() # apply changes

            #delete assessment from student_grade table where course is ...
            query_delete_assessment = "DELETE FROM student_grade WHERE course_id=%s"
            value_delete_assessment = courseName
            c.execute(query_delete_assessment, (value_delete_assessment,))
            con.commit() # apply changes


            #delete assessment from current_student table where course is ...
            query_delete_assessment = "DELETE FROM current_student WHERE course_id=%s"
            value_delete_assessment = courseName
            c.execute(query_delete_assessment, (value_delete_assessment,))
            con.commit() # apply changes




            #delete assessment from assessment table where course is ...
            query_delete_assessment = "DELETE FROM assessment WHERE course_course_id=%s"
            value_delete_assessment = courseName
            c.execute(query_delete_assessment, (value_delete_assessment,))
            con.commit() # apply changes


            #delete course from course table where course is ...
            query_delete_course = "DELETE FROM course WHERE course_id=%s"
            value_delete_course = courseName
            c.execute(query_delete_course, (value_delete_course,))
            con.commit() # apply changes




            #here i want to look if there are pkl file (models) that have been created or not for the selected course. if there are pkle, i want to delte them
            #if exists(picklename+"_RF_Multiclass_model_4.pkl" or picklename+"_RF_Multiclass_model_3.pkl" or picklename+"_RF_Multiclass_model_2.pkl" or picklename+"_RF_Multiclass_model_1.pkl" or picklename+"_RF_Binary_model_4.pkl" or picklename+"_RF_Binary_model_3.pkl" or picklename+"_RF_Binary_model_2.pkl" or picklename+"_RF_Binary_model_1.pkl"):
            if exists(picklename+"_RF_Multiclass_model_1.pkl" or picklename+"_RF_Multiclass_model_1.pkl" or picklename+"_KNN_Multiclass_model_1.pkl" or picklename+"_KNN_Binary_model_1.pkl" or picklename+"_SVM_Multiclass_model_1.pkl" or picklename+"_SVM_Binary_model_1.pkl" or picklename+"_NB_Multiclass_model_1.pkl" or picklename+"_NB_Binary_model_1.pkl"):
                for i in range(length_all_assessments_in_selected_course):

                    #here i want delete all models for all ML algotrithms (binary and multiclass)
                    #os.remove remove files
                    os.remove(picklename+"_RF_Multiclass_model_" +  str(i+1)+".pkl")
                    os.remove(picklename+"_RF_Binary_model_" +  str(i+1)+".pkl")

                    os.remove(picklename+"_SVM_Multiclass_model_" +  str(i+1)+".pkl")
                    os.remove(picklename+"_SVM_Binary_model_" +  str(i+1)+".pkl")

                    os.remove(picklename+"_KNN_Multiclass_model_" +  str(i+1)+".pkl")
                    os.remove(picklename+"_KNN_Binary_model_" +  str(i+1)+".pkl")

                    os.remove(picklename+"_NB_Multiclass_model_" +  str(i+1)+".pkl")
                    os.remove(picklename+"_NB_Binary_model_" +  str(i+1)+".pkl")

                    os.remove(picklename+"_DT_Multiclass_model_" +  str(i+1)+".pkl")
                    os.remove(picklename+"_DT_Binary_model_" +  str(i+1)+".pkl")

            #delete all data [models performance] for selected course from the course_and_models Table
            query_delete_course_and_models_data = "DELETE FROM course_and_models WHERE course_id=%s"
            value_delete_course_and_models_data = courseName
            c.execute(query_delete_course_and_models_data, (value_delete_course_and_models_data,))
            con.commit() # apply changes


            query_delete_models_performance_data = "DELETE FROM models_performance WHERE course_id=%s"
            value_delete_models_performance_data = courseName
            c.execute(query_delete_models_performance_data, (value_delete_models_performance_data,))
            con.commit() # apply changes




            return render_template('createThanks_delete_course.html')

        except sql.Error as e: # if error
            # then display the error in 'database_error.html' page
            return render_template('database_error.html', error=e)

        finally:
            con.close() # close the connection


#NNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNN













#SSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSS
#create model.py



##############################################################################################
######################################create model ############################################################
##################################################################################################




##############################################################################################
###################################### Two functions to create the dataset (x,y) [Binary & Multiclass] ############################################################
##################################################################################################


def function_create_dataset_for_Multiclass (course_id): # here i want to create the dataset (x,y) that i am going to use when creating multiclass models

    con = sql.connect(host="pythonanywhere_host", user="pythonanywhere_user", password="pythonanywhere_password", database="pythonanywhere$database_name") #this is not the real connections details
    c =  con.cursor() # cursor
    c = con.cursor(buffered=True)

    #here I want to get all assessment in the selected course to know how many assessments in the selected course, so i can create models based on number of assessments there -1 (without the final exam)
    all_assessments_in_selected_course_query= "SELECT assessment_name  FROM assessment where course_course_id=%s order by auto_increment"
    values = (course_id)

    #here i want to fech all assessments from database for a specefic course [(course_id) from the function (function_create_dataset) parameter
    all_assessments_in_selected_course= c.execute(all_assessments_in_selected_course_query, (values,))
    all_assessments_in_selected_course = c.fetchall()

    # to get the length of all assessments for selected course (to know how many assessment in this course)
    length_all_assessments_in_selected_course= len(all_assessments_in_selected_course)



    assessment=[] # to append all colomn (assessment) in the database in  one list here
    for i in range(length_all_assessments_in_selected_course): # this for loop is to append all colomn (assessment) in the database in one list
        q="select mark from assessment_std where assessment_course_course_id = %s and assessment_assessment_name =%s" #q=query
        new_all_assessments_in_selected_course = ",".join(all_assessments_in_selected_course[i]) #to solve error "python mysqlconnector mysqlinterfaceerror python type tuple cannot be converted"
        v = (course_id, new_all_assessments_in_selected_course )  #v=value
        c.execute(q, v)
        assessment_fetch  = [ row[0] for row in c.fetchall() if str(row[0]) ] # i used this to return fetch the data without (). I also used str(row[0]) to make sure it does not miss any int 0
        assessment.append(assessment_fetch)

    ###################################################################### total
    #to get all students grade (total grade) for (where condition) course INFT2031
    query_total = "SELECT total FROM student where course_course_id=%s"
    values = (course_id)   #############################################################################
    total = c.execute(query_total, (values,))
    total = [ row[0] for row in c.fetchall() if str(row[0]) ] # i used this to return fetch the data without (). I also used str(row[0]) to make sure it does not miss any int 0

    ###################################################################### pass_or_fail
    #to get all students grade (pass_or_fail grade) for (where condition) course INFT2031
    query_pass_or_fail = "SELECT pass_or_fail FROM student where course_course_id=%s"
    values = (course_id)   #############################################################################
    pass_or_fail = c.execute(query_pass_or_fail, (values,))
    pass_or_fail = [ row[0] for row in c.fetchall() if str(row[0]) ] # i used this to return fetch the data without () . I also used str(row[0]) to make sure it does not miss any int 0

    ###################################################################### multiclass_levels
    #to get all students grade (multiclass_levels grade) for (where condition) course INFT2031
    query_multiclass_levels = "SELECT multiclass_levels FROM student where course_course_id=%s"
    values = (course_id)   #############################################################################
    multiclass_levels = c.execute(query_multiclass_levels, (values,))
    multiclass_levels = [ row[0] for row in c.fetchall() if row[0] ] # i used this to return fetch the data without ()





    # to create dataframe df for (total, pass_or_fail, multiclass_levels)
    df = DataFrame(list(zip(total, pass_or_fail, multiclass_levels)),
        columns =['total' ,'pass_or_fail' , 'multiclass_levels'])


    #loop to add each assessment to the dataframe because fd above does not have the assessments yet
    a=0
    for i in assessment:
        #df [i]= assessment[a]
        df['assessment '+str(a+1)] = p.Series(assessment[a])  # i used p.Series to overcome error "Length of Values Does Not Match Length of Index"
        a=a+1

    # if there are NaN in the data fill them with 0 # i used this because sometimes when loading data a problem could happen and some colomns does not fully load
    df=df.fillna(0)

    #99999999999999999999999999999999999999999999999999999999999999999999999999999999999
    #clean the dataframe (dataset) based in two criteria
    ## student who fail and didn't attent the final exam
    #this could work but still does not work
    first_criteria= df[(df.iloc[ : , length_all_assessments_in_selected_course+2 ]==0) & (df.loc[ : , 'pass_or_fail' ]==0)]    # here i tried this: length_all_assessments_in_selected_course+2 because the dataframe start with total, passorfail, multilevel. iloc start with 0
    df = df.drop(first_criteria.index)

    ## student who drop out from the beginning
    second_criteria=df.query("total==0")
    second_criteria.index
    df = df.drop(second_criteria.index )
    ############## end of cleaning Section
    #99999999999999999999999999999999999999999999999999999999999999999999999999999999999


    # to get rid of the final exam and pass_or_fail and the target value multiclass_levels
    # also to make the dataset split ready
    X = df.drop([ 'total', 'pass_or_fail', 'multiclass_levels'] ,1).to_numpy() # ('assessment '+ str(len(assessment))) to remove final exam from the df
    y = df['multiclass_levels'].to_numpy()

    # here i split the dataset and make X_train, X_test, y_train, y_test, then create the RF model
    #X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.33, random_state=42)

    #return (X_train, X_test, y_train, y_test)
    length_of_dataset_after_cleaning = len(y)

    return (X, y, length_of_dataset_after_cleaning) # i just want to return x and y to use cross validation instead of spliting the dataset




def function_create_dataset_for_Binary_model (course_id):# here i want to create the dataset (x,y) that i am going to use when creating Binary models

    con = sql.connect(host="pythonanywhere_host", user="pythonanywhere_user", password="pythonanywhere_password", database="pythonanywhere$database_name") #this is not the real connections details
    c =  con.cursor() # cursor
    c = con.cursor(buffered=True)

    #here I want to get all assessment in the selected course and see how many assessment there
    #all_assessments_in_selected_course_query= "SELECT assessment_name  FROM assessment where course_course_id=%s order by auto_increment"
    all_assessments_in_selected_course_query= "SELECT assessment_name  FROM assessment where course_course_id=%s order by auto_increment"
    values = (course_id)

    #here i want to fech all assessments from database for a specefic course [(course_id) from the function (function_create_dataset) parameter
    all_assessments_in_selected_course= c.execute(all_assessments_in_selected_course_query, (values,))
    all_assessments_in_selected_course = c.fetchall()

    # to get the length of all assessments for selected course (to know how many assessment in this course)
    length_all_assessments_in_selected_course= len(all_assessments_in_selected_course)



    assessment=[] # to append all colomn (assessment) in the database in  one list here
    for i in range(length_all_assessments_in_selected_course): # this for loop is to append all colomn (assessment) in the database in one list
        q="select mark from assessment_std where assessment_course_course_id = %s and assessment_assessment_name =%s"
        new_all_assessments_in_selected_course = ",".join(all_assessments_in_selected_course[i]) #to solve error "python mysqlconnector mysqlinterfaceerror python type tuple cannot be converted"
        v = (course_id, new_all_assessments_in_selected_course )
        c.execute(q, v)
        assessment_fetch  = [ row[0] for row in c.fetchall() if str(row[0]) ] # i used this to return fetch the data without (). I also used str(row[0]) to make sure it does not miss any int 0
        assessment.append(assessment_fetch)

    ###################################################################### total
    #to get all students grade (total grade) for (where condition) course INFT2031
    query_total = "SELECT total FROM student where course_course_id=%s"
    values = (course_id)   #############################################################################
    total = c.execute(query_total, (values,))
    total = [ row[0] for row in c.fetchall() if str(row[0]) ] # i used this to return fetch the data without (). I also used str(row[0]) to make sure it does not miss any int 0

    ###################################################################### pass_or_fail
    #to get all students grade (pass_or_fail grade) for (where condition) course INFT2031
    query_pass_or_fail = "SELECT pass_or_fail FROM student where course_course_id=%s"
    values = (course_id)   #############################################################################
    pass_or_fail = c.execute(query_pass_or_fail, (values,))
    pass_or_fail = [ row[0] for row in c.fetchall() if str(row[0]) ] # i used this to return fetch the data without () . I also used str(row[0]) to make sure it does not miss any int 0

    ###################################################################### multiclass_levels
    #to get all students grade (multiclass_levels grade) for (where condition) course INFT2031
    query_multiclass_levels = "SELECT multiclass_levels FROM student where course_course_id=%s"
    values = (course_id)   #############################################################################
    multiclass_levels = c.execute(query_multiclass_levels, (values,))
    multiclass_levels = [ row[0] for row in c.fetchall() if row[0] ] # i used this to return fetch the data without ()


    # to create dataframe df for (total, pass_or_fail, multiclass_levels)
    df = DataFrame(list(zip(total, pass_or_fail, multiclass_levels)),
        columns =['total' ,'pass_or_fail' , 'multiclass_levels'])


    #loop to add each assessment to the dataframe
    a=0
    for i in assessment:
        #df [i]= assessment[a]
        df['assessment '+str(a+1)] = p.Series(assessment[a])  # i used p.Series to overcome error "Length of Values Does Not Match Length of Index"
        a=a+1

    # if there are NaN in the data fill them with 0 # i used this because sometimes when loading data a problem could happen and some colomns does not fully load
    df=df.fillna(0)

    #99999999999999999999999999999999999999999999999999999999999999999999999999999999999
    #clean the dataframe (dataset) based in two criteria
    ## student who fail and didn't attent the final exam
    first_criteria= df[(df.iloc[ : , length_all_assessments_in_selected_course+2 ]==0) & (df.loc[ : , 'pass_or_fail' ]==0)]    # here i tried this: length_all_assessments_in_selected_course+2 because the dataframe start with total, passorfail, multilevel. iloc start with 0
    df = df.drop(first_criteria.index)


    ## student who drop out from the beginning
    second_criteria=df.query("total==0")
    second_criteria.index
    df = df.drop(second_criteria.index )
    ############## end of cleaning Section
    #99999999999999999999999999999999999999999999999999999999999999999999999999999999999


    # to get rid of the final exam and pass_or_fail and the target value multiclass_levels
    # also to make the dataset split ready
    X = df.drop([ 'total', 'pass_or_fail', 'multiclass_levels'] ,1).to_numpy() # ('assessment '+ str(len(assessment))) to remove final exam from the df
    y = df['pass_or_fail'].to_numpy()

    length_of_dataset_after_cleaning = len(y)

    return (X, y, length_of_dataset_after_cleaning) # i just want to return x and y to use cross validation instead of spliting the dataset


#####################################################################################################################################
#####################################################################################################################################
#####################################################################################################################################
################  creating models [binary and multiclass] using CV & hyperparameter tuning ################
#RF


def create_multiple_Multiclass_models_RF (courseName, x, y):

        #to get all students mark in assessment 1 for (where condition) course INFT2031
        con = sql.connect(host="pythonanywhere_host", user="pythonanywhere_user", password="pythonanywhere_password", database="pythonanywhere$database_name") #this is not the real connections details
        c =  con.cursor() # cursor
        c = con.cursor(buffered=True)


        #here I want to get all assessment in the selected course
        all_assessments_in_selected_course_query= "SELECT assessment_name  FROM assessment where course_course_id=%s order by auto_increment"
        values = (courseName)

        #here i want to fech all assessments from database for a specefic course [(course_id) from the function (function_create_dataset) parameter
        all_assessments_in_selected_course= c.execute(all_assessments_in_selected_course_query, (values,))
        all_assessments_in_selected_course = c.fetchall()

        # to get the length of all assessments for selected course (to know how many assessment in this course)
        length_all_assessments_in_selected_course= len(all_assessments_in_selected_course)


        #here to create new model
        list_model_accuracy= [] # create list to contain all acc for all models we want to create
        list_model_f1=[]
        list_model_recall=[]
        list_model_precision= []

        picklename = courseName
        list_model_name= [] # to add each model with pickle_i.pkl
        z=0         #to keep track of list_model_name
        h=length_all_assessments_in_selected_course         #to keep track of picklename
        np.random.seed(42)
        w=length_all_assessments_in_selected_course

        #grid_param Dictionary type for hypertuning
        grid_param = {'solver' : ['newton-cg', 'lbfgs', 'liblinear'],
                      'penalty' : ['l1', 'l2'],
                      'C' : [0.001,0.01,0.1,1,10,100]}

        #model = SVC()
        model = LogisticRegression(random_state=0)

        ###################### hypertuning ##############################

        gd_sr = GridSearchCV(estimator=model,
                 param_grid=grid_param,
                 scoring='accuracy', #33333333333333333333333333accuracy
                 cv=5)



        for i in range(length_all_assessments_in_selected_course):
            np.random.seed(42)

            gd_sr.fit(x, y)

            model = gd_sr.best_estimator_

            ###################### hypertuning ##############################

            #accuracy
            model_accuracy = cross_val_score(model, x, y, scoring="accuracy", cv=5)
            model_accuracy= round(model_accuracy.mean(), 3)
            list_model_accuracy.append(model_accuracy) # to append all accuracy in a list

            #f1
            model_f1 = cross_val_score(model, x, y, scoring="f1_weighted", cv=5)
            model_f1= round(model_f1.mean(), 3)
            list_model_f1.append(model_f1) # to append all accuracy in a list

            #recall
            model_recall = cross_val_score(model, x, y, scoring="recall_weighted", cv=5)
            model_recall= round(model_recall.mean(), 3)
            list_model_recall.append(model_recall) # to append all accuracy in a list


            #precision
            model_precision = cross_val_score(model, x, y, scoring="precision_weighted", cv=5)
            model_precision= round(model_precision.mean(), 3)
            list_model_precision.append(model_precision) # to append all accuracy in a list

            model = model.fit(x, y) # i fit my model with all my dataset after i used CV to check the performance. I have to do that in order to use .predict function in the prediction_file.py


            list_model_name.append(model) # to append all accuracy in a list

            pickle.dump(list_model_name[z], open(picklename+"_RF_Multiclass_model_" +  str(h)+".pkl" ,'wb'))

            if w==1:
                break

            x = np.delete(x, w-1, 1)
            #X_train = np.delete(X_train, w-1, 1)
            #X_test  = np.delete(X_test, w-1, 1)

            z=z+1
            h=h-1
            w=w-1

        #to send how many models we created
        number_of_model_created_for_Multiclass_models = length_all_assessments_in_selected_course - 1 #to send how many model have been created

        return (list_model_accuracy, list_model_f1, list_model_recall, list_model_precision,  number_of_model_created_for_Multiclass_models)


def create_multiple_Binary_models_RF (courseName, x, y):

        #to get all students mark in assessment 1 for (where condition) course INFT2031
        con = sql.connect(host="pythonanywhere_host", user="pythonanywhere_user", password="pythonanywhere_password", database="pythonanywhere$database_name") #this is not the real connections details
        c =  con.cursor() # cursor
        c = con.cursor(buffered=True)


        #here I want to get all assessment in the selected course
        all_assessments_in_selected_course_query= "SELECT assessment_name  FROM assessment where course_course_id=%s order by auto_increment"
        values = (courseName)

        #here i want to fech all assessments from database for a specefic course [(course_id) from the function (function_create_dataset) parameter
        all_assessments_in_selected_course= c.execute(all_assessments_in_selected_course_query, (values,))
        all_assessments_in_selected_course = c.fetchall()

        # to get the length of all assessments for selected course (to know how many assessment in this course)
        length_all_assessments_in_selected_course= len(all_assessments_in_selected_course)


        #here to create new model
        list_model_accuracy= [] # create list to contain all acc for all models we want to create
        list_model_f1=[]
        list_model_recall=[]
        list_model_precision= []

        picklename = courseName
        list_model_name= [] # to add each model with pickle_i.pkl
        z=0         #to keep track of list_model_name
        h=length_all_assessments_in_selected_course         #to keep track of picklename
        np.random.seed(42)
        w=length_all_assessments_in_selected_course

        #grid_param Dictionary type for hypertuning
        grid_param = {'solver' : ['newton-cg', 'lbfgs', 'liblinear'],
                      'penalty' : ['l1', 'l2'],
                      'C' : [0.001,0.01,0.1,1,10,100]}

        #model = SVC()
        model = LogisticRegression(random_state=0)

        ###################### hypertuning ##############################

        gd_sr = GridSearchCV(estimator=model,
                 param_grid=grid_param,
                 scoring='accuracy', #33333333333333333333333333accuracy
                 cv=5)

        for i in range(length_all_assessments_in_selected_course):
            np.random.seed(42)



            gd_sr.fit(x, y)

            model = gd_sr.best_estimator_

            ###################### hypertuning ##############################


            #accuracy
            model_accuracy = cross_val_score(model, x, y, scoring="accuracy", cv=5)
            model_accuracy= round(model_accuracy.mean(), 3)
            list_model_accuracy.append(model_accuracy) # to append all accuracy in a list

            #f1
            model_f1 = cross_val_score(model, x, y, scoring="f1", cv=5)
            model_f1= round(model_f1.mean(), 3)
            list_model_f1.append(model_f1) # to append all accuracy in a list

            #recall
            model_recall = cross_val_score(model, x, y, scoring="recall", cv=5)
            model_recall= round(model_recall.mean(), 3)
            list_model_recall.append(model_recall) # to append all accuracy in a list


            #precision
            model_precision = cross_val_score(model, x, y, scoring="precision", cv=5)
            model_precision= round(model_precision.mean(), 3)
            list_model_precision.append(model_precision) # to append all accuracy in a list

            model = model.fit(x, y) # i fit my model with all my dataset after i used CV to check the performance. I have to do that in order to use .predict function in the prediction_file.py


            list_model_name.append(model) # to append all accuracy in a list

            pickle.dump(list_model_name[z], open(picklename+"_RF_Binary_model_" +  str(h)+".pkl" ,'wb'))

            if w==1:
                break

            x = np.delete(x, w-1, 1)
            #X_train = np.delete(X_train, w-1, 1)
            #X_test  = np.delete(X_test, w-1, 1)

            z=z+1
            h=h-1
            w=w-1

        #to send how many models we created
        number_of_model_created_for_Binary_models = length_all_assessments_in_selected_course - 1 #to send how many model have been created

        return (list_model_accuracy, list_model_f1, list_model_recall, list_model_precision,  number_of_model_created_for_Binary_models)


#####################################################################################################################################
#####################################################################################################################################
#####################################################################################################################################

#SVM

def create_multiple_Multiclass_models_SVM (courseName, x, y):

        #to get all students mark in assessment 1 for (where condition) course INFT2031
        con = sql.connect(host="pythonanywhere_host", user="pythonanywhere_user", password="pythonanywhere_password", database="pythonanywhere$database_name") #this is not the real connections details
        c =  con.cursor() # cursor
        c = con.cursor(buffered=True)


        #here I want to get all assessment in the selected course
        all_assessments_in_selected_course_query= "SELECT assessment_name  FROM assessment where course_course_id=%s order by auto_increment"
        values = (courseName)

        #here i want to fech all assessments from database for a specefic course [(course_id) from the function (function_create_dataset) parameter
        all_assessments_in_selected_course= c.execute(all_assessments_in_selected_course_query, (values,))
        all_assessments_in_selected_course = c.fetchall()

        # to get the length of all assessments for selected course (to know how many assessment in this course)
        length_all_assessments_in_selected_course= len(all_assessments_in_selected_course)


        #here to create new model
        list_model_accuracy= [] # create list to contain all acc for all models we want to create
        list_model_f1=[]
        list_model_recall=[]
        list_model_precision= []

        picklename = courseName
        list_model_name= [] # to add each model with pickle_i.pkl
        z=0         #to keep track of list_model_name
        h=length_all_assessments_in_selected_course         #to keep track of picklename
        np.random.seed(42)
        w=length_all_assessments_in_selected_course

        #grid_param Dictionary type for hypertuning
        grid_param = {'C': [1, 10, 100],
                      'gamma': [1, 0.1, 0.01, 0.001],
                      'kernel': ['rbf']}

        model = SVC()

        ###################### hypertuning ##############################

        gd_sr = GridSearchCV(estimator=model,
                 param_grid=grid_param,
                 scoring='accuracy', #33333333333333333333333333accuracy
                 cv=5)

        for i in range(length_all_assessments_in_selected_course):
            np.random.seed(42)

            gd_sr.fit(x, y)

            model = gd_sr.best_estimator_

            ###################### hypertuning ##############################

            #accuracy
            model_accuracy = cross_val_score(model, x, y, scoring="accuracy", cv=5)
            model_accuracy= round(model_accuracy.mean(), 3)
            list_model_accuracy.append(model_accuracy) # to append all accuracy in a list

            #f1
            model_f1 = cross_val_score(model, x, y, scoring="f1_weighted", cv=5)
            model_f1= round(model_f1.mean(), 3)
            list_model_f1.append(model_f1) # to append all accuracy in a list

            #recall
            model_recall = cross_val_score(model, x, y, scoring="recall_weighted", cv=5)
            model_recall= round(model_recall.mean(), 3)
            list_model_recall.append(model_recall) # to append all accuracy in a list


            #precision
            model_precision = cross_val_score(model, x, y, scoring="precision_weighted", cv=5)
            model_precision= round(model_precision.mean(), 3)
            list_model_precision.append(model_precision) # to append all accuracy in a list

            model = model.fit(x, y) # i fit my model with all my dataset after i used CV to check the performance. I have to do that in order to use .predict function in the prediction_file.py


            list_model_name.append(model) # to append all accuracy in a list

            pickle.dump(list_model_name[z], open(picklename+"_SVM_Multiclass_model_" +  str(h)+".pkl" ,'wb'))

            if w==1:
                break

            x = np.delete(x, w-1, 1)
            #X_train = np.delete(X_train, w-1, 1)
            #X_test  = np.delete(X_test, w-1, 1)

            z=z+1
            h=h-1
            w=w-1

        #to send how many models we created
        number_of_model_created_for_Multiclass_models = length_all_assessments_in_selected_course - 1 #to send how many model have been created

        return (list_model_accuracy, list_model_f1, list_model_recall, list_model_precision,  number_of_model_created_for_Multiclass_models)


def create_multiple_Binary_models_SVM (courseName, x, y):

        #to get all students mark in assessment 1 for (where condition) course INFT2031
        con = sql.connect(host="pythonanywhere_host", user="pythonanywhere_user", password="pythonanywhere_password", database="pythonanywhere$database_name") #this is not the real connections details
        c =  con.cursor() # cursor
        c = con.cursor(buffered=True)


        #here I want to get all assessment in the selected course
        all_assessments_in_selected_course_query= "SELECT assessment_name  FROM assessment where course_course_id=%s order by auto_increment"
        values = (courseName)

        #here i want to fech all assessments from database for a specefic course [(course_id) from the function (function_create_dataset) parameter
        all_assessments_in_selected_course= c.execute(all_assessments_in_selected_course_query, (values,))
        all_assessments_in_selected_course = c.fetchall()

        # to get the length of all assessments for selected course (to know how many assessment in this course)
        length_all_assessments_in_selected_course= len(all_assessments_in_selected_course)


        #here to create new model
        list_model_accuracy= [] # create list to contain all acc for all models we want to create
        list_model_f1=[]
        list_model_recall=[]
        list_model_precision= []

        picklename = courseName
        list_model_name= [] # to add each model with pickle_i.pkl
        z=0         #to keep track of list_model_name
        h=length_all_assessments_in_selected_course         #to keep track of picklename
        np.random.seed(42)
        w=length_all_assessments_in_selected_course

        #grid_param Dictionary type for hypertuning
        grid_param = {'C': [1, 10, 100],
                      'gamma': [1, 0.1, 0.01, 0.001],
                      'kernel': ['rbf']}

        model = SVC()

        ###################### hypertuning ##############################

        gd_sr = GridSearchCV(estimator=model,
        		 param_grid=grid_param,
        		 scoring='accuracy', #33333333333333333333333333accuracy
        		 cv=5)

        for i in range(length_all_assessments_in_selected_course):
            np.random.seed(42)



            gd_sr.fit(x, y)

            model = gd_sr.best_estimator_

            ###################### hypertuning ##############################


            #accuracy
            model_accuracy = cross_val_score(model, x, y, scoring="accuracy", cv=5)
            model_accuracy= round(model_accuracy.mean(), 3)
            list_model_accuracy.append(model_accuracy) # to append all accuracy in a list

            #f1
            model_f1 = cross_val_score(model, x, y, scoring="f1", cv=5)
            model_f1= round(model_f1.mean(), 3)
            list_model_f1.append(model_f1) # to append all accuracy in a list

            #recall
            model_recall = cross_val_score(model, x, y, scoring="recall", cv=5)
            model_recall= round(model_recall.mean(), 3)
            list_model_recall.append(model_recall) # to append all accuracy in a list


            #precision
            model_precision = cross_val_score(model, x, y, scoring="precision", cv=5)
            model_precision= round(model_precision.mean(), 3)
            list_model_precision.append(model_precision) # to append all accuracy in a list

            model = model.fit(x, y) # i fit my model with all my dataset after i used CV to check the performance. I have to do that in order to use .predict function in the prediction_file.py


            list_model_name.append(model) # to append all accuracy in a list

            pickle.dump(list_model_name[z], open(picklename+"_SVM_Binary_model_" +  str(h)+".pkl" ,'wb'))

            if w==1:
                break

            x = np.delete(x, w-1, 1)
            #X_train = np.delete(X_train, w-1, 1)
            #X_test  = np.delete(X_test, w-1, 1)

            z=z+1
            h=h-1
            w=w-1

        #to send how many models we created
        number_of_model_created_for_Binary_models = length_all_assessments_in_selected_course - 1 #to send how many model have been created

        return (list_model_accuracy, list_model_f1, list_model_recall, list_model_precision,  number_of_model_created_for_Binary_models)



#####################################################################################################################################
#####################################################################################################################################
#####################################################################################################################################

#KNN

def create_multiple_Multiclass_models_KNN (courseName, x, y):

        #to get all students mark in assessment 1 for (where condition) course INFT2031
        con = sql.connect(host="pythonanywhere_host", user="pythonanywhere_user", password="pythonanywhere_password", database="pythonanywhere$database_name") #this is not the real connections details
        c =  con.cursor() # cursor
        c = con.cursor(buffered=True)


        #here I want to get all assessment in the selected course
        all_assessments_in_selected_course_query= "SELECT assessment_name  FROM assessment where course_course_id=%s order by auto_increment"
        values = (courseName)

        #here i want to fech all assessments from database for a specefic course [(course_id) from the function (function_create_dataset) parameter
        all_assessments_in_selected_course= c.execute(all_assessments_in_selected_course_query, (values,))
        all_assessments_in_selected_course = c.fetchall()

        # to get the length of all assessments for selected course (to know how many assessment in this course)
        length_all_assessments_in_selected_course= len(all_assessments_in_selected_course)


        #here to create new model
        list_model_accuracy= [] # create list to contain all acc for all models we want to create
        list_model_f1=[]
        list_model_recall=[]
        list_model_precision= []

        picklename = courseName
        list_model_name= [] # to add each model with pickle_i.pkl
        z=0         #to keep track of list_model_name
        h=length_all_assessments_in_selected_course         #to keep track of picklename
        np.random.seed(42)
        w=length_all_assessments_in_selected_course

        #grid_param Dictionary type for hypertuning
        grid_param = {'n_neighbors': [3, 5, 7, 9], # usually odd numbers
        			  'leaf_size':[1,3,5],
                      'algorithm':['auto', 'kd_tree']}


        for i in range(length_all_assessments_in_selected_course):
            np.random.seed(42)


            model = KNeighborsClassifier()

            ###################### hypertuning ##############################

            gd_sr = GridSearchCV(estimator=model,
            		 param_grid=grid_param,
            		 scoring='accuracy', #33333333333333333333333333accuracy
            		 cv=5)

            gd_sr.fit(x, y)

            model = gd_sr.best_estimator_

            ###################### hypertuning ##############################

            #accuracy
            model_accuracy = cross_val_score(model, x, y, scoring="accuracy", cv=5)
            model_accuracy= round(model_accuracy.mean(), 3)
            list_model_accuracy.append(model_accuracy) # to append all accuracy in a list

            #f1
            model_f1 = cross_val_score(model, x, y, scoring="f1_weighted", cv=5)
            model_f1= round(model_f1.mean(), 3)
            list_model_f1.append(model_f1) # to append all accuracy in a list

            #recall
            model_recall = cross_val_score(model, x, y, scoring="recall_weighted", cv=5)
            model_recall= round(model_recall.mean(), 3)
            list_model_recall.append(model_recall) # to append all accuracy in a list


            #precision
            model_precision = cross_val_score(model, x, y, scoring="precision_weighted", cv=5)
            model_precision= round(model_precision.mean(), 3)
            list_model_precision.append(model_precision) # to append all accuracy in a list

            model = model.fit(x, y) # i fit my model with all my dataset after i used CV to check the performance. I have to do that in order to use .predict function in the prediction_file.py


            list_model_name.append(model) # to append all accuracy in a list

            pickle.dump(list_model_name[z], open(picklename+"_KNN_Multiclass_model_" +  str(h)+".pkl" ,'wb'))

            if w==1:
                break

            x = np.delete(x, w-1, 1)
            #X_train = np.delete(X_train, w-1, 1)
            #X_test  = np.delete(X_test, w-1, 1)

            z=z+1
            h=h-1
            w=w-1

        #to send how many models we created
        number_of_model_created_for_Multiclass_models = length_all_assessments_in_selected_course - 1 #to send how many model have been created

        return (list_model_accuracy, list_model_f1, list_model_recall, list_model_precision,  number_of_model_created_for_Multiclass_models)


def create_multiple_Binary_models_KNN (courseName, x, y):

        #to get all students mark in assessment 1 for (where condition) course INFT2031
        con = sql.connect(host="pythonanywhere_host", user="pythonanywhere_user", password="pythonanywhere_password", database="pythonanywhere$database_name") #this is not the real connections details
        c =  con.cursor() # cursor
        c = con.cursor(buffered=True)


        #here I want to get all assessment in the selected course
        all_assessments_in_selected_course_query= "SELECT assessment_name  FROM assessment where course_course_id=%s order by auto_increment"
        values = (courseName)

        #here i want to fech all assessments from database for a specefic course [(course_id) from the function (function_create_dataset) parameter
        all_assessments_in_selected_course= c.execute(all_assessments_in_selected_course_query, (values,))
        all_assessments_in_selected_course = c.fetchall()

        # to get the length of all assessments for selected course (to know how many assessment in this course)
        length_all_assessments_in_selected_course= len(all_assessments_in_selected_course)


        #here to create new model
        list_model_accuracy= [] # create list to contain all acc for all models we want to create
        list_model_f1=[]
        list_model_recall=[]
        list_model_precision= []

        picklename = courseName
        list_model_name= [] # to add each model with pickle_i.pkl
        z=0         #to keep track of list_model_name
        h=length_all_assessments_in_selected_course         #to keep track of picklename
        np.random.seed(42)
        w=length_all_assessments_in_selected_course

        #grid_param Dictionary type for hypertuning
        grid_param = {'n_neighbors': [3, 5, 7, 9], # usually odd numbers
        			  'leaf_size':[1,3,5],
                      'algorithm':['auto', 'kd_tree']}

        for i in range(length_all_assessments_in_selected_course):
            np.random.seed(42)

            model = KNeighborsClassifier()

            ###################### hypertuning ##############################

            gd_sr = GridSearchCV(estimator=model,
            		 param_grid=grid_param,
            		 scoring='accuracy',
            		 cv=5)

            gd_sr.fit(x, y)

            model = gd_sr.best_estimator_

            ###################### hypertuning ##############################



            #accuracy
            model_accuracy = cross_val_score(model, x, y, scoring="accuracy", cv=5)
            model_accuracy= round(model_accuracy.mean(), 3)
            list_model_accuracy.append(model_accuracy) # to append all accuracy in a list

            #f1
            model_f1 = cross_val_score(model, x, y, scoring="f1", cv=5)
            model_f1= round(model_f1.mean(), 3)
            list_model_f1.append(model_f1) # to append all accuracy in a list

            #recall
            model_recall = cross_val_score(model, x, y, scoring="recall", cv=5)
            model_recall= round(model_recall.mean(), 3)
            list_model_recall.append(model_recall) # to append all accuracy in a list


            #precision
            model_precision = cross_val_score(model, x, y, scoring="precision", cv=5)
            model_precision= round(model_precision.mean(), 3)
            list_model_precision.append(model_precision) # to append all accuracy in a list

            model = model.fit(x, y) # i fit my model with all my dataset after i used CV to check the performance. I have to do that in order to use .predict function in the prediction_file.py

            list_model_name.append(model) # to append all accuracy in a list

            pickle.dump(list_model_name[z], open(picklename+"_KNN_Binary_model_" +  str(h)+".pkl" ,'wb'))

            if w==1:
                break

            x = np.delete(x, w-1, 1)
            #X_train = np.delete(X_train, w-1, 1)
            #X_test  = np.delete(X_test, w-1, 1)

            z=z+1
            h=h-1
            w=w-1

        #to send how many models we created
        number_of_model_created_for_Binary_models = length_all_assessments_in_selected_course - 1 #to send how many model have been created

        return (list_model_accuracy, list_model_f1, list_model_recall, list_model_precision,  number_of_model_created_for_Binary_models)



#####################################################################################################################################
#####################################################################################################################################
#####################################################################################################################################
#NB

def create_multiple_Multiclass_models_NB (courseName, x, y):

        #to get all students mark in assessment 1 for (where condition) course INFT2031
        con = sql.connect(host="pythonanywhere_host", user="pythonanywhere_user", password="pythonanywhere_password", database="pythonanywhere$database_name") #this is not the real connections details
        c =  con.cursor() # cursor
        c = con.cursor(buffered=True)


        #here I want to get all assessment in the selected course
        all_assessments_in_selected_course_query= "SELECT assessment_name  FROM assessment where course_course_id=%s order by auto_increment"
        values = (courseName)

        #here i want to fech all assessments from database for a specefic course [(course_id) from the function (function_create_dataset) parameter
        all_assessments_in_selected_course= c.execute(all_assessments_in_selected_course_query, (values,))
        all_assessments_in_selected_course = c.fetchall()

        # to get the length of all assessments for selected course (to know how many assessment in this course)
        length_all_assessments_in_selected_course= len(all_assessments_in_selected_course)


        #here to create new model
        list_model_accuracy= [] # create list to contain all acc for all models we want to create
        list_model_f1=[]
        list_model_recall=[]
        list_model_precision= []

        picklename = courseName
        list_model_name= [] # to add each model with pickle_i.pkl
        z=0         #to keep track of list_model_name
        h=length_all_assessments_in_selected_course         #to keep track of picklename
        np.random.seed(42)
        w=length_all_assessments_in_selected_course

        #grid_param Dictionary type for hypertuning
        grid_param = {
            'var_smoothing': [0.00000001, 0.000000001, 0.00000001]
        }


        for i in range(length_all_assessments_in_selected_course):
            np.random.seed(42)


            model = GaussianNB()

            ###################### hypertuning ##############################

            gd_sr = GridSearchCV(estimator=model,
            		 param_grid=grid_param,
            		 scoring='accuracy', #33333333333333333333333333accuracy
            		 cv=5)

            gd_sr.fit(x, y)

            model = gd_sr.best_estimator_

            ###################### hypertuning ##############################

            #accuracy
            model_accuracy = cross_val_score(model, x, y, scoring="accuracy", cv=5)
            model_accuracy= round(model_accuracy.mean(), 3)
            list_model_accuracy.append(model_accuracy) # to append all accuracy in a list

            #f1
            model_f1 = cross_val_score(model, x, y, scoring="f1_weighted", cv=5)
            model_f1= round(model_f1.mean(), 3)
            list_model_f1.append(model_f1) # to append all accuracy in a list

            #recall
            model_recall = cross_val_score(model, x, y, scoring="recall_weighted", cv=5)
            model_recall= round(model_recall.mean(), 3)
            list_model_recall.append(model_recall) # to append all accuracy in a list


            #precision
            model_precision = cross_val_score(model, x, y, scoring="precision_weighted", cv=5)
            model_precision= round(model_precision.mean(), 3)
            list_model_precision.append(model_precision) # to append all accuracy in a list

            model = model.fit(x, y) # i fit my model with all my dataset after i used CV to check the performance. I have to do that in order to use .predict function in the prediction_file.py


            list_model_name.append(model) # to append all accuracy in a list

            pickle.dump(list_model_name[z], open(picklename+"_NB_Multiclass_model_" +  str(h)+".pkl" ,'wb'))

            if w==1:
                break

            x = np.delete(x, w-1, 1)
            #X_train = np.delete(X_train, w-1, 1)
            #X_test  = np.delete(X_test, w-1, 1)

            z=z+1
            h=h-1
            w=w-1

        #to send how many models we created
        number_of_model_created_for_Multiclass_models = length_all_assessments_in_selected_course - 1 #to send how many model have been created

        return (list_model_accuracy, list_model_f1, list_model_recall, list_model_precision,  number_of_model_created_for_Multiclass_models)


def create_multiple_Binary_models_NB (courseName, x, y):

        #to get all students mark in assessment 1 for (where condition) course INFT2031
        con = sql.connect(host="pythonanywhere_host", user="pythonanywhere_user", password="pythonanywhere_password", database="pythonanywhere$database_name") #this is not the real connections details
        c =  con.cursor() # cursor
        c = con.cursor(buffered=True)


        #here I want to get all assessment in the selected course
        all_assessments_in_selected_course_query= "SELECT assessment_name  FROM assessment where course_course_id=%s order by auto_increment"
        values = (courseName)

        #here i want to fech all assessments from database for a specefic course [(course_id) from the function (function_create_dataset) parameter
        all_assessments_in_selected_course= c.execute(all_assessments_in_selected_course_query, (values,))
        all_assessments_in_selected_course = c.fetchall()

        # to get the length of all assessments for selected course (to know how many assessment in this course)
        length_all_assessments_in_selected_course= len(all_assessments_in_selected_course)


        #here to create new model
        list_model_accuracy= [] # create list to contain all acc for all models we want to create
        list_model_f1=[]
        list_model_recall=[]
        list_model_precision= []

        picklename = courseName
        list_model_name= [] # to add each model with pickle_i.pkl
        z=0         #to keep track of list_model_name
        h=length_all_assessments_in_selected_course         #to keep track of picklename
        np.random.seed(42)
        w=length_all_assessments_in_selected_course


        #grid_param Dictionary type for hypertuning
        grid_param = {
            'var_smoothing': [0.00000001, 0.000000001, 0.00000001]
        }

        for i in range(length_all_assessments_in_selected_course):
            np.random.seed(42)

            model = GaussianNB()

            ###################### hypertuning ##############################

            gd_sr = GridSearchCV(estimator=model,
            		 param_grid=grid_param,
            		 scoring='accuracy',
            		 cv=5)

            gd_sr.fit(x, y)

            model = gd_sr.best_estimator_

            ###################### hypertuning ##############################



            #accuracy
            model_accuracy = cross_val_score(model, x, y, scoring="accuracy", cv=5)
            model_accuracy= round(model_accuracy.mean(), 3)
            list_model_accuracy.append(model_accuracy) # to append all accuracy in a list

            #f1
            model_f1 = cross_val_score(model, x, y, scoring="f1", cv=5)
            model_f1= round(model_f1.mean(), 3)
            list_model_f1.append(model_f1) # to append all accuracy in a list

            #recall
            model_recall = cross_val_score(model, x, y, scoring="recall", cv=5)
            model_recall= round(model_recall.mean(), 3)
            list_model_recall.append(model_recall) # to append all accuracy in a list


            #precision
            model_precision = cross_val_score(model, x, y, scoring="precision", cv=5)
            model_precision= round(model_precision.mean(), 3)
            list_model_precision.append(model_precision) # to append all accuracy in a list

            model = model.fit(x, y) # i fit my model with all my dataset after i used CV to check the performance. I have to do that in order to use .predict function in the prediction_file.py

            list_model_name.append(model) # to append all accuracy in a list

            pickle.dump(list_model_name[z], open(picklename+"_NB_Binary_model_" +  str(h)+".pkl" ,'wb'))

            if w==1:
                break

            x = np.delete(x, w-1, 1)
            #X_train = np.delete(X_train, w-1, 1)
            #X_test  = np.delete(X_test, w-1, 1)

            z=z+1
            h=h-1
            w=w-1

        #to send how many models we created
        number_of_model_created_for_Binary_models = length_all_assessments_in_selected_course - 1 #to send how many model have been created

        return (list_model_accuracy, list_model_f1, list_model_recall, list_model_precision,  number_of_model_created_for_Binary_models)



#####################################################################################################################################
#####################################################################################################################################
#####################################################################################################################################

#DT

def create_multiple_Multiclass_models_DT (courseName, x, y):

        #to get all students mark in assessment 1 for (where condition) course INFT2031
        con = sql.connect(host="pythonanywhere_host", user="pythonanywhere_user", password="pythonanywhere_password", database="pythonanywhere$database_name") #this is not the real connections details
        c =  con.cursor() # cursor
        c = con.cursor(buffered=True)


        #here I want to get all assessment in the selected course
        all_assessments_in_selected_course_query= "SELECT assessment_name  FROM assessment where course_course_id=%s order by auto_increment"
        values = (courseName)

        #here i want to fech all assessments from database for a specefic course [(course_id) from the function (function_create_dataset) parameter
        all_assessments_in_selected_course= c.execute(all_assessments_in_selected_course_query, (values,))
        all_assessments_in_selected_course = c.fetchall()

        # to get the length of all assessments for selected course (to know how many assessment in this course)
        length_all_assessments_in_selected_course= len(all_assessments_in_selected_course)


        #here to create new model
        list_model_accuracy= [] # create list to contain all acc for all models we want to create
        list_model_f1=[]
        list_model_recall=[]
        list_model_precision= []

        picklename = courseName
        list_model_name= [] # to add each model with pickle_i.pkl
        z=0         #to keep track of list_model_name
        h=length_all_assessments_in_selected_course         #to keep track of picklename
        np.random.seed(42)
        w=length_all_assessments_in_selected_course

        #grid_param Dictionary type for hypertuning
        grid_param = {'max_depth': np.arange(4, 8),
              "criterion": ["gini", "entropy"]}


        for i in range(length_all_assessments_in_selected_course):
            np.random.seed(42)

            model = DecisionTreeClassifier()

            ###################### hypertuning ##############################

            gd_sr = GridSearchCV(estimator=model,
            		 param_grid=grid_param,
            		 scoring='accuracy', #33333333333333333333333333accuracy
            		 cv=5)

            gd_sr.fit(x, y)

            model = gd_sr.best_estimator_

            ###################### hypertuning ##############################

            #accuracy
            model_accuracy = cross_val_score(model, x, y, scoring="accuracy", cv=5)
            model_accuracy= round(model_accuracy.mean(), 3)
            list_model_accuracy.append(model_accuracy) # to append all accuracy in a list

            #f1
            model_f1 = cross_val_score(model, x, y, scoring="f1_weighted", cv=5)
            model_f1= round(model_f1.mean(), 3)
            list_model_f1.append(model_f1) # to append all accuracy in a list

            #recall
            model_recall = cross_val_score(model, x, y, scoring="recall_weighted", cv=5)
            model_recall= round(model_recall.mean(), 3)
            list_model_recall.append(model_recall) # to append all accuracy in a list


            #precision
            model_precision = cross_val_score(model, x, y, scoring="precision_weighted", cv=5)
            model_precision= round(model_precision.mean(), 3)
            list_model_precision.append(model_precision) # to append all accuracy in a list


            model = model.fit(x, y) # i fit my model with all my dataset after i used CV to check the performance. I have to do that in order to use .predict function in the prediction_file.py

            list_model_name.append(model) # to append all accuracy in a list

            pickle.dump(list_model_name[z], open(picklename+"_DT_Multiclass_model_" +  str(h)+".pkl" ,'wb'))

            if w==1:
                break

            x = np.delete(x, w-1, 1)
            #X_train = np.delete(X_train, w-1, 1)
            #X_test  = np.delete(X_test, w-1, 1)

            z=z+1
            h=h-1
            w=w-1

        #to send how many models we created
        number_of_model_created_for_Multiclass_models = length_all_assessments_in_selected_course - 1 #to send how many model have been created

        return (list_model_accuracy, list_model_f1, list_model_recall, list_model_precision,  number_of_model_created_for_Multiclass_models)


def create_multiple_Binary_models_DT (courseName, x, y):

        #to get all students mark in assessment 1 for (where condition) course INFT2031
        con = sql.connect(host="pythonanywhere_host", user="pythonanywhere_user", password="pythonanywhere_password", database="pythonanywhere$database_name") #this is not the real connections details
        c =  con.cursor() # cursor
        c = con.cursor(buffered=True)


        #here I want to get all assessment in the selected course
        all_assessments_in_selected_course_query= "SELECT assessment_name  FROM assessment where course_course_id=%s order by auto_increment"
        values = (courseName)

        #here i want to fech all assessments from database for a specefic course [(course_id) from the function (function_create_dataset) parameter
        all_assessments_in_selected_course= c.execute(all_assessments_in_selected_course_query, (values,))
        all_assessments_in_selected_course = c.fetchall()

        # to get the length of all assessments for selected course (to know how many assessment in this course)
        length_all_assessments_in_selected_course= len(all_assessments_in_selected_course)


        #here to create new model
        list_model_accuracy= [] # create list to contain all acc for all models we want to create
        list_model_f1=[]
        list_model_recall=[]
        list_model_precision= []

        picklename = courseName
        list_model_name= [] # to add each model with pickle_i.pkl
        z=0         #to keep track of list_model_name
        h=length_all_assessments_in_selected_course         #to keep track of picklename
        np.random.seed(42)
        w=length_all_assessments_in_selected_course

        #grid_param Dictionary type for hypertuning
        grid_param = {'max_depth': np.arange(4, 8),
              "criterion": ["gini", "entropy"]}

        for i in range(length_all_assessments_in_selected_course):
            np.random.seed(42)



            model = DecisionTreeClassifier()

            ###################### hypertuning ##############################

            gd_sr = GridSearchCV(estimator=model,
            		 param_grid=grid_param,
            		 scoring='accuracy', #33333333333333333333333333accuracy
            		 cv=5)

            gd_sr.fit(x, y)

            model = gd_sr.best_estimator_

            ###################### hypertuning ##############################

            #accuracy
            model_accuracy = cross_val_score(model, x, y, scoring="accuracy", cv=5)
            model_accuracy= round(model_accuracy.mean(), 3)
            list_model_accuracy.append(model_accuracy) # to append all accuracy in a list

            #f1
            model_f1 = cross_val_score(model, x, y, scoring="f1", cv=5)
            model_f1= round(model_f1.mean(), 3)
            list_model_f1.append(model_f1) # to append all accuracy in a list

            #recall
            model_recall = cross_val_score(model, x, y, scoring="recall", cv=5)
            model_recall= round(model_recall.mean(), 3)
            list_model_recall.append(model_recall) # to append all accuracy in a list


            #precision
            model_precision = cross_val_score(model, x, y, scoring="precision", cv=5)
            model_precision= round(model_precision.mean(), 3)
            list_model_precision.append(model_precision) # to append all accuracy in a list

            model = model.fit(x, y) # i fit my model with all my dataset after i used CV to check the performance. I have to do that in order to use .predict function in the prediction_file.py

            list_model_name.append(model) # to append all accuracy in a list

            pickle.dump(list_model_name[z], open(picklename+"_DT_Binary_model_" +  str(h)+".pkl" ,'wb'))

            if w==1:
                break

            x = np.delete(x, w-1, 1)
            #X_train = np.delete(X_train, w-1, 1)
            #X_test  = np.delete(X_test, w-1, 1)

            z=z+1
            h=h-1
            w=w-1

        #to send how many models we created
        number_of_model_created_for_Binary_models = length_all_assessments_in_selected_course - 1 #to send how many model have been created

        return (list_model_accuracy, list_model_f1, list_model_recall, list_model_precision,  number_of_model_created_for_Binary_models)



#########################################################################################
########################################################################################
#########################################################################################
#########################################################################################
########################################################################################
#########################################################################################


#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

#here is the maing function
@app.route('/createModel', methods=['GET', 'POST'])
@login_required
def createModel():
    if request.method == 'GET':
        try:
            con = sql.connect(host="pythonanywhere_host", user="pythonanywhere_user", password="pythonanywhere_password", database="pythonanywhere$database_name") #this is not the real connections details
            c =  con.cursor() # cursor
            query = "Select * from course where userName=%s"
            values = session["USERNAME"]
            cityList = c.execute(query, (values,))
            cityList = c.fetchall()

            return render_template('createModel.html', cityList=cityList)

        except sql.Error as e: # if error
            # then display the error in 'database_error.html' page
            return render_template('database_error.html', error=e)

        finally:
            con.close() # close the connection

    else: # request.method == 'POST':
        courseName = request.form['course_name']
        picklename = courseName



        try:

            #11111111111111111
            # to check if there is dataset for selected course or not. i will use it in the if staement that check if there is data in the database for this course or not
            con = sql.connect(host="pythonanywhere_host", user="pythonanywhere_user", password="pythonanywhere_password", database="pythonanywhere$database_name") #this is not the real connections details
            c =  con.cursor() # cursor
            c = con.cursor(buffered=True)
            #check if there are dataset for selected course by checking if there are total in student table for selected course
            check_dataset_for_selected_course_query= "SELECT total  FROM student where course_course_id=%s"
            values = (courseName)

            check_dataset_for_selected_course= c.execute(check_dataset_for_selected_course_query, (values,))
            check_dataset_for_selected_course = c.fetchall()




            #11111111111111111

            if len(check_dataset_for_selected_course) !=0: # to check if there is dataset/data in the database for this course or not. if not render template that says there is no dataset uploaded for this course


                ########################################################## here just to chec if there model already created
                if exists(picklename+"_RF_Multiclass_model_1.pkl" or picklename+"_RF_Binary_model_1.pkl"): # i used _RF_Multiclass_model_1 and _RF_Binary_model_1 because every course that already has model at least will have  a model of one feature. so i want to make sure if there is pkl files of not for the sellected course
                    return render_template('if_model_already_exist.html')




        ######################################################################################################################################################
        ######################################################################################################################################################

                else: #if there is no models (pkl) already created for this course, first call the two fuction that create dataset for you [function_create_dataset_for_Multiclass & function_create_dataset_for_Binary_model]

                    #creating the dataset for both Binary (y=pass&fail feature) and Multiclass (ThrreLevel feature)
                    x_multiclass, y_multiclass, length_of_dataset_after_cleaning_Multiclass = function_create_dataset_for_Multiclass(courseName) # create the dataset by calling the this function and return x and y

                    #return render_template('empty3.html', data = x_multiclass)

                    x_binary, y_binary, length_of_dataset_after_cleaning_Binary =function_create_dataset_for_Binary_model(courseName) # create the dataset by calling the this function and return x and y
                    #return render_template('empty3.html', data = y_binary)
        ######################################################################################################################################################
        ######################################################################################################################################################

                    #RF
                    #create binary models by calling this fuction
                    RF_accuracy_Binary, RF_f1_Binary, RF_recall_Binary, RF_precision_Binary,  RF_number_of_model_Binary = create_multiple_Binary_models_RF (courseName, x_binary, y_binary)
                    #SVM_accuracy_Binary, SVM_f1_Binary, SVM_recall_Binary, SVM_precision_Binary,  SVM_number_of_model_Binary = create_multiple_Binary_models_SVM (courseName, x_binary, y_binary)
                    #return render_template('empty3.html', data = RF_accuracy_Binary)
                    #create Multiclass classification models by calling this fuction
                    RF_accuracy_Multiclass, RF_f1_Multiclass, RF_recall_Multiclass, RF_precision_Multiclass,  RF_number_of_model_Multiclass = create_multiple_Multiclass_models_RF(courseName, x_multiclass, y_multiclass)

        ######################################################################################################################################################
        ######################################################################################################################################################
                    #SVM

                    #Binary
                    SVM_accuracy_Binary, SVM_f1_Binary, SVM_recall_Binary, SVM_precision_Binary,  SVM_number_of_model_Binary = create_multiple_Binary_models_SVM (courseName, x_binary, y_binary)

                    #Multiclass
                    SVM_accuracy_Multiclass, SVM_f1_Multiclass, SVM_recall_Multiclass, SVM_precision_Multiclass,  SVM_number_of_model_Multiclass = create_multiple_Multiclass_models_SVM(courseName, x_multiclass, y_multiclass)
        ######################################################################################################################################################
        ######################################################################################################################################################
                    #KNN

                    #Binary
                    KNN_accuracy_Binary, KNN_f1_Binary, KNN_recall_Binary, KNN_precision_Binary,  KNN_number_of_model_Binary = create_multiple_Binary_models_KNN (courseName, x_binary, y_binary)
                    #Multiclass
                    KNN_accuracy_Multiclass, KNN_f1_Multiclass, KNN_recall_Multiclass, KNN_precision_Multiclass,  KNN_number_of_model_Multiclass = create_multiple_Multiclass_models_KNN(courseName, x_multiclass, y_multiclass)


        ######################################################################################################################################################
        ######################################################################################################################################################

                    #NB

                    #Binary
                    NB_accuracy_Binary, NB_f1_Binary, NB_recall_Binary, NB_precision_Binary,  NB_number_of_model_Binary = create_multiple_Binary_models_NB (courseName, x_binary, y_binary)

                    #Multiclass
                    NB_accuracy_Multiclass, NB_f1_Multiclass, NB_recall_Multiclass, NB_precision_Multiclass,  NB_number_of_model_Multiclass = create_multiple_Multiclass_models_NB(courseName, x_multiclass, y_multiclass)
         ######################################################################################################################################################
        ######################################################################################################################################################

                    #DT

                    #Binary
                    DT_accuracy_Binary, DT_f1_Binary, DT_recall_Binary, DT_precision_Binary,  DT_number_of_model_Binary = create_multiple_Binary_models_DT (courseName, x_binary, y_binary)

                    #Multiclass
                    DT_accuracy_Multiclass, DT_f1_Multiclass, DT_recall_Multiclass, DT_precision_Multiclass,  DT_number_of_model_Multiclass = create_multiple_Multiclass_models_DT(courseName, x_multiclass, y_multiclass)


        ######################################################################################################################################################
        ######################################################################################################################################################
                    #in this section, I save all models performance (accuracy, f1, and recall) created in the course_and_models Table
                    #to calulate how many model been created
                    Number_of_created_model= RF_number_of_model_Multiclass*10 #10 comes from 4*2 [foure ML algorithms * two models binary and multiclass]

                    #######################################################################
                    #here I want to get all assessment in the selected course, to know how many assessments there
                    all_assessments_in_selected_course_query= "SELECT assessment_name  FROM assessment where course_course_id=%s order by auto_increment"
                    values = (courseName)

                    #here i want to fech all assessments from database for a specefic course [(course_id) from the function (function_create_dataset) parameter
                    all_assessments_in_selected_course= c.execute(all_assessments_in_selected_course_query, (values,))
                    all_assessments_in_selected_course = c.fetchall()

                    # to get the length of all assessments for selected course (to know how many assessment in this course)
                    length_all_assessments_in_selected_course= len(all_assessments_in_selected_course)


                     # here i want to first insert course_id & course_name into the course_and_models table
                    c = con.cursor(buffered=True)
                    query_course_name_from_course_table="Select course_name from course where course_id=%s"
                    value_course_name_from_course_table=(courseName)
                    #course_name_from_course_table = c.execute("Select * from course where course_id=%s", courseName)
                    course_name_from_course_table = c.execute(query_course_name_from_course_table, (value_course_name_from_course_table,))
                    #course_name_from_course_table = c.fetchall()
                    course_name_from_course_table  = [ row[0] for row in c.fetchall() if row[0] ] # i used this to return fetch the data without (). I also used str(row[0]) to make sure it does not miss any int 0
                    course_name_from_course_table=str(course_name_from_course_table[0]) # i just convert list to string in order to solve  Python type tuple cannot be converted

                    c.execute("insert INTO course_and_models (course_id, course_name, userName) VALUES (%s,%s,%s)",
                                        (courseName, course_name_from_course_table, session["USERNAME"]))
                    con.commit() # apply changes

                    # END OF (here i want to first insert course_id & course_name into the course_and_models table)


                    counter=length_all_assessments_in_selected_course # i used this counter to help me to keep the (length_all_assessments_in_selected_course) untouch during the loop
                    #insert RF Binary acc & f1 & recall & precision into the course_and_models table
                    for i in range(length_all_assessments_in_selected_course):
                        c.execute("insert INTO models_performance (course_id, Features,  ML_Algorithm, Binary_Multiclass, accuracy, f1, recall, precision_1) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)",
                                        (courseName, counter, "RF", "Binary", RF_accuracy_Binary [i], RF_f1_Binary [i],  RF_recall_Binary [i], RF_precision_Binary [i] ))
                        counter=counter-1
                        con.commit() # apply changes

                    counter=length_all_assessments_in_selected_course # i used this counter to help me to keep the (length_all_assessments_in_selected_course) untouch during the loop
                    #insert RF Multiclass acc & f1 & recall & precision into the course_and_models table
                    for i in range(length_all_assessments_in_selected_course):
                        c.execute("insert INTO models_performance (course_id, Features,  ML_Algorithm, Binary_Multiclass, accuracy, f1, recall , precision_1) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)", # REPLACE INTO: do as insert in do does except if the assessment_name (PK) already exist in the database it will replace it with the new record
                                        (courseName, counter, "RF", "Multiclass", RF_accuracy_Multiclass [i], RF_f1_Multiclass [i], RF_recall_Multiclass [i], RF_precision_Multiclass [i]  ))
                        counter=counter-1
                        con.commit() # apply changes
                    counter=length_all_assessments_in_selected_course # i used this counter to help me to keep the (length_all_assessments_in_selected_course) untouch during the loop

                    #insert SVM Binary acc & f1 & recall & precision into the course_and_models tablefor
                    for i in range(length_all_assessments_in_selected_course):
                        c.execute("insert INTO models_performance (course_id, Features,  ML_Algorithm, Binary_Multiclass, accuracy, f1, recall , precision_1) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)", # REPLACE INTO: do as insert in do does except if the assessment_name (PK) already exist in the database it will replace it with the new record
                                        (courseName, counter, "SVM", "Binary", SVM_accuracy_Binary [i], SVM_f1_Binary [i], SVM_recall_Binary [i] , SVM_precision_Binary [i] ))
                        counter=counter-1
                        con.commit() # apply changes
                    counter=length_all_assessments_in_selected_course # i used this counter to help me to keep the (length_all_assessments_in_selected_course) untouch during the loop

                    #insert SVM Multiclass acc & f1 & recall & precision into the course_and_models table
                    for i in range(length_all_assessments_in_selected_course):
                        c.execute("insert INTO models_performance (course_id, Features,  ML_Algorithm, Binary_Multiclass, accuracy, f1, recall , precision_1) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)", # REPLACE INTO: do as insert in do does except if the assessment_name (PK) already exist in the database it will replace it with the new record
                                        (courseName, counter, "SVM", "Multiclass", SVM_accuracy_Multiclass [i], SVM_f1_Multiclass [i], SVM_recall_Multiclass [i] , SVM_precision_Multiclass [i] ))
                        counter=counter-1
                        con.commit() # apply changes
                    counter=length_all_assessments_in_selected_course # i used this counter to help me to keep the (length_all_assessments_in_selected_course) untouch during the loop

                    #insert KNN Binary acc & f1 & recall & precision into the course_and_models tablefor
                    for i in range(length_all_assessments_in_selected_course):
                        c.execute("insert INTO models_performance (course_id, Features,  ML_Algorithm, Binary_Multiclass, accuracy, f1, recall , precision_1) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)", # REPLACE INTO: do as insert in do does except if the assessment_name (PK) already exist in the database it will replace it with the new record
                                        (courseName, counter, "KNN", "Binary", KNN_accuracy_Binary [i], KNN_f1_Binary [i], KNN_recall_Binary [i], KNN_precision_Binary  [i] ))
                        counter=counter-1
                        con.commit() # apply changes
                    counter=length_all_assessments_in_selected_course # i used this counter to help me to keep the (length_all_assessments_in_selected_course) untouch during the loop

                    #insert KNN Multiclass acc & f1 & recall & precision into the course_and_models table
                    for i in range(length_all_assessments_in_selected_course):
                        c.execute("insert INTO models_performance (course_id, Features,  ML_Algorithm, Binary_Multiclass, accuracy, f1, recall , precision_1) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)", # REPLACE INTO: do as insert in do does except if the assessment_name (PK) already exist in the database it will replace it with the new record
                                        (courseName, counter, "KNN", "Multiclass", KNN_accuracy_Multiclass [i], KNN_f1_Multiclass [i], KNN_recall_Multiclass [i], KNN_precision_Multiclass [i]))
                        counter=counter-1
                        con.commit() # apply changes
                    counter=length_all_assessments_in_selected_course # i used this counter to help me to keep the (length_all_assessments_in_selected_course) untouch during the loop

                    #insert NB Binary acc & f1 & recall & precision into the course_and_models tablefor
                    for i in range(length_all_assessments_in_selected_course):
                        c.execute("insert INTO models_performance (course_id, Features,  ML_Algorithm, Binary_Multiclass, accuracy, f1, recall , precision_1) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)", # REPLACE INTO:
                                        (courseName, counter, "NB", "Binary", NB_accuracy_Binary [i], NB_f1_Binary [i], NB_recall_Binary [i], NB_precision_Binary [i]))
                        counter=counter-1
                        con.commit() # apply changes
                    counter=length_all_assessments_in_selected_course # i used this counter to help me to keep the (length_all_assessments_in_selected_course) untouch during the loop

                    #insert NB Multiclass acc & f1 & recall & precision into the course_and_models table
                    for i in range(length_all_assessments_in_selected_course):
                        c.execute("insert INTO models_performance (course_id, Features,  ML_Algorithm, Binary_Multiclass, accuracy, f1, recall , precision_1) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)", # REPLACE INTO: do as insert in do does except if the assessment_name (PK) already exist in the database it will replace it with the new record
                                        (courseName, counter, "NB", "Multiclass", NB_accuracy_Multiclass [i], NB_f1_Multiclass [i], NB_recall_Multiclass [i], NB_precision_Multiclass [i]))
                        counter=counter-1
                        con.commit() # apply changes
                    counter=length_all_assessments_in_selected_course # i used this counter to help me to keep the (length_all_assessments_in_selected_course) untouch during the loop


                    #insert DT Binary acc & f1 & recall & precision into the course_and_models tablefor
                    for i in range(length_all_assessments_in_selected_course):
                        c.execute("insert INTO models_performance (course_id, Features,  ML_Algorithm, Binary_Multiclass, accuracy, f1, recall , precision_1) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)", # REPLACE INTO:
                                        (courseName, counter, "DT", "Binary", DT_accuracy_Binary [i], DT_f1_Binary [i], DT_recall_Binary [i], DT_precision_Binary [i]))
                        counter=counter-1
                        con.commit() # apply changes
                    counter=length_all_assessments_in_selected_course # i used this counter to help me to keep the (length_all_assessments_in_selected_course) untouch during the loop

                    #insert DT Multiclass acc & f1 & recall & precision into the course_and_models table
                    for i in range(length_all_assessments_in_selected_course):
                        c.execute("insert INTO models_performance (course_id, Features,  ML_Algorithm, Binary_Multiclass, accuracy, f1, recall , precision_1) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)", # REPLACE INTO: do as insert in do does except if the assessment_name (PK) already exist in the database it will replace it with the new record
                                        (courseName, counter, "DT", "Multiclass", DT_accuracy_Multiclass [i], DT_f1_Multiclass [i], DT_recall_Multiclass [i], DT_precision_Multiclass [i]))
                        counter=counter-1
                        con.commit() # apply changes
                    counter=length_all_assessments_in_selected_course # i used this counter to help me to keep the (length_all_assessments_in_selected_course) untouch during the loop



                    con.commit() # apply changes
                    ######################################################################################################################################################
                    ######################################################################################################################################################

                    ##################################################################################################################################################################################################################
                    #here i render thank you page with acc and f1 for all models that have been created + course name + how many model created + number_of_model_for_loop_html [this helps me in the html page to loop based on how many model created for each algorithm]
                    return render_template('thank_you_for_creating_models.html', \
                        RF_accuracy_Binary=RF_accuracy_Binary, RF_f1_Binary=RF_f1_Binary, \
                        RF_accuracy_Multiclass=RF_accuracy_Multiclass, \
                        RF_f1_Multiclass=RF_f1_Multiclass, SVM_accuracy_Binary=SVM_accuracy_Binary, \

                        SVM_f1_Binary=SVM_f1_Binary, SVM_accuracy_Multiclass=SVM_accuracy_Multiclass, \
                        SVM_f1_Multiclass=SVM_f1_Multiclass, KNN_accuracy_Binary=KNN_accuracy_Binary, \

                        KNN_f1_Binary=KNN_f1_Binary, KNN_accuracy_Multiclass=KNN_accuracy_Multiclass, \
                        KNN_f1_Multiclass=KNN_f1_Multiclass, NB_accuracy_Binary=NB_accuracy_Binary, \

                        NB_f1_Binary=NB_f1_Binary, NB_accuracy_Multiclass=NB_accuracy_Multiclass, \
                        NB_f1_Multiclass=NB_f1_Multiclass, \

                        DT_accuracy_Binary=DT_accuracy_Binary, \
                        DT_f1_Binary=DT_f1_Binary, DT_accuracy_Multiclass=DT_accuracy_Multiclass, \
                        DT_f1_Multiclass=DT_f1_Multiclass, \

                        RF_recall_Binary=RF_recall_Binary, RF_precision_Binary=RF_precision_Binary,\
                        RF_recall_Multiclass=RF_recall_Multiclass, RF_precision_Multiclass=RF_precision_Multiclass,\
                        SVM_recall_Binary=SVM_recall_Binary, SVM_precision_Binary=SVM_precision_Binary,\
                        SVM_recall_Multiclass=SVM_recall_Multiclass, SVM_precision_Multiclass=SVM_precision_Multiclass,\
                        KNN_recall_Binary=KNN_recall_Binary, KNN_precision_Binary=KNN_precision_Binary,\
                        KNN_recall_Multiclass=KNN_recall_Multiclass, KNN_precision_Multiclass=KNN_precision_Multiclass,\
                        NB_recall_Binary=NB_recall_Binary, NB_precision_Binary=NB_precision_Binary,\
                        NB_recall_Multiclass=NB_recall_Multiclass, NB_precision_Multiclass=NB_precision_Multiclass,\
                        DT_recall_Binary=DT_recall_Binary, DT_precision_Binary=DT_precision_Binary,\
                        DT_recall_Multiclass=DT_recall_Multiclass, DT_precision_Multiclass=DT_precision_Multiclass,\

                        all_Number_of_created_model=Number_of_created_model, number_of_model_for_loop_html = RF_number_of_model_Multiclass+1, \
                        courseName=courseName, length_of_dataset_after_cleaning_Binary=length_of_dataset_after_cleaning_Binary,\
                           length_of_dataset_after_cleaning_Multiclass=length_of_dataset_after_cleaning_Multiclass )


            else:
                return render_template('no_dataset_for_this_course.html') # if theere is no dataset in the databease for this course

        except sql.Error as e: # if error
            # then display the error in 'database_error.html' page
            return render_template('database_error.html', error=e)

        finally:
            con.close() # close the connection






#NNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNN



#SSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSS
#check_model_performance.py

@app.route('/check_models_performance.html', methods=['GET', 'POST'])
@login_required
def check_models_performance():
    if request.method == 'GET':
        # send the form 99999999999999999999999999999999999999999999999999999999999999999
        try:
            con = sql.connect(host="pythonanywhere_host", user="pythonanywhere_user", password="pythonanywhere_password", database="pythonanywhere$database_name") #this is not the real connections details
            c =  con.cursor() # cursor

            query = "Select * from course_and_models where userName=%s"
            values = session["USERNAME"]
            cityList = c.execute(query, (values,))
            cityList = c.fetchall()

            return render_template('check_models_performance.html', cityList=cityList)

        except sql.Error as e: # if error
            # then display the error in 'database_error.html' page
            return render_template('database_error.html', error=e)

        finally:

            con.close()



    else: # request.method == 'POST':
        # read data from the form and save in variable
        course_course_id = request.form['course_name']


        # store in database
        try:
            con = sql.connect(host="pythonanywhere_host", user="pythonanywhere_user", password="pythonanywhere_password", database="pythonanywhere$database_name") #this is not the real connections details
            c =  con.cursor() # cursor
            # insert data # REPLACE INTO: do as insert in do does except if the assessment_name (PK) already exist in the database it will replace it with the new record


            #here i want to get all models performance based on the ML algorithms and Binary_Multiclass from the models_performance Table for the selected course_id

            query_RF_Binary="SELECT * FROM models_performance where course_id=%s and ML_Algorithm=%s and Binary_Multiclass=%s"
            values=(course_course_id, "RF", "Binary")
            RF_Binary= c.execute(query_RF_Binary,values)
            RF_Binary = c.fetchall()

            query_RF_Multiclass="SELECT * FROM models_performance where course_id=%s and ML_Algorithm=%s and Binary_Multiclass=%s"
            values=(course_course_id, "RF", "Multiclass")
            RF_Multiclass= c.execute(query_RF_Multiclass,values)
            RF_Multiclass = c.fetchall()



            query_SVM_Binary="SELECT * FROM models_performance where course_id=%s and ML_Algorithm=%s and Binary_Multiclass=%s"
            values=(course_course_id, "SVM", "Binary")
            SVM_Binary= c.execute(query_SVM_Binary,values)
            SVM_Binary = c.fetchall()

            query_SVM_Multiclass="SELECT * FROM models_performance where course_id=%s and ML_Algorithm=%s and Binary_Multiclass=%s"
            values=(course_course_id, "SVM", "Multiclass")
            SVM_Multiclass= c.execute(query_SVM_Multiclass,values)
            SVM_Multiclass = c.fetchall()


            query_KNN_Binary="SELECT * FROM models_performance where course_id=%s and ML_Algorithm=%s and Binary_Multiclass=%s"
            values=(course_course_id, "KNN", "Binary")
            KNN_Binary= c.execute(query_KNN_Binary,values)
            KNN_Binary = c.fetchall()

            query_KNN_Multiclass="SELECT * FROM models_performance where course_id=%s and ML_Algorithm=%s and Binary_Multiclass=%s"
            values=(course_course_id, "KNN", "Multiclass")
            KNN_Multiclass= c.execute(query_KNN_Multiclass,values)
            KNN_Multiclass = c.fetchall()

            query_NB_Binary="SELECT * FROM models_performance where course_id=%s and ML_Algorithm=%s and Binary_Multiclass=%s"
            values=(course_course_id, "NB", "Binary")
            NB_Binary= c.execute(query_NB_Binary,values)
            NB_Binary = c.fetchall()

            query_NB_Multiclass="SELECT * FROM models_performance where course_id=%s and ML_Algorithm=%s and Binary_Multiclass=%s"
            values=(course_course_id, "NB", "Multiclass")
            NB_Multiclass= c.execute(query_NB_Multiclass,values)
            NB_Multiclass = c.fetchall()

            query_DT_Binary="SELECT * FROM models_performance where course_id=%s and ML_Algorithm=%s and Binary_Multiclass=%s"
            values=(course_course_id, "DT", "Binary")
            DT_Binary= c.execute(query_DT_Binary,values)
            DT_Binary = c.fetchall()

            query_DT_Multiclass="SELECT * FROM models_performance where course_id=%s and ML_Algorithm=%s and Binary_Multiclass=%s"
            values=(course_course_id, "DT", "Multiclass")
            DT_Multiclass= c.execute(query_DT_Multiclass,values)
            DT_Multiclass = c.fetchall()

            ##################################################################33
            #here i just want to conver list to array
            RF_Binary = np.array(RF_Binary)
            RF_Multiclass = np.array(RF_Multiclass)

            SVM_Binary = np.array(SVM_Binary)
            SVM_Multiclass = np.array(SVM_Multiclass)

            KNN_Binary = np.array(KNN_Binary)
            KNN_Multiclass = np.array(KNN_Multiclass)

            NB_Binary = np.array(NB_Binary)
            NB_Multiclass = np.array(NB_Multiclass)

            DT_Binary = np.array(DT_Binary)
            DT_Multiclass = np.array(DT_Multiclass)

            ####################################################################33

            number_of_model_for_loop_html = len(RF_Binary)  #this i need to use in the Results_check_models_performance.html for tracking number of feature in the table. it just what i did in the thank_you_for_creating_models.html



            return render_template('Results_check_models_performance.html', course_course_id=course_course_id,\
                                    number_of_model_for_loop_html=number_of_model_for_loop_html,\
                                    RF_Binary=RF_Binary , RF_Multiclass=RF_Multiclass, \
            						SVM_Binary=SVM_Binary, SVM_Multiclass=SVM_Multiclass,\
            						KNN_Binary=KNN_Binary, KNN_Multiclass=KNN_Multiclass, \
            						NB_Binary=NB_Binary, NB_Multiclass=NB_Multiclass, \
                                    DT_Binary=DT_Binary, DT_Multiclass=DT_Multiclass)


        except sql.Error as e: # if error
            # then display the error in 'database_error.html' page
            return render_template('database_error.html', error=e)


        finally:
            con.close() # close the connection



#NNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNN


#SSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSS
#prediction_file.py



##############################################################################################
###################################### Prediction for predict_csv_simple  ####################
##############################################################################################


    #here i want to allow academics to without choosing what ML algorithms they want. simply, i choose the best models both binary & multiclass for them based on the performance results from the models_performance Table

# i used this because i just dont want to show tables before prforming prediction
@app.route('/predict_csv_simple_first') # this is the first GET function html that take you to/render_template  predict_csv.html
@login_required
def predict_csv_simple_first():
    try:
        con = sql.connect(host="pythonanywhere_host", user="pythonanywhere_user", password="pythonanywhere_password", database="pythonanywhere$database_name") #this is not the real connections details
        c =  con.cursor() # cursor

        query = "Select * from course_and_models where userName=%s"
        values = session["USERNAME"]
        cityList = c.execute(query, (values,))
        cityList = c.fetchall()

        return render_template('predict_csv_simple_first.html', cityList=cityList)

    except sql.Error as e: # if error
            # then display the error in 'database_error.html' page
            return render_template('database_error.html', error=e)

    finally:
        con.close() # close the connection


@app.route('/predict_csv_simple') # this is the GET function that take you to/render_template  predict_csv.html
@login_required
def predict_csv_simple():
    try:
        con = sql.connect(host="pythonanywhere_host", user="pythonanywhere_user", password="pythonanywhere_password", database="pythonanywhere$database_name") #this is not the real connections details
        c =  con.cursor() # cursor

        query = "Select * from course_and_models where userName=%s"
        values = session["USERNAME"]
        cityList = c.execute(query, (values,))
        cityList = c.fetchall()

        return render_template('predict_csv_simple.html', cityList=cityList)

    except sql.Error as e: # if error
            # then display the error in 'database_error.html' page
            return render_template('database_error.html', error=e)

    finally:
        con.close() # close the connection



#this is for the making prediction without choosing ML algorithms [best model selected automalically]
@app.route('/predict_from_csv_simple',methods=['POST'])
@login_required
def predict_from_csv_simple():
    '''
    For rendering results on HTML GUI
    '''
    ################################################### here just to show the dropdown box after making prediction
    try:
        con = sql.connect(host="pythonanywhere_host", user="pythonanywhere_user", password="pythonanywhere_password", database="pythonanywhere$database_name") #this is not the real connections details
        c =  con.cursor() # cursor
        query = "Select * from course_and_models where userName=%s"
        values = session["USERNAME"]
        cityList = c.execute(query, (values,))
        cityList = c.fetchall()

    except sql.Error as e: # if error
            # then display the error in 'database_error.html' page
            return render_template('database_error.html', error=e)

    finally:
            con.close() # close the connection
    ###################################################


    courseName = request.form['course_name']
    picklename = courseName
    #conversion_radio_btn = request.form['conversion'] # from the conversion radio button


    #ML_algorithms_name = request.form['ml_algorithm'] # from the radio button

    try:
        con = sql.connect(host="pythonanywhere_host", user="pythonanywhere_user", password="pythonanywhere_password", database="pythonanywhere$database_name") #this is not the real connections details
        c =  con.cursor() # cursor
        #here I want to get all assessment in the selected course so i can check if prediction csv file has column more that created models
        all_assessments_in_selected_course_query= "SELECT assessment_name  FROM assessment where course_course_id=%s order by auto_increment"
        values = (courseName)
        #here i want to fech all assessments from database for a specefic course [(course_id) from the function (function_create_dataset) parameter
        all_assessments_in_selected_course= c.execute(all_assessments_in_selected_course_query, (values,))
        all_assessments_in_selected_course = c.fetchall()
        # to get the length of all assessments for selected course (to know how many assessment in this course)
        length_all_assessments_in_selected_course= len(all_assessments_in_selected_course)

    except sql.Error as e: # if error
            # then display the error in 'database_error.html' page
        return render_template('database_error.html', error=e)

    finally:
        con.close() # close the connection


    csv_file = request.files['file']
    if request.files['file'].filename != '': # if there is file the user upload it # i overcome this issue by making input file required
        #output=""   # i dont need it anymore
        csv_file = request.files['file']

        # this helps me to validate if the uploaded file is a csv extention
        file_ext = os.path.splitext(request.files['file'].filename)[1]
        #return render_template('no_dashboard_yet.html', data = file_ext)
        if file_ext not in app.config['UPLOAD_EXTENSIONS']:
            return render_template('no_dashboard_yet.html', data = "please make sure to upload a csv file")
        # END OF this helps me to validate if the uploaded file is a csv extention

        csv_file = TextIOWrapper(csv_file, encoding='utf-8')
        csv_reader = csv.reader(csv_file, delimiter=',')
        next(csv_reader)
        data = [row for row in csv_reader]

        if len(data) == 0:
                return render_template('empty.html')

        #........................................................................................................................
        #here i want to do Rukshan comments about making the first row in CSV file the weight [mark of]
        mark_out_CSV_array = np.array(data)
        #ttype=type(my_array) #temppp
        mark_out_CSV= mark_out_CSV_array[0,2:]  #to take the first row only and after sdt_name and std_ID [only the weight]
        assessment_waitage= mark_out_CSV_array[1,2:]  #to take the second row only and after sdt_name and std_ID [only the weight]

        data = np.array(data)
        data= data [2:, :]
        data=data.tolist()
        #return render_template('empty3.html', data = data)

        #.......................................................................................................................


        #to know check how many column in array (data)
        columns = len(data[0])

        #############
        # here i want to make sure the uploaded file has features less than or equal to the number of assessments in the selected course minu the funal exam
        if columns>(length_all_assessments_in_selected_course+2): # this is to check if csv file feature has more feature than course's assessment s
            #return render_template('too_big_csv_file.html')    # if csv file has feature more than number of assessments in the database
            return render_template('sorry_features_more_than_created_models.html', length_all_assessments_in_selected_course= (length_all_assessments_in_selected_course-1))

        ##############



        #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

        # here in this section, i want to get choose best model performance for performing prediction based on the model performance from the models_performance Table & based on how many features in the uploaded file
        number_of_features_in_the_uploaded_files = columns-2

        #SELECT * FROM prediction.models_performance where course_id="INFT2031" and Features=3 and Binary_Multiclass="Binary" order by accuracy DESC, f1 DESC, recall DESC;
        #SELECT * FROM prediction.models_performance where course_id="INFT2031" and Features=1 and Binary_Multiclass="Multiclass" order by accuracy DESC, f1 DESC, recall DESC;

        query_check_model_performance= "SELECT ML_Algorithm FROM models_performance where course_id=%s and Features=%s and Binary_Multiclass=%s order by accuracy DESC, f1 DESC, recall DESC"
        value_check_model_performance_Binary=(courseName, number_of_features_in_the_uploaded_files, "Binary")
        value_check_model_performance_Multiclass=(courseName, number_of_features_in_the_uploaded_files, "Multiclass")

        try:
            con = sql.connect(host="pythonanywhere_host", user="pythonanywhere_user", password="pythonanywhere_password", database="pythonanywhere$database_name") #this is not the real connections details
            c =  con.cursor() # cursor
            check_model_performance= c.execute(query_check_model_performance, value_check_model_performance_Binary)
            #best_binary_model = c.fetchall()
            best_binary_model = [ row[0] for row in c.fetchall() if row[0] ] # i used this to return fetch the data without ()

            check_model_performance= c.execute(query_check_model_performance, value_check_model_performance_Multiclass)
            #best_multiclass_model = c.fetchall()
            best_multiclass_model = [ row[0] for row in c.fetchall() if row[0] ] # i used this to return fetch the data without ()

            # block .............................................................................
            # here I want to fetch best models accuracy as well
            query_check_model_performance_accuracy= "SELECT accuracy FROM models_performance where course_id=%s and Features=%s and Binary_Multiclass=%s order by accuracy DESC, f1 DESC, recall DESC"
            value_check_model_performance_Binary=(courseName, number_of_features_in_the_uploaded_files, "Binary")
            value_check_model_performance_Multiclass=(courseName, number_of_features_in_the_uploaded_files, "Multiclass")

            #best model's accuarcy [Binary]
            check_model_performance= c.execute(query_check_model_performance_accuracy, value_check_model_performance_Binary)
            best_binary_model_accuracy = [ row[0] for row in c.fetchall() if row[0] ] # i used this to return fetch the data without ()

            #best model's accuarcy [Multiclass]
            check_model_performance= c.execute(query_check_model_performance_accuracy, value_check_model_performance_Multiclass)
            #best_multiclass_model = c.fetchall()
            best_multiclass_model_accuracy = [ row[0] for row in c.fetchall() if row[0] ] # i used this to return fetch the data without ()

            best_binary_model_accuracy=round(best_binary_model_accuracy [0]*100, 1)
            best_multiclass_model_accuracy=round(best_multiclass_model_accuracy [0]*100, 1)
            # end of block .............................................................................



        except sql.Error as e: # if error
            # then display the error in 'database_error.html' page
               return render_template('database_error.html', error=e)

        finally:
            con.close() # close the connection


        # END OF here in this section, i want to get choose best model performance for performing prediction based on the model performance from the models_performance Table & based on how many features in the uploaded file
        #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@


        data = np.array(data) #here i convert data (type: list i think) to array

        all_data_without_std_Name_ID=data[:,2:] #here I removed student name and ID from the data in a new array because i want to send this version to the models to predict

        data_only_std_Name_ID = data[:,:2]  #here I removed all marks and kept student name and ID to used it in the html tables to present students names and id with their results


        #######################################################################################################################################



        #here I want to make sure the csv file does not have any error such as empty cell or "hjbkjb" value
        #####################################################################################################3
        all_data_without_std_Name_ID = np.array(all_data_without_std_Name_ID)
        #columns
        for row in all_data_without_std_Name_ID:

            for i in range(columns-2):


                if row[i]=="": #if the is null in the assessment make it 0
                   row[i]=0

                try:# i used try and except ValueError, to solve if data in the csv file is not nubmber such as jkhkjnh

                    #row[i]=int(row[i]) #i used float because when using int any float number return it 0, so i had to use float

                    #999999999999999999999999999999999999999999999999999999999999999999999999
                    #3333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333
                    #here i want to make sure to match students_id btn student and assessments_Std tables
                    con = sql.connect(host="pythonanywhere_host", user="pythonanywhere_user", password="pythonanywhere_password", database="pythonanywhere$database_name") #this is not the real connections details
                    c = con.cursor() # cursor
                    c = con.cursor(buffered=True)

                    value = courseName
                    query4 = "SELECT assessment_name FROM assessment WHERE course_course_id = %s  order by auto_increment"
                    c.execute(query4,(value,))

                    assessments_order = c.fetchall()

                    assessment_name_to_string = ",".join(assessments_order [i]) #to solve error "python mysqlconnector mysqlinterfaceerror python type tuple cannot be converted"
                    #3333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333


                    #if conversion_radio_btn=="Yes": # here i did the if because i want to check if the user want to convert the data in the csv file or not
                    #here in this block, I tried to convert students marks into a Percentages as Simon suggested useing mark_out and mark_worth
                    #66666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666
                    query5 = "SELECT mark_out FROM assessment where course_course_id=%s and assessment_name =%s"


                    query6 = "SELECT mark_worth FROM assessment where course_course_id=%s and assessment_name =%s"

                    c.execute(query5,(courseName,assessment_name_to_string,))
                    mark_out = [ r[0] for r in c.fetchall() if str(r[0]) ]

                    c.execute(query6,(courseName,assessment_name_to_string,))
                    mark_worth = [ r[0] for r in c.fetchall() if str(r[0]) ]

                    mark_out = np.array(mark_out)
                    mark_worth = np.array(mark_worth)


                    if mark_out_CSV[i] !="0" and assessment_waitage[i] !="0":

                        row[i] = float(row[i]) / int(mark_out_CSV[i]) * int(assessment_waitage[i])
                        row[i] = float(row[i]) / int(assessment_waitage[i]) * 100 # this is the conversion based on Rukshan comments which is the marked out is from the first row in the csv

                    else:     #here the value of mark_out_CSV[i]==0 which means the user did not add correct value for the wieght in the csv file or the value was 0
                        #row[i] = int(row[i])
                        row[i] = float(row[i]) / int(mark_out) * int(mark_worth)
                        row[i] = float(row[i]) / int(mark_worth) * 100



                    #elif conversion_radio_btn=="No":
                    #                row[i] = float(row[i])
                    #66666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666
                    #999999999999999999999999999999999999999999999999999999999999999999999999


                except ValueError: # if the cell has strange string such as (jklnlj) in the assessments grade, it will make it 0
                    row[i] = 0

        all_data_without_std_Name_ID = np.array(all_data_without_std_Name_ID) #convert list to array
        all_data_without_std_Name_ID = all_data_without_std_Name_ID.astype(float) #convert elements in the array from str to float

        #return render_template('empty1.html', all_data_without_std_Name_ID = all_data_without_std_Name_ID)
            #i=i+1


        #####################################################################################################3

        #7878787878
        #here i want to insert students name & id into the current_student table from the uploaded csv file
        try:
            con = sql.connect(host="pythonanywhere_host", user="pythonanywhere_user", password="pythonanywhere_password", database="pythonanywhere$database_name") #this is not the real connections details
            c =  con.cursor() # cursor
            # insert data # REPLACE INTO: do as insert in do does except if the assessment_name (PK) already exist in the database it will replace it with the new record


            for row in data_only_std_Name_ID:

                    c.execute("Insert ignore INTO current_student (student_id, student_name, course_id) VALUES (%s,%s,%s)", # REPLACE INTO: do as insert in do does except if the assessment_name (PK) already exist in the database it will replace it with the new record
                        (row[1], row[0], courseName))
                    con.commit() # apply changes

            #here in this small block, i store students mark, and assessment name into the student_grade table
            length_assessment_in_uplloaded_std_grade=len(all_data_without_std_Name_ID[0])
            con = sql.connect(host="pythonanywhere_host", user="pythonanywhere_user", password="pythonanywhere_password", database="pythonanywhere$database_name") #this is not the real connections details
            c =  con.cursor() # cursor
            # insert data # REPLACE INTO: do as insert in do does except if the assessment_name (PK) already exist in the database it will replace it with the new record

            #to get assessment name order form assessment table
            value = courseName
            query4 = "SELECT assessment_name FROM assessment WHERE course_course_id = %s  order by auto_increment"
            c.execute(query4,(value,))

            #assessments_order = c.fetchall()
            assessments_order = [ r[0] for r in c.fetchall() if str(r[0]) ]
            j=0#increment for std_id from data_only_std_Name_ID
            for row in all_data_without_std_Name_ID:
                for i in range(length_assessment_in_uplloaded_std_grade):

                    unconverted_mark = float(row[i]) / 100 * int(assessment_waitage[i]) # this is for the real mark (unconverted mark such as 18 out of 20)

                    lost_mark= int(assessment_waitage[i]) - float(unconverted_mark) # this is for the lost mark in the assessment
                    #return render_template('empty3.html', data = lost_mark)

                    c.execute("REPLACE INTO student_grade (student_id, assessment_name, course_id, mark, unconverted_mark, lost_mark) VALUES (%s,%s,%s,%s, %s, %s)", # REPLACE INTO: do as insert in do does except if the assessment_name (PK) already exist in the database it will replace it with the new record
                        #(data_only_std_Name_ID [j,1], assessments_order [i], courseName, row[i], unconverted_mark, lost_mark))
                        (data_only_std_Name_ID [j,1], assessments_order [i], courseName, round(row[i], 1), round(unconverted_mark, 1), round(lost_mark, 1)))
                    con.commit() # apply changes
                j=j+1
            #END OF here in this small block, i store students mark, and assessment name into the student_grade table






        except sql.Error as e: # if error
                    # then display the error in 'database_error.html' page
                    return render_template('database_error.html', error=e)

        finally:
                    con.close() # close the connection

        #EDN OF here i want to insert students name & id into the current_student table from the uploaded csv file
        #7878787878


#8888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888

        # here i want to choose the best model for the Binary classification

        if best_binary_model[0]=="RF": #form the radio button

            #first to check if there is model already created for this course based on how many columns in the uploaded csv file
            if exists(picklename+"_RF_Multiclass_model_"+ str(columns-2)+".pkl" and picklename+"_RF_Binary_model_"+ str(columns-2)+".pkl"): #pridict for the RF multiclass





                #to perform prediction using the binary models
                with open(picklename+"_RF_Binary_model_"+ str(columns-2)+".pkl", "rb") as f:
                    model = pickle.load(f)

                prediction_binary = model.predict(all_data_without_std_Name_ID)
                output_binary=prediction_binary

                ML_used_binary="LR" # to check if the code ise right or not make sure which ml result is


                #return render_template('predict_csv.html',ML_used_binary=ML_used_binary, cityList=cityList , prediction_text_binary =output_binary, prediction_text_multiclass=output_multiclass, data_only_std_Name_ID = data_only_std_Name_ID )



            #here i want to check if there are models but user enter features more than created model. for example: try to predict with 4 features in 2 features created model
            elif exists(picklename+"_RF_Multiclass_model_1.pkl" and picklename+"_RF_Binary_model_1.pkl"):  #pridict for the RF Binary
                 return render_template('sorry_features_more_than_created_models.html', length_all_assessments_in_selected_course= (length_all_assessments_in_selected_course-1))



            else:
                return render_template('sorry_no_model_has_been_created_for_this_course.html')

            #111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111

        elif best_binary_model[0]=="SVM":
            if exists(picklename+"_SVM_Multiclass_model_"+ str(columns-2)+".pkl" and picklename+"_SVM_Binary_model_"+ str(columns-2)+".pkl"):


                #to perform prediction using the binary models
                with open(picklename+"_SVM_Binary_model_"+ str(columns-2)+".pkl", "rb") as f:
                    model = pickle.load(f)

                prediction_binary = model.predict(all_data_without_std_Name_ID)
                output_binary=prediction_binary

                ML_used_binary="SVM"
                #return render_template('predict_csv.html',cityList=cityList ,prediction_text_binary=output_binary, prediction_text_multiclass=output_multiclass )
                #return render_template('predict_csv.html', ML_used_binary=ML_used_binary, cityList=cityList , prediction_text_binary =output_binary, prediction_text_multiclass=output_multiclass, data_only_std_Name_ID = data_only_std_Name_ID )

            else:
                return render_template('sorry_no_model_has_been_created_for_this_course.html')

            #11111111111111111111111111111111111111111111111111111111111111111111111111111111111111

        elif best_binary_model[0]=="KNN":
            if exists(picklename+"_KNN_Multiclass_model_"+ str(columns-2)+".pkl" and picklename+"_KNN_Binary_model_"+ str(columns-2)+".pkl"):



                #to perform prediction using the binary models
                with open(picklename+"_KNN_Binary_model_"+ str(columns-2)+".pkl", "rb") as f:
                    model = pickle.load(f)

                prediction_binary = model.predict(all_data_without_std_Name_ID)
                output_binary=prediction_binary

                ML_used_binary="KNN"

                #return render_template('predict_csv.html', ML_used_binary=ML_used_binary, cityList=cityList , prediction_text_binary =output_binary, prediction_text_multiclass=output_multiclass, data_only_std_Name_ID = data_only_std_Name_ID )



            #here i want to check if there are models but user enter features more than created model. for example: try to predict with 4 features in 2 features created model
            elif exists(picklename+"_KNN_Multiclass_model_1.pkl" and picklename+"_KNN_Binary_model_1.pkl"):
                 return render_template('sorry_features_more_than_created_models.html', length_all_assessments_in_selected_course= (length_all_assessments_in_selected_course-1))



            else:
                return render_template('sorry_no_model_has_been_created_for_this_course.html')

            #11111111111111111111111111111111111111111111111

        elif best_binary_model[0]=="NB":
            if exists(picklename+"_NB_Multiclass_model_"+ str(columns-2)+".pkl" and picklename+"_NB_Binary_model_"+ str(columns-2)+".pkl"):



                #to perform prediction using the binary models
                with open(picklename+"_NB_Binary_model_"+ str(columns-2)+".pkl", "rb") as f:
                    model = pickle.load(f)

                # here i want to fix the proplem of NB prediction which is : numpy.core._exceptions.UFuncTypeError: ufunc 'subtract' did not contain a loop with signature matching types (dtype('<U32'), dtype('<U32')) -> dtype('<U32')
                    # what i have done to solve the problem is: first i conver the list (all_data_without_std_Name_ID) to an array, then i conver its type from string to float
                all_data_without_std_Name_ID_NB = all_data_without_std_Name_ID.astype(np.float)

                prediction_binary = model.predict(all_data_without_std_Name_ID_NB)
                output_binary=prediction_binary

                ML_used_binary="NB"
                #return render_template('predict_csv.html',cityList=cityList ,prediction_text_binary=output_binary, prediction_text_multiclass=output_multiclass )
                #return render_template('predict_csv.html',ML_used=ML_used, cityList=cityList , prediction_text_binary =output_binary, prediction_text_multiclass=output_multiclass, data_only_std_Name_ID = data_only_std_Name_ID )



            #here i want to check if there are models but user enter features more than created model. for example: try to predict with 4 features in 2 features created model
            elif exists(picklename+"_NB_Multiclass_model_1.pkl" and picklename+"_NB_Binary_model_1.pkl"):
                 return render_template('sorry_features_more_than_created_models.html', length_all_assessments_in_selected_course= (length_all_assessments_in_selected_course-1))

            else:
                return render_template('sorry_no_model_has_been_created_for_this_course.html')

            #11111111111111111111111111111111111111111111111

        elif best_binary_model[0]=="DT":
            if exists(picklename+"_DT_Multiclass_model_"+ str(columns-2)+".pkl" and picklename+"_DT_Binary_model_"+ str(columns-2)+".pkl"):



                #to perform prediction using the binary models
                with open(picklename+"_DT_Binary_model_"+ str(columns-2)+".pkl", "rb") as f:
                    model = pickle.load(f)

                prediction_binary = model.predict(all_data_without_std_Name_ID)
                output_binary=prediction_binary

                ML_used_binary="DT"
                #return render_template('predict_csv.html',cityList=cityList ,prediction_text_binary=output_binary, prediction_text_multiclass=output_multiclass )
                #return render_template('predict_csv.html',ML_used=ML_used, cityList=cityList , prediction_text_binary =output_binary, prediction_text_multiclass=output_multiclass, data_only_std_Name_ID = data_only_std_Name_ID )



            #here i want to check if there are models but user enter features more than created model. for example: try to predict with 4 features in 2 features created model
            elif exists(picklename+"_DT_Multiclass_model_1.pkl" and picklename+"_DT_Binary_model_1.pkl"):
                 return render_template('sorry_features_more_than_created_models.html', length_all_assessments_in_selected_course= (length_all_assessments_in_selected_course-1))

            else:
                return render_template('sorry_no_model_has_been_created_for_this_course.html')




    #8888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888


    # here i want to choose the best model for the multiclass classification

        if best_multiclass_model[0]=="RF": #form the radio button

            #first to check if there is model already created for this course based on how many columns in the uploaded csv file
            if exists(picklename+"_RF_Multiclass_model_"+ str(columns-2)+".pkl" and picklename+"_RF_Binary_model_"+ str(columns-2)+".pkl"): #pridict for the RF multiclass

                #to perform prediction using the multiclass models
                with open(picklename+"_RF_Multiclass_model_"+ str(columns-2)+".pkl", "rb") as f:
                    model = pickle.load(f)



                prediction_multiclass = model.predict(all_data_without_std_Name_ID) # predict for the whole data [everything in the csv file] # so the prediction_multiclass is list type because it predicts for the whole data in the csv
                output_multiclass = prediction_multiclass # store prediction result for the _RF_Multiclass_model_(how many column in the csv file)



                ML_used_multiclass="LR" # to check if the code ise right or not make sure which ml result is

                #9876543210
                #in this block, i store the results of prediction into student_prediction_results table
                csv_file_raw_length = len(data_only_std_Name_ID)
                data_only_std_Name_ID= np.array(data_only_std_Name_ID)


                #to get from the uploaded csv file to know this prediction after which assessment
                length_column_in_csvfile_assessments_grade=len(all_data_without_std_Name_ID[0])
                length_column_in_csvfile_assessments_grade=int(length_column_in_csvfile_assessments_grade)
                #return render_template('empty1.html', all_data_without_std_Name_ID = length_column_in_csvfile_assessments_grade)

                try:
                    con = sql.connect(host="pythonanywhere_host", user="pythonanywhere_user", password="pythonanywhere_password", database="pythonanywhere$database_name") #this is not the real connections details
                    c =  con.cursor() # cursor
                    # insert data # REPLACE INTO: do as insert in do does except if the assessment_name (PK) already exist in the database it will replace it with the new record

                    #to get assessment name order form assessment table
                    value = courseName
                    query4 = "SELECT assessment_name FROM assessment WHERE course_course_id = %s  order by auto_increment"
                    c.execute(query4,(value,))

                    #assessments_order = c.fetchall()
                    assessments_order = [ r[0] for r in c.fetchall() if str(r[0]) ]

                    #End of to get assessment name order form assessment table

                    for i in range(csv_file_raw_length):
                        c.execute("REPLACE INTO student_prediction_results (student_id, course_id, assessment_name, Binary_prediction_results, Multiclass_prediction_results, number_of_assessment_in_prediction) VALUES (%s,%s,%s,%s,%s, %s)", # REPLACE INTO: do as insert in do does except if the assessment_name (PK) already exist in the database it will replace it with the new record
                              (str(data_only_std_Name_ID[i,1]), courseName, str(assessments_order[length_column_in_csvfile_assessments_grade-1]), str(output_binary[i]), output_multiclass[i], length_column_in_csvfile_assessments_grade))
                        con.commit() # apply changes




                    #return render_template('empty1.html', all_data_without_std_Name_ID = assessments_order[length_column_in_csvfile_assessments_grade-1])

                except sql.Error as e: # if error
                        # then display the error in 'database_error.html' page
                        return render_template('database_error.html', error=e)

                finally:
                        con.close() # close the connection



                #Edn of in this block, i store the results of prediction into student_prediction_results table
                #9876543210



                return render_template('predict_csv_simple.html', ML_used_multiclass = ML_used_multiclass, ML_used_binary = ML_used_binary, cityList=cityList , prediction_text_binary =output_binary, prediction_text_multiclass=output_multiclass, data_only_std_Name_ID = data_only_std_Name_ID, best_binary_model_accuracy = best_binary_model_accuracy, best_multiclass_model_accuracy = best_multiclass_model_accuracy)



            #here i want to check if there are models but user enter features more than created model. for example: try to predict with 4 features in 2 features created model
            elif exists(picklename+"_RF_Multiclass_model_1.pkl" and picklename+"_RF_Binary_model_1.pkl"):  #pridict for the RF Binary
                 return render_template('sorry_features_more_than_created_models.html', length_all_assessments_in_selected_course= (length_all_assessments_in_selected_course-1))



            else:
                return render_template('sorry_no_model_has_been_created_for_this_course.html')

            #111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111

        elif best_multiclass_model[0]=="SVM":
            if exists(picklename+"_SVM_Multiclass_model_"+ str(columns-2)+".pkl" and picklename+"_SVM_Binary_model_"+ str(columns-2)+".pkl"):

                #to perform prediction using the multiclass models
                with open(picklename+"_SVM_Multiclass_model_"+ str(columns-2)+".pkl", "rb") as f:
                    model = pickle.load(f)

                prediction_multiclass = model.predict(all_data_without_std_Name_ID)
                output_multiclass = prediction_multiclass



                ML_used_multiclass="SVM"

                #9876543210
                #in this block, i store the results of prediction into student_prediction_results table
                csv_file_raw_length = len(data_only_std_Name_ID)
                data_only_std_Name_ID= np.array(data_only_std_Name_ID)


                #to get from the uploaded csv file to know this prediction after which assessment
                length_column_in_csvfile_assessments_grade=len(all_data_without_std_Name_ID[0])
                length_column_in_csvfile_assessments_grade=int(length_column_in_csvfile_assessments_grade)
                #return render_template('empty1.html', all_data_without_std_Name_ID = length_column_in_csvfile_assessments_grade)

                try:
                    con = sql.connect(host="pythonanywhere_host", user="pythonanywhere_user", password="pythonanywhere_password", database="pythonanywhere$database_name") #this is not the real connections details
                    c =  con.cursor() # cursor
                    # insert data # REPLACE INTO: do as insert in do does except if the assessment_name (PK) already exist in the database it will replace it with the new record

                    #to get assessment name order form assessment table
                    value = courseName
                    query4 = "SELECT assessment_name FROM assessment WHERE course_course_id = %s  order by auto_increment"
                    c.execute(query4,(value,))

                    #assessments_order = c.fetchall()
                    assessments_order = [ r[0] for r in c.fetchall() if str(r[0]) ]

                    #End of to get assessment name order form assessment table

                    for i in range(csv_file_raw_length):
                        c.execute("REPLACE INTO student_prediction_results (student_id, course_id, assessment_name, Binary_prediction_results, Multiclass_prediction_results, number_of_assessment_in_prediction) VALUES (%s,%s,%s,%s,%s, %s)", # REPLACE INTO: do as insert in do does except if the assessment_name (PK) already exist in the database it will replace it with the new record
                              (str(data_only_std_Name_ID[i,1]), courseName, str(assessments_order[length_column_in_csvfile_assessments_grade-1]), str(output_binary[i]), output_multiclass[i], length_column_in_csvfile_assessments_grade))
                        con.commit() # apply changes




                    #return render_template('empty1.html', all_data_without_std_Name_ID = assessments_order[length_column_in_csvfile_assessments_grade-1])

                except sql.Error as e: # if error
                        # then display the error in 'database_error.html' page
                        return render_template('database_error.html', error=e)

                finally:
                        con.close() # close the connection



                #Edn of in this block, i store the results of prediction into student_prediction_results table
                #9876543210


                return render_template('predict_csv_simple.html', ML_used_multiclass = ML_used_multiclass, ML_used_binary = ML_used_binary, cityList=cityList , prediction_text_binary =output_binary, prediction_text_multiclass=output_multiclass, data_only_std_Name_ID = data_only_std_Name_ID, best_binary_model_accuracy = best_binary_model_accuracy, best_multiclass_model_accuracy = best_multiclass_model_accuracy)




            else:
                return render_template('sorry_no_model_has_been_created_for_this_course.html')

            #11111111111111111111111111111111111111111111111111111111111111111111111111111111111111

        elif best_multiclass_model[0]=="KNN":
            if exists(picklename+"_KNN_Multiclass_model_"+ str(columns-2)+".pkl" and picklename+"_KNN_Binary_model_"+ str(columns-2)+".pkl"):

                #to perform prediction using the multiclass models
                with open(picklename+"_KNN_Multiclass_model_"+ str(columns-2)+".pkl", "rb") as f:
                    model = pickle.load(f)

                prediction_multiclass = model.predict(all_data_without_std_Name_ID)
                output_multiclass = prediction_multiclass


                ML_used_multiclass="KNN"

                #9876543210
                #in this block, i store the results of prediction into student_prediction_results table
                csv_file_raw_length = len(data_only_std_Name_ID)
                data_only_std_Name_ID= np.array(data_only_std_Name_ID)


                #to get from the uploaded csv file to know this prediction after which assessment
                length_column_in_csvfile_assessments_grade=len(all_data_without_std_Name_ID[0])
                length_column_in_csvfile_assessments_grade=int(length_column_in_csvfile_assessments_grade)
                #return render_template('empty1.html', all_data_without_std_Name_ID = length_column_in_csvfile_assessments_grade)

                try:
                    con = sql.connect(host="pythonanywhere_host", user="pythonanywhere_user", password="pythonanywhere_password", database="pythonanywhere$database_name") #this is not the real connections details
                    c =  con.cursor() # cursor
                    # insert data # REPLACE INTO: do as insert in do does except if the assessment_name (PK) already exist in the database it will replace it with the new record

                    #to get assessment name order form assessment table
                    value = courseName
                    query4 = "SELECT assessment_name FROM assessment WHERE course_course_id = %s  order by auto_increment"
                    c.execute(query4,(value,))

                    #assessments_order = c.fetchall()
                    assessments_order = [ r[0] for r in c.fetchall() if str(r[0]) ]

                    #End of to get assessment name order form assessment table

                    for i in range(csv_file_raw_length):
                        c.execute("REPLACE INTO student_prediction_results (student_id, course_id, assessment_name, Binary_prediction_results, Multiclass_prediction_results, number_of_assessment_in_prediction) VALUES (%s,%s,%s,%s,%s, %s)", # REPLACE INTO: do as insert in do does except if the assessment_name (PK) already exist in the database it will replace it with the new record
                              (str(data_only_std_Name_ID[i,1]), courseName, str(assessments_order[length_column_in_csvfile_assessments_grade-1]), str(output_binary[i]), output_multiclass[i], length_column_in_csvfile_assessments_grade))
                        con.commit() # apply changes




                    #return render_template('empty1.html', all_data_without_std_Name_ID = assessments_order[length_column_in_csvfile_assessments_grade-1])

                except sql.Error as e: # if error
                        # then display the error in 'database_error.html' page
                        return render_template('database_error.html', error=e)

                finally:
                        con.close() # close the connection



                #Edn of in this block, i store the results of prediction into student_prediction_results table
                #9876543210


                return render_template('predict_csv_simple.html', ML_used_multiclass = ML_used_multiclass, ML_used_binary = ML_used_binary, cityList=cityList , prediction_text_binary =output_binary, prediction_text_multiclass=output_multiclass, data_only_std_Name_ID = data_only_std_Name_ID, best_binary_model_accuracy = best_binary_model_accuracy, best_multiclass_model_accuracy = best_multiclass_model_accuracy)




            #here i want to check if there are models but user enter features more than created model. for example: try to predict with 4 features in 2 features created model
            elif exists(picklename+"_KNN_Multiclass_model_1.pkl" and picklename+"_KNN_Binary_model_1.pkl"):
                 return render_template('sorry_features_more_than_created_models.html', length_all_assessments_in_selected_course= (length_all_assessments_in_selected_course-1))



            else:
                return render_template('sorry_no_model_has_been_created_for_this_course.html')

            #11111111111111111111111111111111111111111111111

        elif best_multiclass_model[0]=="NB":
            if exists(picklename+"_NB_Multiclass_model_"+ str(columns-2)+".pkl" and picklename+"_NB_Binary_model_"+ str(columns-2)+".pkl"):

                #to perform prediction using the multiclass models
                with open(picklename+"_NB_Multiclass_model_"+ str(columns-2)+".pkl", "rb") as f:
                    model = pickle.load(f)

                # here i want to fix the proplem of NB prediction which is : numpy.core._exceptions.UFuncTypeError: ufunc 'subtract' did not contain a loop with signature matching types (dtype('<U32'), dtype('<U32')) -> dtype('<U32')
                    # what i have done to solve the problem is: first i conver the list (all_data_without_std_Name_ID) to an array, then i conver its type from string to float
                all_data_without_std_Name_ID_NB = all_data_without_std_Name_ID.astype(np.float)

                prediction_multiclass = model.predict(all_data_without_std_Name_ID_NB)
                output_multiclass = prediction_multiclass


                ML_used_multiclass="NB"

                #9876543210
                #in this block, i store the results of prediction into student_prediction_results table
                csv_file_raw_length = len(data_only_std_Name_ID)
                data_only_std_Name_ID= np.array(data_only_std_Name_ID)


                #to get from the uploaded csv file to know this prediction after which assessment
                length_column_in_csvfile_assessments_grade=len(all_data_without_std_Name_ID[0])
                length_column_in_csvfile_assessments_grade=int(length_column_in_csvfile_assessments_grade)
                #return render_template('empty1.html', all_data_without_std_Name_ID = length_column_in_csvfile_assessments_grade)

                try:
                    con = sql.connect(host="pythonanywhere_host", user="pythonanywhere_user", password="pythonanywhere_password", database="pythonanywhere$database_name") #this is not the real connections details
                    c =  con.cursor() # cursor
                    # insert data # REPLACE INTO: do as insert in do does except if the assessment_name (PK) already exist in the database it will replace it with the new record

                    #to get assessment name order form assessment table
                    value = courseName
                    query4 = "SELECT assessment_name FROM assessment WHERE course_course_id = %s  order by auto_increment"
                    c.execute(query4,(value,))

                    #assessments_order = c.fetchall()
                    assessments_order = [ r[0] for r in c.fetchall() if str(r[0]) ]

                    #End of to get assessment name order form assessment table

                    for i in range(csv_file_raw_length):
                        c.execute("REPLACE INTO student_prediction_results (student_id, course_id, assessment_name, Binary_prediction_results, Multiclass_prediction_results, number_of_assessment_in_prediction) VALUES (%s,%s,%s,%s,%s, %s)", # REPLACE INTO: do as insert in do does except if the assessment_name (PK) already exist in the database it will replace it with the new record
                              (str(data_only_std_Name_ID[i,1]), courseName, str(assessments_order[length_column_in_csvfile_assessments_grade-1]), str(output_binary[i]), output_multiclass[i], length_column_in_csvfile_assessments_grade))
                        con.commit() # apply changes




                    #return render_template('empty1.html', all_data_without_std_Name_ID = assessments_order[length_column_in_csvfile_assessments_grade-1])

                except sql.Error as e: # if error
                        # then display the error in 'database_error.html' page
                        return render_template('database_error.html', error=e)

                finally:
                        con.close() # close the connection



                #Edn of in this block, i store the results of prediction into student_prediction_results table
                #9876543210

                #return render_template('predict_csv.html',cityList=cityList ,prediction_text_binary=output_binary, prediction_text_multiclass=output_multiclass )
                return render_template('predict_csv_simple.html', ML_used_multiclass = ML_used_multiclass, ML_used_binary = ML_used_binary, cityList=cityList , prediction_text_binary =output_binary, prediction_text_multiclass=output_multiclass, data_only_std_Name_ID = data_only_std_Name_ID, best_binary_model_accuracy = best_binary_model_accuracy, best_multiclass_model_accuracy = best_multiclass_model_accuracy)




            #here i want to check if there are models but user enter features more than created model. for example: try to predict with 4 features in 2 features created model
            elif exists(picklename+"_NB_Multiclass_model_1.pkl" and picklename+"_NB_Binary_model_1.pkl"):
                 return render_template('sorry_features_more_than_created_models.html', length_all_assessments_in_selected_course= (length_all_assessments_in_selected_course-1))

            else:
                return render_template('sorry_no_model_has_been_created_for_this_course.html')

            #11111111111111111111111111111111111111111111111

        elif best_multiclass_model[0]=="DT":
            if exists(picklename+"_DT_Multiclass_model_"+ str(columns-2)+".pkl" and picklename+"_DT_Binary_model_"+ str(columns-2)+".pkl"):

                #to perform prediction using the multiclass models
                with open(picklename+"_DT_Multiclass_model_"+ str(columns-2)+".pkl", "rb") as f:
                    model = pickle.load(f)

                prediction_multiclass = model.predict(all_data_without_std_Name_ID)
                output_multiclass = prediction_multiclass



                ML_used_multiclass="DT"

                #9876543210
                #in this block, i store the results of prediction into student_prediction_results table
                csv_file_raw_length = len(data_only_std_Name_ID)
                data_only_std_Name_ID= np.array(data_only_std_Name_ID)


                #to get from the uploaded csv file to know this prediction after which assessment
                length_column_in_csvfile_assessments_grade=len(all_data_without_std_Name_ID[0])
                length_column_in_csvfile_assessments_grade=int(length_column_in_csvfile_assessments_grade)
                #return render_template('empty1.html', all_data_without_std_Name_ID = length_column_in_csvfile_assessments_grade)

                try:
                    con = sql.connect(host="pythonanywhere_host", user="pythonanywhere_user", password="pythonanywhere_password", database="pythonanywhere$database_name") #this is not the real connections details
                    c =  con.cursor() # cursor
                    # insert data # REPLACE INTO: do as insert in do does except if the assessment_name (PK) already exist in the database it will replace it with the new record

                    #to get assessment name order form assessment table
                    value = courseName
                    query4 = "SELECT assessment_name FROM assessment WHERE course_course_id = %s  order by auto_increment"
                    c.execute(query4,(value,))

                    #assessments_order = c.fetchall()
                    assessments_order = [ r[0] for r in c.fetchall() if str(r[0]) ]

                    #End of to get assessment name order form assessment table

                    for i in range(csv_file_raw_length):
                        c.execute("REPLACE INTO student_prediction_results (student_id, course_id, assessment_name, Binary_prediction_results, Multiclass_prediction_results, number_of_assessment_in_prediction) VALUES (%s,%s,%s,%s,%s, %s)", # REPLACE INTO: do as insert in do does except if the assessment_name (PK) already exist in the database it will replace it with the new record
                              (str(data_only_std_Name_ID[i,1]), courseName, str(assessments_order[length_column_in_csvfile_assessments_grade-1]), str(output_binary[i]), output_multiclass[i], length_column_in_csvfile_assessments_grade))
                        con.commit() # apply changes




                    #return render_template('empty1.html', all_data_without_std_Name_ID = assessments_order[length_column_in_csvfile_assessments_grade-1])

                except sql.Error as e: # if error
                        # then display the error in 'database_error.html' page
                        return render_template('database_error.html', error=e)

                finally:
                        con.close() # close the connection



                #Edn of in this block, i store the results of prediction into student_prediction_results table
                #9876543210

                #return render_template('predict_csv.html',cityList=cityList ,prediction_text_binary=output_binary, prediction_text_multiclass=output_multiclass )
                return render_template('predict_csv_simple.html', ML_used_multiclass = ML_used_multiclass, ML_used_binary = ML_used_binary, cityList=cityList , prediction_text_binary =output_binary, prediction_text_multiclass=output_multiclass, data_only_std_Name_ID = data_only_std_Name_ID, best_binary_model_accuracy = best_binary_model_accuracy, best_multiclass_model_accuracy = best_multiclass_model_accuracy)



            #here i want to check if there are models but user enter features more than created model. for example: try to predict with 4 features in 2 features created model
            elif exists(picklename+"_DT_Multiclass_model_1.pkl" and picklename+"_DT_Binary_model_1.pkl"):
                 return render_template('sorry_features_more_than_created_models.html', length_all_assessments_in_selected_course= (length_all_assessments_in_selected_course-1))

            else:
                return render_template('sorry_no_model_has_been_created_for_this_course.html')


    else:
        return render_template('sorry_no_file_selected_in_prediction_csv.html') # i solved this issue by making the input file required
        #return 'No selected file'



##############################################################################################
###################################### END OF Prediction for predict_csv_simple  #############
##############################################################################################

##############################################################################################
###################################### Prediction for predict_csv  ###########################
##############################################################################################

    # here is the [advance options] which academics choose the algorithms they want
# i used this because i just dont want to show tables before prforming prediction
@app.route('/predict_csv_first') # this is the GET function that take you to/render_template  predict_csv.html
@login_required
def predict_csv_first():
    try:
        con = sql.connect(host="pythonanywhere_host", user="pythonanywhere_user", password="pythonanywhere_password", database="pythonanywhere$database_name") #this is not the real connections details
        c =  con.cursor() # cursor

        query = "Select * from course_and_models where userName=%s"
        values = session["USERNAME"]
        cityList = c.execute(query, (values,))
        cityList = c.fetchall()

        return render_template('predict_csv_first.html', cityList=cityList)

    except sql.Error as e: # if error
            # then display the error in 'database_error.html' page
            return render_template('database_error.html', error=e)

    finally:
        con.close() # close the connection



@app.route('/predict_csv') # this is the GET function that take you to/render_template  predict_csv.html
@login_required
def predict_csv():
    try:
        con = sql.connect(host="pythonanywhere_host", user="pythonanywhere_user", password="pythonanywhere_password", database="pythonanywhere$database_name") #this is not the real connections details
        c =  con.cursor() # cursor

        query = "Select * from course_and_models where userName=%s"
        values = session["USERNAME"]
        cityList = c.execute(query, (values,))
        cityList = c.fetchall()

        return render_template('predict_csv.html', cityList=cityList)

    except sql.Error as e: # if error
            # then display the error in 'database_error.html' page
            return render_template('database_error.html', error=e)

    finally:
        con.close() # close the connection

# this is for the advanced option in prediction
@app.route('/predict_from_csv',methods=['POST']) # this is for the advanced option in prediction
@login_required
def predict_from_csv():
    '''
    For rendering results on HTML GUI
    '''
    ################################################### here just to show the dropdown box after making prediction
    try:
        con = sql.connect(host="pythonanywhere_host", user="pythonanywhere_user", password="pythonanywhere_password", database="pythonanywhere$database_name") #this is not the real connections details
        c =  con.cursor() # cursor
        query = "Select * from course_and_models where userName=%s"
        values = session["USERNAME"]
        cityList = c.execute(query, (values,))
        cityList = c.fetchall()

    except sql.Error as e: # if error
            # then display the error in 'database_error.html' page
            return render_template('database_error.html', error=e)

    finally:
            con.close() # close the connection
    ###################################################


    courseName = request.form['course_name']
    picklename = courseName
    #conversion_radio_btn = request.form['conversion'] # from the conversion radio button

    ML_algorithms_name_binary = request.form['ml_algorithm_binary'] # from the radio button
    ML_algorithms_name_multiclass = request.form['ml_algorithm_multiclass'] # from the radio button

    try:
        con = sql.connect(host="pythonanywhere_host", user="pythonanywhere_user", password="pythonanywhere_password", database="pythonanywhere$database_name") #this is not the real connections details
        c =  con.cursor() # cursor
    #here I want to get all assessment in the selected course so i can check if prediction csv file has column more that created models
        all_assessments_in_selected_course_query= "SELECT assessment_name  FROM assessment where course_course_id=%s order by auto_increment"
        values = (courseName)
        #here i want to fech all assessments from database for a specefic course [(course_id) from the function (function_create_dataset) parameter
        all_assessments_in_selected_course= c.execute(all_assessments_in_selected_course_query, (values,))
        all_assessments_in_selected_course = c.fetchall()
        # to get the length of all assessments for selected course (to know how many assessment in this course)
        length_all_assessments_in_selected_course= len(all_assessments_in_selected_course)

    except sql.Error as e: # if error
            # then display the error in 'database_error.html' page
        return render_template('database_error.html', error=e)

    finally:
        con.close() # close the connection


    csv_file = request.files['file']
    if request.files['file'].filename != '': # if there is file the user upload it # i overcome this issue by making input file required
        #output=""   # i dont need it anymore
        csv_file = request.files['file']

        # this helps me to validate if the uploaded file is a csv extention
        file_ext = os.path.splitext(request.files['file'].filename)[1]
        #return render_template('no_dashboard_yet.html', data = file_ext)
        if file_ext not in app.config['UPLOAD_EXTENSIONS']:
            return render_template('no_dashboard_yet.html', data = "please make sure to upload a csv file")
        # END OF this helps me to validate if the uploaded file is a csv extention


        csv_file = TextIOWrapper(csv_file, encoding='utf-8')
        csv_reader = csv.reader(csv_file, delimiter=',')
        next(csv_reader)
        data = [row for row in csv_reader]

        if len(data) == 0:
                return render_template('empty.html')

        #........................................................................................................................
        #here i want to do Rukshan comments about making the first row in CSV file the weight [mark of]
        mark_out_CSV_array = np.array(data)
        #ttype=type(my_array) #temppp
        mark_out_CSV= mark_out_CSV_array[0,2:]  #to take the first row only and after sdt_name and std_ID [only the weight]
        assessment_waitage= mark_out_CSV_array[1,2:]  #to take the second row only and after sdt_name and std_ID [only the weight]


        data = np.array(data)
        data= data [2:, :]
        data=data.tolist()
        #return render_template('empty3.html', data = data)

        #.......................................................................................................................



        #to know check how many column in array (data)
        columns = len(data[0])

        #############
        # here i want to make sure the uploaded file has features less than or equal to the number of assessments in the selected course minu the funal exam
        if columns>(length_all_assessments_in_selected_course+2): # this is to check if csv file feature has more feature than course's assessment s
            #return render_template('too_big_csv_file.html')    # if csv file has feature more than number of assessments in the database
            return render_template('sorry_features_more_than_created_models.html', length_all_assessments_in_selected_course= (length_all_assessments_in_selected_course-1))

        ##############



        data = np.array(data) #here i convert data (type: list i think) to array

        all_data_without_std_Name_ID=data[:,2:] #here I removed student name and ID from the data in a new array because i want to send this version to the models to predict

        data_only_std_Name_ID = data[:,:2]  #here I removed all marks and kept student name and ID to used it in the html tables to present students names and id with their results


        #here I want to make sure the csv file does not have any error such as empty cell or "hjbkjb" value
        #####################################################################################################3
        all_data_without_std_Name_ID = np.array(all_data_without_std_Name_ID)
        #columns
        for row in all_data_without_std_Name_ID:

            for i in range(columns-2):



                if row[i]=="": #if the is null in the assessment make it 0
                   row[i]=0



                try:# i used try and except ValueError, to solve if data in the csv file is not nubmber such as jkhkjnh

                    #row[i]=int(row[i]) #i used float because when using int any float number return it 0, so i had to use float



                    #999999999999999999999999999999999999999999999999999999999999999999999999
                    #3333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333
                    #here i want to make sure to match students_id btn student and assessments_Std tables
                    con = sql.connect(host="pythonanywhere_host", user="pythonanywhere_user", password="pythonanywhere_password", database="pythonanywhere$database_name") #this is not the real connections details
                    c = con.cursor() # cursor
                    c = con.cursor(buffered=True)

                    value = courseName
                    query4 = "SELECT assessment_name FROM assessment WHERE course_course_id = %s  order by auto_increment"
                    c.execute(query4,(value,))

                    assessments_order = c.fetchall()

                    assessment_name_to_string = ",".join(assessments_order [i]) #to solve error "python mysqlconnector mysqlinterfaceerror python type tuple cannot be converted"
                    #3333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333

                    #if conversion_radio_btn=="Yes": # here i did the if because i want to check if the user want to convert the data in the csv file or not

                    #here in this block, I tried to convert students marks into a Percentages as Simon suggested useing mark_out and mark_worth
                    #66666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666
                    query5 = "SELECT mark_out FROM assessment where course_course_id=%s and assessment_name =%s"


                    query6 = "SELECT mark_worth FROM assessment where course_course_id=%s and assessment_name =%s"

                    c.execute(query5,(courseName,assessment_name_to_string,))
                    mark_out = [ r[0] for r in c.fetchall() if str(r[0]) ]

                    c.execute(query6,(courseName,assessment_name_to_string,))
                    mark_worth = [ r[0] for r in c.fetchall() if str(r[0]) ]

                    mark_out = np.array(mark_out)
                    mark_worth = np.array(mark_worth)




                    if mark_out_CSV[i] !="0" and assessment_waitage[i] !="0":

                        row[i] = float(row[i]) / int(mark_out_CSV[i]) * int(assessment_waitage[i])
                        row[i] = float(row[i]) / int(assessment_waitage[i]) * 100 # this is the conversion based on Rukshan comments which is the marked out is from the first row in the csv

                    else:     #here the value of mark_out_CSV[i]==0 which means the user did not add correct value for the wieght in the csv file or the value was 0
                        #row[i] = int(row[i])
                        row[i] = float(row[i]) / int(mark_out) * int(mark_worth)
                        row[i] = float(row[i]) / int(mark_worth) * 100


                    #elif conversion_radio_btn=="No":
                    #                row[i] = float(row[i])

                    #66666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666
                    #999999999999999999999999999999999999999999999999999999999999999999999999





                except ValueError: # if the cell has strange string such as (jklnlj) in the assessments grade, it will make it 0
                    row[i] = 0

        all_data_without_std_Name_ID = np.array(all_data_without_std_Name_ID) #convert list to array
        all_data_without_std_Name_ID = all_data_without_std_Name_ID.astype(float) #convert elements in the array from str to float

        #return render_template('empty1.html', all_data_without_std_Name_ID = all_data_without_std_Name_ID, mark_out=mark_out, mark_worth=mark_worth)
        #return render_template('empty1.html', mark_out=mark_out, mark_worth=mark_worth)
        #return render_template('empty1.html', assessment_name_to_string=assessments_order)
        #return render_template('empty1.html', all_data_without_std_Name_ID = all_data_without_std_Name_ID)
            #i=i+1


        #####################################################################################################3

        #7878787878
        #here i want to insert students name & id into the current_student table from the uploaded csv file
        try:
            con = sql.connect(host="pythonanywhere_host", user="pythonanywhere_user", password="pythonanywhere_password", database="pythonanywhere$database_name") #this is not the real connections details
            c =  con.cursor() # cursor
            # insert data # REPLACE INTO: do as insert in do does except if the assessment_name (PK) already exist in the database it will replace it with the new record


            for row in data_only_std_Name_ID:

                    c.execute("insert ignore INTO current_student (student_id, student_name, course_id) VALUES (%s,%s,%s)", # REPLACE INTO: do as insert in do does except if the assessment_name (PK) already exist in the database it will replace it with the new record
                        (row[1], row[0], courseName))
                    con.commit() # apply changes

            #here in this small block, i store students mark, and assessment name into the student_grade table
            length_assessment_in_uplloaded_std_grade=len(all_data_without_std_Name_ID[0])
            con = sql.connect(host="pythonanywhere_host", user="pythonanywhere_user", password="pythonanywhere_password", database="pythonanywhere$database_name") #this is not the real connections details
            c =  con.cursor() # cursor
            # insert data # REPLACE INTO: do as insert in do does except if the assessment_name (PK) already exist in the database it will replace it with the new record

            #to get assessment name order form assessment table
            value = courseName
            query4 = "SELECT assessment_name FROM assessment WHERE course_course_id = %s  order by auto_increment"
            c.execute(query4,(value,))

            #assessments_order = c.fetchall()
            assessments_order = [ r[0] for r in c.fetchall() if str(r[0]) ]
            j=0#increment for std_id from data_only_std_Name_ID
            for row in all_data_without_std_Name_ID:
                for i in range(length_assessment_in_uplloaded_std_grade):

                    unconverted_mark = float(row[i]) / 100 * int(assessment_waitage[i]) # this is for the real mark (unconverted mark such as 18 out of 20)

                    lost_mark= int(assessment_waitage[i]) - float(unconverted_mark) # this is for the lost mark in the assessment
                    #return render_template('empty3.html', data = lost_mark)

                    c.execute("REPLACE INTO student_grade (student_id, assessment_name, course_id, mark, unconverted_mark, lost_mark) VALUES (%s,%s,%s,%s, %s, %s)", # REPLACE INTO: do as insert in do does except if the assessment_name (PK) already exist in the database it will replace it with the new record
                        #(data_only_std_Name_ID [j,1], assessments_order [i], courseName, row[i], unconverted_mark, lost_mark))
                        (data_only_std_Name_ID [j,1], assessments_order [i], courseName, round(row[i], 1), round(unconverted_mark, 1), round(lost_mark, 1)))
                    con.commit() # apply changes
                j=j+1
            #END OF here in this small block, i store students mark, and assessment name into the student_grade table





        except sql.Error as e: # if error
                    # then display the error in 'database_error.html' page
                    return render_template('database_error.html', error=e)

        finally:
                    con.close() # close the connection

        #EDN OF here i want to insert students name & id into the current_student table from the uploaded csv file
        #7878787878






        #return render_template('temp.html', all_data_without_std_Name_ID=all_data_without_std_Name_ID, data_only_std_Name_ID=data_only_std_Name_ID )

        #######################################################################################################################################

        if ML_algorithms_name_binary=="RF": #form the radio button

            #first to check if there is model already created for this course based on how many columns in the uploaded csv file
            if exists(picklename+"_RF_Multiclass_model_"+ str(columns-2)+".pkl" and picklename+"_RF_Binary_model_"+ str(columns-2)+".pkl"): #pridict for the RF multiclass





                #to perform prediction using the binary models
                with open(picklename+"_RF_Binary_model_"+ str(columns-2)+".pkl", "rb") as f:
                    model = pickle.load(f)

                prediction_binary = model.predict(all_data_without_std_Name_ID)
                output_binary=prediction_binary

                ML_used_binary="LR" # to check if the code ise right or not make sure which ml result is


                #return render_template('predict_csv.html',ML_used_binary=ML_used_binary, cityList=cityList , prediction_text_binary =output_binary, prediction_text_multiclass=output_multiclass, data_only_std_Name_ID = data_only_std_Name_ID )



            #here i want to check if there are models but user enter features more than created model. for example: try to predict with 4 features in 2 features created model
            elif exists(picklename+"_RF_Multiclass_model_1.pkl" and picklename+"_RF_Binary_model_1.pkl"):  #pridict for the RF Binary
                 return render_template('sorry_features_more_than_created_models.html', length_all_assessments_in_selected_course= (length_all_assessments_in_selected_course-1))



            else:
                return render_template('sorry_no_model_has_been_created_for_this_course.html')

            #111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111

        elif ML_algorithms_name_binary=="SVM":
            if exists(picklename+"_SVM_Multiclass_model_"+ str(columns-2)+".pkl" and picklename+"_SVM_Binary_model_"+ str(columns-2)+".pkl"):


                #to perform prediction using the binary models
                with open(picklename+"_SVM_Binary_model_"+ str(columns-2)+".pkl", "rb") as f:
                    model = pickle.load(f)

                prediction_binary = model.predict(all_data_without_std_Name_ID)
                output_binary=prediction_binary

                ML_used_binary="SVM"
                #return render_template('predict_csv.html',cityList=cityList ,prediction_text_binary=output_binary, prediction_text_multiclass=output_multiclass )
                #return render_template('predict_csv.html', ML_used_binary=ML_used_binary, cityList=cityList , prediction_text_binary =output_binary, prediction_text_multiclass=output_multiclass, data_only_std_Name_ID = data_only_std_Name_ID )

            else:
                return render_template('sorry_no_model_has_been_created_for_this_course.html')

            #11111111111111111111111111111111111111111111111111111111111111111111111111111111111111

        elif ML_algorithms_name_binary=="KNN":
            if exists(picklename+"_KNN_Multiclass_model_"+ str(columns-2)+".pkl" and picklename+"_KNN_Binary_model_"+ str(columns-2)+".pkl"):



                #to perform prediction using the binary models
                with open(picklename+"_KNN_Binary_model_"+ str(columns-2)+".pkl", "rb") as f:
                    model = pickle.load(f)

                prediction_binary = model.predict(all_data_without_std_Name_ID)
                output_binary=prediction_binary

                ML_used_binary="KNN"

                #return render_template('predict_csv.html', ML_used_binary=ML_used_binary, cityList=cityList , prediction_text_binary =output_binary, prediction_text_multiclass=output_multiclass, data_only_std_Name_ID = data_only_std_Name_ID )



            #here i want to check if there are models but user enter features more than created model. for example: try to predict with 4 features in 2 features created model
            elif exists(picklename+"_KNN_Multiclass_model_1.pkl" and picklename+"_KNN_Binary_model_1.pkl"):
                 return render_template('sorry_features_more_than_created_models.html', length_all_assessments_in_selected_course= (length_all_assessments_in_selected_course-1))



            else:
                return render_template('sorry_no_model_has_been_created_for_this_course.html')

            #11111111111111111111111111111111111111111111111

        elif ML_algorithms_name_binary=="NB":
            if exists(picklename+"_NB_Multiclass_model_"+ str(columns-2)+".pkl" and picklename+"_NB_Binary_model_"+ str(columns-2)+".pkl"):




                #to perform prediction using the binary models
                with open(picklename+"_NB_Binary_model_"+ str(columns-2)+".pkl", "rb") as f:
                    model = pickle.load(f)

                # here i want to fix the proplem of NB prediction which is : numpy.core._exceptions.UFuncTypeError: ufunc 'subtract' did not contain a loop with signature matching types (dtype('<U32'), dtype('<U32')) -> dtype('<U32')
                    # what i have done to solve the problem is: i conver its type from string to float
                all_data_without_std_Name_ID_NB = all_data_without_std_Name_ID.astype(np.float)

                prediction_multiclass = model.predict(all_data_without_std_Name_ID_NB)
                output_binary = prediction_multiclass

                ML_used_binary="NB"
                #return render_template('predict_csv.html',cityList=cityList ,prediction_text_binary=output_binary, prediction_text_multiclass=output_multiclass )
                #return render_template('predict_csv.html',ML_used=ML_used, cityList=cityList , prediction_text_binary =output_binary, prediction_text_multiclass=output_multiclass, data_only_std_Name_ID = data_only_std_Name_ID )



            #here i want to check if there are models but user enter features more than created model. for example: try to predict with 4 features in 2 features created model
            elif exists(picklename+"_NB_Multiclass_model_1.pkl" and picklename+"_NB_Binary_model_1.pkl"):
                 return render_template('sorry_features_more_than_created_models.html', length_all_assessments_in_selected_course= (length_all_assessments_in_selected_course-1))

            else:
                return render_template('sorry_no_model_has_been_created_for_this_course.html')

            #11111111111111111111111111111111111111111111111

        elif ML_algorithms_name_binary=="DT":
            if exists(picklename+"_DT_Multiclass_model_"+ str(columns-2)+".pkl" and picklename+"_DT_Binary_model_"+ str(columns-2)+".pkl"):



                #to perform prediction using the binary models
                with open(picklename+"_DT_Binary_model_"+ str(columns-2)+".pkl", "rb") as f:
                    model = pickle.load(f)

                prediction_binary = model.predict(all_data_without_std_Name_ID)
                output_binary=prediction_binary

                ML_used_binary="DT"
                #return render_template('predict_csv.html',cityList=cityList ,prediction_text_binary=output_binary, prediction_text_multiclass=output_multiclass )
                #return render_template('predict_csv.html',ML_used=ML_used, cityList=cityList , prediction_text_binary =output_binary, prediction_text_multiclass=output_multiclass, data_only_std_Name_ID = data_only_std_Name_ID )



            #here i want to check if there are models but user enter features more than created model. for example: try to predict with 4 features in 2 features created model
            elif exists(picklename+"_DT_Multiclass_model_1.pkl" and picklename+"_DT_Binary_model_1.pkl"):
                 return render_template('sorry_features_more_than_created_models.html', length_all_assessments_in_selected_course= (length_all_assessments_in_selected_course-1))

            else:
                return render_template('sorry_no_model_has_been_created_for_this_course.html')




    #8888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888


    # here i want to choose the best model for the multiclass classification

        if ML_algorithms_name_multiclass=="RF": #form the radio button

            #first to check if there is model already created for this course based on how many columns in the uploaded csv file
            if exists(picklename+"_RF_Multiclass_model_"+ str(columns-2)+".pkl" and picklename+"_RF_Binary_model_"+ str(columns-2)+".pkl"): #pridict for the RF multiclass

                #to perform prediction using the multiclass models
                with open(picklename+"_RF_Multiclass_model_"+ str(columns-2)+".pkl", "rb") as f:
                    model = pickle.load(f)



                prediction_multiclass = model.predict(all_data_without_std_Name_ID) # predict for the whole data [everything in the csv file] # so the prediction_multiclass is list type because it predicts for the whole data in the csv
                output_multiclass = prediction_multiclass # store prediction result for the _RF_Multiclass_model_(how many column in the csv file)



                ML_used_multiclass="LR" # to check if the code ise right or not make sure which ml result is

                #9876543210
                #in this block, i store the results of prediction into student_prediction_results table
                csv_file_raw_length = len(data_only_std_Name_ID)
                data_only_std_Name_ID= np.array(data_only_std_Name_ID)


                #to get from the uploaded csv file to know this prediction after which assessment
                length_column_in_csvfile_assessments_grade=len(all_data_without_std_Name_ID[0])
                length_column_in_csvfile_assessments_grade=int(length_column_in_csvfile_assessments_grade)
                #return render_template('empty1.html', all_data_without_std_Name_ID = length_column_in_csvfile_assessments_grade)

                try:
                    con = sql.connect(host="pythonanywhere_host", user="pythonanywhere_user", password="pythonanywhere_password", database="pythonanywhere$database_name") #this is not the real connections details
                    c =  con.cursor() # cursor
                    # insert data # REPLACE INTO: do as insert in do does except if the assessment_name (PK) already exist in the database it will replace it with the new record

                    #to get assessment name order form assessment table
                    value = courseName
                    query4 = "SELECT assessment_name FROM assessment WHERE course_course_id = %s  order by auto_increment"
                    c.execute(query4,(value,))

                    #assessments_order = c.fetchall()
                    assessments_order = [ r[0] for r in c.fetchall() if str(r[0]) ]

                    #End of to get assessment name order form assessment table

                    for i in range(csv_file_raw_length):
                        c.execute("REPLACE INTO student_prediction_results (student_id, course_id, assessment_name, Binary_prediction_results, Multiclass_prediction_results, number_of_assessment_in_prediction) VALUES (%s,%s,%s,%s,%s, %s)", # REPLACE INTO: do as insert in do does except if the assessment_name (PK) already exist in the database it will replace it with the new record
                              (str(data_only_std_Name_ID[i,1]), courseName, str(assessments_order[length_column_in_csvfile_assessments_grade-1]), str(output_binary[i]), output_multiclass[i], length_column_in_csvfile_assessments_grade))
                        con.commit() # apply changes




                    #return render_template('empty1.html', all_data_without_std_Name_ID = assessments_order[length_column_in_csvfile_assessments_grade-1])

                except sql.Error as e: # if error
                        # then display the error in 'database_error.html' page
                        return render_template('database_error.html', error=e)

                finally:
                        con.close() # close the connection



                #Edn of in this block, i store the results of prediction into student_prediction_results table
                #9876543210



                return render_template('predict_csv.html', ML_used_multiclass = ML_used_multiclass, ML_used_binary = ML_used_binary, cityList=cityList , prediction_text_binary =output_binary, prediction_text_multiclass=output_multiclass, data_only_std_Name_ID = data_only_std_Name_ID )



            #here i want to check if there are models but user enter features more than created model. for example: try to predict with 4 features in 2 features created model
            elif exists(picklename+"_RF_Multiclass_model_1.pkl" and picklename+"_RF_Binary_model_1.pkl"):  #pridict for the RF Binary
                 return render_template('sorry_features_more_than_created_models.html', length_all_assessments_in_selected_course= (length_all_assessments_in_selected_course-1))



            else:
                return render_template('sorry_no_model_has_been_created_for_this_course.html')

            #111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111

        elif ML_algorithms_name_multiclass =="SVM":
            if exists(picklename+"_SVM_Multiclass_model_"+ str(columns-2)+".pkl" and picklename+"_SVM_Binary_model_"+ str(columns-2)+".pkl"):

                #to perform prediction using the multiclass models
                with open(picklename+"_SVM_Multiclass_model_"+ str(columns-2)+".pkl", "rb") as f:
                    model = pickle.load(f)

                prediction_multiclass = model.predict(all_data_without_std_Name_ID)
                output_multiclass = prediction_multiclass



                ML_used_multiclass="SVM"

                #9876543210
                #in this block, i store the results of prediction into student_prediction_results table
                csv_file_raw_length = len(data_only_std_Name_ID)
                data_only_std_Name_ID= np.array(data_only_std_Name_ID)


                #to get from the uploaded csv file to know this prediction after which assessment
                length_column_in_csvfile_assessments_grade=len(all_data_without_std_Name_ID[0])
                length_column_in_csvfile_assessments_grade=int(length_column_in_csvfile_assessments_grade)
                #return render_template('empty1.html', all_data_without_std_Name_ID = length_column_in_csvfile_assessments_grade)

                try:
                    con = sql.connect(host="pythonanywhere_host", user="pythonanywhere_user", password="pythonanywhere_password", database="pythonanywhere$database_name") #this is not the real connections details
                    c =  con.cursor() # cursor
                    # insert data # REPLACE INTO: do as insert in do does except if the assessment_name (PK) already exist in the database it will replace it with the new record

                    #to get assessment name order form assessment table
                    value = courseName
                    query4 = "SELECT assessment_name FROM assessment WHERE course_course_id = %s  order by auto_increment"
                    c.execute(query4,(value,))

                    #assessments_order = c.fetchall()
                    assessments_order = [ r[0] for r in c.fetchall() if str(r[0]) ]

                    #End of to get assessment name order form assessment table

                    for i in range(csv_file_raw_length):
                        c.execute("REPLACE INTO student_prediction_results (student_id, course_id, assessment_name, Binary_prediction_results, Multiclass_prediction_results, number_of_assessment_in_prediction) VALUES (%s,%s,%s,%s,%s, %s)", # REPLACE INTO: do as insert in do does except if the assessment_name (PK) already exist in the database it will replace it with the new record
                              (str(data_only_std_Name_ID[i,1]), courseName, str(assessments_order[length_column_in_csvfile_assessments_grade-1]), str(output_binary[i]), output_multiclass[i], length_column_in_csvfile_assessments_grade))
                        con.commit() # apply changes




                    #return render_template('empty1.html', all_data_without_std_Name_ID = assessments_order[length_column_in_csvfile_assessments_grade-1])

                except sql.Error as e: # if error
                        # then display the error in 'database_error.html' page
                        return render_template('database_error.html', error=e)

                finally:
                        con.close() # close the connection



                #Edn of in this block, i store the results of prediction into student_prediction_results table
                #9876543210


                return render_template('predict_csv.html', ML_used_multiclass = ML_used_multiclass, ML_used_binary = ML_used_binary, cityList=cityList , prediction_text_binary =output_binary, prediction_text_multiclass=output_multiclass, data_only_std_Name_ID = data_only_std_Name_ID )




            else:
                return render_template('sorry_no_model_has_been_created_for_this_course.html')

            #11111111111111111111111111111111111111111111111111111111111111111111111111111111111111

        elif ML_algorithms_name_multiclass=="KNN":
            if exists(picklename+"_KNN_Multiclass_model_"+ str(columns-2)+".pkl" and picklename+"_KNN_Binary_model_"+ str(columns-2)+".pkl"):

                #to perform prediction using the multiclass models
                with open(picklename+"_KNN_Multiclass_model_"+ str(columns-2)+".pkl", "rb") as f:
                    model = pickle.load(f)

                prediction_multiclass = model.predict(all_data_without_std_Name_ID)
                output_multiclass = prediction_multiclass


                ML_used_multiclass="KNN"

                #9876543210
                #in this block, i store the results of prediction into student_prediction_results table
                csv_file_raw_length = len(data_only_std_Name_ID)
                data_only_std_Name_ID= np.array(data_only_std_Name_ID)


                #to get from the uploaded csv file to know this prediction after which assessment
                length_column_in_csvfile_assessments_grade=len(all_data_without_std_Name_ID[0])
                length_column_in_csvfile_assessments_grade=int(length_column_in_csvfile_assessments_grade)
                #return render_template('empty1.html', all_data_without_std_Name_ID = length_column_in_csvfile_assessments_grade)

                try:
                    con = sql.connect(host="pythonanywhere_host", user="pythonanywhere_user", password="pythonanywhere_password", database="pythonanywhere$database_name") #this is not the real connections details
                    c =  con.cursor() # cursor
                    # insert data # REPLACE INTO: do as insert in do does except if the assessment_name (PK) already exist in the database it will replace it with the new record

                    #to get assessment name order form assessment table
                    value = courseName
                    query4 = "SELECT assessment_name FROM assessment WHERE course_course_id = %s  order by auto_increment"
                    c.execute(query4,(value,))

                    #assessments_order = c.fetchall()
                    assessments_order = [ r[0] for r in c.fetchall() if str(r[0]) ]

                    #End of to get assessment name order form assessment table

                    for i in range(csv_file_raw_length):
                        c.execute("REPLACE INTO student_prediction_results (student_id, course_id, assessment_name, Binary_prediction_results, Multiclass_prediction_results, number_of_assessment_in_prediction) VALUES (%s,%s,%s,%s,%s, %s)", # REPLACE INTO: do as insert in do does except if the assessment_name (PK) already exist in the database it will replace it with the new record
                              (str(data_only_std_Name_ID[i,1]), courseName, str(assessments_order[length_column_in_csvfile_assessments_grade-1]), str(output_binary[i]), output_multiclass[i], length_column_in_csvfile_assessments_grade))
                        con.commit() # apply changes




                    #return render_template('empty1.html', all_data_without_std_Name_ID = assessments_order[length_column_in_csvfile_assessments_grade-1])

                except sql.Error as e: # if error
                        # then display the error in 'database_error.html' page
                        return render_template('database_error.html', error=e)

                finally:
                        con.close() # close the connection



                #Edn of in this block, i store the results of prediction into student_prediction_results table
                #9876543210


                return render_template('predict_csv.html', ML_used_multiclass = ML_used_multiclass, ML_used_binary = ML_used_binary, cityList=cityList , prediction_text_binary =output_binary, prediction_text_multiclass=output_multiclass, data_only_std_Name_ID = data_only_std_Name_ID )




            #here i want to check if there are models but user enter features more than created model. for example: try to predict with 4 features in 2 features created model
            elif exists(picklename+"_KNN_Multiclass_model_1.pkl" and picklename+"_KNN_Binary_model_1.pkl"):
                 return render_template('sorry_features_more_than_created_models.html', length_all_assessments_in_selected_course= (length_all_assessments_in_selected_course-1))



            else:
                return render_template('sorry_no_model_has_been_created_for_this_course.html')

            #11111111111111111111111111111111111111111111111

        elif ML_algorithms_name_multiclass=="NB":
            if exists(picklename+"_NB_Multiclass_model_"+ str(columns-2)+".pkl" and picklename+"_NB_Binary_model_"+ str(columns-2)+".pkl"):

                #to perform prediction using the multiclass models
                with open(picklename+"_NB_Multiclass_model_"+ str(columns-2)+".pkl", "rb") as f:
                    model = pickle.load(f)

                # here i want to fix the proplem of NB prediction which is : numpy.core._exceptions.UFuncTypeError: ufunc 'subtract' did not contain a loop with signature matching types (dtype('<U32'), dtype('<U32')) -> dtype('<U32')
                    # what i have done to solve the problem is: i conver its type from string to float
                all_data_without_std_Name_ID_NB = all_data_without_std_Name_ID.astype(np.float)

                prediction_multiclass = model.predict(all_data_without_std_Name_ID_NB)
                output_multiclass = prediction_multiclass


                ML_used_multiclass="NB"

                #9876543210
                #in this block, i store the results of prediction into student_prediction_results table
                csv_file_raw_length = len(data_only_std_Name_ID)
                data_only_std_Name_ID= np.array(data_only_std_Name_ID)


                #to get from the uploaded csv file to know this prediction after which assessment
                length_column_in_csvfile_assessments_grade=len(all_data_without_std_Name_ID[0])
                length_column_in_csvfile_assessments_grade=int(length_column_in_csvfile_assessments_grade)
                #return render_template('empty1.html', all_data_without_std_Name_ID = length_column_in_csvfile_assessments_grade)

                try:
                    con = sql.connect(host="pythonanywhere_host", user="pythonanywhere_user", password="pythonanywhere_password", database="pythonanywhere$database_name") #this is not the real connections details
                    c =  con.cursor() # cursor
                    # insert data # REPLACE INTO: do as insert in do does except if the assessment_name (PK) already exist in the database it will replace it with the new record

                    #to get assessment name order form assessment table
                    value = courseName
                    query4 = "SELECT assessment_name FROM assessment WHERE course_course_id = %s  order by auto_increment"
                    c.execute(query4,(value,))

                    #assessments_order = c.fetchall()
                    assessments_order = [ r[0] for r in c.fetchall() if str(r[0]) ]

                    #End of to get assessment name order form assessment table

                    for i in range(csv_file_raw_length):
                        c.execute("REPLACE INTO student_prediction_results (student_id, course_id, assessment_name, Binary_prediction_results, Multiclass_prediction_results, number_of_assessment_in_prediction) VALUES (%s,%s,%s,%s,%s, %s)", # REPLACE INTO: do as insert in do does except if the assessment_name (PK) already exist in the database it will replace it with the new record
                              (str(data_only_std_Name_ID[i,1]), courseName, str(assessments_order[length_column_in_csvfile_assessments_grade-1]), str(output_binary[i]), output_multiclass[i], length_column_in_csvfile_assessments_grade))
                        con.commit() # apply changes




                    #return render_template('empty1.html', all_data_without_std_Name_ID = assessments_order[length_column_in_csvfile_assessments_grade-1])

                except sql.Error as e: # if error
                        # then display the error in 'database_error.html' page
                        return render_template('database_error.html', error=e)

                finally:
                        con.close() # close the connection



                #Edn of in this block, i store the results of prediction into student_prediction_results table
                #9876543210


                return render_template('predict_csv.html', ML_used_multiclass = ML_used_multiclass, ML_used_binary = ML_used_binary, cityList=cityList , prediction_text_binary = output_binary, prediction_text_multiclass=output_multiclass, data_only_std_Name_ID = data_only_std_Name_ID )





            #here i want to check if there are models but user enter features more than created model. for example: try to predict with 4 features in 2 features created model
            elif exists(picklename+"_NB_Multiclass_model_1.pkl" and picklename+"_NB_Binary_model_1.pkl"):
                 return render_template('sorry_features_more_than_created_models.html', length_all_assessments_in_selected_course= (length_all_assessments_in_selected_course-1))

            else:
                return render_template('sorry_no_model_has_been_created_for_this_course.html')

            #11111111111111111111111111111111111111111111111

        elif ML_algorithms_name_multiclass =="DT":
            if exists(picklename+"_DT_Multiclass_model_"+ str(columns-2)+".pkl" and picklename+"_DT_Binary_model_"+ str(columns-2)+".pkl"):

                #to perform prediction using the multiclass models
                with open(picklename+"_DT_Multiclass_model_"+ str(columns-2)+".pkl", "rb") as f:
                    model = pickle.load(f)

                prediction_multiclass = model.predict(all_data_without_std_Name_ID)
                output_multiclass = prediction_multiclass



                ML_used_multiclass="DT"

                #9876543210
                #in this block, i store the results of prediction into student_prediction_results table
                csv_file_raw_length = len(data_only_std_Name_ID)
                data_only_std_Name_ID= np.array(data_only_std_Name_ID)


                #to get from the uploaded csv file to know this prediction after which assessment
                length_column_in_csvfile_assessments_grade=len(all_data_without_std_Name_ID[0])
                length_column_in_csvfile_assessments_grade=int(length_column_in_csvfile_assessments_grade)
                #return render_template('empty1.html', all_data_without_std_Name_ID = length_column_in_csvfile_assessments_grade)

                try:
                    con = sql.connect(host="pythonanywhere_host", user="pythonanywhere_user", password="pythonanywhere_password", database="pythonanywhere$database_name") #this is not the real connections details
                    c =  con.cursor() # cursor
                    # insert data # REPLACE INTO: do as insert in do does except if the assessment_name (PK) already exist in the database it will replace it with the new record

                    #to get assessment name order form assessment table
                    value = courseName
                    query4 = "SELECT assessment_name FROM assessment WHERE course_course_id = %s  order by auto_increment"
                    c.execute(query4,(value,))

                    #assessments_order = c.fetchall()
                    assessments_order = [ r[0] for r in c.fetchall() if str(r[0]) ]

                    #End of to get assessment name order form assessment table

                    for i in range(csv_file_raw_length):
                        c.execute("REPLACE INTO student_prediction_results (student_id, course_id, assessment_name, Binary_prediction_results, Multiclass_prediction_results, number_of_assessment_in_prediction) VALUES (%s,%s,%s,%s,%s, %s)", # REPLACE INTO: do as insert in do does except if the assessment_name (PK) already exist in the database it will replace it with the new record
                              (str(data_only_std_Name_ID[i,1]), courseName, str(assessments_order[length_column_in_csvfile_assessments_grade-1]), str(output_binary[i]), output_multiclass[i], length_column_in_csvfile_assessments_grade))
                        con.commit() # apply changes




                    #return render_template('empty1.html', all_data_without_std_Name_ID = assessments_order[length_column_in_csvfile_assessments_grade-1])

                except sql.Error as e: # if error
                        # then display the error in 'database_error.html' page
                        return render_template('database_error.html', error=e)

                finally:
                        con.close() # close the connection



                #Edn of in this block, i store the results of prediction into student_prediction_results table
                #9876543210


                #return render_template('predict_csv.html',cityList=cityList ,prediction_text_binary=output_binary, prediction_text_multiclass=output_multiclass )
                return render_template('predict_csv.html', ML_used_multiclass = ML_used_multiclass, ML_used_binary = ML_used_binary, cityList=cityList , prediction_text_binary =output_binary, prediction_text_multiclass=output_multiclass, data_only_std_Name_ID = data_only_std_Name_ID )



            #here i want to check if there are models but user enter features more than created model. for example: try to predict with 4 features in 2 features created model
            elif exists(picklename+"_DT_Multiclass_model_1.pkl" and picklename+"_DT_Binary_model_1.pkl"):
                 return render_template('sorry_features_more_than_created_models.html', length_all_assessments_in_selected_course= (length_all_assessments_in_selected_course-1))

            else:
                return render_template('sorry_no_model_has_been_created_for_this_course.html')


    else:
        return render_template('sorry_no_file_selected_in_prediction_csv.html') # i solved this issue by making the input file required
        #return 'No selected file'


##############################################################################################
###################################### END OF Prediction for predict_csv  ####################
##############################################################################################

#NNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNN




#SSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSS
#update_existing_model.py

##############################################################################################
###################################### upload csv ############################################################
##################################################################################################

#upload or add more data from csv to exisiting course
#this is copy and pased from the upload_file.py because in updating existing model, i make users to upload data then update existing model
@app.route('/update_existing_model_uploadNewData', methods=['GET','POST']) #upload or add more data from csv to exisiting course
@login_required
def update_existing_model_uploadNewData():
  if request.method == 'GET':
    try:
        con = sql.connect(host="pythonanywhere_host", user="pythonanywhere_user", password="pythonanywhere_password", database="pythonanywhere$database_name") #this is not the real connections details
        c =  con.cursor() # cursor
        query = "Select * from course_and_models where userName=%s"
        values = session["USERNAME"]
        cityList = c.execute(query, (values,))
        cityList = c.fetchall()

        return render_template('update_existing_model_uploadNewData.html', cityList=cityList)

    except sql.Error as e: # if error
            # then display the error in 'database_error.html' page
            return render_template('database_error.html', error=e)

    finally:
        con.close() # close the connection

  else:
      if request.method == 'POST':

        course_course_id = request.form['course_course_id']
        #conversion_radio_btn = request.form['conversion'] # from the conversion radio button

        try:
            con = sql.connect(host="pythonanywhere_host", user="pythonanywhere_user", password="pythonanywhere_password", database="pythonanywhere$database_name") #this is not the real connections details
            c =  con.cursor() # cursor

        #to get how many assessment in the selected course, so that we can match the uploaded csv file column with number of assessment
            query_assessment_name= "SELECT assessment_name  FROM assessment where course_course_id=%s"
            values = course_course_id
            assessment_name= c.execute(query_assessment_name, (values,))
            assessment_name = c.fetchall()
            #assessment_name_length = len(assessment_name[0])
            assessment_name_length = len(assessment_name)

            #here i want to know how many record were there before the user insert more dataset
            #here i want to tel users how many record inserted into the database by cheching length of students table for the selected course
            length_of_addedd_data_before=0
            length_of_addedd_data=0

            query_length_of_addedd_data= "Select * from student where course_course_id=%s"
            values = course_course_id
            length_of_addedd_data= c.execute(query_length_of_addedd_data, (values,))
            length_of_addedd_data = c.fetchall()
            length_of_addedd_data_before = len(length_of_addedd_data) #before
            # EDN OF (here i want to tel users how many record inserted into the database by cheching length of students table for the selected course)


            #here i want to read the uploaded csv file
            csv_file = request.files['file'] #from the html file input name

            # this helps me to validate if the uploaded file is a csv extention
            file_ext = os.path.splitext(request.files['file'].filename)[1]
            #return render_template('no_dashboard_yet.html', data = file_ext)
            if file_ext not in app.config['UPLOAD_EXTENSIONS']:
                return render_template('no_dashboard_yet.html', data = "please make sure to upload a csv file")
            # END OF this helps me to validate if the uploaded file is a csv extention


            csv_file = TextIOWrapper(csv_file, encoding='utf-8')
            csv_reader = csv.reader(csv_file, delimiter=',')
            next(csv_reader) #skip the first row (title such as practical test 1)
            data = [row for row in csv_reader] #read all ceel in the csv file and put it in the data [array]


            # to check file is not empty
            if len(data) == 0:
                return render_template('empty.html')

            #........................................................................................................................
            #here i want to do Rukshan comments about making the first row in CSV file the weight [mark of]
            mark_out_CSV_array = np.array(data)
            #ttype=type(my_array) #temppp
            mark_out_CSV= mark_out_CSV_array[0,:]
            assessment_waitage=mark_out_CSV_array[1,:]

            data = np.array(data)
            data= data [2:, :]
            data=data.tolist()
            #return render_template('empty3.html', data = data)

            #.......................................................................................................................



            #this query i will use it later to insert data from [data] array into the assessment_std Table in the database
            query =  "INSERT INTO assessment_std (assessment_course_course_id,mark, assessment_assessment_name, student_student_id) VALUES (%s,%s,%s, %s)"

            if len(data) == 0:
                return render_template('empty.html')

            else:


             for row in data: #this is the first loop that loops as long as the csv file row [instances]

                if len(row)>(assessment_name_length+2): # this is to check if csv file feature has more feature than course's assessment s
                    return render_template('too_big_csv_file.html')    # if csv file has feature more than number of assessments in the database

                elif  len(row)<(assessment_name_length+2):
                    return render_template('too_small_csv_file.html')    # if csv file has feature less than number of assessments in the database

                #[so the right number of csv file columns must be equal to the number of assessments for the selected course + total + grade. then i will generate columns:passorfail and multiclassLevel]
                else:# if csv file has feature exactly same as the number of assessments in the database

                    if row[assessment_name_length]=="": #if the is null in the assessment make it 0
                           row[assessment_name_length]=0

                    try:# i used try and except ValueError, to solve if data in the csv file is not nubmber such as jkhkjnh

                        row[assessment_name_length]=float(row[assessment_name_length]) #i used float because when using int any float number return it 0, so i had to use float

                    except ValueError: # if the cell has strange string such as (jklnlj) in the assessments grade, it will make it 0
                        row[assessment_name_length] = 0

                    if row[assessment_name_length]!="" : #this to make sure it read data based on the total in the csv. if there is no total it stop reading and inserting data to DB

                        #generate pass_or_fail value from total if total >=50 pass, else fail
                        if int(row[assessment_name_length])>=50:
                            pass_or_fail =1
                        else:
                            pass_or_fail=0

                        #generate multiclass_levels value from total if total >55 pass, elif total<45 at_risk, else fail
                        if int(row[assessment_name_length])>55:
                            multiclass_levels ="pass"

                        elif int(row[assessment_name_length])<45:
                            multiclass_levels ="at_risk"
                        else:
                            multiclass_levels="borderline"


                        #query2: to insert data into the student Table in the database
                        query2 = "INSERT INTO student (course_course_id, total, grade, pass_or_fail, multiclass_levels) VALUES (%s, %s, %s, %s, %s)"
                        value = (course_course_id, row[assessment_name_length], row[assessment_name_length+1], pass_or_fail, multiclass_levels)
                        c.execute(query2,(value))
                        con.commit() # apply changes


                        for i in range(assessment_name_length): #this is the second loop that loops as long as the csv file coloumns [features] to fill each assessment in the selected course

                            #444444444444444444444444444444444444
                            #here i want to make sure to match students_id btn student and assessments_Std tables
                            con = sql.connect(host="pythonanywhere_host", user="pythonanywhere_user", password="pythonanywhere_password", database="pythonanywhere$database_name") #this is not the real connections details
                            c = con.cursor() # cursor
                            c = con.cursor(buffered=True)

                            student_id = c.execute("Select student_id from student order by student_id")

                            student_id = [ r[0] for r in c.fetchall() if str(r[0]) ] # i used this to return fetch the data without (). I also used str(row[0]) to make sure it does not miss any int 0


                            last_student_id = student_id[-1] #student_id[-1] get the last student id in the student table, so i can overcome the isse of foriegn key constranit [CASCADE]
                           #444444444444444444444444444444444444

                            #student_id = c.execute("Select student_id from student ")
                            #student_id = [ r[0] for r in c.fetchall() if str(r[0]) ] # i used this to return fetch the data without (). I also used str(row[0]) to make sure it does not miss any int 0

                            #last_student_id = student_id[-1] #student_id[-1] get the last student id in the student table, so i can overcome the isse of foriegn key constranit [CASCADE]
                            #3333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333
                            #here I fixed the problem of inserting without considering the order of assessments
                            value = course_course_id
                            query4 = "SELECT assessment_name FROM assessment WHERE course_course_id = %s  order by auto_increment"
                            c.execute(query4,(value,))

                            assessments_order = c.fetchall()

                            assessment_name_to_string = ",".join(assessments_order [i]) #to solve error "python mysqlconnector mysqlinterfaceerror python type tuple cannot be converted"
                            #3333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333

                            #assessment_name_to_string = ",".join(assessment_name[i]) #to solve error "python mysqlconnector mysqlinterfaceerror python type tuple cannot be converted"

                            if row[i]=="": #if the is null in the assessment make it 0
                                row[i]=0

                            try:# iused try and except ValueError, to solve if data in the csv file is not nubmber such as jkhkjnh

                                row[i]=float(row[i]) #i used float because when using int any float number return it 0, so i had to use float

                                #if conversion_radio_btn=="Yes": # here i did the if because i want to check if the user want to convert the data in the csv file or not
                                #here in this block, I tried to convert students marks into a Percentages as Simon suggested useing mark_out and mark_worth
                                #66666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666
                                query5 = "SELECT mark_out FROM assessment where course_course_id=%s and assessment_name =%s"

                                query6 = "SELECT mark_worth FROM assessment where course_course_id=%s and assessment_name =%s"

                                c.execute(query5,(course_course_id,assessment_name_to_string,))
                                mark_out = [ r[0] for r in c.fetchall() if str(r[0]) ]

                                c.execute(query6,(course_course_id,assessment_name_to_string,))
                                mark_worth = [ r[0] for r in c.fetchall() if str(r[0]) ]

                                mark_out = np.array(mark_out)
                                mark_worth = np.array(mark_worth)


                                if mark_out_CSV[i] !="0" and assessment_waitage[i] !="0":

                                    row[i] = float(row[i]) / int(mark_out_CSV[i]) * int(assessment_waitage[i])

                                    row[i] = float(row[i]) / int(assessment_waitage[i]) * 100 # this is the conversion based on Rukshan comments which is the marked out is from the first row in the csv
                                else:     #here the value of mark_out_CSV[i]==0 which means the user did not add correct value for the wieght in the csv file or the value was 0
                                    #row[i] = int(row[i])
                                    row[i] = float(row[i]) / int(mark_out) * int(mark_worth)
                                    #row[i] = float(row[i]) / int(mark_worth) * int(mark_out)
                                    row[i] = float(row[i]) / int(mark_worth) * 100

                                #elif conversion_radio_btn=="No":
                                #    row[i] = row[i]

                                #66666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666


                                #query: is the one i did before the first for loop #this query i will use it later to insert data from [data] array into the assessment_std Table in the database
                                #this one query =  "INSERT INTO assessment_std (assessment_course_course_id,mark, assessment_assessment_name, student_student_id) VALUES (%s,%s,%s, %s)"
                                c.execute(query,(course_course_id, row[i], assessment_name_to_string , last_student_id, )) #last_student_id: student_id[-1] get the last student id in the student table
                                con.commit() # apply changes

                            except ValueError: # if the cell has strange string such as (jklnlj) in the assessments grade, it will make it 0
                                row[i] = 0
                                c.execute(query,(course_course_id, row[i], assessment_name_to_string , last_student_id, )) #student_id[-1] get the last student id in the student table
                                con.commit() # apply changes


            #here i want to know how many record were there before the user insert more dataset
            #here i want to tel users how many record inserted into the database by cheching length of students table for the selected course
            query_length_of_addedd_data= "Select * from student where course_course_id=%s"
            values = course_course_id
            length_of_addedd_data= c.execute(query_length_of_addedd_data, (values,))
            length_of_addedd_data = c.fetchall()
            length_of_addedd_data_after = len(length_of_addedd_data) #After

            #now i will subtract length_of_addedd_data_after by length_of_addedd_data_before to get the new added data
            length_of_addedd_data_new = length_of_addedd_data_after - length_of_addedd_data_before  # [length_of_addedd_data_new] is the new addedd data
            #new=length_of_addedd_data_after-length_of_addedd_data_before

            # EDN OF (here i want to tel users how many record inserted into the database by cheching length of students table for the selected course)

            # here in this section i just want to get course name by ussing course id fro course Table to show course name in the dropdown list in updation existing model for the selected course
            try:
                con = sql.connect(host="pythonanywhere_host", user="pythonanywhere_user", password="pythonanywhere_password", database="pythonanywhere$database_name") #this is not the real connections details
                c =  con.cursor() # cursor
                course_query= "SELECT * FROM course_and_models where course_id=%s"
                values = (course_course_id)

                cityList = c.execute(course_query, (values,))
                cityList = c.fetchall()
                #cityList = [ row[0] for row in c.fetchall() if row[0] ] # i used this to return fetch the data without ()



            except sql.Error as e: # if error
                    # then display the error in 'database_error.html' page
                    return render_template('database_error.html', error=e)

            finally:
                con.close() # close the connection

            # END OF here in this section i just want to get course name by ussing course id fro course Table to show course name in the dropdown list in updation existing model for the selected course


            #length_of_addedd_data_new=0
            return render_template('update_existing_model_updateModel.html', course_course_id = course_course_id, cityList = cityList , length_of_addedd_data_new = length_of_addedd_data_new)    # if everything went correctly, i render this html that says thankyou you upload was successful

        except sql.Error as e: # if error
            # then display the error in 'database_error.html' page
            return render_template('database_error.html', error=e)

        finally:
            con.close() # close the connection
########################################################################################################################
########################################################################################################################
########################################################################################################################
#upload exisiting models for exising course
#this is copy and pased from the createModel.py because in updating existing model, i make users to upload data then update existing model
#i also copy some from the delete course.py file to delete existing model
@app.route('/update_existing_model_updateModel', methods=['POST']) #upload exisiting models for exising course
@login_required
def update_existing_model_updateModel():


         # request.method == 'POST':
        courseName = request.form['course_course_id']
        picklename = courseName

        #444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444
        #i copy this from the delete course.py file
        #here  i wanted to delete existing pkl file to create new pkl files form create_model_function.

        try:
            con = sql.connect(host="pythonanywhere_host", user="pythonanywhere_user", password="pythonanywhere_password", database="pythonanywhere$database_name") #this is not the real connections details
            c =  con.cursor() # cursor
            c = con.cursor(buffered=True)

            ################################################################################################
            #here i want to know how many assessments in the selected course , so i can loop to delete the pkl file at the end
            #here I want to get all assessment in the selected course
            all_assessments_in_selected_course_query= "SELECT assessment_name  FROM assessment where course_course_id=%s order by auto_increment"
            values = (courseName)

            #here i want to fech all assessments from database for a specefic course [(course_id) from the function (function_create_dataset) parameter
            all_assessments_in_selected_course= c.execute(all_assessments_in_selected_course_query, (values,))
            all_assessments_in_selected_course = c.fetchall()

            # to get the length of all assessments for selected course (to know how many assessment in this course)
            length_all_assessments_in_selected_course= len(all_assessments_in_selected_course)

        except sql.Error as e: # if error
            # then display the error in 'database_error.html' page
            return render_template('database_error.html', error=e)

        finally:
            con.close() # close the connection



        ################################################################################################

        # remove all existing model
        if exists(picklename+"_RF_Multiclass_model_1.pkl" or picklename+"_RF_Multiclass_model_1.pkl" or picklename+"_KNN_Multiclass_model_1.pkl" or picklename+"_KNN_Binary_model_1.pkl" or picklename+"_SVM_Multiclass_model_1.pkl" or picklename+"_SVM_Binary_model_1.pkl" or picklename+"_NB_Multiclass_model_1.pkl" or picklename+"_NB_Binary_model_1.pkl"):
            for i in range(length_all_assessments_in_selected_course):

                #here i want delete all models for all ML algotrithms (binary and multiclass)
                os.remove(picklename+"_RF_Multiclass_model_" +  str(i+1)+".pkl")
                os.remove(picklename+"_RF_Binary_model_" +  str(i+1)+".pkl")

                os.remove(picklename+"_SVM_Multiclass_model_" +  str(i+1)+".pkl")
                os.remove(picklename+"_SVM_Binary_model_" +  str(i+1)+".pkl")

                os.remove(picklename+"_KNN_Multiclass_model_" +  str(i+1)+".pkl")
                os.remove(picklename+"_KNN_Binary_model_" +  str(i+1)+".pkl")

                os.remove(picklename+"_NB_Multiclass_model_" +  str(i+1)+".pkl")
                os.remove(picklename+"_NB_Binary_model_" +  str(i+1)+".pkl")

                os.remove(picklename+"_DT_Multiclass_model_" +  str(i+1)+".pkl")
                os.remove(picklename+"_DT_Binary_model_" +  str(i+1)+".pkl")


        con = sql.connect(host="pythonanywhere_host", user="pythonanywhere_user", password="pythonanywhere_password", database="pythonanywhere$database_name") #this is not the real connections details
        c =  con.cursor() # cursor
        c = con.cursor(buffered=True)
        #delete all data [models performance] for selected course from the course_and_models Table
        query_delete_course_and_models_data = "DELETE FROM course_and_models WHERE course_id=%s"
        value_delete_course_and_models_data = courseName
        c.execute(query_delete_course_and_models_data, (value_delete_course_and_models_data,))
        con.commit() # apply changes


        query_delete_models_performance_data = "DELETE FROM models_performance WHERE course_id=%s"
        value_delete_models_performance_data = courseName
        c.execute(query_delete_models_performance_data, (value_delete_models_performance_data,))
        con.commit() # apply changes

        #444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444




        try:

            #11111111111111111
            # to check if there is dataset for selected course or not. i will use it in the if staement that check if there is data in the database for this course or not
            con = sql.connect(host="pythonanywhere_host", user="pythonanywhere_user", password="pythonanywhere_password", database="pythonanywhere$database_name") #this is not the real connections details
            c =  con.cursor() # cursor
            c = con.cursor(buffered=True)
            #check if there are dataset for selected course by checking if there are total in student table for selected course
            check_dataset_for_selected_course_query= "SELECT total  FROM student where course_course_id=%s"
            values = (courseName)

            check_dataset_for_selected_course= c.execute(check_dataset_for_selected_course_query, (values,))
            check_dataset_for_selected_course = c.fetchall()




            #11111111111111111

            if len(check_dataset_for_selected_course) !=0: # to check if there is dataset/data in the database for this course or not. if not render template that says there is no dataset uploaded for this course


                ########################################################## here just to chec if there model already created
                if exists(picklename+"_RF_Multiclass_model_1.pkl" or picklename+"_RF_Binary_model_1.pkl"): # i used _RF_Multiclass_model_1 and _RF_Binary_model_1 because every course that already has model at least will have  a model of one feature. so i want to make sure if there is pkl files of not for the sellected course
                    return render_template('if_model_already_exist.html')




        ######################################################################################################################################################
        ######################################################################################################################################################

                else: #if there is no models (pkl) already created for this course, first call the two fuction that create dataset for you [function_create_dataset_for_Multiclass & function_create_dataset_for_Binary_model]

                    #creating the dataset for both Binary (y=pass&fail feature) and Multiclass (ThrreLevel feature)
                    x_multiclass, y_multiclass, length_of_dataset_after_cleaning_Multiclass = function_create_dataset_for_Multiclass(courseName) # create the dataset by calling the this function and return x and y

                    #return render_template('empty3.html', data = x_multiclass)

                    x_binary, y_binary, length_of_dataset_after_cleaning_Binary =function_create_dataset_for_Binary_model(courseName) # create the dataset by calling the this function and return x and y

        ######################################################################################################################################################
        ######################################################################################################################################################

                    #RF
                    #create binary models by calling this fuction
                    RF_accuracy_Binary, RF_f1_Binary, RF_recall_Binary, RF_precision_Binary,  RF_number_of_model_Binary = create_multiple_Binary_models_RF (courseName, x_binary, y_binary)

                    #create Multiclass classification models by calling this fuction
                    RF_accuracy_Multiclass, RF_f1_Multiclass, RF_recall_Multiclass, RF_precision_Multiclass,  RF_number_of_model_Multiclass = create_multiple_Multiclass_models_RF(courseName, x_multiclass, y_multiclass)

        ######################################################################################################################################################
        ######################################################################################################################################################
                    #SVM

                    #Binary
                    SVM_accuracy_Binary, SVM_f1_Binary, SVM_recall_Binary, SVM_precision_Binary,  SVM_number_of_model_Binary = create_multiple_Binary_models_SVM (courseName, x_binary, y_binary)

                    #Multiclass
                    SVM_accuracy_Multiclass, SVM_f1_Multiclass, SVM_recall_Multiclass, SVM_precision_Multiclass,  SVM_number_of_model_Multiclass = create_multiple_Multiclass_models_SVM(courseName, x_multiclass, y_multiclass)
        ######################################################################################################################################################
        ######################################################################################################################################################
                    #KNN

                    #Binary
                    KNN_accuracy_Binary, KNN_f1_Binary, KNN_recall_Binary, KNN_precision_Binary,  KNN_number_of_model_Binary = create_multiple_Binary_models_KNN (courseName, x_binary, y_binary)
                    #Multiclass
                    KNN_accuracy_Multiclass, KNN_f1_Multiclass, KNN_recall_Multiclass, KNN_precision_Multiclass,  KNN_number_of_model_Multiclass = create_multiple_Multiclass_models_KNN(courseName, x_multiclass, y_multiclass)


        ######################################################################################################################################################
        ######################################################################################################################################################

                    #NB

                    #Binary
                    NB_accuracy_Binary, NB_f1_Binary, NB_recall_Binary, NB_precision_Binary,  NB_number_of_model_Binary = create_multiple_Binary_models_NB (courseName, x_binary, y_binary)

                    #Multiclass
                    NB_accuracy_Multiclass, NB_f1_Multiclass, NB_recall_Multiclass, NB_precision_Multiclass,  NB_number_of_model_Multiclass = create_multiple_Multiclass_models_NB(courseName, x_multiclass, y_multiclass)
         ######################################################################################################################################################
        ######################################################################################################################################################

                    #DT

                    #Binary
                    DT_accuracy_Binary, DT_f1_Binary, DT_recall_Binary, DT_precision_Binary,  DT_number_of_model_Binary = create_multiple_Binary_models_DT (courseName, x_binary, y_binary)

                    #Multiclass
                    DT_accuracy_Multiclass, DT_f1_Multiclass, DT_recall_Multiclass, DT_precision_Multiclass,  DT_number_of_model_Multiclass = create_multiple_Multiclass_models_DT(courseName, x_multiclass, y_multiclass)


        ######################################################################################################################################################
        ######################################################################################################################################################
                    #in this section, I save all models performance (accuracy, f1, and recall) created in the course_and_models Table
                    #to calulate how many model been created
                    Number_of_created_model= RF_number_of_model_Multiclass*10 #10 comes from 4*2 [foure ML algorithms * two models binary and multiclass]

                    #######################################################################
                    #here I want to get all assessment in the selected course, to know how many assessments there
                    all_assessments_in_selected_course_query= "SELECT assessment_name  FROM assessment where course_course_id=%s order by auto_increment"
                    values = (courseName)

                    #here i want to fech all assessments from database for a specefic course [(course_id) from the function (function_create_dataset) parameter
                    all_assessments_in_selected_course= c.execute(all_assessments_in_selected_course_query, (values,))
                    all_assessments_in_selected_course = c.fetchall()

                    # to get the length of all assessments for selected course (to know how many assessment in this course)
                    length_all_assessments_in_selected_course= len(all_assessments_in_selected_course)


                     # here i want to first insert course_id & course_name into the course_and_models table
                    c = con.cursor(buffered=True)
                    query_course_name_from_course_table="Select course_name from course where course_id=%s"
                    value_course_name_from_course_table=(courseName)
                    #course_name_from_course_table = c.execute("Select * from course where course_id=%s", courseName)
                    course_name_from_course_table = c.execute(query_course_name_from_course_table, (value_course_name_from_course_table,))
                    #course_name_from_course_table = c.fetchall()
                    course_name_from_course_table  = [ row[0] for row in c.fetchall() if row[0] ] # i used this to return fetch the data without (). I also used str(row[0]) to make sure it does not miss any int 0
                    course_name_from_course_table=str(course_name_from_course_table[0]) # i just convert list to string in order to solve  Python type tuple cannot be converted

                    c.execute("insert INTO course_and_models (course_id, course_name, userName) VALUES (%s,%s,%s)",
                                        (courseName, course_name_from_course_table, session["USERNAME"]))
                    con.commit() # apply changes

                    # END OF (here i want to first insert course_id & course_name into the course_and_models table)


                    counter=length_all_assessments_in_selected_course # i used this counter to help me to keep the (length_all_assessments_in_selected_course) untouch during the loop
                    #insert RF Binary acc & f1 & recall & precision into the course_and_models table
                    for i in range(length_all_assessments_in_selected_course):
                        c.execute("insert INTO models_performance (course_id, Features,  ML_Algorithm, Binary_Multiclass, accuracy, f1, recall, precision_1) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)",
                                        (courseName, counter, "RF", "Binary", RF_accuracy_Binary [i], RF_f1_Binary [i],  RF_recall_Binary [i], RF_precision_Binary [i] ))
                        counter=counter-1
                        con.commit() # apply changes

                    counter=length_all_assessments_in_selected_course # i used this counter to help me to keep the (length_all_assessments_in_selected_course) untouch during the loop
                    #insert RF Multiclass acc & f1 & recall & precision into the course_and_models table
                    for i in range(length_all_assessments_in_selected_course):
                        c.execute("insert INTO models_performance (course_id, Features,  ML_Algorithm, Binary_Multiclass, accuracy, f1, recall , precision_1) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)", # REPLACE INTO: do as insert in do does except if the assessment_name (PK) already exist in the database it will replace it with the new record
                                        (courseName, counter, "RF", "Multiclass", RF_accuracy_Multiclass [i], RF_f1_Multiclass [i], RF_recall_Multiclass [i], RF_precision_Multiclass [i]  ))
                        counter=counter-1
                        con.commit() # apply changes
                    counter=length_all_assessments_in_selected_course # i used this counter to help me to keep the (length_all_assessments_in_selected_course) untouch during the loop

                    #insert SVM Binary acc & f1 & recall & precision into the course_and_models tablefor
                    for i in range(length_all_assessments_in_selected_course):
                        c.execute("insert INTO models_performance (course_id, Features,  ML_Algorithm, Binary_Multiclass, accuracy, f1, recall , precision_1) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)", # REPLACE INTO: do as insert in do does except if the assessment_name (PK) already exist in the database it will replace it with the new record
                                        (courseName, counter, "SVM", "Binary", SVM_accuracy_Binary [i], SVM_f1_Binary [i], SVM_recall_Binary [i] , SVM_precision_Binary [i] ))
                        counter=counter-1
                        con.commit() # apply changes
                    counter=length_all_assessments_in_selected_course # i used this counter to help me to keep the (length_all_assessments_in_selected_course) untouch during the loop

                    #insert SVM Multiclass acc & f1 & recall & precision into the course_and_models table
                    for i in range(length_all_assessments_in_selected_course):
                        c.execute("insert INTO models_performance (course_id, Features,  ML_Algorithm, Binary_Multiclass, accuracy, f1, recall , precision_1) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)", # REPLACE INTO: do as insert in do does except if the assessment_name (PK) already exist in the database it will replace it with the new record
                                        (courseName, counter, "SVM", "Multiclass", SVM_accuracy_Multiclass [i], SVM_f1_Multiclass [i], SVM_recall_Multiclass [i] , SVM_precision_Multiclass [i] ))
                        counter=counter-1
                        con.commit() # apply changes
                    counter=length_all_assessments_in_selected_course # i used this counter to help me to keep the (length_all_assessments_in_selected_course) untouch during the loop

                    #insert KNN Binary acc & f1 & recall & precision into the course_and_models tablefor
                    for i in range(length_all_assessments_in_selected_course):
                        c.execute("insert INTO models_performance (course_id, Features,  ML_Algorithm, Binary_Multiclass, accuracy, f1, recall , precision_1) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)", # REPLACE INTO: do as insert in do does except if the assessment_name (PK) already exist in the database it will replace it with the new record
                                        (courseName, counter, "KNN", "Binary", KNN_accuracy_Binary [i], KNN_f1_Binary [i], KNN_recall_Binary [i], KNN_precision_Binary  [i] ))
                        counter=counter-1
                        con.commit() # apply changes
                    counter=length_all_assessments_in_selected_course # i used this counter to help me to keep the (length_all_assessments_in_selected_course) untouch during the loop

                    #insert KNN Multiclass acc & f1 & recall & precision into the course_and_models table
                    for i in range(length_all_assessments_in_selected_course):
                        c.execute("insert INTO models_performance (course_id, Features,  ML_Algorithm, Binary_Multiclass, accuracy, f1, recall , precision_1) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)", # REPLACE INTO: do as insert in do does except if the assessment_name (PK) already exist in the database it will replace it with the new record
                                        (courseName, counter, "KNN", "Multiclass", KNN_accuracy_Multiclass [i], KNN_f1_Multiclass [i], KNN_recall_Multiclass [i], KNN_precision_Multiclass [i]))
                        counter=counter-1
                        con.commit() # apply changes
                    counter=length_all_assessments_in_selected_course # i used this counter to help me to keep the (length_all_assessments_in_selected_course) untouch during the loop

                    #insert NB Binary acc & f1 & recall & precision into the course_and_models tablefor
                    for i in range(length_all_assessments_in_selected_course):
                        c.execute("insert INTO models_performance (course_id, Features,  ML_Algorithm, Binary_Multiclass, accuracy, f1, recall , precision_1) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)", # REPLACE INTO:
                                        (courseName, counter, "NB", "Binary", NB_accuracy_Binary [i], NB_f1_Binary [i], NB_recall_Binary [i], NB_precision_Binary [i]))
                        counter=counter-1
                        con.commit() # apply changes
                    counter=length_all_assessments_in_selected_course # i used this counter to help me to keep the (length_all_assessments_in_selected_course) untouch during the loop

                    #insert NB Multiclass acc & f1 & recall & precision into the course_and_models table
                    for i in range(length_all_assessments_in_selected_course):
                        c.execute("insert INTO models_performance (course_id, Features,  ML_Algorithm, Binary_Multiclass, accuracy, f1, recall , precision_1) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)", # REPLACE INTO: do as insert in do does except if the assessment_name (PK) already exist in the database it will replace it with the new record
                                        (courseName, counter, "NB", "Multiclass", NB_accuracy_Multiclass [i], NB_f1_Multiclass [i], NB_recall_Multiclass [i], NB_precision_Multiclass [i]))
                        counter=counter-1
                        con.commit() # apply changes
                    counter=length_all_assessments_in_selected_course # i used this counter to help me to keep the (length_all_assessments_in_selected_course) untouch during the loop


                    #insert DT Binary acc & f1 & recall & precision into the course_and_models tablefor
                    for i in range(length_all_assessments_in_selected_course):
                        c.execute("insert INTO models_performance (course_id, Features,  ML_Algorithm, Binary_Multiclass, accuracy, f1, recall , precision_1) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)", # REPLACE INTO:
                                        (courseName, counter, "DT", "Binary", DT_accuracy_Binary [i], DT_f1_Binary [i], DT_recall_Binary [i], DT_precision_Binary [i]))
                        counter=counter-1
                        con.commit() # apply changes
                    counter=length_all_assessments_in_selected_course # i used this counter to help me to keep the (length_all_assessments_in_selected_course) untouch during the loop

                    #insert DT Multiclass acc & f1 & recall & precision into the course_and_models table
                    for i in range(length_all_assessments_in_selected_course):
                        c.execute("insert INTO models_performance (course_id, Features,  ML_Algorithm, Binary_Multiclass, accuracy, f1, recall , precision_1) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)", # REPLACE INTO: do as insert in do does except if the assessment_name (PK) already exist in the database it will replace it with the new record
                                        (courseName, counter, "DT", "Multiclass", DT_accuracy_Multiclass [i], DT_f1_Multiclass [i], DT_recall_Multiclass [i], DT_precision_Multiclass [i]))
                        counter=counter-1
                        con.commit() # apply changes
                    counter=length_all_assessments_in_selected_course # i used this counter to help me to keep the (length_all_assessments_in_selected_course) untouch during the loop



                    con.commit() # apply changes
                    ######################################################################################################################################################
                    ######################################################################################################################################################

                    ##################################################################################################################################################################################################################
                    #here i render thank you page with acc and f1 for all models that have been created + course name + how many model created + number_of_model_for_loop_html [this helps me in the html page to loop based on how many model created for each algorithm]
                    return render_template('thank_you_for_creating_models.html', \
                        RF_accuracy_Binary=RF_accuracy_Binary, RF_f1_Binary=RF_f1_Binary, \
                        RF_accuracy_Multiclass=RF_accuracy_Multiclass, \
                        RF_f1_Multiclass=RF_f1_Multiclass, SVM_accuracy_Binary=SVM_accuracy_Binary, \

                        SVM_f1_Binary=SVM_f1_Binary, SVM_accuracy_Multiclass=SVM_accuracy_Multiclass, \
                        SVM_f1_Multiclass=SVM_f1_Multiclass, KNN_accuracy_Binary=KNN_accuracy_Binary, \

                        KNN_f1_Binary=KNN_f1_Binary, KNN_accuracy_Multiclass=KNN_accuracy_Multiclass, \
                        KNN_f1_Multiclass=KNN_f1_Multiclass, NB_accuracy_Binary=NB_accuracy_Binary, \

                        NB_f1_Binary=NB_f1_Binary, NB_accuracy_Multiclass=NB_accuracy_Multiclass, \
                        NB_f1_Multiclass=NB_f1_Multiclass, \

                        DT_accuracy_Binary=DT_accuracy_Binary, \
                        DT_f1_Binary=DT_f1_Binary, DT_accuracy_Multiclass=DT_accuracy_Multiclass, \
                        DT_f1_Multiclass=DT_f1_Multiclass, \

                        RF_recall_Binary=RF_recall_Binary, RF_precision_Binary=RF_precision_Binary,\
                        RF_recall_Multiclass=RF_recall_Multiclass, RF_precision_Multiclass=RF_precision_Multiclass,\
                        SVM_recall_Binary=SVM_recall_Binary, SVM_precision_Binary=SVM_precision_Binary,\
                        SVM_recall_Multiclass=SVM_recall_Multiclass, SVM_precision_Multiclass=SVM_precision_Multiclass,\
                        KNN_recall_Binary=KNN_recall_Binary, KNN_precision_Binary=KNN_precision_Binary,\
                        KNN_recall_Multiclass=KNN_recall_Multiclass, KNN_precision_Multiclass=KNN_precision_Multiclass,\
                        NB_recall_Binary=NB_recall_Binary, NB_precision_Binary=NB_precision_Binary,\
                        NB_recall_Multiclass=NB_recall_Multiclass, NB_precision_Multiclass=NB_precision_Multiclass,\
                        DT_recall_Binary=DT_recall_Binary, DT_precision_Binary=DT_precision_Binary,\
                        DT_recall_Multiclass=DT_recall_Multiclass, DT_precision_Multiclass=DT_precision_Multiclass,\

                        all_Number_of_created_model=Number_of_created_model, number_of_model_for_loop_html = RF_number_of_model_Multiclass+1, \
                        courseName=courseName, length_of_dataset_after_cleaning_Binary=length_of_dataset_after_cleaning_Binary,\
                           length_of_dataset_after_cleaning_Multiclass=length_of_dataset_after_cleaning_Multiclass )


            else:
                return render_template('no_dataset_for_this_course.html') # if theere is no dataset in the databease for this course

        except sql.Error as e: # if error
            # then display the error in 'database_error.html' page
            return render_template('database_error.html', error=e)

        finally:
            con.close() # close the connection


#NNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNN



#SSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSS
#upload_file.py




##############################################################################################
###################################### upload csv ############################################################
##################################################################################################

#[so the right number of csv file columns must be equal to the number of assessments for the selected course + total + grade. then i will generate columns:passorfail and multiclassLevel]


@app.route('/upload_csv', methods=['GET','POST'])
@login_required
def upload_csv():
  if request.method == 'GET':
      try:
        con = sql.connect(host="pythonanywhere_host", user="pythonanywhere_user", password="pythonanywhere_password", database="pythonanywhere$database_name") #this is not the real connections details
        c =  con.cursor() # cursor
        query = "Select * from course where userName=%s"
        values = session["USERNAME"]
        cityList = c.execute(query, (values,))
        cityList = c.fetchall()
        return render_template('upload_csv.html', cityList=cityList)

      except sql.Error as e: # if error
            # then display the error in 'database_error.html' page
            return render_template('database_error.html', error=e)

      finally:
        con.close() # close the connection


  else:
      if request.method == 'POST':
        course_course_id = request.form['course_course_id']
        #conversion_radio_btn = request.form['conversion'] # from the conversion radio button

        year = request.form['year']
        semester_or_trimester = request.form['semester_or_trimester']

        try:

            con = sql.connect(host="pythonanywhere_host", user="pythonanywhere_user", password="pythonanywhere_password", database="pythonanywhere$database_name") #this is not the real connections details
            c =  con.cursor() # cursor

            #to get how many assessment in the selected course, so that we can match the uploaded csv file column with number of assessment
            query_assessment_name= "SELECT assessment_name  FROM assessment where course_course_id=%s"
            values = course_course_id
            assessment_name= c.execute(query_assessment_name, (values,))
            assessment_name = c.fetchall()

            assessment_name_length = len(assessment_name)


            #here i want to read the uploaded csv file
            csv_file = request.files['file'] #from the html file input name

            # this helps me to validate if the uploaded file is a csv extention
            file_ext = os.path.splitext(request.files['file'].filename)[1]
            #return render_template('no_dashboard_yet.html', data = file_ext)
            if file_ext not in app.config['UPLOAD_EXTENSIONS']:
                return render_template('no_dashboard_yet.html', data = "please make sure to upload a csv file")
            # END OF this helps me to validate if the uploaded file is a csv extention


            csv_file = TextIOWrapper(csv_file, encoding='utf-8')
            csv_reader = csv.reader(csv_file, delimiter=',')
            next(csv_reader) #skip the first row (title such as practical test 1)
            data = [row for row in csv_reader] #read all ceel in the csv file and put it in the data [array]

            if len(data) == 0:
                return render_template('empty.html')


            #........................................................................................................................
            #here i want to do Rukshan comments about making the first row in CSV file the weight [mark of]
            mark_out_CSV_array = np.array(data)
            #ttype=type(my_array) #temppp
            mark_out_CSV= mark_out_CSV_array[0,:]
            assessment_waitage=mark_out_CSV_array[1,:]


            data = np.array(data)
            data= data [2:, :]
            data=data.tolist()
            #return render_template('empty3.html', data = data)

            #.......................................................................................................................



            #this query i will use it later to insert data from [data] array into the assessment_std Table in the database
            query =  "INSERT INTO assessment_std (assessment_course_course_id,mark, assessment_assessment_name, student_student_id) VALUES (%s,%s,%s, %s)"

            if len(data) == 0:
                return render_template('empty.html')

            else:

             for row in data: #this is the first loop that loops as long as the csv file row [instances]

                if len(row)>(assessment_name_length+2): # this is to check if csv file feature has more feature than course's assessment s
                    return render_template('too_big_csv_file.html')    # if csv file has feature more than number of assessments in the database

                elif  len(row)<(assessment_name_length+2):
                    return render_template('too_small_csv_file.html')    # if csv file has feature less than number of assessments in the database

                #[so the right number of csv file columns must be equal to the number of assessments for the selected course + total + grade. then i will generate columns:passorfail and multiclassLevel]
                else:# if csv file has feature exactly same as the number of assessments in the database

                    if row[assessment_name_length]=="": #if the is null in the assessment make it 0
                           row[assessment_name_length]=0

                    try:# i used try and except ValueError, to solve if data in the csv file is not nubmber such as jkhkjnh

                        row[assessment_name_length]=float(row[assessment_name_length]) #i used float because when using int any float number return it 0, so i had to use float

                    except ValueError: # if the cell has strange string such as (jklnlj) in the assessments grade, it will make it 0
                        row[assessment_name_length] = 0

                    if row[assessment_name_length]!="" : #this to make sure it read data based on the total in the csv. if there is no total it stop reading and inserting data to DB

                        #generate pass_or_fail value from total if total >=50 pass, else fail
                        if int(row[assessment_name_length])>=50:
                            pass_or_fail =1
                        else:
                            pass_or_fail=0

                        #generate multiclass_levels value from total if total >55 pass, elif total<45 at_risk, else fail
                        if int(row[assessment_name_length])>55:
                            multiclass_levels ="pass"

                        elif int(row[assessment_name_length])<45:
                            multiclass_levels ="at_risk"
                        else:
                            multiclass_levels="borderline"

                        #query2: to insert data into the student Table in the database
                        #query2 = "INSERT INTO student (course_course_id, total, grade, pass_or_fail, multiclass_levels) VALUES (%s, %s, %s, %s, %s)"
                        query2 = "INSERT INTO student (course_course_id, total, grade, pass_or_fail, multiclass_levels, year, semester_or_trimester) VALUES (%s, %s, %s, %s, %s, %s, %s)"

                        #value = (course_course_id, row[assessment_name_length], row[assessment_name_length+1], pass_or_fail, multiclass_levels)
                        #c.execute(query2,(value))

                        c.execute(query2, (course_course_id, row[assessment_name_length], row[assessment_name_length+1], pass_or_fail, multiclass_levels, year, semester_or_trimester),)

                        con.commit() # apply changes


                        for i in range(assessment_name_length): #this is the second loop that loops as long as the csv file coloumns [features] to fill each assessment in the selected course

                            #444444444444444444444444444444444444
                            #here i want to make sure to match students_id btn student and assessments_Std tables
                            con = sql.connect(host="pythonanywhere_host", user="pythonanywhere_user", password="pythonanywhere_password", database="pythonanywhere$database_name") #this is not the real connections details
                            c = con.cursor() # cursor
                            c = con.cursor(buffered=True)

                            student_id = c.execute("Select student_id from student order by student_id")

                            student_id = [ r[0] for r in c.fetchall() if str(r[0]) ] # i used this to return fetch the data without (). I also used str(row[0]) to make sure it does not miss any int 0


                            last_student_id = student_id[-1] #student_id[-1] get the last student id in the student table, so i can overcome the isse of foriegn key constranit [CASCADE]
                           #444444444444444444444444444444444444

                            #student_id = c.execute("Select student_id from student ")
                            #student_id = [ r[0] for r in c.fetchall() if str(r[0]) ] # i used this to return fetch the data without (). I also used str(row[0]) to make sure it does not miss any int 0

                            #last_student_id = student_id[-1] #student_id[-1] get the last student id in the student table, so i can overcome the isse of foriegn key constranit [CASCADE]

                            #3333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333
                            #here I fixed the problem of inserting without considering the order of assessments
                            value = course_course_id
                            query4 = "SELECT assessment_name FROM assessment WHERE course_course_id = %s  order by auto_increment"
                            c.execute(query4,(value,))

                            assessments_order = c.fetchall()

                            assessment_name_to_string = ",".join(assessments_order [i]) #to solve error "python mysqlconnector mysqlinterfaceerror python type tuple cannot be converted"
                            #3333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333


                            #assessment_name_to_string = ",".join(assessment_name[i]) #to solve error "python mysqlconnector mysqlinterfaceerror python type tuple cannot be converted"

                            if row[i]=="": #if the is null in the assessment make it 0
                                row[i]=0

                            try:# iused try and except ValueError, to solve if data in the csv file is not nubmber such as jkhkjnh

                                row[i]=float(row[i]) #i used float because when using int any float number return it 0, so i had to use float

                                #if conversion_radio_btn=="Yes": # here i did the if because i want to check if the user want to convert the data in the csv file or not

                                #here in this block, I tried to convert students marks into a Percentages as Simon suggested useing mark_out and mark_worth
                                #66666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666
                                query5 = "SELECT mark_out FROM assessment where course_course_id=%s and assessment_name =%s"

                                query6 = "SELECT mark_worth FROM assessment where course_course_id=%s and assessment_name =%s"

                                c.execute(query5,(course_course_id,assessment_name_to_string,))
                                mark_out = [ r[0] for r in c.fetchall() if str(r[0]) ]

                                c.execute(query6,(course_course_id,assessment_name_to_string,))
                                mark_worth = [ r[0] for r in c.fetchall() if str(r[0]) ]

                                mark_out = np.array(mark_out)
                                mark_worth = np.array(mark_worth)


                                if mark_out_CSV[i] !="0" and assessment_waitage[i] !="0":

                                    row[i] = float(row[i]) / int(mark_out_CSV[i]) * int(assessment_waitage[i])

                                    row[i] = float(row[i]) / int(assessment_waitage[i]) * 100 # this is the conversion based on Rukshan comments which is the marked out is from the first row in the csv
                                else:     #here the value of mark_out_CSV[i]==0 which means the user did not add correct value for the wieght in the csv file or the value was 0
                                    #row[i] = int(row[i])
                                    row[i] = float(row[i]) / int(mark_out) * int(mark_worth)
                                    #row[i] = float(row[i]) / int(mark_worth) * int(mark_out)
                                    row[i] = float(row[i]) / int(mark_worth) * 100

                                #elif conversion_radio_btn=="No":
                                #    row[i] = row[i]

                                #66666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666


                                #query: is the one i did before the first for loop #this query i will use it later to insert data from [data] array into the assessment_std Table in the database
                                #this one query =  "INSERT INTO assessment_std (assessment_course_course_id,mark, assessment_assessment_name, student_student_id) VALUES (%s,%s,%s, %s)"
                                c.execute(query,(course_course_id, row[i], assessment_name_to_string , last_student_id, )) #last_student_id: student_id[-1] get the last student id in the student table
                                con.commit() # apply changes

                            except ValueError: # if the cell has strange string such as (jklnlj) in the assessments grade, it will make it 0
                                row[i] = 0
                                c.execute(query,(course_course_id, row[i], assessment_name_to_string , last_student_id, )) #student_id[-1] get the last student id in the student table
                                con.commit() # apply changes



            #here i want to tel users how many record inserted into the database by cheching length of students table for the selected course
            query_length_of_addedd_data= "Select * from student where course_course_id=%s"
            values = course_course_id
            length_of_addedd_data= c.execute(query_length_of_addedd_data, (values,))
            length_of_addedd_data = c.fetchall()
            length_of_addedd_data = len(length_of_addedd_data)
            # EDN OF (here i want to tel users how many record inserted into the database by cheching length of students table for the selected course)

            return render_template('createThanks_for_upload.html', length_of_addedd_data = length_of_addedd_data)    # if everything went correctly, i render this html that says thankyou you upload was successful

        except sql.Error as e: # if error
            # then display the error in 'database_error.html' page
            return render_template('database_error.html', error=e)

        finally:
            con.close() # close the connection


#NNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNN



#SSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSS
#create_clo.py


#\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\design_course\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
#this is the Get method to aviod two dynamic dropdown lists. Design a Course
@app.route('/design_course', methods=['GET', 'Post'])
@login_required
def design_course():
    if request.method == 'GET':
        try:
            con = sql.connect(host="pythonanywhere_host", user="pythonanywhere_user", password="pythonanywhere_password", database="pythonanywhere$database_name") #this is not the real connections details
            c =  con.cursor() # cursor
            query = "Select * from course where userName=%s"
            values = session["USERNAME"]
            cityList = c.execute(query, (values,))
            cityList = c.fetchall()

            return render_template('design_course.html', cityList=cityList)

        except sql.Error as e: # if error
            # then display the error in 'database_error.html' page
            return render_template('database_error.html', error=e)

        finally:
            con.close() # close the connection

    #else: # request.method == 'POST':
     #   courseName = request.form['course_course_id']
      #  return render_template('create_clo.html', courseName=courseName)


#\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\End OF design_course\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\

#this is for just to avoid two dynamic dropdown lists. this is the POST method from the Get method above: design_course
@app.route('/create_clo_first',methods=['POST'])
@login_required
def create_clo_first():

    courseName = request.form['course_course_id']

    #courseName=courseName
    try:
        con = sql.connect(host="pythonanywhere_host", user="pythonanywhere_user", password="pythonanywhere_password", database="pythonanywhere$database_name") #this is not the real connections details
        c =  con.cursor() # cursor



        query = "Select * from clo where course_course_id=%s and clo_level='0'"
        #values = session["USERNAME"]
        values=courseName
        parent_clo_db = c.execute(query, (values,))
        parent_clo_db = c.fetchall()

        return render_template('create_clo.html', cityList=courseName, parent_clo_db=parent_clo_db)

    except sql.Error as e: # if error
        # then display the error in 'database_error.html' page
        return render_template('database_error.html', error=e)

    finally:

        con.close() # close the connection


    #return render_template('create_clo.html', courseName=courseName)


##############################################################################################
###################################### create_clo ############################################################
##################################################################################################

#create_clo
@app.route('/create_clo', methods=['GET', 'POST'])
@login_required
def create_clo():
    if request.method == 'POST':



    #else: # request.method == 'POST':
        # read data from the form and save in variable
        course_course_id = request.form['course_course_id']

        clo_name = request.form['clo_name']
        #clo_title = request.form['clo_title']
        clo_level = request.form['clo_level']

        #if request.form['parent_clo']:
        parent_clo = request.form['parent_clo']


        #assessment_name = request.form['assessment_name']
        #mark_out = request.form['mark_out']
        #mark_worth = request.form['mark_worth']


        # store in database
        try:
            con = sql.connect(host="pythonanywhere_host", user="pythonanywhere_user", password="pythonanywhere_password", database="pythonanywhere$database_name") #this is not the real connections details
            c =  con.cursor() # cursor
            # insert data # REPLACE INTO: do as insert in do does except if the assessment_name (PK) already exist in the database it will replace it with the new record
            c.execute("insert IGNORE INTO clo (clo_name, course_course_id, clo_level, parent_clo, userName) VALUES (%s,%s,%s,%s,%s)", # REPLACE INTO: do as insert in do does except if the assessment_name (PK) already exist in the database it will replace it with the new record
                (clo_name, course_course_id, clo_level, parent_clo, session["USERNAME"] ))
            con.commit() # apply changes
            # go to thanks page
            query = "Select course_id from course where course_id=%s"
            values = course_course_id
            cityList = c.execute(query, (values,))
            cityList = [ r[0] for r in c.fetchall() if str(r[0]) ]
            #cityList = c.fetchall()
            #cityList=str(cityList)

            query = "Select * from clo where course_course_id=%s and clo_level='0'"
            values = course_course_id
            parent_clo_db = c.execute(query, (values,))
            parent_clo_db = c.fetchall()


            return render_template('create_clo_after_adding_assessments.html', cityList=cityList, parent_clo_db=parent_clo_db)


        except sql.Error as e: # if error
            # then display the error in 'database_error.html' page
            return render_template('database_error.html', error=e)

        finally:
            con.close() # close the connection

        return render_template('create_clo.html', cityList=cityList)

#\\\\\\\\\\\\\\\


#NNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNN



#SSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSS
#create_tla.py

@app.route('/design_course_tla', methods=['GET', 'Post'])
@login_required
def design_course_tla():
    if request.method == 'GET':
        try:
            con = sql.connect(host="pythonanywhere_host", user="pythonanywhere_user", password="pythonanywhere_password", database="pythonanywhere$database_name") #this is not the real connections details
            c =  con.cursor() # cursor
            query = "Select * from course where userName=%s"
            values = session["USERNAME"]
            cityList = c.execute(query, (values,))
            cityList = c.fetchall()

            return render_template('design_course_tla.html', cityList=cityList)

        except sql.Error as e: # if error
            # then display the error in 'database_error.html' page
            return render_template('database_error.html', error=e)

        finally:
            con.close() # close the connection

    #else: # request.method == 'POST':


#\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\End OF design_course\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\

#this is for just to avoid two dynamic dropdown lists. this is the POST method from the Get method above: design_course
@app.route('/create_tla_first',methods=['POST'])
@login_required
def create_tla_first():


    courseName = request.form['course_course_id']

    try:
        con = sql.connect(host="pythonanywhere_host", user="pythonanywhere_user", password="pythonanywhere_password", database="pythonanywhere$database_name") #this is not the real connections details
        c =  con.cursor() # cursor



        query = "Select * from tla where course_course_id=%s"
        values = courseName
        parent_tla_db = c.execute(query, (values,))
        parent_tla_db = c.fetchall()



        query = "SELECT * FROM clo where userName=%s and course_course_id= %s order by auto_increment"
        values = (session["USERNAME"], courseName)
        parent_clo_db = c.execute(query, values)
        parent_clo_db = c.fetchall()

        query = "SELECT * FROM assessment where  course_course_id=%s order by auto_increment"
        values = courseName
        assessment_name = c.execute(query, (values,))
        assessment_name = c.fetchall()

        #return render_template('empty3.html', data = assessment_name)

        return render_template('create_tla.html', cityList=courseName, parent_tla_db=parent_tla_db, parent_clo_db=parent_clo_db, assessment_name = assessment_name)

    except sql.Error as e: # if error
        # then display the error in 'database_error.html' page
        return render_template('database_error.html', error=e)

    finally:

            con.close() # close the connection




    #return render_template('create_tla.html', cityList=courseName)





    #return render_template('create_clo.html', courseName=courseName)



#
##############################################################################################
###################################### create_tla ############################################################
##################################################################################################

#create_tla
@app.route('/create_tla', methods=['GET', 'POST'])
@login_required
def create_tla():
    if request.method == 'POST':



    #else: # request.method == 'POST':
        # read data from the form and save in variable
        course_course_id = request.form['course_course_id']

        lecture_or_lab = request.form['lecture_or_lab']
        other= request.form['other']
        if lecture_or_lab=="Other":
            lecture_or_lab=other


        lecture_lab_number = request.form['lecture_lab_number']
        tla_topic = request.form['tla_topic']

        tla_Resources= request.form['tla_Resources']
        if tla_Resources:
            tla_Resources= request.form['tla_Resources']
        else:
            tla_Resources=""

        #return render_template('empty3.html', data = tla_Resources)

        parent_tla = request.form['parent_tla']

        clo_checkbox = request.form.getlist('clo_checkbox')

        assessment_checkbox = request.form.getlist('assessment_checkbox')





        # store in database
        try:
            con = sql.connect(host="pythonanywhere_host", user="pythonanywhere_user", password="pythonanywhere_password", database="pythonanywhere$database_name") #this is not the real connections details
            c =  con.cursor() # cursor
            # please know that lecture_lab_number is the Activity Name
            # insert data # REPLACE INTO: do as insert in do does except if the assessment_name (PK) already exist in the database it will replace it with the new record
            c.execute("insert IGNORE INTO tla (lecture_or_lab, course_course_id, lecture_lab_number, tla_topic, parent_tla , userName, tla_Resources) VALUES (%s,%s,%s,%s,%s,%s,%s)", # REPLACE INTO: do as insert in do does except if the assessment_name (PK) already exist in the database it will replace it with the new record
                (lecture_or_lab, course_course_id, lecture_lab_number, tla_topic, parent_tla, session["USERNAME"], tla_Resources ))
            con.commit() # apply changes

            #return render_template('empty3.html', data = tla_topic)
            query = "SELECT tla_id FROM tla where tla_topic=%s and course_course_id=%s"
            values = (tla_topic, course_course_id)
            tla_id = c.execute(query, values)
            tla_id = [ r[0] for r in c.fetchall() if str(r[0]) ]
            #return render_template('empty3.html', data = tla_id)

            for user in clo_checkbox:

                query = "SELECT auto_increment FROM clo where clo_name=%s and course_course_id=%s"
                values = (user , course_course_id)
                c.execute(query, values)
                clo_auto_increment = [ r[0] for r in c.fetchall() if str(r[0]) ]

                #return render_template('empty3.html', data = tla_id[0])
                c.execute("insert IGNORE INTO allign_tla_to_clo_m_to_m (clo_name, tla_id, course_id, clo_auto_increment) VALUES (%s,%s,%s,%s)", # REPLACE INTO: do as insert in do does except if the assessment_name (PK) already exist in the database it will replace it with the new record
                    (user, tla_id[0], course_course_id, clo_auto_increment[0]))
                con.commit() # apply changes




            for user in assessment_checkbox:

                query = "SELECT auto_increment FROM assessment where assessment_name=%s and course_course_id=%s"
                values = (user , course_course_id)
                c.execute(query, values)
                assessment_auto_increment = [ r[0] for r in c.fetchall() if str(r[0]) ]
                #return render_template('empty3.html', data = assessment_auto_increment)

                c.execute("insert IGNORE INTO allign_tla_to_at_m_to_m (assessment_name, tla_id, course_id, assessment_auto_inc) VALUES (%s,%s,%s,%s)", # REPLACE INTO: do as insert in do does except if the assessment_name (PK) already exist in the database it will replace it with the new record
                    (user, tla_id[0], course_course_id, assessment_auto_increment [0]))
                con.commit() # apply changes


            # go to thanks page
            query = "Select course_id from course where course_id=%s"
            values = course_course_id
            cityList = c.execute(query, (values,))
            cityList = [ r[0] for r in c.fetchall() if str(r[0]) ]

            query = "Select * from tla where course_course_id=%s"
            values = course_course_id
            parent_tla_db = c.execute(query, (values,))
            parent_tla_db = c.fetchall()


            query = "SELECT * FROM clo where userName=%s and course_course_id= %s order by auto_increment"
            values = (session["USERNAME"], course_course_id)
            parent_clo_db = c.execute(query, values)
            parent_clo_db = c.fetchall()

            query = "SELECT * FROM assessment where  course_course_id=%s order by auto_increment"
            values = course_course_id
            assessment_name = c.execute(query, (values,))
            assessment_name = c.fetchall()


            return render_template('create_tla_after_adding_assessments.html', cityList=cityList, parent_tla_db=parent_tla_db, parent_clo_db=parent_clo_db, assessment_name = assessment_name)


        except sql.Error as e: # if error
            # then display the error in 'database_error.html' page
            return render_template('database_error.html', error=e)

        finally:
            con.close() # close the connection

        return render_template('create_tla_after_adding_assessments.html', cityList=cityList)
#NNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNN



#SSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSS
#map_Ats_to_TLAs.py


#\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\design_course\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
#this is the Get method to aviod two dynamic dropdown lists. Design a Course
@app.route('/design_course_align', methods=['GET', 'Post'])
@login_required
def design_course_align():
    if request.method == 'GET':
        try:
            con = sql.connect(host="pythonanywhere_host", user="pythonanywhere_user", password="pythonanywhere_password", database="pythonanywhere$database_name") #this is not the real connections details
            c =  con.cursor() # cursor
            query = "Select * from course where userName=%s"
            values = session["USERNAME"]
            cityList = c.execute(query, (values,))
            cityList = c.fetchall()

            return render_template('design_course_align.html', cityList=cityList)

        except sql.Error as e: # if error
            # then display the error in 'database_error.html' page
            return render_template('database_error.html', error=e)

        finally:
            con.close() # close the connection

    #else: # request.method == 'POST':


#\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\End OF design_course\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\

#this is for just to avoid two dynamic dropdown lists. this is the POST method from the Get method above: design_course
@app.route('/create_align_first',methods=['POST'])
@login_required
def create_align_first():


    courseName = request.form['course_course_id']

    try:
        con = sql.connect(host="pythonanywhere_host", user="pythonanywhere_user", password="pythonanywhere_password", database="pythonanywhere$database_name") #this is not the real connections details
        c =  con.cursor() # cursor

        query = "Select * from course where course_id=%s"
        values = courseName
        cityList = c.execute(query, (values,))
        cityList = c.fetchall()

        query = "Select * from assessment where course_course_id=%s order by auto_increment"
        values = courseName
        assessment_db = c.execute(query, (values,))
        assessment_db = c.fetchall()

        query = "Select * from tla where course_course_id=%s"
        values = courseName
        parent_tla_db = c.execute(query, (values,))
        parent_tla_db = c.fetchall()



        return render_template('map_ATs_to_TLAs.html', cityList=courseName, assessment_db=assessment_db, parent_tla_db=parent_tla_db)

    except sql.Error as e: # if error
        # then display the error in 'database_error.html' page
        return render_template('database_error.html', error=e)

    finally:

        con.close() # close the connection





    #return render_template('create_tla.html', cityList=courseName)





    #return render_template('create_clo.html', courseName=courseName)



#

##############################################################################################
###################################### map_Ats_to_TLAs ############################################################
##################################################################################################

#map_Ats_to_TLAs
@app.route('/map_Ats_to_TLAs', methods=['GET', 'POST'])
@login_required
def map_Ats_to_TLAs():
    if request.method == 'POST':

    #else: # request.method == 'POST':
        # read data from the form and save in variable
        course_course_id = request.form['course_course_id']

        assessment_name = request.form['assessment_name']
        #assessment_part = request.form['assessment_part']
        #assessment_task = request.form['assessment_task']
        map_to_tla = request.form['map_to_tla']



        # store in database
        try:
            con = sql.connect(host="pythonanywhere_host", user="pythonanywhere_user", password="pythonanywhere_password", database="pythonanywhere$database_name") #this is not the real connections details
            c =  con.cursor() # cursor
            # insert data # REPLACE INTO: do as insert in do does except if the assessment_name (PK) already exist in the database it will replace it with the new record
            c.execute("insert IGNORE INTO at_map_to_tla (assessment_name, course_course_id, tla_id, userName) VALUES (%s,%s,%s,%s)", # REPLACE INTO: do as insert in do does except if the assessment_name (PK) already exist in the database it will replace it with the new record
                (assessment_name, course_course_id, map_to_tla, session["USERNAME"] ))
            con.commit() # apply changes

            # go to thanks page
            query = "Select course_id from course where course_id=%s"
            values = course_course_id
            cityList = c.execute(query, (values,))
            cityList = [ r[0] for r in c.fetchall() if str(r[0]) ]

            query = "Select * from assessment where course_course_id=%s order by auto_increment"
            values = course_course_id
            assessment_db = c.execute(query, (values,))
            assessment_db = c.fetchall()

            query = "Select * from tla where course_course_id=%s "
            values = course_course_id
            parent_tla_db = c.execute(query, (values,))
            parent_tla_db = c.fetchall()







            return render_template('create_map_ATs_to_TLAs_after_adding_assessments.html', cityList=cityList, parent_tla_db=parent_tla_db, assessment_db=assessment_db)


        except sql.Error as e: # if error
            # then display the error in 'database_error.html' page
            return render_template('database_error.html', error=e)

        finally:
            con.close() # close the connection

        return render_template('create_tla_after_adding_assessments.html', cityList=cityList)

#\\\\\\\\\\\\\\\




#NNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNN


#SSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSS

#pdf.py

#\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\design_course\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
#this is the Get method to aviod two dynamic dropdown lists. Design a Course
@app.route('/pdf_choose_course', methods=['GET', 'Post'])
@login_required
def pdf_choose_course():
    if request.method == 'GET':
        try:
            con = sql.connect(host="pythonanywhere_host", user="pythonanywhere_user", password="pythonanywhere_password", database="pythonanywhere$database_name") #this is not the real connections details
            c =  con.cursor() # cursor
            query = "Select * from course where userName=%s"
            values = session["USERNAME"]
            cityList = c.execute(query, (values,))
            cityList = c.fetchall()

            return render_template('pdf_choose_course.html', cityList=cityList)

        except sql.Error as e: # if error
            # then display the error in 'database_error.html' page
            return render_template('database_error.html', error=e)

        finally:
            con.close() # close the connection

    #else: # request.method == 'POST':
     #   courseName = request.form['course_course_id']
      #  return render_template('create_clo.html', courseName=courseName)


#\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\End OF design_course\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\


##############################################################################################
###################################### pdf ############################################################
##################################################################################################



@app.route('/pdf', methods=['Post'])
@login_required
#@login_required_std
def pdf():
    #if request.method == 'Post':

        #course_id='3_INFT2031'
        course_id = request.form['course_course_id']


        #std_id=session["USERNAME"]
        #return render_template('empty3.html', data = std_id)
        #this block for the barchart
        try:

            con = sql.connect(host="pythonanywhere_host", user="pythonanywhere_user", password="pythonanywhere_password", database="pythonanywhere$database_name") #this is not the real connections details

            c =  con.cursor() # cursor


            # to get course name from course table using course_id

            query = "SELECT course_name FROM course where course_id=%s"
            values = course_id
            cityList = c.execute(query, (values,))
            #course_name = c.fetchall()
            course_name = [ row[0] for row in c.fetchall() if row[0] ] # i used this to return fetch the data without ()
            #return render_template('empty3.html', data = course_name [0])
            # END OF to get course name from course table using course_id


            # this block for std name and id
            #query = "SELECT distinct student_id FROM student_grade where course_id=%s"
            #query = "SELECT distinct student_grade.student_id, current_student.student_name FROM student_grade INNER JOIN current_student ON student_grade.student_id = current_student.student_id where student_grade.course_id=%s"
            query = "SELECT distinct student_grade.student_id, current_student.student_name FROM student_grade INNER JOIN current_student ON student_grade.student_id = current_student.student_id where student_grade.course_id=%s and current_student.course_id=%s"
            values = (course_id, course_id)
            cityList = c.execute(query, values)
            std_id_and_name = c.fetchall()


            #return render_template('empty3.html', data = len(std_id_and_name))




            #this is used if teacher select course that does not have any std's data
            if not std_id_and_name:
               return render_template('no_dashboard_yet.html', data = "NO Data to Show in the Dashboard Yet, Please Add Students Grades and Design Your Course First")

            std_id_and_name = np.asarray(std_id_and_name)
            std_id = std_id_and_name[:,0]
            std_name = std_id_and_name[:,1]
            #std_id = [ row[0] for row in c.fetchall() if row[0] ] # i used this to return fetch the data without ()

            #return render_template('empty3.html', data = std_id_and_name[:,0])
            # END OF this block for std name and id




            # this block for asserssment name of last assessment
            query = "SELECT distinct assessment_name FROM student_grade where course_id=%s"
            values = course_id
            cityList = c.execute(query, (values,))
            #labels = c.fetchall()
            assessment_name = [ row[0] for row in c.fetchall() if row[0] ] # i used this to return fetch the data without ()
            #return render_template('empty3.html', data = assessment_name)
            #labels=type(labels)
            #return render_template('empty3.html', data = labels)

            # END OF this block for asserssment name of last assessment

            #query = "SELECT distinct assessment_name FROM student_grade where course_id=%s"
            query = "SELECT distinct student_id, assessment_name, mark FROM student_grade where course_id=%s"
            values = course_id
            cityList = c.execute(query, (values,))
            temp = c.fetchall()
            temp = np.asarray(temp)

            #temp
            #mark = [ row[0] for row in c.fetchall() if row[0] ] # i used this to return fetch the data without ()
            #return render_template('empty3.html', data = temp[0:4,2])

            lenth_assessments = len(assessment_name) # to get how many assessments std have taken so far
            zero = 0 # i used this variable in the bar_char_pdf.html
            lenth_std = len(std_id) # i used this variable in the bar_char_pdf.html
            #return render_template('empty3.html', data = lenth_std)

            # get std mark in all assessment
            query = "SELECT mark FROM student_grade where course_id=%s"
            values = course_id
            mark = c.execute(query, (values,))
            mark = c.fetchall()
            #mark = [ row[0] for row in c.fetchall() if row[0] ] # i used this to return fetch the data without ()
            #return render_template('empty3.html', data = mark)
            #here I convert list to array firs, then convert array element to str, and then i removed brackets from the element of the array
            mark = np.asarray(mark)
            mark = mark.astype(str)
            mark = [ row[0] for row in mark if row[0] ]
            # END OF here I convert list to array firs, then convert array element to str, and then i removed brackets from the element of the array
            #return render_template('empty3.html', data = mark)
            #mark = [ row[0] for row in c.fetchall() if row[0] ] # i used this to return fetch the data without ()

            #return render_template('empty3.html', data = mark)
            #return render_template('empty3.html', data = len(mark))



            # this block for the revision_plan of the last assessment
            #SELECT DISTINCT assessment_name FROM student_prediction_results where number_of_assessment_in_prediction='4';
            query = "SELECT DISTINCT assessment_name FROM student_prediction_results where number_of_assessment_in_prediction=%s and  course_id =%s"
            values = (lenth_assessments, course_id)
            cityList = c.execute(query, values)
            #number_of_assessment__predicted_so_far = c.fetchall()
            name_of_last_assessment = [ row[0] for row in c.fetchall() if row[0] ] # i used this to return fetch the data without ()



            #$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
            # this block for the revision_plan and CLOs assessment of the all the assessment done
            #SELECT DISTINCT assessment_name FROM student_prediction_results where number_of_assessment_in_prediction='4';
            query = "SELECT DISTINCT assessment_name FROM student_prediction_results where number_of_assessment_in_prediction<=%s and  course_id =%s order by number_of_assessment_in_prediction"
            values = (lenth_assessments, course_id)
            cityList = c.execute(query, values)
            #number_of_assessment__predicted_so_far = c.fetchall()
            list_of_assessments_done = [ row[0] for row in c.fetchall() if row[0] ] # i used this to return fetch the data without ()

            #return render_template('empty3.html', data = list_of_assessments_done)


            d_revision_plan = {} # to create a dictionary for the revision plan for each done assessment

            for user in list_of_assessments_done:
                query = "select allign_tla_to_at_m_to_m.tla_id, allign_tla_to_at_m_to_m.assessment_name, tla.tla_topic, tla.lecture_or_lab, tla.lecture_lab_number, tla.tla_Resources from  tla INNER JOIN allign_tla_to_at_m_to_m  ON tla.tla_id = allign_tla_to_at_m_to_m.tla_id where tla.course_course_id=%s and allign_tla_to_at_m_to_m.assessment_name=%s"
                #values = (course_id, course_id, name_of_last_assessment)
                values = (course_id, user)
                c.execute(query, values)
                data = c.fetchall()
                data = np.array(data)
                #print(data.shape)

                #d["Assessment {0}".format(i)] = data
                d_revision_plan["{0}".format(user)] = data

            #return render_template('empty3.html', data = d['Mid-semester quiz'])
            #return render_template('empty3.html', data = d)
            #return render_template('empty3.html', data = len(d))
            #return render_template('empty3.html', data = d['Mid-semester quiz'][0,4])
            #return render_template('empty3.html', data = d)

            clo_assessment = {} # to create a dictionary for all assessment clo done

            for user in list_of_assessments_done:
                query= "SELECT distinct assessment_name, clo_name  FROM allign_at_to_clo_m_to_m  where course_id=%s and  assessment_name=%s order by assessment_name;"
                #values = (course_id, course_id, name_of_last_assessment)
                values = (course_id, user)
                c.execute(query, values)
                data = c.fetchall()
                data = np.array(data)
                #print(data.shape)

                #d["Assessment {0}".format(i)] = data
                clo_assessment["{0}".format(user)] = data

            #return render_template('empty3.html', data = clo_assessment['Mid-semester quiz'])
            #return render_template('empty3.html', data = clo_assessment)
            #$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$



            if not name_of_last_assessment:
                return render_template('no_dashboard_yet.html', data = "NO Data to Show in the Dashboard Yet, Please Add Students Grades and Design Your Course First")


            name_of_last_assessment = name_of_last_assessment[0] # to conver list with one element to string
            #return render_template('empty3.html', data = name_of_last_assessment)

            #return render_template('empty3.html', data = name_of_last_assessment)
            #return render_template('empty3.html', data = mark % lenth_assessments)

            #if mark% lenth_assessments<100:

            #query = "select distinct allign_tla_to_clo_m_to_m.tla_id , allign_at_to_clo_m_to_m.assessment_name,  tla.tla_topic, tla.lecture_or_lab, tla.lecture_lab_number, tla.tla_Resources  from clo  INNER JOIN allign_at_to_clo_m_to_m  ON clo.clo_name = allign_at_to_clo_m_to_m.clo_name   INNER JOIN allign_tla_to_clo_m_to_m  ON clo.clo_name = allign_tla_to_clo_m_to_m.clo_name  INNER JOIN tla  ON allign_tla_to_clo_m_to_m.tla_id = tla.tla_id  where clo.course_course_id=%s and allign_at_to_clo_m_to_m.assessment_name=%s"
            #query = "select distinct allign_tla_to_clo_m_to_m.tla_id , allign_at_to_clo_m_to_m.assessment_name, tla.tla_topic, tla.lecture_or_lab, tla.lecture_lab_number, tla.tla_Resources from clo INNER JOIN allign_at_to_clo_m_to_m  ON clo.clo_name = allign_at_to_clo_m_to_m.clo_name INNER JOIN allign_tla_to_clo_m_to_m  ON clo.clo_name = allign_tla_to_clo_m_to_m.clo_name INNER JOIN tla  ON allign_tla_to_clo_m_to_m.tla_id = tla.tla_id  where  allign_at_to_clo_m_to_m.assessment_name=%s and allign_tla_to_clo_m_to_m.course_id=%s"
            #values = (name_of_last_assessment, course_id)
            #query = "select distinct allign_tla_to_clo_m_to_m.tla_id , allign_at_to_clo_m_to_m.assessment_name, tla.tla_topic, tla.lecture_or_lab, tla.lecture_lab_number, tla.tla_Resources from clo INNER JOIN allign_at_to_clo_m_to_m  ON clo.clo_name = allign_at_to_clo_m_to_m.clo_name INNER JOIN allign_tla_to_clo_m_to_m  ON clo.clo_name = allign_tla_to_clo_m_to_m.clo_name INNER JOIN tla  ON allign_tla_to_clo_m_to_m.tla_id = tla.tla_id  where  allign_tla_to_clo_m_to_m.course_id=%s and allign_at_to_clo_m_to_m.course_id=%s and allign_at_to_clo_m_to_m.assessment_name=%s"
            query = "select allign_tla_to_at_m_to_m.tla_id, allign_tla_to_at_m_to_m.assessment_name, tla.tla_topic, tla.lecture_or_lab, tla.lecture_lab_number, tla.tla_Resources from  tla INNER JOIN allign_tla_to_at_m_to_m  ON tla.tla_id = allign_tla_to_at_m_to_m.tla_id where tla.course_course_id=%s and allign_tla_to_at_m_to_m.assessment_name=%s"
            #values = (course_id, course_id, name_of_last_assessment)
            values = (course_id, name_of_last_assessment)
            #cityList = c.execute(query, values)
            #revision_plan = c.fetchall()
            #return render_template('empty3.html', data = revision_plan)


            if not d_revision_plan:
               return render_template('no_dashboard_yet.html', data = "NO Data to Show in the Dashboard Yet, Please Add Students Grades and Design Your Course First")
            #else:
            #    revision_plan = ""

            #return render_template('empty3.html', data = revision_plan)

            # END OF this block for the revision_plan of the last assessment

            # GET CLOs Name for current assessment
            #query= "SELECT  distinct assessment_name,  tla.clo_name FROM at_map_to_tla  INNER JOIN tla  ON at_map_to_tla.tla_id = tla.tla_id  WHERE at_map_to_tla.course_course_id=%s and assessment_name=%s order by at_map_to_tla.assessment_name"
            query= "SELECT distinct assessment_name, clo_name  FROM allign_at_to_clo_m_to_m  where course_id=%s and  assessment_name=%s order by assessment_name;"
            values=(course_id, name_of_last_assessment)
            #clo_assessment = c.execute(query, values)
            #number_of_assessment__predicted_so_far = c.fetchall()
            #clo_assessment= c.fetchall()
            #return render_template('empty3.html', data = clo_assessment)
            # END OF GET CLOs Name for current assessment


            # total collected mark
            query = "SELECT student_id, ROUND(sum(unconverted_mark ),2)  'achieved', ROUND(sum(lost_mark ),2)  'unachieved', ROUND(100 - (sum(unconverted_mark ) + sum(lost_mark )),2)  'remained'  FROM student_grade where course_id=%s group by student_id"
            values = (course_id)
            cityList = c.execute(query, (values,))
            #cityList = [ row[0] for row in c.fetchall() if row[0] ] # i used this to return fetch the data without ()
            cityList = c.fetchall()
            cityList = np.asarray(cityList)
            achieved = cityList[:,1]
            unachieved = cityList[:,2]
            remained = cityList[:,3]
            #if collected:
             #   collected=float(collected[1])
            #else:
             #   collected=0

            #return render_template('empty3.html', data = achieved)
            # END OF total collected mark

            # this block to get students mark in the current assessment
            #query = "SELECT student_id, unconverted_mark , ROUND((unconverted_mark  + lost_mark ),2) 'out of',   mark '%' FROM student_grade where course_id=%s and assessment_name=%s group by student_id"
            #query = "SELECT student_id, ROUND(unconverted_mark,1)  , ROUND((unconverted_mark  + lost_mark ),2) 'out of',   mark '%' FROM student_grade where course_id=%s and assessment_name=%s group by student_id"
            query = "SELECT student_id, ROUND(unconverted_mark,1)  , ROUND((unconverted_mark  + lost_mark ),1) 'out of',   ROUND(mark,1) '%' FROM student_grade where course_id=%s and assessment_name=%s group by student_id"
            values = (course_id, name_of_last_assessment)
            c.execute(query, values)
            #cityList = [ row[0] for row in c.fetchall() if row[0] ] # i used this to return fetch the data without ()
            cityList = c.fetchall()
            cityList = np.asarray(cityList)
            unconverted_mark = cityList[:,1]
            mark_out_of = cityList[:,2]
            mark_percentage = cityList[:,3]
            #return render_template('empty3.html', data = unconverted_mark)

            #END OF this block to get students mark in the current assessment


            # get std name and id from student_prediction_results order by prediction results to show at-risk std first in checkbox
            query = "SELECT  student_prediction_results.student_id, current_student.student_name FROM student_prediction_results inner join  current_student on  current_student.student_id= student_prediction_results.student_id where number_of_assessment_in_prediction=%s and  student_prediction_results.course_id =%s and current_student.course_id=%s order by Binary_prediction_results, Multiclass_prediction_results"
            values = (lenth_assessments, course_id, course_id)
            c.execute(query, values)
            std_name_and_id_ = c.fetchall()

            std_name_and_id_ = np.array(std_name_and_id_)


            #std_name_and_id_ = [ row[0] for row in c.fetchall() if row[0] ] # i used this to return fetch the data without ()
            #return render_template('empty3.html', data = std_name_and_id_[:,0])
            # END OF get std name and id from student_prediction_results order by prediction results to show at-risk std first in checkbox






            return render_template('bar_chart_pdf.html', title='Student Dashboard', max=100, labels=assessment_name, values=mark,\
                                   course_id=course_id, course_name = course_name,
                                   assessment_name = assessment_name,\
                                           std_id=std_id, std_name = std_name, lenth_std = lenth_std, std_id_and_name = std_id_and_name,\
                                           lenth_assessments = lenth_assessments, zero=zero,

                                           name_of_last_assessment = name_of_last_assessment, list_of_assessments_done = list_of_assessments_done,
                                           clo_assessment = clo_assessment,
                                           achieved = achieved, unachieved = unachieved, remained = remained,\
                                           unconverted_mark = unconverted_mark, mark_out_of = mark_out_of, mark_percentage = mark_percentage,
                                           d_revision_plan = d_revision_plan,
                                           std_name_and_id_ = std_name_and_id_
                                           )

        except sql.Error as e: # if error
            # then display the error in 'database_error.html' page
            return render_template('database_error.html', error=e)

        finally:
            con.close() # close the connection





#NNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNN

#SSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSS

#tr_dashboard.py

#\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\design_course\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
#this is the Get method to aviod two dynamic dropdown lists. Design a Course
@app.route('/tr_dashboard_choose_course', methods=['GET', 'Post'])
@login_required
def tr_dashboard_choose_course():
    if request.method == 'GET':
        try:
            con = sql.connect(host="pythonanywhere_host", user="pythonanywhere_user", password="pythonanywhere_password", database="pythonanywhere$database_name") #this is not the real connections details
            c =  con.cursor() # cursor
            #query = "Select * from course where userName=%s"
            query = "Select * from course_and_models where userName=%s"
            values = session["USERNAME"]
            cityList = c.execute(query, (values,))
            cityList = c.fetchall()

            return render_template('tr_dashboard_choose_course.html', cityList=cityList)

        except sql.Error as e: # if error
            # then display the error in 'database_error.html' page
            return render_template('database_error.html', error=e)

        finally:
            con.close() # close the connection

    #else: # request.method == 'POST':
     #   courseName = request.form['course_course_id']
      #  return render_template('create_clo.html', courseName=courseName)


#\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\End OF design_course\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\

#this is for just to avoid two dynamic dropdown lists. this is the POST method from the Get method above: design_course
@app.route('/tr_dashboard_first',methods=['POST'])
@login_required
def tr_dashboard_first():

    #courseName = request.args.get('my_var')
    #return render_template('empty3.html', data = courseName)


    courseName = request.form['course_course_id']
    #return render_template('empty3.html', data = courseName)



    #courseName=courseName
    try:
        con = sql.connect(host="pythonanywhere_host", user="pythonanywhere_user", password="pythonanywhere_password", database="pythonanywhere$database_name") #this is not the real connections details
        c =  con.cursor() # cursor

        query = "Select distinct assessment_name from student_grade where course_id=%s"
        values = courseName
        cityList = c.execute(query, (values,))
        #labels = c.fetchall()
        assessment_name = [ row[0] for row in c.fetchall() if row[0] ] # i used this to return fetch the data without ()
        #return render_template('empty3.html', data = assessment_name)


        #here i want to get the average std mark in each assessment
        average_mark_of_each_assessment= []
        assessment_name_list=[]
        for i in assessment_name:
            query = "SELECT ROUND(avg(mark),2), assessment_name FROM student_grade where assessment_name=%s and course_id=%s"
            values = (i, courseName)
            cityList = c.execute(query, values)
            values = c.fetchall()
            #values = [ row[0] for row in c.fetchall() if row[0] ] # i used this to return fetch the data without ()
            values=values[0]
            assessment_name=values[1] # to append all assessment_name in a list
            average_mark_of_each_assessment.append(values[0]) # to append all mark in a list
            assessment_name_list.append(values[1])

        #return render_template('empty3.html', data = assessment_name_list )

        #END OF here i want to get the average std mark in each assessment



        colors = [
            "#F7464A", "#46BFBD", "#FDB45C", "#FEDCBA",
            "#ABCDEF", "#DDDDDD", "#ABCABC", "#4169E1",
            "#C71585", "#FF4500", "#FEDCBA", "#46BFBD"]

        bar_labels=assessment_name_list
        bar_values=average_mark_of_each_assessment


        #return render_template('empty3.html', data = assessment_name)


        # to get the assessment name to show in the html file to tell student the prediction result after this assessment

        query = "SELECT count(DISTINCT assessment_name) FROM student_grade where course_id=%s"
        values = courseName
        cityList = c.execute(query, (values,))
        #number_of_assessment__predicted_so_far = c.fetchall()
        number_of_assessment__predicted_so_far = [ row[0] for row in c.fetchall() if row[0] ] # i used this to return fetch the data without ()

        if not number_of_assessment__predicted_so_far:
            return render_template('no_dashboard_yet.html', data = "NO Data to show in the Dashboard Yet, Please Create Mapping Model, Prediction model, and add Student Data")


        number_of_assessment__predicted_so_far = number_of_assessment__predicted_so_far[0] # to conver list with one element to string


        query = "Select assessment_name from student_prediction_results where course_id=%s and number_of_assessment_in_prediction=%s "
        values = (courseName,number_of_assessment__predicted_so_far)

        cityList = c.execute(query, values)
        #labels = c.fetchall()
        assessment_name_of_last_prediciton = [ row[0] for row in c.fetchall() if row[0] ] # i used this to return fetch the data without ()

        if not assessment_name_of_last_prediciton:
            return render_template('no_dashboard_yet.html', data = "NO Data to show in the Dashboard Yet, Please Create Mapping Model, Prediction model, and add Student Data")


        assessment_name_of_last_prediciton = assessment_name_of_last_prediciton[0]
        # END OF to get the assessment name to show in the html file to tell student the prediction result after this assessment


        query = "SELECT distinct t1.student_id, t2.student_name FROM student_prediction_results t1 INNER JOIN current_student t2 ON t1.student_id = t2.student_id  where t1.course_id=%s and t1.number_of_assessment_in_prediction=%s and (t1.Multiclass_prediction_results='at_risk' or t1.Multiclass_prediction_results='borderline'or t1.Binary_prediction_results='0')"
        values = (courseName, number_of_assessment__predicted_so_far)
        at_risk_std_name_and_id = c.execute(query, values)
        at_risk_std_name_and_id = c.fetchall()
        #return render_template('empty3.html', data = at_risk_std_name_and_id)

        #pie_chart


        query = "SELECT assessment_name, count(student_id) FROM student_grade where course_id=%s and mark<50 group by assessment_name"
        values = courseName
        pie_data = c.execute(query, (values,))
        pie_data = c.fetchall()




        colors = [
                "#F7464A", "#46BFBD", "#FDB45C", "#FEDCBA",
                "#ABCDEF", "#DDDDDD", "#ABCABC", "#4169E1",
                "#C71585", "#FF4500", "#FEDCBA", "#46BFBD"]

        pie_data = np.array(pie_data)

        pie_labels = pie_data[:,0]
        pie_values = pie_data[:,1]
        #return render_template('empty3.html', data = pie_values)
        #return render_template('pie_chart.html', title='Bitcoin Monthly Price in USD', max=17000, set=zip(values, labels, colors))

        #END OF pie_chart



        #box plot
        query = "select mark from student_grade where assessment_name=%s and course_id=%s"
        values = (assessment_name_of_last_prediciton, courseName)
        box = c.execute(query, values)
        #box = c.fetchall()
        box = [ row[0] for row in c.fetchall() if row[0] ] # i used this to return fetch the data without ()
        #return render_template('empty3.html', data = box)
        #return render_template('pie_chart2.html', box = box, assessment_name_of_last_prediciton=assessment_name_of_last_prediciton)


        #END OF box plot



        # to get CLO for the assessnemt name
        #query= "SELECT  distinct assessment_name,  tla.clo_name FROM at_map_to_tla  INNER JOIN tla  ON at_map_to_tla.tla_id = tla.tla_id  WHERE at_map_to_tla.course_course_id=%s and assessment_name=%s order by at_map_to_tla.assessment_name"
        query= "SELECT distinct assessment_name, clo_name  FROM allign_at_to_clo_m_to_m  where course_id=%s and  assessment_name=%s order by assessment_name;"
        values=(courseName, assessment_name_of_last_prediciton)
        clo_assessment = c.execute(query, values)
        #number_of_assessment__predicted_so_far = c.fetchall()
        clo_assessment= c.fetchall()

        clo_assessment = np.array(clo_assessment) # list to array to get only the clo_name
        clo_assessment= clo_assessment[:,1] #to get only the clo_name
        #return render_template('empty3.html', data = clo_assessment )

        # END OF to get CLO for the assessnemt name

        # to get Course name
        #query= "SELECT  distinct assessment_name,  tla.clo_name FROM at_map_to_tla  INNER JOIN tla  ON at_map_to_tla.tla_id = tla.tla_id  WHERE at_map_to_tla.course_course_id=%s and assessment_name=%s order by at_map_to_tla.assessment_name"
        query= "SELECT course_name FROM course where course_id=%s"
        values=(courseName)
        c.execute(query, (values,))
        #number_of_assessment__predicted_so_far = c.fetchall()
        course_name_not_id=  [ row[0] for row in c.fetchall() if row[0] ]

        #return render_template('empty3.html', data = course_name_not_id )

        # END OF to get course name


        return render_template('tr_dashboard.html', title='Teacher Dashboard', max=100, labels=bar_labels, values=bar_values,\
                               courseName=courseName,\
                                   assessment_name_of_last_prediciton = assessment_name_of_last_prediciton,\
                                       at_risk_std_name_and_id= at_risk_std_name_and_id,\
                                           set=zip(pie_values, pie_labels, colors),\
                                               box = box,\
                                               clo_assessment = clo_assessment, course_name_not_id = course_name_not_id [0])
        #return render_template('tr_dashboard.html', course_id=courseName, cityList=assessment_name, std_id=std_id)

    except sql.Error as e: # if error
        # then display the error in 'database_error.html' page
        return render_template('database_error.html', error=e)

    finally:

        con.close() # close the connection


    #return render_template('create_clo.html', courseName=courseName)

@app.route('/tr_dashboard_d2', methods=['GET', 'Post'])
@login_required
def tr_dashboard_d2():

    assessment_name = request.args.get('my_var')
    courseName = request.args.get('my_var2')

    try:
        con = sql.connect(host="pythonanywhere_host", user="pythonanywhere_user", password="pythonanywhere_password", database="pythonanywhere$database_name") #this is not the real connections details
        c =  con.cursor() # cursor

        #box plot
        query = "select mark from student_grade where assessment_name=%s and course_id=%s"
        values = (assessment_name, courseName)
        box = c.execute(query, values)
        #box = c.fetchall()
        box = [ row[0] for row in c.fetchall() if row[0] ] # i used this to return fetch the data without ()
        #return render_template('empty3.html', data = assessment_name)
        #return render_template('pie_chart2.html', box = box, assessment_name_of_last_prediciton=assessment_name_of_last_prediciton)

        #END OF box plot

        # to get at_risk Std Name & id for spesific <<assessment_name>>
        query = "SELECT distinct t1.student_id, t2.student_name  FROM student_prediction_results t1  INNER JOIN current_student t2 ON t1.student_id = t2.student_id   where t1.course_id=%s and t1.assessment_name=%s and (t1.Multiclass_prediction_results='at_risk' or t1.Multiclass_prediction_results='borderline'or t1.Binary_prediction_results='0')"
        values = (courseName, assessment_name)
        at_risk_std_name_and_id = c.execute(query, values)
        at_risk_std_name_and_id = c.fetchall()
        #return render_template('empty3.html', data = at_risk_std_name_and_id)

        #END OF to get at_risk Std Name & id for spesific <<assessment_name>>

        #std who recive <50 in the assessment_name
        query = "SELECT distinct t1.student_id, t2.student_name FROM student_grade t1 INNER JOIN current_student t2 ON t1.student_id = t2.student_id  where t1.assessment_name=%s and t1.course_id=%s and t1.mark<50"
        values = (assessment_name, courseName)
        std_name_and_id_less_50 = c.execute(query, values)
        std_name_and_id_less_50 = c.fetchall()

        #return render_template('empty3.html', data = std_name_and_id_less_50)
        #END OF std who recive <50 in the assessment_name

        # to get CLO for the assessnemt name
        #query= "SELECT  distinct assessment_name,  tla.clo_name FROM at_map_to_tla  INNER JOIN tla  ON at_map_to_tla.tla_id = tla.tla_id  WHERE at_map_to_tla.course_course_id=%s and assessment_name=%s order by at_map_to_tla.assessment_name"
        query= "SELECT distinct assessment_name, clo_name  FROM allign_at_to_clo_m_to_m  where course_id=%s and  assessment_name=%s order by assessment_name;"
        values=(courseName, assessment_name)
        clo_assessment = c.execute(query, values)
        #number_of_assessment__predicted_so_far = c.fetchall()
        clo_assessment= c.fetchall()

        clo_assessment = np.array(clo_assessment) # list to array to get only the clo_name
        clo_assessment= clo_assessment[:,1] #to get only the clo_name
        #return render_template('empty3.html', data = clo_assessment )

        # END OF to get CLO for the assessnemt name

        # to get Course name
        query= "SELECT course_name FROM course where course_id=%s"
        values=(courseName)
        c.execute(query, (values,))
        #number_of_assessment__predicted_so_far = c.fetchall()
        course_name_not_id=  [ row[0] for row in c.fetchall() if row[0] ]

        #return render_template('empty3.html', data = course_name_not_id )

        # END OF to get course name


        return render_template('tr_dashboard_d2.html', assessment_name=assessment_name,\
                                courseName=courseName, course_name_not_id = course_name_not_id, \
                                box=box,\
                                at_risk_std_name_and_id=at_risk_std_name_and_id,\
                                std_name_and_id_less_50=std_name_and_id_less_50,\
                                clo_assessment=clo_assessment)


    except sql.Error as e: # if error
        # then display the error in 'database_error.html' page
        return render_template('database_error.html', error=e)

    finally:

        con.close() # close the connection


#NNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNN

#SSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSS


#tr_d3.py

@app.route('/tr_dashboard_d3_students_detail', methods=['GET', 'Post'])
@login_required
def tr_dashboard_d3_students_detail():
    if request.method == 'GET':

        #std_id=session["USERNAME"]


        std_id = request.args.get('my_var')
        course_id = request.args.get('my_var2')

        std_name = request.args.get('my_var3')

        #return render_template('empty3.html', data = std_id)
        #this block for the barchart
        try:
            con = sql.connect(host="pythonanywhere_host", user="pythonanywhere_user", password="pythonanywhere_password", database="pythonanywhere$database_name") #this is not the real connections details
            c =  con.cursor() # cursor

            if not std_id:
                query = "SELECT student_id FROM current_student where student_name=%s and course_id=%s"
                values = (std_name, course_id)
                cityList = c.execute(query, values)
                #course_id = c.fetchall()
                std_id = [ row[0] for row in c.fetchall() if row[0] ] # i used this to return fetch the data without ()
                std_id=std_id[0]

            query = "Select assessment_name from student_grade where student_id=%s and course_id =%s "
            values = (std_id, course_id)
            cityList = c.execute(query, values)
            #labels = c.fetchall()
            labels = [ row[0] for row in c.fetchall() if row[0] ] # i used this to return fetch the data without ()
            #labels=type(labels)
            #return render_template('empty3.html', data = labels)


            query = "Select mark from student_grade where student_id=%s and course_id=%s"
            values = (std_id, course_id)
            cityList = c.execute(query, values)
            #values = c.fetchall()
            bar_values = [ row[0] for row in c.fetchall() if row[0] ] # i used this to return fetch the data without ()
            #return render_template('empty3.html', data = values)


            #here i want to get the average std mark in each assessment
            average_mark_of_each_assessment= []
            assessment_name_list=[]
            for i in labels:
                query = "SELECT ROUND(avg(mark),2), assessment_name FROM student_grade where assessment_name=%s and course_id=%s"
                values = (i, course_id)
                cityList = c.execute(query, values)
                values = c.fetchall()
                #values = [ row[0] for row in c.fetchall() if row[0] ] # i used this to return fetch the data without ()
                values=values[0]
                #values = np.asarray(values[0])
                #values = values.astype(float)
                #values="{0:.2f}".format(values[0])
                #values[0] = "{:.2f}".format(str)




                #values = round(values, 2)
                #values=format(values, ".1f")
                #values=float(values)
                #float("{:.2f}".format(values))
                #values = "{:.2f}".format(values)
                assessment_name=values[1] # to append all assessment_name in a list
                average_mark_of_each_assessment.append(values) # to append all mark in a list
                #assessment_name_list.append(assessment_name)

            #average_mark_of_each_assessment_array=np.asarray(average_mark_of_each_assessment)
            #list3 = average_mark_of_each_assessment + assessment_name_list
            #average_mark_of_each_assessment=type(average_mark_of_each_assessment)
            #return render_template('empty3.html', data = average_mark_of_each_assessment_array[1])

            #END OF here i want to get the average std mark in each assessment


        except sql.Error as e: # if error
            # then display the error in 'database_error.html' page
            return render_template('database_error.html', error=e)

        finally:
            con.close() # close the connection


        if not labels:
           return render_template('empty3.html', data = "NO Data to show in the Dashboard Yet, Please Come Back Another Time")

        colors = [
            "#F7464A", "#46BFBD", "#FDB45C", "#FEDCBA",
            "#ABCDEF", "#DDDDDD", "#ABCABC", "#4169E1",
            "#C71585", "#FF4500", "#FEDCBA", "#46BFBD"]

        bar_labels=labels
        bar_values=bar_values

        # END OF this block for the barchart

        # this block to get Course name
        try:


            con = sql.connect(host="pythonanywhere_host", user="pythonanywhere_user", password="pythonanywhere_password", database="pythonanywhere$database_name") #this is not the real connections details
            c =  con.cursor() # cursor


            query= "SELECT course_name FROM course where course_id=%s"
            values=(course_id)
            c.execute(query, (values,))
            #number_of_assessment__predicted_so_far = c.fetchall()
            course_name_not_id=  [ row[0] for row in c.fetchall() if row[0] ]

            #return render_template('empty3.html', data = course_name_not_id )

            # END OF to get course name

        except sql.Error as e: # if error
            # then display the error in 'database_error.html' page
            return render_template('database_error.html', error=e)

        finally:
            con.close() # close the connection

        # END OF this block to get Course name


        #this block for prediction results
        try:


            con = sql.connect(host="pythonanywhere_host", user="pythonanywhere_user", password="pythonanywhere_password", database="pythonanywhere$database_name") #this is not the real connections details
            c =  con.cursor() # cursor

            query = "SELECT count(DISTINCT assessment_name) FROM student_grade where course_id =%s"
            values = course_id
            cityList = c.execute(query, (values,) )
            #number_of_assessment__predicted_so_far = c.fetchall()
            number_of_assessment__predicted_so_far = [ row[0] for row in c.fetchall() if row[0] ] # i used this to return fetch the data without ()
            number_of_assessment__predicted_so_far = number_of_assessment__predicted_so_far[0] # to conver list with one element to string


            #number_of_assessment__predicted_so_far=int(number_of_assessment__predicted_so_far)
            #return render_template('empty3.html', data = number_of_assessment__predicted_so_far)

            # to get the assessment name to show in the html file to tell student the prediction result after this assessment
            query = "Select assessment_name from student_prediction_results where student_id=%s and number_of_assessment_in_prediction=%s and course_id =%s"
            values = (std_id,number_of_assessment__predicted_so_far, course_id)

            cityList = c.execute(query, values)
            #labels = c.fetchall()
            assessment_name_of_last_prediciton = [ row[0] for row in c.fetchall() if row[0] ] # i used this to return fetch the data without ()

            assessment_name_of_last_prediciton = assessment_name_of_last_prediciton[0]
            #return render_template('empty3.html', data = assessment_name_of_last_prediciton)
            # END OF to get the assessment name to show in the html file to tell student the prediction result after this assessment


            query = "Select Binary_prediction_results from student_prediction_results where student_id=%s and number_of_assessment_in_prediction=%s and course_id=%s"
            values = (std_id, number_of_assessment__predicted_so_far, course_id)

            cityList = c.execute(query, values)
            #labels = c.fetchall()
            Binary_prediction_results = [ row[0] for row in c.fetchall() if row[0] ] # i used this to return fetch the data without ()

            Binary_prediction_results=Binary_prediction_results[0]

            if Binary_prediction_results==0:
                Binary_prediction_results="At Risk"
            else:
                Binary_prediction_results="Not At Risk"

            #labels=type(labels)
            #return render_template('empty3.html', data = Binary_prediction_results)


            query = "Select Multiclass_prediction_results from student_prediction_results where student_id=%s and number_of_assessment_in_prediction=%s and course_id=%s"
            values = (std_id,number_of_assessment__predicted_so_far, course_id)
            cityList = c.execute(query, values)
            #values = c.fetchall()
            Multiclass_prediction_results = [ row[0] for row in c.fetchall() if row[0] ] # i used this to return fetch the data without ()
            Multiclass_prediction_results=Multiclass_prediction_results[0]
            #return render_template('empty3.html', data = Multiclass_prediction_results)

            #return render_template('design_course.html', cityList=cityList)

        except sql.Error as e: # if error
            # then display the error in 'database_error.html' page
            return render_template('database_error.html', error=e)

        finally:
            con.close() # close the connection
        #END OF this block for prediction results



        #this block for Tutor Comment
        try:


            con = sql.connect(host="pythonanywhere_host", user="pythonanywhere_user", password="pythonanywhere_password", database="pythonanywhere$database_name") #this is not the real connections details
            c =  con.cursor() # cursor








        except sql.Error as e: # if error
            # then display the error in 'database_error.html' page
            return render_template('database_error.html', error=e)

        finally:
            con.close() # close the connection
        #END OF this block for Tutor Comment


        # this block for revision plan
        try:

            #number_of_assessment__predicted_so_far

            con = sql.connect(host="pythonanywhere_host", user="pythonanywhere_user", password="pythonanywhere_password", database="pythonanywhere$database_name") #this is not the real connections details
            c =  con.cursor() # cursor

            #SELECT DISTINCT assessment_name FROM student_prediction_results where number_of_assessment_in_prediction='4';
            #query = "SELECT DISTINCT assessment_name FROM student_prediction_results where number_of_assessment_in_prediction=%s"
            #values = number_of_assessment__predicted_so_far
            #cityList = c.execute(query, (values,))
            query = "SELECT DISTINCT assessment_name FROM student_prediction_results where number_of_assessment_in_prediction=%s and  course_id =%s"
            values = (number_of_assessment__predicted_so_far, course_id)
            cityList = c.execute(query, values)
            #number_of_assessment__predicted_so_far = c.fetchall()
            name_of_last_assessment = [ row[0] for row in c.fetchall() if row[0] ] # i used this to return fetch the data without ()
            name_of_last_assessment = name_of_last_assessment[0] # to conver list with one element to string

            #return render_template('empty3.html', data = name_of_last_assessment)

            #to get course id from student_grade
            #SELECT DISTINCT course_id FROM student_grade where student_id='c3301209';
            query = "SELECT DISTINCT course_id FROM student_grade where student_id=%s and assessment_name=%s and course_id=%s"
            values = (std_id, name_of_last_assessment, course_id)
            cityList = c.execute(query, values)
            #course_id = c.fetchall()
            course_id = [ row[0] for row in c.fetchall() if row[0] ] # i used this to return fetch the data without ()
            course_id = course_id[0] # to conver list with one element to string
            #return render_template('empty3.html', data = course_id)

            #END OF to get course id from student_grade

            query = "SELECT mark FROM student_grade where student_id=%s and course_id=%s and assessment_name=%s"
            values = (std_id, course_id, assessment_name_of_last_prediciton)
            cityList = c.execute(query, values)
            #std_mark_in_last_predicted_assessment = [ row[0] for row in c.fetchall() if row[0] ] # i used this to return fetch the data without ()
            std_mark_in_last_predicted_assessment = c.fetchall()
            std_mark_in_last_predicted_assessment = std_mark_in_last_predicted_assessment[0] # to conver list with one element to string
            #if std_mark_in_last_predicted_assessment[0]=='0':
             #   f=0

            #std_mark_in_last_predicted_assessment=int(std_mark_in_last_predicted_assessment)
            #return render_template('empty3.html', data = std_mark_in_last_predicted_assessment[0])

            # to get std name from current student table
            query = "SELECT student_name FROM current_student where student_id=%s and course_id=%s"
            values = (std_id, course_id)
            cityList = c.execute(query, values)
            std_name = [ row[0] for row in c.fetchall() if row[0] ] # i used this to return fetch the data without ()
            std_name = std_name[0] # to conver list with one element to string
            #END OF to get std name from current student table

            #this block is for bar chart that show achieved and unachieved mark

            query = "SELECT assessment_name, unconverted_mark , lost_mark FROM student_grade where student_id=%s and course_id=%s group by assessment_name"
            values = (std_id, course_id)
            cityList = c.execute(query, values)
            cityList = c.fetchall()

            cityList = np.asarray(cityList)
            labels = cityList[:,0]
            got = cityList[:,1]
            lost = cityList[:,2]
            #return render_template('empty3.html', data = labels)
            #return render_template('empty3.html', data = got)
            #return render_template('empty3.html', data = lost)

            # total collected mark
            query = "SELECT ROUND(sum(unconverted_mark),1) 'collected' FROM student_grade where student_id=%s and course_id=%s"
            values = (std_id, course_id)
            cityList = c.execute(query, values)
            cityList = [ row[0] for row in c.fetchall() if row[0] ] # i used this to return fetch the data without ()
            #cityList = c.fetchall()
            #cityList = np.asarray(cityList)
            collected = cityList
            if collected:
                collected=float(collected[0])
            else:
                collected=0


            #END OF this block is for bar chart that show achieved and unachieved mark


            if std_mark_in_last_predicted_assessment[0]<100:
                #query = "SELECT t1.course_course_id, t1.assessment_name, t2.lecture_or_lab, t2.lecture_lab_number, t2.tla_topic  FROM at_map_to_tla t1  INNER JOIN tla t2 ON t1.tla_id = t2.tla_id WHERE t1.course_course_id= %s and assessment_name= %s"
                #query = "select distinct allign_tla_to_clo_m_to_m.tla_id , allign_at_to_clo_m_to_m.assessment_name,  tla.tla_topic, tla.lecture_or_lab, tla.lecture_lab_number, tla.tla_Resources  from clo  INNER JOIN allign_at_to_clo_m_to_m  ON clo.clo_name = allign_at_to_clo_m_to_m.clo_name   INNER JOIN allign_tla_to_clo_m_to_m  ON clo.clo_name = allign_tla_to_clo_m_to_m.clo_name  INNER JOIN tla  ON allign_tla_to_clo_m_to_m.tla_id = tla.tla_id  where clo.course_course_id=%s and allign_at_to_clo_m_to_m.assessment_name=%s"
                #values = (course_id,name_of_last_assessment)
                #query = "select distinct allign_tla_to_clo_m_to_m.tla_id , allign_at_to_clo_m_to_m.assessment_name,  tla.tla_topic, tla.lecture_or_lab, tla.lecture_lab_number, tla.tla_Resources  from clo  INNER JOIN allign_at_to_clo_m_to_m  ON clo.clo_name = allign_at_to_clo_m_to_m.clo_name   INNER JOIN allign_tla_to_clo_m_to_m  ON clo.clo_name = allign_tla_to_clo_m_to_m.clo_name  INNER JOIN tla  ON allign_tla_to_clo_m_to_m.tla_id = tla.tla_id  where clo.course_course_id=%s and allign_at_to_clo_m_to_m.assessment_name=%s"
                #query = "select distinct allign_tla_to_clo_m_to_m.tla_id , allign_at_to_clo_m_to_m.assessment_name, tla.tla_topic, tla.lecture_or_lab, tla.lecture_lab_number, tla.tla_Resources from clo INNER JOIN allign_at_to_clo_m_to_m  ON clo.clo_name = allign_at_to_clo_m_to_m.clo_name INNER JOIN allign_tla_to_clo_m_to_m  ON clo.clo_name = allign_tla_to_clo_m_to_m.clo_name INNER JOIN tla  ON allign_tla_to_clo_m_to_m.tla_id = tla.tla_id  where  allign_at_to_clo_m_to_m.assessment_name=%s and allign_tla_to_clo_m_to_m.course_id=%s"
                #values = (name_of_last_assessment, course_id)
                #query = "select distinct allign_tla_to_clo_m_to_m.tla_id , allign_at_to_clo_m_to_m.assessment_name, tla.tla_topic, tla.lecture_or_lab, tla.lecture_lab_number, tla.tla_Resources from clo INNER JOIN allign_at_to_clo_m_to_m  ON clo.clo_name = allign_at_to_clo_m_to_m.clo_name INNER JOIN allign_tla_to_clo_m_to_m  ON clo.clo_name = allign_tla_to_clo_m_to_m.clo_name INNER JOIN tla  ON allign_tla_to_clo_m_to_m.tla_id = tla.tla_id  where  allign_tla_to_clo_m_to_m.course_id=%s and allign_at_to_clo_m_to_m.course_id=%s and allign_at_to_clo_m_to_m.assessment_name=%s"
                query = "select allign_tla_to_at_m_to_m.tla_id, allign_tla_to_at_m_to_m.assessment_name, tla.tla_topic, tla.lecture_or_lab, tla.lecture_lab_number, tla.tla_Resources from  tla INNER JOIN allign_tla_to_at_m_to_m  ON tla.tla_id = allign_tla_to_at_m_to_m.tla_id where tla.course_course_id=%s and allign_tla_to_at_m_to_m.assessment_name=%s"
                values = (course_id, name_of_last_assessment)
                cityList = c.execute(query, values)
                revision_plan = c.fetchall()

            else:
                #revision_plan='your mark is > 50%, thus no revision plan needed'
                revision_plan=' '
                return render_template('tr_dashboard_bar_chart_no_revision_plan.html', title='Student Dashboard', max=100, labels=bar_labels, values=bar_values,\
                               Multiclass_prediction_results=Multiclass_prediction_results, Binary_prediction_results=Binary_prediction_results,\
                               revision_plan=revision_plan,\
                                   assessment_name_of_last_prediciton=assessment_name_of_last_prediciton,
                                   course_id=course_id, std_name=std_name,\
                                   average_mark_of_each_assessment=average_mark_of_each_assessment,\

                                           std_id=std_id,
                                                 got=got,
                                                     lost=lost,
                                                            collected=collected, lost2=100-collected)

            #revision_plan = [ row[0] for row in c.fetchall() if row[0] ] # i used this to return fetch the data without ()
            #number_of_assessment__predicted_so_far = number_of_assessment__predicted_so_far[0] # to conver list with one element to string
            #return render_template('empty3.html', data = revision_plan)

            #number_of_assessment__predicted_so_far=int(number_of_assessment__predicted_so_far)
            #return render_template('empty3.html', data = number_of_assessment__predicted_so_far)



        except sql.Error as e: # if error
            # then display the error in 'database_error.html' page
            return render_template('database_error.html', error=e)

        finally:
            con.close() # close the connection

        # END OF this block for revision plan





        return render_template('tr_dashboard_bar_chart.html', title='Student Dashboard', max=100, labels=bar_labels, values=bar_values,\
                               Multiclass_prediction_results=Multiclass_prediction_results, Binary_prediction_results=Binary_prediction_results,\
                               revision_plan=revision_plan,\
                                   assessment_name_of_last_prediciton=assessment_name_of_last_prediciton,
                                   course_id=course_id, std_name=std_name, course_name_not_id = course_name_not_id,\
                                   average_mark_of_each_assessment=average_mark_of_each_assessment,\

                                           std_id=std_id,
                                                 got=got,
                                                     lost=lost,
                                                            collected=collected, lost2=100-collected)




@app.route('/tr_dashboard_d3_students_detail_2', methods=['GET', 'Post'])
@login_required
def tr_dashboard_d3_students_detail_2():

    #assessment_name = request.args.get('my_var', None)
    #return render_template('empty3.html', data = my_var)
    assessment_name = request.args.get('my_var')

    std_name = request.args.get('my_var2')
    #std_id=session["USERNAME"]

    try:


        con = sql.connect(host="pythonanywhere_host", user="pythonanywhere_user", password="pythonanywhere_password", database="pythonanywhere$database_name") #this is not the real connections details
        c =  con.cursor() # cursor

        query = "SELECT student_id FROM current_student where student_name=%s"
        values = std_name
        cityList = c.execute(query, (values,))
        #course_id = c.fetchall()
        std_id = [ row[0] for row in c.fetchall() if row[0] ] # i used this to return fetch the data without ()
        std_id=std_id[0]
        #return render_template('empty3.html', data = std_id)

        #to get course id from student_grade
        #SELECT DISTINCT course_id FROM student_grade where student_id='c3301209';
        #query = "SELECT DISTINCT course_id FROM student_grade where student_id=%s"
        #values = std_id
        #cityList = c.execute(query, (values,))
        query = "SELECT DISTINCT course_id FROM student_grade where student_id=%s and assessment_name=%s"
        values = (std_id, assessment_name)
        cityList = c.execute(query, values)
        #course_id = c.fetchall()
        course_id = [ row[0] for row in c.fetchall() if row[0] ] # i used this to return fetch the data without ()
        course_id = course_id[0] # to conver list with one element to string
        #return render_template('empty3.html', data = course_id)


        # to get std grade in  assessment_name from current student table
        query = "SELECT mark FROM student_grade where student_id=%s and assessment_name=%s and course_id=%s"
        values = (std_id, assessment_name, course_id)
        cityList = c.execute(query, values)
        std_mark = [ row[0] for row in c.fetchall() if row[0] ] # i used this to return fetch the data without ()
        #std_mark = c.fetchall()
        #std_mark = std_name[0] # to conver list with one element to string
        #return render_template('empty3.html', data = std_mark)
        #END OF to get std grade in  assessment_name from current student table





        #query= "SELECT  distinct assessment_name,  tla.clo_name FROM at_map_to_tla  INNER JOIN tla  ON at_map_to_tla.tla_id = tla.tla_id  WHERE at_map_to_tla.course_course_id=%s and assessment_name=%s order by at_map_to_tla.assessment_name"
        query= "SELECT distinct assessment_name, clo_name  FROM allign_at_to_clo_m_to_m  where course_id=%s and  assessment_name=%s order by assessment_name;"
        values=(course_id, assessment_name)
        clo_assessment = c.execute(query, values)
        #number_of_assessment__predicted_so_far = c.fetchall()
        clo_assessment= c.fetchall()

        # to get std name from current student table
        query = "SELECT student_name FROM current_student where student_id=%s and course_id=%s"
        values = (std_id, course_id)
        cityList = c.execute(query, values)
        std_name = [ row[0] for row in c.fetchall() if row[0] ] # i used this to return fetch the data without ()
        std_name = std_name[0] # to conver list with one element to string
        #END OF to get std name from current student table



        #to get std average grade in  assessment_name from student_grade table
        query = "SELECT ROUND(avg(mark),2) FROM student_grade where assessment_name=%s and course_id=%s"
        values = (assessment_name, course_id)
        cityList = c.execute(query, values)
        assessment_average_mark = [ row[0] for row in c.fetchall() if row[0] ] # i used this to return fetch the data without ()
        #return render_template('empty3.html', data = assessment_average_mark)
        #END OF to get std average grade in  assessment_name from student_grade table


        # to get Course name
        query= "SELECT course_name FROM course where course_id=%s"
        values=(course_id)
        c.execute(query, (values,))
        #number_of_assessment__predicted_so_far = c.fetchall()
        course_name_not_id=  [ row[0] for row in c.fetchall() if row[0] ]

        # END OF to get course name


        #revision plan
        std_mark = np.array(std_mark)
        if  std_mark.size == 0:
            std_mark = [0]

        if std_mark[0] <100:
            #query = "SELECT t1.course_course_id, t1.assessment_name, t2.lecture_or_lab, t2.lecture_lab_number, t2.tla_topic  FROM at_map_to_tla t1  INNER JOIN tla t2 ON t1.tla_id = t2.tla_id WHERE t1.course_course_id= %s and assessment_name= %s"
            #query = "select distinct allign_tla_to_clo_m_to_m.tla_id , allign_at_to_clo_m_to_m.assessment_name,  tla.tla_topic, tla.lecture_or_lab, tla.lecture_lab_number, tla.tla_Resources  from clo  INNER JOIN allign_at_to_clo_m_to_m  ON clo.clo_name = allign_at_to_clo_m_to_m.clo_name   INNER JOIN allign_tla_to_clo_m_to_m  ON clo.clo_name = allign_tla_to_clo_m_to_m.clo_name  INNER JOIN tla  ON allign_tla_to_clo_m_to_m.tla_id = tla.tla_id  where clo.course_course_id=%s and allign_at_to_clo_m_to_m.assessment_name=%s"
            #values = (course_id, assessment_name)
            #query = "select distinct allign_tla_to_clo_m_to_m.tla_id , allign_at_to_clo_m_to_m.assessment_name,  tla.tla_topic, tla.lecture_or_lab, tla.lecture_lab_number, tla.tla_Resources  from clo  INNER JOIN allign_at_to_clo_m_to_m  ON clo.clo_name = allign_at_to_clo_m_to_m.clo_name   INNER JOIN allign_tla_to_clo_m_to_m  ON clo.clo_name = allign_tla_to_clo_m_to_m.clo_name  INNER JOIN tla  ON allign_tla_to_clo_m_to_m.tla_id = tla.tla_id  where clo.course_course_id=%s and allign_at_to_clo_m_to_m.assessment_name=%s"
            #values = (course_id, assessment_name)
            #query = "select distinct allign_tla_to_clo_m_to_m.tla_id , allign_at_to_clo_m_to_m.assessment_name,  tla.tla_topic, tla.lecture_or_lab, tla.lecture_lab_number, tla.tla_Resources  from clo  INNER JOIN allign_at_to_clo_m_to_m  ON clo.clo_name = allign_at_to_clo_m_to_m.clo_name   INNER JOIN allign_tla_to_clo_m_to_m  ON clo.clo_name = allign_tla_to_clo_m_to_m.clo_name  INNER JOIN tla  ON allign_tla_to_clo_m_to_m.tla_id = tla.tla_id  where clo.course_course_id=%s and allign_at_to_clo_m_to_m.assessment_name=%s"
            #query = "select distinct allign_tla_to_clo_m_to_m.tla_id , allign_at_to_clo_m_to_m.assessment_name, tla.tla_topic, tla.lecture_or_lab, tla.lecture_lab_number, tla.tla_Resources from clo INNER JOIN allign_at_to_clo_m_to_m  ON clo.clo_name = allign_at_to_clo_m_to_m.clo_name INNER JOIN allign_tla_to_clo_m_to_m  ON clo.clo_name = allign_tla_to_clo_m_to_m.clo_name INNER JOIN tla  ON allign_tla_to_clo_m_to_m.tla_id = tla.tla_id  where  allign_at_to_clo_m_to_m.assessment_name=%s and allign_tla_to_clo_m_to_m.course_id=%s"
            #values = (assessment_name, course_id)
            #query = "select distinct allign_tla_to_clo_m_to_m.tla_id , allign_at_to_clo_m_to_m.assessment_name, tla.tla_topic, tla.lecture_or_lab, tla.lecture_lab_number, tla.tla_Resources from clo INNER JOIN allign_at_to_clo_m_to_m  ON clo.clo_name = allign_at_to_clo_m_to_m.clo_name INNER JOIN allign_tla_to_clo_m_to_m  ON clo.clo_name = allign_tla_to_clo_m_to_m.clo_name INNER JOIN tla  ON allign_tla_to_clo_m_to_m.tla_id = tla.tla_id  where  allign_tla_to_clo_m_to_m.course_id=%s and allign_at_to_clo_m_to_m.course_id=%s and allign_at_to_clo_m_to_m.assessment_name=%s"
            query = "select allign_tla_to_at_m_to_m.tla_id, allign_tla_to_at_m_to_m.assessment_name, tla.tla_topic, tla.lecture_or_lab, tla.lecture_lab_number, tla.tla_Resources from  tla INNER JOIN allign_tla_to_at_m_to_m  ON tla.tla_id = allign_tla_to_at_m_to_m.tla_id where tla.course_course_id=%s and allign_tla_to_at_m_to_m.assessment_name=%s"
            values = (course_id, assessment_name)
            cityList = c.execute(query, values)
            revision_plan = c.fetchall()
        else:
            revision_plan=' '
            return render_template('tr_dashboard_bar_chart_assessment_detail_no_revision_plan.html', assessment_name=assessment_name,\
                           std_id=std_id,\
                               course_id=course_id,\
                                           clo_assessment=clo_assessment,\
                                               std_name=std_name,\
                                                   std_mark=std_mark,\
                                                       assessment_average_mark=assessment_average_mark)
        #END OF revision plan

    except sql.Error as e: # if error
        # then display the error in 'database_error.html' page
        return render_template('database_error.html', error=e)

    finally:
        con.close() # close the connection


    #return render_template('bar_chart_assessment_detail.html', data = clo_assessment)
    #return render_template('bar_chart.html')

    return render_template('tr_dashboard_bar_chart_assessment_detail.html', assessment_name=assessment_name,\
                           std_id=std_id,\
                               course_id=course_id, course_name_not_id = course_name_not_id, \
                                   revision_plan=revision_plan,\
                                           clo_assessment=clo_assessment,\
                                               std_name=std_name,\
                                                   std_mark=std_mark,\
                                                       assessment_average_mark=assessment_average_mark)






#NNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNN

#SSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSS



#all_revision_plan_order_by_assessment_name.py


#\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\design_course\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
#this is the Get method to aviod two dynamic dropdown lists. Design a Course
@app.route('/all_revision_plan_order_by_assessment_name_choose_course', methods=['GET', 'Post'])
@login_required
def all_revision_plan_order_by_assessment_name_choose_course():
    if request.method == 'GET':
        try:
            con = sql.connect(host="pythonanywhere_host", user="pythonanywhere_user", password="pythonanywhere_password", database="pythonanywhere$database_name") #this is not the real connections details
            c =  con.cursor() # cursor
            query = "Select * from course where userName=%s"
            values = session["USERNAME"]
            cityList = c.execute(query, (values,))
            cityList = c.fetchall()

            return render_template('all_revision_plan_order_by_assessment_name_choose_course.html', cityList=cityList)

        except sql.Error as e: # if error
            # then display the error in 'database_error.html' page
            return render_template('database_error.html', error=e)

        finally:
            con.close() # close the connection

    #else: # request.method == 'POST':
     #   courseName = request.form['course_course_id']
      #  return render_template('create_clo.html', courseName=courseName)

@app.route('/all_revision_plan_order_by_assessment_name', methods=['Post'])
@login_required
#@login_required_std
def all_revision_plan_order_by_assessment_name():
    #if request.method == 'Post':

        #course_id='3_INFT2031'
        course_id = request.form['course_course_id']
        #course_id = request.form['course_course_id']


        #std_id=session["USERNAME"]
        #return render_template('empty3.html', data = std_id)
        #this block for the barchart
        try:


            con = sql.connect(host="pythonanywhere_host", user="pythonanywhere_user", password="pythonanywhere_password", database="pythonanywhere$database_name") #this is not the real connections details
            c =  con.cursor() # cursor



            query = "select allign_tla_to_at_m_to_m.tla_id, allign_tla_to_at_m_to_m.assessment_name, tla.tla_topic, tla.lecture_or_lab, tla.lecture_lab_number, tla.tla_Resources from  tla INNER JOIN allign_tla_to_at_m_to_m  ON tla.tla_id = allign_tla_to_at_m_to_m.tla_id where tla.course_course_id=%s order by allign_tla_to_at_m_to_m.assessment_name"
            values = course_id
            cityList = c.execute(query, (values,))
            mapping_model = c.fetchall()
            #return render_template('empty3.html', data = mapping_model)

            if not mapping_model:
               return render_template('no_dashboard_yet.html', data = "NO Data to Show in the Mapping Model Yet, Please Create Mapping Model For Your Course First")


            #course_name = [ row[0] for row in c.fetchall() if row[0] ] # i used this to return fetch the data without ()
            return render_template('show_mapping_model.html', mapping_model = mapping_model, course_id = course_id)





        except sql.Error as e: # if error
            # then display the error in 'database_error.html' page
            return render_template('database_error.html', error=e)

        finally:
            con.close() # close the connection





#NNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNN

#SSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSS

# Excel_data.py

#\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\design_course\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
#this is the Get method to aviod two dynamic dropdown lists. Design a Course
@app.route('/excel_data_choose_course', methods=['GET', 'Post'])
@login_required
def excel_data_choose_course():
    if request.method == 'GET':
        try:
            
            con = sql.connect(host="pythonanywhere_host", user="pythonanywhere_user", password="pythonanywhere_password", database="pythonanywhere$database_name") #this is not the real connections details
            c =  con.cursor() # cursor
            #query = "Select * from course where userName=%s"
            query = "Select * from course_and_models where userName=%s"
            values = session["USERNAME"]
            cityList = c.execute(query, (values,))
            cityList = c.fetchall()

            return render_template('excel_data_choose_course.html', cityList=cityList)

        except sql.Error as e: # if error
            # then display the error in 'database_error.html' page
            return render_template('database_error.html', error=e)

        finally:
            con.close() # close the connection

    #else: # request.method == 'POST':
     #   courseName = request.form['course_course_id']
      #  return render_template('create_clo.html', courseName=courseName)


#\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\End OF design_course\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\


##############################################################################################
###################################### Excel_data ############################################################
##################################################################################################



@app.route('/Excel_data', methods=['GET', 'Post'])
@login_required
#@login_required_std
def Excel_data():

    #course_id='999999'

    course_id = request.form['course_course_id']

    try:


        
        con = sql.connect(host="pythonanywhere_host", user="pythonanywhere_user", password="pythonanywhere_password", database="pythonanywhere$database_name") #this is not the real connections details
        c =  con.cursor() # cursor


        # to get course name from course table using course_id

        query = "SELECT distinct assessment_name FROM student_prediction_results  where course_id=%s order by number_of_assessment_in_prediction"
        values = course_id
        cityList = c.execute(query, (values,))
        #course_name = c.fetchall()
        assessment_name = [ row[0] for row in c.fetchall() if row[0] ] # i used this to return fetch the data without ()
        #return render_template('empty3.html', data = assessment_name)

        if not assessment_name:
            return render_template('no_dashboard_yet.html', data = "NO Data to Show in Here, Please Add Students Grades First Through Preform Prediction")


        #d = {} # to create a dictionary

        i=1     # increment variable
        assessment_lenght = len(assessment_name)
        #return render_template('empty3.html', data = assessment_lenght)

        selectQuery=""

        fromQuery = ""

        whereQuery= ""

        for user in assessment_name:



            #selectQuery  = selectQuery + ", P"+str(i)+".course_id, G"+str(i)+".assessment_name, G"+str(i)+".mark,  P"+str(i)+".number_of_assessment_in_prediction, P"+str(i)+".Binary_prediction_results, P"+str(i)+".Multiclass_prediction_results "

            selectQuery  = selectQuery + ",  G"+str(i)+".unconverted_mark,  P"+str(i)+".Binary_prediction_results, P"+str(i)+".Multiclass_prediction_results "

            #c.execute(query, (values,))
            #values = (i, i, i, i, i)

            #return render_template('empty3.html', data = selectQuery)

            #selectQuery = c.execute(selectQuery, values)



            fromQuery = fromQuery + "INNER JOIN student_grade G"+str(i)+"  ON current_student.student_id = G"+str(i)+".student_id INNER JOIN student_prediction_results P"+str(i)+"  ON current_student.student_id = P"+str(i)+".student_id "

            #values= (i, i, i, i)
            #return render_template('empty3.html', data = fromQuery)
            #fromQuery = c.execute(fromQuery, values)



            whereQuery = whereQuery + " AND    G" + str(i) +".course_id='"+  course_id + "' AND    P"+str(i) + ".course_id='"+ course_id+"' AND  G" + str(i)+ ".assessment_name='" + user+ "' AND  P" + str(i)+ ".number_of_assessment_in_prediction=" + str(i)

            #return render_template('empty3.html', data = whereQuery)

            #values = (i, course_id, i, course_id, i, user, i, i)

            #whereQuery = c.execute(whereQuery, values)


            i=i+1
            assessment_lenght = assessment_lenght - 1

        #end for


        #query = "SELECT DISTINCT current_student.student_name, current_student.student_id " + selectQuery + "FROM current_student " + fromQuery + "WHERE current_student.course_id='"+course_id+ "'" + whereQuery
        query = "SELECT DISTINCT current_student.student_name, current_student.student_id " + selectQuery + "FROM current_student " + fromQuery + "WHERE current_student.course_id='"+course_id+ "'" + whereQuery

        #return render_template('empty3.html', data = query)
        c.execute(query)

        data2 = c.fetchall()
        data2 = np.array(data2)

        #return render_template('empty3.html', data = data2)


        #query = "SELECT DISTINCT current_student.student_name, current_student.student_id " + selectQuery + "FROM current_student " + "WHERE current_student.course_id=%s " + whereQuery

        #values= (course_id)

        #query = c.execute(query, (values,))


        #return render_template('empty3.html', data = query)





        d = {} # to create a dictionary
        i=1     # increment variable
        for user in assessment_name:
            #query = "select distinct current_student.student_id, current_student.student_name, student_grade.assessment_name, student_grade.mark, student_prediction_results.Binary_prediction_results, student_prediction_results.Multiclass_prediction_results from current_student INNER JOIN student_grade  ON current_student.student_id = student_grade.student_id INNER JOIN student_prediction_results  ON current_student.student_id = student_prediction_results.student_id where current_student.course_id=%s and student_grade.assessment_name=%s"
            query = "select distinct current_student.student_name, current_student.student_id, student_prediction_results.course_id, student_grade.assessment_name, student_grade.mark, student_prediction_results.number_of_assessment_in_prediction, student_prediction_results.Binary_prediction_results, student_prediction_results.Multiclass_prediction_results from current_student INNER JOIN student_grade  ON current_student.student_id = student_grade.student_id INNER JOIN student_prediction_results  ON current_student.student_id = student_prediction_results.student_id where current_student.course_id=%s and student_grade.course_id=%s and student_prediction_results.course_id=%s and  student_grade.assessment_name=%s and student_prediction_results.number_of_assessment_in_prediction=%s"
            values = (course_id, course_id, course_id, user, i)
            data = c.execute(query, values)
            data = c.fetchall()
            data = np.array(data)
            #print(data.shape)

            d["Assessment {0}".format(i)] = data
            i=i+1



        # i want to get how many std from the current_student table to use it for for loop in the excel_data.html
        query = "SELECT student_id FROM current_student where course_id=%s"
        values = course_id
        std_id = c.execute(query, (values,))
        #count_std = c.fetchall()
        std_id = [ row[0] for row in c.fetchall() if row[0] ] # i used this to return fetch the data without ()
        #return render_template('empty3.html', data = std_id)


        #h here i want to get dictionary [assessment #] in hand to use it in the excel_data.html for EXPORT ExCEL file
        d_index = list(d)

        #return render_template('empty3.html', data = assessment_name [-1])


        #return render_template('empty3.html', data = data2[0,0])
        length_of_data2 = len(data2[0])
        #return render_template('empty3.html', data = len(data2[0]))






        #return render_template('empty3.html', data = data2)
        return render_template('excel_data 4.html', course_id = course_id,  data2 = data2, assessment_name = assessment_name, length_of_data2 = length_of_data2, d = d,  std_id = std_id, d_index = d_index )
        # END OF to get course name from course table using course_id

    except sql.Error as e: # if error
        # then display the error in 'database_error.html' page
        return render_template('database_error.html', error=e)

    finally:
        con.close() # close the connection

#NNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNN

#SSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSS


# upload_std_marks_py.py

@app.route('/upload_std_marks') # this is the first GET function html that take you to/render_template  predict_csv.html
@login_required
def upload_std_marks():
    try:
        con = sql.connect(host="pythonanywhere_host", user="pythonanywhere_user", password="pythonanywhere_password", database="pythonanywhere$database_name") #this is not the real connections details
        c =  con.cursor() # cursor

        query = "Select * from course where userName=%s"
        values = session["USERNAME"]
        cityList = c.execute(query, (values,))
        cityList = c.fetchall()

        return render_template('upload_std_marks.html', cityList=cityList)

    except sql.Error as e: # if error
            # then display the error in 'database_error.html' page
            return render_template('database_error.html', error=e)

    finally:
        con.close() # close the connection





@app.route('/upload_std_marks_py',methods=['POST'])
@login_required
def upload_std_marks_py():


    courseName = request.form['course_name']

    #conversion_radio_btn = request.form['conversion'] # from the conversion radio button

    #ML_algorithms_name = request.form['ml_algorithm'] # from the radio button

    try:
        con = sql.connect(host="pythonanywhere_host", user="pythonanywhere_user", password="pythonanywhere_password", database="pythonanywhere$database_name") #this is not the real connections details
        c =  con.cursor() # cursor
        #here I want to get all assessment in the selected course so i can check if prediction csv file has column more that created models
        all_assessments_in_selected_course_query= "SELECT assessment_name  FROM assessment where course_course_id=%s order by auto_increment"
        values = (courseName)
        #here i want to fech all assessments from database for a specefic course [(course_id) from the function (function_create_dataset) parameter
        all_assessments_in_selected_course= c.execute(all_assessments_in_selected_course_query, (values,))
        all_assessments_in_selected_course = c.fetchall()
        # to get the length of all assessments for selected course (to know how many assessment in this course)
        length_all_assessments_in_selected_course= len(all_assessments_in_selected_course)

    except sql.Error as e: # if error
            # then display the error in 'database_error.html' page
        return render_template('database_error.html', error=e)

    finally:
        con.close() # close the connection


    csv_file = request.files['file']
    if request.files['file'].filename != '': # if there is file the user upload it # i overcome this issue by making input file required
        #output=""   # i dont need it anymore
        csv_file = request.files['file']

        # this helps me to validate if the uploaded file is a csv extention
        file_ext = os.path.splitext(request.files['file'].filename)[1]
        #return render_template('no_dashboard_yet.html', data = file_ext)
        if file_ext not in app.config['UPLOAD_EXTENSIONS']:
            return render_template('no_dashboard_yet.html', data = "please make sure to upload a csv file")
        # END OF this helps me to validate if the uploaded file is a csv extention

        csv_file = TextIOWrapper(csv_file, encoding='utf-8')
        csv_reader = csv.reader(csv_file, delimiter=',')
        next(csv_reader)
        data = [row for row in csv_reader]

        if len(data) == 0:
                return render_template('empty.html')


        #........................................................................................................................
        #here i want to do Rukshan comments about making the first row in CSV file the weight [mark of]
        mark_out_CSV_array = np.array(data)
        #ttype=type(my_array) #temppp
        mark_out_CSV= mark_out_CSV_array[0,2:]  #to take the first row only and after sdt_name and std_ID [only the weight]
        assessment_waitage= mark_out_CSV_array[1,2:]  #to take the second row only and after sdt_name and std_ID [only the weight]
        #return render_template('empty3.html', data = assessment_waitage)



        data = np.array(data)
        data= data [2:, :]
        data=data.tolist()
        #return render_template('empty3.html', data = data)

        #.......................................................................................................................





        #to know check how many column in array (data)
        columns = len(data[0])

        #############
        # here i want to make sure the uploaded file has features less than or equal to the number of assessments in the selected course minu the funal exam
        if columns>(length_all_assessments_in_selected_course+2): # this is to check if csv file feature has more feature than course's assessment s
            #return render_template('too_big_csv_file.html')    # if csv file has feature more than number of assessments in the database
            return render_template('sorry_features_more_than_created_models.html', length_all_assessments_in_selected_course= length_all_assessments_in_selected_course)

        ##############





        data = np.array(data) #here i convert data (type: list i think) to array

        all_data_without_std_Name_ID=data[:,2:] #here I removed student name and ID from the data in a new array because i want to send this version to the models to predict

        data_only_std_Name_ID = data[:,:2]  #here I removed all marks and kept student name and ID to used it in the html tables to present students names and id with their results


        #######################################################################################################################################


        #here I want to make sure the csv file does not have any error such as empty cell or "hjbkjb" value
        #####################################################################################################3
        all_data_without_std_Name_ID = np.array(all_data_without_std_Name_ID)
        #columns
        for row in all_data_without_std_Name_ID:

            for i in range(columns-2):



                if row[i]=="": #if the is null in the assessment make it 0
                   row[i]=0



                try:# i used try and except ValueError, to solve if data in the csv file is not nubmber such as jkhkjnh

                    #row[i]=int(row[i]) #i used float because when using int any float number return it 0, so i had to use float



                    #999999999999999999999999999999999999999999999999999999999999999999999999
                    #3333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333
                    #here i want to make sure to match students_id btn student and assessments_Std tables
                    con = sql.connect(host="pythonanywhere_host", user="pythonanywhere_user", password="pythonanywhere_password", database="pythonanywhere$database_name") #this is not the real connections details
                    c = con.cursor() # cursor
                    c = con.cursor(buffered=True)

                    value = courseName
                    query4 = "SELECT assessment_name FROM assessment WHERE course_course_id = %s  order by auto_increment"
                    c.execute(query4,(value,))

                    assessments_order = c.fetchall()

                    assessment_name_to_string = ",".join(assessments_order [i]) #to solve error "python mysqlconnector mysqlinterfaceerror python type tuple cannot be converted"
                    #3333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333

                    #if conversion_radio_btn=="Yes": # here i did the if because i want to check if the user want to convert the data in the csv file or not



                    #here in this block, I tried to convert students marks into a Percentages as Simon suggested useing mark_out and mark_worth
                    #66666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666
                    query5 = "SELECT mark_out FROM assessment where course_course_id=%s and assessment_name =%s"


                    query6 = "SELECT mark_worth FROM assessment where course_course_id=%s and assessment_name =%s"

                    c.execute(query5,(courseName,assessment_name_to_string,))
                    mark_out = [ r[0] for r in c.fetchall() if str(r[0]) ]

                    c.execute(query6,(courseName,assessment_name_to_string,))
                    mark_worth = [ r[0] for r in c.fetchall() if str(r[0]) ]

                    mark_out = np.array(mark_out)
                    mark_worth = np.array(mark_worth)


                    #row[i] = int(row[i]) / int(mark_worth) * int(mark_out)

                    if mark_out_CSV[i] !="0" and assessment_waitage[i] !="0":

                        row[i] = float(row[i]) / int(mark_out_CSV[i]) * int(assessment_waitage[i])
                        row[i] = float(row[i]) / int(assessment_waitage[i]) * 100 # this is the conversion based on Rukshan comments which is the marked out is from the first row in the csv

                        #row[i]=float(row[i])
                        #s1=type(row[i])



                    else:     #here the value of mark_out_CSV[i]==0 which means the user did not add correct value for the wieght in the csv file or the value was 0
                        #row[i] = int(row[i])
                        row[i] = float(row[i]) / int(mark_out) * int(mark_worth)
                        row[i] = float(row[i]) / int(mark_worth) * 100

                        #s2=type(row[i])

                    #s1=type(all_data_without_std_Name_ID)

                    #elif conversion_radio_btn=="No":
                    #                row[i] = float(row[i])

                    #66666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666
                    #999999999999999999999999999999999999999999999999999999999999999999999999





                except ValueError: # if the cell has strange string such as (jklnlj) in the assessments grade, it will make it 0
                    row[i] = 0


        all_data_without_std_Name_ID = np.array(all_data_without_std_Name_ID)



        all_data_without_std_Name_ID = all_data_without_std_Name_ID.astype(float)


        #####################################################################################################3


        #7878787878
        #here i want to insert students name & id into the current_student table from the uploaded csv file
        try:
            con = sql.connect(host="pythonanywhere_host", user="pythonanywhere_user", password="pythonanywhere_password", database="pythonanywhere$database_name") #this is not the real connections details
            c =  con.cursor() # cursor
            # insert data # REPLACE INTO: do as insert in do does except if the assessment_name (PK) already exist in the database it will replace it with the new record


            for row in data_only_std_Name_ID:

                    c.execute("insert ignore INTO current_student (student_id, student_name, course_id) VALUES (%s,%s,%s)", # REPLACE INTO: do as insert in do does except if the assessment_name (PK) already exist in the database it will replace it with the new record
                        (row[1], row[0], courseName))
                    con.commit() # apply changes

            #here in this small block, i store students mark, and assessment name into the student_grade table
            length_assessment_in_uplloaded_std_grade=len(all_data_without_std_Name_ID[0])

            #return render_template('empty3.html', data = length_assessment_in_uplloaded_std_grade)
            con = sql.connect(host="pythonanywhere_host", user="pythonanywhere_user", password="pythonanywhere_password", database="pythonanywhere$database_name") #this is not the real connections details
            c =  con.cursor() # cursor
            # insert data # REPLACE INTO: do as insert in do does except if the assessment_name (PK) already exist in the database it will replace it with the new record

            #to get assessment name order form assessment table
            value = courseName
            query4 = "SELECT assessment_name FROM assessment WHERE course_course_id = %s  order by auto_increment"
            c.execute(query4,(value,))

            #assessments_order = c.fetchall()
            assessments_order = [ r[0] for r in c.fetchall() if str(r[0]) ]
            j=0#increment for std_id from data_only_std_Name_ID
            for row in all_data_without_std_Name_ID:
                for i in range(length_assessment_in_uplloaded_std_grade):

                    unconverted_mark = float(row[i]) / 100 * int(assessment_waitage[i]) # this is for the real mark (unconverted mark such as 18 out of 20)

                    lost_mark= int(assessment_waitage[i]) - float(unconverted_mark) # this is for the lost mark in the assessment
                    #return render_template('empty3.html', data = lost_mark)

                    c.execute("REPLACE INTO student_grade (student_id, assessment_name, course_id, mark, unconverted_mark, lost_mark) VALUES (%s,%s,%s,%s, %s, %s)", # REPLACE INTO: do as insert in do does except if the assessment_name (PK) already exist in the database it will replace it with the new record
                        (data_only_std_Name_ID [j,1], assessments_order [i], courseName, row[i], unconverted_mark, lost_mark))
                    con.commit() # apply changes
                j=j+1
            #END OF here in this small block, i store students mark, and assessment name into the student_grade table


            query = "SELECT count(student_id) FROM current_student where course_id=%s"
            value = courseName

            c.execute(query,(value,))
            count_of_uploaded_data = [ row[0] for row in c.fetchall() if row[0] ] # i used this to return fetch the data without ()

        except sql.Error as e: # if error
                    # then display the error in 'database_error.html' page
                    return render_template('database_error.html', error=e)

        finally:
                    con.close() # close the connection

        #EDN OF here i want to insert students name & id into the current_student table from the uploaded csv file
        #7878787878



    #return render_template('sorry_no_file_selected_in_prediction_csv.html') # i solved this issue by making the input file required
    return render_template('Thank_You.html', data = count_of_uploaded_data)


#NNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNN





#SSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSS

# update_tla.py


#\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\update_tla\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
#this is the Get method to aviod two dynamic dropdown lists. Design a Course
@app.route('/update_tla_choose_course', methods=['GET', 'Post'])
@login_required
def update_tla_choose_course():
    if request.method == 'GET':
        try:
            con = sql.connect(host="pythonanywhere_host", user="pythonanywhere_user", password="pythonanywhere_password", database="pythonanywhere$database_name") #this is not the real connections details
            c =  con.cursor() # cursor
            query = "Select * from course where userName=%s"
            values = session["USERNAME"]
            cityList = c.execute(query, (values,))
            cityList = c.fetchall()

            return render_template('update_tla_choose_course.html', cityList=cityList)

        except sql.Error as e: # if error
            # then display the error in 'database_error.html' page
            return render_template('database_error.html', error=e)

        finally:
            con.close() # close the connection

    #else: # request.method == 'POST':
     #   courseName = request.form['course_course_id']
      #  return render_template('create_clo.html', courseName=courseName)

@app.route('/update_tla', methods=['Post'])
@login_required
#@login_required_std
def update_tla():
    #if request.method == 'Post':

        #course_id='3_INFT2031'
        course_id = request.form['course_course_id']
        #course_id = request.form['course_course_id']


        #std_id=session["USERNAME"]
        #return render_template('empty3.html', data = std_id)


        try:


            con = sql.connect(host="pythonanywhere_host", user="pythonanywhere_user", password="pythonanywhere_password", database="pythonanywhere$database_name") #this is not the real connections details
            c =  con.cursor() # cursor



            # this block for clo table
            query = "SELECT * FROM clo where course_course_id=%s order by  auto_increment"
            values = (course_id)
            clo_table = c.execute(query, (values,))
            clo_table = c.fetchall()


            query = "SELECT count(clo_name) FROM clo where course_course_id=%s"
            values = (course_id)
            count_clo_table = c.execute(query, (values,))
            count_clo_table = [ row[0] for row in c.fetchall() if row[0] ] # i used this to return fetch the data without ()
            #return render_template('empty3.html', data = count[0])


            query = "SELECT clo_name FROM clo where course_course_id=%s"
            values = (course_id)
            c.execute(query, (values,))
            parent_clo = [ row[0] for row in c.fetchall() if row[0] ] # i used this to return fetch the data without ()

            # END OF this block for clo table
            ############################################################################




            # this block for tla table
            query = "SELECT * FROM tla where course_course_id=%s"
            values = (course_id)
            tla_table = c.execute(query, (values,))
            tla_table = c.fetchall()


            query = "SELECT count(tla_id) FROM tla where course_course_id=%s"
            values = (course_id)
            count_tla_table = c.execute(query, (values,))
            count_tla_table = [ row[0] for row in c.fetchall() if row[0] ] # i used this to return fetch the data without ()
            #return render_template('empty3.html', data = count[0])

            query = "SELECT tla_topic FROM tla where course_course_id=%s"
            values = (course_id)
            c.execute(query, (values,))
            parent_tla = [ row[0] for row in c.fetchall() if row[0] ] # i used this to return fetch the data without ()

            # END OF this block for tla table
            ############################################################################


            # this block for assessment table
            query = "SELECT * FROM assessment where course_course_id=%s order by  auto_increment"
            values = (course_id)
            c.execute(query, (values,))
            assessment_table = c.fetchall()


            query = "SELECT count(assessment_name) FROM assessment where course_course_id=%s"
            values = (course_id)
            c.execute(query, (values,))
            count_assessment_table = [ row[0] for row in c.fetchall() if row[0] ] # i used this to return fetch the data without ()
            #return render_template('empty3.html', data = count[0])


            # END OF this block for assessment table
            ############################################################################


            if not count_tla_table:
               return render_template('no_dashboard_yet.html', data = "NO Data to Show in the Mapping Model Yet, Please Create Mapping Model For Your Course First")


            #course_name = [ row[0] for row in c.fetchall() if row[0] ] # i used this to return fetch the data without ()
            return render_template('update_tla.html', clo_table = clo_table, count_clo_table = count_clo_table, parent_clo = parent_clo, \
                                   tla_table = tla_table, course_id = course_id, count_tla_table = count_tla_table[0], parent_tla = parent_tla,\
                                   assessment_table = assessment_table, count_assessment_table = count_assessment_table)





        except sql.Error as e: # if error
            # then display the error in 'database_error.html' page
            return render_template('database_error.html', error=e)

        finally:
            con.close() # close the connection


@app.route('/update_tla_submit_btn', methods=['Post'])
@login_required
#@login_required_std
def update_tla_submit_btn():
    #if request.method == 'Post':

        #course_id='3_INFT2031'
        #course_id = request.form['course_course_id']
        count_tla_table = request.args.get('my_var')

        count_clo_table = request.args.get('my_var3')
        count_assessment_table = request.args.get('my_var4')

        if not count_clo_table:
            count_clo_table="0"

        if not count_assessment_table:
            count_assessment_table="0"

        if not count_tla_table:
            count_tla_table="0"

        #return render_template('empty3.html', data = count_assessment_table)


        # this block for clo table
        for i in range(int(count_clo_table)):
            clo_name = request.form['clo_name_clo_table'+str(i)+""]
            #return render_template('empty3.html', data = tla_id)

            course_id = request.form['course_course_id_clo_table'+str(i)+""]

            clo_level = request.form['clo_level_clo_table'+str(i)+""]

            auto_increment = request.form['auto_increment_clo_table'+str(i)+""]

            parent_clo = request.form['parent_clo_clo_table'+str(i)+""]


            if request.form.get('delete_clo_table'+str(i)+""):
                delete_checkbox="delete_yes"

            else:
                delete_checkbox="delete_no"



            try:


                con = sql.connect(host="pythonanywhere_host", user="pythonanywhere_user", password="pythonanywhere_password", database="pythonanywhere$database_name") #this is not the real connections details
                c =  con.cursor() # cursor


                # this block for delete a record if checkbox is checked
                if delete_checkbox=="delete_yes":
                    query = "delete from allign_at_to_clo_m_to_m where clo_auto_increment=%s"
                    values = (auto_increment )
                    c.execute(query, (values,))
                    con.commit() # apply changes

                    query = "delete from allign_tla_to_clo_m_to_m where clo_auto_increment=%s"
                    values = (auto_increment )
                    c.execute(query, (values,))
                    con.commit() # apply changes


                    query = "delete from clo where clo_name=%s and course_course_id=%s and auto_increment=%s"
                    values = (clo_name, course_id, auto_increment )
                    c.execute(query, values)
                    con.commit() # apply changes

                    pass

                # END OF this block for delete a record if checkbox is checked




                #here i need to fix the id problem first
                #query = "UPDATE `clo` SET `clo_name` = %s, `clo_level` = %s, `parent_clo` = %s WHERE clo_name = %s and `course_course_id` = %s"
                query = "UPDATE `clo` SET clo_name = %s, `clo_level` = %s, `parent_clo` = %s WHERE auto_increment = %s and `course_course_id` = %s"
                values = (clo_name, clo_level, parent_clo, auto_increment, course_id )
                c.execute(query, values)
                con.commit() # apply changes

                # this block to update allign_at_to_clo_m_to_m table
                query = "SELECT count(clo_auto_increment) FROM allign_at_to_clo_m_to_m where clo_auto_increment=%s"
                values = auto_increment
                c.execute(query, (values,))
                count_in_allign_at_to_clo_m_to_m = [ row[0] for row in c.fetchall() if row[0] ] # i used this to return fetch the data without ()

                if not count_in_allign_at_to_clo_m_to_m:
                    count_in_allign_at_to_clo_m_to_m = ["0"]

                 #   count_in_allign_at_to_clo_m_to_m =
                #return render_template('empty3.html', data = auto_increment)
                #if count_in_allign_at_to_clo_m_to_m:
                for k in range(int(count_in_allign_at_to_clo_m_to_m[0])):
                    query = "UPDATE `allign_at_to_clo_m_to_m` SET clo_name = %s WHERE clo_auto_increment = %s"
                    values = (clo_name, auto_increment)
                    c.execute(query, values)
                    con.commit() # apply changes

                # END OF this block to update allign_at_to_clo_m_to_m table


                # this block to update allign_tla_to_clo_m_to_m table
                query = "SELECT count(clo_auto_increment) FROM allign_tla_to_clo_m_to_m where clo_auto_increment=%s"
                values = auto_increment
                c.execute(query, (values,))
                count_in_allign_tla_to_clo_m_to_m = [ row[0] for row in c.fetchall() if row[0] ] # i used this to return fetch the data without ()

                if not count_in_allign_tla_to_clo_m_to_m:
                    count_in_allign_tla_to_clo_m_to_m = ["0"]

                for f in range(int(count_in_allign_tla_to_clo_m_to_m[0])):
                    query = "UPDATE `allign_tla_to_clo_m_to_m` SET clo_name = %s WHERE clo_auto_increment = %s"
                    values = (clo_name, auto_increment)
                    c.execute(query, values)
                    con.commit() # apply changes

                # END OF this block to update allign_tla_to_clo_m_to_m table





            except sql.Error as e: # if error
                # then display the error in 'database_error.html' page
                return render_template('database_error.html', error=e)

            finally:
                con.close() # close the connection



            # END OF this block for clo table
            ############################################################################




        # this block for assessment table
        for i in range(int(count_assessment_table)):
            assessment_name = request.form['assessment_name_assessment_table'+str(i)+""]
            #return render_template('empty3.html', data = tla_id)

            course_id = request.form['course_course_id_assessment_table'+str(i)+""]

            auto_increment = request.form['auto_increment_assessment_table'+str(i)+""]

            mark_out = request.form['mark_out_assessment_table'+str(i)+""]

            mark_worth = request.form['mark_worth_assessment_table'+str(i)+""]

            if request.form.get('delete_assessment_table'+str(i)+""):
                delete_checkbox="delete_yes"

            else:
                delete_checkbox="delete_no"

            try:


                con = sql.connect(host="pythonanywhere_host", user="pythonanywhere_user", password="pythonanywhere_password", database="pythonanywhere$database_name") #this is not the real connections details
                c =  con.cursor() # cursor


                # this block for delete a record if checkbox is checked
                if delete_checkbox=="delete_yes":
                    query = "delete from allign_at_to_clo_m_to_m where assessment_auto_increment=%s"
                    values = (auto_increment )
                    c.execute(query, (values,))
                    con.commit() # apply changes

                    query = "delete from allign_tla_to_at_m_to_m where assessment_auto_inc=%s"
                    values = (auto_increment )
                    c.execute(query, (values,))
                    con.commit() # apply changes


                    query = "delete from assessment where assessment_name=%s and course_course_id=%s and auto_increment=%s"
                    values = (assessment_name, course_id, auto_increment )
                    c.execute(query, values)
                    con.commit() # apply changes
                    pass
                # END OF this block for delete a record if checkbox is checked



                #here i need to fix the id problem first
                #query = "UPDATE `clo` SET `clo_name` = %s, `clo_level` = %s, `parent_clo` = %s WHERE clo_name = %s and `course_course_id` = %s"
                query = "UPDATE `assessment` SET assessment_name = %s,  `mark_out` = %s, `mark_worth` = %s WHERE auto_increment = %s and `course_course_id` = %s"
                values = (assessment_name, mark_out, mark_worth, auto_increment, course_id )
                c.execute(query, values)
                con.commit() # apply changes


                # this block to update allign_at_to_clo_m_to_m table
                query = "SELECT count(assessment_auto_increment) FROM allign_at_to_clo_m_to_m where assessment_auto_increment=%s"
                values = auto_increment
                c.execute(query, (values,))
                count_in_allign_at_to_clo_m_to_m = [ row[0] for row in c.fetchall() if row[0] ] # i used this to return fetch the data without ()


                if not count_in_allign_at_to_clo_m_to_m:
                    count_in_allign_at_to_clo_m_to_m = ["0"]

                for k in range(int(count_in_allign_at_to_clo_m_to_m[0])):
                    query = "UPDATE `allign_at_to_clo_m_to_m` SET assessment_name = %s WHERE assessment_auto_increment = %s"
                    values = (assessment_name, auto_increment)
                    c.execute(query, values)
                    con.commit() # apply changes

                # END OF this block to update allign_at_to_clo_m_to_m table


                # this block to update allign_tla_to_at_m_to_m table
                query = "SELECT count(assessment_auto_inc) FROM allign_tla_to_at_m_to_m where assessment_auto_inc=%s"
                values = auto_increment
                c.execute(query, (values,))
                count_in_allign_tla_to_at_m_to_m = [ row[0] for row in c.fetchall() if row[0] ] # i used this to return fetch the data without ()

                if not count_in_allign_tla_to_at_m_to_m:
                    count_in_allign_tla_to_at_m_to_m = ["0"]

                for k in range(int(count_in_allign_tla_to_at_m_to_m [0])):
                    query = "UPDATE `allign_tla_to_at_m_to_m` SET assessment_name = %s WHERE assessment_auto_inc = %s"
                    values = (assessment_name, auto_increment)
                    c.execute(query, values)
                    con.commit() # apply changes

                # END OF this block to update allign_tla_to_at_m_to_m table


            except sql.Error as e: # if error
                # then display the error in 'database_error.html' page
                return render_template('database_error.html', error=e)

            finally:
                con.close() # close the connection



            # END OF this block for assessment table
            ############################################################################




        # this block for tla table
        for i in range(int(count_tla_table)):
            tla_id = request.form['tla_id'+str(i)+""]
            #return render_template('empty3.html', data = tla_id)

            course_id = request.form['course_course_id'+str(i)+""]

            Activity_Type = request.form['Activity_Type'+str(i)+""]

            Activities_Name = request.form['Activities_Name'+str(i)+""]

            Activities_Topic = request.form['Activities_Topic'+str(i)+""]

            parent_tla = request.form['parent_tla'+str(i)+""]

            userName = request.form['userName'+str(i)+""]

            tla_Resources = request.form['tla_Resources'+str(i)+""]


            if request.form.get('delete_tla_table'+str(i)+""):
                delete_checkbox="delete_yes"

            else:
                delete_checkbox="delete_no"


            try:


                con = sql.connect(host="pythonanywhere_host", user="pythonanywhere_user", password="pythonanywhere_password", database="pythonanywhere$database_name") #this is not the real connections details
                c =  con.cursor() # cursor


                # this block for delete a record if checkbox is checked
                if delete_checkbox=="delete_yes":
                    query = "delete from allign_tla_to_clo_m_to_m where tla_id=%s"
                    values = (tla_id )
                    c.execute(query, (values,))
                    con.commit() # apply changes

                    query = "delete from allign_tla_to_at_m_to_m where tla_id=%s"
                    values = (tla_id )
                    c.execute(query, (values,))
                    con.commit() # apply changes


                    query = "delete from tla where tla_id=%s and course_course_id=%s"
                    values = (tla_id, course_id)
                    c.execute(query, values)
                    con.commit() # apply changes

                    pass
                # END OF this block for delete a record if checkbox is checked



                query = "UPDATE `tla` SET `lecture_or_lab` = %s, `lecture_lab_number` = %s, `tla_topic` = %s, `parent_tla` = %s, `tla_Resources` =  %s WHERE `tla_id` = %s"
                values = (Activity_Type, Activities_Name, Activities_Topic, parent_tla, tla_Resources,  tla_id )
                c.execute(query, values)
                con.commit() # apply changes

            except sql.Error as e: # if error
                # then display the error in 'database_error.html' page
                return render_template('database_error.html', error=e)

            finally:
                con.close() # close the connection

         # END OF this block for tla table
         ############################################################################



        return render_template('empty3.html', data = "Thank you, your updates have been applied")
        #course_id = request.form['course_course_id']


#NNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNN




#SSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSS


#update_m2m.py


#\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\ update_m2m \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
#this is the Get method to aviod two dynamic dropdown lists. Design a Course
@app.route('/update_m2m_choose_course', methods=['GET', 'Post'])
@login_required
def update_m2m_choose_course():
    if request.method == 'GET':
        try:
            con = sql.connect(host="pythonanywhere_host", user="pythonanywhere_user", password="pythonanywhere_password", database="pythonanywhere$database_name") #this is not the real connections details
            c =  con.cursor() # cursor
            query = "Select * from course where userName=%s"
            values = session["USERNAME"]
            cityList = c.execute(query, (values,))
            cityList = c.fetchall()

            return render_template('update_m2m_choose_course.html', cityList=cityList)

        except sql.Error as e: # if error
            # then display the error in 'database_error.html' page
            return render_template('database_error.html', error=e)

        finally:
            con.close() # close the connection

    #else: # request.method == 'POST':
     #   courseName = request.form['course_course_id']
      #  return render_template('create_clo.html', courseName=courseName)

@app.route('/update_m2m', methods=['Post'])
@login_required
#@login_required_std
def update_m2m():
    #if request.method == 'Post':

        course_id = request.form['course_course_id']




        #return render_template('empty3.html', data = std_id)


        try:


            con = sql.connect(host="pythonanywhere_host", user="pythonanywhere_user", password="pythonanywhere_password", database="pythonanywhere$database_name") #this is not the real connections details
            c =  con.cursor() # cursor





            # this block for allign_tla_to_clo_m_to_m table
            #query = "SELECT * FROM allign_tla_to_clo_m_to_m where course_id=%s"
            query = "SELECT t1.id_allign_tla_to_clo_m_to_m, t1.clo_name, t1.tla_id, tla.lecture_lab_number, t1.course_id, t1.clo_auto_increment FROM allign_tla_to_clo_m_to_m t1 inner join tla  ON t1.tla_id = tla.tla_id where course_id=%s"
            values = (course_id)
            c.execute(query, (values,))
            allign_tla_to_clo_m_to_m_table = c.fetchall()


            query = "SELECT count(tla_id) FROM allign_tla_to_clo_m_to_m where course_id=%s"
            values = (course_id)
            c.execute(query, (values,))
            count_allign_tla_to_clo_m_to_m_table = [ row[0] for row in c.fetchall() if row[0] ] # i used this to return fetch the data without ()
            #return render_template('empty3.html', data = count[0])


            query = "SELECT clo_name FROM clo where course_course_id=%s"
            values = (course_id)
            c.execute(query, (values,))
            clo_name = [ row[0] for row in c.fetchall() if row[0] ] # i used this to return fetch the data without ()
            #return render_template('empty3.html', data = clo_name)

            # END OF this block for allign_tla_to_clo_m_to_m table
            ############################################################################





            # this block for allign_tla_to_at_m_to_m table
            #query = "SELECT * FROM allign_tla_to_at_m_to_m where course_id=%s"
            query = "SELECT t1.id_allign_tla_to_at_m_to_m, t1.assessment_name, t1.tla_id, tla.lecture_lab_number, t1.course_id, t1.assessment_auto_inc FROM allign_tla_to_at_m_to_m t1 inner join tla  ON t1.tla_id = tla.tla_id where course_id=%s"
            values = (course_id)
            c.execute(query, (values,))
            allign_tla_to_at_m_to_m_table = c.fetchall()


            query = "SELECT count(tla_id) FROM allign_tla_to_at_m_to_m where course_id=%s"
            values = (course_id)
            c.execute(query, (values,))
            count_allign_tla_to_at_m_to_m_table = [ row[0] for row in c.fetchall() if row[0] ] # i used this to return fetch the data without ()
            #return render_template('empty3.html', data = count[0])


            query = "SELECT assessment_name FROM assessment where course_course_id=%s"
            values = (course_id)
            c.execute(query, (values,))
            assessment_name = [ row[0] for row in c.fetchall() if row[0] ] # i used this to return fetch the data without ()
            #return render_template('empty3.html', data = clo_name)

            # END OF this block for allign_tla_to_at_m_to_m table
            ############################################################################




            # this block for allign_at_to_clo_m_to_m table
            query = "SELECT * FROM allign_at_to_clo_m_to_m where course_id=%s"
            values = (course_id)
            c.execute(query, (values,))
            allign_at_to_clo_m_to_m_table = c.fetchall()


            query = "SELECT count(id_allign_at_to_clo_m_to_m) FROM allign_at_to_clo_m_to_m where course_id=%s"
            values = (course_id)
            c.execute(query, (values,))
            count_allign_at_to_clo_m_to_m_table = [ row[0] for row in c.fetchall() if row[0] ] # i used this to return fetch the data without ()
            #return render_template('empty3.html', data = count[0])


            # END OF this block for allign_tla_to_at_m_to_m table
            ############################################################################




            if not count_allign_tla_to_clo_m_to_m_table:
               return render_template('no_dashboard_yet.html', data = "NO Data to Show in the Mapping Model Yet, Please Create Mapping Model For Your Course First")


            #course_name = [ row[0] for row in c.fetchall() if row[0] ] # i used this to return fetch the data without ()
            return render_template('update_m2m.html', course_id = course_id,\
                                   allign_tla_to_clo_m_to_m_table = allign_tla_to_clo_m_to_m_table, count_allign_tla_to_clo_m_to_m_table = count_allign_tla_to_clo_m_to_m_table, clo_name = clo_name,\
                                       allign_tla_to_at_m_to_m_table = allign_tla_to_at_m_to_m_table, count_allign_tla_to_at_m_to_m_table = count_allign_tla_to_at_m_to_m_table,  assessment_name = assessment_name, \
                                               allign_at_to_clo_m_to_m_table = allign_at_to_clo_m_to_m_table, count_allign_at_to_clo_m_to_m_table = count_allign_at_to_clo_m_to_m_table)





        except sql.Error as e: # if error
            # then display the error in 'database_error.html' page
            return render_template('database_error.html', error=e)

        finally:
            con.close() # close the connection


@app.route('/update_m2m_submit_btn', methods=['Post'])
@login_required
#@login_required_std
def update_m2m_submit_btn():
    #if request.method == 'Post':

        #course_id='3_INFT2031'
        #course_id = request.form['course_course_id']

        count_allign_tla_to_clo_m_to_m_table = request.args.get('my_var2')
        count_allign_tla_to_at_m_to_m_table = request.args.get('my_var5')
        count_allign_at_to_clo_m_to_m_table = request.args.get('my_var6')


        if not count_allign_tla_to_clo_m_to_m_table:
            count_allign_tla_to_clo_m_to_m_table="0"

        if not count_allign_tla_to_at_m_to_m_table:
            count_allign_tla_to_at_m_to_m_table="0"

        if not count_allign_at_to_clo_m_to_m_table:
            count_allign_at_to_clo_m_to_m_table="0"


        #return render_template('empty3.html', data = count_assessment_table)



        ###############################################################################
        # this block for allign_at_to_clo_m_to_m table
        for i in range(int(count_allign_at_to_clo_m_to_m_table)):

            #return render_template('empty3.html', data = tla_id)

            id_allign_at_to_clo_m_to_m = request.form['allign_at_to_clo_m_to_m_id'+str(i)+""]

            course_id = request.form['allign_at_to_clo_m_to_m_course_id'+str(i)+""]

            assessment_name = request.form['allign_at_to_clo_m_to_m_assessment_name'+str(i)+""]

            clo_name_allign_at_to_clo_m_to_m = request.form['allign_at_to_clo_m_to_m_clo_name'+str(i)+""]


            if request.form.get('allign_at_to_clo_m_to_m_delete'+str(i)+""):
                delete_checkbox="delete_yes"

            else:
                delete_checkbox="delete_no"

            #return render_template('empty3.html', data = delete_checkbox )









            try:


                con = sql.connect(host="pythonanywhere_host", user="pythonanywhere_user", password="pythonanywhere_password", database="pythonanywhere$database_name") #this is not the real connections details
                c =  con.cursor() # cursor

                # this block for delete a record if checkbox is checked
                if delete_checkbox=="delete_yes":
                    query = "DELETE FROM `allign_at_to_clo_m_to_m` WHERE (`id_allign_at_to_clo_m_to_m` = %s)"
                    values = (id_allign_at_to_clo_m_to_m )
                    c.execute(query, (values,))
                    con.commit() # apply changes
                    pass
                # END OF this block for delete a record if checkbox is checked


                # update assessment_auto_increment only
                query = "SELECT auto_increment FROM assessment where assessment_name=%s and course_course_id=%s"
                values = (assessment_name, course_id )
                c.execute(query, values)
                auto_increment_assessment_table = [ row[0] for row in c.fetchall() if row[0] ] # i used this to return fetch the data without ()

                query = "UPDATE `allign_at_to_clo_m_to_m` SET `assessment_auto_increment` = %s WHERE (`id_allign_at_to_clo_m_to_m` = %s) "
                values = (auto_increment_assessment_table [0], id_allign_at_to_clo_m_to_m )
                c.execute(query, values)
                con.commit() # apply changes

                # END OF update assessment_auto_increment only


                # update assessment_name only
                query = "UPDATE `allign_at_to_clo_m_to_m` SET `assessment_name` = %s WHERE (`id_allign_at_to_clo_m_to_m` = %s) "
                values = (assessment_name, id_allign_at_to_clo_m_to_m )
                c.execute(query, values)
                con.commit() # apply changes
                # END OF update assessment_name only


                # update clo_auto_increment only
                query = "SELECT auto_increment FROM clo where clo_name=%s and course_course_id=%s"
                values = (clo_name_allign_at_to_clo_m_to_m, course_id )
                c.execute(query, values)
                auto_increment_clo_table = [ row[0] for row in c.fetchall() if row[0] ] # i used this to return fetch the data without ()

                query = "UPDATE `allign_at_to_clo_m_to_m` SET `clo_auto_increment` = %s WHERE (`id_allign_at_to_clo_m_to_m` = %s) "
                values = (auto_increment_clo_table [0], id_allign_at_to_clo_m_to_m )
                c.execute(query, values)
                con.commit() # apply changes
                # END OF update clo_auto_increment only


                # update clo_name only
                query = "UPDATE `allign_at_to_clo_m_to_m` SET `clo_name` = %s WHERE (`id_allign_at_to_clo_m_to_m` = %s) "
                values = (clo_name_allign_at_to_clo_m_to_m, id_allign_at_to_clo_m_to_m )
                c.execute(query, values)
                con.commit() # apply changes
                # END OF update clo only


            except sql.Error as e: # if error
                # then display the error in 'database_error.html' page
                return render_template('database_error.html', error=e)

            finally:
                con.close() # close the connection

        # END OF this block for allign_at_to_clo_m_to_m table
         ############################################################################




        ###############################################################################
        # this block for allign_tla_to_clo_m_to_m table
        for i in range(int(count_allign_tla_to_clo_m_to_m_table)):

            #return render_template('empty3.html', data = tla_id)

            id_allign_tla_to_clo_m_to_m = request.form['allign_tla_to_clo_m_to_m_id'+str(i)+""]

            course_id = request.form['allign_tla_to_clo_m_to_m_course_id'+str(i)+""]

            tla_id = request.form['allign_tla_to_clo_m_to_m_tla_id'+str(i)+""]

            clo_name_allign_tla_to_clo_m_to_m_table = request.form['allign_tla_to_clo_m_to_m_clo_name'+str(i)+""]

            if request.form.get('allign_tla_to_clo_m_to_m_delete'+str(i)+""):
                delete_checkbox="delete_yes"

            else:
                delete_checkbox="delete_no"

            try:


                con = sql.connect(host="pythonanywhere_host", user="pythonanywhere_user", password="pythonanywhere_password", database="pythonanywhere$database_name") #this is not the real connections details
                c =  con.cursor() # cursor

                # this block for delete a record if checkbox is checked
                if delete_checkbox=="delete_yes":
                    query = "DELETE FROM `allign_tla_to_clo_m_to_m` WHERE (`id_allign_tla_to_clo_m_to_m` = %s)"
                    values = (id_allign_tla_to_clo_m_to_m )
                    c.execute(query, (values,))
                    con.commit() # apply changes
                    pass
                # END OF this block for delete a record if checkbox is checked


                # update clo_auto_increment only
                query = "SELECT auto_increment FROM clo where clo_name=%s and course_course_id=%s"
                values = (clo_name_allign_tla_to_clo_m_to_m_table, course_id )
                c.execute(query, values)
                auto_increment_clo_table = [ row[0] for row in c.fetchall() if row[0] ] # i used this to return fetch the data without ()

                query = "UPDATE `allign_tla_to_clo_m_to_m` SET `clo_auto_increment` = %s WHERE (`id_allign_tla_to_clo_m_to_m` = %s) "
                values = (auto_increment_clo_table [0], id_allign_tla_to_clo_m_to_m )
                c.execute(query, values)
                con.commit() # apply changes
                # END OF update clo_auto_increment only

                # update clo_name only
                query = "UPDATE `allign_tla_to_clo_m_to_m` SET `clo_name` = %s WHERE (`id_allign_tla_to_clo_m_to_m` = %s) "
                values = (clo_name_allign_tla_to_clo_m_to_m_table, id_allign_tla_to_clo_m_to_m )
                c.execute(query, values)
                con.commit() # apply changes
                # ENF OF update clo_name only


            except sql.Error as e: # if error
                # then display the error in 'database_error.html' page
                return render_template('database_error.html', error=e)

            finally:
                con.close() # close the connection

        # END OF this block for allign_tla_to_clo_m_to_m table
         ############################################################################



        ###############################################################################
        # this block for allign_tla_to_at_m_to_m_table table
        for i in range(int(count_allign_tla_to_at_m_to_m_table)):

            #return render_template('empty3.html', data = tla_id)
            id_allign_tla_to_at_m_to_m = request.form['allign_tla_to_at_m_to_m_id'+str(i)+""]

            course_id = request.form['allign_tla_to_at_m_to_m_course_id'+str(i)+""]

            tla_id = request.form['allign_tla_to_at_m_to_m_tla_id'+str(i)+""]

            assessment_name = request.form['allign_tla_to_at_m_to_m_assessment_name'+str(i)+""]

            if request.form.get('allign_tla_to_at_m_to_m_delete'+str(i)+""):
                delete_checkbox="delete_yes"

            else:
                delete_checkbox="delete_no"

            try:


                con = sql.connect(host="pythonanywhere_host", user="pythonanywhere_user", password="pythonanywhere_password", database="pythonanywhere$database_name") #this is not the real connections details
                c =  con.cursor() # cursor

                # this block for delete a record if checkbox is checked
                if delete_checkbox=="delete_yes":
                    query = "DELETE FROM `allign_tla_to_at_m_to_m` WHERE (`id_allign_tla_to_at_m_to_m` = %s)"
                    values = (id_allign_tla_to_at_m_to_m )
                    c.execute(query, (values,))
                    con.commit() # apply changes
                    pass
                # END OF this block for delete a record if checkbox is checked



                # update assessment_auto_increment only
                query = "SELECT auto_increment FROM assessment where assessment_name=%s and course_course_id=%s"
                values = (assessment_name, course_id )
                c.execute(query, values)
                auto_increment_assessment_table = [ row[0] for row in c.fetchall() if row[0] ] # i used this to return fetch the data without ()

                query = "UPDATE `allign_tla_to_at_m_to_m` SET `assessment_auto_inc` = %s WHERE (`id_allign_tla_to_at_m_to_m` = %s) "
                values = (auto_increment_assessment_table [0], id_allign_tla_to_at_m_to_m )
                c.execute(query, values)
                con.commit() # apply changes

                # END OF update assessment_auto_increment only

                query = "UPDATE `allign_tla_to_at_m_to_m` SET `assessment_name` = %s WHERE id_allign_tla_to_at_m_to_m = %s"
                values = (assessment_name, id_allign_tla_to_at_m_to_m)
                c.execute(query, values)
                con.commit() # apply changes

            except sql.Error as e: # if error
                # then display the error in 'database_error.html' page
                return render_template('database_error.html', error=e)

            finally:
                con.close() # close the connection

        # END OF this block for allign_tla_to_at_m_to_m_table table
         ############################################################################



        return render_template('empty3.html', data = "Thank you, your updates have been applied")
        #course_id = request.form['course_course_id']




#NNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNN

#SSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSS

#std_dashboard1.py

#\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\ std_dashboard1 \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
#this is the Get method to aviod two dynamic dropdown lists. Design a Course
@app.route('/std_dashboard1_choose_course', methods=['GET', 'Post'])
#@login_required
@login_required_std
def std_dashboard1_choose_course():
    if request.method == 'GET':
        try:
            con = sql.connect(host="pythonanywhere_host", user="pythonanywhere_user", password="pythonanywhere_password", database="pythonanywhere$database_name") #this is not the real connections details
            c =  con.cursor() # cursor
            #query = "Select * from course where userName=%s"
            query = "SELECT distinct course_id FROM student_grade where student_id=%s"

            values = session["USERNAME"]
            cityList = c.execute(query, (values,))
            cityList = c.fetchall()
            #cityList = [ row[0] for row in c.fetchall() if row[0] ] # i used this to return fetch the data without ()
            #cityList="SENG1050_local"

            #return render_template('std_dashboard1_choose_course_temp.html', cityList=cityList)
            return render_template('std_dashboard1_choose_course.html', cityList=cityList)

        except sql.Error as e: # if error
            # then display the error in 'database_error.html' page
            return render_template('database_error.html', error=e)

        finally:
            con.close() # close the connection

    #else: # request.method == 'POST':
     #   courseName = request.form['course_course_id']
      #  return render_template('create_clo.html', courseName=courseName)


#\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\End OF choose course\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\


##############################################################################################
###################################### std_dashboard1 ############################################################
##################################################################################################



@app.route('/std_dashboard1', methods=['Post'])
#@login_required
@login_required_std
def std_dashboard1():
    #if request.method == 'Post':

        #course_id='3_INFT2031'
        course_id = request.form['course_course_id']


        std_id=session["USERNAME"]
        #return render_template('empty3.html', data = course_id)
        #this block for the barchart
        try:

            con = sql.connect(host="pythonanywhere_host", user="pythonanywhere_user", password="pythonanywhere_password", database="pythonanywhere$database_name") #this is not the real connections details

            c =  con.cursor() # cursor


            # to get course name from course table using course_id

            query = "SELECT course_name FROM course where course_id=%s"
            values = course_id
            cityList = c.execute(query, (values,))
            #course_name = c.fetchall()
            course_name = [ row[0] for row in c.fetchall() if row[0] ] # i used this to return fetch the data without ()
            #return render_template('empty3.html', data = course_name [0])
            # END OF to get course name from course table using course_id


            # this block for std name and id
            #query = "SELECT distinct student_id FROM student_grade where course_id=%s"
            #query = "SELECT distinct student_grade.student_id, current_student.student_name FROM student_grade INNER JOIN current_student ON student_grade.student_id = current_student.student_id where student_grade.course_id=%s"
            #values = course_id
            #cityList = c.execute(query, (values,))
            #std_id_and_name = c.fetchall()

            query = "SELECT student_id, student_name FROM current_student where student_id=%s"
            values = std_id
            cityList = c.execute(query, (values,))
            std_id_and_name = c.fetchall()
            #return render_template('empty3.html', data = std_id_and_name)


            #this is used if teacher select course that does not have any std's data
            #if not std_id_and_name:
            #   return render_template('no_dashboard_yet.html', data = "NO Data to Show in the Dashboard Yet, Please Add Students Grades and Design Your Course First")

            std_id_and_name = np.asarray(std_id_and_name)
            std_id = std_id_and_name[:,0]
            std_name = std_id_and_name[:,1]
            #return render_template('empty3.html', data = std_id)
            #return render_template('empty3.html', data = std_name)
            #std_id = [ row[0] for row in c.fetchall() if row[0] ] # i used this to return fetch the data without ()

            #return render_template('empty3.html', data = std_id_and_name[:,0])
            # END OF this block for std name and id




            # this block for asserssment name of last assessment
            query = "SELECT distinct assessment_name FROM student_grade where course_id=%s"
            values = course_id
            cityList = c.execute(query, (values,))
            #labels = c.fetchall()
            assessment_name = [ row[0] for row in c.fetchall() if row[0] ] # i used this to return fetch the data without ()
            #return render_template('empty3.html', data = assessment_name)
            #labels=type(labels)
            #return render_template('empty3.html', data = labels)

            # END OF this block for asserssment name of last assessment

            #query = "SELECT distinct assessment_name FROM student_grade where course_id=%s"
            query = "SELECT distinct student_id, assessment_name, mark FROM student_grade where course_id=%s"
            values = course_id
            cityList = c.execute(query, (values,))
            temp = c.fetchall()
            temp = np.asarray(temp)

            #temp
            #mark = [ row[0] for row in c.fetchall() if row[0] ] # i used this to return fetch the data without ()
            #return render_template('empty3.html', data = temp[0:4,2])

            lenth_assessments = len(assessment_name) # to get how many assessments std have taken so far
            zero = 0 # i used this variable in the bar_char_pdf.html
            lenth_std = len(std_id) # i used this variable in the bar_char_pdf.html
            #return render_template('empty3.html', data = lenth_std)



##############################################################9


            # get std mark in all assessment
            query = "SELECT mark FROM student_grade where course_id=%s and student_id=%s"
            #query = "SELECT mark FROM student_grade where student_id=%s"
            values = (course_id, std_id[0])
            c.execute(query, values)
            #mark = c.fetchall()
            mark = [ row[0] for row in c.fetchall() if row[0] ] # i used this to return fetch the data without ()
            #return render_template('empty3.html', data = mark)
            #mark = [ row[0] for row in c.fetchall() if row[0] ] # i used this to return fetch the data without ()
            #return render_template('empty3.html', data = mark)
            #here I convert list to array first, then convert array element to str, and then i removed brackets from the element of the array
            #mark = np.asarray(mark)
            #mark = mark.astype(str)
            #mark = [ row[0] for row in mark if row[0] ]
            # END OF here I convert list to array firs, then convert array element to str, and then i removed brackets from the element of the array
            #return render_template('empty3.html', data = mark)
            #mark = [ row[0] for row in c.fetchall() if row[0] ] # i used this to return fetch the data without ()

            #return render_template('empty3.html', data = mark)
            #return render_template('empty3.html', data = len(mark))
            #return render_template('empty3.html', data = name_of_last_assessment)

##############################################################9

            # this block for the revision_plan of the last assessment
            #SELECT DISTINCT assessment_name FROM student_prediction_results where number_of_assessment_in_prediction='4';
            query = "SELECT DISTINCT assessment_name FROM student_prediction_results where number_of_assessment_in_prediction=%s and  course_id =%s"
            values = (lenth_assessments, course_id)
            cityList = c.execute(query, values)
            #number_of_assessment__predicted_so_far = c.fetchall()
            name_of_last_assessment = [ row[0] for row in c.fetchall() if row[0] ] # i used this to return fetch the data without ()
            #return render_template('empty3.html', data = name_of_last_assessment)


            #$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
            # this block for the revision_plan and CLOs assessment of the all the assessment done
            #SELECT DISTINCT assessment_name FROM student_prediction_results where number_of_assessment_in_prediction='4';
            query = "SELECT DISTINCT assessment_name FROM student_prediction_results where number_of_assessment_in_prediction<=%s and  course_id =%s order by number_of_assessment_in_prediction"
            values = (lenth_assessments, course_id)
            cityList = c.execute(query, values)
            #number_of_assessment__predicted_so_far = c.fetchall()
            list_of_assessments_done = [ row[0] for row in c.fetchall() if row[0] ] # i used this to return fetch the data without ()

            #return render_template('empty3.html', data = list_of_assessments_done)


            d_revision_plan = {} # to create a dictionary for the revision plan for each done assessment

            for user in list_of_assessments_done:
                query = "select allign_tla_to_at_m_to_m.tla_id, allign_tla_to_at_m_to_m.assessment_name, tla.tla_topic, tla.lecture_or_lab, tla.lecture_lab_number, tla.tla_Resources from  tla INNER JOIN allign_tla_to_at_m_to_m  ON tla.tla_id = allign_tla_to_at_m_to_m.tla_id where tla.course_course_id=%s and allign_tla_to_at_m_to_m.assessment_name=%s"
                #values = (course_id, course_id, name_of_last_assessment)
                values = (course_id, user)
                c.execute(query, values)
                data = c.fetchall()
                data = np.array(data)
                #print(data.shape)

                #d["Assessment {0}".format(i)] = data
                d_revision_plan["{0}".format(user)] = data

            #return render_template('empty3.html', data = d['Mid-semester quiz'])
            #return render_template('empty3.html', data = d)
            #return render_template('empty3.html', data = len(d))
            #return render_template('empty3.html', data = d['Mid-semester quiz'][0,4])
            #return render_template('empty3.html', data = d)

            clo_assessment = {} # to create a dictionary for all assessment clo done

            for user in list_of_assessments_done:
                query= "SELECT distinct assessment_name, clo_name  FROM allign_at_to_clo_m_to_m  where course_id=%s and  assessment_name=%s order by assessment_name;"
                #values = (course_id, course_id, name_of_last_assessment)
                values = (course_id, user)
                c.execute(query, values)
                data = c.fetchall()
                data = np.array(data)
                #print(data.shape)

                #d["Assessment {0}".format(i)] = data
                clo_assessment["{0}".format(user)] = data

            #return render_template('empty3.html', data = clo_assessment['Mid-semester quiz'])
            #return render_template('empty3.html', data = clo_assessment)
            #$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$



            if not name_of_last_assessment:
                return render_template('no_dashboard_yet.html', data = "NO Data to Show in the Dashboard Yet, Please Add Students Grades and Design Your Course First")


            name_of_last_assessment = name_of_last_assessment[0] # to conver list with one element to string
            #return render_template('empty3.html', data = name_of_last_assessment)

            #return render_template('empty3.html', data = name_of_last_assessment)
            #return render_template('empty3.html', data = mark % lenth_assessments)

            #if mark% lenth_assessments<100:

            #query = "select distinct allign_tla_to_clo_m_to_m.tla_id , allign_at_to_clo_m_to_m.assessment_name,  tla.tla_topic, tla.lecture_or_lab, tla.lecture_lab_number, tla.tla_Resources  from clo  INNER JOIN allign_at_to_clo_m_to_m  ON clo.clo_name = allign_at_to_clo_m_to_m.clo_name   INNER JOIN allign_tla_to_clo_m_to_m  ON clo.clo_name = allign_tla_to_clo_m_to_m.clo_name  INNER JOIN tla  ON allign_tla_to_clo_m_to_m.tla_id = tla.tla_id  where clo.course_course_id=%s and allign_at_to_clo_m_to_m.assessment_name=%s"
            #query = "select distinct allign_tla_to_clo_m_to_m.tla_id , allign_at_to_clo_m_to_m.assessment_name, tla.tla_topic, tla.lecture_or_lab, tla.lecture_lab_number, tla.tla_Resources from clo INNER JOIN allign_at_to_clo_m_to_m  ON clo.clo_name = allign_at_to_clo_m_to_m.clo_name INNER JOIN allign_tla_to_clo_m_to_m  ON clo.clo_name = allign_tla_to_clo_m_to_m.clo_name INNER JOIN tla  ON allign_tla_to_clo_m_to_m.tla_id = tla.tla_id  where  allign_at_to_clo_m_to_m.assessment_name=%s and allign_tla_to_clo_m_to_m.course_id=%s"
            #values = (name_of_last_assessment, course_id)
            #query = "select distinct allign_tla_to_clo_m_to_m.tla_id , allign_at_to_clo_m_to_m.assessment_name, tla.tla_topic, tla.lecture_or_lab, tla.lecture_lab_number, tla.tla_Resources from clo INNER JOIN allign_at_to_clo_m_to_m  ON clo.clo_name = allign_at_to_clo_m_to_m.clo_name INNER JOIN allign_tla_to_clo_m_to_m  ON clo.clo_name = allign_tla_to_clo_m_to_m.clo_name INNER JOIN tla  ON allign_tla_to_clo_m_to_m.tla_id = tla.tla_id  where  allign_tla_to_clo_m_to_m.course_id=%s and allign_at_to_clo_m_to_m.course_id=%s and allign_at_to_clo_m_to_m.assessment_name=%s"
            query = "select allign_tla_to_at_m_to_m.tla_id, allign_tla_to_at_m_to_m.assessment_name, tla.tla_topic, tla.lecture_or_lab, tla.lecture_lab_number, tla.tla_Resources from  tla INNER JOIN allign_tla_to_at_m_to_m  ON tla.tla_id = allign_tla_to_at_m_to_m.tla_id where tla.course_course_id=%s and allign_tla_to_at_m_to_m.assessment_name=%s"
            #values = (course_id, course_id, name_of_last_assessment)
            values = (course_id, name_of_last_assessment)
            #cityList = c.execute(query, values)
            #revision_plan = c.fetchall()
            #return render_template('empty3.html', data = d_revision_plan)


            if not d_revision_plan:
               return render_template('no_dashboard_yet.html', data = "NO Data to Show in the Dashboard Yet, Please Add Students Grades and Design Your Course First")
            #else:
            #    revision_plan = ""

            #return render_template('empty3.html', data = revision_plan)

            # END OF this block for the revision_plan of the last assessment

            # GET CLOs Name for current assessment
            #query= "SELECT  distinct assessment_name,  tla.clo_name FROM at_map_to_tla  INNER JOIN tla  ON at_map_to_tla.tla_id = tla.tla_id  WHERE at_map_to_tla.course_course_id=%s and assessment_name=%s order by at_map_to_tla.assessment_name"
            query= "SELECT distinct assessment_name, clo_name  FROM allign_at_to_clo_m_to_m  where course_id=%s and  assessment_name=%s order by assessment_name;"
            values=(course_id, name_of_last_assessment)
            #clo_assessment = c.execute(query, values)
            #number_of_assessment__predicted_so_far = c.fetchall()
            #clo_assessment= c.fetchall()
            #return render_template('empty3.html', data = clo_assessment)
            # END OF GET CLOs Name for current assessment


            # total collected mark
            #query = "SELECT student_id, ROUND(sum(unconverted_mark ),2)  'achieved', ROUND(sum(lost_mark ),2)  'unachieved', ROUND(100 - (sum(unconverted_mark ) + sum(lost_mark )),2)  'remained'  FROM student_grade where course_id=%s group by student_id"
            query = "SELECT student_id, ROUND(sum(unconverted_mark ),2)  'achieved', ROUND(sum(lost_mark ),2)  'unachieved', ROUND(100 - (sum(unconverted_mark ) + sum(lost_mark )),2)  'remained'  FROM student_grade where course_id=%s and student_id=%s"
            values = (course_id, std_id[0])
            cityList = c.execute(query, values)
            #cityList = [ row[0] for row in c.fetchall() if row[0] ] # i used this to return fetch the data without ()
            cityList = c.fetchall()
            cityList = np.asarray(cityList)
            achieved = cityList[:,1]
            unachieved = cityList[:,2]
            remained = cityList[:,3]
            #if collected:
             #   collected=float(collected[1])
            #else:
             #   collected=0

            #return render_template('empty3.html', data = remained)
            # END OF total collected mark

            # this block to get students mark in the current assessment
            #query = "SELECT student_id, unconverted_mark , ROUND((unconverted_mark  + lost_mark ),2) 'out of',   mark '%' FROM student_grade where course_id=%s and assessment_name=%s group by student_id"
            #query = "SELECT student_id, ROUND(unconverted_mark,1)  , ROUND((unconverted_mark  + lost_mark ),2) 'out of',   mark '%' FROM student_grade where course_id=%s and assessment_name=%s group by student_id"
            query = "SELECT student_id, ROUND(unconverted_mark,1)  , ROUND((unconverted_mark  + lost_mark ),1) 'out of',   ROUND(mark,1) '%' FROM student_grade where course_id=%s and assessment_name=%s and student_id=%s"
            values = (course_id, name_of_last_assessment, std_id[0])
            c.execute(query, values)
            #cityList = [ row[0] for row in c.fetchall() if row[0] ] # i used this to return fetch the data without ()
            cityList = c.fetchall()
            cityList = np.asarray(cityList)
            unconverted_mark = cityList[:,1]
            mark_out_of = cityList[:,2]
            mark_percentage = cityList[:,3]
            #return render_template('empty3.html', data = mark_percentage)

            #END OF this block to get students mark in the current assessment





            #std_name_and_id_ = [ row[0] for row in c.fetchall() if row[0] ] # i used this to return fetch the data without ()
            #return render_template('empty3.html', data = std_name_and_id_[:,0])
            # END OF get std name and id from student_prediction_results order by prediction results to show at-risk std first in checkbox






            return render_template('std_dashboard1.html', title='Student Dashboard', max=100, labels=assessment_name, values=mark,\
                                   course_id=course_id, course_name = course_name,
                                   assessment_name = assessment_name,\
                                           std_id=std_id, std_name = std_name, lenth_std = lenth_std, std_id_and_name = std_id_and_name,\
                                           lenth_assessments = lenth_assessments, zero=zero,

                                           name_of_last_assessment = name_of_last_assessment, list_of_assessments_done = list_of_assessments_done,
                                           clo_assessment = clo_assessment,
                                           achieved = achieved, unachieved = unachieved, remained = remained,\
                                           unconverted_mark = unconverted_mark, mark_out_of = mark_out_of, mark_percentage = mark_percentage,
                                           d_revision_plan = d_revision_plan

                                           )

        except sql.Error as e: # if error
            # then display the error in 'database_error.html' page
            return render_template('database_error.html', error=e)

        finally:
            con.close() # close the connection





#NNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNN

#SSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSS

#std_dashboard2.py

@app.route('/std_dashboard2', methods=['GET', 'Post'])
#@login_required
@login_required_std
def std_dashboard2():

    #assessment_name = request.args.get('my_var', None)
    #return render_template('empty3.html', data = my_var)
    assessment_name = request.args.get('my_var')



    course_id = request.args.get('my_var2')
    std_id=session["USERNAME"]

    #return render_template('empty3.html', data = course_id)

    try:


        con = sql.connect(host="pythonanywhere_host", user="pythonanywhere_user", password="pythonanywhere_password", database="pythonanywhere$database_name") #this is not the real connections details
        c =  con.cursor() # cursor

        query = "SELECT student_name FROM current_student where student_id=%s"
        values = std_id
        cityList = c.execute(query, (values,))
        #course_id = c.fetchall()
        std_name = [ row[0] for row in c.fetchall() if row[0] ] # i used this to return fetch the data without ()
        std_name=std_name[0]
        #return render_template('empty3.html', data = std_name)

        #to get course id from student_grade
        #SELECT DISTINCT course_id FROM student_grade where student_id='c3301209';
        #query = "SELECT DISTINCT course_id FROM student_grade where student_id=%s"
        #values = std_id
        #cityList = c.execute(query, (values,))


        # to get std grade in  assessment_name from current student table
        query = "SELECT ROUND(mark,2) FROM student_grade where student_id=%s and assessment_name=%s and course_id=%s"
        values = (std_id, assessment_name, course_id)
        cityList = c.execute(query, values)
        std_mark = [ row[0] for row in c.fetchall() if row[0] ] # i used this to return fetch the data without ()
        #std_mark = c.fetchall()
        #std_mark = std_name[0] # to conver list with one element to string
        #return render_template('empty3.html', data = std_mark)
        #END OF to get std grade in  assessment_name from current student table





        #query= "SELECT  distinct assessment_name,  tla.clo_name FROM at_map_to_tla  INNER JOIN tla  ON at_map_to_tla.tla_id = tla.tla_id  WHERE at_map_to_tla.course_course_id=%s and assessment_name=%s order by at_map_to_tla.assessment_name"
        query= "SELECT distinct assessment_name, clo_name  FROM allign_at_to_clo_m_to_m  where course_id=%s and  assessment_name=%s order by assessment_name;"
        values=(course_id, assessment_name)
        clo_assessment = c.execute(query, values)
        #number_of_assessment__predicted_so_far = c.fetchall()
        clo_assessment= c.fetchall()
        #return render_template('empty3.html', data = clo_assessment)



        #to get std average grade in  assessment_name from student_grade table
        query = "SELECT ROUND(avg(mark),2) FROM student_grade where assessment_name=%s and course_id=%s"
        values = (assessment_name, course_id)
        cityList = c.execute(query, values)
        assessment_average_mark = [ row[0] for row in c.fetchall() if row[0] ] # i used this to return fetch the data without ()
        #return render_template('empty3.html', data = assessment_average_mark)
        #END OF to get std average grade in  assessment_name from student_grade table


        # to get Course name
        query= "SELECT course_name FROM course where course_id=%s"
        values=(course_id)
        c.execute(query, (values,))
        #number_of_assessment__predicted_so_far = c.fetchall()
        course_name_not_id=  [ row[0] for row in c.fetchall() if row[0] ]
        #return render_template('empty3.html', data = course_name_not_id)

        # END OF to get course name


        #revision plan
        std_mark = np.array(std_mark)
        if  std_mark.size == 0:
            std_mark = [0]

        if std_mark[0] <100:
            #query = "SELECT t1.course_course_id, t1.assessment_name, t2.lecture_or_lab, t2.lecture_lab_number, t2.tla_topic  FROM at_map_to_tla t1  INNER JOIN tla t2 ON t1.tla_id = t2.tla_id WHERE t1.course_course_id= %s and assessment_name= %s"
            #query = "select distinct allign_tla_to_clo_m_to_m.tla_id , allign_at_to_clo_m_to_m.assessment_name,  tla.tla_topic, tla.lecture_or_lab, tla.lecture_lab_number, tla.tla_Resources  from clo  INNER JOIN allign_at_to_clo_m_to_m  ON clo.clo_name = allign_at_to_clo_m_to_m.clo_name   INNER JOIN allign_tla_to_clo_m_to_m  ON clo.clo_name = allign_tla_to_clo_m_to_m.clo_name  INNER JOIN tla  ON allign_tla_to_clo_m_to_m.tla_id = tla.tla_id  where clo.course_course_id=%s and allign_at_to_clo_m_to_m.assessment_name=%s"
            #values = (course_id, assessment_name)
            #query = "select distinct allign_tla_to_clo_m_to_m.tla_id , allign_at_to_clo_m_to_m.assessment_name,  tla.tla_topic, tla.lecture_or_lab, tla.lecture_lab_number, tla.tla_Resources  from clo  INNER JOIN allign_at_to_clo_m_to_m  ON clo.clo_name = allign_at_to_clo_m_to_m.clo_name   INNER JOIN allign_tla_to_clo_m_to_m  ON clo.clo_name = allign_tla_to_clo_m_to_m.clo_name  INNER JOIN tla  ON allign_tla_to_clo_m_to_m.tla_id = tla.tla_id  where clo.course_course_id=%s and allign_at_to_clo_m_to_m.assessment_name=%s"
            #values = (course_id, assessment_name)
            #query = "select distinct allign_tla_to_clo_m_to_m.tla_id , allign_at_to_clo_m_to_m.assessment_name,  tla.tla_topic, tla.lecture_or_lab, tla.lecture_lab_number, tla.tla_Resources  from clo  INNER JOIN allign_at_to_clo_m_to_m  ON clo.clo_name = allign_at_to_clo_m_to_m.clo_name   INNER JOIN allign_tla_to_clo_m_to_m  ON clo.clo_name = allign_tla_to_clo_m_to_m.clo_name  INNER JOIN tla  ON allign_tla_to_clo_m_to_m.tla_id = tla.tla_id  where clo.course_course_id=%s and allign_at_to_clo_m_to_m.assessment_name=%s"
            #query = "select distinct allign_tla_to_clo_m_to_m.tla_id , allign_at_to_clo_m_to_m.assessment_name, tla.tla_topic, tla.lecture_or_lab, tla.lecture_lab_number, tla.tla_Resources from clo INNER JOIN allign_at_to_clo_m_to_m  ON clo.clo_name = allign_at_to_clo_m_to_m.clo_name INNER JOIN allign_tla_to_clo_m_to_m  ON clo.clo_name = allign_tla_to_clo_m_to_m.clo_name INNER JOIN tla  ON allign_tla_to_clo_m_to_m.tla_id = tla.tla_id  where  allign_at_to_clo_m_to_m.assessment_name=%s and allign_tla_to_clo_m_to_m.course_id=%s"
            #values = (assessment_name, course_id)
            #query = "select distinct allign_tla_to_clo_m_to_m.tla_id , allign_at_to_clo_m_to_m.assessment_name, tla.tla_topic, tla.lecture_or_lab, tla.lecture_lab_number, tla.tla_Resources from clo INNER JOIN allign_at_to_clo_m_to_m  ON clo.clo_name = allign_at_to_clo_m_to_m.clo_name INNER JOIN allign_tla_to_clo_m_to_m  ON clo.clo_name = allign_tla_to_clo_m_to_m.clo_name INNER JOIN tla  ON allign_tla_to_clo_m_to_m.tla_id = tla.tla_id  where  allign_tla_to_clo_m_to_m.course_id=%s and allign_at_to_clo_m_to_m.course_id=%s and allign_at_to_clo_m_to_m.assessment_name=%s"
            query = "select allign_tla_to_at_m_to_m.tla_id, allign_tla_to_at_m_to_m.assessment_name, tla.tla_topic, tla.lecture_or_lab, tla.lecture_lab_number, tla.tla_Resources from  tla INNER JOIN allign_tla_to_at_m_to_m  ON tla.tla_id = allign_tla_to_at_m_to_m.tla_id where tla.course_course_id=%s and allign_tla_to_at_m_to_m.assessment_name=%s"
            values = (course_id, assessment_name)
            cityList = c.execute(query, values)
            revision_plan = c.fetchall()
        else:
            revision_plan=' '
            return render_template('std_dashboard2_no_revision_plan.html', assessment_name=assessment_name,\
                           std_id=std_id,\
                               course_id=course_id,\
                                           clo_assessment=clo_assessment,\
                                               std_name=std_name,\
                                                   std_mark=std_mark,\
                                                       course_name_not_id = course_name_not_id,\
                                                       assessment_average_mark=assessment_average_mark)
        #END OF revision plan
        #return render_template('empty3.html', data = revision_plan)

    except sql.Error as e: # if error
        # then display the error in 'database_error.html' page
        return render_template('database_error.html', error=e)

    finally:
        con.close() # close the connection


    #return render_template('bar_chart_assessment_detail.html', data = clo_assessment)
    #return render_template('bar_chart.html')

    return render_template('std_dashboard2.html', assessment_name=assessment_name,\
                           std_id=std_id,\
                               course_id=course_id, course_name_not_id = course_name_not_id, \
                                   revision_plan=revision_plan,\
                                           clo_assessment=clo_assessment,\
                                               std_name=std_name,\
                                                   std_mark=std_mark,\
                                                       assessment_average_mark=assessment_average_mark)


#NNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNN



#SSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSS



#\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\ Final Report \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
#this is the Get method to aviod two dynamic dropdown lists. Design a Course
@app.route('/final_report1_choose_course', methods=['GET', 'Post'])
@login_required
def final_report1_choose_course():
    if request.method == 'GET':
        try:
            con = sql.connect(host="pythonanywhere_host", user="pythonanywhere_user", password="pythonanywhere_password", database="pythonanywhere$database_name") #this is not the real connections details
            c =  con.cursor() # cursor
            #query = "Select * from course where userName=%s"
            query = "Select * from course_and_models where userName=%s"
            values = session["USERNAME"]
            cityList = c.execute(query, (values,))
            cityList = c.fetchall()

            return render_template('final_report1_choose_course.html', cityList=cityList)

        except sql.Error as e: # if error
            # then display the error in 'database_error.html' page
            return render_template('database_error.html', error=e)

        finally:
            con.close() # close the connection

    #else: # request.method == 'POST':
     #   courseName = request.form['course_course_id']
      #  return render_template('create_clo.html', courseName=courseName)


#\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\End OF final_report1_choose_course \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\

#this is for just to avoid two dynamic dropdown lists. this is the POST method from the Get method above: design_course
@app.route('/final_report1',methods=['POST'])
@login_required
def final_report1():

    #courseName = request.args.get('my_var')
    #return render_template('empty3.html', data = courseName)


    courseName = request.form['course_course_id']
    #return render_template('empty3.html', data = courseName)



    #courseName=courseName
    try:
        con = sql.connect(host="pythonanywhere_host", user="pythonanywhere_user", password="pythonanywhere_password", database="pythonanywhere$database_name") #this is not the real connections details
        c =  con.cursor() # cursor

        query = "Select distinct assessment_name from student_grade where course_id=%s"
        values = courseName
        cityList = c.execute(query, (values,))
        #labels = c.fetchall()
        assessment_name = [ row[0] for row in c.fetchall() if row[0] ] # i used this to return fetch the data without ()
        #return render_template('empty3.html', data = assessment_name)


        #here i want to get the average std mark in each assessment
        average_mark_of_each_assessment= []
        assessment_name_list=[]
        for i in assessment_name:
            query = "SELECT ROUND(avg(mark),2), assessment_name FROM student_grade where assessment_name=%s and course_id=%s"
            values = (i, courseName)
            cityList = c.execute(query, values)
            values = c.fetchall()
            #values = [ row[0] for row in c.fetchall() if row[0] ] # i used this to return fetch the data without ()
            values=values[0]
            assessment_name=values[1] # to append all assessment_name in a list
            average_mark_of_each_assessment.append(values[0]) # to append all mark in a list
            assessment_name_list.append(values[1])

        #return render_template('empty3.html', data = average_mark_of_each_assessment )

        #END OF here i want to get the average std mark in each assessment



        colors = [
            "#F7464A", "#46BFBD", "#FDB45C", "#FEDCBA",
            "#ABCDEF", "#DDDDDD", "#ABCABC", "#4169E1",
            "#C71585", "#FF4500", "#FEDCBA", "#46BFBD"]

        # here i tried to get assessment name in order for the bar char; however, it did not match with the avg value (For Ex. Assingment 1 ave mark is 22, but here is show Assigment to avg mark is 22)
        #query = "SELECT assessment_name FROM assessment where course_course_id=%s order by auto_increment"
        #values = (courseName)
        #c.execute(query, (values,))
        #bar_labels = c.fetchall()
        #bar_labels = [ row[0] for row in c.fetchall() if row[0] ] # i used this to return fetch the data without ()
        #return render_template('empty3.html', data = bar_labels)
        #bar_labels=assessment_name_list
        # END OF here i tried to get assessment name in order for the bar char; however, it did not match with the avg value (For Ex. Assingment 1 ave mark is 22, but here is show Assigment to avg mark is 22)

        bar_labels=assessment_name_list
        bar_values=average_mark_of_each_assessment

        #return render_template('empty3.html', data = bar_values )
        #return render_template('empty3.html', data = assessment_name)


        #box plot
        #query = "select mark from student_grade where assessment_name=%s and course_id=%s"
        #query = "SELECT ROUND(sum(unconverted_mark)/count(distinct student_id),1)  'std avg marks (total)'  FROM student_grade where course_id=%s"
        query = "select ROUND(sum(unconverted_mark),1) from student_grade where course_id=%s group by student_id"
        values = (courseName)
        box = c.execute(query, (values,))
        #box = c.fetchall()
        std_avg_total_mark = [ row[0] for row in c.fetchall() if row[0] ] # i used this to return fetch the data without ()
        box= std_avg_total_mark
        #return render_template('empty3.html', data = box)
        #return render_template('pie_chart2.html', box = box, assessment_name_of_last_prediciton=assessment_name_of_last_prediciton)

        #END OF box plot

        #return render_template('empty3.html', data = box )
        if not box:
            return render_template('empty3.html', data = "Some assessments marks are not uploaded to the system, please make sure to upload all assessments marks including the final assessment")







        # to get Course name
        #query= "SELECT  distinct assessment_name,  tla.clo_name FROM at_map_to_tla  INNER JOIN tla  ON at_map_to_tla.tla_id = tla.tla_id  WHERE at_map_to_tla.course_course_id=%s and assessment_name=%s order by at_map_to_tla.assessment_name"
        query= "SELECT course_name FROM course where course_id=%s"
        values=(courseName)
        c.execute(query, (values,))
        #number_of_assessment__predicted_so_far = c.fetchall()
        course_name_not_id=  [ row[0] for row in c.fetchall() if row[0] ]

        #return render_template('empty3.html', data = course_name_not_id )

        # END OF to get course name




        # to show the impact of the intervention

        #first i want to get the assessments name from the assessment table bcs it is in order
        query = "Select distinct assessment_name from assessment where course_course_id=%s order by auto_increment"
        values = (courseName)
        c.execute(query, (values,))
        assessment_name_list_ordered = [ row[0] for row in c.fetchall() if row[0] ]
        #return render_template('empty3.html', data = assessment_name_list_ordered )

        intervention_for_each_assessment = {} # to create a dictionary for the revision plan for each done assessment
        for user in assessment_name_list_ordered:
            #query = "SELECT std_intervention_table.student_id, std_intervention_table.student_name, student_prediction_results.assessment_name, student_prediction_results.Binary_prediction_results, student_prediction_results.Multiclass_prediction_results, ROUND(sum(student_grade.unconverted_mark ),1)  'Total Mark' FROM std_intervention_table INNER JOIN student_prediction_results  ON std_intervention_table.student_id = student_prediction_results.student_id INNER JOIN student_grade  ON student_grade.student_id = student_prediction_results.student_id where std_intervention_table.course_id=%s and std_intervention_table.assessment_name=%s and student_prediction_results.assessment_name=%s group by student_grade.student_id"
            query = "SELECT std_intervention_table.student_id, std_intervention_table.student_name, student_prediction_results.assessment_name, student_prediction_results.Binary_prediction_results, student_prediction_results.Multiclass_prediction_results, ROUND(sum(student_grade.unconverted_mark ),1)  'Total Mark', IF(ROUND(sum(student_grade.unconverted_mark ),1)>=50, 'Pass', 'Fail') 'Actual Result' FROM std_intervention_table INNER JOIN student_prediction_results  ON std_intervention_table.student_id = student_prediction_results.student_id INNER JOIN student_grade  ON student_grade.student_id = student_prediction_results.student_id where std_intervention_table.course_id=%s and std_intervention_table.assessment_name=%s and student_prediction_results.assessment_name=%s group by student_grade.student_id"
            values = (courseName, user, user)

            c.execute(query, values)

            data = c.fetchall()
            data = np.array(data)
            #print(data.shape)

            #d["Assessment {0}".format(i)] = data
            intervention_for_each_assessment["{0}".format(user)] = data

        #return render_template('empty3.html', data = intervention_for_each_assessment['Mid-semester quiz'])
        #return render_template('empty3.html', data = intervention_for_each_assessment)

        # END OF to show the impact of the intervention



        # start of compare btn current and previuos cohorts

        # 1 query of count of failled std in current cohort
        query = "select count(student_id) as total_of_failed_students_in_current_cohort from (select student_id, ROUND(sum(unconverted_mark),1) as total from student_grade where course_id=%s group by student_id)  src  where  total<50"
        values = (courseName)
        c.execute(query, (values,))
        current_cohort_failed_std = [ row[0] for row in c.fetchall() if row[0] ]
        #return render_template('empty3.html', data = current_cohort_failed_std)

        # 2 query of count of passed std in current cohort
        query = "select count(student_id) as total_of_passed_students_in_current_cohort from (select student_id, ROUND(sum(unconverted_mark),1) as total from student_grade where course_id=%s group by student_id)  src  where  total>=50"
        values = (courseName)
        c.execute(query, (values,))
        current_cohort_passed_std = [ row[0] for row in c.fetchall() if row[0] ]
        #return render_template('empty3.html', data = current_cohort_passed_std)

        # 3 query of count of failled std in previous cohorts
        query = "SELECT count(student_id) as count_of_failed, year, semester_or_trimester FROM student where course_course_id =%s and total<50 group by year , semester_or_trimester ORDER by year, semester_or_trimester"
        values = (courseName)
        c.execute(query, (values,))
        #previous_cohort_passed_std = [ row[0] for row in c.fetchall() if row[0] ]
        previous_cohort_failled_std = c.fetchall()
        #return render_template('empty3.html', data = previous_cohort_failled_std)
        #return render_template('empty3.html', data = type(previous_cohort_failled_std))


        # 4 query of count of passed std in previous cohorts
        query = "SELECT count(student_id) as count_of_passed, year, semester_or_trimester FROM student where course_course_id =%s and total>=50 group by year , semester_or_trimester ORDER by year, semester_or_trimester"
        values = (courseName)
        c.execute(query, (values,))
        #previous_cohort_passed_std = [ row[0] for row in c.fetchall() if row[0] ]
        previous_cohort_passed_std = c.fetchall()
        #return render_template('empty3.html', data = previous_cohort_passed_std)
        #return render_template('empty3.html', data = type(previous_cohort_passed_std))

        length_of_previous_cohort_passed_std = len(previous_cohort_failled_std)
        #return render_template('empty3.html', data = len(previous_cohort_failled_std))

        # END OF start of compare btn current and previuos cohorts



        # 5 query of to get label from previous cohorts
        query = "SELECT CONCAT(year, '-', semester_or_trimester) AS semester FROM student where course_course_id =%s and total>=50 group by year , semester_or_trimester ORDER by year, semester_or_trimester"
        values = (courseName)
        c.execute(query, (values,))
        #label_previous_cohort = [ row[0] for row in c.fetchall() if row[0] ]
        label_previous_cohort = c.fetchall()
        #return render_template('empty3.html', data = label_previous_cohort_passed_std)
        #return render_template('empty3.html', data = type(previous_cohort_passed_std))

        label_previous_cohort = [ row[0] for row in label_previous_cohort if row[0] ] # to get rid of " & ()
        label_previous_cohort.insert(0, "current cohort") # insert current cohort to the list

        value_previous_cohort_passed_std = [] # create a list to get only previous cohort pass rate value from query [# 4 query of count of passed std in previous cohorts]
        for i in previous_cohort_passed_std:
            if not i:
                i=0
            value_previous_cohort_passed_std.append(i[0])

        if not current_cohort_passed_std:
            return render_template('empty3.html', data = "Some assessments marks are not uploaded to the system, please make sure to upload all assessments marks including the final assessment")

        value_previous_cohort_passed_std.insert(0, current_cohort_passed_std [0] ) # to insert current cohort pass rate at the beginning of the list

        #return render_template('empty3.html', data = value_previous_cohort_passed_std)

        value_previous_cohort_failled_std = [] # create a list to get only previous cohort pass rate value from query [# 4 query of count of passed std in previous cohorts]
        for i in previous_cohort_failled_std:
            if not i:
                i=0
            value_previous_cohort_failled_std.append(i[0])

        value_previous_cohort_failled_std.insert(0, current_cohort_failed_std [0] ) # to insert current cohort pass rate at the beginning of the list

        #return render_template('empty3.html', data = value_previous_cohort_failled_std)

        # here i want to get pass/fail rate insead of number of pass/fail std in previous and current cohort

        # 6 query to count of std in each semester from previous cohorts
        query = "SELECT count(student_id) as count_of_failed FROM student where course_course_id =%s  group by year , semester_or_trimester ORDER by year, semester_or_trimester"
        values = (courseName)
        c.execute(query, (values,))
        total_of_std_in_each_previous_semester = [ row[0] for row in c.fetchall() if row[0] ]

        # this block to get pass rate for each previous cohort
        passed_rate_previous_cohort_passed_std=[]
        x=0
        m=len(previous_cohort_passed_std)
        for i in range (m):
            #round_results=round(float(previous_cohort_passed_std[x][0])/float(total_of_std_in_each_previous_semester[x])*100,1)
            #return render_template('empty3.html', data = round_results)
            passed_rate_previous_cohort_passed_std.append(round(float(previous_cohort_passed_std[x][0])/float(total_of_std_in_each_previous_semester[x])*100,1))
            #round(float(current_cohort_passed_std [0])/float(total_of_std_in_current_semester [0])*100, 1)
            x=x+1

        #return render_template('empty3.html', data = passed_rate_previous_cohort_passed_std)
        # END OF this block to get pass rate for each previous cohort

        # this block to get pass rate for each previous cohort
        fail_rate_previous_cohort_passed_std=[]
        x=0
        m=len(previous_cohort_failled_std)
        for i in range (m):
            fail_rate_previous_cohort_passed_std.append(round(float(previous_cohort_failled_std[x][0])/float(total_of_std_in_each_previous_semester[x])*100,1))
            x=x+1

        #return render_template('empty3.html', data = fail_rate_previous_cohort_passed_std)


        #return render_template('empty3.html', data = fail_rate_previous_cohort_passed_std)


        # END OF this block to get pass rate for each previous cohort


        #return render_template('empty3.html', data = fail_rate_previous_cohort_passed_std)


        # 7 query to count of std in current cohort
        query = "select count(distinct student_id) from student_grade where course_id=%s"
        values = (courseName)
        c.execute(query, (values,))
        total_of_std_in_current_semester = [ row[0] for row in c.fetchall() if row[0] ]
        #return render_template('empty3.html', data = total_of_std_in_current_semester)

        # this block to get pass/fail rate for current cohort

        if not current_cohort_failed_std:
            current_cohort_failed_std=0

        current_cohort_passed_std = round(float(current_cohort_passed_std [0])/float(total_of_std_in_current_semester [0])*100, 1)

        current_cohort_failled_std = round(float(current_cohort_failed_std [0])/float(total_of_std_in_current_semester [0])*100, 1)

        #return render_template('empty3.html', data = current_cohort_failled_std)

        # END OF this block to get pass rate for each previous cohort


        #value_previous_cohort_passed_std = [] # create a list to get only previous cohort pass rate value from query [# 4 query of count of passed std in previous cohorts]
        #for i in passed_rate_previous_cohort_passed_std:
        #    value_previous_cohort_passed_std.append(i[0])

        #return render_template('empty3.html', data = type(passed_rate_previous_cohort_passed_std[0]))
        #return render_template('empty3.html', data = type(current_cohort_failled_std))
        passed_rate_previous_cohort_passed_std.insert(0, float(current_cohort_passed_std)) # to insert current cohort pass rate at the beginning of the list

        #return render_template('empty3.html', data = value_previous_cohort_passed_std)

        #value_previous_cohort_failled_std = [] # create a list to get only previous cohort pass rate value from query [# 4 query of count of passed std in previous cohorts]
        #for i in fail_rate_previous_cohort_passed_std:
        #    value_previous_cohort_failled_std.append(i[0])

        fail_rate_previous_cohort_passed_std.insert(0, float(current_cohort_failled_std)) # to insert current cohort pass rate at the beginning of the list




        # END OF here i want to get pass/fail rate insead of number of pass/fail std in previous and current cohort





        #return render_template('temp2.html')

        return render_template('final_report1.html', title='Final Report Dashboard', max=100, labels=bar_labels, values=bar_values,\
                               courseName=courseName,\

                                       assessment_name_list = assessment_name_list,\

                                               box = box,\
                                                   course_name_not_id = course_name_not_id [0],\
                                                       assessment_name_list_ordered = assessment_name_list_ordered,\
                                                           intervention_for_each_assessment = intervention_for_each_assessment, \
                                                               current_cohort_failed_std = current_cohort_failed_std, \
                                                               current_cohort_passed_std = current_cohort_passed_std, \
                                                               previous_cohort_failled_std = previous_cohort_failled_std, \
                                                               previous_cohort_passed_std = previous_cohort_passed_std,\
                                                               length_of_previous_cohort_passed_std = length_of_previous_cohort_passed_std,\

                                                               label_previous_cohort=label_previous_cohort, \
                                                               value_previous_cohort_passed_std = passed_rate_previous_cohort_passed_std,\
                                                                   value_previous_cohort_failled_std = fail_rate_previous_cohort_passed_std
                                                   )

    except sql.Error as e: # if error
        # then display the error in 'database_error.html' page
        return render_template('database_error.html', error=e)

    finally:

        con.close() # close the connection


    #return render_template('create_clo.html', courseName=courseName)

#NNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNN



#SSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSS



#\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\ Upload Intervention Detail \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
@app.route('/upload_intervention_detail_choose_course') # this is the first GET function html that take you to/render_template  predict_csv.html
@login_required
def upload_intervention_detail_choose_course():
    try:
        con = sql.connect(host="pythonanywhere_host", user="pythonanywhere_user", password="pythonanywhere_password", database="pythonanywhere$database_name") #this is not the real connections details
        c =  con.cursor() # cursor

        #query = "Select * from course where userName=%s"
        query = "Select * from course_and_models where userName=%s"
        values = session["USERNAME"]
        cityList = c.execute(query, (values,))
        cityList = c.fetchall()

        return render_template('upload_intervention_detail_choose_course.html', cityList=cityList)

    except sql.Error as e: # if error
            # then display the error in 'database_error.html' page
            return render_template('database_error.html', error=e)

    finally:
        con.close() # close the connection


@app.route('/upload_intervention_detail_1',methods=['POST']) # this is the first GET function html that take you to/render_template  predict_csv.html
@login_required
def upload_intervention_detail_1(): #this is to aviod dynamic dropbox

    course_id = request.form['course_course_id']
    #return render_template('empty3.html', data = course_id)

    try:
        con = sql.connect(host="pythonanywhere_host", user="pythonanywhere_user", password="pythonanywhere_password", database="pythonanywhere$database_name") #this is not the real connections details
        c =  con.cursor() # cursor

        query = "SELECT assessment_name FROM assessment where course_course_id=%s order by auto_increment"
        values = course_id
        cityList = c.execute(query, (values,))
        cityList = c.fetchall()

        return render_template('upload_intervention_detail_1.html', cityList=cityList, course_id = course_id)

    except sql.Error as e: # if error
            # then display the error in 'database_error.html' page
            return render_template('database_error.html', error=e)

    finally:
        con.close() # close the connection




#this is for the making prediction without choosing ML algorithms [best model selected automalically]
@app.route('/upload_intervention_detail_2',methods=['POST'])
@login_required
def upload_intervention_detail_2():


    courseName = request.form['course_course_id']
    assessment_name = request.form['assessment_name']

    csv_file = request.files['file']
    if request.files['file'].filename != '': # if there is file the user upload it # i overcome this issue by making input file required
        #output=""   # i dont need it anymore
        csv_file = request.files['file']

        file_ext = os.path.splitext(request.files['file'].filename)[1]
        #return render_template('no_dashboard_yet.html', data = file_ext)
        if file_ext not in app.config['UPLOAD_EXTENSIONS']:
            return render_template('no_dashboard_yet.html', data = "please make sure to upload a csv file")


        csv_file = TextIOWrapper(csv_file, encoding='utf-8')
        csv_reader = csv.reader(csv_file, delimiter=',')
        next(csv_reader)
        data = [row for row in csv_reader]

        if len(data) == 0:
                return render_template('empty.html')

        #return render_template('empty3.html', data = data)
        data = np.array(data)
        #data= data [2:, :]
        data=data.tolist()
        #return render_template('empty3.html', data = data)

        #.......................................................................................................................





        #to know check how many column in array (data)
        columns = len(data[0])

        #here is just to test [not complete yet]
        if columns < 3:
                return render_template('no_dashboard_yet.html', data = "please make sure to upload a csv file has std name, std id, and email intervention msg")
        #here is just to test [not complete yet]
        if columns > 3:
                return render_template('no_dashboard_yet.html', data = "please make sure to upload a csv file has std name, std id, and email intervention msg")

    #return render_template('empty3.html', data = columns)
    #return render_template('empty3.html', data = type(columns))









        #99999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999

        data = np.array(data) #here i convert data (type: list i think) to array

        for row in data:

            for i in range(columns):





                try:# i used try and except ValueError, to solve if data in the csv file is not nubmber such as jkhkjnh

                    #row[i]=int(row[i]) #i used float because when using int any float number return it 0, so i had to use float



                    #999999999999999999999999999999999999999999999999999999999999999999999999
                    #3333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333
                    #here i want to make sure to match students_id btn student and assessments_Std tables
                    con = sql.connect(host="pythonanywhere_host", user="pythonanywhere_user", password="pythonanywhere_password", database="pythonanywhere$database_name") #this is not the real connections details
                    c = con.cursor() # cursor
                    c = con.cursor(buffered=True)

                    #00000000000000000000000000000000000000000000000000000000000000000000000000000000000000

                    #return render_template('empty3.html', data = row[1])
                    c.execute("insert ignore INTO std_intervention_table (student_id, student_name, course_id, assessment_name, intervention_message) VALUES (%s,%s,%s, %s,%s)", # REPLACE INTO: do as insert in do does except if the assessment_name (PK) already exist in the database it will replace it with the new record
                            (row[1], row[0], courseName, assessment_name, row[2]))
                    con.commit() # apply changes



                except sql.Error as e: # if error
                    # then display the error in 'database_error.html' page
                    return render_template('database_error.html', error=e)

                finally:
                    con.close() # close the connection

        #return render_template('empty3.html', data = len(data))
        return render_template('Thank_You.html', data = len(data))


#NNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNN




#SSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSS



#NNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNN




#SSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSS



#NNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNN





if __name__ == '__main__':
    # '0.0.0.0' = 127.0.0.1 i.e. localhost
    # port = 5000 : we can modify it for localhost
    app.run(host='0.0.0.0', port=5000, debug=True) # local webserver : app.run()