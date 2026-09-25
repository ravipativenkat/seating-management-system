# Employee Seating Management System

A web app to view and manage office seat assignments, with an AI admin
assistant that lets an administrator type a plain-English instruction
(e.g. *"Move Sarah Johnson to seat B4"*) to reassign an employee's seat.

- **Backend:** Python (Flask + SQLAlchemy + SQLite)
- **AI:** Groq free-tier API (Llama 3.1) — no credit card required
- **Frontend:** Server-rendered HTML + vanilla JS (no build step)
- **Hosting:** Render.com free tier
- **Code hosting:** GitHub (public repo)

Total cost to run this project: **$0**.

---

## 1. Project files

```
seating-management-system/
├── app.py                 # Flask app + all routes/API endpoints
├── models.py               # SQLAlchemy models: Employee, Seat, ActivityLog
├── ai_assistant.py         # Calls Groq API, turns prompt into a JSON action
├── seed_data.py             # Populates sample employees + seats
├── requirements.txt
├── render.yaml              # One-click free deploy config for Render
├── .env.example              # Copy to .env and fill in your Groq key
├── .gitignore
├── README.md
├── templates/
│   ├── base.html
│   ├── index.html           # Public seating map
│   └── admin.html           # Admin panel + AI assistant box
└── static/
    ├── style.css
    └── admin.js
```

---

## 2. Local setup (exact commands)

```bash
# 1. Create the project folder and enter it
mkdir seating-management-system
cd seating-management-system

# (copy all the files from this project into this folder,
#  keeping the same names and the templates/ and static/ subfolders)

# 2. Create and activate a virtual environment
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Create your .env file
cp .env.example .env
# then open .env and paste in your free Groq API key (see step 3 below)

# 5. Seed the database with sample employees and seats
python seed_data.py

# 6. Run the app
python app.py
```

Open **http://127.0.0.1:5000** for the seating map, and
**http://127.0.0.1:5000/admin** for the admin panel with the AI assistant.

---

## 3. Get a free AI API key (Groq)

1. Go to **https://console.groq.com/keys**
2. Sign up (free, no credit card).
3. Click **Create API Key**, copy it.
4. Paste it into your `.env` file as `GROQ_API_KEY=gsk_...`

Groq's free tier is generous and works well for this feature. (Gemini's
free tier or any OpenAI-compatible provider would also work — just swap
the URL/model in `ai_assistant.py`.)

---

## 4. Push the code to GitHub (exact commands)

```bash
cd seating-management-system
git init
git add .
git commit -m "Initial commit: Employee Seating Management System"

# Create a new PUBLIC repo on GitHub first (via github.com/new),
# then link it:
git branch -M main
git remote add origin https://github.com/<your-username>/seating-management-system.git
git push -u origin main
```

`.env` is already in `.gitignore`, so your API key will never be pushed.

---

## 5. Deploy for free (Render.com)

1. Go to **https://dashboard.render.com** and sign up free.
2. Click **New +** → **Web Service** → connect your GitHub repo.
3. Render will detect `render.yaml` automatically. If asked manually, use:
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn app:app`
   - **Plan:** Free
4. Under **Environment**, add:
   - `GROQ_API_KEY` = your Groq key
   - `SECRET_KEY` = any random string
5. Click **Create Web Service**. Render gives you a live URL like
   `https://seating-management-system.onrender.com`.
6. Once deployed, run the seed script once via Render's **Shell** tab:
   ```bash
   python seed_data.py
   ```

(Vercel and Netlify are built for static/serverless sites and need extra
adapter config for a Flask app with a database — Render is the simplest
free option for this kind of app. If you'd rather use Vercel, say so and
I can restructure `app.py` as serverless functions.)

---

## 6. Using the AI Assistant

On `/admin`, type instructions such as:

- `Move Sarah Johnson to seat C3`
- `Assign Alex Kim to B2`
- `Unassign John Smith`
- `Free up seat A1`

The prompt is sent to `/api/ai-assist`, which calls Groq to extract
`{employee, action, seat}` as JSON, then updates the database and logs
the change in the Activity feed at the bottom of the admin panel.

---

## 7. Submitting the assignment

- **GitHub Repository Link:** the `https://github.com/<you>/seating-management-system` URL from step 4
- **Live URL:** the Render URL from step 5
