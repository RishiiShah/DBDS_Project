# BuyMe — Full App Test Guide

**Setup:** `python seed.py` then `python app.py` → open `http://127.0.0.1:5000`

For a clean slate: delete `instance/buyme.db` (or `buyme.db`), then re-run `python seed.py`.

---

## Test Accounts

| Username   | Password  | Role  |
|------------|-----------|-------|
| admin      | admin123  | Admin |
| johndoe    | password  | User  |
| janesmith  | password  | User  |
| alice      | password  | User  |
| bob        | password  | User  |

> Rep accounts must be created by admin first — see Section III below.

---

## I. Regular User

### 1. Registration & Auth

- [ ] Visit `/register` while logged out → fill all fields → submit → lands on home, user is logged in
- [ ] Try registering with an existing username → validation error shown
- [ ] Try registering with password < 6 chars → validation error shown
- [ ] Log out → visit `/login` → log in as `johndoe / password` → welcome flash shown
- [ ] Try logging in with wrong password → "Invalid username or password" shown
- [ ] Visit any protected route (e.g. `/dashboard`) while logged out → redirected to login

---

### 2. Dashboard

- [ ] Log in as `johndoe` → click **Dashboard** in nav
- [ ] **Active Listings** shows correct count of johndoe's open auctions
- [ ] **Active Bids** shows count of auctions johndoe has placed bids on and are still active
- [ ] **Unread Alerts** count shown; turns red if > 0; clicking navigates to Alerts page
- [ ] **Auctions Won** shows count of closed auctions johndoe won
- [ ] All 4 stat cards are clickable and link to the right pages
- [ ] Quick-action cards visible: Sell an Item, Browse Auctions, My Wishlist, Get Support

---

### 3. Browse & Search

- [ ] Click **Browse** → two root categories visible: **Electronics** and **Sporting Goods**
- [ ] Browse Electronics → Computers, Gaming, Mobile Phones, Wearables, Home Electronics → leaf subcategories below each
- [ ] Browse Sporting Goods → Cycling, Fitness, Outdoor & Adventure, Team Sports → leaf subcategories below each
- [ ] Click a leaf category (e.g. Laptops) → shows active auctions in that category
- [ ] Click a Sporting Goods leaf (e.g. Bikes) → shows Sporting Goods auctions in that category
- [ ] Click **Search** → search for `MacBook` → results shown with condition badge, category, description snippet, price
- [ ] Filter by price range (e.g. min $500) → results narrow correctly
- [ ] Filter by condition → results narrow correctly
- [ ] Sort by **Price: Low → High** → order changes
- [ ] Search with no results → "No auctions found" message shown

---

### 4. Auction Detail & Bidding

- [ ] From Browse or Search, click **View** on any auction → detail page loads with item info, current price, end time, bid history
- [ ] Log in → visit an auction you are **not** the seller of → bid form is visible
- [ ] Place a bid below the minimum → error: "Bid must be at least $X.XX"
- [ ] Place a valid bid → success flash, bid appears in history, current price updates
- [ ] Log in as a different user → place a higher manual bid → first user receives an **outbid** alert (covers both manual-vs-manual and manual-vs-auto scenarios)
- [ ] Try bidding on your own auction → error: "Sellers cannot bid on their own auctions"
- [ ] Scroll to bottom of any auction detail page → **Similar Auctions** section shows related listings (same category or similar price); click **View Auction** on one to navigate to it

---

### 5. Auto-Bid

- [ ] On an active auction, set an auto-bid upper limit at or above the current minimum → success flash shown; if no current winner, price updates and you become the winner immediately
- [ ] After setting, the **Auto-Bid** card shows a status banner: "Active — Your limit: $XXX.XX"
- [ ] The form pre-fills with your current limit and button reads "Update Auto-Bid"
- [ ] Update the limit to a higher value → banner reflects the new amount
- [ ] Click **Cancel Auto-Bid** → confirm prompt → auto-bid deactivated; banner shows "Inactive"; form resets to "Set Auto-Bid"
- [ ] Log in as another user → place a manual bid lower than the auto-bid limit → auto-bid fires, auto-bidder retakes the lead; outbid alert sent to the manual bidder
- [ ] Place a bid above the auto-bid upper limit → auto-bidder's limit is exhausted → they receive an **auto_bid_exceeded** alert

**Parallel auto-bid test (two users both using auto-bid):**
- [ ] User A logs in → sets auto-bid at $200 → becomes winner at starting price immediately; bid history shows an Auto entry for User A
- [ ] User B logs in → sets auto-bid at $150 → price updates instantly; User A retains lead at `min($200, $150+increment)`; User B receives **auto_bid_exceeded** alert; bid history shows auto entries for both users
- [ ] Reverse: User B sets auto-bid at $250 when User A holds $200 → User B wins at `min($250, $200+increment)`; User A receives **auto_bid_exceeded** alert
- [ ] Tie case: both users set equal limits → the first bidder (earlier `created_at`) retains the lead; second bidder receives **auto_bid_exceeded** alert

---

### 6. Create an Auction (Sell)

- [ ] Click **My Auctions** → **Create Auction** (or go to `/auction/create`)
- [ ] **Category** dropdown shows root categories (Electronics, Sporting Goods)
- [ ] Select **Electronics** → **Subcategory** dropdown appears with Electronics leaf categories
- [ ] Select **Sporting Goods** → **Subcategory** dropdown repopulates with Sporting Goods leaves (Bikes, Camping Gear, etc.)
- [ ] Select a subcategory that has required fields (e.g. Laptops → brand, ram, storage, screen_size) → those fields appear below the subcategory dropdown
- [ ] Select a subcategory with no required fields (e.g. Bikes → frame_size, material, gears) → those fields appear (or no extra fields if none defined)
- [ ] Fill all fields with end time in the past → error: "End time must be in the future"
- [ ] Trigger a validation error intentionally (e.g. leave item name blank) → on reload, both Category and Subcategory dropdowns restore to previous selections
- [ ] Fill all fields correctly (use Flatpickr to pick date+time) → auction created → redirected to auction detail page
- [ ] New auction appears in **My Auctions → Selling** tab
- [ ] If a wishlist watch matches the new auction's keyword → alert fires for the watching user

---

### 7. My Auctions

- [ ] Go to **My Auctions**
- [ ] **Selling** tab → shows auctions you created (active and closed)
- [ ] **Bidding** tab → shows active auctions you have placed bids on
- [ ] **Won** tab → shows closed auctions where you are the winner
- [ ] **Lost** tab → shows closed auctions you bid on but did not win

---

### 8. Alerts

- [ ] Go to **Alerts** → unread alerts listed newest first
- [ ] Click **Mark as Read** on an alert → alert marked read, badge count decreases
- [ ] Unread badge in nav auto-updates every 30 seconds

---

### 9. Wishlist

- [ ] Go to **Wishlist** → click **Add Watch** → enter a keyword (e.g. `Sony`)
- [ ] Optionally set category, min/max price → submit → watch appears in list
- [ ] Create a new auction whose name matches the keyword (log in as another user) → the watching user receives an **item_available** alert
- [ ] Delete a watch → removed from list

---

### 10. Profile

- [ ] Go to **Profile** → current name and email shown
- [ ] Edit first name, last name, email → save → changes persist
- [ ] Submit with empty first name → validation error
- [ ] **Delete Account** → account deactivated, logged out, redirected to home
- [ ] Try logging in as the deactivated account → "account has been deactivated" message

---

### 11. Support Q&A

- [ ] Click **Support** in nav → "My Questions" page loads
- [ ] Click **+ Ask a Question** → fill subject and message → submit
- [ ] Redirected to "My Questions" → question shows with status **Open**
- [ ] Visit `/support/search` → search a keyword from a submitted question → no results yet (questions answered by rep will appear here)
- [ ] After rep replies (see Section II) → question status changes to **Answered** with rep reply visible
- [ ] Search `/support/search` again with keyword → answered question now appears

---

## II. Customer Rep

> First create a rep account via Admin (Section III step 1), then log in as that rep.

### 1. Login & Nav

- [ ] Log in as the rep account → login succeeds
- [ ] **Rep Panel** link visible in nav
- [ ] Visiting `/admin/` as a rep → 403 Forbidden

---

### 2. Rep Dashboard

- [ ] Click **Rep Panel** → dashboard loads
- [ ] Stats show: Open Questions, Active Users, Active Auctions
- [ ] Open Questions count is red if > 0
- [ ] Three action cards visible: Manage Users, Manage Auctions, Answer Questions

---

### 3. Answer Questions

- [ ] Click **Answer Questions** → open questions from users listed
- [ ] Filter by **Answered** → answered questions shown
- [ ] Filter by **Closed** → closed questions shown
- [ ] Search by keyword in subject/body → filters results
- [ ] Type a reply in the inline form → click **Post Reply** → status changes to **Answered**; user can now see the reply in their My Questions page
- [ ] Click **Close** on a question → status changes to **Closed**, reply form hidden

---

### 4. Manage Users

- [ ] Click **Manage Users** → all end-users listed
- [ ] Search by username, email, or name → results filter correctly
- [ ] Click **Edit Info** on a user → inline form expands → update name and/or email → **Save** → change persists; verify by checking that user's profile
- [ ] Click **Reset PW** → enter new password (min 6 chars) → submit → log in as that user with new password to confirm it works
- [ ] Try resetting with < 6 char password → validation error
- [ ] Click **Deactivate** on a user → confirm prompt → status changes to **Inactive**
- [ ] Try logging in as the deactivated user → "account has been deactivated" shown
- [ ] Click **Reactivate** → user can log in again
- [ ] Try editing or deactivating an admin or rep account from this page → error: "Only end-user accounts can be edited/deactivated here"

---

### 5. Manage Auctions — Remove a Bid

- [ ] Click **Manage Auctions** → active auctions listed
- [ ] Click **Bids** on any auction with bids → bid panel opens showing bidder, amount, type (manual/auto), time
- [ ] Click **Remove** on the highest bid → confirm → bid disappears
- [ ] Auction's current price recalculates to the next highest bid (or reverts to starting price if no bids remain)
- [ ] Log in as the bidder whose bid was removed → **Alerts** → alert with message "Your bid was removed by a customer rep" is shown with no errors

---

### 6. Manage Auctions — Remove an Auction

- [ ] Back in **Manage Auctions**, filter by **Active**
- [ ] Click **Remove** on any auction → inline form expands
- [ ] Enter an optional reason → click **Confirm Remove**
- [ ] Auction status changes to **Cancelled**; no longer appears in active list
- [ ] Log in as the auction's seller → **Alerts** → `auction_cancelled` alert shown with reason (if provided)
- [ ] If the auction had a current winner → that user also receives an `auction_cancelled` alert

---

## III. Admin

### 1. Create a Customer Rep

- [ ] Log in as `admin / admin123` → **Admin** link visible in nav
- [ ] Click **Admin** → admin dashboard loads with user/rep counts and rep list
- [ ] Click **+ Create Rep Account** → fill all fields → submit
- [ ] New rep appears in the rep list on admin dashboard with status **Active**
- [ ] Try creating a rep with an existing username → "Username already taken" error
- [ ] Try creating a rep with an existing email → "Email already in use" error
- [ ] Log out → log in as the new rep with the password you just set → login succeeds

---

### 2. Admin can access Rep Panel

- [ ] While logged in as admin → **Rep Panel** link is visible in nav
- [ ] Admin can perform all rep actions: manage users, manage auctions, answer questions

---

### 3. Sales Reports (requires closed auctions)

- [ ] Click **Admin** → **Sales Reports**
- [ ] If no auctions have closed yet → empty state: "No completed transactions yet" shown
- [ ] **To generate test data:** In the DB (`instance/buyme.db`), set any active auction's `end_time` to a past datetime. Then visit `/auctions` in the browser (this triggers `close_expired_auctions()`). Refresh the reports page.
- [ ] **Total Sales** count > 0
- [ ] **Total Revenue** and **BuyMe Commission (5%)** show correct dollar amounts
- [ ] **Top Items by Sale Price** table populated
- [ ] **Earnings by Category** table populated
- [ ] **Best Sellers** table populated
- [ ] **Best Buyers** table populated
- [ ] Only auctions that closed with a winning bid **above the reserve price** appear in reports (reserve not met = no transaction)

---

### 4. Access Control

- [ ] Log in as `johndoe` → visit `/admin/` → 403 Forbidden
- [ ] Log in as rep → visit `/admin/` → 403 Forbidden
- [ ] Log out → visit `/rep/` → redirected to login page
- [ ] Log out → visit `/support/ask` → redirected to login page
- [ ] Log out → visit `/support/search` → page loads (public route)
