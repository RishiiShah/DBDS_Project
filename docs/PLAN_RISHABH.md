# Rishabh — Scaffold, Models, Auth + Integration & Polish

**Order**: 1st (Phase 1) and 4th/Last (Phase 2)
**Branch**: `main`

---

## Phase 1 — Foundation (✅ COMPLETE)

Everything below is already done and committed to `main`.

- [x] Virtual environment + `requirements.txt`
- [x] `docker-compose.yml` for MySQL
- [x] `config.py` with SQLite fallback (`USE_MYSQL=true` to switch)
- [x] `app.py` — Flask factory, Flask-Login, bcrypt
- [x] All 13 database models (`models/`)
- [x] Auth routes — Register, Login, Logout (`routes/auth.py`)
- [x] `utils/decorators.py` — `@role_required`
- [x] Base template + dark theme CSS + JS
- [x] `seed.py` — admin + test users + category hierarchy
- [x] `README.md`

---

## Phase 2 — Integration & Polish (AFTER Vivek, Om, Hitanshu finish)

### Part A: Blueprint Wiring & Nav

Update `app.py` to register all new blueprints:

```python
# app.py — add after existing blueprints
from routes.auction import auction_bp      # Vivek
from routes.search import search_bp        # Om
from routes.user import user_bp            # Om
from routes.admin import admin_bp          # Hitanshu
from routes.rep import rep_bp              # Hitanshu
from routes.support import support_bp      # Hitanshu

app.register_blueprint(auction_bp)
app.register_blueprint(search_bp)
app.register_blueprint(user_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(rep_bp)
app.register_blueprint(support_bp)
```

Update `templates/base.html` nav to include all pages:
```html
<!-- Add to nav-links -->
<a href="/browse" class="nav-link">Browse</a>
<a href="/search" class="nav-link">Search</a>
<!-- Logged-in links -->
<a href="/my-auctions" class="nav-link">My Auctions</a>
<a href="/wishlist" class="nav-link">WishList</a>
<a href="/alerts" class="nav-link">Alerts <span id="alert-badge"></span></a>
<a href="/support" class="nav-link">Support</a>
<!-- Admin only -->
<a href="/admin" class="nav-link">Admin</a>
<!-- Rep only -->
<a href="/rep" class="nav-link">Rep Panel</a>
```

Hook auction closing into app lifecycle:
```python
@app.before_request
def before_request():
    from utils.bidding import close_expired_auctions
    close_expired_auctions()
```

### Part B: Shared UI Components

Create these shared partials that all pages use:

**`templates/partials/auction_card.html`** — Reusable card showing:
- Item name, image placeholder, category
- Current price, bid count, time remaining
- Link to auction detail

**`templates/partials/empty_state.html`** — "No results" with icon

**Alert badge polling** — Add to `static/js/app.js`:
```javascript
// Poll unread alert count every 30s
setInterval(async () => {
    const res = await fetch('/alerts/unread-count');
    const data = await res.json();
    const badge = document.getElementById('alert-badge');
    if (badge) badge.textContent = data.count > 0 ? data.count : '';
}, 30000);
```

### Part C: Demo Data

Expand `seed.py` to add:
- 15-20 sample auctions across all categories
- Bids and auto-bids on those auctions
- Some completed transactions (so admin reports have data)
- Sample questions and answers
- Item watches / alerts

### Part D: Final Deliverables

- [ ] Generate `er_diagram.png` from models (matches handwritten ER)
- [ ] MySQL cutover: `docker compose up -d`, `USE_MYSQL=true`, re-seed
- [ ] Update `README.md` — team members, full feature checklist, screenshots
- [ ] End-to-end test: register → auction → bid → auto-bid → close → report
- [ ] Edge case testing: invalid bids, closed auctions, deactivated users
- [ ] Final commit audit: verify all 4 members have code commits

### Files to Create/Modify

| File | Action |
|------|--------|
| `app.py` | MODIFY — wire all blueprints, add `before_request` hook |
| `templates/base.html` | MODIFY — full nav with all links + alert badge |
| `templates/partials/auction_card.html` | NEW |
| `templates/partials/empty_state.html` | NEW |
| `seed.py` | MODIFY — rich demo data |
| `static/css/style.css` | MODIFY — auction card styles, animations |
| `static/js/app.js` | MODIFY — alert badge polling |
| `er_diagram.py` | NEW — generate ER diagram |
| `README.md` | MODIFY — final version |

### Checklist

- [ ] All blueprints registered and pages load without errors
- [ ] Nav shows correct links per role (user/rep/admin)
- [ ] Alert badge updates in real-time
- [ ] Auction card partial used everywhere (list, search, browse, similar)
- [ ] Demo data seeded — auctions, bids, transactions visible
- [ ] All pages responsive on mobile
- [ ] ER diagram generated and committed
- [ ] README finalized with team info and screenshots
- [ ] MySQL tested via Docker
- [ ] Each team member has code commits
