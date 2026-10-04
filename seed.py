"""
Fills the database with a SIMULATED 7-day campaign so the dashboard has something to show.
All names/emails are fake. Campaign Day 1 = 6 days ago, Day 7 = today.

    python seed.py            # ~492 simulated registrations (so you can push it past 500 live in the demo)
    python seed.py 300        # custom number
    python seed.py --empty    # wipe everything and start clean
"""
import os
import random
import sqlite3
import sys
from datetime import date, datetime, timedelta

from app import DB_PATH, init_db

random.seed(7)
FIRST = ["Aarav", "Ananya", "Rohit", "Sneha", "Karthik", "Divya", "Vamsi", "Keerthi", "Rahul", "Pooja", "Sai",
         "Harika", "Arjun", "Lakshmi", "Nikhil", "Meghana", "Teja", "Bhavana", "Vikram", "Sahithi", "Manoj",
         "Tejaswini", "Abhinav", "Ishita", "Charan", "Navya", "Pranav", "Ritika", "Suresh", "Yamini"]
LAST = ["Reddy", "Rao", "Sharma", "Naidu", "Kumar", "Varma", "Iyer", "Patel", "Chowdary", "Nair", "Gupta", "Murthy"]
COLLEGES = ["VIT-AP University", "SRM University AP", "KL University", "GITAM Vizag", "Amrita Coimbatore",
            "CBIT Hyderabad", "VNR VJIET", "Vasavi College of Engg", "GRIET", "Andhra University",
            "JNTU Kakinada", "RVR & JC College", "Anurag University", "MVGR Vizianagaram", "Aditya Engg College",
            "SASTRA University", "PSG Tech", "BVRIT Narsapur", "Malla Reddy Engg College", "Sreenidhi IET"]
BRANCHES = ["CSE", "CSE", "CSE", "IT", "AI & DS", "AI & DS", "ECE", "ECE", "EEE", "Mech"]
# Channel mix the plan expects (non-referral share). Referrals are layered on top.
ORGANIC_MIX = [("whatsapp", 0.52), ("club", 0.22), ("linkedin", 0.12), ("bot", 0.08), ("direct", 0.06)]
# Daily share of total registrations (ramps up with waves on Day 2, 5 and the last-24h push on Day 6-7)
DAY_WEIGHTS = [0.05, 0.13, 0.15, 0.14, 0.18, 0.19, 0.16]


def pick(mix):
    r, acc = random.random(), 0
    for k, w in mix:
        acc += w
        if r <= acc:
            return k
    return mix[-1][0]


def main():
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
    conn = sqlite3.connect(DB_PATH)
    init_db(conn)
    start = date.today() - timedelta(days=6)
    conn.execute("INSERT OR REPLACE INTO meta VALUES ('start', ?)", (start.isoformat(),))
    if "--empty" in sys.argv:
        conn.commit()
        print("Database reset. Campaign Day 1 starts", start)
        return
    n_total = int(next((a for a in sys.argv[1:] if a.isdigit()), 492))

    people, seq = [], 0
    for day, w in enumerate(DAY_WEIGHTS):
        for _ in range(round(n_total * w)):
            if len(people) >= n_total:
                break
            seq += 1
            name = f"{random.choice(FIRST)} {random.choice(LAST)}"
            # ~28% of registrations come through someone's referral link (more as the campaign matures)
            referrer = None
            if people and random.random() < 0.12 + 0.04 * day:
                # power-law: early/active people refer more
                referrer = random.choice(people[: max(5, len(people) // 3)])
            college = referrer["college"] if referrer and random.random() < 0.75 else random.choice(COLLEGES)
            ts = datetime.combine(start + timedelta(days=day), datetime.min.time()) + timedelta(
                minutes=random.randint(9 * 60, 23 * 60))
            if ts > datetime.now():
                ts = datetime.now() - timedelta(minutes=random.randint(1, 300))
            p = {
                "name": name, "email": f"{name.split()[0].lower()}.{seq}@example.com",
                "phone": f"+91 9{random.randint(100000000, 999999999)}", "college": college,
                "branch": random.choice(BRANCHES),
                "year": random.choices(["Final year (4th)", "3rd year", "Other / Graduate"], [0.82, 0.13, 0.05])[0],
                "ref_code": f"{name.split()[0].upper()[:6]}{seq:03d}",
                "referred_by": referrer["ref_code"] if referrer else None,
                "source": "referral" if referrer else pick(ORGANIC_MIX),
                "created_at": ts.isoformat(timespec="seconds"),
            }
            if seq == 1:  # fixed demo student so the README/video can reference a known code
                p.update(name="Priya Reddy", email="priya.demo@example.com", ref_code="PRIYA001")
            people.append(p)
    conn.executemany(
        """INSERT INTO students (name,email,phone,college,branch,year,ref_code,referred_by,source,created_at)
           VALUES (:name,:email,:phone,:college,:branch,:year,:ref_code,:referred_by,:source,:created_at)""", people)
    conn.commit()
    print(f"Seeded {len(people)} simulated registrations. Campaign Day 1 = {start}, Day 7 = today.")
    print("Demo student page: http://127.0.0.1:5000/me/PRIYA001")


if __name__ == "__main__":
    main()
