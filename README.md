# Modern Parking Management System

A professional Tkinter + SQLite parking management application.

## Features

- Secure staff login
- PBKDF2-SHA256 password hashing
- Failed-login lockout
- Admin and attendant roles
- Role-based access to administration features
- Vehicle registration and validation
- Automatic parking-slot assignment
- Live parking-slot map
- Check-in and checkout
- Automatic hourly billing
- Cash, M-Pesa and Card payment recording
- Receipt numbers
- Vehicle search
- Payment history
- Revenue reports
- Activity/audit log
- User management
- Configurable parking rates
- SQLite foreign keys and parameterized SQL
- Database backup
- Dark cinematic burnt-orange UI

## First login (demo)

Username: `admin`

Password: `Admin@123`

This credential is included only for the project/demo setup. For real deployment, change it immediately and restrict access to the database file.

## Run

```bash
python main.py
```

## Important files

- `main.py` - application entry point
- `database.py` - database and business data operations
- `security.py` - password hashing and login protection
- `validation.py` - input validation
- `ui.py` - Tkinter user interface
- `parking_system.db` - created automatically on first run
- `backups/` - database backups

## Security notes

This is a desktop educational/project system. The database is local SQLite, so operating-system access to the project folder should also be protected.

Passwords are not stored as plaintext. They are stored using salted PBKDF2-SHA256 hashes.

All user-controlled database values use parameterized SQL queries.

For a production deployment, add OS-level file permissions, encrypted backups, centralized authentication, HTTPS/API security if a network version is created, and a formal secrets-management system.

## Security and professional-system features

- Salted PBKDF2-SHA256 password hashing (no plaintext password storage)
- Temporary lockout after repeated failed login attempts
- Admin/attendant role separation
- Parameterized SQLite queries to reduce SQL-injection risk
- Input validation for names, phone numbers, usernames, passwords and registration numbers
- SQLite foreign-key enforcement
- Audit trail for login, logout, parking, checkout, user administration, settings and backups
- Confirmation before completing a checkout/payment
- Unique receipt numbers for completed transactions
- Automatic slot allocation and release
- Database backup from the administrator settings page
- Configurable hourly rates for car, bike, truck and bus
- Cinematic black/burnt-orange visual theme

## Submission/demo flow

1. Run `python main.py`.
2. Log in with the demo admin account above.
3. Park a vehicle and show the automatic slot assignment.
4. Open **Parked Vehicles** and **Search**.
5. Use **Checkout** to calculate the bill and record Cash, M-Pesa or Card payment.
6. Show the generated receipt and released slot.
7. Open **Payments**, **Reports** and **Activity Log**.
8. Open **Users** and **Settings** to demonstrate administrator-only controls.
9. Create a database backup from **Settings**.
