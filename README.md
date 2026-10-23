# 📚 Neo-Bibliotheca — Library Management System

A web-based **Library Management System** built with **Python 3**, **Flask**, **SQLite**, and **SQLAlchemy**, following a strict **Model-View-Controller (MVC)** architecture. Features an engaging modern UI ("Neo-Lumina" aesthetic) with electric indigo & aurora accents, glassmorphic floating navigation, interactive Chart.js visualizations, and responsive Dark/Light mode.

---

## ✨ System Highlights & Core Modules

### 📖 1. Book Management
- Full CRUD: Add, edit, delete, and view catalog entries with ISBN validation.
- Inventory tracking with dynamic stock calculation: Total Copies vs. Available Copies.
- Multiple view modes: **Modern 3D Grid View** (with stylized book covers and spine accents) and **Tabular Data View**.
- Multi-parameter filtering: Search keyword, category/genre, availability status, and sorting (Title A-Z, Title Z-A, Author, Popularity, Newest).
- Direct "Loan" action straight from any book card.

### 👥 2. Patron & Member Management
- Member directory with registration, editing, profile views, and account suspension toggles.
- **Tiered Membership Architecture**:
  - **Standard Tier**: Up to 5 books concurrently, 14-day default loan period.
  - **Premium Tier**: Up to 10 books concurrently, 30-day default loan period.
- Real-time **Borrowing Capacity Meter** / progress bar indicating active loans vs. ceiling allowance.
- Instant overview of outstanding fines and historical borrow logs per member.

### 🔄 3. Circulation & Loan Operations
- Streamlined checkout flow with interactive dynamic preview of book stock and member borrowing capacity.
- Due date tracking with automatic countdown: "X days remaining", "Due today", "X days late".
- One-click loan extensions (+7 or +14 days) protected against overdue loans.

### 💰 4. Fines & Penalty Management
- Dedicated **Fines & Fee Management Center** (`/fines`).
- Real-time overdue penalty calculation ($1.00/day configurable).
- One-click fine settlement ("Mark as Paid") and administrative fee waivers ("Waive Fine").
- Option to collect and settle fines immediately upon book return or register as debt on the member profile.

### 📊 5. Visual Analytics & Statistics Hub
- Dedicated **Analytics Hub** (`/analytics`) powered by **Chart.js**:
  - Monthly borrowing activity trends (Area/Line chart).
  - Catalog category distribution (Doughnut chart).
  - Circulation status ratio (Active, Overdue, Returned).
  - Patron membership tier breakdown (Standard vs. Premium).
  - Top 5 Most Borrowed Titles & Top 5 Most Active Patrons.
- JSON REST API endpoints (`/api/stats`, `/api/books`, `/api/members`, `/api/borrows`).

---

## 🎨 Visual Identity: "Neo-Lumina" Modern Aesthetic

- **Color Palette**: Deep slate obsidian (`#0b0f19` / `#0f172a`), Dark Indigo Navy (`#1e1b4b`), Electric Indigo (`#6366f1`), Royal Violet (`#8b5cf6`), Neo Mint / Emerald (`#10b981`), Amber Honey (`#f59e0b`), and Coral Rose (`#f43f5e`).
- **Typography**: Google Fonts pairing — *Outfit* (display titles and metric values) + *Plus Jakarta Sans* (refined UI elements and body text).
- **Glassmorphism**: Translucent floating topbar with frosted background blur (`backdrop-filter: blur(16px)`).
- **Dark Mode**: Persistent dark mode toggle stored in `localStorage` with zero-flash rendering.
- **Pills & Badges**: Soft micro-glow badges with pulsing live status indicators.

---

## 🏗️ MVC Architecture

```
LIBRARY_APP/
├── app/
│   ├── __init__.py           # Application Factory, Jinja filters, context processors
│   ├── models.py             # SQLAlchemy Models: Book, Member, Borrow (Model)
│   ├── routes.py             # Blueprint routes, validation, controllers (Controller)
│   │
│   ├── static/
│   │   ├── css/
│   │   │   └── style.css     # Modern custom stylesheet with Dark Mode
│   │   └── js/
│   │       └── main.js       # Theme toggle, checkout previews, interactive UI
│   │
│   └── templates/            # Jinja2 Templates (View)
│       ├── base.html         # Base template with responsive modern navbar & footer
│       ├── index.html        # Dashboard with KPI cards and loan alerts
│       ├── search.html       # Global multi-entity search
│       ├── analytics/
│       │   └── index.html    # Chart.js analytics hub
│       ├── fines/
│       │   └── list.html     # Dedicated fines management dashboard
│       ├── books/
│       │   ├── list.html     # Grid & table catalog with filters
│       │   ├── detail.html   # Book details, borrower list, loan history
│       │   ├── add.html      # Add book form
│       │   └── edit.html     # Edit book form
│       ├── members/
│       │   ├── list.html     # Member directory
│       │   ├── detail.html   # Member profile & capacity gauge
│       │   ├── add.html      # Register member form
│       │   └── edit.html     # Edit member profile
│       ├── borrows/
│       │   ├── list.html     # Circulation list & loan actions
│       │   ├── checkout.html # Interactive loan checkout
│       │   └── return.html   # Return confirmation & fee settlement
│       └── errors/
│           ├── 403.html
│           ├── 404.html
│           └── 500.html
│
├── config.py                 # Development, Testing, Production configurations
├── database.db               # SQLite database
├── requirements.txt          # Dependencies
├── run.py                    # Entry point & CLI seed commands
└── README.md
```

---

## 🚀 Getting Started

### 1. Requirements
- Python 3.9+
- Flask 3.0+
- Flask-SQLAlchemy

### 2. Installation
```bash
# Clone or open the repository
cd library_app

# Install dependencies
pip install -r requirements.txt
```

### 3. Initialize & Seed Database
```bash
# Populate with curated books, members, active loans, and overdue records:
python -m flask --app run.py seed-db
```

### 4. Run Development Server
```bash
python run.py
```
Open your browser and navigate to **`http://localhost:5000`**.

---

## ⚡ CLI Utilities
- `python -m flask --app run.py init-db`: Create database tables.
- `python -m flask --app run.py seed-db`: Seed catalog with 12 books, 6 members, and realistic loans.
- `python -m flask --app run.py reset-db`: Drop, re-create, and seed database.