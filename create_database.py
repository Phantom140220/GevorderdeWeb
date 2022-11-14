import sqlite3
from flask_bcrypt import bcrypt
try:
    connection = sqlite3.connect('database.db')
    cursor = connection.cursor()
    cursor.execute('''CREATE TABLE "log" (
	"id"	INTEGER NOT NULL UNIQUE,
	"user_id"	INTEGER NOT NULL,
	"time"	NUMERIC NOT NULL,
	"a1"	INTEGER NOT NULL,
	"b1"	INTEGER NOT NULL,
	"c1"	INTEGER NOT NULL,
	"a2"	INTEGER NOT NULL,
	"b2"	INTEGER NOT NULL,
	"c2"	INTEGER NOT NULL,
	"a3"	INTEGER NOT NULL,
	"b3"	INTEGER NOT NULL,
	"c3"	INTEGER NOT NULL,
	"a4"	INTEGER NOT NULL,
	"b4"	INTEGER NOT NULL,
	"c4"	INTEGER NOT NULL,
	"a5"	INTEGER NOT NULL,
	"b5"	INTEGER NOT NULL,
	"c5"	INTEGER NOT NULL,
	PRIMARY KEY("id" AUTOINCREMENT)
)''')
    connection.commit()
    cursor.execute('''CREATE TABLE "user" (
	"user_id"	INTEGER NOT NULL UNIQUE,
	"first_name"	TEXT NOT NULL,
	"last_name"	TEXT NOT NULL,
	"email"	TEXT NOT NULL,
	"password"	TEXT NOT NULL,
	"admin"	INTEGER,
	PRIMARY KEY("user_id" AUTOINCREMENT)
)''')
    connection.commit()
    cursor.execute("INSERT INTO user (first_name, last_name, email, password, admin) values (?,?,?,?,?)",('admin', 'admin', 'admin@admin.be', bcrypt.generate_password_hash('pass'), '1'))
    connection.commit()
                    
    connection.close()
except Exception as e:
    print(e)
