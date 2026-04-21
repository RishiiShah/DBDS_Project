# Hitanshu — Admin Dashboard, Customer Rep & Support Q&A

**Order**: 4th (after Vivek + Om are on `main`) | **Branch**: `main`

---

## Your Deliverables

| # | File | Purpose |
|---|------|---------|
| 1 | `routes/admin.py` | Admin: create reps, reports |
| 2 | `routes/rep.py` | Rep: manage users, remove bids/auctions |
| 3 | `routes/support.py` | Q&A: ask questions, rep answers |
| 4 | `templates/admin/dashboard.html` | Admin home + stats |
| 5 | `templates/admin/create_rep.html` | Create rep account form |
| 6 | `templates/admin/reports.html` | Sales reports tables |
| 7 | `templates/rep/dashboard.html` | Rep home: open questions |
| 8 | `templates/rep/questions.html` | List + reply to questions |
| 9 | `templates/rep/manage_user.html` | Edit/deactivate user, reset password |
| 10 | `templates/rep/manage_auctions.html` | View/remove auctions + bids |
| 11 | `templates/support/ask.html` | User submits question |
| 12 | `templates/support/my_questions.html` | User views Q&A history |
| 13 | `app.py` | MODIFY — register 3 blueprints |

---

## Routes — Admin (`routes/admin.py`)

All routes use `@role_required('admin')` from `utils/decorators.py`.

```
GET  /admin                  → Dashboard (total users, auctions, transactions)
GET  /admin/create-rep       → Show form
POST /admin/create-rep       → Create user with role='rep', hash password with bcrypt

GET  /admin/reports          → Sales reports page
GET  /admin/reports/data     → JSON API, ?type= param:
      total_earnings          → SUM(Transaction.commission)
      earnings_per_item       → GROUP BY Item.name
      earnings_per_type       → GROUP BY Category.name
      earnings_per_user       → GROUP BY User (buyer or seller)
      best_selling_items      → ORDER BY transaction count DESC, LIMIT 10
      best_buyers             → ORDER BY total spend DESC, LIMIT 10
```

**Key report queries:**
```python
from sqlalchemy import func
from models.auction import Transaction, Auction
from models.item import Item, Category
from models.user import User

# Total earnings
db.session.query(func.sum(Transaction.commission)).scalar()

# Earnings per category
db.session.query(Category.name, func.sum(Transaction.commission)) \
    .join(Auction, Transaction.auction_id == Auction.id) \
    .join(Item, Auction.item_id == Item.id) \
    .join(Category, Item.category_id == Category.id) \
    .group_by(Category.name).all()

# Best-selling items
db.session.query(Item.name, func.count(Transaction.id)) \
    .join(Auction).join(Transaction) \
    .group_by(Item.name).order_by(func.count(Transaction.id).desc()).limit(10).all()

# Best buyers
db.session.query(User.username, func.sum(Transaction.final_price)) \
    .join(Transaction, User.id == Transaction.buyer_id) \
    .group_by(User.username).order_by(func.sum(Transaction.final_price).desc()).limit(10).all()
```

---

## Routes — Customer Rep (`routes/rep.py`)

All routes use `@role_required('rep')`.

```
GET  /rep                        → Dashboard: open question count, recent activity
GET  /rep/questions              → All open questions
POST /rep/question/<id>/answer   → Post reply, set question status='answered'

GET  /rep/users                  → Search/list all users
GET  /rep/user/<id>              → User detail
POST /rep/user/<id>/edit         → Edit name, email
POST /rep/user/<id>/reset-password → Set new password (hash with bcrypt)
POST /rep/user/<id>/deactivate   → Set is_active=False

POST /rep/bid/<id>/remove        → Delete bid, call recalc_after_bid_removal()
POST /rep/auction/<id>/remove    → Set status='cancelled', alert all bidders
```

**Bid removal** — import from Vivek's code:
```python
from utils.bidding import recalc_after_bid_removal

@rep_bp.route('/rep/bid/<int:id>/remove', methods=['POST'])
@role_required('rep')
def remove_bid(id):
    bid = Bid.query.get_or_404(id)
    auction = bid.auction
    db.session.delete(bid)
    db.session.commit()
    recalc_after_bid_removal(auction)
    flash('Bid removed.', 'success')
    return redirect(url_for('auction.detail', id=auction.id))
```

---

## Routes — Support Q&A (`routes/support.py`)

```
GET  /support                → My questions (login required)
GET  /support/ask            → Show form
POST /support/ask            → Create Question(user_id, subject, body)
GET  /support/question/<id>  → Question detail + answers
GET  /support/browse         → All answered Q&A (public)
GET  /support/search?q=      → Search questions by keyword
```

---

## Checklist

- [ ] Admin dashboard shows user/auction/transaction counts
- [ ] Admin can create rep account (appears with Rep role)
- [ ] All 6 report types return correct data
- [ ] Reports page renders tables/stats
- [ ] Rep can view and reply to questions
- [ ] Rep can edit user info and reset passwords
- [ ] Rep can deactivate users
- [ ] Rep can remove bids (price recalculates)
- [ ] Rep can remove/cancel auctions (bidders alerted)
- [ ] Users can ask questions and view answers
- [ ] Support browse and search work
- [ ] All 3 blueprints registered in `app.py`
- [ ] All committed to `main`

## How to Test
1. Login as `admin` → create rep account (e.g., `rep1/rep123`)
2. Login as `admin` → view reports (need transactions — Vivek's test auctions)
3. Login as `johndoe` → ask a question via `/support/ask`
4. Login as `rep1` → answer the question → verify status changes
5. As rep → edit johndoe's email → verify change
6. As rep → remove a bid → verify auction price recalculates
7. As rep → cancel an auction → verify bidders get alerts
