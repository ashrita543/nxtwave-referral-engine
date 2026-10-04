# NxtWave Growth Challenge: Submission Guide

This guide covers all four things the form asks for, plus a checklist.

| # | Item asked for | What you submit |
|---|---|---|
| 1 | Growth Plan (max 5 slides) | The 5-slide deck. Download it as **PDF** and upload or link it |
| 2 | Working Asset | The live Render link (see README), or a GitHub link plus a screen-recorded demo |
| 3 | AI + Learning Notes | Section A below. Paste it into the form or save it as a PDF |
| 4 | 3-minute video | Script in Section B. Record with Loom or OBS and submit an unlisted YouTube or Drive link |

> **Make it yours.** The notes and script below describe the decisions behind this plan. Before you submit, rewrite them in your own words. If your own process was different (for example, you asked something else or changed something else), write what really happened. Interviewers will ask about it.

---

## A. AI + Learning Notes (What I asked → What AI suggested → What I changed)

**Example 1: Choosing channels**
- **I asked:** "Give me a plan to get 500 engineering students to register for a free AI workshop with ₹2,000 in 7 days."
- **AI suggested:** About 8 channels: Instagram and LinkedIn ads, YouTube micro-influencers, college posters, a pre-webinar, email blasts, WhatsApp groups, referral contests and Telegram.
- **What I changed:** I cut it to 3 prioritised channels: campus ambassadors in WhatsApp groups, a referral loop, and clubs and placement cells. With 7 days and ₹2,000, spreading effort across 8 channels means doing none of them well. ₹2,000 of ads buys tens of sign-ups, not hundreds. Final-year students actually read their class WhatsApp groups, so I put the effort there.

**Example 2: What to build**
- **I asked:** "Build me a landing page for this workshop."
- **AI suggested:** A landing page with a countdown timer, testimonials and an FAQ.
- **What I changed:** A landing page only converts traffic; it doesn't create any. My plan depends on people sharing, so I built a referral engine instead. Every registrant gets a personal link, a WhatsApp share button and a reward ladder. I added a WhatsApp bot flow, because students in a group chat don't want to open a form, and a growth dashboard so I can see which channel is working by Day 3.

**Example 3: Referral rewards (rejected)**
- **I asked:** "How should I reward students for referrals?"
- **AI suggested:** Pay ₹10 cash per successful referral.
- **What I changed:** I rejected it. At 500 registrations that's up to ₹5,000, more than double the budget, and paying per sign-up invites fake registrations. I switched to tiered rewards that cost nothing (prompt pack at 1 referral, badge and shout-out at 3, 1:1 project review at 5), plus top-3 leaderboard prizes of ₹300/₹200/₹100. I also made the system reject duplicate emails.

*(Optional 4th)* **WhatsApp integration:** AI suggested wiring up the real WhatsApp Business API straight away. I built a simulator with the same conversation logic instead, because Meta business verification can take days and the challenge is a 48-hour simulation. In the code, `bot_reply()` would plug into Interakt, WATI or Twilio unchanged.

---

## B. 3-Minute Video Script (about 430 words)

Practise it twice. Use screen share: the deck for the first half, the app for the second half.

**[0:00–0:20] Hook (camera on, or the deck's first slide)**
"Hi, I'm ______. The challenge was to get 500 final-year engineering students to register for a free AI workshop in 7 days, with only ₹2,000. My core bet is that students register when a classmate invites them, not when an ad does. So I built a plan, and a tool, that turns every registrant into a distributor."

**[0:20–0:50] The student (slide 1)**
"I'm targeting final-year B.Tech students in CSE, IT, AI&DS and ECE at Tier-2 and Tier-3 colleges. They're in placement season, and interviewers now ask 'Have you built anything with AI?' They don't have time for a 6-week course, but they have 60 minutes. So the promise is concrete: leave with a live AI project link for your resume."

**[0:50–1:30] The plan (slides 2–4)**
"I chose three channels, in priority order. First, 20 campus ambassadors who post in their class, department and hostel WhatsApp groups. That's about 250 registrations. Second, a referral loop where every registrant gets a link and climbs a reward ladder. That's about 140. Third, coding clubs and placement cells for credibility, about 100. Together that's around 530, which gives me a buffer. I left out paid ads. The ₹2,000 goes only to prizes for top ambassadors and referrers, plus a ₹400 reserve. On Day 3 I check the dashboard, and if we're under 150, the reserve goes to whichever channel is working."

**[1:30–2:35] Demo (switch to the app)**
"This is what I built, using Python and Flask with AI assistance.
- *(Open /admin)* The growth dashboard. We're on Day 7 at 492 out of 500. It shows pace against target, which channel is bringing students, our viral coefficient, and a recommended next move.
- *(Open /whatsapp, click JOIN)* Students can register without leaving WhatsApp: four questions, and they get a referral code and a share link.
- *(Open the link in a new tab)* When a friend opens it, the page says who invited them. *(Register a friend.)*
- *(Open /me page)* Each student sees their link, a one-tap WhatsApp share, and the rewards they've unlocked.
- *(Open /leaderboard)* The college-vs-college race drives the competition.
- *(Back to /admin, refresh)* And we've crossed 500. The dashboard updates live."

**[2:35–3:00] How I thought (slide 5)**
"My first idea was a landing page with ads. I changed it because a page doesn't bring traffic; people do. AI suggested ₹10 cash per referral, and I rejected it because it would blow the budget and attract fake sign-ups. With 24 more hours, I'd connect the real WhatsApp Business API, add OTP verification, and deploy it publicly. Thank you!"

**Recording tips:** use Loom (free, records screen and face) or OBS. Run `python seed.py` right before recording so the count starts at 492. Zoom the browser to 110–125% so text is readable. Keep it under 3:00.

---

## C. The three "How you thought" questions (if the form asks for them separately)

**1. What changed between your first idea and final solution?**
My first idea was a landing page plus Instagram ads. When I did the math, ₹2,000 of ads couldn't reach 500 students, and a landing page only converts traffic I don't have. The final solution is people-powered: campus ambassadors in WhatsApp groups, plus a referral engine that makes every registrant a distributor. A dashboard checks my assumptions daily, so I can move effort to the best channel by Day 3.

**2. If you had another 24 hours, what would you improve?**
(1) Connect the bot to the real WhatsApp Business API (Interakt or WATI) so the JOIN flow runs inside WhatsApp. (2) Add OTP verification and disposable-email blocking to stop fake referrals. (3) Use an LLM to generate a personalised outreach message for each college and club. (4) Add attendance nudges, such as reminders 24 hours and 1 hour before the session, because registration isn't attendance.

**3. What did AI suggest that you rejected, and why?**
AI suggested paying ₹10 per referral. I rejected it because it could cost up to ₹5,000, over budget, and paying per sign-up rewards fake registrations rather than real interest. I used non-cash tiered rewards plus small top-3 prizes. I also rejected AI's suggestion to spread across 8 channels, and chose 3 that I could actually execute well in 7 days.

---

## D. Final checklist before submitting
- [ ] Deck: add your name, then download it as PDF (5 slides).
- [ ] App runs locally (`python seed.py` then `python app.py`). Optionally deploy it to Render for a live link.
- [ ] Push the code to GitHub (public repository) and include the link.
- [ ] AI notes (Section A), rewritten in your own words.
- [ ] Video of 3:00 or less, uploaded as unlisted YouTube or a Drive link set to "Anyone with the link".
- [ ] Submit at https://forms.gle/xEtJSgJfeqvnxv8q6 within the 48-hour window.
