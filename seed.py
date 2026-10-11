"""Create analytics.db with a small, realistic dataset for the demo.

Run once before recording:
    uv run seed.py
"""

import random
import sqlite3
from datetime import date, timedelta

DB = "analytics.db"
random.seed(42)  

FIRST = ["Ada", "Linus", "Grace", "Alan", "Margaret", "Dennis", "Barbara",
         "Ken", "Edsger", "Radia", "Vint", "Katherine", "Donald", "Hedy",
         "John", "Anita", "Tags", "Whitfield", "Frances", "Niklaus"]
LAST = ["Lovelace", "Torvalds", "Hopper", "Turing", "Hamilton", "Ritchie",
        "Liskov", "Thompson", "Dijkstra", "Perlman", "Cerf", "Johnson",
        "Knuth", "Lamarr", "McCarthy", "Borg", "Diffie", "Merchant", "Allen",
        "Wirth"]
PLANS = ["free", "pro", "team"]
COUNTRIES = ["US", "IN", "DE", "BR", "GB", "JP", "NG", "CA", "FR", "AU"]
EVENTS = ["login", "view_dashboard", "create_project", "invite_member",
          "upgrade", "downgrade", "cancel"]
PLAN_PRICE = {"free": 0, "pro": 2000, "team": 9900}  # cents / month

con = sqlite3.connect(DB)
cur = con.cursor()
cur.executescript(
    """
    DROP TABLE IF EXISTS users;
    DROP TABLE IF EXISTS events;
    DROP TABLE IF EXISTS orders;

    CREATE TABLE users (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        email TEXT NOT NULL,
        plan TEXT NOT NULL,
        country TEXT NOT NULL,
        signup_date TEXT NOT NULL
    );
    CREATE TABLE events (
        id INTEGER PRIMARY KEY,
        user_id INTEGER NOT NULL,
        event TEXT NOT NULL,
        ts TEXT NOT NULL
    );
    CREATE TABLE orders (
        id INTEGER PRIMARY KEY,
        user_id INTEGER NOT NULL,
        amount_cents INTEGER NOT NULL,
        plan TEXT NOT NULL,
        created_at TEXT NOT NULL
    );
    """
)

start = date(2025, 1, 1)
today = date(2026, 9, 30)

users = []
for uid in range(1, 301):
    name = f"{random.choice(FIRST)} {random.choice(LAST)}"
    email = name.lower().replace(" ", ".") + f"{uid}@example.com"
    plan = random.choices(PLANS, weights=[6, 3, 1])[0]
    country = random.choice(COUNTRIES)
    signup = start + timedelta(days=random.randint(0, (today - start).days))
    users.append((uid, name, email, plan, country, signup.isoformat()))
cur.executemany("INSERT INTO users VALUES (?, ?, ?, ?, ?, ?)", users)

events = []
eid = 1
for uid, *_ in users:
    for _ in range(random.randint(1, 25)):
        ts = start + timedelta(days=random.randint(0, (today - start).days))
        events.append((eid, uid, random.choice(EVENTS), ts.isoformat()))
        eid += 1
cur.executemany("INSERT INTO events VALUES (?, ?, ?, ?)", events)

orders = []
oid = 1
for uid, _, _, plan, _, signup in users:
    if plan == "free":
        continue
    n = random.randint(1, 8)
    sd = date.fromisoformat(signup)
    for _ in range(n):
        d = sd + timedelta(days=random.randint(0, 300))
        if d > today:
            d = today
        orders.append((oid, uid, PLAN_PRICE[plan], plan, d.isoformat()))
        oid += 1
cur.executemany("INSERT INTO orders VALUES (?, ?, ?, ?, ?)", orders)

con.commit()
print(f"users={len(users)} events={len(events)} orders={len(orders)} -> {DB}")
con.close()
