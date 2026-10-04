# NxtWave Workshop Referral Engine

A working growth asset for the NxtWave Growth Challenge. The goal is to get 500 final-year students registered for **"Build Your First AI Project in 60 Minutes"** in 7 days, on a ₹2,000 budget.

It does more than a landing page. It turns every registrant into a distributor and shows the campaign owner what to do next.

| Page | URL | What it shows |
|---|---|---|
| Registration | `/` | Form that captures who referred the student (`?ref=CODE`) and which channel they came from (`?src=whatsapp`) |
| My referral page | `/me/<code>` | Personal link, one-tap WhatsApp share, friends joined, rank, reward ladder |
| WhatsApp bot | `/whatsapp` | Simulated chat. Type `JOIN` and answer 4 questions to register. `STATUS <code>` shows referral count |
| Leaderboard | `/leaderboard` | Top referrers and the college-vs-college race |
| Growth dashboard | `/admin` | Progress to 500, daily pace vs. target, channel mix, viral coefficient, Day-7 projection, and a "next move" recommendation |
| Message kit | `/admin/messages` | Ready-to-paste messages for WhatsApp groups, clubs, LinkedIn and reminders, each with a tracked link |
| Export | `/admin/export.csv` | All registrations as a CSV file |

## Run it in VS Code (about 5 minutes)

1. Install **Python 3.10+** from python.org. On Windows, tick **"Add Python to PATH"** during setup.
2. Unzip this folder. In VS Code, go to **File → Open Folder** and pick `nxtwave-referral-engine`.
3. Open a terminal (**Terminal → New Terminal**) and run:

```bash
# create and activate a virtual environment
python -m venv .venv
# Windows:
.venv\Scripts\activate
# Mac/Linux:
source .venv/bin/activate

pip install flask
python seed.py        # loads a simulated 7-day campaign (492 fake registrations)
python app.py         # starts the server
```

4. Open **http://127.0.0.1:5000** in your browser.

Useful commands:
- `python seed.py --empty` starts with an empty database.
- `python seed.py 300` loads a different number of simulated registrations.
- A demo student is already loaded: **http://127.0.0.1:5000/me/PRIYA001**
- Stop the server with `Ctrl + C`.

> If `python` doesn't work, try `py` (Windows) or `python3` (Mac/Linux).

## Demo flow for the video (pushes the count past 500 live)

1. Open `/admin`. It shows **492 / 500** on Day 7 and the "Next move" recommendation.
2. Open `/me/PRIYA001` to show a student's referral page, share button and reward ladder.
3. Open `/whatsapp`, click **JOIN** and register as a new student through the chat.
4. Copy the referral link the bot gives you and open it in a new tab. The banner says "X invited you". Register 2–3 friends with any fake details.
5. Go back to `/admin` and refresh. The count has crossed 500, the channel bars have moved, and the recommendation has changed.
6. Open `/leaderboard` and `/admin/messages`.

## Get a live link (optional, free, about 10 minutes)

The form asks for a "Live link / prototype / demo". If you don't deploy, a screen-recorded demo is enough. To deploy:

1. Push this folder to a new **GitHub** repository. `campaign.db` is already excluded by `.gitignore`.
2. Go to **render.com**, then **New → Web Service**, and connect the repository.
3. Use these settings:
   - Build command: `pip install -r requirements.txt && python seed.py`
   - Start command: `gunicorn app:app`
   - Instance type: **Free**
4. Render gives you a link like `https://nxtwave-referral.onrender.com`. Submit that link.

Note: on Render's free tier the SQLite data resets whenever the service restarts or redeploys. That's fine for a demo.

## How it would go to production
- **WhatsApp:** `bot_reply()` is the conversation logic. Connect it to the WhatsApp Business API through Interakt, WATI or Twilio, which send messages to a webhook. The bot logic stays the same.
- **Database:** move from SQLite to Postgres.
- **Fraud:** add OTP verification and block disposable email domains.
- **Admin:** put a login in front of the `/admin` pages.

## Files
```
app.py            all routes, bot logic and dashboard metrics
seed.py           generates the simulated campaign data
templates/        HTML pages (Jinja)
static/style.css  styling
static/chart.umd.js  Chart.js (bundled so charts work offline)
```
