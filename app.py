import json as json_lib
import os
import random
import string
from datetime import datetime
from hashlib import md5

import requests
from flask import abort
from flask import flash
from flask import Flask
from flask import jsonify
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for
from flask_login import current_user
from flask_login import login_required
from flask_login import login_user
from flask_login import LoginManager
from flask_login import logout_user
from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from oauthlib.oauth2 import WebApplicationClient
from passlib.hash import sha256_crypt
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

from email_utils.email_helper import mail_handler
from email_utils.email_verification import generate_token
from email_utils.email_verification import validate_token
from validation import EMAIL_VALIDATION
from validation import PASSWORD_VALIDATION
from validation import validate

# load import.json file containing database uri, admin email and other impt info
with open("import.json", "r") as c:
    json = json_lib.load(c)["jsondata"]

# create a Flask app and setup its configuration
app = Flask(__name__)
app.secret_key = "76^)(HEY,BULK-MAILER-HERE!)(skh390880213%^*&%6h&^&69lkjw*&kjh"
app.config["SQLALCHEMY_DATABASE_URI"] = json["databaseUri"]
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

# use LoginManager to provide login functionality and do some initial confg
login_manager = LoginManager(app)
login_manager.login_view = "login"
login_manager.login_message_category = "info"

# function to load the currently active user


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


# Google Login Credentials
GOOGLE_CLIENT_ID = json["google_client_id"]
GOOGLE_CLIENT_SECRET = json["google_client_secret"]
GOOGLE_DISCOVERY_URL = "https://accounts.google.com/.well-known/openid-configuration"

"""DATABASE MODELS"""

# represents a group of users to whom a specific email can be sent


class Group(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    date = db.Column(db.String(50), nullable=False)
    subscribers = db.relationship(
        "Subscriber", cascade="all,delete", backref="subscribers"
    )
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))


# represents a subscriber that belongs to a group


class Subscriber(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(50), nullable=False)
    date = db.Column(db.String(50), nullable=False)
    group_id = db.Column(db.Integer, db.ForeignKey("group.id"))
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))


# represents an email template


class Template(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    link = db.Column(db.String(100), nullable=False)
    content = db.Column(db.String(500), nullable=False)
    date = db.Column(db.String(50), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))


# represents a user in an organisation
# currently only one organisation with multiple users is supported


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(500), nullable=False)
    status = db.Column(db.Integer, nullable=False)
    date = db.Column(db.String(50), nullable=False)
    profile_image = db.Column(db.String(500), nullable=True)
    is_staff = db.Column(db.Integer, nullable=True)
    groups = db.relationship("Group", cascade="all,delete", backref="groups")
    templates = db.relationship("Template", cascade="all,delete", backref="templates")
    # subscribers = db.relationship('Subscriber',cascade = "all,delete", backref='subscribers')


"""END OF DATABASE MODELS"""

# For Gravatar


def avatar(email, size):
    digest = md5(email.lower().encode("utf-8")).hexdigest()
    return f"https://www.gravatar.com/avatar/{digest}?d=identicon&s={size}"


# generate a random 8 lettered password for forgot password
letters = string.ascii_letters
new_password = "".join(random.choice(letters) for i in range(8))

# convert the current datetime to string, to be stored in the db
x = datetime.now()
time = x.strftime("%c")

# domain name
testing_email = json["testing_email"]

# def get_user_name(username):
#     response = requests.get(f"https://api.github.com/users/{username}")
#     json_data = response.json()
#     return json_data['name']
#
#
# def get_contributors_data():
#     response = requests.get(
#         "https://api.github.com/repos/vigneshshettyin/Bulk-Mailer/contributors?per_page=1000")
#     json_data = response.json()
#     unique_contributors = {}
#     mentors = ['vigneshshettyin', 'data-charya', 'laureenf', 'shettyraksharaj']
#     for d in json_data:
#         if d["login"] not in unique_contributors.keys() and d["login"] not in mentors:
#             new_data = {
#                 "username": d["login"],
#                 "image": d["avatar_url"],
#                 "profile_url": d["html_url"],
#                 "name": get_user_name(d["login"])
#             }
#             unique_contributors[d["login"]] = new_data
#     return unique_contributors
#
# @app.route('/', methods = ['GET'])
# def default_page():
#     team = get_contributors_data()
#     return render_template('default.html', json=json, team=team)


# login route
@app.route("/login", methods=["GET", "POST"])
def login():
    # check if user is authenticated
    if current_user.is_authenticated:
        # if true, go to the dash page
        return redirect(url_for("dash_page"))
    # check if a form has been submitted i.e., user has tried to login
    if request.method == "POST":
        # get the data in the email, password, and remember me fields
        email = request.form.get("email")
        password = request.form.get("password")
        remember = request.form.get("remember")
        # get user with the email entered by querying the database
        user = User.query.filter_by(email=email).first()
        # check if user exists
        if not user:
            # if user doesn't exist i.e., email not found, flash an error
            flash("Valid account not found!", "danger")
            return render_template("login.html", json=json)
        elif (sha256_crypt.verify(password, user.password) == 1) and (user.status == 1):
            # if user exists and correct password has been entered and the user's account has been activated
            # update the last login to current date and add it to the db
            user.date = time
            db.session.add(user)
            db.session.commit()
            # log the user in using login_user
            login_user(user, remember=remember)
            # go to the page that the user tried to access if exists
            # otherwise go to the dash page
            next_page = request.args.get("next")
            return redirect(next_page) if next_page else redirect(url_for("dash_page"))
        else:
            # user doesn't exist so flash an error
            flash("Account not activated or invalid credentials!", "danger")
    return render_template("login.html", json=json)


# logout route


@app.route("/logout")
@login_required
def logout():
    # log the user out using logout_user, flash a msg and go to the login page
    logout_user()
    flash("Logged Out Successfully!", "success")
    return redirect(url_for("login"))


# register route


@app.route("/register", methods=["GET", "POST"])
def register_page():
    # check if form has been submitted i.e., user has tried to register
    if request.method == "POST":
        # get the data in name, email, and password fields
        name = request.form.get("name")
        email = request.form.get("email")
        profile_image = avatar(email, 128)
        # Validate email address
        if not validate(EMAIL_VALIDATION, email):
            flash("Invalid Email Address!", "danger")
            return render_template("register.html", json=json)

        password = request.form.get("password")

        # Validate password
        if not validate(PASSWORD_VALIDATION, password):
            flash("Invalid Password. Please enter a valid password!", "danger")
            return render_template("register.html", json=json)

        password2 = request.form.get("password2")
        # check if passwords match
        if password != password2:
            # if not, flash an error msg
            flash("Password unmatched!", "danger")
            return render_template("register.html", json=json)
        else:
            # generate the hashed password
            password = sha256_crypt.hash(password)
            response = User.query.filter_by(email=email).first()
            # check if the email already exists in the db
            if not response:
                # add the user to the db using the details entered and flash a msg
                entry = User(
                    name=name,
                    email=email,
                    password=password,
                    date=time,
                    profile_image=profile_image,
                    status=1,
                    is_staff=1,
                )
                db.session.add(entry)
                db.session.commit()

                # Generate email verification token
                verification_token = generate_token(email)
                # generate the welcome email to be sent to the user
                subject = "Welcome aboard " + name + "!"

                content = render_template(
                    "email_template.html", token=verification_token, email=email
                )

                response = mail_handler(
                    recepient_email=email, subject=subject, content=content
                )

                # If any error occurs, the response will be equal to False
                if isinstance(response, bool) and not response:
                    flash("Error while sending mail!", "danger")
                else:
                    flash(
                        "Now verify your email address for activating your account.",
                        "success",
                    )

                return redirect(url_for("login"))
            else:
                # user exists so flash an error
                flash("User exists!", "danger")
                return render_template("register.html", json=json)
    return render_template("register.html", json=json)


# Verify email route
@app.route("/verify_email/<string:token>/<string:email>", methods=["GET"])
def verify_email(token, email):
    if validate_token(token):
        user = User.query.filter_by(email=email).first()
        user.status = 1
        db.session.commit()
        flash("Account activated Successfully!!", "success")
        return redirect(url_for("dash_page"))
    else:
        flash("Email Verification Failed!!", "danger")
        return render_template("login.html", json=json)


# forgot password route
@app.route("/forgot", methods=["GET", "POST"])
def forgot_password_page():
    # check if form has been submitted
    if request.method == "POST":
        # get the email entered
        email = request.form.get("email")
        # get the user from the db
        post = User.query.filter_by(email=email).first()
        if post:
            # if user exists
            if post.is_staff == 1:
                # if user tried to reset admin password
                flash("You can't reset password of administrator!", "danger")
                return render_template("forgot-password.html", json=json)
            else:
                # hash the new password generated
                passwordemail = new_password
                post.password = sha256_crypt.hash(new_password)
                db.session.commit()
                # generate the forgot password email to be sent to the user
                subject = "Password Generated : " + passwordemail
                content = """<!DOCTYPE html><html xmlns="http://www.w3.org/1999/xhtml" xmlns:v="urn:schemas-microsoft-com:vml" xmlns:o="urn:schemas-microsoft-com:office:office"><head><title>Reset Your Password</title> <!--[if !mso]> --><meta http-equiv="X-UA-Compatible" content="IE=edge"> <!--<![endif]--><meta http-equiv="Content-Type" content="text/html; charset=UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><style type="text/css">#outlook a{padding:0}.ReadMsgBody{width:100%}.ExternalClass{width:100%}.ExternalClass *{line-height:100%}body{margin:0;padding:0;-webkit-text-size-adjust:100%;-ms-text-size-adjust:100%}table,td{border-collapse:collapse;mso-table-lspace:0pt;mso-table-rspace:0pt}img{border:0;height:auto;line-height:100%;outline:none;text-decoration:none;-ms-interpolation-mode:bicubic}p{display:block;margin:13px 0}</style><style type="text/css">@media only screen and (max-width:480px){@-ms-viewport{width:320px}@viewport{width:320px}}</style><style type="text/css">@media only screen and (min-width:480px){.mj-column-per-100{width:100%!important}}</style></head><body style="background: #f0f0f0;"><div class="mj-container" style="background-color:#f0f0f0;"><table role="presentation" cellpadding="0" cellspacing="0" style="background:#f0f0f0;font-size:0px;width:100%;" border="0"><tbody><tr><td><div style="margin:0px auto;max-width:600px;"><table role="presentation" cellpadding="0" cellspacing="0" style="font-size:0px;width:100%;" align="center" border="0"><tbody><tr><td style="text-align:center;vertical-align:top;direction:ltr;font-size:0px;padding:0px 0px 0px 0px;"><div class="mj-column-per-100 outlook-group-fix" style="vertical-align:top;display:inline-block;direction:ltr;font-size:13px;text-align:left;width:100%;"><table role="presentation" cellpadding="0" cellspacing="0" width="100%" border="0"><tbody><tr><td style="word-wrap:break-word;font-size:0px;"><div style="font-size:1px;line-height:30px;white-space:nowrap;">&#xA0;</div></td></tr></tbody></table></div></td></tr></tbody></table></div></td></tr></tbody></table><div style="margin:0px auto;max-width:600px;background:#FFFFFF;"><table role="presentation" cellpadding="0" cellspacing="0" style="font-size:0px;width:100%;background:#FFFFFF;" align="center" border="0"><tbody><tr><td style="text-align:center;vertical-align:top;direction:ltr;font-size:0px;padding:9px 0px 9px 0px;"><div class="mj-column-per-100 outlook-group-fix" style="vertical-align:top;display:inline-block;direction:ltr;font-size:13px;text-align:left;width:100%;"><table role="presentation" cellpadding="0" cellspacing="0" width="100%" border="0"><tbody><tr><td style="word-wrap:break-word;font-size:0px;padding:25px 25px 25px 25px;" align="center"><table role="presentation" cellpadding="0" cellspacing="0" style="border-collapse:collapse;border-spacing:0px;" align="center" border="0"><tbody><tr><td style="width:204px;"> <img alt="" title="" height="100px" width="100px" src="https://cdn.discordapp.com/attachments/577137963985534994/791571694803353610/favicon.ico" style="border:none;border-radius:0px;display:block;font-size:13px;outline:none;text-decoration:none;width:100%;height:auto;" width="204"></td></tr></tbody></table></td></tr><tr><td style="word-wrap:break-word;font-size:0px;padding:0px 15px 0px 15px;" align="center"><div style="cursor:auto;color:#333333;font-family:Helvetica, sans-serif;font-size:15px;line-height:22px;text-align:center;"><h3 style="font-family: Helvetica, sans-serif; font-size: 24px; color: #333333; line-height: 50%;">Your password has been reset successfully</h3></div></td></tr><tr><td style="word-wrap:break-word;font-size:0px;padding:0px 50px 0px 50px;" align="center"><div style="cursor:auto;color:#333333;font-family:Helvetica, sans-serif;font-size:15px;line-height:22px;text-align:center;"><p>Forgot your password or need to change it? No problem.</p></div></td></tr><tr><td style="word-wrap:break-word;font-size:0px;padding:20px 25px 20px 25px;padding-top:10px;padding-left:25px;" align="center"><table role="presentation" cellpadding="0" cellspacing="0" style="border-collapse:separate;" align="center" border="0"><tbody><tr><td style="border:none;border-radius:5px;color:#FFFFFF;cursor:auto;padding:10px 25px;" align="center" valign="middle" bgcolor="#4DAA50"><a href="#" style="text-decoration: none; background: #4DAA50; color: #FFFFFF; font-family: Helvetica, sans-serif; font-size: 19px; font-weight: normal; line-height: 120%; text-transform: none; margin: 0px;" target="_blank">Login</a></td></tr></tbody></table></td></tr><tr><td style="word-wrap:break-word;font-size:0px;padding:0px 47px 0px 47px;" align="center"><div style="cursor:auto;color:#333333;font-family:Helvetica, sans-serif;font-size:15px;line-height:22px;text-align:center;"><p><span style="font-size:14px;"><strong>Questions?&#xA0;</strong><br>Email us at <a href="mailto:email@bulkmailer.cf" style="color: #555555;">email@bulkmailer.cf</a>.&#xA0;</span></p></div></td></tr></tbody></table></div></td></tr></tbody></table></div><table role="presentation" cellpadding="0" cellspacing="0" style="background:#f0f0f0;font-size:0px;width:100%;" border="0"><tbody><tr><td><div style="margin:0px auto;max-width:600px;"><table role="presentation" cellpadding="0" cellspacing="0" style="font-size:0px;width:100%;" align="center" border="0"><tbody><tr><td style="text-align:center;vertical-align:top;direction:ltr;font-size:0px;padding:0px 0px 0px 0px;"><div class="mj-column-per-100 outlook-group-fix" style="vertical-align:top;display:inline-block;direction:ltr;font-size:13px;text-align:left;width:100%;"><table role="presentation" cellpadding="0" cellspacing="0" width="100%" border="0"><tbody><tr><td style="word-wrap:break-word;font-size:0px;padding:0px 98px 0px 98px;" align="center"><div style="cursor:auto;color:#777777;font-family:Helvetica, sans-serif;font-size:15px;line-height:22px;text-align:center;"><p><span style="font-size:12px;"><a href="https://bulkmailer.cf" style="color: #555555;">TERMS OF SERVICE</a> | <a href="https://bulkmailer.cf" style="color: #555555;">PRIVACY POLICY</a><br>&#xA9; 2020 Bulk Mailer<br><a href="https://bulkmailer.cf/unsubscribe" style="color: #555555;">UNSUBSCRIBE</a></span></p></div></td></tr></tbody></table></div></td></tr></tbody></table></div></td></tr></tbody></table></div></body></html>"""
                message = Mail(
                    from_email=(testing_email, "Bulk Mailer Reset Password"),
                    to_emails=email,
                    subject=subject,
                    html_content=content,
                )
                try:
                    # using the sendgrid api, send the email to the user's email
                    sg = SendGridAPIClient(json["sendgridapi"])
                    response = sg.send(message)
                    flash(
                        "You will receive a mail shortly. Password rested successfully!",
                        "success",
                    )
                    # print(response.status_code)
                    # print(response.body)
                    # print(response.headers)
                except Exception as e:
                    # if error occurs flash a msg
                    print("Error!")
        else:
            # user doesn't exist
            flash("We didn't find your account!", "danger")
            return render_template("forgot-password.html", json=json)

    return render_template("forgot-password.html", json=json)


# route to view groups


@app.route("/view/groups")
@login_required
def group_page():
    # get all the groups in the db ordered by id
    groups = Group.query.filter_by(user_id=current_user.id).all()
    return render_template("group_list.html", groups=groups, user=current_user)


# route to add a new group


@app.route("/new/group", methods=["POST"])
@login_required
def submit_new_group():
    # check if form has been submitted
    if request.method == "POST":
        # add the group with the entered name to the db and redirect to view groups page
        group_name = request.form.get("groupname")
        entry = Group(name=group_name, date=time, user_id=current_user.id)
        db.session.add(entry)
        db.session.commit()
        flash("New group added successfully!", "success")
    return redirect("/view/groups")


@app.route("/edit/group/<int:group_id>", methods=["GET", "POST"])
@login_required
def edit_group(group_id):
    if request.method == "POST":
        data = json_lib.loads(request.data)
        name = data["name"]
        exist = Group.query.filter_by(name=name).first()
        if exist:
            return jsonify(group_duplicate="Group with this name already exists.")
        grp = Group.query.filter_by(id=group_id).first()
        grp.name = name
        try:
            db.session.commit()
            return jsonify(group_success="Group edited successfully.")
        except Exception:
            return jsonify(
                group_error="SOmething went wrong while editing. Please try again"
            )
    else:
        try:
            grp = Group.query.filter_by(id=group_id).first()
            group = {"id": grp.id, "name": grp.name}
            return jsonify(group=group)
        except Exception:
            return jsonify(group_not_exist="Group doesn't exist.")


# route to delete group with specified id
@app.route("/delete/group/<int:id>", methods=["GET"])
@login_required
def delete_group(id):
    # get the record of the group to be deleted
    delete_group = Group.query.filter_by(id=id).first()
    db.session.delete(delete_group)
    db.session.commit()
    flash("Group deleted successfully!", "danger")
    return redirect("/view/groups")


# route to activate/deactivate a user's account


@app.route("/activate/user/<int:id>", methods=["GET"])
@login_required
def activate_user(id):
    if current_user.is_staff != 1:
        # get the record of the user with the specified id
        activate_user = User.query.filter_by(id=id).first()
        if activate_user.status == 1:
            # if user's status is active then deactivate account
            activate_user.status = 0
            flash("User deactivated successfully!", "warning")
        else:
            # otherwise, activate account
            activate_user.status = 1
            flash("User activated successfully!", "success")
        db.session.commit()
        # redirect to view users page
        return redirect("/view/users")
    else:
        flash("Can't perform this operation!", "danger")
        return redirect("/view/users")


# route to delete a user


@app.route("/delete/user/<int:id>", methods=["GET"])
@login_required
def delete_user(id):
    # get the record of the user with the specified id
    delete_user = User.query.filter_by(id=id).first()
    # if user tries to delete admin, flash an error
    if delete_user.is_staff == 1:
        flash("You cannot delete administrator", "warning")
    # otherwise check if user is admin
    elif current_user.is_staff == 1:
        # delete specified user
        db.session.delete(delete_user)
        db.session.commit()
        flash("User deleted successfully!", "danger")
    else:
        # flash an error msg that only admins can delete users
        flash("Only admins can delete users!", "warning")
    # redirect to view users page
    return redirect("/view/users")


# route to delete a template


@app.route("/delete/template/<int:id>", methods=["GET"])
@login_required
def delete_template(id):
    # get the record of the template with the specified id and delete it
    delete_template = Template.query.filter_by(id=id).first()
    # check if template exists
    if delete_template:
        # delete template
        db.session.delete(delete_template)
        db.session.commit()
        flash("Template deleted successfully!", "danger")
    else:
        # flash an error msg that template doesn't exist
        flash("Template does not exist!", "danger")
    return redirect("/view/templates")


# route to view subscribers of a particular group


@app.route("/view/subscribers/<int:number>")
@login_required
def subscribers_page(number):
    # get the records of all the subscribers of the group and display
    post = (
        Subscriber.query.filter_by(group_id=number)
        .filter_by(user_id=current_user.id)
        .all()
    )
    response = Group.query.filter_by(user_id=current_user.id).all()
    return render_template(
        "group_members.html", post=post, response=response, user=current_user
    )


# route to add a new subscriber


@app.route("/new/subscribers", methods=["POST"])
@login_required
def submit_new_subscribers():
    if request.method == "POST":
        # using the data entered, create a subscriber in the specified group and add to db
        email = request.form.get("email")
        gid = request.form.get("gid")
        entry = Subscriber(
            email=email, date=time, group_id=gid, user_id=current_user.id
        )
        db.session.add(entry)
        db.session.commit()
        flash("New subscriber added successfully!", "success")
    # redirect to view subscribers of the group page
    return redirect("/view/subscribers/" + str(gid))


# route to delete a subscriber


@app.route("/delete/subscriber/<int:gid>/<int:number>", methods=["GET"])
@login_required
def delete_subscriber(gid, number):
    # get the record of the subscriber to be deleted
    delete_subscriber = Subscriber.query.filter_by(id=number).first()
    # check if subscriber exists
    if delete_subscriber:
        # delete subscriber
        db.session.delete(delete_subscriber)
        db.session.commit()
        flash("Subscriber deleted successfully!", "danger")
    else:
        # flash an error msg
        flash("Subscriber not found!", "danger")
    # redirect to view subscribers page
    return redirect("/view/subscribers/" + str(gid))


# route to compose and send the bulk email


@app.route("/mail", methods=["POST", "GET"])
@login_required
def mail_page():
    # check if form has been submitted
    if request.method == "POST":
        # get the email fields entered
        username = request.form.get("username")
        name = request.form.get("name")
        subject = request.form.get("subject")
        group = request.form.get("group")
        html_content = request.form.get("editordata")
        html_content = (
            html_content
            + """<table role="presentation" cellpadding="0" cellspacing="0" style="background:#f0f0f0;font-size:0px;width:100%;" border="0"><tbody><tr><td><div style="margin:0px auto;max-width:600px;"><table role="presentation" cellpadding="0" cellspacing="0" style="font-size:0px;width:100%;" align="center" border="0"><tbody><tr><td style="text-align:center;vertical-align:top;direction:ltr;font-size:0px;padding:0px 0px 0px 0px;"><div class="mj-column-per-100 outlook-group-fix" style="vertical-align:top;display:inline-block;direction:ltr;font-size:13px;text-align:left;width:100%;"><table role="presentation" cellpadding="0" cellspacing="0" width="100%" border="0"><tbody><tr><td style="word-wrap:break-word;font-size:0px;padding:0px 98px 0px 98px;" align="center"><div style="cursor:auto;color:#777777;font-family:Helvetica, sans-serif;font-size:15px;line-height:22px;text-align:center;"><p><span style="font-size:12px;"><a href="https://bulkmailer.cf" style="color: #555555;">TERMS OF SERVICE</a> | <a href="https://bulkmailer.cf" style="color: #555555;">PRIVACY POLICY</a><br>© 2020 Bulk Mailer<br><a href="https://bulkmailer.cf/unsubscribe" style="color: #555555;">UNSUBSCRIBE</a></span></p></div></td></tr></tbody></table></div></td></tr></tbody></table></div></td></tr></tbody></table>"""
        )
        # generate the from email
        fromemail = testing_email
        # generate the mail list by extracting the emails of all the subscribers in the specified group
        mailobj = Subscriber.query.filter_by(group_id=group).all()
        maillist = []
        for mailobj in mailobj:
            maillist = maillist + [mailobj.email]
        # generate the mail
        message = Mail(
            from_email=(fromemail, name),
            to_emails=maillist,
            subject=subject,
            html_content=html_content,
        )
        try:
            # send the email
            sg = SendGridAPIClient(json["sendgridapi"])
            response = sg.send(message)
            flash("Mail has been sent successfully!", "success")
        except Exception as e:
            # flash an error msg if exception occurs
            flash("Error due to invalid details entered!", "danger")
    # get all the groups and templates in the db to display to the user
    group = Group.query.order_by(Group.id).all()
    mailtemp = Template.query.order_by(Template.id).all()
    return render_template(
        "mail.html", group=group, template=mailtemp, user=current_user, json=json
    )


# route to use a template


@app.route("/use/template/<int:id>", methods=["GET"])
@login_required
def use_template(id):
    # get the record of the template to be used
    post = Template.query.filter_by(id=id).first()
    # get all groups and templates to be displayed
    group = Group.query.order_by(Group.id).all()
    mailtemp = Template.query.order_by(Template.id).all()
    # redirect to mail with the specified template in the content
    return render_template("mail2.html", group=group, template=mailtemp, post=post)


# route to select a group


@app.route("/use/group/<int:id>", methods=["GET"])
@login_required
def use_group(id):
    # get the record of the group to whom the email has to be sent
    post = Group.query.filter_by(id=id).first()
    # get all the templates to display
    mailtemp = Template.query.order_by(Template.id).all()
    # redirect to mail with the specified group as the recipient
    return render_template(
        "mail3.html", template=mailtemp, post=post, user=current_user
    )


# route to view all the templates


@app.route("/view/templates")
@login_required
def template_page():
    # get the records of all the templates and display them
    template = Template.query.filter_by(user_id=current_user.id).all()
    return render_template("templates.html", template=template, user=current_user)


# route to add a template


@app.route("/add/template", methods=["POST"])
@login_required
def add_template():
    # if form has been submitted
    if request.method == "POST":
        # get the data in the form fields
        link = request.form.get("link")
        name = request.form.get("name")
        editordata = request.form.get("editordata")
        # use the data to create a record and add it to the db
        entry = Template(
            name=name, date=time, content=editordata, link=link, user_id=current_user.id
        )
        db.session.add(entry)
        db.session.commit()
        # flash a msg and redirect to view all templates page
        flash("Template added successfully!", "success")
        return redirect("/view/templates")


# -- API NotImplemented ---
#

# #api to subscribe using user's email
# @app.route('/subscribe', methods=['GET', 'POST'])
# def sub_page():
#     #if form has been submitted
#     if (request.method == 'POST'):
#         #get the user's email
#         email = request.form.get('email')
#         #check if the subscriber already exists in the db
#         check = Subscriber.query.filter_by(email=email).first()
#         if not check:
#             #if subscriber doesn't exist, create a record (add user to default group)
#             entry = Subscriber(email=email, date=time, group_id=3)
#             #commit to the db
#             db.session.add(entry)
#             db.session.commit()
#             # flash('Newsletter subscribed successfully!', 'success')
#             return render_template('thankyou.html')
#         else:
#             #if user exists then flash an error msg
#             flash('You have already subscribed!', 'danger')
#             return render_template('error.html')

# api to unsubscribe from a group
# @app.route('/unsubscribe', methods=['GET', 'POST'])
# def unsub_page():
#     #check if form has been submitted
#     if (request.method == 'POST'):
#         #get the user's email
#         email = request.form.get('email')
#         #get the subcriber's record from the db
#         delete_subscriber = Subscriber.query.filter_by(email=email).first()
#         if not delete_subscriber:
#             #if subscriber doesn't exist, flash an error msg
#             flash('We did not find your data in our database!', 'danger')
#             return render_template('error.html')
#         else:
#             #if subscriber exists, delete from db
#             db.session.delete(delete_subscriber)
#             db.session.commit()
#             flash('Newsletter unsubscribed  successfully!', 'success')
#             return render_template('error.html')


# -- API NotImplemented ---

# main page
@app.route("/")
@login_required
def dash_page():
    # get the number of groups, subscribers, and templates; display them to the user
    glen = len(Group.query.filter_by(user_id=current_user.id).all())
    slen = len(Subscriber.query.filter_by(user_id=current_user.id).all())
    tlen = len(Template.query.filter_by(user_id=current_user.id).all())
    return render_template(
        "index.html", glen=glen, slen=slen, tlen=tlen, user=current_user
    )


# route to view list of users


@app.route("/view/users")
@login_required
def users_page():
    if current_user.is_staff == 1:
        # get the records of all the users and display to the user
        users = User.query.order_by(User.id).all()
        return render_template("user_list.html", users=users, user=current_user)
    else:
        flash("Not authorized!", "danger")
        return redirect("/")


# Google Login
client = WebApplicationClient(GOOGLE_CLIENT_ID)


def get_google_provider_cfg():
    return requests.get(GOOGLE_DISCOVERY_URL).json()


# Google Login Route


@app.route("/login/google")
def google_login():
    # Find out what URL to hit for Google login
    google_provider_cfg = get_google_provider_cfg()
    authorization_endpoint = google_provider_cfg["authorization_endpoint"]

    # Use library to construct the request for Google login and provide
    # scopes that let us retrieve user's profile from Google

    print(f"I am base url {request.base_url}")

    request_uri = client.prepare_request_uri(
        authorization_endpoint,
        redirect_uri=request.base_url + "/callback",
        scope=["openid", "email", "profile"],
    )
    return redirect(request_uri)


@app.route("/login/google/callback")
def google_login_callback():
    # Get authorization code Google sent back to us
    code = request.args.get("code")

    # Find out what URL to hit to get tokens that allow us to ask for
    # things on behalf of a user
    google_provider_cfg = get_google_provider_cfg()
    token_endpoint = google_provider_cfg["token_endpoint"]

    token_url, headers, body = client.prepare_token_request(
        token_endpoint,
        authorization_response=request.url,
        redirect_url=request.base_url,
        code=code,
    )
    token_response = requests.post(
        token_url,
        headers=headers,
        data=body,
        auth=(GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET),
    )

    # Parse the tokens!
    client.parse_request_body_response(json_lib.dumps(token_response.json()))

    # Now that we have tokens, let's find and hit the URL
    # from Google that gives us the user's profile information,
    # including their Google profile image and email
    userinfo_endpoint = google_provider_cfg["userinfo_endpoint"]
    uri, headers, body = client.add_token(userinfo_endpoint)
    userinfo_response = requests.get(uri, headers=headers, data=body)

    # You want to make sure their email is verified.
    # The user authenticated with Google, authorized your
    # app, and now we've verified their email through Google!
    if userinfo_response.json().get("email_verified"):
        users_email = userinfo_response.json()["email"]
        picture = userinfo_response.json()["picture"]
        users_name = userinfo_response.json()["name"]
    else:
        abort(401)
    pwd = new_password
    password = sha256_crypt.hash(pwd)
    # Create a user in your db with the information provided
    # by Google

    # Doesn't exist? Add it to the database.
    if not User.query.filter_by(email=users_email).first():
        entry = User(
            name=users_name,
            email=users_email,
            password=password,
            date=time,
            profile_image=picture,
            status=1,
            is_staff=1,
        )
        db.session.add(entry)
        db.session.commit()

    # Begin user session by logging the user in

    user = User.query.filter_by(email=users_email).first()
    login_user(user)

    # Send user back to homepage
    return redirect(url_for("dash_page"))


# route to handle page not found


@app.errorhandler(404)
def page_not_found(e):
    # note that we set the 404 status explicitly
    return render_template("404.html"), 404


# execute if file is the main file i.e., file wasn't imported
if __name__ == "__main__":
    app.run(debug=True)
