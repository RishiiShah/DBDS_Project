# BuyMe — Combined Implementation Plan

**Team**: Rishabh (rs2780) · Vivek · Om · Hitanshu
**Branch**: All work on `main` (sequential)
**Order**: Rishabh → Vivek → Om → Hitanshu → Rishabh (integration)

See individual plans in `docs/PLAN_<NAME>.md` for full details.

---

## Work Order & Dependencies

```
1. Rishabh (DONE) ──→ 2. Vivek ──→ 3. Om ──→ 4. Hitanshu ──→ 5. Rishabh (integration)
   Scaffold              Auctions     Search     Admin/Rep      Polish & deliverables
   Models                Bidding      Browse     Reports        Nav wiring
   Auth                  AutoBid      WishList   Support Q&A    Demo data
   Base UI               Closing      Alerts     User mgmt      ER diagram
                                      Profile    Bid removal     MySQL cutover
```

---

## Member Summary

### 1. Rishabh — Phase 1: Scaffold + Auth (✅ DONE)

| Done | Deliverable |
|------|------------|
| ✅ | Virtual env, requirements, Docker Compose, config |
| ✅ | All 13 database models matching ER diagram |
| ✅ | Auth: Register, Login, Logout |
| ✅ | Base template, dark theme CSS, JS |
| ✅ | Seed script: admin + users + category hierarchy |
| ✅ | Role decorators: `@role_required` |

---

### 2. Vivek — Auctions & Bidding (6 files)

| File | Purpose |
|------|---------|
| `routes/auction.py` | CRUD + bid + auto-bid routes |
| `utils/bidding.py` | Auto-bid engine, auction closing, bid recalc |
| `templates/auction/create.html` | Form with dynamic category fields |
| `templates/auction/detail.html` | Auction page: price, countdown, bids |
| `templates/auction/list.html` | Active auctions grid |
| `static/js/auction.js` | Countdown timer, bid polling |

**Key routes**: `/auctions`, `/auction/create`, `/auction/<id>`, `/auction/<id>/bid`, `/auction/<id>/autobid`

**Exports for others**: `process_new_bid()`, `close_expired_auctions()`, `recalc_after_bid_removal()`

---

### 3. Om — Search, Browse, WishList, Alerts, Profile (11 files)

| File | Purpose |
|------|---------|
| `routes/search.py` | Browse categories, search, similar items |
| `routes/user.py` | Profile, my auctions, alerts, wishlist |
| `utils/similarity.py` | Similar items scoring |
| `utils/watches.py` | WishList → Alert trigger |
| `templates/search/browse.html` | Category tree |
| `templates/search/results.html` | Search results + filters |
| `templates/user/profile.html` | View/edit profile |
| `templates/user/my_auctions.html` | Selling/Bidding/Won/Lost tabs |
| `templates/user/alerts.html` | Notification center |
| `templates/user/wishlist.html` | Manage watches |
| `static/js/search.js` | Filter UI |

**Key routes**: `/browse`, `/search`, `/profile`, `/my-auctions`, `/alerts`, `/wishlist`, `/auction/<id>/similar`

**Exports for others**: `check_wishlist()` (Vivek calls from auction create)

---

### 4. Hitanshu — Admin, Rep & Support (12 files)

| File | Purpose |
|------|---------|
| `routes/admin.py` | Create reps, sales reports |
| `routes/rep.py` | Manage users, remove bids/auctions |
| `routes/support.py` | Q&A system |
| `templates/admin/dashboard.html` | Admin home |
| `templates/admin/create_rep.html` | Create rep form |
| `templates/admin/reports.html` | Sales report tables |
| `templates/rep/dashboard.html` | Rep home |
| `templates/rep/questions.html` | Question list + reply |
| `templates/rep/manage_user.html` | Edit/deactivate/reset user |
| `templates/rep/manage_auctions.html` | Remove auctions/bids |
| `templates/support/ask.html` | Submit question |
| `templates/support/my_questions.html` | View Q&A |

**Key routes**: `/admin`, `/admin/create-rep`, `/admin/reports`, `/rep`, `/rep/questions`, `/support`

**Imports from others**: `recalc_after_bid_removal()` from Vivek

---

### 5. Rishabh — Phase 2: Integration & Polish (after all merges)

| Task | Details |
|------|---------|
| Blueprint wiring | Register all blueprints in `app.py` |
| Nav updates | Add all links to `base.html`, role-aware visibility |
| Shared partials | `auction_card.html`, `empty_state.html` |
| Alert badge | Real-time unread count in nav |
| Demo data | Expand `seed.py` with 15-20 auctions + bids + transactions |
| ER diagram | Generate `er_diagram.png` from models |
| MySQL cutover | Docker Compose up, switch to MySQL, re-seed |
| README | Finalize with team, features, screenshots |
| Testing | End-to-end flow + edge cases |

---

## Cross-Team Interfaces

| Function | Written By | Called By |
|----------|-----------|----------|
| `process_new_bid(auction, amount, bidder_id)` | Vivek | Vivek (internal) |
| `close_expired_auctions()` | Vivek | Rishabh (hooks in `app.py`) |
| `recalc_after_bid_removal(auction)` | Vivek | Hitanshu (rep bid removal) |
| `check_wishlist(new_auction)` | Om | Vivek (after auction create) |
| `find_similar(auction)` | Om | Om (internal) |

---

## Effort

| Member | Scope | Effort |
|--------|-------|--------|
| Rishabh | Phase 1 ✅ + Phase 2 Integration | 🟡 6-8 hrs total |
| Vivek | Auctions, Bidding, AutoBid | 🔴 8-10 hrs |
| Om | Search, Browse, WishList, Alerts | 🟡 7-9 hrs |
| Hitanshu | Admin, Rep, Reports, Support | 🟡 7-9 hrs |

---

## Quick Start

```bash
cd Finalproject && source venv/bin/activate && flask run --debug
# → http://127.0.0.1:5000
# Accounts: admin/admin123 · johndoe/password · janesmith/password
```
