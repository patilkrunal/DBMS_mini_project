import sqlite3
import hashlib
import datetime
from flask_mysqldb import MySQL
from flask import Flask
import MySQLdb.cursors 
import re 

app = Flask(__name__)
mysql = MySQL(app)

def list_users():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor) 
    cursor.execute("SELECT username FROM users;") 
    l = cursor.fetchall()
    result = [x['username'] for x in l]
    return result

def verify(username, password):    
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT password FROM users WHERE username = '" + username + "';")

    result = cursor.fetchone()['password'] == hashlib.sha256(password.encode()).hexdigest()
    return result

def delete_user_from_db(username):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor) 
    cursor.execute("SELECT password FROM users WHERE username = '" + username + "';")
    
    cursor.execute("DELETE FROM users WHERE username = '" + username + "';")
    mysql.connection.commit()
    
    # when we delete a user FROM database USERS, we also need to delete all his or her notes data FROM database NOTES
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor) 
    cursor.execute("DELETE FROM notes WHERE user = '" + username + "';")
    mysql.connection.commit()
    
    # when we delete a user FROM database USERS, we also need to 
    # [1] delete all his or her images FROM image pool (done in app.py)
    # [2] delete all his or her images records FROM database IMAGES
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor) 
    cursor.execute("DELETE FROM files WHERE owner = '" + username + "';")
    mysql.connection.commit()
    

def add_user(username, pw):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor) 
    cursor.execute("INSERT INTO users values(?, ?)", (username, hashlib.sha256(pw.encode()).hexdigest()))
    mysql.connection.commit()
    

def read_note_from_db(username):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor) 

    command = "SELECT note_id, timestamp, note FROM notes WHERE user = '" + username + "';" 
    cursor.execute(command)
    result = cursor.fetchall()

    return result

def match_user_id_with_note_id(note_id):
    # Given the note id, confirm if the current user is the owner of the note which is being operated.
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor) 
    command = "SELECT user FROM notes WHERE note_id = '" + note_id + "';" 
    cursor.execute(command)
    result = cursor.fetchone()
    mysql.connection.commit()
    return result['user']

def write_note_into_db(id, note_to_write):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor) 
    current_timestamp = str(datetime.datetime.now())
    cursor.execute("INSERT INTO notes values(%s, %s, %s, %s, %s)", (None,id, current_timestamp, note_to_write, hashlib.sha1((id + current_timestamp).encode()).hexdigest()))
    mysql.connection.commit()

def delete_note_from_db(note_id):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor) 
    command = "DELETE FROM notes WHERE note_id = '" + note_id + "';" 
    cursor.execute(command)
    mysql.connection.commit()

def image_upload_record(uid, owner, image_name, timestamp):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor) 
    cursor.execute("INSERT INTO files VALUES (%s, %s, %s, %s)", (uid, owner, image_name, timestamp))
    mysql.connection.commit()
    
def list_images_for_user(owner):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor) 
    command = "SELECT uid, timestamp, name FROM files WHERE owner = '{0}'".format(owner)
    cursor.execute(command)
    result = cursor.fetchall()
    mysql.connection.commit()
    
    return result

def match_user_id_with_image_uid(image_uid):
    # Given the note id, confirm if the current user is the owner of the note which is being operated.
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor) 
    command = "SELECT owner FROM files WHERE uid = '" + image_uid + "';" 
    cursor.execute(command)
    result = cursor.fetchone()
    mysql.connection.commit()
    return result['owner']

def delete_image_from_db(image_uid):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)   
    command = "DELETE FROM files WHERE uid = '" + image_uid + "';" 
    cursor.execute(command)
    mysql.connection.commit()

def read_user_from_db(username , password):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor) 
    cursor.execute('SELECT * FROM users WHERE username = %s AND password = %s', (username, password, )) 
    result = cursor.fetchone() 
    
    return result

def read_user1_from_db(username):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor) 
    cursor.execute('SELECT * FROM users WHERE username = %s', (username, )) 
    result = cursor.fetchone()

    return result


def insert_user1_into_db(username, password):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('INSERT INTO users VALUES (%s, %s)', (username, hashlib.sha256(password.encode()).hexdigest()),)
    mysql.connection.commit()

if __name__ == "__main__":
    # print(list_users())
    pass
