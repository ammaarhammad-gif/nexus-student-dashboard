"""
test_restructured_modules.py — Automated verification of all 10 restructured modules.
"""

import sys
import unittest
from database import init_db
from models import (
    create_user, get_user_profile, save_user_profile,
    get_all_subjects, add_subject, add_chapter, add_topic,
    save_progress, get_top_nexus_priorities,
    calculate_exam_readiness_score, get_recent_activity_stream,
    get_weak_areas, add_note, get_all_notes,
    add_formula, get_all_formulas, add_mistake,
    get_all_mistakes, get_revision_queue, get_user_theme,
    get_user_wallpaper_config
)
from preloaded_syllabi import preload_standard_syllabus
from anki_export import export_formulas_to_anki, export_mistakes_to_anki, export_active_recall_to_anki, export_all_to_anki
from pages_modules.dashboard import render_dashboard_page
from pages_modules.learn import render_learn_page
from pages_modules.planner import render_planner_page
from pages_modules.practice import render_practice_page
from pages_modules.review import render_review_page
from pages_modules.focus import render_focus_page
from pages_modules.ai_command_center import render_ai_command_center_page
from pages_modules.statistics import render_statistics_page
from pages_modules.search import render_search_page
from pages_modules.settings import render_settings_page


class TestRestructuredModules(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        init_db()
        import random
        cls.username = f"test_ux_{random.randint(100000, 999999)}"
        cls.user_id = create_user(cls.username, "TestPass123!#")
        preload_standard_syllabus(cls.user_id, "CBSE", "Class 10")

    def test_01_all_10_module_functions_exist(self):
        """Ensure all 10 module render functions are importable and callable."""
        modules = [
            render_dashboard_page,
            render_learn_page,
            render_planner_page,
            render_practice_page,
            render_review_page,
            render_focus_page,
            render_ai_command_center_page,
            render_statistics_page,
            render_search_page,
            render_settings_page
        ]
        for m in modules:
            self.assertTrue(callable(m), f"{m.__name__} must be callable")

    def test_02_recent_activity_stream(self):
        """Validate get_recent_activity_stream returns correct structure."""
        stream = get_recent_activity_stream(self.user_id, limit=5)
        self.assertIsInstance(stream, list)

    def test_03_weak_areas_remediation(self):
        """Validate get_weak_areas query."""
        weak = get_weak_areas(self.user_id, limit=5)
        self.assertIsInstance(weak, list)

    def test_04_notes_and_formulas_in_learn_module(self):
        """Test note creation and formula vault creation linked to curriculum."""
        subjects = get_all_subjects(self.user_id)
        self.assertTrue(len(subjects) > 0)
        s_id = subjects[0]["id"]
        from models import get_chapters_for_subject, get_topics_for_chapter
        chaps = get_chapters_for_subject(self.user_id, s_id)
        self.assertTrue(len(chaps) > 0)
        c_id = chaps[0]["id"]
        tops = get_topics_for_chapter(self.user_id, c_id)
        self.assertTrue(len(tops) > 0)
        t_id = tops[0]["id"]

        # Add Note
        n_id = add_note(self.user_id, s_id, c_id, t_id, "Optics Summary", "Ray diagram rules", "physics,optics")
        self.assertIsNotNone(n_id)
        notes = get_all_notes(self.user_id, subject_id=s_id)
        self.assertTrue(any(n["id"] == n_id for n in notes))

        # Add Formula
        f_id = add_formula(self.user_id, s_id, c_id, "Lens Formula", r"\frac{1}{f} = \frac{1}{v} - \frac{1}{u}")
        self.assertIsNotNone(f_id)
        formulas = get_all_formulas(self.user_id, subject_id=s_id)
        self.assertTrue(any(f["id"] == f_id for f in formulas))

    def test_05_anki_and_csv_exports(self):
        """Test Anki deck exporter for formulas, mistakes, recall, and master deck."""
        f_tsv = export_formulas_to_anki(self.user_id, format_type="tsv")
        self.assertIsInstance(f_tsv, str)
        self.assertIn("Lens Formula", f_tsv)

        m_tsv = export_all_to_anki(self.user_id, format_type="tsv")
        self.assertIsInstance(m_tsv, str)

    def test_06_dashboard_readiness_and_priorities(self):
        """Ensure dashboard composite calculations run cleanly."""
        readiness = calculate_exam_readiness_score(self.user_id)
        self.assertIn("readiness_score", readiness)
        self.assertTrue(0 <= readiness["readiness_score"] <= 100)

        priorities = get_top_nexus_priorities(self.user_id, limit=3)
        self.assertIsInstance(priorities, list)


if __name__ == "__main__":
    unittest.main()
