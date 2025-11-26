# 📌 Task Analyzer — Internship Assignment

A complete task-prioritization system consisting of:

- A **scoring engine** (`scoring.py`)
- **Unit tests** (`test_scoring.py`)
- **Django backend API** (`tasks/views.py`, `tasks/urls.py`)
- A **fully functional frontend UI** (`task-analyzer-frontend.html`)

This project analyzes tasks using urgency, importance, effort, and dependency unlocking.  
It supports multiple scoring strategies like **Smart Balance**, **Fastest Wins**, **High Impact**, and **Deadline Driven**.

---

# 🚀 Features

### ✔ **Advanced Priority Scoring**
- Urgency based on due date  
- Importance weight (1–10)  
- Effort reduction (small tasks get higher score)  
- Dependency unlocking score  
- Overdue tasks get urgency boost  
- Cycle detection for dependency loops  

### ✔ **Multiple Strategies Supported**
- **Smart Balance** (default)
- **Fastest Wins** (low effort first)
- **High Impact** (importance first)
- **Deadline Driven** (due date priority)

### ✔ **Frontend Application**
- Add individual tasks through a form  
- Bulk paste JSON input  
- Choose strategy  
- View results with:
  - Color-coded priority indicators  
  - Explanation for each score  
  - Task metadata (due date, importance, effort)  

### ✔ **Backend API (Django)**
- `POST /api/tasks/analyze/` → returns sorted tasks with scores  
- `GET /api/tasks/suggest/` → returns top 3 recommended tasks  

---

# 📁 Folder Structure (Recommended)

