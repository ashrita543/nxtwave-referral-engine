"""
NxtWave Workshop Referral Engine
--------------------------------
Working asset for the NxtWave Growth Challenge:
"Build Your First AI Project in 60 Minutes" -> 500 final-year registrations in 7 days.

What it does
  1. Registration page that remembers WHO referred a student (?ref=CODE) and WHICH channel (?src=whatsapp)
  2. Every registrant gets a personal referral link + one-tap WhatsApp share + reward tiers
  3. WhatsApp bot flow (simulated): student types JOIN and registers inside the chat
  4. Public leaderboard: top referrers + college-vs-college race
  5. Growth dashboard: progress to 500, daily pace vs target, channel mix, viral coefficient, 7-day projection
  6. Message kit generator for ambassadors / clubs / placement cells

Run:  pip install flask   ->   python seed.py   ->   python app.py   ->   http://127.0.0.1:5000
"""
import csv
import io
import os
import random
import re
import sqlite3
import string
from datetime import datetime, timedelta, date
from urllib.parse import quote

from flask import (Flask, Response, abort, g, jsonify, redirect,
                   render_template, request, url_for)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "campaign.db")

GOAL = 500
CAMPAIGN_DAYS = 7
WORKSHOP = {
    "title": "Build Your First AI Project in 60 Minutes",
    "when": "Saturday · 7:00 PM IST · Live online",
    "outcome": "Leave with a working AI project + a live link to put on your resume",
}
# Reward tiers for referrals (what the ₹2,000 budget + zero-cost rewards fund)
TIERS = [
    (1, "AI Prompt Pack", "50 ready-to-use prompts for projects & interviews (free, digital)"),
    (3, "Community Builder badge", "Shout-out in the workshop + LinkedIn-ready certificate"),
    (5, "1:1 Project Review", "15-min review of your AI project by a mentor"),
    (10, "Leaderboard prize zone", "Top 3 referrers win ₹300 / ₹200 / ₹100 vouchers"),
]
SOURCES = {
    "whatsapp": "WhatsApp groups (ambassadors)",
    "referral": "Student referral link",
    "club": "Coding clubs / placement cells",
    "linkedin": "LinkedIn / Instagram organic",
    "bot": "WhatsApp bot",
    "direct": "Direct / other",
}

app = Flask(__name__)


# ----------------------------------------------------------------- database
def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(_):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db(conn=None):
    own = conn is None
    conn = conn or sqlite3.connect(DB_PATH)
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            phone TEXT,
            college TEXT NOT NULL,
            branch TEXT,
            year TEXT,
            ref_code TEXT NOT NULL UNIQUE,
            referred_by TEXT,
            source TEXT NOT NULL DEFAULT 'direct',
            created_at TEXT NOT NULL
        );
        CREATE INDEX IF NOT EXISTS idx_ref ON students(referred_by);
        CREATE TABLE IF NOT EXISTS meta (k TEXT PRIMARY KEY, v TEXT);
        """
    )
    conn.commit()
    if own:
        conn.close()


def campaign_start(db):
    row = db.execute("SELECT v FROM meta WHERE k='start'").fetchone()
    if row:
        return date.fromisoformat(row["v"])
    start = date.today()
    db.execute("INSERT OR REPLACE INTO meta VALUES ('start', ?)", (start.isoformat(),))
    db.commit()
    return start


def make_code(name, db):
    first = re.sub(r"[^A-Za-z]", "", name.split()[0] if name.split() else "NXT").upper()[:6] or "NXT"
    while True:
        code = f"{first}{''.join(random.choices(string.digits, k=3))}"
        if not db.execute("SELECT 1 FROM students WHERE ref_code=?", (code,)).fetchone():
            return code


def register_student(db, name, email, phone, college, branch, year, ref, source):
    """Single place where a registration is created (used by web form AND WhatsApp bot)."""
    email = email.strip().lower()
    existing = db.execute("SELECT * FROM students WHERE email=?", (email,)).fetchone()
    if existing:
        return existing, False
    if ref and not db.execute("SELECT 1 FROM students WHERE ref_code=?", (ref,)).fetchone():
        ref = None  # ignore invalid codes
    if ref and source in ("direct", "", None):
        source = "referral"
    code = make_code(name, db)
    db.execute(
        """INSERT INTO students (name,email,phone,college,branch,year,ref_code,referred_by,source,created_at)
           VALUES (?,?,?,?,?,?,?,?,?,?)""",
        (name.strip(), email, phone.strip(), college.strip(), branch, year, code, ref,
         source if source in SOURCES else "direct", datetime.now().isoformat(timespec="seconds")),
    )
    db.commit()
    return db.execute("SELECT * FROM students WHERE ref_code=?", (code,)).fetchone(), True


def total(db):
    return db.execute("SELECT COUNT(*) c FROM students").fetchone()["c"]


def share_text(student, link):
    return (
        f"Hey! I just registered for a FREE NxtWave live workshop: *{WORKSHOP['title']}* 🚀\n"
        f"You leave with a working AI project you can put on your resume before placements.\n"
        f"{WORKSHOP['when']}. Takes 60 seconds to register 👇\n{link}"
    )


# ----------------------------------------------------------------- public pages
@app.route("/")
def landing():
    db = get_db()
    ref = request.args.get("ref", "").upper()
    src = request.args.get("src", "direct")
    referrer = db.execute("SELECT name, college FROM students WHERE ref_code=?", (ref,)).fetchone() if ref else None
    top_colleges = db.execute(
        "SELECT college, COUNT(*) c FROM students GROUP BY college ORDER BY c DESC LIMIT 3").fetchall()
    return render_template("landing.html", w=WORKSHOP, count=total(db), goal=GOAL, ref=ref, src=src,
                           referrer=referrer, top_colleges=top_colleges)


@app.post("/register")
def register():
    db = get_db()
    f = request.form
    required = ["name", "email", "phone", "college", "year"]
    if any(not f.get(k, "").strip() for k in required):
        return redirect(url_for("landing", ref=f.get("ref", ""), src=f.get("src", ""), err=1))
    student, created = register_student(
        db, f["name"], f["email"], f["phone"], f["college"], f.get("branch", ""), f["year"],
        f.get("ref", "").upper() or None, f.get("src", "direct"))
    return redirect(url_for("me", code=student["ref_code"], new=int(created)))


@app.route("/me/<code>")
def me(code):
    db = get_db()
    s = db.execute("SELECT * FROM students WHERE ref_code=?", (code.upper(),)).fetchone()
    if not s:
        abort(404)
    friends = db.execute("SELECT name, college FROM students WHERE referred_by=? ORDER BY id DESC",
                         (s["ref_code"],)).fetchall()
    n = len(friends)
    link = url_for("landing", ref=s["ref_code"], src="referral", _external=True)
    wa = "https://wa.me/?text=" + quote(share_text(s, link))
    rank_row = db.execute(
        """SELECT COUNT(*)+1 r FROM (SELECT referred_by, COUNT(*) c FROM students WHERE referred_by IS NOT NULL
           GROUP BY referred_by) WHERE c > ?""", (n,)).fetchone()
    next_tier = next((t for t in TIERS if t[0] > n), None)
    return render_template("me.html", s=s, friends=friends, n=n, link=link, wa=wa, tiers=TIERS,
                           next_tier=next_tier, rank=rank_row["r"] if n else None,
                           new=request.args.get("new") == "1", w=WORKSHOP)


@app.route("/leaderboard")
def leaderboard():
    db = get_db()
    people = db.execute(
        """SELECT s.name, s.college, COUNT(r.id) c FROM students s JOIN students r ON r.referred_by = s.ref_code
           GROUP BY s.id ORDER BY c DESC, s.id LIMIT 10""").fetchall()
    colleges = db.execute(
        "SELECT college, COUNT(*) c FROM students GROUP BY college ORDER BY c DESC LIMIT 10").fetchall()
    return render_template("leaderboard.html", people=people, colleges=colleges, count=total(db), goal=GOAL)


# ----------------------------------------------------------------- WhatsApp bot (simulated)
BOT_SESSIONS = {}
YEARS = {"1": "Final year (4th)", "2": "3rd year", "3": "Other / Graduate"}


def bot_reply(sid, text):
    db = get_db()
    text = (text or "").strip()
    up = text.upper()
    st = BOT_SESSIONS.setdefault(sid, {"step": "idle", "data": {}})

    if up.startswith("STATUS"):
        parts = up.split()
        if len(parts) < 2:
            return ["Send STATUS followed by your code, e.g. *STATUS PRIYA123*"]
        s = db.execute("SELECT * FROM students WHERE ref_code=?", (parts[1],)).fetchone()
        if not s:
            return ["I couldn't find that code 🤔"]
        n = db.execute("SELECT COUNT(*) c FROM students WHERE referred_by=?", (s["ref_code"],)).fetchone()["c"]
        nxt = next((t for t in TIERS if t[0] > n), None)
        msg = f"Hi {s['name'].split()[0]}! You've brought *{n}* friend(s) so far. 🎉"
        if nxt:
            msg += f"\n{nxt[0]-n} more to unlock *{nxt[1]}*."
        return [msg]
    if up == "HELP":
        return ["Commands:\n• *JOIN* – register for the workshop\n• *STATUS <code>* – check your referrals\n• *ABOUT* – what is this workshop?"]
    if up == "ABOUT":
        return [f"*{WORKSHOP['title']}*\n{WORKSHOP['when']}\n✅ {WORKSHOP['outcome']}\n✅ Free · certificate of participation\nType *JOIN* to grab a seat."]
    if up.startswith("JOIN") or up.startswith("HI") or up.startswith("HELLO"):
        ref = up.split()[1] if len(up.split()) > 1 and up.startswith("JOIN") else None
        st.update(step="name", data={"ref": ref})
        return [f"👋 Welcome! Free live workshop: *{WORKSHOP['title']}*.\n{WORKSHOP['when']}",
                "Let's get you registered in 4 quick questions.\n\n1/4 What's your *full name*?"]

    step, d = st["step"], st["data"]
    if step == "name":
        if len(text) < 2:
            return ["Please type your full name 🙂"]
        d["name"] = text.title(); st["step"] = "college"
        return [f"Nice to meet you, {d['name'].split()[0]}! 2/4 Which *college* are you from?"]
    if step == "college":
        d["college"] = text; st["step"] = "year"
        return ["3/4 Which year are you in?\n*1* – Final year\n*2* – 3rd year\n*3* – Other"]
    if step == "year":
        if text not in YEARS:
            return ["Please reply with 1, 2 or 3"]
        d["year"] = YEARS[text]; st["step"] = "email"
        extra = "" if text == "1" else "\n(This one's designed for final-years, but you're welcome!)"
        return ["4/4 Your *email* (we'll send the joining link here)" + extra]
    if step == "email":
        if not re.match(r"[^@\s]+@[^@\s]+\.[^@\s]+$", text):
            return ["That email doesn't look right — try again?"]
        s, created = register_student(db, d["name"], text, sid, d["college"], "", d["year"], d.get("ref"), "bot")
        st.update(step="idle", data={})
        link = url_for("landing", ref=s["ref_code"], src="referral", _external=True)
        head = "✅ You're registered!" if created else "You were already registered 😊"
        return [f"{head} Seat #{total(db)} of {GOAL}.\nYour referral code: *{s['ref_code']}*",
                f"Bring friends, unlock rewards 🎁\n• 1 friend → AI Prompt Pack\n• 3 → Community Builder badge\n• 5 → 1:1 project review\n\nForward this to your class group 👇\n{link}",
                f"Track progress anytime: send *STATUS {s['ref_code']}*"]
    return ["Hi! Type *JOIN* to register for the free AI workshop, or *HELP* for options."]


@app.route("/whatsapp")
def whatsapp():
    return render_template("whatsapp.html", sid="+91 9" + "".join(random.choices(string.digits, k=9)),
                           ref=request.args.get("ref", ""))


@app.post("/api/bot")
def api_bot():
    data = request.get_json(force=True)
    return jsonify(replies=bot_reply(data.get("sid", "anon"), data.get("message", "")))


# ----------------------------------------------------------------- growth dashboard
@app.route("/admin")
def admin():
    db = get_db()
    start = campaign_start(db)
    rows = db.execute("SELECT * FROM students ORDER BY created_at").fetchall()
    n = len(rows)

    # daily + cumulative vs. target pace
    days = [start + timedelta(days=i) for i in range(CAMPAIGN_DAYS)]
    per_day = {d: 0 for d in days}
    for r in rows:
        d = datetime.fromisoformat(r["created_at"]).date()
        if d in per_day:
            per_day[d] += 1
    cum, running = [], 0
    for d in days:
        running += per_day[d]
        cum.append(running)
    target_curve = [round(GOAL * (i + 1) / CAMPAIGN_DAYS) for i in range(CAMPAIGN_DAYS)]

    today_idx = min(max((date.today() - start).days, 0), CAMPAIGN_DAYS - 1)
    days_elapsed = today_idx + 1
    pace = n / days_elapsed if days_elapsed else 0
    projected = round(pace * CAMPAIGN_DAYS) if days_elapsed < CAMPAIGN_DAYS else n

    by_src = {k: 0 for k in SOURCES}
    for r in rows:
        by_src[r["source"]] = by_src.get(r["source"], 0) + 1
    referred = sum(1 for r in rows if r["referred_by"])
    sharers = db.execute("SELECT COUNT(DISTINCT referred_by) c FROM students WHERE referred_by IS NOT NULL").fetchone()["c"]
    k_factor = round(referred / max(n - referred, 1), 2)  # new people brought per organically-acquired person
    final_year = sum(1 for r in rows if (r["year"] or "").startswith("Final"))
    colleges = db.execute("SELECT college, COUNT(*) c FROM students GROUP BY college ORDER BY c DESC LIMIT 8").fetchall()
    recent = rows[-12:][::-1]

    # simple rule-based "what to do next" recommendation
    best_src = max(by_src, key=by_src.get) if n else "whatsapp"
    gap = target_curve[today_idx] - cum[today_idx]
    if n >= GOAL:
        advice = "Goal hit 🎯 Shift effort to attendance: send reminders on Day 7 and 1 hour before the workshop."
    elif gap > 0:
        advice = (f"Behind target by {gap} today. Double down on '{SOURCES[best_src]}' (your best channel) and "
                  f"push the leaderboard — {sharers} students are already sharing.")
    else:
        advice = f"Ahead of pace by {-gap}. Keep the cadence; start collecting testimonials for Day 5 social proof."

    return render_template(
        "admin.html", n=n, goal=GOAL, pct=min(100, round(100 * n / GOAL)),
        labels=[f"Day {i+1}" for i in range(CAMPAIGN_DAYS)], daily=[per_day[d] for d in days], cum=cum,
        target=target_curve, by_src=[(SOURCES[k], v) for k, v in by_src.items()], k_factor=k_factor,
        referred=referred, sharers=sharers, projected=projected, colleges=colleges, recent=recent,
        final_year_pct=round(100 * final_year / n) if n else 0, today=today_idx + 1, advice=advice,
        n_colleges=db.execute("SELECT COUNT(DISTINCT college) c FROM students").fetchone()["c"])


@app.route("/admin/export.csv")
def export_csv():
    rows = get_db().execute("SELECT * FROM students ORDER BY id").fetchall()
    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(rows[0].keys() if rows else ["empty"])
    for r in rows:
        w.writerow(list(r))
    return Response(buf.getvalue(), mimetype="text/csv",
                    headers={"Content-Disposition": "attachment; filename=registrations.csv"})


# ----------------------------------------------------------------- message kit
KIT = {
    "whatsapp": ("WhatsApp class group (ambassador)",
                 "Hi everyone 👋 {college} folks — NxtWave is running a FREE live workshop: *{title}*.\n"
                 "In 60 minutes you build a working AI project and get a live link for your resume — "
                 "useful for placement interviews this season.\n🗓 {when}\nRegister (60 sec): {link}"),
    "club": ("Coding club / placement cell (email)",
             "Subject: Free 60-min AI project workshop for {college} final-years\n\n"
             "Dear {college} team,\n\nNxtWave is hosting a free live session, \"{title}\" ({when}). "
             "Students leave with a deployed AI project they can show recruiters. "
             "Could you share it with your final-year students? Registration link: {link}\n\n"
             "Happy to send a poster for your notice board.\n\nThanks!"),
    "linkedin": ("LinkedIn / Instagram post",
                 "Placement season tip: \"Tell me about an AI project you built\" is now a common interview question.\n\n"
                 "If you don't have one yet — NxtWave's free live workshop \"{title}\" gets you from zero to a "
                 "working, deployed project in 60 minutes.\n{when}\n👉 {link}\n#placements #AI #engineering"),
    "reminder": ("Day-7 reminder (registered students)",
                 "⏰ Tomorrow! *{title}* — {when}.\nKeep a laptop ready; no setup needed. "
                 "Bring a friend from {college} — share {link}"),
}


@app.route("/admin/messages")
def messages():
    college = request.args.get("college", "your college")
    ch = request.args.get("channel", "whatsapp")
    ch = ch if ch in KIT else "whatsapp"
    link = url_for("landing", src=ch if ch in SOURCES else "direct", _external=True)
    text = KIT[ch][1].format(college=college, title=WORKSHOP["title"], when=WORKSHOP["when"], link=link)
    return render_template("messages.html", kit=KIT, ch=ch, college=college, text=text)


init_db()  # also runs under gunicorn when deployed

if __name__ == "__main__":
    app.run(debug=True)
