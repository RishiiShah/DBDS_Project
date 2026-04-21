# BuyMe - Online Electronics Auction Platform

**CS 527 Database Systems - Final Project**

## Team Members
<!-- Update this section with your final member names and NetIDs -->
- Rishabh Sanjeev Shah (RS2780)
- Hitanshu Oza (HRO24)
- Om Nirav Patel (OP187)
- Vivek Sai Manthri (VM614)

## Tech Stack
- **Backend:** Python 3, Flask, SQLAlchemy ORM
- **Database:** MySQL 8.0 (via Docker)
- **Frontend:** Jinja2 templates, vanilla CSS/JS
- **Auth:** Flask-Login + bcrypt

## Quick Start

```bash
# 1. Clone & enter the project
git clone git@github.com:RishiiShah/DBDS_Project.git && cd Finalproject

# 2. Create & activate virtual environment
python3 -m venv venv
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Start MySQL via Docker
docker compose up -d

# 5. Copy env file (defaults work with docker-compose)
cp .env.example .env

# 6. Seed the database (creates admin + categories)
python seed.py

# 7. Run the app
flask run --debug
```

Open **http://127.0.0.1:5000** in your browser.

## Default Accounts
| Username | Password | Role |
|----------|----------|------|
| admin | admin123 | Admin |
| johndoe | password | User |
| janesmith | password | User |

## Project Structure
```
├── app.py              # Flask app factory
├── config.py           # Configuration
├── seed.py             # Database seeder
├── docker-compose.yml  # MySQL container
├── models/             # SQLAlchemy models (all tables)
├── routes/             # Flask blueprints
├── templates/          # Jinja2 HTML templates
├── static/             # CSS, JS, images
└── utils/              # Decorators, helpers
```

## Category Hierarchy (Electronics)
```
Electronics
├── Computers → Laptops, Desktops, Components
├── Phones → Smartphones, Feature Phones
├── Audio → Headphones, Speakers, Turntables
└── Gaming → Consoles, Accessories
```
Each leaf category has required fields (stored as JSON in DB) - **no code changes needed to add new categories** (bonus feature).
