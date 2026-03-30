from flask import Flask, request, jsonify, g, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv
import mysql.connector
import os
import jwt
import datetime
from functools import wraps
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash

from mailer import (
    send_verification_email,
    send_reset_email,
    render_verification_success_page,
    render_verification_error_page,
)

load_dotenv()

app = Flask(__name__)
CORS(app)

PORT = int(os.getenv("PORT", 5100))
JWT_SECRET = os.getenv("JWT_SECRET", "my_super_secret_key_123")
APP_BASE_URL = os.getenv("APP_BASE_URL", f"http://localhost:{PORT}")

UPLOADS_ROOT = os.path.join(os.path.dirname(__file__), "uploads")
PROFILE_DIR = os.path.join(UPLOADS_ROOT, "profile")
ACCOUNT_DIR = os.path.join(UPLOADS_ROOT, "account")

os.makedirs(PROFILE_DIR, exist_ok=True)
os.makedirs(ACCOUNT_DIR, exist_ok=True)

ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png", "webp"}
blacklisted_tokens = set()


# =========================
# DATABASE CONNECTION
# =========================
def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST", "localhost"),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD", ""),
        database=os.getenv("DB_NAME", "account18_db"),
    )


# =========================
# HELPERS
# =========================
def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def generate_random_token():
    import secrets
    return secrets.token_hex(32)


def delete_file_if_exists(relative_path):
    if not relative_path:
        return
    cleaned = relative_path.lstrip("/\\")
    full_path = os.path.join(os.path.dirname(__file__), cleaned)
    if os.path.exists(full_path):
        os.remove(full_path)


def public_file_url(relative_path):
    if not relative_path:
        return None
    if relative_path.startswith("http"):
        return relative_path
    return f"{APP_BASE_URL}{relative_path}"


def now_iso(value):
    if isinstance(value, (datetime.datetime, datetime.date)):
        return value.isoformat()
    return value


def serialize_row(row):
    if not row:
        return row
    result = {}
    for key, value in row.items():
        if key in ("profile_image", "account_image"):
            result[key] = public_file_url(value)
        else:
            result[key] = now_iso(value)
    return result


def get_payload():
    if request.form:
        return request.form
    return request.get_json(silent=True) or {}


def save_uploaded_file(file_storage, target_dir, url_prefix):
    if not file_storage or file_storage.filename == "":
        return None

    filename = secure_filename(file_storage.filename)
    if not allowed_file(filename):
        raise ValueError("Only JPG, JPEG, PNG, and WEBP files are allowed.")

    ext = filename.rsplit(".", 1)[1].lower()
    unique_name = f"{datetime.datetime.now().strftime('%Y%m%d%H%M%S%f')}.{ext}"
    save_path = os.path.join(target_dir, unique_name)
    file_storage.save(save_path)

    return f"{url_prefix}/{unique_name}"


# =========================
# AUTH MIDDLEWARE
# =========================
def verify_token(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")

        if not auth_header.startswith("Bearer "):
            return jsonify({"message": "No token provided."}), 401

        token = auth_header.split(" ", 1)[1]

        if token in blacklisted_tokens:
            return jsonify({"message": "Token is already logged out."}), 401

        try:
            decoded = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])

            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute(
                """
                SELECT user_id, username, fullname, email, profile_image, token, is_verified
                FROM users
                WHERE user_id = %s AND token = %s
                LIMIT 1
                """,
                (decoded["user_id"], token),
            )
            user = cursor.fetchone()
            cursor.close()
            conn.close()

            if not user:
                return jsonify({"message": "Invalid token."}), 401

            if not user["is_verified"]:
                return jsonify({"message": "Account is not verified."}), 403

            g.current_user = user
            g.token = token
            return f(*args, **kwargs)

        except jwt.ExpiredSignatureError:
            return jsonify({"message": "Invalid or expired token."}), 401
        except jwt.InvalidTokenError:
            return jsonify({"message": "Invalid or expired token."}), 401
        except Exception as e:
            return jsonify({"message": "Authentication failed.", "error": str(e)}), 500

    return decorated


# =========================
# STATIC UPLOADS
# =========================
@app.route("/uploads/<path:filename>")
def uploaded_file(filename):
    return send_from_directory(UPLOADS_ROOT, filename)


# =========================
# DEFAULT
# =========================
@app.route("/", methods=["GET"])
def home():
    return jsonify({"message": "Activity 18 Flask API is running."})


# =========================
# REGISTER
# POST /api/register
# =========================
@app.route("/api/register", methods=["POST"])
def register():
    data = get_payload()

    username = data.get("username")
    fullname = data.get("fullname")
    email = data.get("email")
    password = data.get("password")

    if not username or not fullname or not email or not password:
        return jsonify({
            "message": "username, fullname, email, and password are required."
        }), 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute(
            "SELECT user_id FROM users WHERE username = %s OR email = %s",
            (username, email),
        )
        existing = cursor.fetchone()

        if existing:
            cursor.close()
            conn.close()
            return jsonify({
                "message": "Username or email already exists."
            }), 409

        hashed_password = generate_password_hash(password)
        verification_token = generate_random_token()

        cursor.execute(
            """
            INSERT INTO users
            (username, fullname, email, password, profile_image, token, is_verified, verification_token, reset_token, reset_token_expires)
            VALUES (%s, %s, %s, %s, NULL, '', 0, %s, NULL, NULL)
            """,
            (username, fullname, email, hashed_password, verification_token),
        )
        conn.commit()

        cursor.close()
        conn.close()

        email_sent = True
        email_error = None

        try:
            send_verification_email(email, fullname, verification_token)
        except Exception as mail_error:
            email_sent = False
            email_error = str(mail_error)

        if email_sent:
            return jsonify({
                "message": "Registration successful. Please check your email to verify your account."
            }), 201

        return jsonify({
            "message": "Registration successful, but verification email could not be sent.",
            "email_sent": False,
            "email_error": email_error
        }), 201

    except Exception as e:
        return jsonify({
            "message": "Failed to register user.",
            "error": str(e)
        }), 500


# =========================
# VERIFY EMAIL
# GET /api/verify-email?token=...
# =========================
@app.route("/api/verify-email", methods=["GET"])
def verify_email():
    token = request.args.get("token")

    if not token:
        return render_verification_error_page(), 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute(
            "SELECT user_id, is_verified FROM users WHERE verification_token = %s LIMIT 1",
            (token,),
        )
        row = cursor.fetchone()

        if not row:
            cursor.close()
            conn.close()
            return render_verification_error_page(), 400

        cursor.execute(
            "UPDATE users SET is_verified = 1, verification_token = NULL WHERE user_id = %s",
            (row["user_id"],),
        )
        conn.commit()

        cursor.close()
        conn.close()

        return render_verification_success_page(), 200

    except Exception:
        return render_verification_error_page(), 500


# =========================
# LOGIN
# POST /api/login
# =========================
@app.route("/api/login", methods=["POST"])
def login():
    data = get_payload()

    identifier = data.get("identifier") or data.get("username") or data.get("email")
    password = data.get("password")

    if not identifier or not password:
        return jsonify({"message": "username/email and password are required."}), 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute(
            "SELECT * FROM users WHERE username = %s OR email = %s LIMIT 1",
            (identifier, identifier),
        )
        user = cursor.fetchone()

        if not user:
            cursor.close()
            conn.close()
            return jsonify({"message": "Invalid login credentials."}), 401

        if not user["is_verified"]:
            cursor.close()
            conn.close()
            return jsonify({
                "message": "Your account is not verified. Please verify your email first."
            }), 403

        if not check_password_hash(user["password"], password):
            cursor.close()
            conn.close()
            return jsonify({"message": "Invalid login credentials."}), 401

        token = jwt.encode(
            {
                "user_id": user["user_id"],
                "username": user["username"],
                "email": user["email"],
                "exp": datetime.datetime.utcnow() + datetime.timedelta(days=1),
            },
            JWT_SECRET,
            algorithm="HS256",
        )

        cursor.execute(
            "UPDATE users SET token = %s WHERE user_id = %s",
            (token, user["user_id"]),
        )
        conn.commit()

        cursor.close()
        conn.close()

        return jsonify({
            "message": "Login successful.",
            "token": token,
            "user": {
                "user_id": user["user_id"],
                "username": user["username"],
                "fullname": user["fullname"],
                "email": user["email"],
                "profile_image": public_file_url(user["profile_image"]),
            },
        }), 200

    except Exception as e:
        return jsonify({"message": "Login failed.", "error": str(e)}), 500


# =========================
# LOGOUT
# POST /api/logout
# =========================
@app.route("/api/logout", methods=["POST"])
@verify_token
def logout():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
            "UPDATE users SET token = %s WHERE user_id = %s",
            ("", g.current_user["user_id"]),
        )
        conn.commit()

        cursor.close()
        conn.close()

        blacklisted_tokens.add(g.token)

        return jsonify({"message": "Logout successful."}), 200

    except Exception as e:
        return jsonify({"message": "Logout failed.", "error": str(e)}), 500


# =========================
# FORGOT PASSWORD
# POST /api/forgot-password
# =========================
@app.route("/api/forgot-password", methods=["POST"])
def forgot_password():
    data = get_payload()
    email = data.get("email")

    if not email:
        return jsonify({"message": "Email is required."}), 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute(
            "SELECT user_id, fullname, email FROM users WHERE email = %s LIMIT 1",
            (email,),
        )
        user = cursor.fetchone()

        if user:
            reset_token = generate_random_token()
            reset_expires = datetime.datetime.now() + datetime.timedelta(hours=1)

            cursor.execute(
                "UPDATE users SET reset_token = %s, reset_token_expires = %s WHERE user_id = %s",
                (reset_token, reset_expires, user["user_id"]),
            )
            conn.commit()

            send_reset_email(user["email"], user["fullname"], reset_token)

        cursor.close()
        conn.close()

        return jsonify({
            "message": "If the email exists, a password reset link has been sent."
        }), 200

    except Exception as e:
        return jsonify({"message": "Forgot password failed.", "error": str(e)}), 500


# =========================
# RESET PASSWORD
# POST /api/reset-password
# =========================
@app.route("/api/reset-password", methods=["POST"])
def reset_password():
    data = get_payload()
    token = data.get("token")
    new_password = data.get("newPassword")

    if not token or not new_password:
        return jsonify({"message": "token and newPassword are required."}), 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT user_id
            FROM users
            WHERE reset_token = %s AND reset_token_expires > NOW()
            LIMIT 1
            """,
            (token,),
        )
        row = cursor.fetchone()

        if not row:
            cursor.close()
            conn.close()
            return jsonify({"message": "Reset token is invalid or expired."}), 400

        hashed_password = generate_password_hash(new_password)

        cursor.execute(
            """
            UPDATE users
            SET password = %s, reset_token = NULL, reset_token_expires = NULL, token = %s
            WHERE user_id = %s
            """,
            (hashed_password, "", row["user_id"]),
        )
        conn.commit()

        cursor.close()
        conn.close()

        return jsonify({"message": "Password has been reset successfully."}), 200

    except Exception as e:
        return jsonify({"message": "Reset password failed.", "error": str(e)}), 500


# =========================
# GET PROFILE
# GET /api/profile
# =========================
@app.route("/api/profile", methods=["GET"])
@verify_token
def get_profile():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT user_id, username, fullname, email, profile_image, is_verified, created_at, updated_at
            FROM users
            WHERE user_id = %s
            LIMIT 1
            """,
            (g.current_user["user_id"],),
        )
        row = cursor.fetchone()

        cursor.close()
        conn.close()

        if not row:
            return jsonify({"message": "Profile not found."}), 404

        return jsonify(serialize_row(row)), 200

    except Exception as e:
        return jsonify({"message": "Failed to fetch profile.", "error": str(e)}), 500


# =========================
# UPDATE PROFILE
# PUT /api/profile
# form-data or JSON
# =========================
@app.route("/api/profile", methods=["PUT"])
@verify_token
def update_profile():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute(
            "SELECT * FROM users WHERE user_id = %s LIMIT 1",
            (g.current_user["user_id"],),
        )
        current_user = cursor.fetchone()

        if not current_user:
            cursor.close()
            conn.close()
            return jsonify({"message": "User not found."}), 404

        data = get_payload()
        username = data.get("username") or current_user["username"]
        fullname = data.get("fullname") or current_user["fullname"]
        email = data.get("email") or current_user["email"]

        cursor.execute(
            """
            SELECT user_id FROM users
            WHERE (username = %s OR email = %s) AND user_id <> %s
            """,
            (username, email, g.current_user["user_id"]),
        )
        duplicate = cursor.fetchone()

        if duplicate:
            cursor.close()
            conn.close()
            return jsonify({"message": "Username or email is already in use."}), 409

        hashed_password = current_user["password"]
        if data.get("password") and str(data.get("password")).strip() != "":
            hashed_password = generate_password_hash(data.get("password"))

        profile_image_path = current_user["profile_image"]
        uploaded_file = request.files.get("profile_image")

        if uploaded_file and uploaded_file.filename:
            if profile_image_path:
                delete_file_if_exists(profile_image_path)
            profile_image_path = save_uploaded_file(
                uploaded_file, PROFILE_DIR, "/uploads/profile"
            )

        cursor.execute(
            """
            UPDATE users
            SET username = %s, fullname = %s, email = %s, password = %s, profile_image = %s
            WHERE user_id = %s
            """,
            (
                username,
                fullname,
                email,
                hashed_password,
                profile_image_path,
                g.current_user["user_id"],
            ),
        )
        conn.commit()

        cursor.execute(
            """
            SELECT user_id, username, fullname, email, profile_image, is_verified, created_at, updated_at
            FROM users
            WHERE user_id = %s
            LIMIT 1
            """,
            (g.current_user["user_id"],),
        )
        updated_user = cursor.fetchone()

        cursor.close()
        conn.close()

        return jsonify({
            "message": "Profile updated successfully.",
            "user": serialize_row(updated_user),
        }), 200

    except ValueError as ve:
        return jsonify({"message": str(ve)}), 400
    except Exception as e:
        return jsonify({"message": "Failed to update profile.", "error": str(e)}), 500


# =========================
# CREATE ACCOUNT ITEM
# POST /api/account
# form-data or JSON
# =========================
@app.route("/api/account", methods=["POST"])
@verify_token
def create_account_item():
    try:
        data = get_payload()
        site = data.get("site")
        account_username = data.get("account_username") or data.get("username")
        account_password = data.get("account_password") or data.get("password")

        uploaded_file = request.files.get("account_image")
        account_image = None

        if not site or not account_username or not account_password:
            return jsonify({"message": "site, username, and password are required."}), 400

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT account_id
            FROM account_items
            WHERE user_id = %s AND site = %s AND account_username = %s
            LIMIT 1
            """,
            (g.current_user["user_id"], site, account_username),
        )
        duplicate = cursor.fetchone()

        if duplicate:
            cursor.close()
            conn.close()
            return jsonify({
                "message": "This account item already exists for this user."
            }), 409

        if uploaded_file and uploaded_file.filename:
            account_image = save_uploaded_file(
                uploaded_file, ACCOUNT_DIR, "/uploads/account"
            )

        cursor.execute(
            """
            INSERT INTO account_items
            (user_id, site, account_username, account_password, account_image)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (
                g.current_user["user_id"],
                site,
                account_username,
                account_password,
                account_image,
            ),
        )
        conn.commit()
        account_id = cursor.lastrowid

        cursor.close()
        conn.close()

        return jsonify({
            "message": "Account item created successfully.",
            "account_id": account_id,
        }), 201

    except ValueError as ve:
        return jsonify({"message": str(ve)}), 400
    except Exception as e:
        return jsonify({"message": "Failed to create account item.", "error": str(e)}), 500


# =========================
# GET ALL ACCOUNT ITEMS
# GET /api/account
# =========================
@app.route("/api/account", methods=["GET"])
@verify_token
def get_account_items():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT account_id, user_id, site, account_username, account_password, account_image, created_at, updated_at
            FROM account_items
            WHERE user_id = %s
            ORDER BY account_id DESC
            """,
            (g.current_user["user_id"],),
        )
        rows = cursor.fetchall()

        cursor.close()
        conn.close()

        return jsonify([serialize_row(row) for row in rows]), 200

    except Exception as e:
        return jsonify({"message": "Failed to fetch account items.", "error": str(e)}), 500


# =========================
# GET ONE ACCOUNT ITEM
# GET /api/account/<id>
# =========================
@app.route("/api/account/<int:account_id>", methods=["GET"])
@verify_token
def get_account_item(account_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT account_id, user_id, site, account_username, account_password, account_image, created_at, updated_at
            FROM account_items
            WHERE account_id = %s AND user_id = %s
            LIMIT 1
            """,
            (account_id, g.current_user["user_id"]),
        )
        row = cursor.fetchone()

        cursor.close()
        conn.close()

        if not row:
            return jsonify({"message": "Account item not found."}), 404

        return jsonify(serialize_row(row)), 200

    except Exception as e:
        return jsonify({"message": "Failed to fetch account item.", "error": str(e)}), 500


# =========================
# UPDATE ACCOUNT ITEM
# PUT /api/account/<id>
# form-data or JSON
# =========================
@app.route("/api/account/<int:account_id>", methods=["PUT"])
@verify_token
def update_account_item(account_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute(
            "SELECT * FROM account_items WHERE account_id = %s AND user_id = %s LIMIT 1",
            (account_id, g.current_user["user_id"]),
        )
        current_item = cursor.fetchone()

        if not current_item:
            cursor.close()
            conn.close()
            return jsonify({"message": "Account item not found."}), 404

        data = get_payload()
        site = data.get("site") or current_item["site"]
        account_username = data.get("account_username") or data.get("username") or current_item["account_username"]
        account_password = data.get("account_password") or data.get("password") or current_item["account_password"]

        account_image = current_item["account_image"]
        uploaded_file = request.files.get("account_image")

        if uploaded_file and uploaded_file.filename:
            if account_image:
                delete_file_if_exists(account_image)
            account_image = save_uploaded_file(
                uploaded_file, ACCOUNT_DIR, "/uploads/account"
            )

        cursor.execute(
            """
            UPDATE account_items
            SET site = %s, account_username = %s, account_password = %s, account_image = %s
            WHERE account_id = %s AND user_id = %s
            """,
            (
                site,
                account_username,
                account_password,
                account_image,
                account_id,
                g.current_user["user_id"],
            ),
        )
        conn.commit()

        cursor.close()
        conn.close()

        return jsonify({"message": "Account item updated successfully."}), 200

    except ValueError as ve:
        return jsonify({"message": str(ve)}), 400
    except Exception as e:
        return jsonify({"message": "Failed to update account item.", "error": str(e)}), 500


# =========================
# DELETE ACCOUNT ITEM
# DELETE /api/account/<id>
# =========================
@app.route("/api/account/<int:account_id>", methods=["DELETE"])
@verify_token
def delete_account_item(account_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute(
            "SELECT * FROM account_items WHERE account_id = %s AND user_id = %s LIMIT 1",
            (account_id, g.current_user["user_id"]),
        )
        row = cursor.fetchone()

        if not row:
            cursor.close()
            conn.close()
            return jsonify({"message": "Account item not found."}), 404

        if row["account_image"]:
            delete_file_if_exists(row["account_image"])

        cursor.execute(
            "DELETE FROM account_items WHERE account_id = %s AND user_id = %s",
            (account_id, g.current_user["user_id"]),
        )
        conn.commit()

        cursor.close()
        conn.close()

        return jsonify({"message": "Account item deleted successfully."}), 200

    except Exception as e:
        return jsonify({"message": "Failed to delete account item.", "error": str(e)}), 500





if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=PORT)