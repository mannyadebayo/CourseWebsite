from flask import Flask, session, redirect, url_for, escape, request, render_template, g
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import text

app=Flask(__name__)
app.secret_key = b'abbas'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///assignment3.db'
db = SQLAlchemy(app)


# given a query, executes and returns the result
# (don't worry if you don't understand this code)
def query_db(query, args=(), one=False):
    cur = db.engine.execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv


@app.route('/', methods=['GET', 'POST'])
def home():
    if 'username' in session:
        return redirect(url_for('index'))
    else:
        return render_template('home.html')


# To keep track of who is logged in
current_user = ''
@app.route('/instructorlogin',methods=['GET','POST'])
def instructor():
    if 'username' in session:
        return redirect(url_for('home'))
    elif request.method == 'GET':
        return render_template('instructorLoginSignup.html')
    else:
        myUsername = request.form['username']
        myPassword = request.form['password']
        myQuery = "SELECT * FROM Instructors where usernames is " + '"' + request.form['username'] + '"'
        results = db.engine.execute(text(myQuery))
        # loop through the returned query to get all rows with username the one entered by the user
        for item in results:
            if item['usernames'] == myUsername and item['password'] == myPassword:
                global instructor_username
                instructor_username = request.form['username']
                session['username']=myUsername, 'instructor'
                return redirect(url_for('home'))
        incorrect = 'Incorrect password or username'
        return render_template('instructorLoginSignup.html', incorrect=incorrect)

@app.route('/instructorSignup',methods=['GET','POST'])
def instructorSignup():
    items = []
    if 'username' in session:
        return redirect(url_for('home'))
    elif request.method == 'GET':
        return render_template('instructorSignup.html')
    else:
        firstname = '"' + request.form['firstname'] + '"'
        lastname = '"' + request.form['lastname'] + '"'
        username = '"' + request.form['username'] + '"'
        password = '"' + request.form['password'] + '"'
        myQuery = "SELECT * FROM Instructors where usernames is " + '"' + request.form['username'] + '"'
       	insert_Query = "INSERT INTO Instructors (firstname, lastname, usernames, password) values(" + firstname + "," + lastname + ',' + username + ',' + password + ')' 
        results = db.engine.execute(text(myQuery))
        for item in results:
            items.append(item)
        if len(items) > 0:
        	taken = "username already taken"
        	return render_template('instructorSignup.html', taken=taken)
        else:
        	if request.form['firstname'] == "" or request.form['lastname'] == "" or request.form['username'] == "" or request.form['password'] == "":
        		empty = "please make sure all fields are filled"
        		return render_template('instructorSignup.html', empty=empty)
        	# Another case you want to take care of, is special characters including underscores
        	elif not (request.form['username'].isalnum()):
				right_values = """ Please make sure that there are special characters in your username
				including underscores
				"""
				return render_template('student-signup.html', right_values = right_values)
        	# Check to make sure no numbers are entered for firstname, last name and not all
			# characters in username are numbers
        	elif not ( request.form['firstname'].isalpha() and request.form['lastname'].isalpha() and not request.form['username'].isdigit()):
        		right_values = """Please make sure you enter alphanumeric characters for your Firstname and Lastname.
        		with no spaces and usernmames cannot be all numbers"""
        		empty = ''
        		return render_template('instructorSignup.html', empty=empty, right_values = right_values)
        	else:
	            results = db.engine.execute(text(insert_Query))
	            global instructor_username
            	instructor_username = request.form['username']
            	session['username']= request.form['username'], 'instructor'
            	return redirect(url_for('home'))


@app.route('/student', methods = ['GET', 'POST'])
def student():
	incorrect = ''
	if 'username' in session:
		return redirect(url_for('index'))
	elif request.method == 'POST':
		incorrect = 'Incorect password or Username'
		# First get the username and password from the site
		check_username = '"' + request.form['username'] + '"'
		check_password = '"' + request.form['password'] + '"'
		# Now verify the username first, then password
		username_query = """
		SELECT *
		FROM student WHERE username is """ + check_username
		student = db.engine.execute(text(username_query))
		# Now loop through the data
		for info in student:
			if request.form['username'] == info['username']:
				if request.form['password'] == info['password']:
					session['username']=request.form['username'], 'student'
					global current_user
					current_user = request.form['username']
					return redirect(url_for('index'))
		# It will return this is the query never found a row with the username
		# or the password is wrong
		return render_template('student.html', incorrect = incorrect)


	else:
		return render_template('student.html', incorrect = incorrect)


@app.route('/student-signup', methods = ['GET', 'POST'])
def student_signup():
	if 'username' in session:
		return render_template('index.html')

	elif request.method == 'POST':
		taken = ''
		# FIRST REQUIRE THEM TO SIGN UP
		students = []
		check_username = '"' + request.form['username'] + '"'
		# Check if the given username is already in use
		check_query = """ SELECT * FROM student WHERE username is """
		for each_student in query_db(check_query + check_username):
			students.append(each_student)
		# Check if the student is in the database
		if len(students) > 0:
			taken = 'username is taking, pick another one'
			return render_template('student-signup.html', data=students, taken = taken)
		else:
			# Here you want to make sure that no field is empty
			if request.form['firstname'] == "" or request.form['lastname'] == "" or request.form['username'] == "" or request.form['password'] == "":
				empty = 'Please make sure all fields are filled'
				return render_template('student-signup.html', empty = empty)
			# Another case you want to take care of, is special characters including underscores
			elif not (request.form['username'].isalnum()):
				right_values = """ Please make sure that there are special characters in your username
				including underscores
				"""
				return render_template('student-signup.html', right_values = right_values)
			# Check to make sure no numbers are entered for firstname, last name and not all
			# characters in username are numbers
			elif not (request.form['firstname'].isalpha() and request.form['lastname'].isalpha() and not request.form['username'].isdigit()):
				empty = ''
				right_values = """please enter alphanumeric characters for firstname and lastname
				with no spaces and username cannot be all numbers"""
				return render_template('student-signup.html', right_values = right_values)
			else:
				# If the student is missing, then add them to the database
				check_firstname = '"' + request.form['firstname'] + '"'
				check_lastname = '"' + request.form['lastname'] + '"'
				check_username = '"' + request.form['username'] + '"'
				check_password = '"' + request.form['password'] + '"'

				signup_query = """ INSERT INTO student(username, password, firstname, lastname)
				VALUES (""" + check_username + ',' + check_password + ',' + check_firstname + ',' + check_lastname + ');'
				# now create a query to input them into the grades database
				grade_query = """ 
				INSERT INTO grades(username, firstname, lastname)
				VALUES (""" + check_username + ',' + check_firstname + ',' + check_lastname + ');'
				# Create a session
				session['username']=request.form['username'], 'student'
				global current_user
				current_user = request.form['username']
				# Execute both Queries
				db.engine.execute(text(signup_query))
				db.engine.execute(text(grade_query))
				# Then create session and log them in and redirect to home page
				return redirect(url_for('index'))
	else:
		return render_template('student-signup.html')


# HOME PAGE AFTER THEY LOG IN
@app.route('/home', methods = ['GET', 'POST'])
def index():
	if 'username' in session:
		return render_template('index.html')
	else:
		return render_template('home.html')


@app.route('/grades', methods = ['GET', 'POST'])
def grades():
	if 'username' in session:
		# You want to be able to know if it is a student or instructor
		if 'student' in session['username']:
			if request.method == 'POST':
				# Here you want to add their requests to the database
				midtermremark = "'" + request.form['midterm'] + "'"
				finalremark = "'" + request.form['finalexam'] + "'"
				a1remark = "'" + request.form['assignment1'] + "'"
				a2remark = "'" + request.form['assignment2'] + "'"
				labremark = "'" + request.form['lab'] + "'"
				# now add things to the database
				if request.form['midterm'] != '':
					query = """
					UPDATE grades
					SET midtermremark = """ + midtermremark + 'WHERE username =' "'" + str(session['username'][0]) + "'"
					db.engine.execute(text(query))
				if request.form['finalexam'] != '':
					query = """
					UPDATE grades
					SET finalremark = """ + finalremark + 'WHERE username =' "'" + str(session['username'][0]) + "'"
					db.engine.execute(text(query))
				if request.form['assignment1'] != '':
					query = """
					UPDATE grades
					SET a1remark = """ + a1remark + 'WHERE username =' "'" + str(session['username'][0]) + "'"
					db.engine.execute(text(query))

				if request.form['assignment2'] != '':
					query = """
					UPDATE grades
					SET a2remark = """ + a2remark + 'WHERE username =' "'" + str(session['username'][0]) + "'"
					db.engine.execute(text(query))

				if request.form['lab'] != '':
					query = """
					UPDATE grades
					SET labremark = """ + labremark + 'WHERE username =' "'" + str(session['username'][0]) + "'"
					db.engine.execute(text(query))

				# This is for after they send their request
				grade_query = """
				SELECT * FROM grades
				WHERE username is """ + "'" + str(session['username'][0]) + "'"
				student_grades = db.engine.execute(text(grade_query))
				message = 'Your Remark has been submitted'
				return render_template('student-grades.html', student_grades =student_grades, request = message)

			else:
				user = "'" + current_user + "'"
				# Now you want get the grades for the username
				message = ''
				grade_query = """
				SELECT * FROM grades
				WHERE username is """ + "'" + str(session['username'][0]) + "'"
				student_grades = db.engine.execute(text(grade_query))
				return render_template('student-grades.html', student_grades =student_grades, request=message)

		elif 'instructor' in session['username']:
			# First you want to check if there is a post request to see if the instructor
			# has asked for a specific student and is student selected is not empty
			if request.method == 'POST':
				student_selected = "'" + request.form['username'] + "'"
				# YOU WANT TO GET THE REMARK REQUEST DEPENDING ON WHAT STDUENT IS SELECTED
				# AND THEN SEND THE RESULT TO THE HTML PAGE, you have this under
				# student_selected
				request_query = """
				SELECT midtermremark, finalremark, a1remark, a2remark, labremark 
				FROM grades WHERE username is """ + student_selected
				student_request = db.engine.execute(text(request_query))

				# When it is a post request, you want to collect what they answered and
				# query the database
				grade_query = """
				SELECT * FROM grades
				WHERE username is """ + student_selected
				student_grades = db.engine.execute(text(grade_query))
				# You also want to make sure that they can re-select any other student
				students_query = """
				SELECT * FROM grades
				"""
				students = db.engine.execute(text(students_query))
				# This is show the button AFTER a student has been selected
				button = 'true'
				# This is to store the value of the username of the student for future use
				if student_selected != '':
					global current_student
					current_student = student_selected
				return render_template('instructor-grades.html', student_grades = student_grades, students = students, button=button, 
					current=current_student, student_request = student_request)

			else:
				# now get the usernames, firstnames and last names of all the students
				students_query = """
				SELECT * FROM grades
				"""
				students = db.engine.execute(text(students_query))
				return render_template('instructor-grades.html', students = students)
	else:
		return redirect(url_for('home'))

@app.route('/change-grades', methods=['GET', 'POST'])
def change_grades():
	if 'username' in session:
		if 'student' in session['username']:
			return redirect(url_for('home'))
		elif 'instructor' in session['username']:
			# First get the grades of the current user
			if request.method == 'POST':
				# Now you want to account for every case so that you do not make a grade
				# blank when nothing is entered
				if request.form['midterm'] != '' and request.form['midterm'].isnumeric():
					new_grade = """
					UPDATE grades
					SET midterm = """ + request.form['midterm'] + ' WHERE username is' + current_student
					db.engine.execute(text(new_grade))
					#return redirect(url_for('grades'))
				if request.form['finalexam'] != '' and request.form['finalexam'].isnumeric():
					new_grade = """
					UPDATE grades
					SET finalexam = """ + request.form['finalexam'] + ' WHERE username is' + current_student
					db.engine.execute(text(new_grade))
					#return redirect(url_for('grades'))
				if request.form['assignment1'] != '' and request.form['assignment1'].isnumeric():
					new_grade = """
					UPDATE grades
					SET assignment1 = """ + request.form['assignment1'] + ' WHERE username is' + current_student
					db.engine.execute(text(new_grade))
					#return redirect(url_for('grades'))
				if request.form['assignment2'] != '' and request.form['assignment2'].isnumeric():
					new_grade = """
					UPDATE grades
					SET assignment2 = """ + request.form['assignment2'] + ' WHERE username is' + current_student
					db.engine.execute(text(new_grade))
					#return redirect(url_for('grades'))
				if request.form['lab'] != '' and request.form['lab'].isnumeric():
					new_grade = """
					UPDATE grades
					SET lab = """ + request.form['lab'] + ' WHERE username is' + current_student
					db.engine.execute(text(new_grade))
					#return redirect(url_for('grades'))
				return redirect(url_for('grades'))
			else:
				if current_student != '':
					grade_query = """
					SELECT * FROM grades
					WHERE username is """ + current_student
					student_grades = db.engine.execute(text(grade_query))
					return render_template('change-grades.html', student_grades=student_grades)
				else:
					return redirect(url_for('grades'))

	else:
		return redirect(url_for('home'))

@app.route('/feedback', methods = ['GET', 'POST'])
def feedback():
	# If they are logged in AND thery are trying to submit something
	try:
		if 'username' in session:
			if 'instructor' in session['username']:
				query_one = """SELECT * from Instructors where usernames is """ + '"' + instructor_username + '"'
				instructor_info = db.engine.execute(text(query_one))
				query = """SELECT * FROM Feedback WHERE usernames is """ + '"' + instructor_username + '"' 
				answers = db.engine.execute(text(query))
				return render_template('instructorFeedback.html', instructor=instructor_info, answers=answers)
			else:
				if request.method == 'GET':
					query = """SELECT * FROM Instructors"""
					instructors = db.engine.execute(text(query))
					return(render_template('studentFeedback.html', instructors=instructors))
				else:
					ins_name = '"' + request.form['instructorName'] + '"'
	                question1_answer = '"' + request.form['question1'] + '"'
	                question2_answer = '"' + request.form['question2'] + '"'
	                question3_answer = '"' + request.form['question3'] + '"'
	                question4_answer = '"' + request.form['question4'] + '"'
	                if request.form['question1'] == "" or request.form['question2'] == "" or request.form['question3'] == "" or request.form['question4'] == "":
	                	query = """SELECT * FROM Instructors"""
	                	instructors = db.engine.execute(text(query))
	                	message = 'Please make sure that all the fields are filled.'
	                	return render_template('studentFeedback.html', message=message, instructors=instructors)
	                query = """
	                INSERT INTO Feedback(usernames, question1, question2, question3, question4) 
	                VALUES (""" + ins_name +',' + question1_answer +  ',' + question2_answer + ',' + question3_answer + ',' + question4_answer + ')'
	                #query_list.append("INSERT INTO Question1 (usernames, answer) values (" + '"' + ins_name + '"' + ', ' + question1_answer + ')')
	                #query_list.append("INSERT INTO Question2 (usernames, answer) values (" + '"' + ins_name + '"' + ', ' + question2_answer + ')')
	                #query_list.append("INSERT INTO Question3 (usernames, answer) values (" + '"' + ins_name + '"' + ', ' + question3_answer + ')')
	                #query_list.append("INSERT INTO Question4 (usernames, answer) values (" + '"' + ins_name + '"' + ', ' + question4_answer + ')')
	                #for query in query_list:
	                	#query_executer(query)
	                # So they can reselect a different instructor
	                db.engine.execute(text(query))
	                query = """SELECT * FROM Instructors"""
	                instructors = db.engine.execute(text(query))
	                
	                response = 'Your reponse has been recorded!'
	                return render_template('studentFeedback.html', response=response, instructors=instructors)
		
		if 'username' not in session:
			return redirect(url_for('home'))
	except:
		return redirect(url_for('logout'))
	


@app.route('/calendar', methods = ['GET', 'POST'])
def calendar():
	if 'username' in session:
		return render_template('calendar.html')
	else:
		return redirect(url_for('home'))
@app.route('/announcements', methods = ['GET', 'POST'])
def announcements():
	if 'username' in session:
		return render_template('announcements.html')
	else:
		return redirect(url_for('home'))
@app.route('/resources', methods = ['GET', 'POST'])
def resources():
	if 'username' in session:
		return render_template('resources.html')
	else:
		return redirect(url_for('home'))

@app.route('/lectures', methods = ['GET', 'POST'])
def lectures():
	if 'username' in session:
		return render_template('lectures.html')
	else:
		return redirect(url_for('home'))
@app.route('/assignments', methods = ['GET', 'POST'])
def assignments():
	if 'username' in session:
		return render_template('assignments.html')
	else:
		return redirect(url_for('home'))
@app.route('/statistics', methods = ['GET', 'POST'])
def statistics():
	if 'username' in session:
		return render_template('statistics.html')
	else:
		return redirect(url_for('home'))
@app.route('/tutorials', methods = ['GET', 'POST'])
def tutorials():
	if 'username' in session:
		return render_template('tutorials.html')
	else:
		return redirect(url_for('home'))
@app.route('/logout')
def logout():
	session.pop('username', None)
	return redirect(url_for('home'))


@app.route('/debug', methods = ['GET', 'POST'])
def debug():
	return render_template('sample.html', random=random)


if __name__=="__main__":
	app.run(debug=False, host='0.0.0.0', port=5000)
