"""
pages_modules/onboarding_guide.py — Interactive Command Center Guide & Product Tour.

Presents a full interactive walkthrough of the Nexus Student Dashboard:
- Core Philosophy: PLAN → LEARN → PRACTICE → REVIEW → FOCUS → MEASURE
- Detailed breakdown of all 10 modules: What it is, Why use it, How to use it.
- Seamless slide transitions, visual previews, progress capsules, and a prominent 'Skip Guide' option in the bottom right corner.
"""

import streamlit as st
from models import get_user_profile, set_completed_guide


GUIDE_SLIDES = [
    {
        "id": "welcome",
        "step_num": 1,
        "title": "Welcome to Nexus Academic OS",
        "tag": "⚡ PRODUCT COMMAND PHILOSOPHY",
        "tag_color": "#38BDF8",
        "headline": "Your NASA-Grade Personal Study Command Center",
        "summary": "Nexus is engineered to replace scattered notes, unstructured cramming, and exam anxiety with a unified, scientifically grounded cognitive operating system.",
        "icon": "🚀",
        "philosophy_loop": [
            ("🗓️ 1. PLAN", "Align upcoming exams with smart auto-scheduled daily topic targets."),
            ("📚 2. LEARN", "Master curriculum via interactive syllabus, LaTeX notes, and Formula Vault."),
            ("🎯 3. PRACTICE", "Consolidate memory with custom syllabus quizzes and Feynman active recall."),
            ("🧠 4. REVIEW", "Defeat forgetting curve via Spaced Repetition and 7-category Mistake Vault."),
            ("⏱️ 5. FOCUS", "Execute deep single-tasking sprints with ambient soundscapes and XP streaks."),
            ("📊 6. MEASURE", "Track 0-100 Exam Readiness Index and export vector PDF audit reports.")
        ],
        "what_it_is": "A unified high-performance desktop workstation tailored for high school and board exam students (CBSE, ICSE & state boards).",
        "why_use_it": "Students who follow a structured Retrieval + Spaced Repetition + Deep Work routine retain up to 300% more concept knowledge than passive re-readers.",
        "how_to_use": "Follow your daily mission briefing each morning, log deep focus sessions, and resolve mistake cards before exam day.",
        "badge_pills": ["Cognitive Science", "Spaced Repetition", "Zero Clutter", "Cloud Sync"]
    },
    {
        "id": "dashboard",
        "step_num": 2,
        "title": "Module 1: 🏠 Academic Dashboard",
        "tag": "COMMAND & DISPATCH",
        "tag_color": "#4F46E5",
        "headline": "Answers the Most Critical Question: 'What Should I Study Right Now?'",
        "summary": "Eliminates decision fatigue and procrastination by turning your entire syllabus into actionable daily missions and prioritized topic recommendations.",
        "icon": "🏠",
        "features": [
            ("🚀 Today's Mission & Primary CTA", "A consolidated daily checklist aggregating overdue revisions, high-weightage topics, and pending mistakes into a single 'Start Recommended Session' launchpad."),
            ("🎯 Exam Readiness Index (0–100)", "A real-time composite score calculated from syllabus coverage (40%), mastery level (25%), revision consistency (20%), and mistake resolution rate (15%)."),
            ("⏳ Real-Time Exam Countdowns", "Live day-counters for your Unit Tests, Mid-Terms, Pre-Boards, and Final Board Exams with urgency-coded badges."),
            ("⚡ Top 3 Smart Priorities", "Algorithmic topic ranking based on syllabus weightage, low comprehension ratings, and upcoming milestone dates with 1-click Focus launchers.")
        ],
        "what_it_is": "The central mission briefing hub that unifies all academic inputs into clear, prioritized daily actions.",
        "why_use_it": "Eliminates morning paralysis and guesswork so you start productive deep work within 10 seconds of opening your dashboard.",
        "how_to_use": "Open the Dashboard, check your countdowns, and click '🚀 Start Recommended Session' to begin your most urgent task immediately.",
        "badge_pills": ["Readiness Index", "Priority Engine", "Live Countdowns", "Recent Stream"]
    },
    {
        "id": "learn",
        "step_num": 3,
        "title": "Module 2: 📚 Learn Hub",
        "tag": "CURRICULUM & KNOWLEDGE BASE",
        "tag_color": "#10B981",
        "headline": "Syllabus Manager, LaTeX Notes & Formula Vault",
        "summary": "Consolidates your complete official board syllabus, rich notes repository, and KaTeX mathematical equation vault into a single interconnected knowledge workspace.",
        "icon": "📚",
        "features": [
            ("📋 1-Click Syllabus Tracking", "Pre-loaded with official CBSE/ICSE curriculum. Mark topics as completed, rate understanding (1–5 stars), and flag difficult concepts in seconds."),
            ("📝 Notes Repository with Math Keyboard", "Write rich Markdown and LaTeX notes with quick mathematical symbol inserters (fractions, integrals, Greek letters, matrices)."),
            ("📐 KaTeX Formula Vault", "Store essential equations with KaTeX rendering, favorite markers, and instant 1-click export to Anki flashcard decks."),
            ("⚡ 1-Click Topic Action Shortcuts", "Every syllabus topic features direct shortcut buttons ('📝 Note', '💡 Active Recall', '⏱️ Focus') for frictionless context switching.")
        ],
        "what_it_is": "Your complete subject syllabus and knowledge repository organized neatly by Subject → Chapter → Topic.",
        "why_use_it": "Ensures zero syllabus blindspots and connects theoretical notes directly to active testing and flashcard generation.",
        "how_to_use": "Select your subject tab, tick off topics as they are taught in class, rate your confidence, and save core formulas into the vault.",
        "badge_pills": ["Preloaded Syllabus", "LaTeX Support", "KaTeX Formulas", "Anki Exporter"]
    },
    {
        "id": "planner",
        "step_num": 4,
        "title": "Module 3: 🗓️ Planner & Scheduler",
        "tag": "TIME & DEADLINE MANAGEMENT",
        "tag_color": "#F59E0B",
        "headline": "Smart Auto-Scheduler, Daily Tasks & Term Allocator",
        "summary": "Balances your academic workload across calendar days automatically, preventing last-minute all-nighters before major exams.",
        "icon": "🗓️",
        "features": [
            ("⚡ Smart Auto-Scheduler", "Calculates remaining days until your next exam and automatically distributes uncompleted topics into manageable daily study quotas with a single click."),
            ("📋 Today's Action Plan", "Date-picker task board with subject color tags, drag-to-reorder prioritization, and quick completion checkboxes."),
            ("🔄 Overdue Task Rebalancer", "1-click rebalance button that reschedules missed tasks into tomorrow's schedule without breaking streak momentum."),
            ("🎯 Exam Term Allocator", "Allocate specific chapters and topics to Unit Tests, Mid-Terms, or Final Boards to scope your preparation horizon.")
        ],
        "what_it_is": "An intelligent planning engine designed to prevent student burnout through algorithmic pacing.",
        "why_use_it": "Breaking massive 500-page curricula into 3–4 daily topics makes daunting board exams completely manageable.",
        "how_to_use": "Configure your exam date, select your study horizon (e.g. 14 or 30 days), click '⚡ Auto-Schedule Curriculum', and complete your assigned daily targets.",
        "badge_pills": ["Auto Pacing", "Overdue Rebalancer", "Term Scoping", "Goal Tracker"]
    },
    {
        "id": "practice",
        "step_num": 5,
        "title": "Module 4: 🎯 Practice Studio",
        "tag": "ACTIVE RETRIEVAL & TESTING",
        "tag_color": "#EC4899",
        "headline": "Interactive Quiz Engine & Active Recall Studio",
        "summary": "Puts knowledge to the test using active cognitive retrieval, which strengthens memory recall 3x faster than passive re-reading.",
        "icon": "🎯",
        "features": [
            ("🧠 Interactive Quiz Engine", "Generate customized MCQ quizzes filtered by Subject, Chapter, or Difficulty with countdown timers, immediate scoring, and detailed explanations."),
            ("🔁 Mistake Vault Auto-Sync", "Every question answered incorrectly during a quiz is automatically categorized and sent straight to your Mistake Vault for review."),
            ("💡 Feynman Active Recall Studio", "Prompt-based retrieval: Explain complex concepts from memory without looking at notes, utilizing our visual math symbol keyboard."),
            ("⭐ Self-Evaluation & Rubric Scoring", "Grade your retrieval on a 1–5 scale against structured key concept criteria to build deep conceptual metacognition.")
        ],
        "what_it_is": "A rigorous testing environment focused on active retrieval practice and diagnostic assessment.",
        "why_use_it": "Testing yourself exposes illusion of competence and proves whether you truly understand a topic before sitting in an exam hall.",
        "how_to_use": "After learning a topic in Module 2, launch a 5-question Quiz or an Active Recall session to solidify comprehension.",
        "badge_pills": ["Custom Quizzes", "Feynman Method", "Instant Grading", "Auto Mistake Sync"]
    },
    {
        "id": "review",
        "step_num": 6,
        "title": "Module 5: 🧠 Review Hub",
        "tag": "LONG-TERM RETENTION & ERROR DIAGNOSTIC",
        "tag_color": "#8B5CF6",
        "headline": "Spaced Repetition Queue & 7-Category Mistake Vault",
        "summary": "Combines algorithmic memory reinforcement with root-cause error analysis so you never repeat the same mistake twice.",
        "icon": "🧠",
        "features": [
            ("⏳ Automated Spaced Repetition", "Calculates optimal review intervals (1, 3, 7, 14, and 30 days) based on the Ebbinghaus Forgetting Curve to shift knowledge into permanent memory."),
            ("❌ 7 Root-Cause Mistake Categories", "Classify errors into: 1. Conceptual Gap, 2. Calculation Slip, 3. Formula Confusion, 4. Memory Lapse, 5. Careless Reading, 6. Time Pressure, or 7. Application Error."),
            ("⚡ Re-Quiz from Mistakes Generator", "Generate specialized diagnostic re-quizzes built exclusively from past missed questions to verify complete error resolution."),
            ("📦 Anki & CSV Export", "Export your entire mistake registry and revision cards into Anki TSV decks or spreadsheet CSVs for on-the-go revision.")
        ],
        "what_it_is": "A dedicated memory vault and post-mortem error analysis station for targeted score improvement.",
        "why_use_it": "Top rankers improve their scores not by doing more questions, but by systematically diagnosing and eliminating past errors.",
        "how_to_use": "Review your 'Overdue' and 'Due Today' cards every afternoon, log mistakes with prevention strategies, and run a Re-Quiz weekly.",
        "badge_pills": ["Spaced Repetition", "7 Error Categories", "Re-Quiz Engine", "TSV Exporter"]
    },
    {
        "id": "focus",
        "step_num": 7,
        "title": "Module 6: ⏱️ Focus Studio",
        "tag": "DEEP WORK & FLOW STATE",
        "tag_color": "#06B6D4",
        "headline": "Distraction-Free Deep Work with Ambient Soundscapes",
        "summary": "A distraction-free single-tasking studio equipped with scientific productivity timers, ambient audio generators, and automatic XP streak rewards.",
        "icon": "⏱️",
        "features": [
            ("⌛ 3 Scientific Focus Modes", "Choose between Classic Pomodoro (25m), Standard Deep Work (50m), or Ultradian Sprint (90m) with short/long break intervals."),
            ("🎧 5 Ambient Audio Soundscapes", "Built-in soothing background noise generators: Alpha Binaural Beats, Gentle Rain, White Noise, Cozy Coffeehouse, and Lo-Fi Study Chords."),
            ("🎯 Topic Pre-Selection & Notes", "Lock in the exact Subject and Topic you are focusing on before starting to enforce strict single-task discipline."),
            ("🏆 Automatic XP & Analytics Sync", "Every completed focus session records study minutes, increments your daily streak, and awards XP towards higher Rank titles.")
        ],
        "what_it_is": "Your digital study sanctuary designed to shield you from phone notifications and multitasking.",
        "why_use_it": "Deep, uninterrupted single-tasking blocks produce 2x higher retention in half the time compared to distracted study sessions.",
        "how_to_use": "Pre-select your subject and topic, select an ambient soundscape, click 'Start Focus Session', and immerse in distraction-free work.",
        "badge_pills": ["Pomodoro & 50m", "Binaural Beats", "XP Gamification", "Streak Tracker"]
    },
    {
        "id": "ai_analytics_settings",
        "step_num": 8,
        "title": "Modules 7–10: 🤖 AI, 📊 Analytics & ⚙️ Settings",
        "tag": "INTELLIGENCE, METRICS & APPEARANCE",
        "tag_color": "#E11D48",
        "headline": "Autonomous AI Mentor, Visual Analytics & 4K Wallpapers",
        "summary": "Harness AI grounded in your curriculum, track objective mastery trajectories with Plotly charts, and customize your glassmorphic aesthetic.",
        "icon": "🤖",
        "features": [
            ("🤖 Nexus AI Command Center (7 Capabilities)", "Daily Blueprint, Concept Mentor, Quiz Crafter, Study Planner, Diagnostic, Revision Strategist, and Error Diagnostic grounded in your real syllabus data."),
            ("📊 Academic Analytics & Vector PDF", "Interactive Plotly subject mastery distribution, daily focus hour trends, and instant download of publication-grade Vector PDF progress reports."),
            ("🔍 Global Nexus Search", "Instant unified search querying across Topics, Notes, Formulas, Mistakes, and Exam Tasks in under 50ms."),
            ("⚙️ Appearance & 20 4K Wallpapers Studio", "Personalize your aesthetic in Settings → Appearance with 20 curated 4K themes (Cyberpunk, Library, Minimalist, Sci-Fi, Nature), custom uploads, blur and dark overlay contrast sliders.")
        ],
        "what_it_is": "Advanced tools for strategic pedagogical insight, progress verification, and visual customization.",
        "why_use_it": "Provides objective metrics on exam readiness and allows you to curate an aesthetic workspace you actually love using every day.",
        "how_to_use": "Ask Nexus AI to explain difficult concepts, check your weekly mastery charts, and tailor your wallpaper in Settings → Appearance.",
        "badge_pills": ["7 AI Modes", "Vector PDF", "Global Search", "4K Wallpapers"]
    }
]


def render_onboarding_guide(user_id: int):
    """Renders the full-screen interactive onboarding guide with slide transitions and bottom-right skip option."""
    profile = get_user_profile(user_id)
    user_name = profile.get("name", "Student")
    user_class = profile.get("class_name", "Class 10")
    user_board = profile.get("board", "CBSE")

    # Step State Management
    if "guide_step" not in st.session_state:
        st.session_state["guide_step"] = 0

    current_idx = st.session_state["guide_step"]
    current_idx = max(0, min(current_idx, len(GUIDE_SLIDES) - 1))
    slide = GUIDE_SLIDES[current_idx]
    total_steps = len(GUIDE_SLIDES)

    # Styling injection for guide transitions & floating skip button
    st.markdown("""
        <style>
        .nexus-guide-container {
            max-width: 1060px;
            margin: 0 auto 20px auto;
            animation: nexusGuideFadeIn 0.35s ease-out;
        }
        @keyframes nexusGuideFadeIn {
            from { opacity: 0; transform: translateY(12px); }
            to { opacity: 1; transform: translateY(0); }
        }
        .nexus-guide-card {
            background: linear-gradient(135deg, rgba(15, 23, 42, 0.95) 0%, rgba(30, 41, 59, 0.92) 100%);
            border: 1px solid rgba(56, 189, 248, 0.35);
            border-radius: 20px;
            padding: 28px 32px;
            box-shadow: 0 16px 48px rgba(0, 0, 0, 0.5), 0 0 30px rgba(56, 189, 248, 0.12);
            position: relative;
            overflow: hidden;
        }
        .nexus-guide-pill {
            display: inline-block;
            font-size: 0.76rem;
            font-weight: 800;
            letter-spacing: 0.08em;
            text-transform: uppercase;
            padding: 4px 12px;
            border-radius: 20px;
            margin-bottom: 12px;
        }
        .nexus-guide-feature-box {
            background: rgba(15, 23, 42, 0.65);
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 14px;
            padding: 14px 18px;
            margin-bottom: 12px;
            transition: all 0.2s ease;
        }
        .nexus-guide-feature-box:hover {
            border-color: rgba(56, 189, 248, 0.35);
            background: rgba(30, 41, 59, 0.85);
            transform: translateX(4px);
        }
        .nexus-guide-step-dot {
            display: inline-block;
            width: 10px;
            height: 10px;
            border-radius: 50%;
            margin: 0 4px;
            transition: all 0.3s ease;
        }
        .nexus-guide-step-dot.active {
            background: #38BDF8;
            width: 28px;
            border-radius: 10px;
            box-shadow: 0 0 12px #38BDF8;
        }
        .nexus-guide-step-dot.inactive {
            background: rgba(148, 163, 184, 0.3);
        }
        .nexus-guide-badge {
            display: inline-block;
            background: rgba(56, 189, 248, 0.12);
            color: #38BDF8;
            border: 1px solid rgba(56, 189, 248, 0.25);
            border-radius: 8px;
            padding: 3px 10px;
            font-size: 0.78rem;
            font-weight: 600;
            margin-right: 6px;
            margin-top: 6px;
        }
        </style>
    """, unsafe_allow_html=True)

    # Main Guide Container
    st.markdown("<div class='nexus-guide-container'>", unsafe_allow_html=True)

    # Top Header & Step Progress Capsules
    step_dots_html = "".join([
        f"<span class='nexus-guide-step-dot {'active' if i == current_idx else 'inactive'}'></span>"
        for i in range(total_steps)
    ])

    st.markdown(f"""
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; flex-wrap: wrap; gap: 10px;">
            <div style="display: flex; align-items: center; gap: 10px;">
                <span style="font-size: 1.6rem;">{slide['icon']}</span>
                <div>
                    <h2 style="font-family: 'Outfit', sans-serif; font-size: 1.5rem; font-weight: 800; color: #F8FAFC; margin: 0;">
                        {slide['title']}
                    </h2>
                    <span style="font-size: 0.82rem; color: #94A3B8; font-weight: 500;">
                        Step {current_idx + 1} of {total_steps} • Welcome, {user_name} ({user_class} {user_board})
                    </span>
                </div>
            </div>
            <div style="display: flex; align-items: center; gap: 6px;">
                {step_dots_html}
            </div>
        </div>
    """, unsafe_allow_html=True)

    # Main Content Glass Card
    with st.container():
        st.markdown(f"""
            <div class="nexus-guide-card">
                <div class="nexus-guide-pill" style="background: {slide['tag_color']}20; color: {slide['tag_color']}; border: 1px solid {slide['tag_color']}50;">
                    {slide['tag']}
                </div>
                <h3 style="font-family: 'Outfit', sans-serif; font-size: 1.45rem; font-weight: 800; color: #FFFFFF; margin: 4px 0 10px 0;">
                    {slide['headline']}
                </h3>
                <p style="color: #CBD5E1; font-size: 0.96rem; line-height: 1.6; margin-bottom: 20px;">
                    {slide['summary']}
                </p>
            </div>
        """, unsafe_allow_html=True)

        st.markdown("<div style='margin-top: 14px;'></div>", unsafe_allow_html=True)

        # 2-Column Structured Deep-Dive (Left: Core Breakdown / Features | Right: The 3 Core Questions)
        col_left, col_right = st.columns([1.2, 1.1])

        with col_left:
            st.markdown("""
                <div style="font-size: 0.88rem; font-weight: 800; color: #38BDF8; letter-spacing: 0.05em; text-transform: uppercase; margin-bottom: 10px; font-family: 'Outfit', sans-serif;">
                    ✨ Key Modules & Superpowers
                </div>
            """, unsafe_allow_html=True)

            if "philosophy_loop" in slide:
                for loop_title, loop_desc in slide["philosophy_loop"]:
                    st.markdown(f"""
                        <div class="nexus-guide-feature-box">
                            <strong style="color: #F8FAFC; font-size: 0.95rem; font-family: 'Outfit', sans-serif;">{loop_title}</strong>
                            <p style="color: #94A3B8; font-size: 0.85rem; margin: 4px 0 0 0; line-height: 1.45;">{loop_desc}</p>
                        </div>
                    """, unsafe_allow_html=True)
            elif "features" in slide:
                for feat_title, feat_desc in slide["features"]:
                    st.markdown(f"""
                        <div class="nexus-guide-feature-box">
                            <strong style="color: #F8FAFC; font-size: 0.95rem; font-family: 'Outfit', sans-serif;">{feat_title}</strong>
                            <p style="color: #94A3B8; font-size: 0.85rem; margin: 4px 0 0 0; line-height: 1.45;">{feat_desc}</p>
                        </div>
                    """, unsafe_allow_html=True)

        with col_right:
            st.markdown("""
                <div style="font-size: 0.88rem; font-weight: 800; color: #A855F7; letter-spacing: 0.05em; text-transform: uppercase; margin-bottom: 10px; font-family: 'Outfit', sans-serif;">
                    💡 Why & How It Supercharges Your Study
                </div>
            """, unsafe_allow_html=True)

            st.markdown(f"""
                <div style="background: rgba(15, 23, 42, 0.7); border: 1px solid rgba(168, 85, 247, 0.25); border-radius: 14px; padding: 16px 18px; margin-bottom: 12px;">
                    <div style="font-size: 0.82rem; font-weight: 700; color: #A855F7; text-transform: uppercase; letter-spacing: 0.05em;">🎯 What It Is</div>
                    <div style="color: #F1F5F9; font-size: 0.88rem; margin-top: 4px; line-height: 1.5;">{slide['what_it_is']}</div>
                </div>
                <div style="background: rgba(15, 23, 42, 0.7); border: 1px solid rgba(56, 189, 248, 0.25); border-radius: 14px; padding: 16px 18px; margin-bottom: 12px;">
                    <div style="font-size: 0.82rem; font-weight: 700; color: #38BDF8; text-transform: uppercase; letter-spacing: 0.05em;">💡 Why Use This Feature</div>
                    <div style="color: #F1F5F9; font-size: 0.88rem; margin-top: 4px; line-height: 1.5;">{slide['why_use_it']}</div>
                </div>
                <div style="background: rgba(15, 23, 42, 0.7); border: 1px solid rgba(34, 197, 94, 0.25); border-radius: 14px; padding: 16px 18px; margin-bottom: 14px;">
                    <div style="font-size: 0.82rem; font-weight: 700; color: #22C55E; text-transform: uppercase; letter-spacing: 0.05em;">🚀 How To Use It</div>
                    <div style="color: #F1F5F9; font-size: 0.88rem; margin-top: 4px; line-height: 1.5;">{slide['how_to_use']}</div>
                </div>
            """, unsafe_allow_html=True)

            # Badges
            badges_html = "".join([f"<span class='nexus-guide-badge'>✓ {b}</span>" for b in slide.get("badge_pills", [])])
            st.markdown(f"<div>{badges_html}</div>", unsafe_allow_html=True)

    st.markdown("<div style='margin-top: 24px;'></div>", unsafe_allow_html=True)

    # ══════════════════════════════════════════════════════════════════════════
    # NAVIGATION CONTROLS & BOTTOM RIGHT CORNER SKIP OPTION
    # ══════════════════════════════════════════════════════════════════════════
    nav_col1, nav_col2, nav_col3, nav_col4 = st.columns([1.2, 1.8, 1.4, 1.4])

    with nav_col1:
        if current_idx > 0:
            if st.button("⬅️ Previous", use_container_width=True, key="guide_prev_btn"):
                st.session_state["guide_step"] = current_idx - 1
                st.rerun()
        else:
            st.button("⬅️ Previous", disabled=True, use_container_width=True, key="guide_prev_disabled")

    with nav_col2:
        st.markdown(f"""
            <div style="text-align: center; padding-top: 8px; font-size: 0.88rem; color: #94A3B8; font-weight: 600;">
                Step {current_idx + 1} of {total_steps}
            </div>
        """, unsafe_allow_html=True)

    with nav_col3:
        if current_idx < total_steps - 1:
            if st.button("Next ➡️", type="primary", use_container_width=True, key="guide_next_btn"):
                st.session_state["guide_step"] = current_idx + 1
                st.rerun()
        else:
            if st.button("🚀 Launch Command Center", type="primary", use_container_width=True, key="guide_finish_btn"):
                set_completed_guide(user_id, True)
                st.session_state["show_onboarding_guide"] = False
                st.session_state["current_page"] = "🏠 Dashboard"
                st.rerun()

    with nav_col4:
        # ── OPTION TO SKIP THE GUIDE IN BOTTOM RIGHT CORNER ──
        if st.button("⏭️ Skip Guide", type="secondary", use_container_width=True, key="guide_skip_bottom_right"):
            set_completed_guide(user_id, True)
            st.session_state["show_onboarding_guide"] = False
            st.session_state["current_page"] = "🏠 Dashboard"
            st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)
