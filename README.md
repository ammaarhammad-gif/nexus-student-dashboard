# 🎓 Nexus Student Dashboard

**Nexus** is a futuristic, dark-themed student syllabus manager, study planner, and progress analytics dashboard. Built with Streamlit and cloud-backed by PostgreSQL, it allows multiple students to sign up, log in securely, and track their study progress independently.

![App screenshot placeholder](https://raw.githubusercontent.com/streamlit/streamlit/main/assets/images/logo.png) <!-- Replace with your actual screenshot URL if desired -->

---

## ⚡ Key Features

* **🔑 Secure Multi-User Auth:** Complete login and signup portal with salted password hashing powered by `bcrypt`.
* **📚 Hierarchical Syllabus Tracker:** Organizes study goals into `Subjects ➔ Chapters ➔ Topics ➔ Subtopics`.
* **🧠 Understanding & Focus Indicators:** Tag topics by difficulty level (1–5 scale), flag important sections, and write quick study notes.
* **📊 Visual Statistics:** Dynamic analytics using Plotly charts showing progress breakdowns, subject completion bars, and understanding levels.
* **🗓️ Study Planner & Allocator:**
  * Date-based daily schedule log with estimated durations.
  * Goal tracker with customized targets (Daily, Weekly, Monthly).
  * Allocate specific chapters to custom exam terms (e.g. Mid-Terms, Finals) and watch completion metrics update dynamically.
* **🎨 Glassmorphic Dark UI:** Custom futuristic design, styling, and animations using custom CSS and Outfit/Inter fonts.

---

## 🛠️ Tech Stack

* **Frontend & Framework:** Streamlit
* **Database Backend:** Cloud PostgreSQL (compatible with Supabase, Neon, etc.)
* **Data Visualization:** Plotly, Pandas
* **Security:** Bcrypt (Blowfish cipher hashing)

---

## 🚀 How to Set Up Locally

### 1. Clone the repository
```bash
git clone https://github.com/YOUR_GITHUB_USERNAME/nexus-student-dashboard.git
cd nexus-student-dashboard
```

### 2. Install dependencies
Make sure you have Python 3.9+ installed, then run:
```bash
pip install -r requirements.txt
```

### 3. Connect your PostgreSQL Database
Create a folder named `.streamlit` at the root of the project, and create a `secrets.toml` file inside it with your credentials:
```toml
# .streamlit/secrets.toml
[postgres]
url = "postgresql://your_user:your_password@your_host:5432/your_database"
```
*(You can create a free cloud PostgreSQL database in 1 minute using [Supabase](https://supabase.com) or [Neon](https://neon.tech)).*

### 4. Start the Application
```bash
python -m streamlit run app.py
```
Open [http://localhost:8501](http://localhost:8501) in your browser.

---

## 🌐 How to Deploy to the Cloud (Streamlit Community Cloud)

1. Push your local project folder to your GitHub repository.
2. Sign in to **[Streamlit Community Cloud](https://share.streamlit.io)**.
3. Click **New app**, select your repository, branch (`main`), and set the main file path to `app.py`.
4. Before clicking deploy, open **Advanced settings** -> **Secrets** and paste your database config details:
   ```toml
   [postgres]
   url = "postgresql://your_user:your_password@your_host:5432/your_database"
   ```
5. Click **Deploy!** 🚀
