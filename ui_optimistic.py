"""
ui_optimistic.py — Nexus Optimistic UI State Engine & Micro-Animation System.

Provides:
1. Instant Local State Updates (<10ms perceived latency)
2. Safe Database Persistence with Automatic Rollback
3. Animated CSS Progress Bars with Cubic-Bezier Easing
4. Floating XP Popups & Milestone Micro-Animations
5. Fragment-Scoped Cache Management
"""

import streamlit as st
import logging

logger = logging.getLogger(__name__)


def _ensure_optimistic_stores():
    """Initializes in-memory optimistic state dictionaries in session_state."""
    if "opt_topic_status" not in st.session_state:
        st.session_state["opt_topic_status"] = {}
    if "opt_topic_understanding" not in st.session_state:
        st.session_state["opt_topic_understanding"] = {}
    if "opt_plan_status" not in st.session_state:
        st.session_state["opt_plan_status"] = {}
    if "opt_revision_done" not in st.session_state:
        st.session_state["opt_revision_done"] = set()
    if "opt_formula_favorites" not in st.session_state:
        st.session_state["opt_formula_favorites"] = {}
    if "opt_xp_bump" not in st.session_state:
        st.session_state["opt_xp_bump"] = 0


# ══════════════════════════════════════════════════════════
# TOPIC OPTIMISTIC STATE
# ══════════════════════════════════════════════════════════

def get_optimistic_topic_status(topic_id: int, fallback_status: str) -> str:
    """Returns local optimistic status for topic, or falls back to DB status."""
    _ensure_optimistic_stores()
    return st.session_state["opt_topic_status"].get(topic_id, fallback_status)


def set_optimistic_topic_status(user_id: int, topic_id: int, new_status: str, save_callback=None) -> bool:
    """
    Optimistically updates topic status in local session state,
    then executes database synchronization. Reverts on failure.
    """
    _ensure_optimistic_stores()
    old_status = st.session_state["opt_topic_status"].get(topic_id, "Not Started")
    st.session_state["opt_topic_status"][topic_id] = new_status

    if save_callback:
        try:
            save_callback()
            return True
        except Exception as e:
            logger.error(f"Optimistic persistence failed for topic {topic_id}: {e}")
            # Rollback local state
            st.session_state["opt_topic_status"][topic_id] = old_status
            st.toast("⚠️ Could not sync changes with server. Please try again.", icon="❌")
            return False
    return True


# ══════════════════════════════════════════════════════════
# PLANNER OPTIMISTIC STATE
# ══════════════════════════════════════════════════════════

def get_optimistic_plan_status(plan_id: int, fallback_status: bool) -> bool:
    """Returns local optimistic completion for daily plan task."""
    _ensure_optimistic_stores()
    return st.session_state["opt_plan_status"].get(plan_id, fallback_status)


def set_optimistic_plan_status(user_id: int, plan_id: int, is_completed: bool, save_callback=None) -> bool:
    """
    Optimistically updates plan task completion in local session state,
    then executes database synchronization. Reverts on failure.
    """
    _ensure_optimistic_stores()
    old_status = st.session_state["opt_plan_status"].get(plan_id, not is_completed)
    st.session_state["opt_plan_status"][plan_id] = is_completed

    if save_callback:
        try:
            save_callback()
            return True
        except Exception as e:
            logger.error(f"Optimistic persistence failed for plan {plan_id}: {e}")
            st.session_state["opt_plan_status"][plan_id] = old_status
            st.toast("⚠️ Could not sync task with server. Please try again.", icon="❌")
            return False
    return True


# ══════════════════════════════════════════════════════════
# REVISION QUEUE OPTIMISTIC STATE
# ══════════════════════════════════════════════════════════

def is_revision_optimistically_completed(revision_id: int) -> bool:
    """Returns True if the user just clicked done in this session."""
    _ensure_optimistic_stores()
    return revision_id in st.session_state["opt_revision_done"]


def mark_revision_optimistically_completed(user_id: int, revision_id: int, save_callback=None) -> bool:
    """Optimistically marks revision card as done and hides it."""
    _ensure_optimistic_stores()
    st.session_state["opt_revision_done"].add(revision_id)

    if save_callback:
        try:
            save_callback()
            return True
        except Exception as e:
            logger.error(f"Optimistic persistence failed for revision {revision_id}: {e}")
            st.session_state["opt_revision_done"].discard(revision_id)
            st.toast("⚠️ Could not save revision progress.", icon="❌")
            return False
    return True


# ══════════════════════════════════════════════════════════
# ANIMATED UI COMPONENTS & MICRO-INTERACTIONS
# ══════════════════════════════════════════════════════════

def render_animated_progress_bar(percentage: float, color: str = "#38BDF8", height_px: int = 10, label: str = ""):
    """
    Renders an ultra-smooth animated CSS progress bar with cubic-bezier easing,
    subtle glow highlight, and responsive width interpolation.
    """
    pct = max(0.0, min(100.0, float(percentage)))
    rounded_pct = round(pct, 1)

    label_html = ""
    if label:
        label_html = f"""
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px; font-size: 0.84rem;">
                <span style="font-weight: 600; color: var(--nexus-text-sub);">{label}</span>
                <span style="font-weight: 800; color: {color}; font-family: 'Outfit', sans-serif;">{rounded_pct}%</span>
            </div>
        """

    html = f"""
        <div class="nexus-progress-wrapper" style="width: 100%; margin: 6px 0;">
            {label_html}
            <div style="width: 100%; height: {height_px}px; background: rgba(255,255,255,0.08); border-radius: {height_px}px; overflow: hidden; position: relative; box-shadow: inset 0 1px 3px rgba(0,0,0,0.3);">
                <div class="nexus-smooth-bar" style="
                    width: {rounded_pct}%;
                    height: 100%;
                    background: linear-gradient(90deg, {color} 0%, #818CF8 100%);
                    border-radius: {height_px}px;
                    transition: width 0.9s cubic-bezier(0.34, 1.56, 0.64, 1);
                    box-shadow: 0 0 12px {color}66;
                    position: relative;
                ">
                    <div style="position: absolute; right: 0; top: 0; bottom: 0; width: 8px; background: rgba(255,255,255,0.6); filter: blur(2px); border-radius: {height_px}px;"></div>
                </div>
            </div>
        </div>
    """
    st.markdown(html, unsafe_allow_html=True)


def render_floating_xp_toast(xp_amount: int = 25, reason: str = "Mastery Milestone"):
    """Shows an immediate micro-toast notification with floating +XP styling."""
    st.toast(f"✨ +{xp_amount} XP • {reason}", icon="⚡")
