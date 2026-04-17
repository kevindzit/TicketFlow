# TicketFlow Testing Documentation

This document covers the testing performed on the TicketFlow application. Each test case includes the steps taken, expected outcome, and actual result.

---

## Authentication

### LOGIN-T1: Valid Admin Login
- **Steps:** Navigate to /login, enter kevin@ticketflow.com / password123, click Login
- **Expected:** Redirect to admin dashboard with stats and all tickets
- **Actual:** PASS

### LOGIN-T2: Valid Technician Login
- **Steps:** Navigate to /login, enter mike@ticketflow.com / password123, click Login
- **Expected:** Redirect to technician dashboard showing only assigned tickets
- **Actual:** PASS

### LOGIN-T3: Invalid Credentials
- **Steps:** Navigate to /login, enter kevin@ticketflow.com with wrong password, click Login
- **Expected:** Stay on login page with "Invalid email or password" error
- **Actual:** PASS

### LOGIN-T4: Role Based Access
- **Steps:** Log in as technician (mike@ticketflow.com), navigate to /technicians
- **Expected:** Access denied message and redirect to dashboard
- **Actual:** PASS

---

## Ticket Intake

### INTAKE-T1: Create Ticket Through Web Form
- **Steps:** Log in as admin, click New Ticket, select client, enter subject and description, submit
- **Expected:** Ticket created with AI classification applied, flash message confirms
- **Actual:** PASS

### INTAKE-T2: Missing Required Fields
- **Steps:** Go to New Ticket form, leave subject blank, submit
- **Expected:** Validation error "Subject and description are required"
- **Actual:** PASS

### INTAKE-T3: API Endpoint
- **Steps:** POST JSON to /api/tickets with subject, description, and client_id
- **Expected:** 201 response with ticket_id and AI classification data
- **Actual:** PASS

---

## AI Classification

### CLASS-T1: AI Classification Accuracy
- **Steps:** Create ticket with subject "Printer not printing" and description about offline printer
- **Expected:** AI classifies as Hardware category with reasonable urgency
- **Actual:** PASS

### CLASS-T2: Classification Fallback
- **Steps:** Stop Ollama service, create a new ticket
- **Expected:** Ticket created with defaults (category=Other, urgency=Medium, summary says needs manual review)
- **Actual:** PASS (tested when Ollama was off)

---

## Technician Management

### TECHPRO-T1: Add Technician
- **Steps:** Go to Technicians page, click Add Technician, fill in name/email/skills, save
- **Expected:** New technician appears in the list with selected skills
- **Actual:** PASS

### TECHPRO-T2: Edit Technician
- **Steps:** Click Edit on an existing technician, change skills, save
- **Expected:** Updated skills saved and reflected in the list
- **Actual:** PASS

### TECHPRO-T3: Delete Technician
- **Steps:** Click Delete on a technician who has open tickets, confirm
- **Expected:** Technician removed, their tickets become unassigned
- **Actual:** PASS

---

## Ticket Assignment

### ASSIGN-T1: Automatic Assignment
- **Steps:** Create a new ticket with a category that matches a technician's skills
- **Expected:** Ticket automatically assigned to the least loaded matching technician
- **Actual:** PASS

### ASSIGN-T2: No Available Tech
- **Steps:** Create a ticket with a category no technician has in their skills
- **Expected:** Ticket status set to Pending, no technician assigned
- **Actual:** PASS

---

## Dashboard

### DASH-T1: Technician Dashboard
- **Steps:** Log in as technician, view dashboard
- **Expected:** Only tickets assigned to this technician are shown
- **Actual:** PASS

### DASH-T2: Admin Filters
- **Steps:** Log in as admin, use filter dropdowns for status, category, urgency, technician, client
- **Expected:** Table updates to show only matching tickets
- **Actual:** PASS

### DASH-T3: Status Updates and Notes
- **Steps:** Open a ticket detail, change status via dropdown, add a note
- **Expected:** Status saves, note appears in timeline with author and timestamp
- **Actual:** PASS

---

## Notifications

### NOTIFY-T1: Notification on Assignment
- **Steps:** Create a new ticket that gets auto-assigned
- **Expected:** Assigned technician sees bell badge increment, notification in dropdown
- **Actual:** PASS

### NOTIFY-T2: Notification on Reassignment
- **Steps:** Admin reassigns a ticket to a different technician
- **Expected:** New technician receives notification, reassignment note added to ticket
- **Actual:** PASS

---

## Reports

### REPORT-T1: Admin Reports Page
- **Steps:** Log in as admin, navigate to Reports
- **Expected:** Summary cards show correct counts, category and technician breakdowns display
- **Actual:** PASS

---

## Known Issues

### KNOWN-T1: Add Known Issue
- **Steps:** Go to Known Issues, click Add, fill in title/description/category/fix, save
- **Expected:** New known issue appears in the list
- **Actual:** PASS

### KNOWN-T2: Known Issue Matched
- **Steps:** Create a ticket whose category matches an active known issue
- **Expected:** Known issue and suggested fix shown on the ticket detail page
- **Actual:** PASS

---

## Summary

All 22 test cases passed as of 4/16/2026. The application is functioning as designed across all implemented features.
