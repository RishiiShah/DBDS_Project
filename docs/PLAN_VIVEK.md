# Vivek — Auction Engine & Bidding

**Order**: 2nd (after Rishabh's scaffold) | **Branch**: `main`

---

## Your Deliverables

| # | File | Purpose |
|---|------|---------|
| 1 | `routes/auction.py` | All auction + bidding routes |
| 2 | `utils/bidding.py` | Auto-bid engine + auction closing logic |
| 3 | `templates/auction/create.html` | Create auction form (dynamic category fields) |
| 4 | `templates/auction/detail.html` | Auction page: bids, countdown, auto-bid form |
| 5 | `templates/auction/list.html` | Grid of active auctions |
| 6 | `static/js/auction.js` | Countdown timer, AJAX bid polling |
| 7 | `app.py` | MODIFY — register `auction_bp` blueprint |

---

## Routes (`routes/auction.py`)

```
GET  /auctions              → List active auctions (optional ?category=<id>)
GET  /auction/create         → Show create form (login required)
POST /auction/create         → Create Item + ItemAttributes + Auction
GET  /auction/<id>           → Detail: item info, price, countdown, bid history
POST /auction/<id>/bid       → Place manual bid (validate >= current + increment)
POST /auction/<id>/autobid   → Set AutoBid upper_limit
GET  /auction/<id>/history   → JSON bid history for AJAX polling
```

**Create auction flow:**
1. User picks a leaf category → load `category.required_fields` JSON
2. Render dynamic inputs (brand, ram, storage, etc.)
3. On POST: create `Item`, create `ItemAttribute` for each field, create `Auction` with `current_price = starting_price`

**Place bid flow:**
1. Validate `amount >= auction.current_price + auction.bid_increment`
2. Call `process_new_bid(auction, amount, bidder_id)` from `utils/bidding.py`

---

## Auto-Bidding Engine (`utils/bidding.py`)

### `process_new_bid(auction, bid_amount, bidder_id)`
1. Save the manual `Bid`
2. Query active `AutoBid`s for this auction (exclude current bidder), sorted by `upper_limit DESC`
3. Top auto-bidder counter-bids at `bid_amount + auction.bid_increment`:
   - If within their `upper_limit` → place auto `Bid`, create `Alert('outbid')` for displaced bidder
   - If exceeds `upper_limit` → deactivate, create `Alert('auto_bid_exceeded')`
4. If 2+ auto-bidders compete → highest limit wins at `(2nd_highest + increment)`
5. Update `auction.current_price` and `current_winner_id`

### `close_expired_auctions()`
- Query auctions where `status='active' AND end_time <= now`
- If `current_price >= reserve_price` → create `Transaction` (5% commission), `Alert('auction_won')` to winner
- Else → `Alert('auction_lost')`, reserve not met

### `recalc_after_bid_removal(auction)`
- After Hitanshu removes a bid, recalculate `current_price` from remaining bids
- Export this so Hitanshu can import it

---

## Templates

**`auction/create.html`**: Form with item fields + category dropdown + dynamic attribute fields + auction pricing + end date/time picker

**`auction/detail.html`**: Item card, current price (large), countdown timer, bid form, auto-bid form (collapsible), bid history table with auto/manual badges

**`auction/list.html`**: Grid of cards (name, price, time left, bid count)

**`static/js/auction.js`**: Countdown timer (h/m/s), bid history polling every 5s

---

## Checklist

- [ ] All 7 routes working
- [ ] Auto-bid tested with 2+ competing auto-bidders
- [ ] `close_expired_auctions()` creates transactions + alerts
- [ ] `recalc_after_bid_removal()` exported for Hitanshu
- [ ] Dynamic category fields render on create form
- [ ] Countdown timer works in JS
- [ ] Blueprint registered in `app.py`
- [ ] All committed to `main`

## How to Test
1. `johndoe` creates auction (Laptops, fill brand/ram/etc.)
2. `janesmith` bids → verify bid appears
3. `johndoe` sets auto-bid $500 → `janesmith` bids $300 → auto-bid fires
4. Create 1-min auction → wait → verify close + winner alert
