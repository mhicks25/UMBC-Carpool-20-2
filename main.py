import sqlite3
import database
import bcrypt

from flask import Flask, redirect, render_template, request, session, flash, url_for #type: ignore

app = Flask(__name__)

# using a secret key to securely sign the session cookie
# will change this key tuesday
app.secret_key = 'your_secret_key'

@app.route('/')
def index():
  return render_template('index.html')

# changed to improved the login page to access the database
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        pswd = request.form.get('psw')
        
        # Connect to the database
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        
        # Retrieve hashed password from database
        database_pswd = cursor.execute('SELECT pswd_hash FROM student WHERE email = ?', (email,)).fetchone()
        
        #input_pswd = bcrypt.hashpw(pswd.encode('utf-8'), database_pswd[1])
        
        if database_pswd is None:
            # The email is not found in the database, so display an error message
            flash('Invalid email or password')
            return redirect(url_for('login'))
          
        # Decode the hashed password from bytes to str
        database_pswd = database_pswd[0].decode('utf-8')
        
        if bcrypt.checkpw(pswd.encode('utf-8'),database_pswd.encode('utf-8')):
          # Check if the email, password, and role match records in the database
          result = cursor.execute('SELECT * FROM student WHERE email = ?',(email,)).fetchone()
          conn.close()
          
          if result:
            # Redirect to a different page based on the role
            if result[11] == 'driver':
              # Store the student ID and role in the session
              session['student_id'] = result[0]
              session['role'] = result[11]
              return redirect('driver')
            else:
              # Store the student ID and role in the session
              session['student_id'] = result[0]
              session['role'] = result[11]
              return redirect('passenger')
          else:
            # Login failed, show an error message
            flash('Invalid email or password', 'error')
            
        conn.close()
          
    return render_template('login.html')

@app.route('/dropdown.html')
def dropdown():
  return render_template('dropdown.html')


@app.route('/edit')
def EditProfile():
  
    #check if student id is in session
    #if not reuturn to login
    if 'student_id' not in session:
        return redirect(url_for('login'))
      
    student_id = session['student_id']
      
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    student_info = getStudentInfo(student_id)
      
    return render_template('EditProfile.html', student_info=student_info)
  
@app.route('/edit_profile', methods=['POST'])
def edit_profile():
  
  conn = sqlite3.connect('database.db')
  cursor = conn.cursor()
  
  if request.method == 'POST':
        student_info = {
            'fname': request.form['fname'],
            'lname': request.form['lname'],
            'street_name': request.form['street_name'],
            'city': request.form['city'],
            'state': request.form['state'],
            'zipcode': request.form['zipcode'],
            'age': request.form['age'],
            'num': request.form['num'],
        }

        conn.execute('UPDATE student SET fname=?, lname=?, street_name=?, city=?, state=?, zipcode=?, age=?, num=? WHERE student_id =?',
                     (student_info['fname'], student_info['lname'], student_info['street_name'], student_info['city'], student_info['state'], student_info['zipcode'],
                      student_info['age'], student_info['num'], session['student_id']))

        conn.commit()
        conn.close()
        
  conn.close()
  return redirect(url_for('EditProfile'))


@app.route('/settings')
def settings():
  return render_template('settings.html')


@app.route('/driver')
def driver():
  return render_template('driver.html')


@app.route('/passenger')
def passenger():
  return render_template('passenger.html')


#register page
@app.route('/register')
def register():
  return render_template('register.html')

#delete account
@app.route('/delete_account', methods=['POST'])
def delete_account():
    if 'student_id' in session:
        student_id = session['student_id']  # retrieving student_id from session
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
      
        # perform the deletion operations, using student_id
        cursor.execute('DELETE FROM student WHERE student_id = ?', (student_id,))
        cursor.execute('DELETE FROM driver WHERE student_id = ?', (student_id,))
        cursor.execute('DELETE FROM passenger WHERE student_id = ?', (student_id,))
        conn.commit()
        conn.close()

        # clear the session or log the user out
        session.pop('student_id', None)  # clearing student_id from session

        return redirect('login')
    else:
        # user is not logged in or student_id is not in session
        return 'Error: User not found', 404

#register page - form is submitted
@app.route('/reg_success', methods=['POST'])
def reg_success():
  
  #get the data from the form
  #student info
  fname = request.form.get('fname')
  lname = request.form.get('lname')
  street_name = request.form.get('street_name')
  city = request.form.get('city')
  state = request.form.get('state')
  zipcode = request.form.get('zipcode')
  age = request.form.get('age')
  num = request.form.get('num')
  email = request.form.get('email')
  pswd = request.form.get('psw')

  #choice between driver and passenger
  role = request.form.get('role')

  #driver info
  lic = request.form.get('lic') or None
  lic_plate = request.form.get('lic_plate') or None
  
  salt = bcrypt.gensalt()
  hashed_password = bcrypt.hashpw(pswd.encode('utf-8'), salt)

  #connect to the database
  conn = sqlite3.connect('database.db')
  cursor = conn.cursor()

  #insert the data from form into student
  cursor.execute('INSERT INTO student (fname, lname, street_name, city, state, zipcode, age, num, email, pswd_hash, pswd_salt, role) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', (fname, lname, street_name, city, state, zipcode, age, num, email, hashed_password, salt, role))
  #get student_id from student
  student_id = cursor.lastrowid
  
  #insert the data from form into driver
  if(role == 'driver'):
    cursor.execute('INSERT INTO driver (student_id, lic, lic_plate) VALUES (?,?,?)', (student_id,lic, lic_plate))
  else:
    #insert the data from form into passenger
    cursor.execute('INSERT INTO passenger (student_id) VALUES (?)', (student_id,))

  conn.commit()
  conn.close()
  
  return redirect('login')

def create_database():
  conn = sqlite3.connect('database.db')
  database.create_table()
  conn.close()


def getStudentInfo(student_id):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM student WHERE student_id = ?', (student_id,))
    student = cursor.fetchone()

    conn.close()

    return student


if __name__ == '__main__':
  create_database()
  app.run(host='0.0.0.0', port=80)
