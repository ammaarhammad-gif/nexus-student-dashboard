"""
ai_service.py — Production-Grade Nexus AI Service Abstraction Layer & Context Bridge.

Supports:
- Multi-Provider LLM Integration (Google Gemini, OpenAI, Groq, Anthropic) via direct REST API
- Server-side API key management via st.secrets, os.environ, or secure session overrides
- Authorized Student Context Assembly across all 8 Nexus data domains:
  (Syllabus, Understanding, Exams, Tasks, Focus Sessions, Spaced Repetitions, Quizzes, Mistakes)
- 7 Core AI Capabilities:
  1. Daily Recommendations & Blueprint
  2. Concept Mentor & Multi-Style Feynman Explainer
  3. Adaptive AI Quiz Generation
  4. Intelligent Study Planner
  5. Deep Progress & Velocity Diagnostics
  6. Spaced Revision Optimization
  7. Mistake Vault Root-Cause Analysis
- Graceful Unconfigured State Handling with Zero Fake Hardcoding
"""

import os
import json
import datetime
import requests
import streamlit as st
from models import (
    get_user_profile,
    get_overall_stats,
    get_all_subjects_with_stats,
    get_chapters_for_subject,
    get_topics_for_chapter,
    get_active_upcoming_terms,
    get_daily_plans,
    get_study_sessions,
    get_revision_queue,
    get_due_revisions,
    get_quiz_history,
    get_all_mistakes,
    get_mistake_analytics,
    get_recall_stats,
    calculate_exam_readiness_score,
    get_top_nexus_priorities,
    get_all_formulas,
    get_connection
)
import psycopg2.extras


# ══════════════════════════════════════════════
# AUTHORIZED NEXUS CONTEXT BUILDER
# ══════════════════════════════════════════════

class NexusContextBuilder:
    """
    Assembles authorized student data into structured, high-signal context
    for LLM prompt engineering without exposing sensitive auth credentials.
    """

    @staticmethod
    def get_student_profile(user_id: int) -> dict:
        profile = get_user_profile(user_id)
        return {
            "name": profile.get("name", "Student"),
            "class_name": profile.get("class_name", "Class 10"),
            "board": profile.get("board", "CBSE"),
            "academic_year": profile.get("academic_year", "")
        }

    @staticmethod
    def get_syllabus_context(user_id: int) -> dict:
        stats = get_overall_stats(user_id)
        subjects = get_all_subjects_with_stats(user_id)
        
        subj_summary = []
        for s in subjects:
            subj_summary.append({
                "subject_name": s["name"],
                "chapters_count": s["total_chapters"],
                "topics_count": s["total_topics"],
                "completed_topics": s["completed"],
                "percent_completed": s["percent_completed"],
                "avg_understanding": s["avg_understanding"]
            })
            
        return {
            "overall_stats": stats,
            "subjects_breakdown": subj_summary
        }

    @staticmethod
    def get_exam_context(user_id: int) -> list:
        terms = get_active_upcoming_terms(user_id)
        today = datetime.date.today()
        exam_list = []
        for t in terms:
            days_left = None
            if t.get("exam_date"):
                try:
                    ex_d = datetime.datetime.strptime(t["exam_date"], "%Y-%m-%d").date()
                    days_left = (ex_d - today).days
                except Exception:
                    pass
            exam_list.append({
                "term_id": t["id"],
                "name": t["name"],
                "exam_date": t.get("exam_date"),
                "days_left": days_left
            })
        return exam_list

    @staticmethod
    def get_weak_and_priority_topics(user_id: int, limit: int = 8) -> list:
        priorities = get_top_nexus_priorities(user_id, limit=limit)
        return [{
            "topic_name": p["topic_name"],
            "subject_name": p["subject_name"],
            "chapter_name": p["chapter_name"],
            "priority_tier": p["tier"],
            "reasons": p["reasons"]
        } for p in priorities]

    @staticmethod
    def get_mistake_vault_context(user_id: int) -> dict:
        analytics = get_mistake_analytics(user_id)
        unreviewed = get_all_mistakes(user_id, is_reviewed=False)
        return {
            "total_mistakes": analytics.get("total", 0),
            "unreviewed_count": analytics.get("unreviewed", 0),
            "reviewed_count": analytics.get("reviewed", 0),
            "error_distribution": analytics.get("breakdown", []),
            "recent_unreviewed_samples": [{
                "question": m["question"],
                "your_answer": m.get("your_answer"),
                "correct_answer": m.get("correct_answer"),
                "mistake_type": m.get("mistake_type"),
                "subject_name": m.get("subject_name"),
                "prevention_strategy": m.get("prevention_strategy")
            } for m in unreviewed[:5]]
        }

    @staticmethod
    def get_revision_queue_context(user_id: int) -> dict:
        q = get_revision_queue(user_id)
        overdue = q.get("overdue", [])
        due_today = q.get("due_today", [])
        due_week = q.get("due_this_week", [])
        total_active = len(overdue) + len(due_today) + len(due_week)

        return {
            "total_active_revisions": total_active,
            "overdue_count": len(overdue),
            "due_today_count": len(due_today),
            "overdue_items": [{
                "topic_name": r.get("topic_name") or r.get("item_name"),
                "subject_name": r.get("subject_name"),
                "due_date": str(r.get("next_revision_date") or r.get("due_date", "")),
                "interval_days": r.get("interval_days")
            } for r in overdue[:5]],
            "due_today_items": [{
                "topic_name": r.get("topic_name") or r.get("item_name"),
                "subject_name": r.get("subject_name"),
                "interval_days": r.get("interval_days")
            } for r in due_today[:5]]
        }

    @staticmethod
    def get_assessment_context(user_id: int) -> dict:
        quizzes = get_quiz_history(user_id, limit=6)
        recall_stats = get_recall_stats(user_id)
        readiness = calculate_exam_readiness_score(user_id)
        
        avg_quiz_acc = (sum(q["accuracy_pct"] for q in quizzes) / len(quizzes)) if quizzes else 0
        return {
            "exam_readiness_score": readiness.get("readiness_score", 0),
            "readiness_factors": readiness.get("factors", {}),
            "recent_quizzes_count": len(quizzes),
            "avg_quiz_accuracy": round(avg_quiz_acc, 1),
            "active_recall_sessions": recall_stats.get("total_sessions", 0),
            "active_recall_avg_rating": recall_stats.get("avg_score", 0)
        }

    @staticmethod
    def get_study_habits_context(user_id: int) -> dict:
        today_str = datetime.date.today().strftime("%Y-%m-%d")
        plans = get_daily_plans(user_id, today_str)
        sessions = get_study_sessions(user_id, limit=7)
        
        total_recent_mins = sum(s.get("duration_minutes", 0) for s in sessions)
        return {
            "today_tasks": [{
                "task": p.get("task") or p.get("description", ""),
                "subject_name": p.get("subject_name"),
                "is_completed": bool(p.get("is_completed"))
            } for p in plans],
            "recent_7_sessions_minutes": total_recent_mins
        }

    @classmethod
    def assemble_full_context(cls, user_id: int) -> dict:
        """Assembles comprehensive authorized student context into a clean JSON-serializable dictionary."""
        return {
            "profile": cls.get_student_profile(user_id),
            "syllabus": cls.get_syllabus_context(user_id),
            "exams": cls.get_exam_context(user_id),
            "priorities": cls.get_weak_and_priority_topics(user_id),
            "mistakes": cls.get_mistake_vault_context(user_id),
            "revisions": cls.get_revision_queue_context(user_id),
            "assessments": cls.get_assessment_context(user_id),
            "habits": cls.get_study_habits_context(user_id)
        }


# ══════════════════════════════════════════════
# CLEAN AI SERVICE ABSTRACTION LAYER
# ══════════════════════════════════════════════

class NexusAIService:
    """
    Clean AI Service interacting with Google Gemini, OpenAI, Groq, or Anthropic.
    Ensures safe server-side API key handling, prompt structuring, and graceful fallback.
    """

    def __init__(self):
        self.provider = None
        self.api_key = None
        self.model_name = None
        self._detect_provider_and_key()

    def _detect_provider_and_key(self):
        """Auto-detects active LLM provider from st.secrets, os.environ, or session override."""
        # 1. Check Streamlit Session override (allows student/admin to test custom key in UI securely)
        if "nexus_custom_ai_key" in st.session_state and st.session_state["nexus_custom_ai_key"].strip():
            self.api_key = st.session_state["nexus_custom_ai_key"].strip()
            self.provider = st.session_state.get("nexus_custom_ai_provider", "gemini").lower()
            self.model_name = st.session_state.get("nexus_custom_ai_model") or self._default_model_for_provider(self.provider)
            return

        # 2. Check Streamlit secrets
        try:
            if hasattr(st, "secrets"):
                if "GEMINI_API_KEY" in st.secrets:
                    self.provider = "gemini"
                    self.api_key = st.secrets["GEMINI_API_KEY"]
                    self.model_name = "gemini-2.5-flash"
                    return
                elif "OPENAI_API_KEY" in st.secrets:
                    self.provider = "openai"
                    self.api_key = st.secrets["OPENAI_API_KEY"]
                    self.model_name = "gpt-4o-mini"
                    return
                elif "GROQ_API_KEY" in st.secrets:
                    self.provider = "groq"
                    self.api_key = st.secrets["GROQ_API_KEY"]
                    self.model_name = "llama-3.3-70b-versatile"
                    return
                elif "ANTHROPIC_API_KEY" in st.secrets:
                    self.provider = "anthropic"
                    self.api_key = st.secrets["ANTHROPIC_API_KEY"]
                    self.model_name = "claude-3-5-sonnet-20241022"
                    return
        except Exception:
            pass

        # 3. Check Environment Variables
        if os.environ.get("GEMINI_API_KEY"):
            self.provider = "gemini"
            self.api_key = os.environ.get("GEMINI_API_KEY")
            self.model_name = "gemini-2.5-flash"
        elif os.environ.get("OPENAI_API_KEY"):
            self.provider = "openai"
            self.api_key = os.environ.get("OPENAI_API_KEY")
            self.model_name = "gpt-4o-mini"
        elif os.environ.get("GROQ_API_KEY"):
            self.provider = "groq"
            self.api_key = os.environ.get("GROQ_API_KEY")
            self.model_name = "llama-3.3-70b-versatile"
        elif os.environ.get("ANTHROPIC_API_KEY"):
            self.provider = "anthropic"
            self.api_key = os.environ.get("ANTHROPIC_API_KEY")
            self.model_name = "claude-3-5-sonnet-20241022"

    def _default_model_for_provider(self, provider: str) -> str:
        defaults = {
            "gemini": "gemini-2.5-flash",
            "openai": "gpt-4o-mini",
            "groq": "llama-3.3-70b-versatile",
            "anthropic": "claude-3-5-sonnet-20241022"
        }
        return defaults.get(provider.lower(), "gemini-2.5-flash")

    def get_status(self) -> dict:
        """Returns provider configuration status and masked API key info."""
        self._detect_provider_and_key()
        is_conf = bool(self.api_key and self.provider)
        masked_key = ""
        if self.api_key:
            if len(self.api_key) > 8:
                masked_key = f"{self.api_key[:4]}...{self.api_key[-4:]}"
            else:
                masked_key = "****"

        return {
            "is_configured": is_conf,
            "provider": self.provider or "None",
            "model": self.model_name or "None",
            "masked_key": masked_key,
            "setup_guide": """
### 🔌 How to Configure Your Nexus AI Provider:

Add your API key to **`.streamlit/secrets.toml`** (locally) or in your **Streamlit Cloud Dashboard Secrets**:

```toml
# .streamlit/secrets.toml
GEMINI_API_KEY = "AIzaSy..."

# OR for OpenAI:
# OPENAI_API_KEY = "sk-..."

# OR for Groq:
# GROQ_API_KEY = "gsk_..."
```
*(Or enter your key temporarily in the AI Command Center configuration box).*
"""
        }

    def _call_llm(self, system_instruction: str, user_prompt: str, temperature: float = 0.4) -> str:
        """Dispatches prompt to the configured LLM provider via REST API."""
        self._detect_provider_and_key()
        if not self.api_key or not self.provider:
            raise RuntimeError("NO_AI_CONFIGURED: AI Provider is not configured. Please set your API key in secrets.toml or via the configuration panel.")

        prov = self.provider.lower()

        # ── 1. GOOGLE GEMINI ──
        if prov == "gemini":
            model = self.model_name or "gemini-2.5-flash"
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={self.api_key}"
            payload = {
                "contents": [{
                    "role": "user",
                    "parts": [{"text": f"{system_instruction}\n\n{user_prompt}"}]
                }],
                "generationConfig": {
                    "temperature": temperature,
                    "maxOutputTokens": 2500
                }
            }
            resp = requests.post(url, json=payload, headers={"Content-Type": "application/json"}, timeout=45)
            if resp.status_code != 200:
                raise RuntimeError(f"Gemini API Error ({resp.status_code}): {resp.text}")
            data = resp.json()
            try:
                return data["candidates"][0]["content"]["parts"][0]["text"]
            except Exception as e:
                raise RuntimeError(f"Failed to parse Gemini response: {data}") from e

        # ── 2. OPENAI ──
        elif prov == "openai":
            model = self.model_name or "gpt-4o-mini"
            url = "https://api.openai.com/v1/chat/completions"
            payload = {
                "model": model,
                "messages": [
                    {"role": "system", "content": system_instruction},
                    {"role": "user", "content": user_prompt}
                ],
                "temperature": temperature,
                "max_tokens": 2500
            }
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            resp = requests.post(url, json=payload, headers=headers, timeout=45)
            if resp.status_code != 200:
                raise RuntimeError(f"OpenAI API Error ({resp.status_code}): {resp.text}")
            data = resp.json()
            return data["choices"][0]["message"]["content"]

        # ── 3. GROQ ──
        elif prov == "groq":
            model = self.model_name or "llama-3.3-70b-versatile"
            url = "https://api.groq.com/openai/v1/chat/completions"
            payload = {
                "model": model,
                "messages": [
                    {"role": "system", "content": system_instruction},
                    {"role": "user", "content": user_prompt}
                ],
                "temperature": temperature,
                "max_tokens": 2500
            }
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            resp = requests.post(url, json=payload, headers=headers, timeout=45)
            if resp.status_code != 200:
                raise RuntimeError(f"Groq API Error ({resp.status_code}): {resp.text}")
            data = resp.json()
            return data["choices"][0]["message"]["content"]

        # ── 4. ANTHROPIC ──
        elif prov == "anthropic":
            model = self.model_name or "claude-3-5-sonnet-20241022"
            url = "https://api.anthropic.com/v1/messages"
            payload = {
                "model": model,
                "system": system_instruction,
                "messages": [
                    {"role": "user", "content": user_prompt}
                ],
                "max_tokens": 2500,
                "temperature": temperature
            }
            headers = {
                "x-api-key": self.api_key,
                "anthropic-version": "2023-06-01",
                "Content-Type": "application/json"
            }
            resp = requests.post(url, json=payload, headers=headers, timeout=45)
            if resp.status_code != 200:
                raise RuntimeError(f"Anthropic API Error ({resp.status_code}): {resp.text}")
            data = resp.json()
            return data["content"][0]["text"]

        else:
            raise RuntimeError(f"Unsupported AI Provider '{self.provider}'. Supported: gemini, openai, groq, anthropic.")

    # ══════════════════════════════════════════════════════════
    # CAPABILITY 1: DAILY RECOMMENDATIONS & BLUEPRINT
    # ══════════════════════════════════════════════════════════
    def generate_daily_recommendations(self, user_id: int) -> dict:
        """Generates an intelligent daily study blueprint tailored to pending exams, weak topics, and overdue revisions."""
        context = NexusContextBuilder.assemble_full_context(user_id)
        
        system_prompt = """
You are the Nexus Cognitive AI Academic Advisor, specializing in ICSE and CBSE student performance optimization.
Analyze the student's authorized syllabus coverage, exam deadlines, spaced repetition queue, mistake vault, and study habits.
Generate a structured, motivating Daily Study Blueprint in clean Markdown with:
1. 🎯 **Executive Priority Summary**: 1-2 sentences identifying today's critical bottleneck.
2. ⚡ **Top 3 Actionable Study Blocks**: Exact topics/tasks with recommended focus duration (e.g. 25m, 50m) and specific study methodology (e.g. active recall, numerical derivation, revision).
3. 🔄 **Spaced Repetition Alert**: Overdue topics requiring urgent reinforcement to prevent forgetting curve decay.
4. ❌ **Mistake Prevention Rule of the Day**: A golden rule addressing their most common mistake category.
5. 💡 **Momentum Quote & Exam Countdown Reminder**.
Be crisp, structured, and pedagogical. Avoid generic fluff.
"""
        user_prompt = f"Student Data Context:\n```json\n{json.dumps(context, indent=2)}\n```"
        
        response_text = self._call_llm(system_prompt, user_prompt, temperature=0.3)
        return {
            "status": "success",
            "content": response_text,
            "generated_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        }

    # ══════════════════════════════════════════════════════════
    # CAPABILITY 2: CONCEPT MENTOR & FEYNMAN EXPLAINER
    # ══════════════════════════════════════════════════════════
    def generate_explanation(self, user_id: int, topic_id: int, style: str = "Feynman Technique", student_query: str = "") -> dict:
        """Generates deep multi-level conceptual explanations for any topic in the syllabus."""
        conn = get_connection()
        topic_name = "Topic"
        chapter_name = "Chapter"
        subject_name = "Subject"
        try:
            with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                cursor.execute("""
                    SELECT t.name as topic_name, c.name as chapter_name, s.name as subject_name
                    FROM topics t
                    JOIN chapters c ON t.chapter_id = c.id
                    JOIN subjects s ON c.subject_id = s.id
                    WHERE t.id = %s AND t.user_id = %s
                """, (topic_id, user_id))
                row = cursor.fetchone()
                if row:
                    topic_name = row["topic_name"]
                    chapter_name = row["chapter_name"]
                    subject_name = row["subject_name"]
        finally:
            conn.close()

        profile = NexusContextBuilder.get_student_profile(user_id)
        all_formulas = get_all_formulas(user_id)
        matched_formulas = [f["formula_latex"] for f in all_formulas if f.get("topic_id") == topic_id or f.get("title", "").lower() in topic_name.lower()]

        system_prompt = f"""
You are the Nexus AI Concept Mentor for {profile['board']} ({profile['class_name']}).
Your goal is to explain **'{topic_name}'** (Chapter: {chapter_name}, Subject: {subject_name}) using the style: **{style}**.

Explanation Style Rules:
- **Feynman Technique**: Explain using plain, intuitive language and relatable real-world analogies without jargon. Break down *why* it works from first principles.
- **Board Exam Derivation**: Step-by-step mathematical/theoretical derivation, standard statements, formal definitions, sign conventions, and diagram instructions.
- **Visual Analogy**: High-impact mental model and physical analogies that make the concept unforgettable.
- **Socratic Derivation**: Guided step-by-step questions leading to the fundamental solution.

Include:
1. 🌟 **Core Conceptual Intuition**
2. 📐 **Essential Governing Laws / Formulas / Reactions**
3. ⚠️ **Common Exam Pitfalls & Misconceptions to Avoid**
4. 📝 **Quick 1-Question Check of Understanding**
"""
        user_prompt = f"Topic: {topic_name}\nStudent Specific Question/Confusion: {student_query or 'Provide a complete comprehensive explanation.'}\nFormulas: {matched_formulas}"
        
        explanation_text = self._call_llm(system_prompt, user_prompt, temperature=0.4)
        return {
            "status": "success",
            "topic_name": topic_name,
            "chapter_name": chapter_name,
            "subject_name": subject_name,
            "style": style,
            "content": explanation_text
        }

    # ══════════════════════════════════════════════════════════
    # CAPABILITY 3: ADAPTIVE AI QUIZ GENERATOR
    # ══════════════════════════════════════════════════════════
    def generate_ai_quiz(self, user_id: int, subject_id: int, chapter_id: int = None,
                         topic_id: int = None, difficulty: str = "Adaptive", count: int = 5,
                         focus_prompt: str = "") -> dict:
        """Generates structured multiple-choice questions via LLM that can be directly exported into the Quiz Engine."""
        syllabus_ctx = NexusContextBuilder.get_syllabus_context(user_id)
        profile = NexusContextBuilder.get_student_profile(user_id)
        mistake_ctx = NexusContextBuilder.get_mistake_vault_context(user_id)

        # Retrieve specific target names
        conn = get_connection()
        s_name, c_name, t_name = "General", "", ""
        try:
            with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                if topic_id:
                    cursor.execute("SELECT t.name as t_name, c.name as c_name, s.name as s_name FROM topics t JOIN chapters c ON t.chapter_id = c.id JOIN subjects s ON c.subject_id = s.id WHERE t.id = %s", (topic_id,))
                    r = cursor.fetchone()
                    if r:
                        t_name, c_name, s_name = r["t_name"], r["c_name"], r["s_name"]
                elif chapter_id:
                    cursor.execute("SELECT c.name as c_name, s.name as s_name FROM chapters c JOIN subjects s ON c.subject_id = s.id WHERE c.id = %s", (chapter_id,))
                    r = cursor.fetchone()
                    if r:
                        c_name, s_name = r["c_name"], r["s_name"]
                elif subject_id:
                    cursor.execute("SELECT name as s_name FROM subjects WHERE id = %s", (subject_id,))
                    r = cursor.fetchone()
                    if r:
                        s_name = r["s_name"]
        finally:
            conn.close()

        system_prompt = f"""
You are the Nexus AI Assessment Engine creating a high-rigor multiple-choice quiz for {profile['board']} {profile['class_name']} students.
Subject: {s_name}
Chapter: {c_name or 'General Curriculum'}
Topic: {t_name or 'Key Topics'}
Difficulty: {difficulty}

Generate exactly {count} multiple-choice questions in strict, valid JSON format.
Each question MUST test conceptual understanding, numerical application, or common trap detection rather than simple recall.
Provide 4 plausible options, specify the exact correct answer, and provide a clear pedagogical explanation.

CRITICAL: Return ONLY valid JSON in this exact schema without backticks or markdown wrap:
[
  {{
    "id": 1,
    "question": "Clear problem statement or question text",
    "options": ["Option A", "Option B", "Option C", "Option D"],
    "correct_answer": "Option A",
    "explanation": "Detailed step-by-step reasoning and formula application.",
    "prevention_strategy": "Rule to prevent falling for common distractors."
  }}
]
"""
        user_prompt = f"Focus Areas: {focus_prompt or 'Comprehensive syllabus mastery'}\nRecent Mistake Patterns to Test: {[m['mistake_type'] for m in mistake_ctx.get('error_distribution', [])]}"
        
        raw_resp = self._call_llm(system_prompt, user_prompt, temperature=0.3).strip()
        
        # Clean potential markdown JSON formatting
        if raw_resp.startswith("```"):
            raw_resp = raw_resp.split("\n", 1)[1]
            if raw_resp.endswith("```"):
                raw_resp = raw_resp.rsplit("```", 1)[0]
            raw_resp = raw_resp.strip()

        try:
            questions = json.loads(raw_resp)
        except Exception:
            # Fallback if json parsing fails
            import re
            match = re.search(r'\[\s*\{.*\}\s*\]', raw_resp, re.DOTALL)
            if match:
                questions = json.loads(match.group(0))
            else:
                raise RuntimeError(f"AI generated invalid quiz JSON format. Output:\n{raw_resp[:300]}")

        # Inject topic / subject IDs for Quiz Engine compatibility
        for idx, q in enumerate(questions, 1):
            q["id"] = idx
            q["subject_id"] = subject_id
            q["chapter_id"] = chapter_id
            q["topic_id"] = topic_id

        quiz_title = f"AI Quiz • {t_name or c_name or s_name} ({difficulty})"
        return {
            "status": "success",
            "title": quiz_title,
            "subject_id": subject_id,
            "chapter_id": chapter_id,
            "topic_id": topic_id,
            "difficulty": difficulty,
            "questions": questions
        }

    # ══════════════════════════════════════════════════════════
    # CAPABILITY 4: INTELLIGENT STUDY PLANNER
    # ══════════════════════════════════════════════════════════
    def generate_ai_study_plan(self, user_id: int, term_id: int = None,
                               daily_hours: float = 3.0, target_days: int = 7) -> dict:
        """Generates an intelligent multi-day study schedule allocating topics, revision intervals, and focus blocks."""
        context = NexusContextBuilder.assemble_full_context(user_id)
        
        system_prompt = f"""
You are the Nexus Cognitive Study Planner.
Generate an optimal, realistic {target_days}-day study schedule based on the student's authorized syllabus, weak spots, and exam dates.
Available study time: {daily_hours} hours/day.

CRITICAL: Return ONLY valid JSON in this exact structure without extra conversational text:
{{
  "strategy_summary": "1-2 sentence executive overview of the scheduling strategy",
  "daily_plans": [
    {{
      "day_number": 1,
      "date_label": "Day 1 (Upcoming)",
      "target_focus_hours": {daily_hours},
      "tasks": [
        {{
          "task": "Study Topic Name / Solve numericals",
          "subject_name": "Subject Name",
          "duration_minutes": 50,
          "task_type": "New Topic | Revision | Problem Solving"
        }}
      ],
      "daily_goal": "Key milestone to complete by end of day"
    }}
  ],
  "exam_readiness_impact": "How this plan will improve the student's readiness score"
}}
"""
        user_prompt = f"Student Context:\n```json\n{json.dumps(context, indent=2)}\n```"
        raw_resp = self._call_llm(system_prompt, user_prompt, temperature=0.3).strip()
        
        if raw_resp.startswith("```"):
            raw_resp = raw_resp.split("\n", 1)[1]
            if raw_resp.endswith("```"):
                raw_resp = raw_resp.rsplit("```", 1)[0]
            raw_resp = raw_resp.strip()

        try:
            plan_data = json.loads(raw_resp)
        except Exception:
            import re
            match = re.search(r'\{.*\}', raw_resp, re.DOTALL)
            if match:
                plan_data = json.loads(match.group(0))
            else:
                raise RuntimeError(f"AI generated invalid study plan JSON format. Output:\n{raw_resp[:300]}")

        return {
            "status": "success",
            "plan_data": plan_data
        }

    # ══════════════════════════════════════════════════════════
    # CAPABILITY 5: PROGRESS & VELOCITY DIAGNOSTICS
    # ══════════════════════════════════════════════════════════
    def generate_progress_diagnostic(self, user_id: int) -> dict:
        """Deep diagnostic report analyzing syllabus coverage velocity, bottleneck chapters, and score projections."""
        context = NexusContextBuilder.assemble_full_context(user_id)
        
        system_prompt = """
You are the Nexus Academic Diagnostics AI.
Perform a comprehensive audit of the student's learning analytics.
Generate a structured diagnostic report in clean Markdown covering:
1. 📊 **Curriculum Velocity & Trajectory**: Are they on track for their upcoming exam terms?
2. 🔍 **High-Risk Bottlenecks**: Subjects and chapters with low completion (<40%) or weak understanding (<=2/5).
3. 🏆 **Mastered Strengths**: High-performing areas with strong quiz/active recall retention.
4. 📈 **Exam Readiness Projection**: Concrete roadmap to increase their Exam Readiness Score by +15 to +25 points.
5. 🛡️ **3 Strategic Interventions for this Week**.
"""
        user_prompt = f"Student Analytics Context:\n```json\n{json.dumps(context, indent=2)}\n```"
        diagnostic_text = self._call_llm(system_prompt, user_prompt, temperature=0.3)
        
        return {
            "status": "success",
            "content": diagnostic_text,
            "generated_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        }

    # ══════════════════════════════════════════════════════════
    # CAPABILITY 6: SPACED REVISION OPTIMIZATION
    # ══════════════════════════════════════════════════════════
    def generate_revision_recommendations(self, user_id: int) -> dict:
        """Analyzes forgetting curve intervals and generates a prioritized sequence of topics to review."""
        rev_ctx = NexusContextBuilder.get_revision_queue_context(user_id)
        priorities = NexusContextBuilder.get_weak_and_priority_topics(user_id)
        assessments = NexusContextBuilder.get_assessment_context(user_id)
        
        system_prompt = """
You are the Nexus Spaced Repetition Strategist.
Analyze the student's overdue and upcoming revisions alongside their weak understanding ratings.
Generate a prioritized spaced revision advisory in clean Markdown:
1. 🚨 **Urgent Interventions (Forgetting Curve Risk)**: Topics overdue or due today that must be revised immediately.
2. 🧠 **Optimal Review Techniques**: Specific active recall methods (e.g. flashcard blurt, formula derivation, Feynman teaching) recommended per subject.
3. 📅 **7-Day Spaced Repetition Cadence**: Daily revision schedule balancing new topics vs old reinforcement.
"""
        user_prompt = f"Revision Context:\n```json\n{json.dumps({'revisions': rev_ctx, 'weak_topics': priorities, 'assessments': assessments}, indent=2)}\n```"
        rev_text = self._call_llm(system_prompt, user_prompt, temperature=0.3)
        
        return {
            "status": "success",
            "content": rev_text,
            "generated_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        }

    # ══════════════════════════════════════════════════════════
    # CAPABILITY 7: MISTAKE VAULT ROOT-CAUSE ANALYSIS
    # ══════════════════════════════════════════════════════════
    def generate_mistake_root_cause_analysis(self, user_id: int) -> dict:
        """Diagnoses cognitive error patterns across past quizzes and builds personalized prevention strategies."""
        mistake_ctx = NexusContextBuilder.get_mistake_vault_context(user_id)
        
        system_prompt = """
You are the Nexus Error Pattern Specialist.
Analyze the student's logged mistakes, root-cause distribution (Conceptual, Calculation, Memory, Careless Reading, Formula, Application), and recorded errors.
Generate a targeted Error Diagnostic & Prevention Blueprint in clean Markdown:
1. 🔍 **Dominant Error Trap**: Identify the primary cognitive root cause (e.g. calculation speed, confusing vector vs scalar, sign conventions).
2. 🧩 **Misconception Breakdown**: Analyze specific recorded mistakes and explain *why* the student's brain fell for the wrong answer.
3. 🛡️ **Custom 3-Rule Anti-Mistake Checklist**: Three actionable rules the student must check before submitting exam questions.
4. 🎯 **Targeted Practice Recommendations**.
"""
        user_prompt = f"Mistake Vault Context:\n```json\n{json.dumps(mistake_ctx, indent=2)}\n```"
        mistake_text = self._call_llm(system_prompt, user_prompt, temperature=0.3)
        
        return {
            "status": "success",
            "content": mistake_text,
            "generated_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        }


# Global Singleton
nexus_ai = NexusAIService()
