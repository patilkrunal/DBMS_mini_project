import re
import os
import datetime
import hashlib
from werkzeug.utils import secure_filename
from database import app
from flask import session, url_for, redirect, render_template, request, abort, flash
from database import (
  list_users, verify, delete_user_from_db, add_user, 
  read_note_from_db, write_note_into_db, delete_note_from_db, match_user_id_with_note_id, 
  image_upload_record, list_images_for_user, match_user_id_with_image_uid, delete_image_from_db,
  read_user_from_db, read_user1_from_db, insert_user1_into_db
  )

app.config.from_object('config')

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'root'
app.config['MYSQL_DB'] = 'miniproject'


@app.route("/")
def FUN_root():
    return render_template("index.html")


@app.route("/private/")
def FUN_private():
    if "current_user" in session.keys():
        notes_list = read_note_from_db(session['current_user'])
        
        notes_table = zip([x['note_id'] for x in notes_list],\
                          [str(x['timestamp']) for x in notes_list],\
                          [x['note'] for x in notes_list],\
                          ["/delete_note/" + x['note_id'] for x in notes_list])

        images_list = list_images_for_user(session['current_user'])
        images_table = zip([x['uid'] for x in images_list],\
                          [x['timestamp'] for x in images_list],\
                          [x['name'] for x in images_list],\
                          ["/delete_image/" + x['uid'] for x in images_list])

        return render_template("private_page.html", notes = notes_table, images = images_table)
    else:
        return abort(401)


@app.route("/admin/")
def FUN_admin():
    if session.get("current_user", None) == "admin":
        user_list = list_users()
        user_table = zip(range(1, len(user_list)+1),\
                        user_list,\
                        [x + y for x,y in zip(["/delete_user/"] * len(user_list), user_list)])
        return render_template("admin.html", users = user_table)
    else:
        return abort(401)


@app.route("/write_note", methods = ["POST"])
def FUN_write_note():
    text_to_write = request.form.get("text_note_to_take")
    write_note_into_db(session['current_user'], text_to_write)

    return(redirect(url_for("FUN_private")))


@app.route("/delete_note/<note_id>", methods = ["GET"])
def FUN_delete_note(note_id):
    if session.get("current_user", None) == match_user_id_with_note_id(note_id): # Ensure the current user is NOT operating on other users' note.
        delete_note_from_db(note_id)
    else:
        return abort(401)
    return(redirect(url_for("FUN_private")))


ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif', 'pdf', 'doc', 'txt', 'docx'])
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/upload_image", methods = ['POST'])
def FUN_upload_image():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return(redirect(url_for("FUN_private")))
        file = request.files['file']
        # if user does not select file, browser also submit a empty part without filename
        if file.filename == '':
            flash('No selected file')
            return(redirect(url_for("FUN_private")))
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            upload_time = str(datetime.datetime.now())
            image_uid = hashlib.sha1((upload_time + filename).encode()).hexdigest()
            # Save the image into UPLOAD_FOLDER
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], image_uid + "-" + filename))
            # Record this uploading in database
            image_upload_record(image_uid, session['current_user'], filename, upload_time)
            return(redirect(url_for("FUN_private")))

    return(redirect(url_for("FUN_private")))


@app.route("/delete_image/<image_uid>", methods = ["GET"])
def FUN_delete_image(image_uid):
    if session.get("current_user", None) == match_user_id_with_image_uid(image_uid): # Ensure the current user is NOT operating on other users' note.
        # delete the corresponding record in database
        delete_image_from_db(image_uid)
        # delete the corresponding image file from image pool
        image_to_delete_from_pool = [y for y in [x for x in os.listdir(app.config['UPLOAD_FOLDER'])] if y.split("-", 1)[0] == image_uid][0]
        os.remove(os.path.join(app.config['UPLOAD_FOLDER'], image_to_delete_from_pool))
    else:
        return abort(401)
    return(redirect(url_for("FUN_private")))


@app.route("/delete_user/<id>/", methods = ['GET'])
def FUN_delete_user(id):
    if session.get("current_user", None) == "ADMIN":
        if id == "ADMIN": # ADMIN account can't be deleted.
            return abort(403)

        # [1] Delete this user's images in image pool
        images_to_remove = [x[0] for x in list_images_for_user(id)]
        for f in images_to_remove:
            image_to_delete_from_pool = [y for y in [x for x in os.listdir(app.config['UPLOAD_FOLDER'])] if y.split("-", 1)[0] == f][0]
            os.remove(os.path.join(app.config['UPLOAD_FOLDER'], image_to_delete_from_pool))
        # [2] Delele the records in database files
        delete_user_from_db(id)
        return(redirect(url_for("FUN_admin")))
    else:
        return abort(401)


@app.route("/add_user", methods = ["POST"])
def FUN_add_user():
    if session.get("current_user", None) == "ADMIN": # only Admin should be able to add user.
        # before we add the user, we need to ensure this is doesn't exsit in database. We also need to ensure the id is valid.
        if request.form.get('id') in list_users():
            user_list = list_users()
            user_table = zip(range(1, len(user_list)+1),\
                            user_list,\
                            [x + y for x,y in zip(["/delete_user/"] * len(user_list), user_list)])
            return(render_template("admin.html", id_to_add_is_duplicated = True, users = user_table))
        if " " in request.form.get('id') or "'" in request.form.get('id'):
            user_list = list_users()
            user_table = zip(range(1, len(user_list)+1),\
                            user_list,\
                            [x + y for x,y in zip(["/delete_user/"] * len(user_list), user_list)])
            return(render_template("admin.html", id_to_add_is_invalid = True, users = user_table))
        else:
            add_user(request.form.get('id'), request.form.get('pw'))
            return(redirect(url_for("FUN_admin")))
    else:
        return abort(401)


@app.route("/login", methods = ['post'])
def FUN_login():
    username = request.form.get('username')

    if(username in list_users() and verify(username, request.form.get("password"))):
      session['current_user'] = username
    if username == "admin":
      return(redirect(url_for("FUN_admin")))
    else:
      return(redirect(url_for("FUN_private")))


@app.route("/logout/")
def FUN_logout():
    session.pop("current_user", None)
    return(redirect(url_for("FUN_root")))
  

@app.route('/register', methods =['GET', 'POST']) 
def register(): 
    msg = '' 
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form : 
        username = request.form['username'] 
        password = request.form['password'] 
        
        account = read_user1_from_db(username)
        if account: 
            msg = 'Account already exists !'
        elif not re.match(r'[A-Za-z0-9]+', username): 
            msg = 'Username must contain only characters and numbers !'
        elif not username or not password: 
            msg = 'Please fill out the form !'
        else: 
            insert_user1_into_db(username, password)
            msg = 'You have successfully registered !'
        return render_template('index.html', msg = msg)
    elif request.method == 'POST': 
        msg = 'Please fill out the form !'
    return render_template('register.html', msg = msg)

if __name__ == "__main__":
    app.run(debug=True)
