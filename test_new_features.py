"""
test_new_features.py — Verification suite for:
1. Weekly Progress PDF Report generation (ReportLab vector PDF)
2. Visual LaTeX Math Keyboard palettes & snippets
3. Universal Anki Flashcard Exporter (Mistakes, Active Recall, Formulas)
"""

import os
import time
import json
from models import (
    create_user,
    get_user_by_id,
    add_subject,
    add_chapter,
    add_topic,
    add_mistake,
    add_formula,
    save_active_recall_session,
    log_focus_session
)
from pdf_generator import generate_weekly_progress_pdf
from anki_export import (
    export_mistakes_to_anki,
    export_active_recall_to_anki,
    export_formulas_to_anki,
    export_all_to_anki
)
from components.math_keyboard import MATH_PALETTES


def run_tests():
    print("=================================================================")
    print("[TEST] TESTING NEXUS NEW FEATURES: PDF REPORT, MATH KEYBOARD & ANKI")
    print("=================================================================")

    ts = int(time.time() * 1000)
    uname = f"nexus_pro_{ts}"
    uid = create_user(uname, "StrongPass!123")
    print(f"[OK] Created test user: {uname} (ID: {uid})")

    # 1. Seed Syllabus & Learning Data
    s1 = add_subject(uid, "Physics Core", "#6366F1")
    c1 = add_chapter(uid, s1, "Electromagnetism")
    t1 = add_topic(uid, c1, "Faraday's Law of Induction")

    s2 = add_subject(uid, "Mathematics", "#38BDF8")
    c2 = add_chapter(uid, s2, "Calculus & Integrals")
    t2 = add_topic(uid, c2, "Integration by Parts")

    # 2. Add Mistakes
    add_mistake(
        user_id=uid,
        question="What is the induced EMF in a coil according to Faraday's law?",
        mistake_type="Formula",
        subject_id=s1,
        chapter_id=c1,
        topic_id=t1,
        your_answer="EMF = N * (dPhi / dt)",
        correct_answer="EMF = -N * (dPhi / dt)",
        explanation="Lenz's law requires the negative sign to oppose the change in magnetic flux.",
        prevention_strategy="Always remember the negative sign representing Lenz's law."
    )
    add_mistake(
        user_id=uid,
        question="Evaluate the integral of ln(x) dx.",
        mistake_type="Conceptual",
        subject_id=s2,
        chapter_id=c2,
        topic_id=t2,
        your_answer="1/x + C",
        correct_answer="x ln(x) - x + C",
        explanation="Use integration by parts with u = ln(x) and dv = dx.",
        prevention_strategy="Use the ILATE rule when picking parts."
    )

    # 3. Add Formulas
    add_formula(
        user_id=uid,
        subject_id=s1,
        chapter_id=c1,
        title="Faraday-Lenz Induction Law",
        formula_latex=r"\mathcal{E} = -N \frac{d\Phi_B}{dt}",
        description="Induced electromotive force opposes rate of change of magnetic flux."
    )
    add_formula(
        user_id=uid,
        subject_id=s2,
        chapter_id=c2,
        title="Integration by Parts Formula",
        formula_latex=r"\int u \, dv = u v - \int v \, du",
        description="ILATE priority selection rule applies."
    )

    # 4. Add Active Recall Sessions
    save_active_recall_session(
        user_id=uid,
        topic_id=t1,
        prompt_text="Explain Faraday's Law from first principles and write the governing equation.",
        user_response="Whenever there is a change in magnetic flux linked with a circuit, an EMF is induced.",
        evaluation_feedback="Solid definition. Remember to emphasize Lenz's opposing sign.",
        understanding_score=4
    )

    # 5. Add Focus Sessions
    log_focus_session(uid, 45, subject_id=s1, notes="Faraday's Law Derivations")
    log_focus_session(uid, 60, subject_id=s2, notes="Calculus Problem Set")
    print("[OK] Seeded comprehensive multi-subject academic records.")

    # ── TEST 1: PDF REPORT GENERATION ──
    print("\n--- 1. Testing Weekly Progress PDF Report Generation ---")
    pdf_7 = generate_weekly_progress_pdf(uid, days=7)
    assert isinstance(pdf_7, bytes), "PDF output must be bytes"
    assert len(pdf_7) > 2000, f"PDF file size too small: {len(pdf_7)} bytes"
    assert pdf_7.startswith(b"%PDF-"), "Generated file must have standard %PDF- header"
    print(f"[PASS] 7-Day Progress PDF generated successfully ({len(pdf_7)} bytes)")

    pdf_30 = generate_weekly_progress_pdf(uid, days=30)
    assert len(pdf_30) > 2000, "30-day PDF generation failed"
    assert pdf_30.startswith(b"%PDF-"), "30-day PDF header invalid"
    print(f"[PASS] 30-Day Progress PDF generated successfully ({len(pdf_30)} bytes)")

    # ── TEST 2: ANKI FLASHCARD EXPORT ENGINE ──
    print("\n--- 2. Testing Universal Anki Flashcard Exporter ---")
    mst_tsv = export_mistakes_to_anki(uid, format_type="tsv")
    assert "#separator:Tab" in mst_tsv, "Anki TSV must contain #separator:Tab header"
    assert "#html:true" in mst_tsv, "Anki TSV must contain #html:true header"
    assert "Faraday" in mst_tsv, "Mistake question must be in export"
    assert "Lenz" in mst_tsv, "Mistake explanation must be in export"
    print("[PASS] Mistake Vault Anki TSV export verified.")

    mst_csv = export_mistakes_to_anki(uid, format_type="csv")
    assert "Front" in mst_csv and "Back" in mst_csv, "CSV header missing Front/Back"
    print("[PASS] Mistake Vault CSV export verified.")

    rec_tsv = export_active_recall_to_anki(uid, format_type="tsv")
    assert "#separator:Tab" in rec_tsv, "Active recall TSV header missing"
    assert "ACTIVE RECALL" in rec_tsv, "Active recall card badge missing"
    print("[PASS] Active Recall Anki TSV export verified.")

    form_tsv = export_formulas_to_anki(uid, format_type="tsv")
    assert r"\mathcal{E}" in form_tsv or r"\Phi_B" in form_tsv, "Formula LaTeX missing in Anki export"
    print("[PASS] Formula Vault Anki TSV export verified.")

    master_tsv = export_all_to_anki(uid, format_type="tsv")
    assert len(master_tsv.strip().split("\n")) >= 4, "Master Anki TSV must contain all cards"
    print("[PASS] Master Multi-Deck Anki export verified.")

    # ── TEST 3: VISUAL LATEX MATH KEYBOARD PALETTES ──
    print("\n--- 3. Testing Visual LaTeX Math Keyboard Palettes ---")
    assert len(MATH_PALETTES) >= 5, "Math keyboard must have at least 5 categories"
    for cat_name, items in MATH_PALETTES.items():
        assert len(items) >= 8, f"Category '{cat_name}' must have rich symbol selection"
        for label, snippet in items:
            assert isinstance(snippet, str) and len(snippet) > 0, f"Invalid snippet in {cat_name}: {label}"
    print(f"[PASS] Verified {sum(len(v) for v in MATH_PALETTES.values())} mathematical and scientific LaTeX symbol templates.")

    print("\n=================================================================")
    print("[SUCCESS] ALL NEW FEATURES TESTED & VERIFIED WITH 100% SUCCESS!")
    print("=================================================================")


if __name__ == "__main__":
    run_tests()
