"""
formulas.py — Nexus Formula Vault with KaTeX & LaTeX Mathematical Rendering.
"""

import streamlit as st
from models import (
    add_formula,
    get_all_formulas,
    toggle_formula_favorite,
    delete_formula,
    get_all_subjects,
    get_chapters_for_subject,
    get_topics_for_chapter
)

from components.math_keyboard import render_latex_math_keyboard
from anki_export import export_formulas_to_anki

def render_formulas_page(user_id: int):
    st.markdown("""
        <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; margin-bottom: 20px;">
            <div>
                <div style="display: inline-flex; align-items: center; gap: 6px; background: rgba(56, 189, 248, 0.12); border: 1px solid rgba(56, 189, 248, 0.35); color: #38BDF8; font-size: 0.75rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.08em; padding: 4px 12px; border-radius: 20px; margin-bottom: 8px;">
                    <span>📐</span> <span>MATHEMATICAL & SCIENTIFIC LAWS</span>
                </div>
                <h1 style="font-family: 'Outfit', sans-serif; font-size: 2.2rem; font-weight: 800; margin: 0; color: var(--nexus-text-title);">
                    Formula Vault
                </h1>
                <p style="color: var(--nexus-text-sub); margin: 4px 0 0 0; font-size: 0.95rem;">
                    Instant access to mathematical derivations, chemical equations, and physics laws with clean mathematical formatting.
                </p>
            </div>
        </div>
    """, unsafe_allow_html=True)

    tab_vault, tab_add = st.tabs(["📚 Formula Repository", "➕ Add Formula"])

    with tab_add:
        st.subheader("Add Formula to Vault")
        subjects = get_all_subjects(user_id)
        if not subjects:
            st.warning("Please set up subjects in the Syllabus Manager first.")
        else:
            s_map = {s["name"]: s["id"] for s in subjects}
            c1, c2 = st.columns(2)
            with c1:
                sel_subj_name = st.selectbox("Subject", list(s_map.keys()), key="form_add_subj")
            sel_subj_id = s_map[sel_subj_name]
            
            chapters = get_chapters_for_subject(user_id, sel_subj_id)
            c_map = {c["name"]: c["id"] for c in chapters} if chapters else {}
            
            with c2:
                sel_chap_name = st.selectbox("Chapter", list(c_map.keys()) if c_map else ["None"], key="form_add_chap")
            sel_chap_id = c_map.get(sel_chap_name)

            # Interactive Visual Math Keyboard
            render_latex_math_keyboard("form_add_latex_code", label="Interactive Equation & LaTeX Builder")

            title = st.text_input("Formula Title", placeholder="e.g. Quadratic Formula, Lens Formula, Snell's Law", key="form_add_title")
            latex_code = st.text_area("LaTeX / Math Code", placeholder=r"e.g. x = \frac{-b \pm \sqrt{b^2 - 4ac}}{2a}  or  \frac{1}{f} = \frac{1}{v} - \frac{1}{u}", key="form_add_latex_code")
            desc = st.text_input("Description / Notes", placeholder="e.g. For ax^2 + bx + c = 0, where b^2 - 4ac is discriminant", key="form_add_desc")
            
            if st.button("⚡ Save Formula to Vault", type="primary", use_container_width=True, key="save_form_btn"):
                if not title or not latex_code or not sel_chap_id:
                    st.error("Please provide Title, LaTeX code, and select a Chapter.")
                else:
                    add_formula(user_id, sel_subj_id, sel_chap_id, title, latex_code, description=desc)
                    st.success(f"Formula '{title}' saved successfully!")
                    st.session_state["form_add_latex_code"] = ""
                    st.session_state["form_add_title"] = ""
                    st.session_state["form_add_desc"] = ""
                    st.rerun()

    with tab_vault:
        subjects = get_all_subjects(user_id)
        s_filt_map = {"All Subjects": None}
        if subjects:
            s_filt_map.update({s["name"]: s["id"] for s in subjects})
            
        c_f1, c_f2, c_f3 = st.columns([1, 2, 1])
        with c_f1:
            sel_filt_s = st.selectbox("Filter by Subject", list(s_filt_map.keys()), key="form_filt_subj")
        with c_f2:
            search_txt = st.text_input("🔍 Search Formulas", placeholder="Search title or equation...", key="form_search_q")
        with c_f3:
            # 1-Click Anki Deck Export
            anki_tsv_data = export_formulas_to_anki(user_id, subject_id=s_filt_map[sel_filt_s], format_type="tsv")
            st.download_button(
                label="📥 Export to Anki (.tsv)",
                data=anki_tsv_data,
                file_name=f"Nexus_Formulas_{sel_filt_s.replace(' ', '_')}.tsv",
                mime="text/tab-separated-values",
                use_container_width=True,
                key="dl_form_anki_tsv"
            )
            
        formulas = get_all_formulas(user_id, subject_id=s_filt_map[sel_filt_s])
        if search_txt:
            formulas = [f for f in formulas if search_txt.lower() in f["title"].lower() or search_txt.lower() in f["formula_latex"].lower() or search_txt.lower() in f["description"].lower()]

        if not formulas:
            st.info("No formulas found in the vault. Add formulas to access them instantly during revision!")
        else:
            for f in formulas:
                with st.container():
                    st.markdown(f"""
                        <div class="priority-item-card" style="border-left-color: {f.get('subject_color', '#38BDF8')};">
                            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                                <div style="display: flex; gap: 8px; align-items: center;">
                                    <span style="font-size: 0.75rem; font-weight: 700; color: {f.get('subject_color', '#38BDF8')}; background: rgba(56,189,248,0.1); padding: 2px 8px; border-radius: 12px;">
                                        {f.get('subject_name')}
                                    </span>
                                    <span style="font-size: 0.8rem; color: var(--nexus-text-sub);">{f.get('chapter_name')}</span>
                                </div>
                                <span style="font-size: 0.85rem; color: #F97316;">{'⭐ Favorite' if f.get('is_favorite') else ''}</span>
                            </div>
                            <div style="font-size: 1.1rem; font-weight: 700; color: var(--nexus-text-title); margin-bottom: 8px;">
                                {f['title']}
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    # Render LaTeX
                    st.latex(f["formula_latex"])
                    
                    if f.get("description"):
                        st.caption(f"📝 {f['description']}")
                        
                    c_act1, c_act2, c_act3 = st.columns([1, 1, 4])
                    with c_act1:
                        fav_label = "★ Unfavorite" if f.get("is_favorite") else "☆ Favorite"
                        if st.button(fav_label, key=f"fav_btn_{f['id']}"):
                            toggle_formula_favorite(user_id, f['id'], 0 if f.get("is_favorite") else 1)
                            st.rerun()
                    with c_act2:
                        if st.button("🗑️ Delete", key=f"del_form_{f['id']}"):
                            delete_formula(user_id, f['id'])
                            st.toast("Formula deleted", icon="🗑️")
                            st.rerun()
                    st.markdown("<hr style='margin: 10px 0; opacity: 0.15;'/>", unsafe_allow_html=True)
