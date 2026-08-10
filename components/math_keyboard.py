"""
math_keyboard.py — Visual Interactive LaTeX Math & Science Equation Keyboard.

Provides a clickable formula builder with categorized symbols, Greek letters,
calculus notations, physical constants, and instant KaTeX live preview.
"""

import streamlit as st

MATH_PALETTES = {
    "🔢 Basic & Algebra": [
        ("a/b Fraction", r"\frac{a}{b}"),
        ("x² Power", r"x^{2}"),
        ("xⁿ Exponent", r"x^{n}"),
        ("xᵢ Subscript", r"x_{i}"),
        ("√x Square Root", r"\sqrt{x}"),
        ("ⁿ√x Nth Root", r"\sqrt[n]{x}"),
        ("± Plus-Minus", r"\pm"),
        ("× Multiply", r"\times"),
        ("÷ Divide", r"\div"),
        ("· Dot", r"\cdot"),
        ("≈ Approx", r"\approx"),
        ("≠ Not Equal", r"\neq"),
        ("≤ Less Equal", r"\le"),
        ("≥ Greater Equal", r"\ge"),
        ("∞ Infinity", r"\infty"),
        ("∝ Proportional", r"\propto"),
    ],
    "🔤 Greek Letters": [
        ("α Alpha", r"\alpha"),
        ("β Beta", r"\beta"),
        ("γ Gamma", r"\gamma"),
        ("δ Delta", r"\delta"),
        ("ε Epsilon", r"\epsilon"),
        ("θ Theta", r"\theta"),
        ("λ Lambda", r"\lambda"),
        ("μ Mu", r"\mu"),
        ("π Pi", r"\pi"),
        ("ρ Rho", r"\rho"),
        ("σ Sigma", r"\sigma"),
        ("τ Tau", r"\tau"),
        ("ϕ Phi", r"\phi"),
        ("ψ Psi", r"\psi"),
        ("ω Omega", r"\omega"),
        ("Δ Delta (Cap)", r"\Delta"),
        ("Ω Ohm/Omega", r"\Omega"),
        ("Σ Summation (Cap)", r"\Sigma"),
    ],
    "📐 Trig & Geometry": [
        ("sin(θ)", r"\sin(\theta)"),
        ("cos(θ)", r"\cos(\theta)"),
        ("tan(θ)", r"\tan(\theta)"),
        ("sin⁻¹(x)", r"\arcsin(x)"),
        ("cos⁻¹(x)", r"\arccos(x)"),
        ("tan⁻¹(x)", r"\arctan(x)"),
        ("Degree °", r"^\circ"),
        ("∠ Angle", r"\angle"),
        ("⊥ Perp", r"\perp"),
        ("∥ Parallel", r"\parallel"),
        ("ΔABC Triangle", r"\Delta ABC"),
    ],
    "📈 Calculus & Vectors": [
        ("∫ Def Integral", r"\int_{a}^{b} f(x) \, dx"),
        ("∫ Indef Integral", r"\int f(x) \, dx"),
        ("∬ Double Int", r"\iint f(x, y) \, dx dy"),
        ("df/dx Derivative", r"\frac{df}{dx}"),
        ("∂f/∂x Partial", r"\frac{\partial f}{\partial x}"),
        ("∑ Summation", r"\sum_{i=1}^{n} x_i"),
        ("lim Limit", r"\lim_{x \to 0}"),
        ("v⃗ Vector", r"\vec{v}"),
        ("î Unit Vector", r"\hat{i}"),
        ("ĵ Unit Vector", r"\hat{j}"),
        ("k̂ Unit Vector", r"\hat{k}"),
        ("∇ Gradient", r"\nabla"),
    ],
    "⚛️ Physics & Chemistry": [
        ("→ Reaction", r"\rightarrow"),
        ("⇌ Equilibrium", r"\rightleftharpoons"),
        ("ΔH Enthalpy", r"\Delta H"),
        ("ΔS Entropy", r"\Delta S"),
        ("ΔG Gibbs", r"\Delta G"),
        ("ℰ EMF", r"\mathcal{E}"),
        ("Φ_B Magnetic Flux", r"\Phi_B"),
        ("μ₀ Permeability", r"\mu_0"),
        ("ε₀ Permittivity", r"\epsilon_0"),
        ("h Plancks", r"h"),
        ("ħ Reduced Planck", r"\hbar"),
        ("c Light Speed", r"c"),
    ]
}


def render_latex_math_keyboard(target_key: str, label: str = "Mathematical & Scientific Equation Builder"):
    """
    Renders an interactive LaTeX Math Keyboard that appends equations into target_key
    and provides a live KaTeX mathematical preview.
    """
    st.markdown(f"""
        <div style="background: rgba(99, 102, 241, 0.06); border: 1px solid rgba(99, 102, 241, 0.2); border-radius: 12px; padding: 12px 16px; margin: 10px 0 16px 0;">
            <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 8px;">
                <div style="display: flex; align-items: center; gap: 8px;">
                    <span style="font-size: 1.1rem;">⌨️</span>
                    <span style="font-weight: 700; color: var(--nexus-text-title); font-size: 0.95rem;">{label}</span>
                </div>
                <span style="font-size: 0.75rem; color: #6366F1; font-weight: 600; background: rgba(99, 102, 241, 0.12); padding: 2px 8px; border-radius: 10px;">
                    Click to Insert LaTeX
                </span>
            </div>
            <p style="font-size: 0.8rem; color: var(--nexus-text-sub); margin: 0 0 8px 0;">
                Click any scientific symbol or formula template to automatically insert it into your editor.
            </p>
        </div>
    """, unsafe_allow_html=True)

    category_names = list(MATH_PALETTES.keys())
    tabs = st.tabs(category_names)

    for tab_idx, cat in enumerate(category_names):
        with tabs[tab_idx]:
            items = MATH_PALETTES[cat]
            cols = st.columns(4)
            for i, (display_name, latex_snippet) in enumerate(items):
                col = cols[i % 4]
                with col:
                    btn_label = f"{display_name}"
                    if st.button(btn_label, key=f"btn_math_{target_key}_{tab_idx}_{i}", use_container_width=True):
                        cur_val = st.session_state.get(target_key, "")
                        if cur_val and not cur_val.endswith(" "):
                            new_val = cur_val + " " + latex_snippet
                        else:
                            new_val = (cur_val or "") + latex_snippet
                        st.session_state[target_key] = new_val
                        st.rerun()

    # Quick Math Utility Bar
    c_q1, c_q2, c_q3, c_q4 = st.columns([1, 1, 1, 1])
    with c_q1:
        if st.button("➕ Wrap in $$...$$", key=f"wrap_display_{target_key}", use_container_width=True):
            val = st.session_state.get(target_key, "").strip()
            if val and not (val.startswith("$$") and val.endswith("$$")):
                st.session_state[target_key] = f"$${val}$$"
                st.rerun()
    with c_q2:
        if st.button("➕ Wrap in $...$", key=f"wrap_inline_{target_key}", use_container_width=True):
            val = st.session_state.get(target_key, "").strip()
            if val and not (val.startswith("$") and val.endswith("$")):
                st.session_state[target_key] = f"${val}$"
                st.rerun()
    with c_q3:
        if st.button("➕ Add Parentheses ( )", key=f"add_paren_{target_key}", use_container_width=True):
            val = st.session_state.get(target_key, "")
            st.session_state[target_key] = (val + r" \left( \right) ").strip()
            st.rerun()
    with c_q4:
        if st.button("🧹 Clear Equation", key=f"clear_{target_key}", use_container_width=True):
            st.session_state[target_key] = ""
            st.rerun()

    # Live KaTeX Equation Preview
    preview_text = st.session_state.get(target_key, "")
    if preview_text:
        st.markdown("""
            <div style="font-size: 0.8rem; font-weight: 700; color: #6366F1; text-transform: uppercase; letter-spacing: 0.05em; margin: 12px 0 4px 0;">
                ✨ KaTeX Live Equation Preview:
            </div>
        """, unsafe_allow_html=True)
        try:
            clean_math = preview_text.replace("$$", "").replace("$", "").strip()
            st.latex(clean_math)
        except Exception:
            st.markdown(f"*{preview_text}*")
