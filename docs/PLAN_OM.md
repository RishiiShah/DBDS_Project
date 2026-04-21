# Om — Search, Browse, WishList, Alerts & Profile

**Order**: 3rd (after Vivek's auctions are on `main`) | **Branch**: `main`

---

## Your Deliverables

| # | File | Purpose |
|---|------|---------|
| 1 | `routes/search.py` | Browse categories, search, similar items |
| 2 | `routes/user.py` | Profile, my auctions, alerts, wishlist |
| 3 | `utils/similarity.py` | Similar items scoring algorithm |
| 4 | `utils/watches.py` | WishList → Alert trigger (called by Vivek's auction create) |
| 5 | `templates/search/browse.html` | Category tree navigation |
| 6 | `templates/search/results.html` | Search results with filter sidebar |
| 7 | `templates/user/profile.html` | View/edit profile |
| 8 | `templates/user/my_auctions.html` | Tabs: Selling / Bidding / Won / Lost |
| 9 | `templates/user/alerts.html` | Notification center |
| 10 | `templates/user/wishlist.html` | Manage item watches |
| 11 | `static/js/search.js` | Dynamic filters, live search |
| 12 | `app.py` | MODIFY — register `search_bp` and `user_bp` |

---

## Routes — Search & Browse (`routes/search.py`)

```
GET /browse                 → Category hierarchy page
GET /browse/<category_id>   → Auctions in that category (include children)
GET /search                 → Multi-criteria search with query params:
                               ?q=keyword&category_id=5&min_price=100
                               &max_price=500&condition=new&sort=price_asc
GET /auction/<id>/similar   → Similar items from past month
```

**Search query builder:**
- Keyword: `Item.name.ilike(f'%{q}%') | Item.description.ilike(f'%{q}%')`
- Category: filter by `category_id` OR any child categories
- Price: `Auction.current_price.between(min, max)`
- Condition: `Item.condition == condition`
- Attributes: JOIN `ItemAttribute`, filter by `attr_name/attr_value`
- Sort: `price_asc`, `price_desc`, `ending_soon`, `newest`, `most_bids`

---

## Routes — Profile & Alerts (`routes/user.py`)

```
GET  /profile               → View profile
POST /profile/edit           → Update name, email
POST /profile/delete         → Soft-delete (is_active=False), logout

GET  /my-auctions            → Auctions I'm selling / bidding on
GET  /user/<id>/auctions     → Public: all auctions user participated in

GET  /alerts                 → All alerts (newest first, paginated)
POST /alerts/<id>/read       → Mark alert as read
GET  /alerts/unread-count    → JSON: { "count": N } (for nav badge)

GET  /wishlist               → My active watches
POST /wishlist/create        → Create watch (keyword, category, price range)
POST /wishlist/<id>/delete   → Remove a watch
```

---

## Similarity Algorithm (`utils/similarity.py`)

```python
def find_similar(auction, limit=10):
    """
    Score other active auctions from the past month.
    
    Scoring:
      +40  Same leaf category
      +20  Same parent category (different leaf)
      +20  Price within ±30% of auction.current_price
      +10  Each matching ItemAttribute (brand, condition)
    
    Returns top `limit` auctions sorted by score DESC.
    """
```

---

## WishList Trigger (`utils/watches.py`)

```python
def check_wishlist(new_auction):
    """
    Called when a new auction is created (by Vivek's routes/auction.py).
    Check all active ItemWatch entries. If match:
      - keyword found in item.name or item.description
      - category matches (if specified in watch)
      - price in range (if specified)
    Then create Alert('item_available') for that user.
    """
```

> Vivek should add `from utils.watches import check_wishlist` in his auction create route.
> If his code already has a try/except around it, just make sure the import path works.

---

## Checklist

- [ ] Browse page shows category tree, click → filtered auctions
- [ ] Search works with keyword, category, price range, condition, sort
- [ ] Similar items shows scored results from past month
- [ ] Profile edit and delete work
- [ ] My Auctions tabs show correct data
- [ ] Alerts page lists all notifications, mark-as-read works
- [ ] `/alerts/unread-count` returns JSON
- [ ] WishList create/delete works
- [ ] `check_wishlist()` creates alerts for matching new auctions
- [ ] Both blueprints registered in `app.py`
- [ ] All committed to `main`

## How to Test
1. Browse categories → click Laptops → see Vivek's sample auctions
2. Search "MacBook" → verify keyword match
3. View an auction → click "Similar Items" → verify scoring
4. Create a WishList watch for "iPhone" → create matching auction → verify alert appears
5. Check `/alerts` and `/alerts/unread-count`
