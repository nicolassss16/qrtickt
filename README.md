# Ticketing System

A web-based ticketing system for managing events and ticket sales. This application enables users to purchase tickets and provides admins with tools to manage events effectively.

## Features
- **User Features:**
  - View upcoming events.
  - Purchase tickets with QR codes.
- **Admin Features:**
  - Add, update, and delete events.
  - Manage attendees.
- **QR Code Validation:**
  - Validate tickets using QR code scanning.

## Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/imonisweet1/ticket_system.git
   cd ticket_system
   ```
2. Create a Virtual Environment
   ```bash
    cd backend
    python -m venv venv
    source venv/bin/activate  # On Windows:       venv\\Scripts\\activate
   ```
3. Install Dependencies
    ```bash
    pip install -r requirements.txt
    ```
4. Configure the flask<br>Edit the ```ticket_system/config.py``` file to configure your database. By default, it uses SQLite:
    ```
    SQLALCHEMY_DATABASE_URI = 'sqlite:///tickets.db'
    
    Run Database Migrations

    flask db init
    flask db migrate
    flask db upgrade
    ```
## Usage
- Visit http://127.0.0.1:5000 to browse events and purchase tickets.

- Admins can log in via ```/admin``` to manage events.
## Technologies Used
- Backend: Flask

- Database: SQLite

- Frontend: HTML, CSS

- Libraries: Flask-Login, Flask-Bcrypt, QR Code library
## Project Structure
```bash
ticket_system/
├── app/
│   ├── __init__.py
│   ├── models.py
│   ├── routes.py
│   └── templates/
│       ├── index.html
│       ├── admin.html
│       └── ticket.html
├── config.py
└── run.py
```

