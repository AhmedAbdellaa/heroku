# ------------------importing library---------------------------
from app import app
from flask import (render_template,request,
    redirect,
    jsonify,
    make_response,
    after_this_request,
    abort,
    send_file,
    url_for,
    session,
    flash,
    send_from_directory
)
from app.tasks import linux_join_read,windows_join_read

from werkzeug.utils import secure_filename
import secrets
import pickle
import time
# ---------------------------------------------------------------------------
# -------------------------------------------------------------------------
# upload file
import os
import logging
if os.name == "posix":
    from app import r ,q

# print(
#     "********************************************************views********************************************************"
# )
try:
    os.mkdir(app.config["PDF_UPLOADS"])
except: 
    pass
try:
    os.mkdir(app.config["CLIENT_FOLDER"])
except :
    pass
   
if os.path.exists(app.config["USER_FILE"]):
    users = pickle.load(open(app.config["USER_FILE"], "rb"))
else:
    users = {
        "admin": {
            "username": "admin",
            "password": "admin",
            "email": "ahmed.m.abdellah99@gmial.com",
        }
    }
    pickle.dump(users, open(app.config["USER_FILE"], "wb"))
print("*******************************************views*****************************")
print(os.getcwd())
print(os.listdir(os.getcwd()))
# print(os.listdir(os.path.join("/web/app/static/")))
for user in users :
    # if not os.path.isdir(os.path.join(app.config["CLIENT_FOLDER"],user)):
    try:
        os.mkdir(os.path.join(app.config["CLIENT_FOLDER"],user))
    except:
        pass

@app.route("/sign-up", methods=["GET", "POST"])
def sign_up():
    if request.method == "POST":
        req = request.form
        print(req)
        username = req["username"]
        email = req.get("email")
        password = request.form["password"]
        print(username)
        if not (username == "" or email == "" or password == ""):

            if username not in users or " " not in username:
                if len(password) > 6:
                    flash("account succefully created")
                    print(username, email, password)
                    new_user = {
                        username: {
                            "username": username,
                            "password": password,
                            "email": email,
                        }
                    }
                    users.update(new_user)
                    pickle.dump(users, open(app.config["USER_FILE"], "wb"))
                    print(type(username))
                    os.mkdir(os.path.join(app.config["CLIENT_FOLDER"], username))
                    return redirect("/")
                else:
                    flash("password must be more than 6 char")
                    return redirect(request.url)
            else:
                flash("this user name unavliable", "message")
                return redirect(request.url)

        else:
            print("eceptin")
            flash("all fileds require")
            return redirect(request.url)
    else:
        return render_template("public/signup.html")


# -----------------------------------------------------------------------------------
@app.route("/", methods=["GET", "POST"])
def login():

    if request.method == "POST":
        print(users)
        print(users["admin"]["password"])
        req = request.form
        print(req)
        if "username" in req and "password" in req:
            username = req.get("username")
            password = req.get("password")

            if username in users:
                if password == users[username]["password"]:
                    session["username"] = username
                    # return make_response('welcome',200)
                    return redirect(url_for("upload_pdf"))
            else:
                return redirect(request.url)
        else:
            return redirect(request.url)
    else:
        return render_template("public/login.html")


@app.route("/pdfs-list")
def profile():
    if "username" in session:

        user = session.get("username")
        folder = os.path.join(app.config["CLIENT_FOLDER"], user)
        files =[ (file,time.ctime(os.stat(os.path.join(folder,file))[8]),os.path.join(folder,file)) for file in os.listdir(folder)]
        print(files)
        return render_template("public/profile.html", user=user,files=files)
    else:
        return redirect("/")

os.stat
@app.route("/signout")
def signout():
    session.pop("username", None)  # none handel if username not in session
    return redirect("/")


# -----------------------------------------------------------------------------------


@app.route("/upload-pdf", methods=["POST", "GET"])
def upload_pdf():
    if request.method == "POST":
        # print("****************************post***************")
        if request.files and request.form["dir_name"]:

            group_directory = request.form["dir_name"]

            # if not os.path.isdir(os.path.join(app.config["PDF_UPLOADS"], group_directory)):
            try:
                os.mkdir(os.path.join(app.config["PDF_UPLOADS"], group_directory))
            except:
                logging.info("folder arledy exist info")
                logging.warning("folder arledy exist warning")
            file = request.files["file"]
            if os.path.splitext(file.filename)[1] != ".pdf":
                print(os.path.splitext(file.filename)[1])
                print("only pdf allowed")
                return redirect(request.url)
            else:
                filename = f"{secure_filename(file.filename)}"
                save_path = os.path.join(
                    app.config["PDF_UPLOADS"], group_directory, filename
                )
                try:
                    with open(save_path, "ab") as f:
                        f.seek(int(request.form["dzchunkbyteoffset"]))
                        f.write(file.stream.read())
                    print("uploading")
                    print(save_path)
                    with open(save_path,"rb") as fi:
                        print(fi.readline())    
                    return redirect(request.url, 200)
                except OSError:
                    return "error uploading file try again later", 500

    elif request.method == "GET":
        generated_key = secrets.token_urlsafe(6)
        return render_template("public/upload_pdf.html", dir_name=generated_key)
    else:
        return make_response({"message": "error"}, 404)


@app.route("/delete", methods=["POST"])
def delete_file():
    if request.method == "POST":
        if request.form:
            req = request.form
            dir_path = os.path.join(app.config["PDF_UPLOADS"], req["dir_name"])
            file_path = os.path.join(dir_path, secure_filename(req["file_name"]))
            if os.path.isdir(dir_path):
               
                try:
                    os.remove(file_path)

                except:
                    print("file not exist")
                finally:
                    if len(os.listdir(dir_path)) == 0:
                        os.rmdir(dir_path)
                        return redirect(request.url, 200)
        return make_response(jsonify({"output_path": "asdf"}), 200)
    else:
        return make_response({"message": "error"}, 404)



@app.route("/delet-output-file",methods=["POST"])
def delet_output_file():
    req = request.form
    if "username" in session:
        if "file_name" in req:
            file_pathe = os.path.join(app.config["CLIENT_FOLDER"], session["username"],req["file_name"])    
            try: 
                os.remove(file_pathe) 
                return make_response(jsonify({"message": "file deleted"}), 200)
            except:
                return make_response(jsonify({"message": "error deleted file"}), 500)
    return make_response(jsonify({"message": "no user session"}), 400)
# ---------------------------------------------------------------
# sending file
@app.route("/send", methods=["GET", "POST"])
def send():
    if request.method == "POST":
        req = request.form
        dir_path = os.path.join(app.config["PDF_UPLOADS"], req["dir_name"])
        
        print("*************************sending*********************")
        print(dir_path)
        print(os.getcwd())
        print(os.listdir(os.getcwd()))
        file_name = req["outputname"]+"_"
        if os.name =='posix':
            if "username" in session:
            
                if not os.path.isdir(os.path.join(app.config["CLIENT_FOLDER"], session["username"])):
                    os.mkdir(os.path.join(app.config["CLIENT_FOLDER"], session["username"]))

                output_path = os.path.join(app.config["CLIENT_FOLDER"],session["username"],f"{file_name}{secrets.token_urlsafe(6)}_ocr.pdf")
                

                task = q.enqueue(linux_join_read,dir_path,output_path)
                return make_response(
                        jsonify({"message": "succsseed","show":"converted pdf will show soon in your pdf list","os":"linux"}), 200
                    )
                # return redirect("/upload-pdf"),200
            else:
                return make_response(
                    jsonify({"message": "bad request"}), 400
                )
            
        elif os.name == "nt":  # windos
            output_path = os.path.join(app.config["CLIENT_FOLDER"],f"{file_name}{secrets.token_urlsafe(6)}_ocr.pdf")
            if "username" in session:
                if not os.path.isdir(os.path.join(app.config["CLIENT_FOLDER"], session["username"])):
                    os.mkdir(os.path.join(app.config["CLIENT_FOLDER"], session["username"]))
                output_path = os.path.join(app.config["CLIENT_FOLDER"],session["username"],f"{file_name}{secrets.token_urlsafe(6)}_ocr.pdf")


            if windows_join_read(dir_path, output_path):
                return make_response(jsonify({"message": "succsseed","output_path": output_path,"os":"windows"}), 200)
            else:
                return make_response(
                    jsonify({"message": "error"}), 500
                )  # internel server error
    else:
        return make_response({"message": "error"}, 404)


# ---------------------------------------------------------------

from pathlib import Path
@app.route("/pdfViewer", methods=["GET", "POST"])
def view_pdf():
    if request.method == "POST":
        req = request.form
        if "output_path" in req:
            output_path = os.path.join(request.form["output_path"])
            return send_file(output_path, as_attachment=True) 

        else :
            return make_response({"message": "error"}, 404)
    else:
        return make_response({"message": "error"}, 404)

@app.route("/pdf-from-list/<path:filename>")
def get_pdf(filename):
    print(session["username"])
    output_dir= os.path.join(app.config["CLIENT_FOLDER"], session["username"])
    print(filename)
    try:
        return send_from_directory(output_dir,
            filename,as_attachment=True)

    except FileNotFoundError:
        abort(404)