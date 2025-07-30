from functools import wraps
from flask import redirect, render_template, session
import sqlite3
from werkzeug.security import check_password_hash
from smtplib import SMTP 
from email.message import EmailMessage
from cryptography.fernet import Fernet

SITE_IP = "http://127.0.0.1:5000/"


ADDRESS = "botnoreply55@gmail.com"

PASSWORD = "thvi uwly many zufv"

KEY = "+i0LhDY3+LyC0EwDUSQupelrYovyrWJALH309iDhNwg="


def crypt_data(data: str, encrypt: bool = True):
    crypt = Fernet(KEY)
    
    if encrypt:
        return crypt.encrypt(data.encode()).decode()
    return crypt.decrypt(data.encode()).decode()

def make_url(page: str, args: dict):
    url = SITE_IP + page + "?"
    
    for i, j in args.items():
        url = url + i + "=" + j + "&"
        
    return url



def send_confirmation_email(reciver_address: str, message: str):
    
    msg = EmailMessage()
    msg["To"] = reciver_address
    reciver_address = reciver_address.replace("@", "%40")
    print(crypt_data(reciver_address))
    msg.set_content(message)
    msg["Subject"] = "Confirmation Email"
    msg["From"] = ADDRESS
  

        # Initialize SMTP connection
    with SMTP("smtp.gmail.com", 587) as s:
        s.starttls()  # Enable TLS
        s.login(ADDRESS, PASSWORD)
        s.send_message(msg)

def error(message):
    return render_template("error.html", message=message)


def login_required(f):
    

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)

    return decorated_function

def enter(name: str, passwd: str):
    res = db_exec("SELECT id, password_hash FROM User WHERE username = ?", (name, ))

    if res:
        if not check_password_hash(res[0][1], passwd):
            return None
        return res[0][0]
    else:
        return None

def db_exec(query: str, arguments: tuple):
    conn = sqlite3.connect("brainstorm.db")
    curr = conn.cursor()
    try:
        res = curr.execute(query, arguments).fetchall()
    except sqlite3.IntegrityError:
        return "Username is already taken"
    conn.commit()
    conn.close()
    return res