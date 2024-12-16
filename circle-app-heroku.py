import os
import psycopg2
from psycopg2.extras import DictCursor
from urllib.parse import urlparse
from flask import Flask, flash, redirect, render_template, request, session, jsonify, g
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from helpers import login_required, usd, timestamp_formatter, contact_recency_checker, datetimeFormatter, calendar_notifier
import re
from datetime import datetime, timedelta

# Configure application
app = Flask(__name__)

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Get the database URL from the Heroku environment variables
url = urlparse(os.getenv["DATABASE_URL"])

# Connect to the PostgreSQL database
db = psycopg2.connect(
    database=url.path[1:],  # Strip the leading '/'
    user=url.username,
    password=url.password,
    host=url.hostname,
    port=url.port,
    sslmode='require'
)
db.autocommit = True  # Auto commit for every query


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/update_timestamps", methods=["POST"])
def update_timestamps():
    """ If user is in session, update their timestamp to now """
    # If the user is active, update their personal timestamp in users table
    if "user_id" in session:
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # Use the 'with' statement for cursor management
        with db.cursor() as cursor:
            cursor.execute("UPDATE users SET timestamp = %s WHERE id = %s", (now, session["user_id"]))

            # If the active user is the contact of others, update timestamp in contacts table so contacts can access latest activity
            cursor.execute("SELECT * FROM contacts WHERE contact_user_id = %s", (session["user_id"],))
            contactCheck = cursor.fetchone()
            if contactCheck:
                cursor.execute("UPDATE contacts SET contact_timestamp = %s WHERE contact_user_id = %s", (now, session["user_id"]))

        return jsonify({"status": "user timestamp updated"})
    else:
        return jsonify({"status": "user not active"})




@app.route("/", methods=["GET", "POST"])
@login_required
def index():
    """Show app homepage (description and help), reasonably static"""
    if request.method == "POST":
        feedback = request.form.get("feedback")

        # Use the 'with' statement for cursor management
        with db.cursor() as cursor:
            # Check if feedback already exists from this user
            cursor.execute("SELECT * FROM feedback WHERE user_id = %s", (session["user_id"],))
            existing_feedback = cursor.fetchone()

            # Handle form validation
            if not feedback:
                flash("Error submitting feedback.")
                return redirect("/")

            elif existing_feedback:
                flash("You have already submitted feedback.")
                return redirect("/")

            else:
                print(f"Text: {feedback}")
                # Insert feedback into the database
                cursor.execute("INSERT INTO feedback(user_id, feedback) VALUES(%s, %s)", (session["user_id"], feedback))

    else:
        return render_template("homepage.html")



@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Request Method POST: if user attempts login
    if request.method == "POST":

        # Initialize user inputs (request.form.get)
        username = request.form.get("username")
        password = request.form.get("password")

        # Validation: if BOTH username and password are NOT submitted
        if not username and not password:
            flash("Provide a username and password.")
            return redirect("/login")

        # Validation: if only username is NOT submitted
        elif not username:
            flash("Provide a username.")
            return redirect("/login")

        # Validation: if only password is NOT submitted
        elif not password:
            flash("Provide a password.")
            return redirect("/login")

        # Query database for username
        with db.cursor() as cursor:
            cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
            rows = cursor.fetchall()  # Fetch results into a list

            # Validation: if username does not exist or password is incorrect
            if len(rows) != 1 or not check_password_hash(rows[0]["hash"], password):
                flash("Invalid username and/ or password.")
                return redirect("/login")

            # Remember which user has logged in
            session["user_id"] = rows[0]["id"]

            # Update user timestamp
            now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            cursor.execute("UPDATE users SET timestamp = %s WHERE id = %s", (now, session["user_id"]))
            cursor.execute("UPDATE contacts SET contact_timestamp = %s WHERE contact_user_id = %s", (now, session["user_id"]))

        # Redirect user to home page
        return redirect("/")

    # Request Method GET: render login page
    else:
        return render_template("login.html")



@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/login")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    # Request Method GET: if user attempts to register
    if request.method == "POST":

        # Declare username, password, and confirmation for abstraction
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        # Validation: if BOTH username and password are NOT submitted
        if not username and not password:
            flash("Provide a username and password.")
            return redirect("/register")

        # Validation: if username is NOT submitted
        elif not username:
            flash("Provide a username.")
            return redirect("/register")

        # Validation: if password is NOT submitted
        elif not password:
            flash("Provide a password.")
            return redirect("/register")

        # Validation: if password is not: 10+ characters and inclusive of
        # 1+ digit, 1+ lowercase letter, 1+ uppercase letter, 1+ special character
        if not re.search(r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&.,_£€^+=/\|:;]{9,}$", password):
            flash("Password criteria: 10+ characters, 1+ number, 1+ lowercase letter, 1+ uppercase letter, 1+ special character.")
            return redirect("/register")


        # Validation: if password does NOT match password confirmation
        elif password != confirmation:
            flash("Password did not match confirmation.")
            return redirect("/register")

        # Query database for data related to input username
        with db.cursor() as cursor:
            cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
            rows = cursor.fetchall()

            # If query returns empty list, then username is not taken
            # So, store the username and hash value of the password in the users table (and current timestamp)
            if not rows:
                hashPassword = generate_password_hash(password)

                # Add new user to users table in database
                now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                cursor.execute("INSERT INTO users(username, hash, timestamp, creation_timestamp) VALUES(%s, %s, %s, %s)",
                               (username, hashPassword, now, now))
                db.commit()  # Commit the insert operation

                # And then log the user in
                cursor.execute("SELECT id FROM users WHERE username = %s", (username,))
                new_user = cursor.fetchone()
                session["user_id"] = new_user[0]
                flash("Registered.")
                return redirect("/")

            # Else, username is taken
            else:
                flash("Username taken.")
                return redirect("/register")

    # Request Method GET: render register page
    else:
        return render_template("register.html")




@app.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    """Display user details, user friends contacts, user family contacts"""
    # Initialize global variables
    with db.cursor() as cursor:
        cursor.execute("SELECT * FROM contacts WHERE active_user_id = %s AND relation = %s", (session["user_id"], 'friend'))
        friends = cursor.fetchall()

        cursor.execute("SELECT COUNT(*) AS n FROM contacts WHERE active_user_id = %s AND relation = %s", (session["user_id"], 'friend'))
        friendsCountResult = cursor.fetchone()
        friendsCount = friendsCountResult["n"]

        cursor.execute("SELECT * FROM contacts WHERE active_user_id = %s AND relation = %s", (session["user_id"], 'family'))
        families = cursor.fetchall()

        cursor.execute("SELECT COUNT(*) AS n FROM contacts WHERE active_user_id = %s AND relation = %s", (session["user_id"], 'family'))
        familiesCountResult = cursor.fetchone()
        familiesCount = familiesCountResult["n"]

        cursor.execute("SELECT * FROM users WHERE id = %s", (session["user_id"],))
        returned = cursor.fetchone()
        username = returned["username"]

        accountCreationTimestamp = returned["creation_timestamp"]
        datetimeObject = datetime.strptime(accountCreationTimestamp, '%Y-%m-%d %H:%M:%S')
        accountCreationDate = datetimeObject.strftime(('%A %d %B, %Y'))

    # Request Method GET: access database for 3 profile sections:
    if request.method == "GET":
        # When loading profile page, first update and format contact last active timestamps
        with db.cursor() as cursor:
            for friend in friends:
                cursor.execute("SELECT timestamp, id FROM users WHERE username = %s", (friend["contact_username"],))
                friend_id_and_timestamp = cursor.fetchone()
                formatFriendTimestamp = timestamp_formatter(friend_id_and_timestamp["timestamp"])
                cursor.execute("UPDATE contacts SET contact_timestamp = %s WHERE contact_user_id = %s", (formatFriendTimestamp, friend_id_and_timestamp["id"]))

            for family in families:
                cursor.execute("SELECT timestamp, id FROM users WHERE username = %s", (family["contact_username"],))
                family_id_and_timestamp = cursor.fetchone()
                formatFamilyTimestamp = timestamp_formatter(family_id_and_timestamp["timestamp"])
                cursor.execute("UPDATE contacts SET contact_timestamp = %s WHERE contact_user_id = %s", (formatFamilyTimestamp, family_id_and_timestamp["id"]))

        # Declare updated friends and family lists
        with db.cursor() as cursor:
            cursor.execute("SELECT * FROM contacts WHERE active_user_id = %s AND relation = %s", (session["user_id"], 'friend'))
            friends = cursor.fetchall()

            cursor.execute("SELECT * FROM contacts WHERE active_user_id = %s AND relation = %s", (session["user_id"], 'family'))
            families = cursor.fetchall()

        # Render template with these up to date, formatted timestamps
        return render_template("profile.html", friends=friends, families=families, friendsCount=friendsCount,
                               familiesCount=familiesCount, username=username, accountCreationDate=accountCreationDate)



@app.route("/delete_account", methods=["POST"])
@login_required
def deleteAccount():
    """ Delete user's account on form confirmation """
    confirmation = request.form.get("confirmDeletion")

    if confirmation:
        with db.cursor() as cursor:
            cursor.execute("DELETE FROM users WHERE id = %s", (session["user_id"],))

        return redirect("/login")
    else:
        return redirect("/profile")


@app.route("/calendar", methods=["GET"])
@login_required
def calendar():
    """Display calendar form with list of user contacts for options, and update related notifications"""
    # Initialize global variables
    user_id = session["user_id"]

    with db.cursor() as cursor:
        # Get user contacts
        cursor.execute("SELECT contact_name FROM contacts WHERE active_user_id = %s", (session["user_id"],))
        userContacts = cursor.fetchall()

        # When page loaded, update any active calendar related notifications: "receiverHasOpened" = true
        cursor.execute("UPDATE calendar_events SET receiverHasOpened = %s WHERE receiver_id = %s AND receiverHasOpened = %s",
                       (1, session["user_id"], 0))

        # Handle calendar-related notifications
        cursor.execute("SELECT id FROM notifications WHERE user_id = %s AND isActive = %s AND (type = %s OR type = %s OR type = %s)",
                       (session["user_id"], 1, "calendar_updates", "calendar_reminders", "calendar_deletions"))
        notification_IDs = cursor.fetchall()

        # Update notifications
        if notification_IDs:
            for notification in notification_IDs:
                cursor.execute("UPDATE notifications SET isActive = %s WHERE id = %s", (0, notification["id"]))

    return render_template("calendar.html", userContacts=userContacts, user_id=user_id)



@app.route("/add_calendar_event", methods=["GET", "POST"])
@login_required
def add_calendar_event():
    """ On calendar form submission, add calendar event to database """
    # Initialize variables from calendar form on submission
    creator_id = session["user_id"]
    data = request.json
    title = data.get("title")
    receiverName = data.get("contact")
    unformattedDatetime = data.get("datetime")
    datetime = datetimeFormatter(unformattedDatetime)

    # Retrieve relevant user and contact info
    with db.cursor() as cursor:
        cursor.execute("SELECT contact_user_id FROM contacts WHERE active_user_id = %s AND contact_name = %s",
                       (session["user_id"], receiverName))
        receiverID_return = cursor.fetchone()

        if receiverID_return:
            receiverID = receiverID_return["contact_user_id"]
        else:
            return jsonify({"success": False, "error": "Receiver ID not found"})

        cursor.execute("SELECT contact_name FROM contacts WHERE active_user_id = %s AND contact_user_id = %s",
                       (receiverID, creator_id))
        creatorName_return = cursor.fetchone()

        if creatorName_return:
            creatorName = creatorName_return["contact_name"]
        else:
            return jsonify({"success": False, "error": "Creator name not found"})

        # Insert calendar appointment into database
        cursor.execute("INSERT INTO calendar_events(creator_id, receiver_id, creator_name, receiver_name, date, title, date_std) VALUES(?, ?, ?, ?, ?, ?, ?)",
                       (creator_id, receiverID, creatorName, receiverName, datetime, title, unformattedDatetime))

        # Retrieve the new calendar event ID
        cursor.execute("SELECT id FROM calendar_events ORDER BY id DESC LIMIT 1")
        result = cursor.fetchone()
        lastrowID = result["id"] if result else None

        if not lastrowID:
            return jsonify({"success": False, "error": "Failed to retrieve event ID"})

        # Retrieve the new calendar event formatted datetime and standardized datetime
        cursor.execute("SELECT date, date_std FROM calendar_events WHERE id = %s", (lastrowID,))
        dateResult = cursor.fetchone()
        date = dateResult["date"] if dateResult else None
        date_std = dateResult["date_std"] if dateResult else None

        if not date or not date_std:
            return jsonify({"success": False, "error": "Failed to retrieve event dates"})

        # Insert two rows in calendar_position_and_notation table (default values) for creator user & receiver user
        cursor.execute("INSERT INTO calendar_position_and_notation(user_id, calendar_event_id) VALUES(?, ?)",
                       (creator_id, lastrowID))
        cursor.execute("INSERT INTO calendar_position_and_notation(user_id, calendar_event_id) VALUES(?, ?)",
                       (receiverID, lastrowID))

    return jsonify({"success": True, "id": lastrowID, "datetime": date, "datetimeStandard": date_std})



@app.route("/send_calendar_events", methods=["GET"])
@login_required
def send_calendar_events():
    """ Send calendar event info to frontend for javascript creation and display of "calendar sticky notes" """

    try:
        with db.cursor() as cursor:
            cursor.execute("""
                SELECT
                    calendar_events.id AS event_id,
                    calendar_events.creator_id,
                    calendar_events.receiver_id,
                    calendar_events.creator_name,
                    calendar_events.receiver_name,
                    calendar_events.date,
                    calendar_events.title,
                    calendar_events.date_std,
                    calendar_position_and_notation.top,
                    calendar_position_and_notation.left,
                    calendar_position_and_notation.notation
                FROM
                    calendar_events
                JOIN
                    calendar_position_and_notation
                ON
                    calendar_events.id = calendar_position_and_notation.calendar_event_id
                WHERE
                    calendar_position_and_notation.user_id = ?
            """, (session["user_id"],))

            # Fetch all the results
            calendar_data = cursor.fetchall()

        # Return joined table to front end
        return jsonify(calendar_data), 200

    except Exception as e:
        # Log the error message to the server logs for debugging purposes
        print(f"Error in /send_calendar_events: {e}")

        # Return an error response with a 500 Internal Server Error status code
        return jsonify({'success': False, 'message': 'An error occurred while fetching calendar events.'}), 500


@app.route("/update_calendar_styles", methods=["POST"])
@login_required
def update_calendar_styles():
    """ Every time a calendar sticky note's page positioning or notation is edited by user, update related database table values """
    try:
        # Extract data from request
        data = request.json
        id = data.get('id')
        top = data.get('top')
        left = data.get('left')
        notation = data.get('notation')

        # Validate data
        if id is None or top is None or left is None:
            return jsonify({'success': False, 'message': 'Missing required fields'}), 400

        # Update calendar sticky note top and left styling and notation content
        with db.cursor() as cursor:
            cursor.execute("""
                UPDATE
                    calendar_position_and_notation
                SET
                    top = ?,
                    left = ?,
                    notation = ?
                WHERE
                    calendar_event_id = ?
                    AND user_id = ?
            """, (top, left, notation, id, session["user_id"]))

        return jsonify({'success': True}), 200

    except Exception as e:
        # Log the error message with the data for better debugging
        print(f"Error in /update_calendar_styles: {e}, Data: {data}")

        return jsonify({'success': False, 'message': 'An error occurred while updating calendar styles.'}), 500



@app.route("/delete_calendar_event", methods=["POST"])
@login_required
def delete_calendar_event():
    """ Delete calendar event from database, and add info to deleted table for notifications """
    try:
        # Extract data from request
        data = request.json
        id = data.get('id')

        # Validate data
        if not id:
            return jsonify({'success': False, 'message': 'Missing id value'}), 400

        # Establish cursor for PostgreSQL
        with db.cursor() as cursor:
            # Retrieve the calendar event to be deleted
            cursor.execute("SELECT * FROM calendar_events WHERE id = %s", (id,))
            deleted_info = cursor.fetchone()

            if not deleted_info:
                return jsonify({'success': False, 'message': 'Calendar event not found'}), 404

            title = deleted_info["title"]
            deleter_id = session["user_id"]

            # Determine who is the deleter and deletee based on creator and receiver
            if deleter_id == deleted_info["creator_id"]:
                deletee_id = deleted_info["receiver_id"]
                deletee_name = deleted_info["receiver_name"]
                deleter_name = deleted_info["creator_name"]
            else:
                deletee_id = deleted_info["creator_id"]
                deletee_name = deleted_info["creator_name"]
                deleter_name = deleted_info["receiver_name"]

            # Insert into deleted_calendar_events table
            cursor.execute("""
                INSERT INTO deleted_calendar_events(deleter_id, deletee_id, deleter_name, deletee_name, title)
                VALUES (%s, %s, %s, %s, %s)
            """, (deleter_id, deletee_id, deleter_name, deletee_name, title))

            # Delete the calendar event and related position/notation rows
            cursor.execute("DELETE FROM calendar_events WHERE id = %s", (id,))
            cursor.execute("DELETE FROM calendar_position_and_notation WHERE calendar_event_id = %s", (id,))

            # Commit the changes (needed because autocommit is not enabled by default in PostgreSQL)
            db.commit()

        return jsonify({'success': True}), 200

    except Exception as e:
        # Log the error for debugging
        print(f"Error in /delete_calendar_event: {e}")
        return jsonify({'success': False, 'message': 'An error occurred while deleting the calendar event.'}), 500


    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'success': False, 'message': 'An error occurred'}), 500


@app.route("/removeContact", methods=["POST"])
@login_required
def removeContact():
    """ Simply, delete from contacts table on contact deletion """

    # Extract the form data
    friendUsername = request.form.get("friendUsername")
    familyUsername = request.form.get("familyUsername")

    # Ensure a cursor is used for PostgreSQL interaction
    try:
        with db.cursor() as cursor:
            if friendUsername:
                # Delete friend contact from active user's contacts
                cursor.execute("DELETE FROM contacts WHERE active_user_id = %s AND contact_username = %s",
                               (session["user_id"], friendUsername))
                # Retrieve contact's ID from users table
                cursor.execute("SELECT id FROM users WHERE username = %s", (friendUsername,))
                row = cursor.fetchone()
                if row:
                    contact_id = row["id"]
                    # Delete active user from the contact's contacts
                    cursor.execute("DELETE FROM contacts WHERE active_user_id = %s AND contact_user_id = %s",
                                   (contact_id, session["user_id"]))
                    flash(f"{friendUsername} removed from your circle")
                else:
                    flash(f"Contact {friendUsername} not found.")

            if familyUsername:
                # Delete family contact from active user's contacts
                cursor.execute("DELETE FROM contacts WHERE active_user_id = %s AND contact_username = %s",
                               (session["user_id"], familyUsername))
                # Retrieve contact's ID from users table
                cursor.execute("SELECT id FROM users WHERE username = %s", (familyUsername,))
                row = cursor.fetchone()
                if row:
                    contact_id = row["id"]
                    # Delete active user from the contact's contacts
                    cursor.execute("DELETE FROM contacts WHERE active_user_id = %s AND contact_user_id = %s",
                                   (contact_id, session["user_id"]))
                    flash(f"{familyUsername} removed from your circle")
                else:
                    flash(f"Contact {familyUsername} not found.")

        # Changes are automatically committed with autocommit enabled
    except Exception as e:
        print(f"Error in /removeContact: {e}")
        flash("An error occurred while removing the contact.")

    return redirect("/profile")



@app.route("/editContactName", methods=["POST"])
@login_required
def editContactUsername():
    """Update contacts table 'contact_name' on name update form submission"""
    contactUsername = request.form.get("contactUsername")
    newName = request.form.get("newContactName")

    if not contactUsername or not newName:
        return redirect("/profile")

    try:
        with db.cursor() as cursor:
            cursor.execute(
                """
                UPDATE contacts
                SET contact_name = %s
                WHERE contact_username = %s AND active_user_id = %s
                """,
                (newName, contactUsername, session["user_id"])
            )
        return redirect("/profile")

    except Exception as e:
        # Log the error for debugging
        print(f"Error in editContactUsername: {e}")
        return redirect("/profile")



@app.route("/send_contact_request", methods=["POST"])
@login_required
def send_contact_request():
    """Send friend/family request to contact on contact add form submission if user has less than 10 friends/10 family"""

    # Global variables
    friend = request.form.get("usernameFriendSearch")
    family = request.form.get("usernameFamilySearch")
    sender_id = session["user_id"]

    try:
        with db.cursor() as cursor:
            # Check friend count
            cursor.execute("""
                SELECT COUNT(*) AS n
                FROM contacts
                WHERE active_user_id = %s AND relation = %s
            """, (sender_id, 'friend'))
            friends_count = cursor.fetchone()["n"]

            # Check family count
            cursor.execute("""
                SELECT COUNT(*) AS n
                FROM contacts
                WHERE active_user_id = %s AND relation = %s
            """, (sender_id, 'family'))
            families_count = cursor.fetchone()["n"]

            # Validation: No username provided
            if not friend and not family:
                flash("Provide a username to add to your circle")
                return redirect("/profile")

            # Determine contact type
            if friend:
                contact_username = friend
                contact_relation = "friend"
                if friends_count == 10:
                    flash("Your friends' circle is at capacity.")
                    return redirect("/profile")
            elif family:
                contact_username = family
                contact_relation = "family"
                if families_count == 10:
                    flash("Your family's circle is at capacity.")
                    return redirect("/profile")

            # Check if contact exists
            cursor.execute("SELECT id FROM users WHERE username = %s", (contact_username,))
            receiver = cursor.fetchone()
            if not receiver:
                flash("User does not exist")
                return redirect("/profile")

            receiver_id = receiver["id"]

            # Validation: Prevent duplicate requests
            cursor.execute("""
                SELECT 1
                FROM contact_requests
                WHERE sender_id = %s AND receiver_id = %s
            """, (sender_id, receiver_id))
            if cursor.fetchone():
                flash("Request already sent")
                return redirect("/profile")

            # Validation: Prevent self-requests
            if receiver_id == sender_id:
                flash("Can't add yourself, genius")
                return redirect("/profile")

            # Check if already in contacts
            cursor.execute("""
                SELECT 1
                FROM contacts
                WHERE active_user_id = %s AND contact_username = %s
            """, (sender_id, contact_username))
            if cursor.fetchone():
                flash(f"{contact_username} is already in your circle")
                return redirect("/profile")

            # Add request to `contact_requests` table
            cursor.execute("""
                INSERT INTO contact_requests (sender_id, receiver_id, relation)
                VALUES (%s, %s, %s)
            """, (sender_id, receiver_id, contact_relation))

        flash(f"{contact_username} has been invited into your Circle")
        return redirect("/profile")

    except Exception as e:
        print(f"Error in send_contact_request: {e}")
        flash("An error occurred while processing your request")
        return redirect("/profile")



@app.route("/handle_contact_request", methods=["POST"])
@login_required
def handle_contact_request():
    """Accept or reject a contact request"""
    # Retrieve form info
    acceptedFriend = request.form.get("acceptFriendUsername")
    rejectedFriend = request.form.get("rejectFriendUsername")
    acceptedFamily = request.form.get("acceptFamilyUsername")
    rejectedFamily = request.form.get("rejectFamilyUsername")

    try:
        with db.cursor() as cursor:
            # If the contact request was an "accept"
            if acceptedFriend or acceptedFamily:
                if acceptedFriend:
                    addContactUsername = acceptedFriend
                    contactRelation = "friend"
                if acceptedFamily:
                    addContactUsername = acceptedFamily
                    contactRelation = "family"

                # Retrieve sender ID and timestamp
                cursor.execute("SELECT timestamp, id FROM users WHERE username = %s", (addContactUsername,))
                sender_data = cursor.fetchone()
                sender_id = sender_data["id"]
                formattedSenderTimestamp = timestamp_formatter(sender_data["timestamp"])

                # Add sender to receiver's contacts
                cursor.execute("""
                    INSERT INTO contacts (active_user_id, contact_user_id, contact_username, relation, contact_timestamp)
                    VALUES (%s, %s, %s, %s, %s)
                """, (session["user_id"], sender_id, addContactUsername, contactRelation, formattedSenderTimestamp))

                # Add receiver to sender's contacts
                cursor.execute("SELECT timestamp, username FROM users WHERE id = %s", (session["user_id"],))
                receiver_data = cursor.fetchone()
                activeUsername = receiver_data["username"]
                formattedReceiverTimestamp = timestamp_formatter(receiver_data["timestamp"])

                cursor.execute("""
                    INSERT INTO contacts (active_user_id, contact_user_id, contact_username, relation, contact_timestamp)
                    VALUES (%s, %s, %s, %s, %s)
                """, (sender_id, session["user_id"], activeUsername, contactRelation, formattedReceiverTimestamp))

                # Remove the contact request
                cursor.execute("""
                    DELETE FROM contact_requests
                    WHERE receiver_id = %s AND sender_id IN (SELECT id FROM users WHERE username = %s)
                """, (session["user_id"], addContactUsername))

                flash(f"{addContactUsername} added to your {contactRelation} circle")

            # If the contact request was a "reject"
            else:
                if rejectedFriend:
                    rejectContactUsername = rejectedFriend
                    contactRelation = "friend"
                if rejectedFamily:
                    rejectContactUsername = rejectedFamily
                    contactRelation = "family"

                # Remove the contact request
                cursor.execute("""
                    DELETE FROM contact_requests
                    WHERE receiver_id = %s AND sender_id IN (SELECT id FROM users WHERE username = %s)
                """, (session["user_id"], rejectContactUsername))

                flash(f"{rejectContactUsername} rejected from your {contactRelation} circle")

        return redirect("/profile")

    except Exception as e:
        print(f"Error in handle_contact_request: {e}")
        flash("An error occurred while processing your request")
        return redirect("/profile")



@app.before_request
def load_user_data():
    """Make user data globally accessible"""
    if "user_id" in session:
        try:
            with db.cursor() as cursor:
                # Retrieve user data
                cursor.execute("SELECT * FROM users WHERE id = %s", (session["user_id"],))
                user_data = cursor.fetchone()
                g.user_data = user_data if user_data else None
        except Exception as e:
            print(f"Error in load_user_data: {e}")
            g.user_data = None
    else:
        g.user_data = None



@app.context_processor
def display_contact_requests():
    """Display user's contact requests in navbar by injecting said info into all templates (context processor)."""
    if "user_id" in session:
        try:
            with db.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                # Fetch friend requests
                cursor.execute("""
                    SELECT username
                    FROM users
                    WHERE id IN (
                        SELECT sender_id
                        FROM contact_requests
                        WHERE receiver_id = %s AND relation = %s
                    )
                """, (session["user_id"], 'friend'))
                friend_requests = cursor.fetchall()

                # Fetch family requests
                cursor.execute("""
                    SELECT username
                    FROM users
                    WHERE id IN (
                        SELECT sender_id
                        FROM contact_requests
                        WHERE receiver_id = %s AND relation = %s
                    )
                """, (session["user_id"], 'family'))
                family_requests = cursor.fetchall()

                # Convert results to list of dictionaries for easier template usage
                friend_requests = [row["username"] for row in friend_requests] if friend_requests else None
                family_requests = [row["username"] for row in family_requests] if family_requests else None

        except Exception as e:
            print(f"Error in display_contact_requests: {e}")
            friend_requests, family_requests = None, None

        return dict(friend_requests=friend_requests, family_requests=family_requests)

    return dict(friend_requests=None, family_requests=None)



@app.route("/customise_CAN", methods=["POST"])
@login_required
def customise_CAN():
    """When user submits form, customise CAN (contact absence notification) period for a given contact in the database"""
    # Retrieve form info
    contactUsername = request.form.get("contactUsername")
    CAN_period_weeks = request.form.get("CAN_period_weeks")

    # If values retrieved, update database
    if contactUsername and CAN_period_weeks:
        try:
            # Ensure CAN_period_weeks is a valid integer
            CAN_period_weeks = int(CAN_period_weeks)
            if CAN_period_weeks <= 0:
                flash("Please enter a valid positive number for CAN period.")
                return redirect("/profile")
        except ValueError:
            flash("Invalid input for CAN period. Please enter a valid number.")
            return redirect("/profile")

        try:
            # Establish database connection with autocommit enabled
            with db.cursor() as cursor:
                # Update the contact's CAN period in the database
                cursor.execute("""
                    UPDATE contacts
                    SET CAN_period_weeks = %s
                    WHERE active_user_id = %s AND contact_username = %s
                """, (CAN_period_weeks, session["user_id"], contactUsername))

                # Retrieve the contact name to display in the flash message
                cursor.execute("""
                    SELECT contact_name
                    FROM contacts
                    WHERE active_user_id = %s AND contact_username = %s
                """, (session["user_id"], contactUsername))

                result = cursor.fetchone()
                if result:
                    contactName = result["contact_name"]
                    flash(f"Contact absence notification period set as {CAN_period_weeks} weeks for {contactName}.")
                else:
                    flash(f"Contact {contactUsername} not found.")
                    return redirect("/profile")
        except Exception as e:
            print(f"Error in customise_CAN: {e}")
            flash("Error updating CAN.")
            return redirect("/profile")
    else:
        flash("Error updating CAN.")
        return redirect("/profile")

    return redirect("/profile")



@app.context_processor
def display_notifications():
    """ Every time a user changes or reloads a page:
    Check if their last contact with any of their contacts exceeds CAN (contact absence notification) period
    Check if user has any unopened messages
    Check if user has any calendar updates/ reminders/ deletions """

    if "user_id" in session:

        # Initialize current time for database entries
        now = datetime.now()

        # CAN notifications
        # Query user's contacts' IDs and names
        with db.cursor() as cursor:
            cursor.execute("SELECT * FROM contacts WHERE active_user_id = %s AND hasCAN = %s", (session["user_id"], 0))
            userContactInfo = cursor.fetchall()

            # For every one of active user's contacts, determine if contact absence notification is necessary
            for row in userContactInfo:
                id = row["id"]
                contactID = row["contact_user_id"]
                contactName = row["contact_name"]
                cursor.execute("SELECT CAN_period_weeks FROM contacts WHERE active_user_id = %s AND contact_user_id = %s", (session["user_id"], contactID))
                CAN_return = cursor.fetchone()
                CAN_period_weeks = CAN_return["CAN_period_weeks"]
                cursor.execute("SELECT timestamp FROM messages WHERE sender_id = %s AND receiver_id = %s ORDER BY timestamp DESC",
                               (session["user_id"], contactID))
                messageTimestamps = cursor.fetchall()

                if messageTimestamps:
                    mostRecentMessageTimestamp = messageTimestamps[0]["timestamp"]

                    # If CAN is necessary, append notification message to notification list
                    if contact_recency_checker(mostRecentMessageTimestamp, CAN_period_weeks):
                        cursor.execute("INSERT INTO notifications(user_id, content, type, creation_timestamp) VALUES(%s, %s, %s, %s)",
                                       (session["user_id"],
                                        f"{contactName}: last contact over {CAN_period_weeks} weeks ago",
                                        "CAN",
                                        now))
                        cursor.execute("UPDATE contacts SET hasCAN = %s WHERE id = %s", (1, id))

        # Friend message Notifications
        with db.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) as n FROM contacts WHERE active_user_id = %s AND relation = %s AND has_unopened_message = %s",
                           (session["user_id"], 'friend', 1))
            friendCountResult = cursor.fetchone()
            friendCount = friendCountResult["n"]

            if friendCount == 1:
                cursor.execute("DELETE FROM notifications WHERE user_id = %s AND type = %s", (session["user_id"], "friend_messages"))
                # If notification is not already active, add to notifications table for display
                cursor.execute("SELECT * FROM notifications WHERE user_id = %s AND content = %s",
                               (session["user_id"], "1 unopened message from friend"))
                if not cursor.fetchone():
                    cursor.execute("INSERT INTO notifications(user_id, content, type, creation_timestamp) VALUES(%s, %s, %s, %s)",
                                   (session["user_id"], "1 unopened message from friend", "friend_messages", now))

            elif friendCount > 1:
                cursor.execute("DELETE FROM notifications WHERE user_id = %s AND type = %s", (session["user_id"], "friend_messages"))
                # If notification is not already active, add to notifications table for display
                cursor.execute("SELECT * FROM notifications WHERE user_id = %s AND content = %s",
                               (session["user_id"], f"{friendCount} unopened messages from friends"))
                if not cursor.fetchone():
                    cursor.execute("INSERT INTO notifications(user_id, content, type, creation_timestamp) VALUES(%s, %s, %s, %s)",
                                   (session["user_id"], f"{friendCount} unopened messages from friends", "friend_messages", now))

            else:
                cursor.execute("DELETE FROM notifications WHERE user_id = %s AND type = %s", (session["user_id"], "friend_messages"))

        # Family message notifications
        with db.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) as n FROM contacts WHERE active_user_id = %s AND relation = %s AND has_unopened_message = %s",
                           (session["user_id"], 'family', 1))
            familyCountResult = cursor.fetchone()
            familyCount = familyCountResult["n"]

            if familyCount == 1:
                cursor.execute("DELETE FROM notifications WHERE user_id = %s AND type = %s", (session["user_id"], "family_messages"))
                # If notification is not already active, add to notifications table for display
                cursor.execute("SELECT * FROM notifications WHERE user_id = %s AND content = %s",
                               (session["user_id"], "1 unopened message from family"))
                if not cursor.fetchone():
                    cursor.execute("INSERT INTO notifications(user_id, content, type, creation_timestamp) VALUES(%s, %s, %s, %s)",
                                   (session["user_id"], "1 unopened message from family", "family_messages", now))

            elif familyCount > 1:
                cursor.execute("DELETE FROM notifications WHERE user_id = %s AND type = %s", (session["user_id"], "family_messages"))
                # If notification is not already active, add to notifications table for display
                cursor.execute("SELECT * FROM notifications WHERE user_id = %s AND content = %s",
                               (session["user_id"], f"{familyCount} unopened messages from family"))
                if not cursor.fetchone():
                    cursor.execute("INSERT INTO notifications(user_id, content, type, creation_timestamp) VALUES(%s, %s, %s, %s)",
                                   (session["user_id"], f"{familyCount} unopened messages from family", "family_messages", now))

            else:
                cursor.execute("DELETE FROM notifications WHERE user_id = %s AND type = %s", (session["user_id"], "family_messages"))

        # Calendar updates
        with db.cursor() as cursor:
            cursor.execute("SELECT * FROM calendar_events WHERE receiver_id = %s AND receiverHasOpened = %s AND receiverNotified = %s",
                           (session["user_id"], 0, 0))
            updates = cursor.fetchall()

            if updates:
                # Loop through all calendar events for user, retrieve notification relevant info
                for update in updates:
                    if session["user_id"] == update["creator_id"]:
                        name = update["receiver_name"]
                    else:
                        name = update["creator_name"]
                        cursor.execute("INSERT INTO notifications(user_id, content, type, creation_timestamp) VALUES(%s, %s, %s, %s)",
                                       (session["user_id"], f"New calendar date with {name}", "calendar_updates", now))
                        id = update["id"]
                        # Add info to notifications table for display
                        cursor.execute("UPDATE calendar_events SET receiverNotified = %s WHERE id = %s", (1, id))

        # Calendar reminders
        with db.cursor() as cursor:
            cursor.execute("SELECT * FROM calendar_events WHERE (creator_id = %s OR receiver_id = %) AND receiverReminded = %s",
                           (session["user_id"], session["user_id"], 0))
            reminders = cursor.fetchall()

            if reminders:
                # Loop through all user's calendar events, calculate whether reminder notification is now necessary
                for reminder in reminders:
                    calendarDatetime = reminder["date"]
                    if calendar_notifier(calendarDatetime):
                        dtObject = datetime.strptime(calendarDatetime, '%d %B at %I:%M %p')
                        time = dtObject.strftime('%H:%M %p')

                        if session["user_id"] == reminder["creator_id"]:
                            name = reminder["receiver_name"]
                        else:
                            name = reminder["creator_name"]

                        cursor.execute("INSERT INTO notifications(user_id, content, type, creation_timestamp) VALUES(%s, %s, %s, %s)",
                                       (session["user_id"], f"Calendar reminder - today at {time} with {name}", "calendar_reminders", now))
                        id = reminder["id"]
                        cursor.execute("UPDATE calendar_events SET receiverReminded = %s WHERE id = %s", (1, id))

        # Deleted calendar notifications
        with db.cursor() as cursor:
            cursor.execute("SELECT * FROM deleted_calendar_events WHERE deletee_id = %s AND isNotified = %s",
                           (session["user_id"], 0))
            deletedInfo = cursor.fetchall()

            if deletedInfo:
                for row in deletedInfo:
                    deleterName = row["deleter_name"]
                    title = row["title"]
                    id = row["id"]

                    cursor.execute("INSERT INTO notifications(user_id, content, type, creation_timestamp) VALUES(%s, %s, %s, %s)",
                                   (session["user_id"], f"Calendar event '{title}' deleted by {deleterName}", "calendar_deletions", now))
                    cursor.execute("UPDATE deleted_calendar_events SET isNotified = %s WHERE id = %s", (1, id))

        # Finally, display all user's notifications in descending date order (notification active status filtered in front end)
        with db.cursor() as cursor:
            cursor.execute("SELECT * FROM notifications WHERE user_id = %s ORDER BY id DESC", (session["user_id"],))
            notifications = cursor.fetchall()

            # If there are notifications with active status, front end will display notifications icon
            cursor.execute("SELECT * FROM notifications WHERE user_id = %s AND isActive = %s",
                           (session["user_id"], 1))
            activeNotifications = cursor.fetchall()

            return dict(notifications=notifications, activeNotifications=activeNotifications)



@app.route("/messages", methods=["GET", "POST"])
@login_required
def messages():
    """ Display friends and family contacts (clickable to access messages), and sender user_id to page for value passing """
    if request.method == "GET":
        try:
            # Fetching friends and family contacts for the active user using cursor
            with db.cursor() as cursor:
                cursor.execute("SELECT * FROM contacts WHERE active_user_id = %s AND relation = %s", (session["user_id"], 'friend'))
                friends = cursor.fetchall()

                cursor.execute("SELECT * FROM contacts WHERE active_user_id = %s AND relation = %s", (session["user_id"], 'family'))
                families = cursor.fetchall()

            # Pass the contacts and user_id to the messages template
            return render_template("messages.html", friends=friends, families=families, user_id=session["user_id"])

        except Exception as e:
            print(f"Error fetching contacts: {e}")
            return render_template("error.html", message="An error occurred while fetching contacts.")



@app.route("/send_message", methods=["POST"])
@login_required
def send_message():
    """Send a message to a user's contact"""
    if "user_id" not in session:
        return redirect("/login")

    # Retrieve form data
    sender_id = session["user_id"]
    receiver_id = request.form.get("receiver_id")
    content = request.form.get("content")
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # Validate fields
    if not receiver_id or not content:
        return jsonify({"status": "Error", "message": "Missing fields"}), 400

    # Insert content of message into messages database table, and automatically set "is_unopened" value to true
    try:
        with db.cursor() as cursor:
            # Insert message into the database
            cursor.execute("INSERT INTO messages (sender_id, receiver_id, content, timestamp) VALUES (%s, %s, %s, %s)",
                           (sender_id, receiver_id, content, now))
            # Update the contact's unread message status
            cursor.execute("UPDATE contacts SET has_unopened_message = %s WHERE active_user_id = %s AND contact_user_id = %s",
                           (1, receiver_id, sender_id))

            # Also, if sender has an active CAN notification (hasCAN = true), update hasCAN to false now that contact reinitiated
            cursor.execute("SELECT * FROM contacts WHERE hasCAN = %s AND active_user_id = %s AND contact_user_id = %s",
                           (1, sender_id, receiver_id))
            sender_has_can = cursor.fetchone()

            if sender_has_can:
                # Update the hasCAN value to false
                cursor.execute("UPDATE contacts SET hasCAN = %s WHERE active_user_id = %s AND contact_user_id = %s",
                               (0, sender_id, receiver_id))

                # Deactivate the notification related to the sender's CAN status
                contact_name = sender_has_can["contact_name"]
                can_period = sender_has_can["CAN_period_weeks"]
                cursor.execute("UPDATE notifications SET isActive = %s WHERE user_id = %s AND type = %s AND content = %s",
                               (0, sender_id, "CAN", f"{contact_name}: last contact over {can_period} weeks ago"))

        return jsonify({"status": "Message sent, and unopened status==TRUE"})

    except Exception as e:
        print(f"Error: {e}")
        return "Internal Server Error", 500



@app.route("/messages/<int:contact_id>")
@login_required
def get_message(contact_id):
    """Fetch messages between active user and selected contact"""
    if "user_id" not in session:
        return redirect("/login")

    try:
        with db.cursor() as cursor:
            # Fetch messages between the active user and the selected contact
            cursor.execute("""
                SELECT * FROM messages
                WHERE (sender_id = %s AND receiver_id = %s)
                OR (sender_id = %s AND receiver_id = %s)
                ORDER BY timestamp ASC
            """, (session["user_id"], contact_id, contact_id, session["user_id"]))
            messages = cursor.fetchall()

            # Update the "is_unopened" status to false for the selected contact's messages
            cursor.execute("""
                UPDATE contacts
                SET has_unopened_message = %s
                WHERE contact_user_id = %s AND active_user_id = %s AND has_unopened_message = %s
            """, (0, contact_id, session["user_id"], 1))

        # Format timestamps and prepare the response
        formatted_messages = []
        for message in messages:
            formatted_message = {
                "sender_id": message["sender_id"],
                "receiver_id": message["receiver_id"],
                "content": message["content"],
                "timestamp": timestamp_formatter(message["timestamp"])
            }
            formatted_messages.append(formatted_message)

        return jsonify(formatted_messages)

    except Exception as e:
        print(f"Error: {e}")
        return "Internal Server Error", 500


