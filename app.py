from flask import Flask, render_template, request, session, redirect, flash
from werkzeug.security import generate_password_hash
from smtplib import SMTPRecipientsRefused
# Import necessary libraries for functionality

from markdown import markdown
from datetime import datetime

from generation import generate_idea
from random import randint
from utils import login_required, enter, db_exec, error, send_confirmation_email, crypt_data, make_url
from fetch_image import fetch_image

app = Flask(__name__)

# Set a secret key for session management
app.secret_key = "FooBarBaz"


# Route for user registration
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        # Render the registration form
        return render_template("register.html")
    else:
        # Handle form submission
        f = request.form
        name = f["username"]
        passwd = f["password"]
        confirmation = f["confirmation"]

        # Validate form inputs
        if not name or not passwd or not confirmation:
            return error("Fill all the form")

        if passwd != confirmation:
            return error("Passwords do not match")

        # Send confirmation email to the user
        
        url = make_url("confirm", {"email": name, "key": crypt_data(name), "passwd": crypt_data(passwd)})
        
        try:
            send_confirmation_email(name, url)
        except SMTPRecipientsRefused:
            return error("Not a valid email addres")
            
        flash("Check your email")
        return redirect("/login")

# Route to confirm email and complete registration
@app.route("/confirm")
def confirm():
    # Extract query parameters from the URL
    if (key := request.args.get("key")) and (passwd := request.args.get("passwd")) and (email := request.args.get("email")):
        
        
        
        # Verify the integrity of the URL
        if crypt_data(key, False).replace("%40", "@") != email:
            print(crypt_data(key, False))
            return error("Check URL integrity")
        

        
        
        # Hash the password and register the user in the database
        passwd = crypt_data(passwd, False)
        
        pass_hash = generate_password_hash(passwd)
        # Insert the user into the database
        if error_message := db_exec("INSERT INTO User (username, password_hash) VALUES (?, ?)", (email, pass_hash)):
            return error(error_message)

        # Log the user in and redirect to the homepage
        if id := enter(email, passwd):
            session["user_id"] = id
            return redirect("/")
        
        return error("Registration failed, please try again")
    else:
        return error("Wrong URL")

# Route for user login
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        # Render the login form
        return render_template("login.html")
    else:
        # Handle login form submission
        if not (name := request.form.get("username")) or not (passwd := request.form.get("password")):
            return error("Fill all the form")

        # Authenticate the user
        if (id := enter(name, passwd)):
            session["user_id"] = id
            return redirect("/")
        else:
            return error("Wrong username or password")

# Route to reset the password
@app.route("/reset")
def reset():
    if not session.get("code"): 
        code = randint(100000, 999999)
        session["code"] = str(code)
    return render_template("reset.html")

@app.route("/confirm_reset", methods=["GET", "POST"])
def confirm_reset(): 
    if request.method == "POST":
        if (email := request.form.get("email")) \
        and (passwd := request.form.get("new_password")) \
        and (confirmation := request.form.get("confirm_password")):
            
            if passwd != confirmation:
                return error("Passwords do not match")
            
            if not db_exec("SELECT * FROM User WHERE username=?", (email,)):
               return error("This user does not exist") 
            
            url = make_url("confirm_reset", {
                "code": session.get("code"), 
                "email": email, 
                "password": crypt_data(passwd)})
            
            send_confirmation_email(email, url)
            flash("Check your email")
            return redirect("/login")
    elif request.method == "GET":
        session.pop("code")
        if (request.args.get("code") == session.get("code")) \
        and (passwd := request.args.get("password")) \
        and (email := request.args.get("email")):
            
            passwd = crypt_data(passwd, False)
            password = generate_password_hash(passwd)
            db_exec("UPDATE User SET password_hash = ? WHERE username = ?", (password,email))
            if user_id := enter(email, passwd):
                print("in 2 if")
                session["user_id"] = user_id
                return redirect("/")
    return error("Check URL integrity")
         

# Route for the homepage
@app.route("/", methods=["GET"])
@login_required
def index():
    # Initialize session data for brainstorming responses
    session["prev_responces"] = []
    return render_template("index.html")

# Route for brainstorming ideas
@app.route("/brainstorm")
@login_required
def brainstorm():
    if "topic" in request.args.keys():
        if request.args.get("topic"):
            # Generate ideas based on the topic
            responces = session.get("prev_responces")
            topic = request.args.get("topic") + "which is not in " + ("" if responces == None else str(responces))
            text = generate_idea(topic)
            img = fetch_image(text)

            # Convert text to markdown and store responses in the session
            text = markdown(text)
            session["prev_responces"] = session.get("prev_responces") + [text,]
            session["topic"] = request.args.get("topic")
            return render_template("brainstorm.html", text=text, img=img)
        return error("Write a topic")
    else:
        return redirect("/")

# Route to save an idea
@app.route("/idea")
@login_required
def idea():
    if "title" in request.args.keys() and "img" in request.args.keys():
        if idea := request.args.get("title"):
            # Clear previous responses and save the idea in the database
            session.pop("prev_responces")
            img = request.args.get("img")
            desctiption = markdown(generate_idea(idea, False))
            arguments = (session.get("user_id"), session.get("topic"), idea, img, str(datetime.now()), desctiption)
            db_exec("INSERT INTO BrainstormSession (user_id, topic, idea, image_url, timestamp, idea_description) VALUES (?, ?, ?, ?, ?, ?)", arguments)
            session.pop("topic")
            return render_template("idea.html", title=idea, img=img, desc=desctiption)
    else:
        return error("Enter a topic")

# Route to view brainstorming history
@app.route("/history")
@login_required
def history():
    rows = db_exec("SELECT topic, idea, id FROM BrainstormSession WHERE user_id = ? ORDER BY timestamp DESC", (session.get("user_id"),))
    return render_template("history.html", rows=rows)

# Route to display a specific idea
@app.route("/show-idea")
@login_required
def show_idea():
    if request.args.get("session_id"):
        # Fetch idea details from the database
        row = db_exec("SELECT idea, idea_description, image_url FROM BrainstormSession WHERE id=?", (request.args.get("session_id"), ))[0]
        return render_template("idea.html", img=row[2], desc=row[1], title=row[0])
    return error("Missing argument")

# Route to log out the user
@app.route("/logout", methods=["GET", "POST",])
@login_required
def logout():
    session.clear()  # Clear session data
    return redirect("/login")
