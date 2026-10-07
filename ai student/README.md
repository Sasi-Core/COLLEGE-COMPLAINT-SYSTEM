# Nandha Engineering College – College Complaint Management System

A complete, modern, beginner-friendly, and fully functional College Complaint Management Web Application built for **Nandha Engineering College (Autonomous)**, designed for College Project-Based Learning (PBL).

---

## 🏛️ Project Overview

The **Nandha Engineering College Complaint System** provides a centralized, transparent digital platform where students can submit grievances (academic, infrastructure, hostel, transport, canteen, internet, etc.) and track their resolution status in real-time. Administrators can review, assign, update progress status, attach official remarks/responses, and manage grievances.

---

## 🛠️ Technology Stack

- **Frontend**:
  - HTML5 (Semantic Structure)
  - CSS3 (Vanilla CSS with CSS Variables, Responsive Grid & Flexbox, Nandha College Theme)
  - JavaScript (Vanilla JS for interactive tabs, auto-fill, real-time clock, modals)
  - FontAwesome 6 (Clean icons)
  - Google Fonts (`Outfit` & `Inter`)
- **Backend**:
  - Python 3.11+
  - Flask (Lightweight Python Web Framework)
  - Jinja2 (Dynamic Server-Side Templating)
  - Werkzeug (Secure Password Hashing with PBKDF2/SHA256 & Secure File Uploads)
- **Database**:
  - SQLite (`database.db`) with Foreign Key integrity and indexing

---

## 📂 Project Structure

```
college_complaint_system/
│
├── app.py                      # Flask backend, routing, database logic, & authentication
├── database.db                 # SQLite database (auto-generated on startup)
├── requirements.txt            # Python dependencies
├── run.bat                     # Windows 1-click launcher script
├── README.md                   # Complete documentation & PBL manual
│
├── templates/                  # Jinja2 HTML Templates
│   ├── base.html               # Master layout (College branding, navbar, flash alerts, footer)
│   ├── login.html              # Student & Admin login portal with 1-click demo fillers
│   ├── student_dashboard.html  # Student home, grievance statistics, recent filings
│   ├── submit_complaint.html   # Complaint filing form with attachments & priorities
│   ├── my_complaints.html      # Complaints table with status filter chips
│   ├── complaint_details.html  # Detailed complaint view, progress stepper, admin response
│   └── admin_dashboard.html    # Administrative console with filters, search, & controls
│
└── static/
    ├── css/
    │   └── style.css           # Nandha College custom responsive stylesheet
    ├── js/
    │   └── script.js           # Client-side validation, tabs, & helpers
    └── uploads/                # Directory for student complaint file attachments
```

---

## 🔑 Demo Login Credentials

The database is pre-seeded on first run with the required test accounts:

### 🎓 1. Student Account
- **Student ID**: `STU001`
- **Password**: `student123`
- **Name**: Kavitha R
- **Department**: Computer Science & Engineering

### 🛡️ 2. Admin Account
- **Admin Username**: `admin`
- **Password**: `admin123`
- **Name**: Campus Admin Officer
- **Department**: Administrative Office

*(Quick 1-click auto-fill buttons are also available directly on the login page for effortless grading and demonstration.)*

---

## 🚀 How to Install and Run

### Step 1: Install Requirements
Open PowerShell or Command Prompt in the project folder and run:
```bash
pip install -r requirements.txt
```

### Step 2: Start the Application
Run:
```bash
python app.py
```
*(Or simply double-click `run.bat` on Windows!)*

### Step 3: Open in Browser
Open your favorite web browser and visit:
```
http://127.0.0.1:5000
```

---

## 🌟 Key Features

1. **Role-Based Authentication**:
   - Distinct portals for Students and Administrators.
   - Protected routes (`@login_required`, `@student_required`, `@admin_required`).
   - Secure password hashing using Werkzeug.

2. **Student Module**:
   - Summary statistics (Total, Pending, In Progress, Resolved).
   - Lodge new complaint with:
     - Title, Category, Department, Priority (Low, Medium, High, Urgent), and Description.
     - Optional attachment upload (Images, PDFs, Docs).
   - Generates unique tracking ID format (e.g., `NEC-2026-XXXX`).
   - Real-time status filtering (Pending, In Progress, Resolved, Rejected).
   - Visual progress stepper (Submitted ➔ Under Investigation ➔ Resolved/Decision).
   - View official administration resolution remarks.

3. **Administrator Module**:
   - Executive dashboard with counts for Total, Pending, In Progress, Resolved, and Rejected grievances.
   - Live search by Complaint ID, Title, Student Name, or Student ID.
   - Multi-parameter filtering by Status, Category, Priority, and Department.
   - Update complaint status and provide official resolution notes.
   - Permanently delete records with confirmation prompts.

4. **UI & Aesthetics**:
   - Designed with Nandha Engineering College navy and gold identity.
   - Fully responsive across desktop, laptop, tablet, and mobile browsers.
   - No unnecessary animations; clean, accessible, and fast.
