---

## 2. Comprehensive Bottleneck Inventory

| Component / Action | Current Bottleneck | Estimated Latency | Proposed Remediation |
| :--- | :--- | :--- | :--- |
| **Syllabus Checkbox** | `checked != is_completed` calls `save_progress` → `st.cache_data.clear()` → `st.rerun()` → 18 SQL queries. | 3,800ms | Wrap topics in `@st.fragment`. Update in-memory session state optimistically (<50ms). Animate progress bar & XP toast. Persist in background. |
| **Daily Planner Checkbox** | `toggle_daily_plan` triggers global cache wipe & whole-page script rerun. | 3,200ms | Wrap planner table in `@st.fragment`. Optimistic task tick + `+15 XP` float + background DB sync. |
| **Spaced Repetition Queue** | `complete_adaptive_revision` triggers full review tab reload. | 3,100ms | Wrap review cards in `@st.fragment`. Instant optimistic card removal + `+50 XP` micro-toast. |
| **Focus Studio Timer** | Static text display (`25:00`) with no real-time countdown unless page reloads. | N/A | Implement client-side 60fps JavaScript/HTML countdown timer with circular progress and `@st.fragment` session logging. |
| **Active Quiz Player** | Radio button selections and question transitions trigger full form rerenders. | 2,500ms | Local state caching for questions with `@st.fragment`. Instant option selection without DB roundtrips until final submit. |
| **Nexus AI Responses** | Full response is buffered before displaying; user waits 5 seconds on blank chat. | 4,000ms – 6,000ms | Immediate *"🧠 Nexus is thinking..."* skeleton state + progressive streaming token output (`st.write_stream`). |
| **Dashboard Metrics** | Progress bars and counters jump abruptly without animation. | N/A | Add CSS `@keyframes` with `cubic-bezier(0.4, 0, 0.2, 1)` easing and smooth number interpolation. |

---

## 3. Optimistic UI & Modern Streamlit Architecture Plan

```
USER ACTION (Click Checkbox / Button)
               │
               ▼  (<10ms)
    ┌────────────────────────────────────────┐
    │ 1. IMMEDIATELY UPDATE LOCAL STATE      │
    │    (st.session_state optimistic cache) │
    └────────────────────────────────────────┘
               │
               ▼  (<50ms)
    ┌────────────────────────────────────────┐
    │ 2. PLAY MICRO-ANIMATION                │
    │    - Checkmark spring animation        │
    │    - Floating "+25 XP" micro-badge     │
    │    - Smooth progress bar transition    │
    └────────────────────────────────────────┘
               │
               ▼  (<100ms)
    ┌────────────────────────────────────────┐
    │ 3. RERUN ONLY LOCAL @st.fragment       │
    │    (Zero top-level page rerun)         │
    └────────────────────────────────────────┘
               │
               ▼  (Background / Async)
    ┌────────────────────────────────────────┐
    │ 4. PERSIST TO POSTGRESQL DATABASE      │
    │    - Targeted single-row update        │
    │    - If error: rollback & toast alert  │
    └────────────────────────────────────────┘
```

---

## 4. Performance Metrics Target

| Metric | Baseline (Before) | Target (After) | Status |
| :--- | :--- | :--- | :--- |
| **Checkbox Perceived Response** | 3,800ms | **<100ms** | 🎯 In Progress |
| **Topic Status Update** | 3,500ms | **<120ms** | 🎯 In Progress |
| **Planner Task Completion** | 3,200ms | **<100ms** | 🎯 In Progress |
| **Spaced Revision Tick** | 3,100ms | **<100ms** | 🎯 In Progress |
| **Focus Studio Clock** | Static | **Smooth 60fps Client-Side** | 🎯 In Progress |
| **AI First Token Feedback** | 4,500ms | **<250ms (Streaming)** | 🎯 In Progress |
| **Progress Bar Transition** | Instant jump | **600–1000ms smooth cubic easing** | 🎯 In Progress |

---

## 5. Next Steps: Implementation Roadmap

1. Implement `styles.py` Motion System (keyframes, animations, progress bar easing, XP floating toast).
2. Implement `ui_optimistic.py` Local State Cache & Optimistic Persistence Helper.
3. Optimize `models.py` by removing global `st.cache_data.clear()` on targeted updates.
4. Upgrade `pages_modules/learn.py` with `@st.fragment` and optimistic topic completion.
5. Upgrade `pages_modules/planner.py` with `@st.fragment` and optimistic task completion.
6. Upgrade `pages_modules/review.py` with `@st.fragment` and optimistic revision cards.
7. Upgrade `pages_modules/focus.py` with client-side interactive Pomodoro timer.
8. Upgrade `pages_modules/practice.py` with instant quiz navigation and mistake resolution.
9. Upgrade `pages_modules/ai_command_center.py` with streaming output and instant thinking indicators.
10. Test and document before/after verification in this document.
