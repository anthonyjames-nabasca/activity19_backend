

## Backend `README.md`

````md
# Activity 19 Flask Backend

Flask API with MySQL for account management system.

## Features

- User registration
- Email verification
- Login and logout using token authorization
- Forgot password and reset password
- User profile fetch and update with image
- Account item CRUD with image upload

## Tech Stack

- Flask
- MySQL
- python-dotenv
- PyJWT
- mysql-connector-python
- Werkzeug
- smtplib / Gmail SMTP

## Project Structure

```bash
backend/
├── app.py
├── mailer.py
├── .env
├── uploads/
│   ├── profile/
│   └── account/
└── README.md
````

## Database

Database name:

```text
account18_db
```

Main tables:

* `users`
* `account_items`

## Install Dependencies

Open terminal inside backend folder and run:

```bash
pip install flask flask-cors mysql-connector-python python-dotenv pyjwt werkzeug
```

## Environment File

Create a `.env` file in the backend root and paste the environment variables.

## Run the Backend

```bash
python app.py
```

Backend will run on:

```text
http://localhost:5100
```

## Main API Endpoints

### Auth

* `POST /api/register`
* `GET /api/verify-email?token=...`
* `POST /api/login`
* `POST /api/logout`

### Password

* `POST /api/forgot-password`
* `POST /api/reset-password`

### Profile

* `GET /api/profile`
* `PUT /api/profile`

### Account Items

* `POST /api/account`
* `GET /api/account`
* `GET /api/account/:id`
* `PUT /api/account/:id`
* `DELETE /api/account/:id`

## Notes

* Run XAMPP MySQL before starting backend.
* Uploaded images are stored inside:

  * `uploads/profile`
  * `uploads/account`
* Do not upload `.env` to GitHub.
* Add `.env` to `.gitignore`.

## Suggested `.gitignore`

```gitignore
__pycache__/
.env
uploads/
```

````

---

## Frontend `README.md`

```md
# Activity 19 Frontend

React + Vite frontend for the Flask account management system.

## Features

- Login
- Register
- Forgot password
- Reset password
- Protected routes
- Profile page
- Account items page
- Connects to Flask backend API

## Tech Stack

- React
- Vite
- Axios
- React Router DOM

## Project Structure

```bash
frontend/
├── public/
├── src/
│   ├── api/
│   ├── components/
│   ├── pages/
│   ├── App.jsx
│   ├── main.jsx
│   ├── App.css
│   └── index.css
├── .env
├── package.json
├── vite.config.js
└── README.md
````

## Install Dependencies

Open terminal inside frontend folder and run:

```bash
npm install
```

## Environment File

Create a `.env` file in the frontend root.

For local backend connection:

```env
VITE_API_BASE_URL=http://localhost:5100
```

## Run the Frontend

```bash
npm run dev
```

Frontend will run on:

```text
http://localhost:5173
```

## Build Frontend

```bash
npm run build
```

## GitHub Pages

This frontend can be published using GitHub Pages.

Important:

* The frontend may be published online
* The backend still runs locally on `http://localhost:5100`
* This setup is only suitable for school/demo use on the same machine running the backend

## Notes

* Make sure backend is running before using frontend
* API base URL must match the backend URL
* Use `HashRouter` for GitHub Pages routing

````

---

## Backend `.env`

```env
FLASK_APP=app.py
FLASK_ENV=development
PORT=5100

DB_HOST=localhost
DB_USER=root
DB_PASSWORD=
DB_NAME=account18_db

JWT_SECRET=my_super_secret_key_123
APP_BASE_URL=http://localhost:5100
CLIENT_URL=http://localhost:5173

MAIL_FROM=anthonyjames.nabasca@nmsc.edu.ph
SMTP_HOST=smtp.gmail.com
SMTP_PORT=465
SMTP_SECURE=true
SMTP_USER=anthonyjames.nabasca@nmsc.edu.ph
SMTP_PASS=httf tjuh rqzx ugak
````



