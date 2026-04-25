# BuyMe — Online Auction Platform

**CS 527 Database Systems — Final Project**

## Team Members

| Name | NetID |
|------|-------|
| Rishabh Sanjeev Shah | RS2780 |
| Hitanshu Oza | HRO24 |
| Om Nirav Patel | OP187 |
| Vivek Sai Manthri | VM614 |

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python 3, Flask, SQLAlchemy ORM |
| Database | SQLite (dev) → MySQL 8.0 via Docker (prod) |
| Frontend | Jinja2 templates, vanilla CSS/JS |
| Auth | Flask-Login + Flask-Bcrypt |
| Extras | Flatpickr (date picker) |

---

## Quick Start (SQLite — no Docker needed)

```bash
# 1. Clone & enter the project
git clone git@github.com:RishiiShah/DBDS_Project.git
cd DBDS_Project

# 2. Create & activate virtual environment
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Seed the database (creates all accounts, categories, and sample auctions)
python seed.py

# 5. Run the app
python app.py
```

Open **http://127.0.0.1:5001** in your browser.

> **Re-seeding:** If you need a clean slate, delete `instance/buyme.db` (or `buyme.db`) then re-run `python seed.py`. The seeder is safe to re-run — each block is guarded and skips data that already exists.

---

## Default Accounts

| Username | Password | Role |
|----------|----------|------|
| admin | admin123 | Admin |
| johndoe | password | User |
| janesmith | password | User |
| alice | password | User |
| bob | password | User |

> Customer Rep accounts are created by the admin at `/admin/create-rep`.

---

## Features

### Regular Users
- Register, log in, manage profile (edit info, delete account)
- Browse active auctions by category across multiple item families, with electronics seeded most heavily
- Filter auctions by keyword, category, price range, condition, sort order, and category-specific item fields
- Place manual bids with real-time minimum enforcement
- Auto-bid (proxy bidding): set an upper limit — system bids automatically to keep you in the lead; current limit and status shown on the auction page; cancel or update anytime; parallel auto-bid competition resolves instantly when two auto-bids meet
- Create auction listings with category-specific attributes, Flatpickr date picker, and price tooltips
- View similar auctions on each auction detail page (scored by category, price, and attributes)
- Wishlist / keyword watches: get alerted when a matching auction is listed
- Wishlist / keyword watches can also include category-specific attribute filters
- Alert inbox: outbid, auction won/lost, auto-bid exceeded, item available, auction cancelled, bid removed
- Support Q&A: submit questions to customer reps, view rep replies, search answered questions

### Customer Reps
- Manage end-users: edit profile info, reset passwords, deactivate/reactivate accounts
- Manage auctions: cancel any active auction (alerts seller + winner), remove individual bids (price recalculates automatically)
- Answer support questions: reply to open questions, close resolved threads

### Admin
- Create customer rep accounts
- View sales reports: total revenue, 5% platform commission, top items, earnings by category, best sellers, best buyers
- All rep capabilities (admin is a superset of rep)

---

## Category Hierarchy

```
Electronics
├── Computers
│   ├── Laptops           (brand, ram, storage, screen_size)
│   └── Desktops          (brand, ram, storage, gpu)
├── Gaming
│   ├── Consoles          (brand, storage, generation)
│   └── Gaming Accessories(brand, compatibility)
├── Mobile Phones
│   ├── Smartphones       (brand, os, storage, screen_size)
│   └── Feature Phones    (brand, network)
├── Wearables
│   ├── Smartwatches      (brand, compatibility, battery_life)
│   └── Fitness Trackers  (brand, waterproof, battery_life)
└── Home Electronics
    ├── Headphones        (brand, type, connectivity)
    ├── Speakers          (brand, connectivity, watts)
    └── Smart Home        (brand, protocol)

Sporting Goods
├── Cycling
│   ├── Bikes             (frame_size, material, gears)
│   └── Cycling Accessories(brand, compatibility)
├── Fitness
│   ├── Cardio Equipment  (brand, resistance_levels, max_weight)
│   └── Strength Equipment(brand, weight_range, adjustable)
├── Outdoor & Adventure
│   ├── Camping Gear      (brand, capacity, season_rating)
│   └── Hiking Gear       (brand, size, waterproof)
└── Team Sports
    ├── Football          (brand, size, material)
    ├── Basketball        (brand, size, indoor_outdoor)
    └── Baseball          (brand, glove_size, position)
```

Each leaf category stores its required fields as JSON — **adding a new category never requires code changes** (bonus feature).

## ER Diagram

- See [docs/ER_DIAGRAM.md](docs/ER_DIAGRAM.md) for the current project ER diagram.

---

## Project Structure

```
├── app.py                  # Flask app factory + blueprint registration
├── config.py               # Dev/prod configuration
├── seed.py                 # Database seeder (safe to re-run)
├── docker-compose.yml      # MySQL container for production
├── requirements.txt
│
├── models/
│   ├── user.py             # User (role: user / rep / admin)
│   ├── item.py             # Item, Category, ItemAttribute
│   ├── auction.py          # Auction, Bid, AutoBid, Transaction
│   ├── alert.py            # Alert (outbid, won, lost, cancelled, etc.)
│   └── support.py          # SupportQuestion
│
├── routes/
│   ├── auth.py             # /register, /login, /logout
│   ├── main.py             # /, /dashboard
│   ├── auction.py          # /auctions, /auction/<id>, /bid, /autobid
│   ├── search.py           # /search, /browse
│   ├── user.py             # /profile, /alerts, /wishlist, /my-auctions
│   ├── admin.py            # /admin/* (admin only)
│   ├── rep.py              # /rep/* (rep + admin)
│   └── support.py          # /support/*
│
├── templates/
│   ├── base.html           # Shared layout + nav
│   ├── dashboard.html      # User dashboard
│   ├── auction/            # list, detail, create
│   ├── auth/               # login, register
│   ├── user/               # profile, alerts, wishlist, my_auctions
│   ├── search/             # browse, results
│   ├── admin/              # dashboard, create_rep, reports
│   ├── rep/                # dashboard, manage_user, manage_auctions, questions
│   ├── support/            # ask, my_questions, search
│   └── components/         # reusable partials
│
├── static/
│   ├── css/                # Stylesheets
│   └── js/                 # Auction countdown, bid history polling, search
│
└── utils/
    ├── bidding.py          # process_new_bid, trigger_autobid_on_register, close_expired_auctions
    ├── similarity.py       # find_similar (category + price + attribute scoring)
    ├── watches.py          # check_wishlist (fires item_available alerts)
    └── decorators.py       # role_required
```
