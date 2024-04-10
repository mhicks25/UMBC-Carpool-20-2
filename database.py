import sqlite3

conn = sqlite3.connect('database.db')
conn.execute('PRAGMA foreign_keys = ON')

def create_table():
  conn.execute('''
  CREATE TABLE IF NOT EXISTS student (
    student_id INTEGER PRIMARY KEY AUTOINCREMENT,
    fname VARCHAR(500), 
    lname VARCHAR(500), 
    street_name VARCHAR(500), 
    city VARCHAR(500),
    state VARCHAR(2),
    zipcode INT(5),
    age INT(2),
    num INT(10),
    email VARCHAR(500) UNIQUE,
    pswd_hash TEXT,
    pswd_salt TEXT,
    role TEXT CHECK(role IN ('driver', 'passenger'))
  )
  ''')

  conn.execute('''
    CREATE TABLE IF NOT EXISTS driver (
      driver_id INTEGER PRIMARY KEY AUTOINCREMENT,
      student_id INT,
      lic VARCHAR(500),
      lic_plate VARCHAR(20),
      FOREIGN KEY (student_id) REFERENCES student(student_id)
    )
  ''')

  conn.execute('''
    CREATE TABLE IF NOT EXISTS passenger (
      passenger_id INTEGER PRIMARY KEY AUTOINCREMENT,
      student_id INT,
      FOREIGN KEY (student_id) REFERENCES student(student_id)
    )
  ''')

  conn.execute('''
    CREATE TABLE IF NOT EXISTS trip (
    trip_id INTEGER PRIMARY KEY AUTOINCREMENT,
    driver_id INTEGER,
    passenger_id INTEGER,
    status TEXT,
    FOREIGN KEY (driver_id) REFERENCES driver(driver_id),
    FOREIGN KEY (passenger_id) REFERENCES passenger(passenger_id)
               )
   ''')
  conn.commit()
  conn.close()
