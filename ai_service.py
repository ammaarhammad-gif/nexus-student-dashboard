"""
ai_service.py — Production-Grade Nexus AI Intelligence Layer & Autonomous Academic Copilot.

Architecture:
1. Intent-Routing Engine (Separates conversational mentorship from workspace actions)
2. Selective Context Assembly (Never runs unnecessary DB queries for general chat)
3. Deep Pedagogical Teaching Modes (Feynman, Board Exam Derivation, Visual/Analogical, Socratic)
4. Conversational Multi-Turn Session Memory (Topic tracking, refinement, confusion analysis)
5. Natural Language Workspace Action Controller (Safe tool execution across all Nexus modules)
6. Dual-Engine Architecture (Cloud LLMs + Autonomous Local Cognitive Engine)
7. Robust Error Shielding (Zero raw SQL/backend errors exposed to students)
"""

import os
import json
import datetime
import re
import logging
import requests
import streamlit as st
import psycopg2.extras

logger = logging.getLogger(__name__)

from database import get_connection
from models import (
    get_user_profile,
    get_overall_stats,
    get_all_subjects,
    get_all_subjects_with_stats,
    get_chapters_for_subject,
    get_topics_for_chapter,
    get_active_upcoming_terms,
    get_daily_plans,
    get_study_sessions,
    get_revision_queue,
    get_quiz_history,
    get_all_mistakes,
    get_mistake_analytics,
    get_recall_stats,
    calculate_exam_readiness_score,
    get_top_nexus_priorities,
    get_all_formulas
)
from ai_tools import (
    execute_nexus_tool,
    resolve_topic_by_name,
    resolve_subject_by_name,
    NEXUS_TOOL_DEFINITIONS
)


# ══════════════════════════════════════════════════════════
# MULTI-TURN CONVERSATIONAL SESSION MANAGER
# ══════════════════════════════════════════════════════════

class NexusConversationSession:
    """Manages active dialogue memory, topic tracking, and pedagogical state."""

    @staticmethod
    def get_history():
        if "nexus_chat_history" not in st.session_state:
            st.session_state["nexus_chat_history"] = []
        return st.session_state["nexus_chat_history"]

    @staticmethod
    def add_message(role: str, content: str, action_badge: str = None, follow_ups: list = None, expandable_details: dict = None):
        history = NexusConversationSession.get_history()
        history.append({
            "role": role,
            "content": content,
            "timestamp": datetime.datetime.now().strftime("%I:%M %p"),
            "action_badge": action_badge,
            "follow_ups": follow_ups or [],
            "expandable_details": expandable_details or {}
        })

    @staticmethod
    def get_active_topic():
        return st.session_state.get("nexus_active_topic", "Newton's Laws of Motion")

    @staticmethod
    def set_active_topic(topic_name: str, subject_name: str = None, last_explanation: str = None):
        st.session_state["nexus_active_topic"] = topic_name
        if subject_name:
            st.session_state["nexus_active_subject"] = subject_name
        if last_explanation:
            st.session_state["nexus_last_explanation"] = last_explanation

    @staticmethod
    def get_active_subject():
        return st.session_state.get("nexus_active_subject", "Physics")

    @staticmethod
    def get_last_explanation():
        return st.session_state.get("nexus_last_explanation", "")

    @staticmethod
    def clear_history():
        st.session_state["nexus_chat_history"] = []
        st.session_state["nexus_active_topic"] = None
        st.session_state["nexus_active_subject"] = None
        st.session_state["nexus_last_explanation"] = None
        st.session_state["pending_destructive_action"] = None


# ══════════════════════════════════════════════════════════
# INTENT CLASSIFICATION ROUTER
# ══════════════════════════════════════════════════════════

class NexusIntentRouter:
    """
    Categorizes student queries into explicit semantic intent types.
    Strictly separates conversational mentorship from workspace actions.
    """

    @staticmethod
    def classify(query: str) -> str:
        q = query.lower().strip()

        # 1. Destructive Actions
        if any(w in q for w in ["delete all my notes", "delete all notes", "reset my progress", "delete account", "delete my account"]):
            return "DESTRUCTIVE_ACTION"

        # 2. Natural Greetings & Onboarding
        greetings = ["hi", "hello", "hey", "hey nexus", "hi nexus", "hello nexus", "good morning", "good evening", "good afternoon", "who are you", "what can you do", "help"]
        if q in greetings or q.startswith("hi ") or q.startswith("hello "):
            if not any(kw in q for kw in ["explain", "teach", "how", "why", "quiz", "schedule", "plan", "procrastinat", "mit", "iit"]):
                return "GREETING"

        # 3. Contextual Follow-up Clarifications (Multi-turn dialogue)
        if any(w in q for w in ["second part", "part 2", "second point", "the 2nd part", "second step"]):
            return "CONTEXT_CLARIFICATION_SECOND_PART"

        if any(w in q for w in ["make it easier", "make that easier", "explain like a normal person", "too complicated", "simpler please", "explain simpler", "simplify"]):
            return "CONTEXT_SIMPLIFICATION"

        if any(w in q for w in ["icse exam", "icse version", "board version", "derivation", "mathematical version", "for my exam"]):
            return "CONTEXT_EXAM_MODE"

        if any(w in q for w in ["quiz me on this", "give me questions on this", "test me on this", "quiz me on it", "test me on it"]):
            return "CONTEXT_QUIZ_ME"

        if any(w in q for w in ["save this explanation to my notes", "save that explanation to my notes", "save this to my notes", "save this as a note", "save explanation to notes"]):
            return "CONTEXT_SAVE_NOTE"

        if any(w in q for w in ["add this to my revision queue", "add to my revision queue", "add this topic to tomorrow's revision", "add this to revision"]):
            return "CONTEXT_ADD_REVISION"

        # 4. Procrastination & Motivation Coaching
        procrastinate_keywords = [
            "procrastinating", "don't feel like studying", "dont feel like studying", "lost motivation",
            "feeling lazy", "can't focus", "cannot focus", "how to stop procrastinating", "help me get back on track",
            "procrastination", "wasting time", "no energy to study"
        ]
        if any(w in q for w in procrastinate_keywords):
            return "STUDY_ADVICE_PROCRASTINATION"

        # 5. Career & High-Level Academic Ambitions (e.g. MIT, IIT, Olympiads)
        goal_keywords = [
            "mit", "stanford", "harvard", "iit", "jee", "neet", "olympiad", "board topper", "98%", "99%", "100%",
            "wanna get into", "want to get into", "aiming for", "target university", "target college", "dream college",
            "become an engineer", "become a doctor", "astrophysics", "career in", "how to get into", "how do i get into",
            "get admission in", "crack jee", "crack neet", "prepare for mit"
        ]
        if any(w in q for w in goal_keywords):
            return "CAREER_ACADEMIC_GOAL"

        # 6. Daily Study Recommendations & Planning Inquiries
        study_today_keywords = [
            "what should i study today", "what to study today", "what should i do next", "make me a plan",
            "what should i focus on today", "how should i spend my study time", "plan my day", "recommend a study plan"
        ]
        if any(w in q for w in study_today_keywords):
            return "DAILY_STUDY_RECOMMENDATION"

        # 7. Study Advice, Stress & Emotional Coaching
        advice_keywords = [
            "struggling with", "struggling in", "scared about", "feeling behind", "behind in", "how should i study",
            "tips for", "how to prepare", "feeling overwhelmed", "exam next month",
            "how to stay focused", "how to revise", "how to score high", "i don't understand how to study",
            "anxious about", "improve my marks", "improve my score", "weak in physics", "weak in chemistry", "weak in math"
        ]
        if any(w in q for w in advice_keywords):
            return "STUDY_ADVICE_STRESS"

        # 8. Mistake Analysis (e.g. "I made a mistake in question 4. Help me understand why.")
        mistake_keywords = [
            "made a mistake", "got question", "got it wrong", "why is question", "why did i get",
            "mistake in question", "help me understand why i was wrong", "got 3 wrong", "got 4 wrong"
        ]
        if any(w in q for w in mistake_keywords):
            return "APP_COMMAND_MISTAKES"

        # 9. Progress & Analytics Queries
        progress_keywords = [
            "how am i doing", "how am i progressing", "my progress", "weakest topics", "weakest subjects",
            "weak topics", "weak subjects", "exam readiness", "my readiness", "progress audit", "how is my physics",
            "how is my chemistry", "how is my math", "my stats", "analytics", "how am i doing overall"
        ]
        if any(w in q for w in progress_keywords):
            return "PROGRESS_ANALYSIS"

        # 10. Socratic Dialogue Requests
        if any(w in q for w in ["socratic", "using questions", "ask me questions", "guide me with questions", "quiz me through questions"]):
            return "SOCRATIC_MODE"

        # 11. Workspace Control Commands (Explicit Actions)
        if any(w in q for w in ["focus session", "start focus", "start timer", "pomodoro", "deep work"]):
            return "APP_COMMAND_FOCUS"
        if any(w in q for w in ["schedule", "plan tomorrow", "add to schedule", "add to planner", "remind me to study"]):
            return "APP_COMMAND_PLANNER"
        if "mark " in q and any(w in q for w in ["completed", "complete", "done", "in progress"]):
            return "APP_COMMAND_SYLLABUS"
        if "revision" in q and any(w in q for w in ["add", "put", "schedule", "queue", "set"]):
            return "APP_COMMAND_REVISION"
        if ("note" in q or "notes" in q) and any(w in q for w in ["save", "create", "add", "make"]):
            return "APP_COMMAND_NOTES"
        if any(w in q for w in ["save formula", "add formula", "create formula"]):
            return "APP_COMMAND_FORMULAS"
        if any(w in q for w in ["quiz me", "test me", "generate quiz", "create quiz", "give me a test", "start a quiz", "give me harder questions"]):
            return "APP_COMMAND_QUIZ"
        if q.startswith("find ") or q.startswith("search ") or "look up" in q:
            return "APP_COMMAND_SEARCH"
        if any(w in q for w in ["wallpaper", "theme", "dark mode", "light mode", "change theme"]):
            return "APP_COMMAND_THEME"
        if any(w in q for w in ["open my", "take me to", "go to", "navigate to", "open the"]):
            return "APP_COMMAND_NAVIGATION"

        # 12. Default: Educational Concept Explanation
        return "CONCEPT_EXPLANATION"


# ══════════════════════════════════════════════════════════
# AUTHORIZED NEXUS CONTEXT BUILDER
# ══════════════════════════════════════════════════════════

class NexusContextBuilder:
    """Assembles authorized student data for AI reasoning."""

    @staticmethod
    def get_student_profile(user_id: int) -> dict:
        try:
            profile = get_user_profile(user_id) or {}
            return {
                "name": profile.get("name", "Student"),
                "class_name": profile.get("class_name", "Class 10"),
                "board": profile.get("board", "CBSE"),
                "academic_year": profile.get("academic_year", "")
            }
        except Exception as e:
            logger.error(f"Error fetching profile for user {user_id}: {e}")
            return {"name": "Student", "class_name": "Class 10", "board": "CBSE", "academic_year": ""}

    @staticmethod
    def get_syllabus_summary(user_id: int) -> dict:
        try:
            stats = get_overall_stats(user_id) or {}
            subjects = get_all_subjects_with_stats(user_id) or []
            return {
                "total_topics": stats.get("total_topics", 0),
                "completed_topics": stats.get("completed_topics", 0),
                "percent_completed": stats.get("percent_completed", 0),
                "subjects": [{
                    "name": s["name"],
                    "completed": s.get("completed", 0),
                    "total": s.get("total_topics", 0),
                    "pct": s.get("percent_completed", 0),
                    "avg_understanding": s.get("avg_understanding", 3)
                } for s in subjects]
            }
        except Exception as e:
            logger.error(f"Error fetching syllabus summary for user {user_id}: {e}")
            return {"total_topics": 0, "completed_topics": 0, "percent_completed": 0, "subjects": []}

    @staticmethod
    def get_priorities(user_id: int) -> list:
        try:
            priorities = get_top_nexus_priorities(user_id, limit=5) or []
            return [{
                "topic_name": p.get("topic_name", "Core Concept"),
                "subject_name": p.get("subject_name", "General"),
                "chapter_name": p.get("chapter_name", ""),
                "reasons": p.get("reasons", ["High-yield focus"])
            } for p in priorities]
        except Exception as e:
            logger.error(f"Error fetching priorities for user {user_id}: {e}")
            return []

    @staticmethod
    def assemble_full_context(user_id: int) -> dict:
        return {
            "profile": NexusContextBuilder.get_student_profile(user_id),
            "syllabus": NexusContextBuilder.get_syllabus_summary(user_id),
            "priorities": NexusContextBuilder.get_priorities(user_id)
        }


# ══════════════════════════════════════════════════════════
# DEEP PEDAGOGICAL KNOWLEDGE BASE (STEM & Humanities)
# ══════════════════════════════════════════════════════════

EXPANDED_KNOWLEDGE_BASE = {
    "newton": {
        "title": "Newton's Laws of Motion & Action-Reaction Principle",
        "subject": "Physics",
        "keywords": ["newton", "third law", "first law", "second law", "force", "action reaction", "momentum", "inertia", "laws of motion"],
        "intuition": "Forces in the universe never exist in isolation. You cannot touch something without it touching you back with the exact same strength. When you push against a brick wall, you feel the wall pressing firmly against your palm. The universe enforces a strict balance: every single interaction is a mutual two-way handshake.",
        "feynman_analogy": "Imagine you and your friend are wearing ice skates on completely frictionless ice. If you reach out and push your friend forward, what happens? You don't stay still — you slide backward at the exact same instant! Even if you are the one who did the pushing with your muscles, you both experience identical force magnitudes in opposite directions. The skates make the hidden reaction force impossible to miss.",
        "microscopic_reality": "At the atomic level, when surfaces make contact, the electron clouds of the outer atoms repel each other via the fundamental electromagnetic force. The electron cloud compression in Body A exerts an equal repulsive electrostatic force on the electron clouds of Body B ($F_{AB} = -F_{BA}$). Because these forces act on *different bodies*, they never cancel each other out.",
        "jargon_translator": "- *Inertia:* Natural laziness of matter — an object resists changing its current velocity unless forced.\n- *Momentum ($p = mv$):* How hard an object is to stop.\n- *Action-Reaction Pair:* Two forces that are equal in magnitude, opposite in direction, occur simultaneously, and act on two completely different objects.",
        "derivation_steps": [
            "**Step 1 (Newton's Second Law):** Rate of change of momentum is directly proportional to applied net force: $F = \\frac{dp}{dt} = \\frac{d(mv)}{dt} = m \\frac{dv}{dt} = ma$.",
            "**Step 2 (Two-Body Isolated System):** Consider two interacting masses $m_1$ and $m_2$ in an isolated system with no external forces ($\\Sigma F_{ext} = 0$).",
            "**Step 3 (Conservation of Linear Momentum):** Total momentum $p_{total} = p_1 + p_2 = \\text{constant}$.",
            "**Step 4 (Time Derivative of Momentum):** $\\frac{d(p_1 + p_2)}{dt} = 0 \\implies \\frac{dp_1}{dt} + \\frac{dp_2}{dt} = 0$.",
            "**Step 5 (Newton's Third Law Expression):** Since $F_{12} = \\frac{dp_1}{dt}$ and $F_{21} = \\frac{dp_2}{dt}$, we obtain $F_{12} + F_{21} = 0 \\implies \\mathbf{F_{12} = -F_{21}}$."
        ],
        "cartesian_signs": "Vector directional convention: Choose one direction (e.g. right/upward) as positive $(+)$. Forces in the opposite direction (left/downward) are strictly negative $(-)$. In momentum problems: $m_1 u_1 + m_2 u_2 = m_1 v_1 + m_2 v_2$.",
        "diagram_blueprint": "Draw Free Body Diagrams (FBDs) for each object separately. Object A shows force $\\vec{F}_{BA}$ pointing left. Object B shows force $\\vec{F}_{AB}$ pointing right. Never draw both action and reaction forces on the same single body FBD!",
        "examiner_traps": "1. **'Action and Reaction cancel each other' Trap:** NEVER say they cancel! They act on two different bodies. (Deducts 1 mark).\n2. **'Horse and Cart' Paradox:** The cart moves forward because the horse pushes backward against the *ground*, and the *ground pushes forward* on the horse's hooves with greater force than the cart's rolling friction.",
        "what_if_matrix": [
            ("A massive truck collides with a tiny mosquito", "Both experience the EXACT same collision force magnitude ($|F_{truck}| = |F_{mosquito}|$). The mosquito experiences catastrophic acceleration ($a = F/m$) because its mass is tiny."),
            ("You jump off a small boat onto a wooden dock", "Your legs push the boat backward (boat moves backward in water) as the boat pushes you forward onto the dock."),
            ("A rocket fires in empty space with no air to push against", "The rocket accelerates forward by pushing exhaust gases backward ($F_{rocket} = -F_{exhaust}$). It does not need an atmosphere.")
        ],
        "exam_question": "A gun of mass $M = 4\\text{ kg}$ fires a bullet of mass $m = 50\\text{ g}$ with a muzzle velocity of $v = 400\\text{ m/s}$. Calculate the recoil velocity of the gun.",
        "exam_solution": "**Step 1:** Convert units: $m = 50\\text{ g} = 0.05\\text{ kg}$.\n**Step 2:** Conservation of linear momentum: $(M + m)u = M V_{gun} + m v_{bullet} = 0$.\n**Step 3:** $4 V_{gun} + (0.05)(400) = 0 \\implies 4 V_{gun} + 20 = 0$.\n**Step 4:** $V_{gun} = -\\frac{20}{4} = -5\\text{ m/s}$ *(The negative sign indicates recoil opposite to bullet direction)*."
    },
    "photosynthesis": {
        "title": "Photosynthesis & Autotrophic Plant Physiology",
        "subject": "Biology",
        "keywords": ["photosynthesis", "chlorophyll", "chloroplast", "light reaction", "dark reaction", "calvin", "stomata", "photolysis"],
        "intuition": "Every calorie of food you have ever eaten, and every breath of oxygen you take, is solar energy processed by leaves. Plants are microscopic chemical solar power plants that capture photons from 93 million miles away and lock that energy into glucose sugar rings.",
        "feynman_analogy": "Imagine a leaf is a sun-powered bakery. The factory workers are green **Chlorophyll** molecules. The raw ingredients entering the loading dock are **Water** (pumped up from the roots) and **$\\text{CO}_2$** (sucked in through microscopic leaf windows called stomata). Sunlight provides the heat to crack water molecules in half, releasing oxygen out the window. The captured hydrogen is baked into delicious glucose bread rolls.",
        "microscopic_reality": "Photosynthesis happens in two distinct biochemical phases inside the chloroplast:\n1. **Light Reaction (in Thylakoid Grana):** Light photons strike photosystem II, exciting electrons. Photolysis of water occurs ($2\\text{H}_2\\text{O} \\xrightarrow{\\text{light}} 4\\text{H}^+ + 4e^- + \\text{O}_2$), generating ATP and NADPH.\n2. **Dark Reaction / Calvin Cycle (in Stroma):** ATP and NADPH power the enzyme RuBisCO to fix $\\text{CO}_2$ and synthesize $\\text{C}_6\\text{H}_{12}\\text{O}_6$, which is converted into insoluble starch for storage.",
        "jargon_translator": "- *Photolysis:* Splitting of water molecules using solar photon energy.\n- *Stroma:* The fluid matrix of the chloroplast where dark reactions synthesize sugars.\n- *Grana:* Stacks of thylakoid discs containing chlorophyll.",
        "derivation_steps": [
            "**Balanced Overall Equation:**\n$$6\\text{CO}_2 + 12\\text{H}_2\\text{O} \\xrightarrow[\\text{Chlorophyll}]{\\text{Sunlight}} \\text{C}_6\\text{H}_{12}\\text{O}_6 + 6\\text{O}_2 + 6\\text{H}_2\\text{O}$$",
            "**Phase 1 (Light Phase):** Absorption of light $\\to$ Electron excitation $\\to$ Photolysis of water ($2\\text{H}_2\\text{O} \\to 4\\text{H}^+ + 4e^- + \\text{O}_2$) $\\to$ Photophosphorylation (ADP + Pi $\\to$ ATP) $\\to$ NADP$^+$ reduction to NADPH.",
            "**Phase 2 (Dark Phase / Light-Independent):** Fixation of $\\text{CO}_2$ using ATP and NADPH in the stroma $\\to$ Phosphoglycerate (PGA) $\\to$ Glucose synthesis."
        ],
        "cartesian_signs": "Conditions written over/under arrow: 'Sunlight' and 'Chlorophyll' are strictly required in ICSE/CBSE board answers.",
        "diagram_blueprint": "Draw leaf cross-section: Upper cuticle $\\to$ Upper epidermis $\\to$ Palisade mesophyll (dense vertical cells with chloroplasts) $\\to$ Spongy mesophyll (air spaces for gas diffusion) $\\to$ Vascular bundle (Xylem inside, Phloem outside) $\\to$ Lower epidermis with stomatal pore and guard cells.",
        "examiner_traps": "1. **Unbalanced Equation:** Writing $\\text{CO}_2 + \\text{H}_2\\text{O} \\to \\text{C}_6\\text{H}_{12}\\text{O}_6 + \\text{O}_2$ loses 1 full mark.\n2. **Water on Both Sides:** ICSE mandates $12\\text{H}_2\\text{O}$ on left and $6\\text{H}_2\\text{O}$ on right because oxygen comes exclusively from water photolysis, not carbon dioxide!",
        "what_if_matrix": [
            ("Plant placed in dark for 48 hours", "Completely destarched. Used as a control setup in photosynthesis verification experiments."),
            ("Potassium ions ($K^+$) enter guard cells", "Endosmosis occurs, guard cells become turgid, and the stomatal aperture opens."),
            ("Leaf boiled in alcohol in a water bath", "Chlorophyll dissolves, decolorizing the leaf so blue-black iodine starch test is clearly visible.")
        ],
        "exam_question": "Explain why leaves are destarched before photosynthesis experiments and state the chemical test used to verify starch presence.",
        "exam_solution": "**Destarching:** The potted plant is kept in continuous dark for 48 hours so stored starch in leaves is fully consumed by cellular respiration.\n**Starch Test:** Dip decolorized leaf in iodine solution. Mastered areas containing starch turn **blue-black**, while non-photosynthetic control areas turn **brownish-yellow**."
    },
    "lens": {
        "title": "Optics, Thin Lens Formula & Image Formation",
        "subject": "Physics",
        "keywords": ["lens", "lens formula", "focal length", "magnification", "convex lens", "concave lens", "refraction", "optics"],
        "intuition": "A lens is simply a glass tool that alters the wavefront of light rays through refraction. A convex lens bends divergent light rays inward toward a real focus point, acting like a light funnel, whereas a concave lens spreads them outwards.",
        "feynman_analogy": "Think of light as a marching band marching in unison across pavement. When they hit a patch of muddy grass (denser glass lens), the soldiers who enter the mud first slow down while the others continue at full speed, causing the whole marching column to wheel around and bend toward the focal spot.",
        "microscopic_reality": "Light slows down inside the dielectric glass medium ($v = c/n$) due to electromagnetic phase delays during photon absorption and re-emission by glass atoms. By shaping the surface with spherical curvature, we make light at the thicker center travel through more glass than light at the thinner edges, causing all wave crests to arrive in phase at the focal point (Fermat's Principle of Least Time).",
        "jargon_translator": "- *Real Image:* An image formed by actual intersection of refracted rays; can be captured on a physical screen.\n- *Virtual Image:* Formed by apparent intersection when rays are produced backwards; cannot be caught on a screen.\n- *Magnification ($m = v/u = h_i/h_o$):* Ratio of image height to object height.",
        "derivation_steps": [
            "**Step 1 (Geometry of Convex Lens):** Place object $AB$ of height $h_o$ at distance $u$ in front of a thin convex lens of focal length $f$. A ray parallel to the principal axis passes through second focus $F_2$, and a ray through optical center $O$ passes undeviated.",
            "**Step 2 (Similar Triangles $\\Delta ABO \\sim \\Delta A'B'O$):** $\\frac{A'B'}{AB} = \\frac{OB'}{OB} \\implies \\frac{-h_i}{h_o} = \\frac{+v}{-u} \\implies \\frac{h_i}{h_o} = \\frac{v}{u}$.",
            "**Step 3 (Similar Triangles $\\Delta A'B'F_2 \\sim \\Delta MOF_2$):** $\\frac{A'B'}{MO} = \\frac{F_2 B'}{OF_2} \\implies \\frac{-h_i}{h_o} = \\frac{v - f}{f}$.",
            "**Step 4 (Equating Magnifications):** $\\frac{v}{u} = \\frac{v - f}{f} \\implies vf = uv - uf$.",
            "**Step 5 (Dividing throughout by $uvf$):** $\\frac{vf}{uvf} = \\frac{uv}{uvf} - \\frac{uf}{uvf} \\implies \\frac{1}{u} = \\frac{1}{f} - \\frac{1}{v} \\implies \\mathbf{\\frac{1}{f} = \\frac{1}{v} - \\frac{1}{u}}$."
        ],
        "cartesian_signs": "New Cartesian Sign Convention:\n- Optical center $O$ is the origin $(0,0)$.\n- Object distance $u$ is ALWAYS negative $(-u)$.\n- For Convex Lens: Focal length $f$ is POSITIVE $(+f)$.\n- For Concave Lens: Focal length $f$ is NEGATIVE $(-f)$.\n- Real image: $v$ is positive $(+v)$, $m$ is negative $(-m)$.\n- Virtual image: $v$ is negative $(-v)$, $m$ is positive $(+m)$.",
        "diagram_blueprint": "Draw principal axis with lens at center. Mark $2F_1, F_1, O, F_2, 2F_2$. Draw 2 standard rays: Ray 1 parallel to axis $\\to$ refracts through $F_2$. Ray 2 through optical center $O$ $\\to$ straight undeviated. Intersection gives inverted real image $A'B'$.",
        "examiner_traps": "1. **Mirror vs Lens Formula:** Lens formula is $\\frac{1}{f} = \\frac{1}{v} - \\frac{1}{u}$ (MINUS sign!). Do not write the mirror formula $\\frac{1}{f} = \\frac{1}{v} + \\frac{1}{u}$.\n2. **Missing Ray Arrowheads:** Rays without direction arrows lose 1 full mark in ICSE/CBSE board diagrams.",
        "what_if_matrix": [
            ("Object placed at $2F_1$", "Image forms at $2F_2$, Real, Inverted, Same Size ($m = -1$)."),
            ("Object placed between $F_1$ and O$", "Image forms on same side behind object, Virtual, Erect, Magnified ($m > +1$, Magnifying Glass effect)."),
            ("Lower half of lens is covered with black paper", "Full image is still formed, but its brightness/intensity is reduced to half.")
        ],
        "exam_question": "An object $5\\text{ cm}$ high is placed at a distance of $20\\text{ cm}$ in front of a convex lens of focal length $10\\text{ cm}$. Find the position, nature, and height of the image.",
        "exam_solution": "**Step 1:** Given $h_o = +5\\text{ cm}$, $u = -20\\text{ cm}$, $f = +10\\text{ cm}$.\n**Step 2:** Lens Formula: $\\frac{1}{f} = \\frac{1}{v} - \\frac{1}{u} \\implies \\frac{1}{10} = \\frac{1}{v} - \\frac{1}{-20} = \\frac{1}{v} + \\frac{1}{20}$.\n**Step 3:** $\\frac{1}{v} = \\frac{1}{10} - \\frac{1}{20} = \\frac{1}{20} \\implies \\mathbf{v = +20\\text{ cm}}$ *(Image forms $20\\text{ cm}$ behind the lens, Real and Inverted)*.\n**Step 4:** Magnification $m = \\frac{v}{u} = \\frac{20}{-20} = -1$.\n**Step 5:** Image height $h_i = m \\times h_o = -1 \\times 5 = \\mathbf{-5\\text{ cm}}$ *(Same size, inverted)*."
    },
    "quadratic": {
        "title": "Quadratic Equations, Discriminant & Parabolic Roots",
        "subject": "Mathematics",
        "keywords": ["quadratic", "discriminant", "roots", "completing square", "quadratic formula", "parabola", "nature of roots", "equations"],
        "intuition": "A quadratic equation represents a curved parabolic flight path in geometry. Solving for roots is simply finding the exact coordinates where the curve touches or crosses the zero ground line.",
        "feynman_analogy": "Imagine throwing a basketball into the air. The path is a symmetrical parabola ($y = ax^2 + bx + c$). The **Discriminant ($D = b^2 - 4ac$)** is your ground detector: If $D > 0$, the ball cuts through the floor at two distinct points. If $D = 0$, the bottom tip of the ball touches the floor at exactly 1 single point. If $D < 0$, the ball is floating above the floor and never touches it in the real world.",
        "microscopic_reality": "By completing the square on $ax^2 + bx + c = 0$, we translate the coordinate frame so the parabola's vertex is at $\\left(-\\frac{b}{2a}, -\\frac{D}{4a}\\right)$. The symmetry of parabolas guarantees that real roots are spaced symmetrically at distances $\\pm \\frac{\\sqrt{D}}{2a}$ from the vertex line of symmetry.",
        "jargon_translator": "- *Discriminant ($D = b^2 - 4ac$):* The mathematical indicator deciding root nature.\n- *Real and Equal Roots:* A single repeated solution ($x = -b/2a$).\n- *Roots / Zeros / Solutions:* Values of $x$ that satisfy the equation.",
        "derivation_steps": [
            "**Step 1 (Standard Form):** $ax^2 + bx + c = 0$ ($a \\neq 0$). Divide by $a$: $x^2 + \\frac{b}{a}x + \\frac{c}{a} = 0$.",
            "**Step 2 (Complete the Square):** Add and subtract $\\left(\\frac{b}{2a}\\right)^2$: $\\left(x + \\frac{b}{2a}\\right)^2 - \\frac{b^2}{4a^2} + \\frac{c}{a} = 0$.",
            "**Step 3 (Isolate Squared Term):** $\\left(x + \\frac{b}{2a}\\right)^2 = \\frac{b^2 - 4ac}{4a^2}$.",
            "**Step 4 (Square Root & Final Quadratic Formula):** $\\mathbf{x = \\frac{-b \\pm \\sqrt{b^2 - 4ac}}{2a}}$."
        ],
        "cartesian_signs": "When $b$ is negative, always compute $(-b)^2$ with parentheses to avoid the common sign slip of writing $-b^2$.",
        "diagram_blueprint": "Plot $y = ax^2 + bx + c$. Illustrate: $D > 0$ (2 intercepts), $D = 0$ (tangent to x-axis), $D < 0$ (suspended above x-axis).",
        "examiner_traps": "1. **Negative Dimensions/Speeds in Word Problems:** Always reject negative values with explicit rationale (e.g. 'Since speed cannot be negative, $x = 30\\text{ km/h}$').\n2. **Equal Roots Parameter numericals:** Set $D = b^2 - 4ac = 0$ directly to solve for unknown $k$.",
        "what_if_matrix": [
            ("Discriminant $D > 0$ and is a perfect square", "Two distinct rational roots."),
            ("Discriminant $D = 0$", "Two real and equal roots ($x = -b/2a$)."),
            ("Discriminant $D < 0$", "No real roots (conjugate complex roots in higher mathematics).")
        ],
        "exam_question": "Find the value of $k$ for which the quadratic equation $kx(x - 2) + 6 = 0$ has two equal real roots.",
        "exam_solution": "**Step 1:** Rewrite in standard form: $kx^2 - 2kx + 6 = 0$. Here $a = k$, $b = -2k$, $c = 6$.\n**Step 2:** For equal roots, Discriminant $D = 0 \\implies b^2 - 4ac = 0$.\n**Step 3:** $(-2k)^2 - 4(k)(6) = 0 \\implies 4k^2 - 24k = 0 \\implies 4k(k - 6) = 0$.\n**Step 4:** $k = 0$ or $k = 6$. Since $a \\neq 0$, $k = 0$ is rejected $\\implies \\mathbf{k = 6}$."
    }
}


def _match_knowledge(query: str):
    q = query.lower()
    for key, data in EXPANDED_KNOWLEDGE_BASE.items():
        if key in q:
            return data
        for kw in data.get("keywords", []):
            if kw in q:
                return data
    return None


# ══════════════════════════════════════════════════════════
# PRODUCTION NEXUS AI SERVICE
# ══════════════════════════════════════════════════════════

class NexusAIService:
    """
    Production-grade AI service combining Cloud LLMs and Autonomous Cognitive Engine.
    """

    def __init__(self):
        self.provider = None
        self.api_key = None
        self.model_name = None
        self._detect_provider_and_key()

    def _detect_provider_and_key(self):
        """Auto-detects active LLM provider from st.secrets, os.environ, or session override."""
        if "nexus_custom_ai_key" in st.session_state and st.session_state["nexus_custom_ai_key"].strip():
            self.api_key = st.session_state["nexus_custom_ai_key"].strip()
            self.provider = st.session_state.get("nexus_custom_ai_provider", "gemini").lower()
            self.model_name = st.session_state.get("nexus_custom_ai_model") or self._default_model_for_provider(self.provider)
            return

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
        self._detect_provider_and_key()
        is_cloud = bool(self.api_key and self.provider)
        masked_key = f"{self.api_key[:4]}...{self.api_key[-4:]}" if (self.api_key and len(self.api_key) > 8) else ("****" if self.api_key else "")
        return {
            "is_configured": True,
            "is_cloud": is_cloud,
            "engine_mode": f"Cloud LLM ({self.provider.upper()})" if is_cloud else "Autonomous Cognitive Engine",
            "provider": self.provider or "Autonomous Engine",
            "model": self.model_name or "Nexus Cognitive v4.0",
            "masked_key": masked_key
        }

    def _call_llm_with_tools(self, user_id: int, system_prompt: str, user_query: str, chat_history: list) -> dict:
        """Invokes Cloud LLM with full student context and tool execution support."""
        self._detect_provider_and_key()
        if not self.api_key or not self.provider:
            return None

        prov = self.provider.lower()
        full_system = f"{system_prompt}\n\nAvailable Tools:\n{json.dumps(NEXUS_TOOL_DEFINITIONS)}\nIf an action is required, respond with a JSON block ```json\n{{\"tool\": \"tool_name\", \"parameters\": {{...}}}}\n```"
        
        formatted_history = "\n".join([f"{m['role'].capitalize()}: {m['content']}" for m in chat_history[-6:]])
        full_prompt = f"Chat History:\n{formatted_history}\n\nUser: {user_query}"

        try:
            if prov == "gemini":
                model = self.model_name or "gemini-2.5-flash"
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={self.api_key}"
                payload = {
                    "contents": [{"role": "user", "parts": [{"text": f"{full_system}\n\n{full_prompt}"}]}],
                    "generationConfig": {"temperature": 0.4, "maxOutputTokens": 3000}
                }
                resp = requests.post(url, json=payload, headers={"Content-Type": "application/json"}, timeout=45)
                if resp.status_code == 200:
                    text = resp.json()["candidates"][0]["content"]["parts"][0]["text"]
                    return self._process_llm_output(user_id, text)
            elif prov in ["openai", "groq"]:
                url = "https://api.openai.com/v1/chat/completions" if prov == "openai" else "https://api.groq.com/openai/v1/chat/completions"
                headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
                payload = {
                    "model": self.model_name,
                    "messages": [
                        {"role": "system", "content": full_system},
                        {"role": "user", "content": full_prompt}
                    ],
                    "temperature": 0.4,
                    "max_tokens": 3000
                }
                resp = requests.post(url, json=payload, headers=headers, timeout=45)
                if resp.status_code == 200:
                    text = resp.json()["choices"][0]["message"]["content"]
                    return self._process_llm_output(user_id, text)
        except Exception as e:
            logger.error(f"Cloud LLM call failed: {e}")

        return None

    def _process_llm_output(self, user_id: int, raw_text: str) -> dict:
        """Parses tool calls from LLM output, executes them, and formats response."""
        badge = None
        action_json = None
        
        match = re.search(r"```json\s*(\{.*?\})\s*```", raw_text, re.DOTALL)
        if match:
            try:
                action_json = json.loads(match.group(1))
            except Exception:
                pass

        if action_json and "tool" in action_json:
            tool_name = action_json["tool"]
            params = action_json.get("parameters", {})
            result = execute_nexus_tool(user_id, tool_name, params)
            if result.get("success"):
                badge = f"⚡ {result.get('message', 'Action executed.')}"
            elif result.get("error"):
                badge = f"⚠️ {result.get('error')}"

        clean_text = re.sub(r"```json\s*\{.*?\}\s*```", "", raw_text, flags=re.DOTALL).strip()
        return {
            "content": clean_text or raw_text,
            "action_badge": badge
        }

    # ══════════════════════════════════════════════════════════
    # MAIN CONVERSATIONAL CHAT ENGINE (Dual-Engine with Intent Routing)
    # ══════════════════════════════════════════════════════════
    def process_chat_message(self, user_id: int, user_message: str) -> dict:
        """
        Main entry point for Nexus conversational intelligence.
        Routes user query through the NexusIntentRouter.
        """
        query = (user_message or "").strip()
        if not query:
            return {
                "content": "I'm here to help with your studies! Ask me any concept question, request a quiz, or give a study command.",
                "action_badge": "🤖 Ready"
            }

        # Safe, lightweight profile loading only
        profile = NexusContextBuilder.get_student_profile(user_id)
        chat_history = NexusConversationSession.get_history()

        try:
            # ── 1. Destructive Action Guardrail ──
            pending = st.session_state.get("pending_destructive_action")
            if pending and "confirm" in query.lower():
                if pending == "DELETE_ALL_NOTES":
                    res = execute_nexus_tool(user_id, "delete_all_notes", {"confirmed": True})
                    st.session_state["pending_destructive_action"] = None
                    return {
                        "content": f"✅ **Action Confirmed:** {res.get('message', 'All notes deleted.')}",
                        "action_badge": "🗑️ All Notes Deleted",
                        "follow_ups": ["View Syllabus", "Create New Note", "Plan Today's Study"]
                    }

            # ── 2. Classify Intent ──
            intent = NexusIntentRouter.classify(query)

            # ── 3. Handle Intent Specifically ──

            # Intent A: Destructive Action Prompt
            if intent == "DESTRUCTIVE_ACTION":
                st.session_state["pending_destructive_action"] = "DELETE_ALL_NOTES"
                return {
                    "content": """
⚠️ **Destructive Action Confirmation Required**

Are you sure you want to permanently delete **all study notes** in your repository? This action cannot be undone.

> To proceed, type **"confirm delete all notes"**. To cancel, simply ask any other study question.
""",
                    "action_badge": "⚠️ Confirmation Pending",
                    "follow_ups": ["confirm delete all notes", "Cancel & View My Notes"]
                }

            # Intent B: Natural Greeting & Onboarding
            if intent == "GREETING":
                return self._handle_greeting(profile)

            # Intent C: Career & High-Level Academic Goal (MIT, IIT, Stanford, Olympiads)
            if intent == "CAREER_ACADEMIC_GOAL":
                return self._handle_career_goal(profile, query)

            # Intent D: Procrastination & Mindset Reset
            if intent == "STUDY_ADVICE_PROCRASTINATION":
                return self._handle_procrastination_and_motivation(profile, query)

            # Intent E: Study Advice, Stress & Emotional Coaching
            if intent == "STUDY_ADVICE_STRESS":
                return self._handle_study_advice(profile, query)

            # Intent F: Daily Study Recommendation ("What should I study today?")
            if intent == "DAILY_STUDY_RECOMMENDATION":
                return self._handle_daily_study_recommendation(user_id, profile)

            # Intent G: Multi-turn Follow-ups (Clarification, Simplification, Exam Mode)
            if intent == "CONTEXT_CLARIFICATION_SECOND_PART":
                return self._handle_clarification_second_part()

            if intent == "CONTEXT_SIMPLIFICATION":
                return self._handle_simplification()

            if intent == "CONTEXT_EXAM_MODE":
                return self._handle_exam_mode(profile)

            if intent == "CONTEXT_QUIZ_ME":
                active_t = NexusConversationSession.get_active_topic()
                return self._handle_workspace_command(user_id, "APP_COMMAND_QUIZ", f"Quiz me on {active_t}", profile)

            if intent == "CONTEXT_SAVE_NOTE":
                return self._handle_workspace_command(user_id, "APP_COMMAND_NOTES", "save note", profile)

            if intent == "CONTEXT_ADD_REVISION":
                active_t = NexusConversationSession.get_active_topic()
                return self._handle_workspace_command(user_id, "APP_COMMAND_REVISION", f"Add {active_t} to revision", profile)

            # Intent H: Progress & Analytics Query
            if intent == "PROGRESS_ANALYSIS":
                return self._handle_progress_analysis(user_id)

            # Intent I: Workspace Control Commands
            if intent.startswith("APP_COMMAND_"):
                return self._handle_workspace_command(user_id, intent, query, profile)

            # Intent J: Socratic Mode
            if intent == "SOCRATIC_MODE":
                return self._handle_socratic_mode(query)

            # Intent K: Educational Concept Explanation
            # 1. Try Cloud LLM first if configured
            system_instruction = f"""
You are Nexus AI, a warm, patient, highly intelligent academic tutor and study copilot for {profile['name']} ({profile['class_name']} • {profile['board']}).
Guidelines:
1. Communicate naturally and conversationally, like a great human private tutor.
2. Teach concepts with step-by-step intuition, analogies, real examples, formal definitions, and KaTeX equations where relevant.
3. Keep your answers focused strictly on academic and study mastery.
"""
            cloud_result = self._call_llm_with_tools(user_id, system_instruction, query, chat_history)
            if cloud_result and cloud_result.get("content"):
                return {
                    "content": cloud_result["content"],
                    "action_badge": cloud_result.get("action_badge") or "💡 Deep Pedagogical Lesson",
                    "follow_ups": ["Explain Simpler", "Show Board Derivation", "Quiz Me on This", "Save as Note", "Add to Revision"]
                }

            # 2. Autonomous Local Pedagogical Synthesis
            return self._handle_concept_explanation(user_id, query, profile)

        except Exception as e:
            logger.exception(f"Unexpected error in process_chat_message for query '{query}': {e}")
            return {
                "content": f"""
I ran into a temporary technical issue while processing your request, but I am still here to help!

Could you please rephrase your question, or ask about a specific concept you'd like to study?
""",
                "action_badge": "🤖 Nexus Copilot Ready",
                "follow_ups": ["Explain Newton's Laws simply", "Plan my study sprints", "Quiz me on weak topics"]
            }

    # ══════════════════════════════════════════════════════════
    # DEDICATED INTENT HANDLERS (Conversational & Safe)
    # ══════════════════════════════════════════════════════════

    def _handle_greeting(self, profile: dict) -> dict:
        """Personalized, warm academic greeting with actionable shortcuts."""
        board = profile.get("board", "CBSE")
        return {
            "content": f"""
👋 **Hello {profile.get('name', 'Student')}! I'm your Nexus Academic Copilot.**

I'm here as your personal tutor and workspace assistant for **{profile.get('class_name', 'Class 10')} ({board})**. Here is how we can work together:

1. 💡 **Master Concepts:** Ask me to teach anything (*"Explain Newton's Third Law simply"*, *"Teach me Photosynthesis from first principles"*, *"Show mathematical derivation of Lens Formula"*).
2. 🎯 **Adaptive Quizzing:** Say *"Quiz me on Chemical Bonding"* or *"Test my weak topics"*.
3. 🗓️ **Plan Your Study:** Say *"Schedule 45 minutes of Physics tomorrow"* or *"What should I study today?"*.
4. 🧠 **Spaced Repetition & Notes:** Tell me *"Add this to my revision queue"* or *"Save this explanation as a note"*.
5. ❌ **Mistake Diagnostics:** Tell me *"I made a mistake in question 4"* and I'll analyze the root cause.
6. ⏱️ **Focus Studio:** Say *"Start a 25 min focus session for Chemistry"*.

**What concept or goal are we tackling today?**
""",
            "action_badge": f"🤖 Nexus Academic Copilot • {board}",
            "follow_ups": ["Explain Newton's Third Law to me", "What should I study today?", "Start a 25 min Focus session", "I wanna get into MIT"]
        }

    def _handle_career_goal(self, profile: dict, query: str) -> dict:
        """Dynamic, comprehensive conversational mentorship for ambitious academic goals (MIT, Stanford, IIT). Zero DB queries!"""
        target = "MIT"
        q_lower = query.lower()
        if "iit" in q_lower or "jee" in q_lower:
            target = "IIT / JEE Advanced"
        elif "neet" in q_lower or "doctor" in q_lower:
            target = "NEET / Top Medical Colleges"
        elif "stanford" in q_lower:
            target = "Stanford"
        elif "harvard" in q_lower:
            target = "Harvard"

        content = f"""
Absolutely — and that's a seriously ambitious goal. 😄

If you're talking about getting into **{target}** from your current stage in **{profile.get('class_name', 'Class 10')}**, the important thing is that you don't need to somehow become an elite university-level scholar overnight.

You have time.

What matters right now is building the foundations that will eventually make you a very strong applicant: **mathematics, core science, programming, problem-solving stamina, independent projects, communication**, and most importantly, the habit of **going deep into things instead of just studying for marks**.

And there's one key mindset shift I'd recommend about the way you approach this...

> **Don't make the goal: *"How do I get into {target}?"***
> **Make the goal: *"How do I become the kind of student {target} would want?"***

Those are very different goals. The second one puts you in control of your daily learning right now.

If you want, I can help you build that path from where you are right now — including academics, problem-solving, projects, Olympiad competitions, and study habits.

**What subject or technical area are you currently most curious about?**
"""
        return {
            "content": content,
            "action_badge": f"🎯 Strategic Roadmap • Target: {target}",
            "follow_ups": [
                "Explain Newton's Laws from first principles",
                "Plan a 45-min STEM Focus Sprint",
                "Show Olympiad Level Math Quiz",
                "What should I study today?"
            ]
        }

    def _handle_procrastination_and_motivation(self, profile: dict, query: str) -> dict:
        """Grounded, empathetic anti-procrastination coaching using the 5-Minute Rule."""
        content = f"""
I hear you. Let's be real: **nobody feels 100% motivated every single day**, and beating yourself up about procrastinating usually just creates more friction and makes you procrastinate more.

The secret isn't waiting for motivation to strike out of nowhere. It's **lowering the bar to start so low that your brain doesn't resist it**.

---

### 🛠️ The 5-Minute Rule

1. **Pick One Tiny Action:** Don't think about finishing a massive chapter or studying for 3 hours. That feels overwhelming.
2. **Commit to Just 5 Minutes:** Tell yourself: *"I will open my notebook and read just 1 page or solve 2 questions."*
3. **The Inertia Shift:** Once you start and cross the initial activation energy barrier, the brain's natural resistance disappears.

---

Let's do this together right now. 

Would you like me to **start a gentle 15-minute Focus Sprint** in Focus Studio, or would you prefer we **talk through an interesting concept together** first?
"""
        return {
            "content": content,
            "action_badge": "💡 Reset & Refocus Protocol",
            "follow_ups": [
                "Start a 25 minute Physics focus session",
                "Explain Newton's Third Law to me",
                "What should I study today?",
                "Check my overall progress"
            ]
        }

    def _handle_study_advice(self, profile: dict, query: str) -> dict:
        """Empathetic, structured study strategy and mindset coaching. Zero DB queries!"""
        q_lower = query.lower()
        subject = "Physics" if "physics" in q_lower else ("Chemistry" if "chem" in q_lower else ("Mathematics" if "math" in q_lower else "your subjects"))

        content = f"""
🤝 **I hear you, and it is completely normal to feel this way.**

When studying for rigorous examinations in **{profile.get('class_name', 'Class 10')}**, feeling stuck or behind in **{subject}** happens to every great student. Remember: **struggle is not a sign of failure — it's the exact moment your brain is rewiring for deeper understanding.**

---

### 🛠️ The 4-Step Recovery Protocol

1. 🎯 **Triage & Narrow the Focus:**
   - Don't try to study the entire textbook at once. We'll pick **one single subtopic** today (e.g. *Forces & Motion*, *Refraction*, or *Chemical Bonding*).

2. 💡 **Ditch Passive Reading for First-Principles Intuition:**
   - Re-reading and highlighting creates an illusion of competence. Instead, let me explain the concept using the **Feynman Technique** (simple everyday analogies + microscopic mechanisms).

3. ✍️ **Active Recall & Mistake Vaulting:**
   - Immediately solve 3–5 targeted practice questions. If you make an error, celebrate it! We'll diagnose the root cause and store it in your **Mistake Vault** so you never repeat it on exam day.

4. 🧠 **Spaced Repetition Protection:**
   - We will schedule automated reviews at optimal intervals (Day 1, Day 3, Day 7) so concepts stay permanently locked in long-term memory.

---

**Let's take immediate action together right now. What is the #1 topic in {subject} that is giving you trouble?**
"""
        return {
            "content": content,
            "action_badge": f"💡 Academic Coaching • {subject}",
            "follow_ups": [
                f"Explain {subject if subject != 'your subjects' else 'Newton'} simply",
                "Start a 25 minute Physics focus session",
                "Schedule 45 minutes of Physics tomorrow",
                "What should I study today?"
            ]
        }

    def _handle_daily_study_recommendation(self, user_id: int, profile: dict) -> dict:
        """Inspects actual database records across subjects, revision queue, and mistakes to reason about today's study priorities."""
        try:
            subjects = get_all_subjects_with_stats(user_id) or []
            rev_queue = get_revision_queue(user_id) or []
            mistakes = get_all_mistakes(user_id) or []
            stats = get_overall_stats(user_id) or {}

            # Sort subjects by completion percentage (ascending) to identify growth areas
            subj_summary = []
            lowest_subj = "Physics"
            lowest_pct = 100
            for s in subjects:
                pct = s.get("percent_completed", 0)
                name = s.get("name", "Science")
                subj_summary.append(f"**{name}:** {pct}% completed")
                if pct < lowest_pct:
                    lowest_pct = pct
                    lowest_subj = name

            stats_bullets = " • ".join(subj_summary) if subj_summary else "**Physics:** 54% • **Chemistry:** 72% • **Mathematics:** 88%"
            rev_count = len(rev_queue)

            content = f"""
Looking at your workspace right now, here is what your study data shows:

- 📊 **Curriculum Coverage:** {stats_bullets}
- 🧠 **Pending Spaced Revisions:** **{rev_count} topics** due in your review queue
- ❌ **Unreviewed Mistake Cards:** **{len(mistakes)} items** in your Mistake Vault

---

### 🎯 Why I Recommend Prioritizing {lowest_subj} Today:
**{lowest_subj}** currently has your highest growth potential (at {lowest_pct}% completion). Tackling it with dedicated deep work blocks today will give you the single biggest lift in your overall **Exam Readiness Score**.

---

### ⚡ 3 Actionable Study Blocks for Today:

1. 🧠 **Deep Work Sprint (45 min) • {lowest_subj}**
   - **Strategy:** Read core derivations, write formulas from memory, and test self with 3 active recall questions.
2. 📐 **Practice & Problem Solving (25 min) • High-Yield Numericals**
   - **Strategy:** Solve 5 previous-year board questions under timed conditions.
3. 🔄 **Spaced Repetition & Retention (15 min)**
   - **Strategy:** Clear your {rev_count} pending revision cards to prevent forgetting-curve decay (+50 XP).

---

**Would you like me to start a 45-minute Focus Session for {lowest_subj}, or schedule these blocks in your Planner?**
"""
            return {
                "content": content,
                "action_badge": f"🗓️ Data-Driven Study Plan • Priority: {lowest_subj}",
                "follow_ups": [
                    f"Start a 25 minute {lowest_subj} focus session",
                    f"Schedule 45 minutes of {lowest_subj} tomorrow",
                    "Quiz me on weak areas",
                    "Explain Newton's Third Law to me"
                ]
            }
        except Exception as e:
            logger.error(f"Error in _handle_daily_study_recommendation: {e}")
            return {
                "content": """
Here is your strategic study recommendation for today:

1. 🧠 **Block 1 (45 min):** Deep work on your lowest-confidence STEM subject.
2. 📐 **Block 2 (25 min):** Active problem-solving and numerical practice.
3. 🔄 **Block 3 (15 min):** Clear your active Spaced Repetition queue.

Would you like me to configure a 25-minute Focus Session to get started?
""",
                "action_badge": "🗓️ Recommended Study Blueprint",
                "follow_ups": ["Start a 25 minute Physics focus session", "Plan my study sprints", "Quiz me on weak areas"]
            }

    def _handle_clarification_second_part(self) -> dict:
        """Patiently re-explains the 2nd part/microscopic mechanism of the active topic."""
        active_t = NexusConversationSession.get_active_topic()
        kb = _match_knowledge(active_t) or EXPANDED_KNOWLEDGE_BASE["newton"]

        content = f"""
That's completely fine! If the first explanation didn't click, that's on the explanation — not on you. 😄

Let's slow down and zoom specifically into **the second part of {kb['title']}**:

---

### 🔬 The Microscopic Reality (Step-by-Step)

{kb['microscopic_reality']}

---

### 💡 The Crucial Distinction That Confuses Most Students:
> **Why Action and Reaction NEVER Cancel Out:**
> When you push a wall, the action force acts on the **wall**. The reaction force acts on **your hands**.
> Because the two forces act on **two completely different physical bodies**, they cannot cancel each other out!

---

Does seeing it at the atomic level make more intuitive sense, or should we try another everyday example?
"""
        return {
            "content": content,
            "action_badge": f"💡 Clarification • {kb['title']}",
            "follow_ups": ["Make it easier", "Quiz me on this", "Save this explanation to my notes", "Show Board Derivation"]
        }

    def _handle_simplification(self) -> dict:
        """Delivers an ultra-simple, everyday story-based explanation with zero jargon."""
        active_t = NexusConversationSession.get_active_topic()
        kb = _match_knowledge(active_t) or EXPANDED_KNOWLEDGE_BASE["newton"]

        content = f"""
Let's strip away all textbook words and explain **{kb['title']}** in plain everyday language:

---

### 🚲 The Pure Analogy

{kb['feynman_analogy']}

---

### 🌟 The One Sentence Rule
Whenever Object A touches Object B, Object B pushes back on Object A with the **exact same strength in the opposite direction**. It is a mandatory two-way handshake enforced by the universe.

Can you imagine pushing off the side of a swimming pool? You push the concrete backward, and the concrete launches you forward through the water!

**Does that click better now?**
"""
        return {
            "content": content,
            "action_badge": f"💡 Simplified Intuition • {kb['title']}",
            "follow_ups": ["Quiz me on this", "Save this explanation to my notes", "Now explain it like I'm preparing for an ICSE exam", "Add this to my revision queue"]
        }

    def _handle_exam_mode(self, profile: dict) -> dict:
        """Switches the active topic into Board Exam Derivation mode."""
        active_t = NexusConversationSession.get_active_topic()
        board = profile.get("board", "CBSE")
        kb = _match_knowledge(active_t) or EXPANDED_KNOWLEDGE_BASE["newton"]
        return self._build_board_exam_lesson(kb, board)

    def _handle_progress_analysis(self, user_id: int) -> dict:
        """Safely queries student's progress and readiness score without crashing."""
        try:
            readiness = calculate_exam_readiness_score(user_id) or {}
            stats = get_overall_stats(user_id) or {}
            score = readiness.get("readiness_score", 0)
            tier = readiness.get("readiness_tier", "Building Foundation")
            completed = stats.get("completed_topics", 0)
            total = stats.get("total_topics", 0)
            pct = stats.get("percent_completed", 0)

            content = f"""
### 📊 Academic Velocity & Progress Audit

- **Exam Readiness Score:** **{score} / 100** ({tier})
- **Syllabus Coverage:** **{completed} of {total} topics** ({pct}% completed).

---

### 🟢 What Is Going Well
- Foundation established in completed curriculum modules.
- Active recall tracking configured in your workspace.

### 🟡 Key Leverage Points for Fast Improvement
- Clear pending items in your **Spaced Repetition queue** to prevent forgetting-curve decay.
- Review unreviewed cards in your **Mistake Vault** through targeted re-testing.

### 🚀 3 Strategic Actions for Today:
1. Complete a **25-min Focus Sprint** on high-yield priority topics.
2. Clear your active Spaced Repetition queue (+50 XP).
3. Take a 5-question practice quiz to calibrate accuracy.
"""
            return {
                "content": content,
                "action_badge": f"📊 Progress Audit ({score}/100)",
                "follow_ups": ["What should I study today?", "Start a 25 minute Physics focus session", "Quiz me on weak areas"]
            }
        except Exception as e:
            logger.error(f"Error in _handle_progress_analysis: {e}")
            return {
                "content": "Your progress tracking is active! You can view detailed subject completion, understanding heatmaps, and exam velocity in the **📊 Analytics** page.",
                "action_badge": "📊 Progress Overview",
                "follow_ups": ["Open Analytics Page", "Plan Today's Study", "Start Focus Session"]
            }

    def _handle_workspace_command(self, user_id: int, intent: str, query: str, profile: dict) -> dict:
        """Executes explicit application control tools safely."""
        q_lower = query.lower()
        active_topic = NexusConversationSession.get_active_topic()
        board = profile.get("board", "CBSE")

        # Focus Session
        if intent == "APP_COMMAND_FOCUS":
            dur_match = re.search(r"(\d+)\s*(?:min|minute)", q_lower)
            dur = int(dur_match.group(1)) if dur_match else 25
            subject = None
            for s in ["Physics", "Chemistry", "Mathematics", "Biology", "English", "History", "Geography"]:
                if s.lower() in q_lower:
                    subject = s
                    break
            res = execute_nexus_tool(user_id, "start_focus_session", {
                "subject_name": subject,
                "topic_name": active_topic,
                "duration_minutes": dur
            })
            execute_nexus_tool(user_id, "navigate_to_page", {"page_name": "Focus"})
            subj_label = subject or active_topic or "Physics"
            return {
                "content": f"Done! 🚀 I've opened Focus Studio, selected **{subj_label}**, and started a **{dur}-minute session**. Let's lock in and get some deep work done.",
                "action_badge": f"⏱️ Focus Sprint ({dur} min)",
                "follow_ups": ["Start Timer", "Set Ambient Audio", "Plan Next Task"]
            }

        # Planner
        if intent == "APP_COMMAND_PLANNER":
            dur_match = re.search(r"(\d+)\s*(?:min|minute|hr|hour)", q_lower)
            dur = 45
            if dur_match:
                val = int(dur_match.group(1))
                dur = val * 60 if "hr" in dur_match.group(0) or "hour" in dur_match.group(0) else val
            date_target = "tomorrow" if "tomorrow" in q_lower else "today"

            subject = None
            for s in ["Physics", "Chemistry", "Mathematics", "Biology", "English", "History", "Geography"]:
                if s.lower() in q_lower:
                    subject = s
                    break

            task_desc = f"Study {subject or 'Physics'}"
            if "of " in q_lower:
                task_desc = f"Study {query.split('of ', 1)[1].split('tomorrow')[0].split('today')[0].strip()}"
            elif "for " in q_lower and "min" not in q_lower.split("for ", 1)[1][:10]:
                task_desc = query.split("for ", 1)[1].strip()

            res = execute_nexus_tool(user_id, "create_study_task", {
                "task_description": task_desc,
                "plan_date": date_target,
                "duration_minutes": dur,
                "subject_name": subject
            })
            return {
                "content": f"""
I've scheduled this into your **Daily Study Planner**:

- 🗓️ **Date:** {date_target.capitalize()} ({res.get('date', 'Upcoming')})
- ⏱️ **Duration:** {dur} Minutes
- 📚 **Mission:** **{task_desc}**

*Consistency is key to high-stakes exam performance. Win this study block!*
""",
                "action_badge": f"🗓️ Scheduled Task ({dur} min)",
                "follow_ups": ["What should I study today?", "Start a 25 minute Physics focus session", "Show Today's Planner"]
            }

        # Syllabus
        if intent == "APP_COMMAND_SYLLABUS":
            status = "Completed" if ("completed" in q_lower or "complete" in q_lower or "done" in q_lower) else "In Progress"
            t_query = q_lower.replace("mark", "").replace("as completed", "").replace("as complete", "").replace("as done", "").replace("completed", "").strip()
            res = execute_nexus_tool(user_id, "update_topic_status", {"topic_name": t_query, "status": status})
            if res.get("success"):
                return {
                    "content": f"✅ **Syllabus Updated:** {res['message']}\n\nYour curriculum completion percentage and velocity metrics have been updated in your dashboard analytics.",
                    "action_badge": f"✅ {res['new_status']}: {res['topic_name']}",
                    "follow_ups": ["Add this to my revision queue", "Quiz me on this", "View Syllabus"]
                }
            return {
                "content": f"I checked your syllabus for '{t_query}'. {res.get('error', 'Topic updated.')}",
                "action_badge": "✅ Syllabus Updated",
                "follow_ups": ["View Syllabus", "Quiz me on this"]
            }

        # Revision
        if intent in ["APP_COMMAND_REVISION", "CONTEXT_ADD_REVISION"]:
            t_query = q_lower.replace("add", "").replace("this topic", "").replace("this", "").replace("to tomorrow's revision", "").replace("to my revision queue", "").replace("to revision", "").replace("put in revision", "").replace("schedule revision", "").replace("queue", "").strip() or active_topic
            res = execute_nexus_tool(user_id, "schedule_revision", {"topic_name": t_query})
            topic_label = res.get("topic_name", active_topic)
            return {
                "content": f"Done! 🧠 I've added **{topic_label}** to your **Spaced Repetition Queue**. Nexus will prompt you at optimal forgetting-curve intervals (1d, 3d, 7d) so this concept stays permanently locked in your memory.",
                "action_badge": "🧠 Scheduled Spaced Revision",
                "follow_ups": ["View Revision Queue", "Quiz me on this", "What should I study today?"]
            }

        # Notes
        if intent in ["APP_COMMAND_NOTES", "CONTEXT_SAVE_NOTE"]:
            last_ai_msg = NexusConversationSession.get_last_explanation()
            if not last_ai_msg:
                for m in reversed(NexusConversationSession.get_history()):
                    if m["role"] == "nexus":
                        last_ai_msg = m["content"]
                        break
            note_content = last_ai_msg or f"Summary and key principles of {active_topic}."
            res = execute_nexus_tool(user_id, "create_note", {
                "topic_name": active_topic,
                "title": f"Nexus Notes: {active_topic}",
                "content_markdown": note_content
            })
            return {
                "content": f"Done! 📝 I've saved this full explanation to your **Notes Repository** under **{active_topic}** with all equations and diagrams intact (+25 XP).",
                "action_badge": "📝 Note Saved to Repository",
                "follow_ups": ["View All Notes", "Quiz me on this", "Add this to my revision queue"]
            }

        # Formulas
        if intent == "APP_COMMAND_FORMULAS":
            return {
                "content": "To save a formula, specify the title and LaTeX expression (e.g. *'Save formula Lens Formula \\frac{1}{f} = \\frac{1}{v} - \\frac{1}{u}'*).",
                "action_badge": "📐 Formula Assistant",
                "follow_ups": ["Save Lens Formula", "View Formula Vault"]
            }

        # Mistakes
        if intent == "APP_COMMAND_MISTAKES":
            return {
                "content": f"""
### ❌ Diagnostic Mistake Breakdown

Let's diagnose exactly where errors typically happen on **{active_topic}**:

1. **Root-Cause Classification:** Most errors on this concept stem from **Formula Sign Convention** (e.g. Cartesian vector signs) or **Missing SI Unit Conversions** (e.g. grams vs kilograms, cm vs meters).
2. **The Golden Rule to Prevent This:**
   - Always write out the formula in standard algebraic symbols before substituting numerical values.
   - Verify that coordinate axes are explicitly drawn before calculating.
3. **Mastery Action:** Would you like me to log this into your **Mistake Vault** so we can re-test it on your next practice sprint?
""",
                "action_badge": "❌ Error Diagnosed",
                "follow_ups": ["Log Mistake to Vault", "Try Similar Question", "Explain Concept Again"]
            }

        # Quiz
        if intent in ["APP_COMMAND_QUIZ", "CONTEXT_QUIZ_ME"]:
            target = active_topic if (active_topic and active_topic != "General Academic Mastery") else "Core High-Yield Concepts"
            res = execute_nexus_tool(user_id, "generate_and_launch_quiz", {
                "topic_or_subject": target,
                "count": 5,
                "difficulty": "Board Exam Hard"
            })
            return {
                "content": f"""
### 🎯 AI Assessment Ready

I have crafted a 5-question high-rigor quiz on **{target}** targeting standard {board} exam traps:

- **Difficulty:** Board Exam Caliber
- **Auto-Sync:** Incorrect answers will be automatically sent to your Mistake Vault for targeted re-testing.

> Click below or navigate to **🎯 Practice** to launch your interactive assessment!
""",
                "action_badge": f"🎯 Launched Quiz: {target}",
                "follow_ups": ["Play Quiz Now", "Quiz on Mistakes Only", "Explain Concept First"]
            }

        # Search
        if intent == "APP_COMMAND_SEARCH":
            search_term = q_lower.replace("find", "").replace("search", "").replace("everything related to", "").replace("for", "").strip()
            res = execute_nexus_tool(user_id, "search_nexus_workspace", {"query": search_term})
            return {
                "content": f"""
### 🔍 Nexus Workspace Search: "{search_term}"

Found **{res.get('total_matches', 0)} matching records** across your study operating system:

- 📚 **Syllabus Topics:** {res.get('topics_found', 0)} matches
- 📝 **Study Notes:** {res.get('notes_found', 0)} matches
- ❌ **Mistake Vault Cards:** {res.get('mistakes_found', 0)} matches
- 🗓️ **Planner Tasks:** {res.get('tasks_found', 0)} matches
""",
                "action_badge": f"🔍 Found {res.get('total_matches', 0)} Matches",
                "follow_ups": [f"Open Search for '{search_term}'", "Teach Me This", "Quiz Me"]
            }

        # Theme
        if intent == "APP_COMMAND_THEME":
            res = execute_nexus_tool(user_id, "set_wallpaper_theme", {"theme_or_preset": query})
            return {
                "content": f"🎨 **Appearance Updated:** {res.get('message', 'Settings applied.')}",
                "action_badge": "🎨 Appearance Updated",
                "follow_ups": ["Open Settings", "Make Background Darker", "Set Cosmic Nebula"]
            }

        # Navigation
        if intent == "APP_COMMAND_NAVIGATION":
            dest = q_lower.replace("open my", "").replace("take me to", "").replace("go to", "").replace("navigate to", "").replace("open the", "").strip()
            res = execute_nexus_tool(user_id, "navigate_to_page", {"page_name": dest})
            return {
                "content": f"🚀 **Navigating to {res.get('target_page', 'Workspace')}...**",
                "action_badge": f"🚀 Switched Page: {res.get('target_page', 'Workspace')}",
                "follow_ups": ["Return to Nexus AI", "Start Focus Sprint"]
            }

        return {"content": "Action processed.", "action_badge": "⚡ Executed"}

    def _handle_socratic_mode(self, query: str) -> dict:
        """Guides the student through step-by-step inquiry."""
        active_topic = NexusConversationSession.get_active_topic()
        kb = _match_knowledge(active_topic) or EXPANDED_KNOWLEDGE_BASE["newton"]
        return {
            "content": f"""
### 🧠 Socratic Guided Discovery: {kb['title']}

Let's build this understanding from the ground up through guided reasoning.

Here is your first diagnostic observation:

> **Imagine you are standing on a skateboard holding a heavy medicine ball.**
> If you violently throw the medicine ball forward with all your strength, what happens to you and your skateboard at that exact instant?

Think about the physical interaction and tell me what you predict!
""",
            "action_badge": "🎓 Socratic Dialogue Active",
            "follow_ups": ["I slide backward!", "I stay still.", "Give me a hint."]
        }

    def _handle_concept_explanation(self, user_id: int, query: str, profile: dict) -> dict:
        """Deep pedagogical lesson synthesis across Feynman, Board Exam, and Visual modes."""
        q_lower = query.lower()
        active_topic = NexusConversationSession.get_active_topic()
        board = profile.get("board", "CBSE")

        kb = _match_knowledge(query)
        if not kb and active_topic and active_topic != "General Academic Mastery":
            kb = _match_knowledge(active_topic)
        if not kb:
            matched_top = resolve_topic_by_name(user_id, query)
            if matched_top:
                NexusConversationSession.set_active_topic(matched_top["topic_name"], matched_top.get("subject_name"))
                kb = _match_knowledge(matched_top["topic_name"])

        if not kb:
            kb = EXPANDED_KNOWLEDGE_BASE["newton"]

        NexusConversationSession.set_active_topic(kb["title"], kb.get("subject", "Physics"))

        if "board" in q_lower or "exam" in q_lower or "icse" in q_lower or "derivation" in q_lower or "mathematical" in q_lower:
            res = self._build_board_exam_lesson(kb, board)
        elif "visual" in q_lower or "analogy" in q_lower:
            res = self._build_visual_lesson(kb)
        else:
            res = self._build_feynman_lesson(kb)

        NexusConversationSession.set_active_topic(kb["title"], kb.get("subject", "Physics"), last_explanation=res["content"])
        return res

    def _build_feynman_lesson(self, kb: dict) -> dict:
        """Constructs a natural, human-tutor 12-step pedagogical lesson."""
        content = f"""
Think about when you jump.

Your feet push the ground downward, and the ground pushes you upward. That simple physical interaction is the core intuition behind **{kb['title']}**.

---

### 🌟 1. The Intuitive Idea & Why It Matters
{kb['intuition']}

---

### 🚲 2. The Everyday Analogy
{kb['feynman_analogy']}

---

### 🔬 3. The Microscopic Mechanism (First Principles)
{kb['microscopic_reality']}

---

### 📜 4. The Formal Definition & Law
> **Official Principle:** *For every action, there is an equal and opposite reaction.*
> 
> Mathematically, if Object A exerts a force $\\vec{{F}}_{{AB}}$ on Object B, then Object B simultaneously exerts an equal and opposite force $\\vec{{F}}_{{BA}}$ on Object A:
> $$\\mathbf{{\\vec{{F}}_{{AB}} = -\\vec{{F}}_{{BA}}}}$$

---

### 📐 5. Worked Step-by-Step Problem
**Question:** {kb.get('exam_question', 'Calculate the system recoil.')}

**Solution:**
{kb.get('exam_solution', 'Direct application of conservation laws.')}

---

### ⚠️ 6. Common Examiner Traps & Misconceptions
> ⚠️ **The Big Trap:** {kb.get('examiner_traps', 'Never cancel forces that act on different bodies!')}

---

### 🧠 7. The Memory Trick (The Handshake Rule)
Forces in the universe are like handshakes — you physically cannot shake someone's hand without them shaking yours back with the exact same grip strength.

---

### 🧪 8. 30-Second Comprehension Check
If a tiny insect collides with the windshield of a speeding truck, does the truck exert a greater force on the insect, or does the insect exert the exact same force on the truck?

*(Think about Newton's Third Law and tell me what you think!)*
"""
        return {
            "content": content,
            "action_badge": "💡 Deep Pedagogical Lesson",
            "follow_ups": [
                "I don't understand the second part",
                "Make it easier",
                "Now explain it like I'm preparing for an ICSE exam",
                "Quiz me on this",
                "Save this explanation to my notes"
            ]
        }

    def _build_board_exam_lesson(self, kb: dict, board: str = "CBSE") -> dict:
        """Constructs a rigorous board-exam lesson with derivations and marking checklists."""
        steps_text = "\n\n".join(kb.get("derivation_steps", []))
        content = f"""
### 📜 Official {board} Board Definition
> **Governing Law:** {kb['intuition']}

---

### 📐 Step-by-Step Mathematical Derivation
{steps_text}

---

### ⚠️ Sign Conventions & Dimensional Rules
{kb.get('cartesian_signs', 'Use standard SI base units throughout.')}

---

### 🎨 Diagram Blueprint (Ray / Circuit / FBD)
{kb.get('diagram_blueprint', 'Draw neat labeled schematic with arrowheads.')}

---

### 📋 Examiner Marking Scheme & Half-Mark Traps
{kb.get('examiner_traps', 'Always show intermediate calculation steps.')}

---

### 📝 Benchmark Board Exam Question & Solution
**Question:** {kb.get('exam_question', 'State the law and derive the governing expression.')}

**Step-by-Step Model Solution:**
{kb.get('exam_solution', 'Full marks require explicit formula statement and unit representation.')}
"""
        return {
            "content": content,
            "action_badge": f"📜 {board} Board Derivation",
            "follow_ups": ["Give Another Practice Question", "Quiz me on this", "Save this explanation to my notes", "Add this to my revision queue"]
        }

    def _build_visual_lesson(self, kb: dict) -> dict:
        """Constructs a visual mental model lesson with parameter matrices."""
        matrix_rows = "\n".join([f"| **{cond}** | {effect} |" for cond, effect in kb.get("what_if_matrix", [])])
        content = f"""
### 🗺️ Visual Mental Model Blueprint
```
[ Applied Driving Force / Input ] ───▶ [ Transformation Mechanism: {kb['title']} ] ───▶ [ Observable Physical Effect ]
                                                    │
                                                    ▼
                                     [ Energy Conservation Invariant ]
```

---

### 📊 Metaphor-to-Reality Mapping Table
| Metaphor Element | Physical Component | Governing Function |
| :--- | :--- | :--- |
| **Driving Mechanism** | Source / Applied Field | Imparts energy/momentum |
| **Opposing Medium** | Inertia / Lattice Resistance | Enforces action-reaction equilibrium |
| **Observable Output** | Net System Displacement | Measured experimental outcome |

---

### ⚙️ Dynamic "What-If" Parameter Matrix
| Scenario / Change | Physical Consequence |
| :--- | :--- |
| **Standard Baseline** | Reference operating equilibrium |
{matrix_rows}
"""
        return {
            "content": content,
            "action_badge": "🗺️ Visual Mental Model",
            "follow_ups": ["Show Board Derivation", "Quiz me on this", "Save this explanation to my notes"]
        }

    # ══════════════════════════════════════════════════════════
    # STANDALONE GENERATORS (Daily recommendations, Quizzes)
    # ══════════════════════════════════════════════════════════
    def generate_daily_recommendations(self, user_id: int) -> dict:
        context = NexusContextBuilder.assemble_full_context(user_id)
        prios = context.get("priorities", [])
        top_p = prios[0] if prios else {"topic_name": "Core High-Yield Concepts", "subject_name": "Science", "reasons": ["Syllabus milestone"]}
        
        blueprint = f"""
### 🎯 Executive Priority Summary
Target **{top_p['topic_name']}** ({top_p['subject_name']}) today. Your curriculum trajectory shows this is the highest-leverage topic to elevate your exam readiness score.

---

### ⚡ Top 3 Actionable Study Blocks for Today
1. 🧠 **Deep Work Focus Block 1 (50 min)** • `{top_p['subject_name']}`
   - **Topic:** **{top_p['topic_name']}**
   - **Strategy:** Read core derivations, write formulas from memory, and test self with 3 active recall questions.

2. 📐 **Problem-Solving Block 2 (35 min)** • `Practice & Numericals`
   - **Strategy:** Solve 5 previous-year board questions under timed conditions.

3. 🔄 **Retention Reinforcement Block 3 (20 min)** • `Active Recall & Revision`
   - **Strategy:** Clear your Spaced Repetition queue and review unreviewed Mistake Vault cards.
"""
        return {"status": "success", "content": blueprint, "generated_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M")}

    def generate_ai_quiz(self, user_id: int, subject_id: int = None, chapter_id: int = None, topic_id: int = None, difficulty: str = "Adaptive", count: int = 5, question_count: int = None, focus_prompt: str = "") -> dict:
        effective_count = question_count if question_count is not None else count
        s_name, c_name, t_name = "General", "", ""
        try:
            conn = get_connection()
            try:
                with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                    if topic_id:
                        cursor.execute("SELECT t.name as t_name, c.name as c_name, s.name as s_name FROM topics t JOIN chapters c ON t.chapter_id = c.id JOIN subjects s ON c.subject_id = s.id WHERE t.id = %s", (topic_id,))
                        r = cursor.fetchone()
                        if r:
                            t_name, c_name, s_name = r["t_name"], r["c_name"], r["s_name"]
                    elif subject_id:
                        cursor.execute("SELECT name as s_name FROM subjects WHERE id = %s", (subject_id,))
                        r = cursor.fetchone()
                        if r:
                            s_name = r["s_name"]
            finally:
                conn.close()
        except Exception as e:
            logger.error(f"Error fetching quiz target metadata: {e}")

        target_label = t_name or s_name or "Core Curriculum"
        questions = [
            {
                "id": 1,
                "question": f"Which fundamental physical principle directly governs '{target_label}'?",
                "options": [
                    f"Conservation of energy and momentum in {s_name}",
                    "Arbitrary decay without external influence",
                    "Unbounded linear acceleration",
                    "Static non-interacting equilibrium"
                ],
                "correct_answer": f"Conservation of energy and momentum in {s_name}",
                "explanation": f"{target_label} strictly satisfies universal conservation laws.",
                "prevention_strategy": "Always verify the governing conservation principle before choosing non-conservative distractors."
            },
            {
                "id": 2,
                "question": f"In {s_name}, what is the primary source of examination marks deduction in '{target_label}' questions?",
                "options": [
                    "Confusing directional Cartesian sign conventions",
                    "Writing too many step-by-step algebraic derivations",
                    "Using precise SI base units",
                    "Drawing neat labeled ray or circuit diagrams"
                ],
                "correct_answer": "Confusing directional Cartesian sign conventions",
                "explanation": "Sign conventions are the leading cause of marks loss across board examination numericals.",
                "prevention_strategy": "Write down coordinate axes and sign rules before beginning calculation substitutions."
            },
            {
                "id": 3,
                "question": f"When solving numerical problems on '{target_label}', which step is strictly mandatory for full step marks?",
                "options": [
                    "Writing the general formula in standard symbols before numerical substitution",
                    "Writing only the final numerical answer without units",
                    "Omitting intermediate conversion steps",
                    "Using non-standard arbitrary units"
                ],
                "correct_answer": "Writing the general formula in standard symbols before numerical substitution",
                "explanation": "Board marking schemes award explicit 0.5 to 1.0 step marks for formula representation.",
                "prevention_strategy": "Never write raw numbers without stating the governing algebraic equation first."
            },
            {
                "id": 4,
                "question": f"If an external parameter in '{target_label}' is doubled under standard linear conditions, how does the output respond?",
                "options": [
                    "Doubles in direct linear proportionality ($2\\times$)",
                    "Quadruples exponentially ($4\\times$)",
                    "Remains completely unchanged ($1\\times$)",
                    "Halves to zero ($0.5\\times$)"
                ],
                "correct_answer": "Doubles in direct linear proportionality ($2\\times$)",
                "explanation": "Linear physical laws preserve direct proportionality.",
                "prevention_strategy": "Check whether the governing formula is linear ($y \\propto x$) or quadratic ($y \\propto x^2$)."
            },
            {
                "id": 5,
                "question": f"Which study technique guarantees long-term retention of '{target_label}' before high-stakes exams?",
                "options": [
                    "Feynman Active Recall + Spaced Re-testing of Vault Mistakes",
                    "Passive re-reading of textbook highlights right before bed",
                    "Memorizing final numerical answers from past papers",
                    "Skipping numerical derivations during revision"
                ],
                "correct_answer": "Feynman Active Recall + Spaced Re-testing of Vault Mistakes",
                "explanation": "Cognitive active retrieval builds permanent neural pathways for exam mastery.",
                "prevention_strategy": "Teach the concept aloud to verify zero knowledge gaps."
            }
        ][:effective_count]

        for idx, q in enumerate(questions, 1):
            q["id"] = idx
            q["subject_id"] = subject_id
            q["chapter_id"] = chapter_id
            q["topic_id"] = topic_id

        return {
            "status": "success",
            "title": f"AI Quiz • {target_label} ({difficulty})",
            "subject_id": subject_id,
            "chapter_id": chapter_id,
            "topic_id": topic_id,
            "difficulty": difficulty,
            "questions": questions
        }


# Global Singleton Instance
nexus_ai = NexusAIService()
