# TicketFlow

An AI powered ticket triage and routing system built for MSP (Managed Service Provider) operations.

## About

This project is my final capstone for my Computer Science degree at Lewis University (Spring 2026). I work at an MSP and this solves a real problem I deal with every day. Tickets come in from emails, alerts, and client portals and someone has to manually read each one, figure out the issue, and assign it to the right tech. When things get busy tickets end up with the wrong people or just sit in the queue too long. TicketFlow automates this entire process using AI.

## What It Does

The system reads incoming support tickets and uses a locally hosted LLM to classify them by category and urgency. It then checks for known outages or common fixes using a combination of a known issues database and real time web search. After that it automatically assigns the ticket to the best available technician based on their skills, availability, and current workload. Technicians and admins interact with everything through a web dashboard.

## Features

- User login and authentication with role based access (admin and technician)
- Ticket intake through a web form and REST API endpoint
- AI powered ticket classification using Llama 3.1 through Ollama
- Technician profile management with skill tracking
- Technician availability tracking with calendar integration
- Known issue and outage detection with real time web search
- Automated ticket assignment based on skills, availability, and workload
- Ticket dashboard with color coded urgency and detail views
- Admin assignment override
- In app notifications for ticket assignments
- Basic reporting and statistics

## Tech Stack

- Python
- Flask
- MySQL with SQLAlchemy
- Ollama with Llama 3.1 (local LLM)
- HTML, CSS, JavaScript
- Git

## Status

Currently in the planning and design phase. Development is underway for the Spring 2026 semester.
