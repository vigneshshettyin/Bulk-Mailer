import csv
import io
import json as json_lib
import os
import random
import re
import string
import psycopg2
from datetime import datetime
from hashlib import md5
import requests
from email_utils.email_helper import mail_handler
from email_utils.email_verification import generate_token, validate_token
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from flask import (
    Flask,
    abort,
    flash,
    jsonify,
    make_response,
    redirect,
    render_template,
    request,
    url_for,
)
from flask_login import (
    LoginManager,
    UserMixin,
    current_user,
    login_required,
    login_user,
    logout_user,
)
from flask_sqlalchemy import SQLAlchemy
from oauthlib.oauth2 import WebApplicationClient
from passlib.hash import sha256_crypt
from validation import EMAIL_VALIDATION, PASSWORD_VALIDATION, validate
from decouple import config
from functools import wraps


# create a Flask app and setup its configuration
app = Flask(__name__)
app.secret_key = "76^)(HEY,BULK-MAILER-HERE!)(skh390880213%^*&%6h&^&69lkjw*&kjh"
DATABASE_URI = config("DATABASE_URL")
if DATABASE_URI.startswith("postgres://"):
    DATABASE_URI = DATABASE_URI.replace("postgres://", "postgresql://", 1)
app.config["SQLALCHEMY_DATABASE_URI"] = config("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

# Config vars
favTitle = config("favTitle")

# use LoginManager to provide login functionality and do some initial confg
login_manager = LoginManager(app)
login_manager.login_view = "login"
login_manager.login_message_category = "info"

# function to load the currently active user


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


# Google Login Credentials
GOOGLE_CLIENT_ID = config("google_client_id")
GOOGLE_CLIENT_SECRET = config("google_client_secret")
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
    is_staff = db.Column(db.Boolean, default=False, nullable=False)
    groups = db.relationship("Group", cascade="all,delete", backref="groups")
    templates = db.relationship("Template", cascade="all,delete", backref="templates")
    # subscribers = db.relationship('Subscriber',cascade = "all,delete", backref='subscribers')


class Contact(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    firstname = db.Column(db.String(50), nullable=False)
    lastname = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(50), nullable=False)
    number = db.Column(db.String(50), nullable=False)
    msg = db.Column(db.String(50), nullable=False)


"""END OF DATABASE MODELS"""

# For Gravatar


def avatar(email, size):
    digest = md5(email.lower().encode("utf-8")).hexdigest()
    return f"https://www.gravatar.com/avatar/{digest}?d=identicon&s={size}"


def send_mail(message):
    sg = SendGridAPIClient(config("SENDGRID_API_KEY"))
    response = sg.send(message)
    return response


# Admin Required Decorator


def admin_required(func):
    @wraps(func)
    def decorated_view(*args, **kwargs):
        if not current_user.is_staff:
            flash("You are not authorized to access this page.", "danger")
            return render_template("block.html", favTitle=favTitle, user=current_user)
        return func(*args, **kwargs)

    return decorated_view


# generate a random 8 lettered password for forgot password
letters = string.ascii_letters
new_password = "".join(random.choice(letters) for _ in range(8))

# convert the current datetime to string, to be stored in the db
x = datetime.now()
time = x.strftime("%c")

# domain name
testing_email = config("testing_email")


@app.route("/validate/email", methods=["POST"])
def email_validation():
    data = json_lib.loads(request.data)
    email = data["email"]
    pattern = "^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"  # noqa
    user = User.query.filter_by(email=email).first()
    if user and user.status == 0:
        return jsonify(account_inactive=True)
    if user:
        return jsonify(
            email_error="You are already registered. Please login to continue.",
            status=409,
        )
    if not bool(re.match(pattern, email)):
        return jsonify(email_pattern_error="Please enter a valid email address.")
    return jsonify(email_valid=True)


@app.route("/validate/password", methods=["POST"])
def validate_password():
    data = json_lib.loads(request.data)
    password = data["password"]
    pattern = (
        "^(?=.*[0-9])(?=.*[a-z])(?=.*[A-Z])(?=.*[$#@!%^&*()])(?=\S+$).{8,30}$"  # noqa
    )
    if bool(re.match(pattern, password)):
        return jsonify(password_valid=True)
    return jsonify(
        password_error="Password must be 8-30 characters long and must contain atleast one uppercase letter, one lowercase letter, one number(0-9) and one special character(@,#,$,%,&,_)"  # noqa
    )


@app.route("/match/passwords", methods=["POST"])
def match_passwords():
    data = json_lib.loads(request.data)
    password1 = data["password"]
    password2 = data["password2"]
    if str(password1) == str(password2):
        return jsonify(password_match=True)
    return jsonify(password_mismatch="Password and Confirm Password do not match.")


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
            return render_template("login.html", favTitle=favTitle)
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
    return render_template("login.html", favTitle=favTitle)


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
            return render_template("register.html", favTitle=favTitle)

        password = request.form.get("password")

        # Validate password
        if not validate(PASSWORD_VALIDATION, password):
            flash("Invalid Password. Please enter a valid password!", "danger")
            return render_template("register.html", favTitle=favTitle)

        password2 = request.form.get("password2")
        # check if passwords match
        if password != password2:
            # if not, flash an error msg
            flash("Password unmatched!", "danger")
            return render_template("register.html", favTitle=favTitle)
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
                    status=0,
                    is_staff=True,
                )
                db.session.add(entry)
                db.session.commit()

                # Generate email verification token
                verification_token = generate_token(email)
                print(url_for("verify_email", token=verification_token, email=email))
                # generate the welcome email to be sent to the user

                message = Mail(
                    from_email=("register@bulkmailer.cf", "Register Bot | Bulk Mailer"),
                    to_emails=email,
                    subject="Welcome aboard " + name + "!",
                    html_content=render_template(
                        "emails/register.html", token=verification_token, email=email
                    ),
                )

                # If any error occurs, the response will be equal to False
                if isinstance(send_mail(message), bool) and not response:
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
                return render_template("register.html", favTitle=favTitle)
    return render_template("register.html", favTitle=favTitle)


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
        return render_template("login.html", favTitle=favTitle)


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
            if post.is_staff:
                # if user tried to reset admin password
                flash("You can't reset password of administrator!", "danger")
                return render_template("forgot-password.html", favTitle=favTitle)
            else:
                # Generate email verification token
                verification_token = generate_token(email)
                print(url_for("reset_password", token=verification_token, email=email))
                # generate the email to be sent to the user
                message = Mail(
                    from_email=("forgot@bulkmailer.cf", "Password Bot | Bulk Mailer"),
                    to_emails=email,
                    subject="Password Reset Link | BulkMailer",
                    html_content=render_template(
                        "emails/forgot-pwd.html", token=verification_token, email=email
                    ),
                )
                # If any error occurs, the response will be equal to False
                if isinstance(send_mail(message), bool) and not response:
                    flash("Error while sending mail!", "danger")
                else:
                    flash(
                        f"We've sent a password reset link on {email}!",
                        "success",
                    )
        else:
            # user doesn't exist
            flash("We didn't find your account!", "danger")
            return render_template("forgot-password.html", favTitle=favTitle)

    return render_template("forgot-password.html", favTitle=favTitle)


@app.route("/reset-password/<token>/<email>", methods=["GET", "POST"])
def reset_password(token, email):
    if current_user.is_authenticated:
        return redirect(url_for("dash_page"))
    if request.method == "POST":
        password = request.form.get("password")
        password = sha256_crypt.hash(password)
        user = User.query.filter_by(email=email).first()
        user.password = password
        db.session.add(user)
        db.session.commit()
        flash("Password changed successfully.", "success")
        return redirect(url_for("login"))
    if not validate_token(token):
        return render_template(
            "forgot-password.html", favTitle=favTitle, verified=False
        )
    user = User.query.filter_by(email=email).first()
    first_name = user.name.split(" ")[0]
    return render_template(
        "forgot-password.html",
        favTitle=favTitle,
        name=first_name,
        token=token,
        email=email,
        verified=True,
    )


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
@admin_required
def activate_user(id):
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


# route to delete a user


@app.route("/delete/user/<int:id>", methods=["GET"])
@login_required
@admin_required
def delete_user(id):
    # get the record of the user with the specified id
    delete_user = User.query.filter_by(id=id).first()
    # if user tries to delete admin, flash an error
    if delete_user.is_staff:
        flash("You cannot delete administrator", "warning")
    else:
        # delete specified user
        db.session.delete(delete_user)
        db.session.commit()
        flash("User deleted successfully!", "danger")
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
        #     # get the email fields entered
        #     # username = request.form.get("username")
        #     # name = request.form.get("name")
        #     # subject = request.form.get("subject")
        #     group = request.form.get("group")
        #     html_content = request.form.get("editordata")
        #     html_content = (
        #         html_content
        #         + """<table role="presentation" cellpadding="0" cellspacing="0" style="background:#f0f0f0;font-size:0px;width:100%;" border="0"><tbody><tr><td><div style="margin:0px auto;max-width:600px;"><table role="presentation" cellpadding="0" cellspacing="0" style="font-size:0px;width:100%;" align="center" border="0"><tbody><tr><td style="text-align:center;vertical-align:top;direction:ltr;font-size:0px;padding:0px 0px 0px 0px;"><div class="mj-column-per-100 outlook-group-fix" style="vertical-align:top;display:inline-block;direction:ltr;font-size:13px;text-align:left;width:100%;"><table role="presentation" cellpadding="0" cellspacing="0" width="100%" border="0"><tbody><tr><td style="word-wrap:break-word;font-size:0px;padding:0px 98px 0px 98px;" align="center"><div style="cursor:auto;color:#777777;font-family:Helvetica, sans-serif;font-size:15px;line-height:22px;text-align:center;"><p><span style="font-size:12px;"><a href="https://bulkmailer.cf" style="color: #555555;">TERMS OF SERVICE</a> | <a href="https://bulkmailer.cf" style="color: #555555;">PRIVACY POLICY</a><br>© 2020 Bulk Mailer<br><a href="https://bulkmailer.cf/unsubscribe" style="color: #555555;">UNSUBSCRIBE</a></span></p></div></td></tr></tbody></table></div></td></tr></tbody></table></div></td></tr></tbody></table>"""  # noqa
        #     )
        #     # generate the from email
        #     # fromemail = testing_email
        #     # generate the mail list by extracting the emails of all the subscribers in the specified group
        #     mailobj = Subscriber.query.filter_by(group_id=group).all()
        #     maillist = []
        #     for mailobj in mailobj:
        #         maillist = maillist + [mailobj.email]
        #     # generate the mail
        #     # message = Mail(
        #     #     from_email=(fromemail, name),
        #     #     to_emails=maillist,
        #     #     subject=subject,
        #     #     html_content=html_content,
        #     # )
        #     try:
        #         # send the email
        #         # sg = SendGridAPIClient(json["sendgridapi"])
        #         # response = sg.send(message)
        #         flash("Mail has been sent successfully!", "success")
        #     except Exception:
        #         # flash an error msg if exception occurs
        #         flash("Error due to invalid details entered!", "danger")
        # # get all the groups and templates in the db to display to the user

        group = Group.query.order_by(Group.id).all()
        mailtemp = Template.query.order_by(Template.id).all()
        flash(
            "Due to security reasons we have disabled mailing functionality!", "warning"
        )
        return redirect("/mail")
    group = Group.query.order_by(Group.id).all()
    mailtemp = Template.query.order_by(Template.id).all()
    return render_template(
        "mail.html", group=group, template=mailtemp, user=current_user
    )


# route to select a template


@app.route("/select/template/<int:id>", methods=["GET"])
@login_required
def select_template(id):
    # get the record of the template to be used
    post = Template.query.filter_by(id=id).first()
    content = {"content": post.content}
    return jsonify(post=content)


# route to use a template
@app.route("/use/template/<int:id>", methods=["GET"])
@login_required
def use_template(id):
    return redirect(url_for("mail_page", selected=id))


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

# home page
@app.route("/")
def home_page():
    response = requests.get(config("contributors_api"))
    team = response.json()
    return render_template("landing.html", team=team)


# dashboard page
@app.route("/dashboard")
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
@admin_required
def users_page():
    # get the records of all the users and display to the user
    users = User.query.order_by(User.id).all()
    return render_template("user_list.html", users=users, user=current_user)


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
            is_staff=False,
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


@app.route("/contact", methods=["POST", "GET"])
def contact():
    if request.method == "POST":
        firstname = request.form.get("firstname")
        lastname = request.form.get("lastname")
        email = request.form.get("email")
        number = request.form.get("number")
        msg = request.form.get("msg")
        print(firstname, lastname, email, number, msg)
        entry = Contact(
            firstname=firstname, lastname=lastname, email=email, number=number, msg=msg
        )
        db.session.add(entry)
        db.session.commit()
        flash("Thanks For Contacting Us Someone will reach you soon!!", "success")
        return redirect("/")
    else:
        return render_template("contact.html")


@app.route("/view/contacts")
@login_required
@admin_required
def contact_page():
    # get the records of all the users and display to the user
    allContacts = Contact.query.all()
    return render_template(
        "contact_table.html", allContacts=allContacts, user=current_user
    )


# for contact
def rowToListContact(obj):
    lst = []
    firstname = obj.firstname
    lastname = obj.lastname
    email = obj.email
    number = obj.number
    msg = obj.msg
    lst.append(firstname)
    lst.append(lastname)
    lst.append(email)
    lst.append(number)
    lst.append(msg)
    return lst


@app.route("/downloadcontact")
@login_required
@admin_required
def ContactToCsv():
    allContacts = Contact.query.all()
    if len(allContacts) == 0:
        flash("No Contacts available", "danger")
        return redirect("/view/contacts")
    si = io.StringIO()
    cw = csv.writer(si, delimiter=",")
    cw.writerow(["FirstName", "LastName", "Email", "Number", "Message"])
    for row in allContacts:
        row = rowToListContact(row)
        cw.writerow(row)
    output = make_response(si.getvalue())
    output.headers["Content-Disposition"] = "attachment; filename=contact_response.csv"
    output.headers["Content-type"] = "text/csv"
    return output


# execute if file is the main file i.e., file wasn't imported
if __name__ == "__main__":
    app.run(debug=True)
