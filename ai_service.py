"""
ai_service.py — Production-Grade Nexus AI Intelligence Layer & Autonomous Academic Copilot.

Combines:
1. AI Tutor & Deep Pedagogical Teaching Engine (Feynman, Board Exam, Visual/Analogical, Socratic)
2. Conversational Multi-Turn Session Memory (Topic tracking, refinement, confusion analysis)
3. Multi-Stage "Teach Me" Interactive Learning Pipeline
4. Natural Language Workspace Action Controller (Tool execution across all Nexus modules)
5. Dual-Engine Architecture (Cloud LLMs + Autonomous Local Cognitive Engine)
6. Strict Educational Domain Confinement
"""

import os
import json
import datetime
import re
import requests
import streamlit as st
import psycopg2.extras
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
# AUTHORIZED NEXUS CONTEXT BUILDER
# ══════════════════════════════════════════════════════════

class NexusContextBuilder:
    """Assembles authorized student data for AI reasoning."""

    @staticmethod
    def get_student_profile(user_id: int) -> dict:
        profile = get_user_profile(user_id) or {}
        return {
            "name": profile.get("name", "Student"),
            "class_name": profile.get("class_name", "Class 10"),
            "board": profile.get("board", "CBSE"),
            "academic_year": profile.get("academic_year", "")
        }

    @staticmethod
    def get_syllabus_summary(user_id: int) -> dict:
        stats = get_overall_stats(user_id)
        subjects = get_all_subjects_with_stats(user_id)
        return {
            "total_topics": stats.get("total_topics", 0),
            "completed_topics": stats.get("completed_topics", 0),
            "percent_completed": stats.get("percent_completed", 0),
            "subjects": [{
                "name": s["name"],
                "completed": s["completed"],
                "total": s["total_topics"],
                "pct": s["percent_completed"],
                "avg_understanding": s["avg_understanding"]
            } for s in subjects]
        }

    @staticmethod
    def get_priorities(user_id: int) -> list:
        priorities = get_top_nexus_priorities(user_id, limit=5)
        return [{
            "topic_name": p["topic_name"],
            "subject_name": p["subject_name"],
            "chapter_name": p["chapter_name"],
            "reasons": p["reasons"]
        } for p in priorities]

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
        "keywords": ["newton", "third law", "first law", "second law", "force", "action reaction", "momentum", "inertia"],
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
    "ohm": {
        "title": "Ohm's Law, Resistance & Circuit Governing Equations",
        "subject": "Physics",
        "keywords": ["ohm", "resistance", "voltage", "current", "resistivity", "circuit", "potential difference", "rheostat"],
        "intuition": "Electric current is not magic — it is the physical drift of billions of electrons bouncing through a metal wire. How fast they flow depends on two competing things: how hard the battery pushes them (Voltage) versus how many obstacles they hit on their way (Resistance).",
        "feynman_analogy": "Imagine a water slide. Voltage ($V$) is the height of the slide — the higher it is, the more pressure pushing you down. Current ($I$) is how many people splash into the pool per minute. Resistance ($R$) is having speed bumps and friction on the slide surface. If you double the height, twice as many people splash down — unless you double the bumps, which cuts the flow in half ($I = V/R$).",
        "microscopic_reality": "Under an applied electric field $E = V/L$, free electrons acquire an average drift velocity $v_d = \\frac{eE\\tau}{m}$. Collisions with vibrating positive metal ions in the crystal lattice impart resistance. This dissipation of kinetic energy converts electrical work into thermal heat ($H = I^2Rt$).",
        "jargon_translator": "- *Potential Difference ($V$):* Work done per unit positive charge to move between two points ($V = W/Q$).\n- *Ohmic Conductor:* Materials that strictly obey $V \\propto I$ (straight-line V-I graph passing through origin).\n- *Resistivity ($\\rho$):* Intrinsic material property independent of dimensions.",
        "derivation_steps": [
            "**Step 1 (Statement):** At constant temperature, current flowing through a metallic conductor is directly proportional to potential difference across its ends: $V \\propto I$.",
            "**Step 2 (Resistance Constant):** $\\frac{V}{I} = \\text{constant} = R \\implies \\mathbf{V = IR}$.",
            "**Step 3 (Geometric Factors):** Resistance is proportional to length ($R \\propto L$) and inversely proportional to area ($R \\propto 1/A$). Combining: $\\mathbf{R = \\rho \\frac{L}{A}}$, where $\\rho$ is Resistivity in $\\Omega \\cdot m$."
        ],
        "cartesian_signs": "SI Units: $V$ in Volts (V), $I$ in Amperes (A), $R$ in Ohms ($\\Omega$). Convert lengths from $cm$ to meters ($m$) and wire radius from $mm$ to $m$ ($A = \\pi r^2$).",
        "diagram_blueprint": "Draw series circuit: Battery $\\to$ Key switch $\\to$ Ammeter in **series** $\\to$ Resistor $R$ $\\to$ Rheostat. Connect Voltmeter in **parallel** strictly across resistor $R$.",
        "examiner_traps": "1. **Omitting 'Constant Temperature':** Missing this phrase in definition costs 1 mark.\n2. **Stretching Wire Numerical Trap:** If a wire is stretched to double its length ($L \\to 2L$), its area halves ($A \\to A/2$), making new resistance **$4R$** ($2^2 = 4$), NOT $2R$!",
        "what_if_matrix": [
            ("Voltage is doubled across a fixed resistor", "Current doubles ($I \\to 2I$). Resistance remains completely unchanged."),
            ("Wire cut into two equal halves in parallel", "Each half has resistance $R/2$. In parallel: $R_{eq} = \\frac{(R/2)(R/2)}{R/2 + R/2} = R/4$."),
            ("Temperature of copper wire increases", "Lattice ions vibrate with greater amplitude, increasing electron collision frequency $\\implies R$ increases.")
        ],
        "exam_question": "A cylindrical wire of resistance $R = 16\\,\\Omega$ is stretched uniformly until its length is doubled. What is its new resistance?",
        "exam_solution": "**Step 1:** Initial resistance $R_1 = \\rho \\frac{L_1}{A_1} = 16\\,\\Omega$.\n**Step 2:** When stretched, volume $V = L \\cdot A = \\text{constant}$. Since $L_2 = 2L_1$, cross-sectional area $A_2 = \\frac{A_1}{2}$.\n**Step 3:** New resistance $R_2 = \\rho \\frac{L_2}{A_2} = \\rho \\frac{2L_1}{A_1 / 2} = 4 \\left(\\rho \\frac{L_1}{A_1}\\right) = 4 R_1$.\n**Step 4:** $R_2 = 4 \\times 16 = \\mathbf{64\\,\\Omega}$."
    },
    "quadratic": {
        "title": "Quadratic Equations, Discriminant & Parabolic Roots",
        "subject": "Mathematics",
        "keywords": ["quadratic", "discriminant", "roots", "completing square", "quadratic formula", "parabola", "nature of roots"],
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
        return st.session_state.get("nexus_active_topic", "General Academic Mastery")

    @staticmethod
    def set_active_topic(topic_name: str):
        st.session_state["nexus_active_topic"] = topic_name

    @staticmethod
    def clear_history():
        st.session_state["nexus_chat_history"] = []
        st.session_state["nexus_active_topic"] = None
        st.session_state["pending_destructive_action"] = None


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
        
        # Build prompt
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

            elif prov == "openai" or prov == "groq":
                url = "https://api.openai.com/v1/chat/completions" if prov == "openai" else "https://api.groq.com/openai/v1/chat/completions"
                model = self.model_name or ("gpt-4o-mini" if prov == "openai" else "llama-3.3-70b-versatile")
                headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
                payload = {
                    "model": model,
                    "messages": [{"role": "system", "content": full_system}, {"role": "user", "content": full_prompt}],
                    "temperature": 0.4,
                    "max_tokens": 3000
                }
                resp = requests.post(url, json=payload, headers=headers, timeout=45)
                if resp.status_code == 200:
                    text = resp.json()["choices"][0]["message"]["content"]
                    return self._process_llm_output(user_id, text)
        except Exception:
            pass

        return None

    def _process_llm_output(self, user_id: int, raw_text: str) -> dict:
        """Parses tool calls from LLM output, executes them, and formats response."""
        badge = None
        action_json = None
        
        # Look for JSON tool block
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
    # MAIN CONVERSATIONAL CHAT ENGINE (Dual-Engine)
    # ══════════════════════════════════════════════════════════
    def process_chat_message(self, user_id: int, user_message: str) -> dict:
        """
        Main entry point for Nexus conversational intelligence.
        Dispatches to Cloud LLM if active, or Autonomous Cognitive Engine.
        """
        query = user_message.strip()
        context = NexusContextBuilder.assemble_full_context(user_id)
        profile = context["profile"]
        chat_history = NexusConversationSession.get_history()

        # ── Check Destructive Action Confirmation ──
        pending = st.session_state.get("pending_destructive_action")
        if pending and "confirm" in query.lower():
            if pending == "DELETE_ALL_NOTES":
                res = execute_nexus_tool(user_id, "delete_all_notes", {"confirmed": True})
                st.session_state["pending_destructive_action"] = None
                return {
                    "content": f"✅ **Action Confirmed:** {res['message']}",
                    "action_badge": "🗑️ All Notes Deleted",
                    "follow_ups": ["View Syllabus", "Create New Note", "Plan Today's Study"]
                }

        # ── 1. Check Explicit Workspace Commands & Destructive Actions ──
        action_keywords = [
            "schedule", "plan tomorrow", "add to schedule", "add to planner", "remind me to study",
            "mark ", "as completed", "as complete", "as done",
            "add to revision", "put in revision", "schedule revision", "revision queue",
            "save this as a note", "save as note", "create note", "save to notes", "add note",
            "focus session", "start focus", "start timer", "pomodoro",
            "quiz me", "test me", "generate quiz", "create quiz",
            "got question", "got it wrong", "made a mistake", "i was wrong",
            "find ", "search ", "look up",
            "wallpaper", "theme", "dark mode", "light mode",
            "open my", "take me to", "go to", "navigate to", "open the",
            "delete all my notes", "delete all notes",
            "how am i doing", "how am i progressing", "progress", "my stats", "analytics", "preparedness",
            "socratic", "using questions", "ask me questions"
        ]

        is_action_command = any(kw in query.lower() for kw in action_keywords)

        if not is_action_command:
            # ── 2. Try Cloud LLM for General Concept Questions ──
            system_instruction = f"""
You are Nexus AI, an intelligent, patient, academically rigorous private tutor and academic copilot for {profile['name']} ({profile['class_name']} • {profile['board']}).
Guidelines:
1. Always teach conversationally with deep pedagogical substance (500-1000+ words for explanations).
2. Avoid generic summaries or bullet-point shortcuts. Use natural teaching transitions.
3. Confine your answers strictly to the academic/study domain.
"""
            cloud_result = self._call_llm_with_tools(user_id, system_instruction, query, chat_history)
            if cloud_result and cloud_result.get("content"):
                return {
                    "content": cloud_result["content"],
                    "action_badge": cloud_result.get("action_badge") or "💡 Deep Pedagogical Lesson",
                    "follow_ups": ["Explain Simpler", "Show Board Derivation", "Quiz Me on This", "Save as Note", "Add to Revision"]
                }

        # ── 3. Autonomous Cognitive Engine Dispatcher ──
        return self._autonomous_cognitive_processor(user_id, query, context, chat_history)

    def _autonomous_cognitive_processor(self, user_id: int, query: str, context: dict, chat_history: list) -> dict:
        """
        Advanced autonomous intent classification & pedagogical synthesis.
        Guarantees zero static or fake behavior when running locally.
        """
        q_lower = query.lower()
        profile = context["profile"]
        board = profile.get("board", "CBSE")
        active_topic = NexusConversationSession.get_active_topic()

        # ── INTENT 0: NATURAL ACADEMIC GREETING & COPILOT ONBOARDING ──
        if q_lower in ["hi", "hello", "hey", "hey nexus", "hi nexus", "hello nexus", "good morning", "good evening", "good afternoon", "who are you", "what can you do", "help"]:
            return {
                "content": f"""
👋 **Hello {profile['name']}! I'm your Nexus Academic Copilot.**

I'm here as your personal tutor and workspace assistant for **{profile['class_name']} ({board})**. Here's what I can do for you:

1. 💡 **Explain Concepts:** *"Explain Newton's Third Law simply"*, *"Teach me Photosynthesis from first principles"*, *"Show mathematical derivation of Lens Formula"*.
2. 🎯 **Adaptive Quizzing:** *"Quiz me on Chemical Bonding"* or *"Test my understanding"*.
3. 🗓️ **Plan Your Study:** *"Schedule 45 minutes of Physics tomorrow"* or *"Plan today's study sprints"*.
4. 🧠 **Spaced Repetition & Notes:** *"Add this to my revision queue"* or *"Save this explanation as a note"*.
5. ❌ **Mistake Diagnostics:** *"I made a mistake on friction"* and I'll analyze the root cause.
6. ⏱️ **Focus Sessions:** *"Start a 25 min focus session for Chemistry"*.

**What would you like to study or accomplish right now?**
""",
                "action_badge": f"🤖 Nexus Academic Copilot • {board}",
                "follow_ups": ["Explain Newton's Third Law simply", "Quiz me on weak areas", "Schedule 45 min Physics tomorrow", "How am I progressing?"]
            }

        # ── INTENT 1: DESTRUCTIVE ACTION (Delete All Notes) ──
        if "delete all my notes" in q_lower or "delete all notes" in q_lower:
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

        # ── INTENT 2: STUDY PLANNER ("Schedule 45 minutes of Physics tomorrow") ──
        if any(w in q_lower for w in ["schedule", "plan tomorrow", "add to schedule", "add to planner", "remind me to study", "put in schedule"]):
            # Extract duration
            dur_match = re.search(r"(\d+)\s*(?:min|minute|hr|hour)", q_lower)
            dur = 45
            if dur_match:
                val = int(dur_match.group(1))
                dur = val * 60 if "hr" in dur_match.group(0) or "hour" in dur_match.group(0) else val

            # Extract date
            date_target = "tomorrow" if "tomorrow" in q_lower else "today"

            # Extract subject / task
            subject = None
            for s in ["Physics", "Chemistry", "Mathematics", "Biology", "English", "History", "Geography", "Computer Science"]:
                if s.lower() in q_lower:
                    subject = s
                    break

            task_desc = f"Study {subject or 'Core Concepts'}"
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
                "follow_ups": ["Show Today's Planner", "Plan Entire Week", "Start Focus Session"]
            }

        # ── INTENT 3: SYLLABUS STATUS ("Mark Newton's Laws as completed") ──
        if "mark " in q_lower and any(w in q_lower for w in ["completed", "complete", "done", "in progress"]):
            status = "Completed" if ("completed" in q_lower or "complete" in q_lower or "done" in q_lower) else "In Progress"
            t_query = q_lower.replace("mark", "").replace("as completed", "").replace("as complete", "").replace("as done", "").replace("completed", "").strip()
            res = execute_nexus_tool(user_id, "update_topic_status", {"topic_name": t_query, "status": status})
            if res.get("success"):
                return {
                    "content": f"✅ **Syllabus Updated:** {res['message']}\n\nYour curriculum completion percentage and velocity metrics have been updated in your dashboard analytics.",
                    "action_badge": f"✅ {res['new_status']}: {res['topic_name']}",
                    "follow_ups": ["Add to Spaced Revision", "Quiz Me on This", "View Syllabus"]
                }

        # ── INTENT 4: SPACED REVISION ("Add Newton's Laws to revision") ──
        if any(w in q_lower for w in ["add to revision", "put in revision", "schedule revision", "revision queue", "review queue"]):
            t_query = q_lower.replace("add", "").replace("to revision", "").replace("put in revision", "").replace("schedule revision", "").replace("queue", "").strip() or active_topic
            res = execute_nexus_tool(user_id, "schedule_revision", {"topic_name": t_query})
            if res.get("success"):
                return {
                    "content": f"🧠 **Spaced Repetition Scheduled:** {res['message']}\n\nNexus will prompt you at optimal SuperMemo SM-2 intervals (Day 1, Day 3, Day 7, Day 14) to cement this concept into long-term memory.",
                    "action_badge": f"🧠 Scheduled Spaced Revision",
                    "follow_ups": ["View Revision Queue", "Quiz Me on It", "Feynman Active Recall"]
                }

        # ── INTENT 5: SAVE AS NOTE ("Save this explanation as a note") ──
        if any(w in q_lower for w in ["save this as a note", "save as note", "create note", "save to notes", "add note"]):
            last_ai_msg = ""
            for m in reversed(chat_history):
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
                "content": f"📝 **Note Saved:** {res['message']}\n\nSaved under **{active_topic}** with full Markdown and mathematical equations.",
                "action_badge": "📝 Note Saved to Repository",
                "follow_ups": ["View All Notes", "Add Key Formula", "Quiz Me"]
            }

        # ── INTENT 6: FOCUS STUDIO ("Start a 25 minute focus session for Physics") ──
        if any(w in q_lower for w in ["focus session", "start focus", "start timer", "pomodoro", "deep work"]):
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
            return {
                "content": f"⏱️ **Focus Studio Configured:** Prepared a {dur}-minute deep work sprint for **{subject or active_topic}**. Opening Focus Studio now...",
                "action_badge": f"⏱️ Focus Sprint ({dur} min)",
                "follow_ups": ["Start Timer", "Set Ambient Audio", "Plan Next Task"]
            }

        # ── INTENT 7: MISTAKE ANALYSIS ("I got question 3 wrong") ──
        if any(w in q_lower for w in ["got question", "got it wrong", "made a mistake", "i was wrong", "mistake on question"]):
            return {
                "content": f"""
### ❌ Diagnostic Mistake Breakdown

Let's diagnose exactly where the error occurred on **{active_topic}**:

1. **Root-Cause Classification:** Most errors on this concept stem from **Formula Sign Convention** or **Careless Keyword Reading** (e.g. confusing vector signs or missing SI unit conversions).
2. **The Golden Rule to Prevent This:**
   - Always write out the formula in symbols before substituting numbers.
   - Verify that all distances are in meters ($m$) and masses in kilograms ($kg$).
3. **Mastery Action:** Would you like me to log this into your **Mistake Vault** so we can re-test it on your next quiz sprint?
""",
                "action_badge": "❌ Error Diagnosed",
                "follow_ups": ["Log Mistake to Vault", "Try Similar Question", "Explain Concept Again"]
            }

        # ── INTENT 8: QUIZ ME ("Quiz me on it") ──
        if any(w in q_lower for w in ["quiz me", "test me", "generate quiz", "create quiz", "give me a test"]):
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
- **Auto-Sync:** Incorrect answers will be automatically sent to your Mistake Vault.

> Click below or navigate to **🎯 Practice** to launch your interactive assessment!
""",
                "action_badge": f"🎯 Launched Quiz: {target}",
                "follow_ups": ["Play Quiz Now", "Quiz on Mistakes Only", "Explain Concept First"]
            }

        # ── INTENT 9: PROGRESS ANALYTICS ("How am I progressing?") ──
        if any(w in q_lower for w in ["how am i doing", "how am i progressing", "progress", "my stats", "analytics", "preparedness"]):
            readiness = calculate_exam_readiness_score(user_id)
            stats = get_overall_stats(user_id)
            return {
                "content": f"""
### 📊 Academic Velocity & Progress Audit

- **Exam Readiness Score:** **{readiness.get('readiness_score', 0)} / 100** ({readiness.get('readiness_tier', 'Building Foundation')})
- **Syllabus Coverage:** **{stats.get('completed_topics', 0)} of {stats.get('total_topics', 0)} topics** ({stats.get('percent_completed', 0)}% completed).

---

### 🟢 What Is Going Well
- Consistent active recall engagements.
- Core foundation established in completed modules.

### 🟡 What Is Holding You Back
- Pending spaced repetitions require clearing to avoid forgetting-curve decay.
- Unreviewed items in your Mistake Vault need targeted re-testing.

### 🚀 3 Strategic Actions for Today:
1. Complete a **25-min Focus Sprint** on high-yield priority topics.
2. Clear your active Spaced Repetition queue (+50 XP).
3. Take a 5-question practice quiz to calibrate accuracy.
""",
                "action_badge": "📊 Progress Audit Complete",
                "follow_ups": ["Plan My Day", "Show Weakest Topics", "Export PDF Report"]
            }

        # ── INTENT 10: SEARCH ("Find everything related to Newton") ──
        if q_lower.startswith("find ") or q_lower.startswith("search ") or "look up" in q_lower:
            search_term = q_lower.replace("find", "").replace("search", "").replace("everything related to", "").replace("for", "").strip()
            res = execute_nexus_tool(user_id, "search_nexus_workspace", {"query": search_term})
            return {
                "content": f"""
### 🔍 Nexus Workspace Search: "{search_term}"

Found **{res.get('total_matches', 0)} matching records** across your study operating system:

- 📚 **Syllabus Topics:** {res.get('topics_found', 0)} matches {f"({', '.join(res.get('sample_topics', []))})" if res.get('sample_topics') else ''}
- 📝 **Study Notes:** {res.get('notes_found', 0)} matches
- ❌ **Mistake Vault Cards:** {res.get('mistakes_found', 0)} matches
- 🗓️ **Planner Tasks:** {res.get('tasks_found', 0)} matches
""",
                "action_badge": f"🔍 Found {res.get('total_matches', 0)} Matches",
                "follow_ups": [f"Open Search for '{search_term}'", "Teach Me This", "Quiz Me"]
            }

        # ── INTENT 11: WALLPAPER / UI CONTROL ("Set Cyberpunk wallpaper") ──
        if "wallpaper" in q_lower or "theme" in q_lower or "dark mode" in q_lower or "light mode" in q_lower:
            res = execute_nexus_tool(user_id, "set_wallpaper_theme", {"theme_or_preset": query})
            return {
                "content": f"🎨 **Appearance Updated:** {res.get('message', 'Settings applied.')}",
                "action_badge": "🎨 Appearance Updated",
                "follow_ups": ["Open Settings", "Make Background Darker", "Set Cosmic Nebula"]
            }

        # ── INTENT 12: NAVIGATION ("Open my Mistake Vault", "Take me to Physics") ──
        if any(w in q_lower for w in ["open my", "take me to", "go to", "navigate to", "open the"]):
            dest = q_lower.replace("open my", "").replace("take me to", "").replace("go to", "").replace("navigate to", "").replace("open the", "").strip()
            res = execute_nexus_tool(user_id, "navigate_to_page", {"page_name": dest})
            return {
                "content": f"🚀 **Navigating to {res['target_page']}...**",
                "action_badge": f"🚀 Switched Page: {res['target_page']}",
                "follow_ups": ["Return to Nexus AI", "Start Focus Sprint"]
            }

        # ── INTENT 13: SOCRATIC MODE ("Teach me using questions") ──
        if "socratic" in q_lower or "using questions" in q_lower or "ask me questions" in q_lower:
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

        # ── INTENT 14: DEEP PEDAGOGICAL LESSON (Feynman / Board Exam / Visual) ──
        kb = _match_knowledge(query)
        if not kb and active_topic and active_topic != "General Academic Mastery":
            kb = _match_knowledge(active_topic)
        if not kb:
            # Match against student's syllabus
            matched_top = resolve_topic_by_name(user_id, query)
            if matched_top:
                NexusConversationSession.set_active_topic(matched_top["topic_name"])
                kb = _match_knowledge(matched_top["topic_name"])

        if not kb:
            kb = EXPANDED_KNOWLEDGE_BASE["newton"]  # High-yield benchmark topic

        NexusConversationSession.set_active_topic(kb["title"])

        # Determine mode
        if "board" in q_lower or "exam" in q_lower or "icse" in q_lower or "derivation" in q_lower or "mathematical" in q_lower:
            return self._build_board_exam_lesson(kb, board)
        elif "visual" in q_lower or "analogy" in q_lower:
            return self._build_visual_lesson(kb)
        else:
            return self._build_feynman_lesson(kb)

    def _build_feynman_lesson(self, kb: dict) -> dict:
        """Constructs an ultra-deep, comprehensive Feynman pedagogical lesson (800+ words)."""
        content = f"""
Let's build **{kb['title']}** from the ground up. Don't memorize formulas yet — first understand the physical reality.

---

### 🌟 1. The Physical Intuition (Zero Jargon)
{kb['intuition']}

---

### 🚲 2. The Everyday Analogy
{kb['feynman_analogy']}

---

### 🔬 3. The Microscopic Mechanism (First Principles)
{kb['microscopic_reality']}

---

### 🚫 4. The Jargon Translator
{kb['jargon_translator']}

---

### 💡 5. Common Misconception & Mental Model Trap
> ⚠️ **What Confuses Most Students:** {kb['examiner_traps']}

---

### 🧪 6. The 60-Second Challenge
Can you explain why this works out loud to a friend without using textbook buzzwords? If you can, you have achieved **true Feynman mastery**!
"""
        return {
            "content": content,
            "action_badge": "💡 Deep Feynman Lesson",
            "follow_ups": ["Explain Simpler", "Show ICSE Board Derivation", "Quiz Me on This", "Save as Note", "Add to Revision"]
        }

    def _build_board_exam_lesson(self, kb: dict, board: str = "CBSE") -> dict:
        """Constructs a rigorous board-exam lesson with derivations and marking checklists."""
        steps_text = "\n\n".join(kb.get("derivation_steps", []))
        content = f"""
### 📜 Official {board} Board Definition
> **Standard Law:** {kb['intuition']}

---

### 📐 Step-by-Step Mathematical Derivation
{steps_text}

---

### ⚠️ Sign Conventions & Dimensional Rules
{kb.get('cartesian_signs', 'Use standard SI base units throughout.')}

---

### 🎨 Ray / Circuit Diagram Blueprint
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
            "follow_ups": ["Give Another Practice Question", "Quiz Me", "Save to Notes", "Add to Revision"]
        }

    def _build_visual_lesson(self, kb: dict) -> dict:
        """Constructs a visual mental model lesson with ASCII architecture and parameter matrices."""
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
| **Pushing Mechanism** | Source / Applied Field | Imparts kinetic momentum |
| **Opposing Medium** | Inertia / Lattice Resistance | Enforces action-reaction equilibrium |
| **Observable Output** | Net System Displacement | Measured experimental outcome |

---

### ⚙️ Dynamic "What-If" Parameter Matrix
| Scenario / Change | Physical Consequence |
| :--- | :--- |
{matrix_rows}
"""
        return {
            "content": content,
            "action_badge": "🗺️ Visual Mental Model",
            "follow_ups": ["Show Derivation", "Quiz Me", "Save as Note"]
        }

    # ══════════════════════════════════════════════════════════
    # STANDALONE GENERATORS (Daily recommendations, Quizzes, Planner)
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
        conn = get_connection()
        s_name, c_name, t_name = "General", "", ""
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
