# TicketFlow

An AI powered ticket triage and routing system built for MSP (Managed Service Provider) operations.

## About

This project is my final capstone for my Computer Science degree at Lewis University (Spring 2026). I work at an MSP and this solves a real problem I deal with every day. Tickets come in from emails, alerts, and client portals and someone has to manually read each one, figure out the issue, and assign it to the right tech. When things get busy tickets end up with the wrong people or just sit in the queue too long. TicketFlow automates this entire process using a locally hosted LLM and an assignment engine that matches tickets to technicians based on skills, availability, and workload.

## Features

- AI ticket classification using Llama 3.1 through Ollama
- Automated ticket assignment based on tech skills, calendar availability, and current workload
- Technician management with skill tracking and availability status
- Known issues database with suggested fixes attached to matching tickets
- Role based dashboards for admins and technicians
- In app notification bell with unread badge and dropdown
- Admin reports with stats and category/technician breakdowns
- Ticket reassignment with reason field and history tracking
- Ticket intake through both a web form and a REST API endpoint
- Forgot password flow with token based reset

## Tech Stack

- Python
- Flask
- MySQL
- SQLAlchemy
- Ollama
- Llama 3.1
- HTML, CSS, JavaScript

## Prerequisites

- Python 3.10+
- MySQL 8+
- Ollama
- Git

## Installation

1. Clone the repo
```
git clone https://github.com/kevindzit/TicketFlow.git
cd TicketFlow
```

2. Create a virtual environment and activate it
```
python -m venv venv
source venv/bin/activate
# on Windows: venv\Scripts\activate
```

3. Install dependencies
```
pip install -r requirements.txt
```

4. Install Ollama from https://ollama.com and pull the model
```
ollama pull llama3.1
```

5. Create the MySQL database
```
mysql -u root -p
CREATE DATABASE ticketflow;
```

6. Copy the env file and update with your MySQL credentials
```
cp .env.example .env
# edit .env and set DATABASE_URL to match your local MySQL setup
```

7. Seed the database with sample data
```
python seed.py
```

8. Start the server
```
python run.py
```

The app will be running at http://127.0.0.1:5000

## Usage

Default login credentials for testing:

- Admin: `kevin@ticketflow.com` / `password123`
- Technician: `mike@ticketflow.com` / `password123`

All seeded users use the same password.

## Project Structure

```
TicketFlow/
├── app/
│   ├── __init__.py
│   ├── models/
│   │   ├── user.py
│   │   ├── ticket.py
│   │   ├── technician.py
│   │   ├── known_issue.py
│   │   ├── calendar_entry.py
│   │   ├── notification.py
│   │   └── assignment_log.py
│   ├── routes/
│   │   ├── auth.py
│   │   ├── dashboard.py
│   │   ├── tickets.py
│   │   ├── admin.py
│   │   ├── technicians.py
│   │   ├── known_issues.py
│   │   ├── notifications.py
│   │   └── reports.py
│   ├── services/
│   │   ├── ai_classifier.py
│   │   └── assignment_engine.py
│   ├── templates/
│   └── static/
│       └── css/
├── config.py
├── run.py
├── seed.py
├── requirements.txt
├── .env.example
├── TESTING.md
└── README.md
```

## Testing

See [TESTING.md](TESTING.md) for the full test plan and results.

## License

MIT
