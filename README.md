# AI Ticket Dispatcher

An AI powered ticket triage and routing system built for MSP (Managed Service Provider) operations.

## About

This project is my final capstone for my Computer Science degree at Lewis University (Spring 2026). I work at an MSP and this solves a real problem I deal with every day: tickets coming in from all directions and someone having to manually figure out who should handle each one.

## What It Does

- Reads incoming support tickets and classifies the issue type and urgency
- Matches tickets to the best available technician based on skills, schedule, and current workload
- Checks for known outages or global issues before assigning
- Sends Teams notifications when a ticket is assigned
- Provides a dashboard to view the queue and technician workloads

## Tech Stack

- Python
- Flask or FastAPI
- Microsoft Graph API (Teams, Outlook calendar)
- LLM integration for ticket classification
- SQL database
- Basic frontend dashboard

## Status

Currently in the planning phase. Code and documentation will be added throughout the Spring 2026 semester.
