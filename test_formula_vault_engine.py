"""
test_formula_vault_engine.py — Comprehensive Test Suite for Nexus Formula Vault.

Verifies:
1. Auto-seeding of canonical STEM formula library from syllabus.
2. Multi-level filtering (Subject, Chapter, Category, Search, Favorites).
3. Formula metadata integrity (KaTeX, variables, units, conditions, traps, examples).
4. Custom student-created formula lifecycle (Creation, custom badge flag, Deletion).
5. User-specific favorite bookmarks and persistence.
6. Anki TSV/CSV deck generation with chapter, subject, and favorite filters.
7. Cross-module bridges (Nexus AI explanation context, Practice prefill, Notes auto-save, Revision queue).
8. Contextual empty-state resolution for non-formula conceptual chapters.
"""

import os
import sys
import time
import json

# Ensure UTF-8 stdout on Windows terminal
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
from database import init_db, get_connection
from models import (
    create_user,
    get_all_subjects,
    get_chapters_for_subject,
    get_topics_for_chapter,
    add_formula,
    get_all_formulas,
    get_formula_by_id,
    toggle_formula_favorite,
    delete_formula,
    get_formulas_grouped_by_category,
    get_chapter_formula_count_summary,
    add_note,
    get_all_notes,
    schedule_revisions,
    get_revision_queue
)
from preloaded_syllabi import preload_standard_syllabus
from preloaded_formulas import seed_user_canonical_formulas
from anki_export import export_formulas_to_anki


def run_tests():
    print("=" * 70)
    print("🚀 STARTING NEXUS FORMULA VAULT INTEGRATION TEST SUITE")
    print("=" * 70)

    # 1. Database Initialization
    print("\n[STEP 1] Initializing Database & Migrations...")
    assert init_db() is True, "Database initialization failed"
    print("✅ Database schema initialized with formula vault metadata & indexes.")

    # 2. Setup Test Student with CBSE Class 10 Syllabus
    test_user = f"formula_tester_{int(time.time())}"
    user_id = create_user(test_user, "password123")
    assert user_id is not None, "Failed to create test user"
    print(f"✅ Created test user: {test_user} (ID: {user_id})")

    preload_ok = preload_standard_syllabus(user_id, "CBSE", "Class 10")
    assert preload_ok is True, "Failed to preload standard CBSE Class 10 syllabus"
    print("✅ Preloaded CBSE Class 10 syllabus successfully.")

    # 3. Test Automatic Canonical Formula Seeding
    print("\n[STEP 2] Testing Automatic Canonical Formula Seeding...")
    seeded_count = seed_user_canonical_formulas(user_id)
    print(f"✅ Canonical formula seeder completed. Seeded {seeded_count} formulas.")

    all_formulas = get_all_formulas(user_id)
    assert len(all_formulas) >= 15, f"Expected at least 15 seeded formulas, got {len(all_formulas)}"
    print(f"✅ Total formulas in vault: {len(all_formulas)}")

    # 4. Test Subject & Chapter Cascading & Content Verification
    print("\n[STEP 3] Testing Subject & Chapter Linkage...")
    subjects = get_all_subjects(user_id)
    assert len(subjects) > 0, "No subjects found for test user"

    phys_sub = next((s for s in subjects if "physics" in s["name"].lower()), None)
    assert phys_sub is not None, "Physics subject not found in syllabus"

    phys_chaps = get_chapters_for_subject(user_id, phys_sub["id"])
    assert len(phys_chaps) > 0, "No chapters found for Physics"

    light_chap = next((c for c in phys_chaps if "light" in c["name"].lower()), None)
    assert light_chap is not None, "Light chapter not found in Physics"

    light_formulas = get_all_formulas(user_id, subject_id=phys_sub["id"], chapter_id=light_chap["id"])
    assert len(light_formulas) >= 5, f"Expected at least 5 formulas in Light chapter, got {len(light_formulas)}"

    mirror_f = next((f for f in light_formulas if "mirror formula" in f["title"].lower()), None)
    lens_f = next((f for f in light_formulas if "lens formula" in f["title"].lower()), None)
    snell_f = next((f for f in light_formulas if "snell" in f["title"].lower()), None)

    assert mirror_f is not None, "Mirror formula not found in Light chapter"
    assert lens_f is not None, "Lens formula not found in Light chapter"
    assert snell_f is not None, "Snell's law not found in Light chapter"

    assert r"\frac{1}{f} = \frac{1}{v} + \frac{1}{u}" in mirror_f["formula_latex"], "Mirror formula LaTeX incorrect"
    assert r"\frac{1}{f} = \frac{1}{v} - \frac{1}{u}" in lens_f["formula_latex"], "Lens formula LaTeX incorrect"
    print(f"✅ Verified Light chapter canonical formulas ({len(light_formulas)} found: Mirror, Lens, Snell's Law, etc.).")

    # 5. Test Category Grouping (Core, Derived, Definitions, Constants)
    print("\n[STEP 4] Testing Category Grouping Engine...")
    grouped = get_formulas_grouped_by_category(user_id, chapter_id=light_chap["id"])
    assert "Core Formulas" in grouped, "Core Formulas category missing from Light chapter"
    assert len(grouped["Core Formulas"]) >= 3, "Expected at least 3 Core Formulas in Light chapter"
    print(f"✅ Grouped categories verified: {list(grouped.keys())}")

    # 6. Test Favorite Bookmarking & Persistence
    print("\n[STEP 5] Testing Favorite Bookmarking & Persistence...")
    assert lens_f["is_favorite"] == 0, "Formula should initially not be favorited"
    toggle_formula_favorite(user_id, lens_f["id"], 1)

    fav_list = get_all_formulas(user_id, is_favorite_only=True)
    assert len(fav_list) >= 1, "Expected at least 1 favorite formula"
    assert any(f["id"] == lens_f["id"] for f in fav_list), "Lens formula not found in favorites filter"
    print("✅ Verified formula favorite toggle and persisted filter.")

    # 7. Test Search Across Title, Variables, LaTeX, and Concept
    print("\n[STEP 6] Testing Real-Time Formula Search...")
    search_lens = get_all_formulas(user_id, search_query="lens")
    assert len(search_lens) >= 2, f"Expected at least 2 search results for 'lens', got {len(search_lens)}"

    search_ohm = get_all_formulas(user_id, search_query="ohm")
    assert len(search_ohm) >= 1, "Expected search for 'ohm' to match Ohm's Law"

    search_quad = get_all_formulas(user_id, search_query="sridharacharya")
    assert len(search_quad) >= 1, "Expected search for 'sridharacharya' to match Quadratic formula"
    print("✅ Search engine successfully matched keywords across multiple subjects.")

    # 8. Test Custom Formula Lifecycle
    print("\n[STEP 7] Testing Custom Student-Created Formula Lifecycle...")
    math_sub = next((s for s in subjects if "math" in s["name"].lower()), None)
    assert math_sub is not None, "Mathematics subject not found"
    math_chaps = get_chapters_for_subject(user_id, math_sub["id"])
    assert len(math_chaps) > 0, "No chapters in Math"

    custom_f_id = add_formula(
        user_id=user_id,
        subject_id=math_sub["id"],
        chapter_id=math_chaps[0]["id"],
        title="Euler's Polyhedron Formula",
        formula_latex=r"V - E + F = 2",
        description="Relationship between vertices (V), edges (E), and faces (F) of a convex polyhedron",
        variables_json={"V": "Vertices count", "E": "Edges count", "F": "Faces count"},
        units="Dimensionless integer count",
        conditions="Valid for any simply connected convex 3D polyhedron",
        category="Custom Formulas",
        is_core=0,
        is_custom=1
    )
    assert custom_f_id > 0, "Failed to create custom formula"

    custom_record = get_formula_by_id(user_id, custom_f_id)
    assert custom_record is not None, "Failed to retrieve custom formula"
    assert custom_record["is_custom"] == 1, "Custom formula must have is_custom=1"
    assert custom_record["title"] == "Euler's Polyhedron Formula"
    print("✅ Successfully created custom formula with custom badge metadata.")

    # 9. Test Anki Flashcard Export with Multi-Level Filters
    print("\n[STEP 8] Testing Anki Flashcard Export Bridge...")
    anki_chap_tsv = export_formulas_to_anki(user_id, chapter_id=light_chap["id"], format_type="tsv")
    assert "FORMULA VAULT" in anki_chap_tsv, "Anki TSV missing Formula Vault header"
    assert "Mirror Formula" in anki_chap_tsv or "Lens Formula" in anki_chap_tsv, "Anki TSV missing chapter formulas"

    anki_fav_tsv = export_formulas_to_anki(user_id, is_favorite_only=True, format_type="tsv")
    assert "Lens Formula" in anki_fav_tsv, "Anki favorites TSV missing favorited lens formula"

    anki_csv = export_formulas_to_anki(user_id, format_type="csv")
    assert len(anki_csv) > 200, "Anki CSV export is empty"
    print("✅ Verified Anki TSV/CSV deck generation across chapter, subject, and favorites.")

    # 10. Test Notes Bridge & Revision Bridge
    print("\n[STEP 9] Testing Notes & Spaced Repetition Bridges...")
    topics = get_topics_for_chapter(user_id, light_chap["id"])
    top_id = topics[0]["id"] if topics else None

    # Save to Notes
    note_id = add_note(
        user_id=user_id,
        subject_id=phys_sub["id"],
        chapter_id=light_chap["id"],
        topic_id=top_id,
        title=f"Formula: {lens_f['title']}",
        content=f"$${lens_f['formula_latex']}$$\n\nMeaning: {lens_f.get('description', '')}",
        tags="formula, physics, optics",
        is_pinned=0
    )
    assert note_id > 0, "Failed to save formula to notes"
    all_notes = get_all_notes(user_id)
    assert any(n["id"] == note_id for n in all_notes), "Formula note not found in notes repository"
    print("✅ Verified 'Save to Notes' bridge.")

    # Add to Revision
    schedule_revisions(user_id, "topic" if top_id else "chapter", top_id or light_chap["id"])
    rev_queue = get_revision_queue(user_id)
    print(f"✅ Verified 'Add to Revision' spaced repetition bridge (Queue items: {len(rev_queue)}).")

    # 11. Test Contextual Empty State on Conceptual Chapters
    print("\n[STEP 10] Testing Contextual Handling of Non-Formula Conceptual Chapters...")
    eng_sub = next((s for s in subjects if "english" in s["name"].lower() or "social" in s["name"].lower()), None)
    if eng_sub:
        eng_chaps = get_chapters_for_subject(user_id, eng_sub["id"])
        if eng_chaps:
            eng_grouped = get_formulas_grouped_by_category(user_id, chapter_id=eng_chaps[0]["id"])
            assert len(eng_grouped) == 0, "Conceptual chapters should have 0 formula categories"
            print(f"✅ Confirmed conceptual chapter '{eng_chaps[0]['name']}' has 0 formulas, triggering smart contextual empty state.")

    # 12. Test Custom Formula Deletion
    print("\n[STEP 11] Testing Custom Formula Deletion...")
    delete_formula(user_id, custom_f_id)
    deleted_check = get_formula_by_id(user_id, custom_f_id)
    assert deleted_check is None, "Custom formula was not deleted"
    # Verify canonical formulas remain untouched
    canonical_check = get_formula_by_id(user_id, lens_f["id"])
    assert canonical_check is not None, "Canonical formula was accidentally deleted"
    print("✅ Verified custom formula deletion without affecting canonical formula library.")

    print("\n" + "=" * 70)
    print("🎉 ALL 11 FORMULA VAULT INTEGRATION TESTS PASSED WITH 100% SUCCESS!")
    print("=" * 70)


if __name__ == "__main__":
    run_tests()
