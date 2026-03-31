# Personal Finance Tracking Management System (PFTMS)

## Requirements
- Python 3.8+ (pre-installed on Ubuntu 22.04)
- Tkinter (pre-installed with Python on Ubuntu)

## Installation on Ubuntu
```bash
# Tkinter is usually pre-installed. If not:
sudo apt update
sudo apt install python3-tk

# No other dependencies needed!
```

## Installation on Windows
- Install Python 3.8+ from python.org (make sure to check "Add to PATH" and "tcl/tk" during install)
- Tkinter comes bundled with Python on Windows

## How to Run
```bash
cd PFTMS
python main.py
```

## Default Login Credentials
- **Admin:** username: `admin` | password: `admin123`
- **User:** username: `user1` | password: `user123`

## File Structure
```
PFTMS/
├── main.py              # Main application
├── README.md            # This file
├── data/
│   ├── users.csv        # User accounts (pipe-delimited)
│   ├── income.csv       # Income records
│   ├── expenses.csv     # Expense records
│   └── logs.csv         # Activity logs
└── backups/             # Auto-generated backups
```

## Features
- Login & Registration system with role-based access (admin/user)
- Add Income with categories (Salary, Business, Freelance, etc.)
- Add Expenses with categories (Food, Transport, Utilities, etc.)
- Dashboard with real-time balance calculation
- View & filter all records
- Backup to local folder or USB drive
- Admin: Manage users
- Admin: View activity logs
