"""
pdf_generator.py — Nexus Academic Progress & Weekly Performance PDF Report Generator.

Generates high-resolution, beautifully styled vector PDF reports using ReportLab.
Includes:
- Executive Student KPI Callout Grid
- Daily Study Velocity & Focus Hours Breakdown
- Subject Mastery & Topic Completion Matrix
- Mistake Vault Health & Resolution Rate
- Active Recall & Spaced Repetition Metrics
- AI Pedagogical Action Plan & Strategic Next Steps
"""

import io
import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    KeepTogether,
    HRFlowable
)
from reportlab.pdfgen import canvas

from models import (
    get_user_by_id,
    get_user_settings,
    calculate_exam_readiness_score,
    get_focus_analytics,
    get_all_subjects_with_stats,
    get_mistake_analytics,
    get_recall_stats,
    get_quiz_history
)
import logging
from ai_service import nexus_ai

logger = logging.getLogger(__name__)


class NumberedCanvas(canvas.Canvas):
    """Two-pass canvas to dynamically compute and render total page count footer."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_number(num_pages)
            super().showPage()
        super().save()

    def draw_page_number(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#64748B"))
        # Header accent bar
        self.setStrokeColor(colors.HexColor("#6366F1"))
        self.setLineWidth(1)
        self.line(40, 755, 572, 755)
        
        # Footer
        self.setStrokeColor(colors.HexColor("#E2E8F0"))
        self.line(40, 45, 572, 45)
        self.drawString(40, 32, "NEXUS ACADEMIC OPERATING SYSTEM • CONFIDENTIAL STUDENT REPORT")
        page_text = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(572, 32, page_text)
        self.restoreState()


def generate_weekly_progress_pdf(user_id: int, days: int = 7) -> bytes:
    """
    Generates a complete, multi-page weekly progress PDF report for the given student.
    Returns bytes buffer ready for Streamlit download button.
    """
    user = get_user_by_id(user_id) or {"username": "Student", "email": "student@nexus.edu"}
    settings = get_user_settings(user_id) or {}
    student_name = user.get("username", "Nexus Scholar").title()
    student_grade = settings.get("grade", "Class 10")
    student_board = settings.get("board", "CBSE")
    target_exam = settings.get("target_exam", "Annual Board Exam")
    
    end_date = datetime.date.today()
    start_date = end_date - datetime.timedelta(days=days - 1)
    date_range_str = f"{start_date.strftime('%b %d, %Y')} – {end_date.strftime('%b %d, %Y')}"
    gen_timestamp = datetime.datetime.now().strftime("%B %d, %Y at %I:%M %p")

    # ── Fetch Data Subsystems ──
    readiness = calculate_exam_readiness_score(user_id)
    comp_score = readiness.get("composite_score", readiness.get("readiness_score", 70))
    breakdown = readiness.get("breakdown", {})
    
    focus_data = get_focus_analytics(user_id, days=days)
    total_focus_min = focus_data.get("total_minutes", 0)
    total_focus_hours = round(total_focus_min / 60.0, 1)
    focus_sessions_count = focus_data.get("session_count", 0)
    daily_focus = focus_data.get("daily_breakdown", [])
    
    subjects_stats = get_all_subjects_with_stats(user_id) or []
    total_topics_all = sum(s.get("total_topics", 0) for s in subjects_stats)
    completed_topics_all = sum(s.get("completed", 0) for s in subjects_stats)
    overall_progress_pct = round((completed_topics_all / max(total_topics_all, 1)) * 100, 1)
    
    mistakes_data = get_mistake_analytics(user_id) or {}
    total_mistakes = mistakes_data.get("total", 0)
    reviewed_mistakes = mistakes_data.get("reviewed", 0)
    resolution_rate = round((reviewed_mistakes / max(total_mistakes, 1)) * 100, 1) if total_mistakes > 0 else 100.0
    dominant_error = mistakes_data.get("dominant_type", "Calculation & Units")
    
    recall_stats = get_recall_stats(user_id) or {}
    total_recalls = recall_stats.get("total_sessions", 0)
    avg_recall_score = recall_stats.get("average_score", 0)
    
    quizzes = get_quiz_history(user_id) or []
    total_quizzes = len(quizzes)

    # AI Pedagogical Strategic Advice
    ai_text = "Maintain daily spaced retrieval and focus on high-yield derivations."
    try:
        if hasattr(nexus_ai, "generate_progress_diagnostic"):
            ai_diag = nexus_ai.generate_progress_diagnostic(user_id) or {}
            ai_text = ai_diag.get("content", ai_text)
        elif hasattr(nexus_ai, "analyze_progress"):
            ai_diag = nexus_ai.analyze_progress(user_id) or {}
            ai_text = ai_diag.get("content", ai_text)
    except Exception as e:
        logger.warning(f"Error fetching AI progress diagnostic for PDF: {e}")

    # ── ReportLab Document Setup ──
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        leftMargin=40,
        rightMargin=40,
        topMargin=45,
        bottomMargin=55
    )

    styles = getSampleStyleSheet()
    
    # Custom Typography Styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=colors.HexColor("#0F172A")
    )
    subtitle_style = ParagraphStyle(
        'DocSub',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=colors.HexColor("#64748B")
    )
    section_heading = ParagraphStyle(
        'SecHeading',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=16,
        textColor=colors.HexColor("#1E1B4B"),
        spaceBefore=12,
        spaceAfter=6
    )
    body_style = ParagraphStyle(
        'BodyTextCustom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13,
        textColor=colors.HexColor("#334155")
    )
    kpi_num_style = ParagraphStyle(
        'KpiNum',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=16,
        leading=18,
        alignment=1, # Center
        textColor=colors.HexColor("#4338CA")
    )
    kpi_label_style = ParagraphStyle(
        'KpiLabel',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=7.5,
        leading=10,
        alignment=1, # Center
        textColor=colors.HexColor("#64748B")
    )
    th_style = ParagraphStyle(
        'TableHead',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8.5,
        leading=11,
        textColor=colors.HexColor("#FFFFFF")
    )
    td_style = ParagraphStyle(
        'TableCell',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=11,
        textColor=colors.HexColor("#1E293B")
    )
    td_bold = ParagraphStyle(
        'TableCellBold',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8.5,
        leading=11,
        textColor=colors.HexColor("#1E293B")
    )

    story = []

    # ══════════════════════════════════════════════════════════
    # HEADER BANNER
    # ══════════════════════════════════════════════════════════
    header_data = [
        [
            Paragraph(f"<b>NEXUS ACADEMIC INTELLIGENCE</b><br/><font size=8 color='#6366F1'>WEEKLY PERFORMANCE & EXAM READINESS AUDIT</font>", title_style),
            Paragraph(f"<b>Student:</b> {student_name}<br/><b>Class & Board:</b> {student_grade} • {student_board}<br/><b>Target:</b> {target_exam}<br/><b>Period:</b> {date_range_str}", subtitle_style)
        ]
    ]
    header_table = Table(header_data, colWidths=[310, 222])
    header_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(header_table)
    story.append(Spacer(1, 10))

    # ══════════════════════════════════════════════════════════
    # EXECUTIVE KPI CALLOUT GRID (2 x 3)
    # ══════════════════════════════════════════════════════════
    readiness_color = "#10B981" if comp_score >= 75 else ("#F59E0B" if comp_score >= 50 else "#EF4444")
    
    kpi_data = [
        [
            [Paragraph(f"<font color='{readiness_color}'>{comp_score}%</font>", kpi_num_style), Paragraph("EXAM READINESS", kpi_label_style)],
            [Paragraph(f"{total_focus_hours} hrs", kpi_num_style), Paragraph(f"TOTAL FOCUS ({focus_sessions_count} sessions)", kpi_label_style)],
            [Paragraph(f"{overall_progress_pct}%", kpi_num_style), Paragraph(f"SYLLABUS COVERED ({completed_topics_all}/{total_topics_all})", kpi_label_style)]
        ],
        [
            [Paragraph(f"{resolution_rate}%", kpi_num_style), Paragraph(f"MISTAKE RESOLUTION ({reviewed_mistakes}/{total_mistakes})", kpi_label_style)],
            [Paragraph(f"{avg_recall_score}%", kpi_num_style), Paragraph(f"ACTIVE RECALL MASTERY ({total_recalls} logs)", kpi_label_style)],
            [Paragraph(f"{total_quizzes}", kpi_num_style), Paragraph("ASSESSMENTS COMPLETED", kpi_label_style)]
        ]
    ]
    
    # Flatten into ReportLab flowable grid
    cell_matrix = []
    for row in kpi_data:
        row_cells = []
        for cell in row:
            row_cells.append(cell)
        cell_matrix.append(row_cells)

    kpi_table = Table(cell_matrix, colWidths=[174, 174, 174])
    kpi_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#F8FAFC")),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor("#E2E8F0")),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    story.append(kpi_table)
    story.append(Spacer(1, 14))

    # ══════════════════════════════════════════════════════════
    # SECTION 1: EXAM READINESS MULTI-FACTOR TRAJECTORY
    # ══════════════════════════════════════════════════════════
    story.append(Paragraph("🎯 Exam Readiness Composite Breakdown", section_heading))
    
    readiness_rows = [
        [
            Paragraph("Metric Factor", th_style),
            Paragraph("Weight", th_style),
            Paragraph("Current Score", th_style),
            Paragraph("Status & Velocity", th_style)
        ],
        [
            Paragraph("Syllabus Topic Completion", td_bold),
            Paragraph("30%", td_style),
            Paragraph(f"{breakdown.get('topic_completion', 0)}%", td_bold),
            Paragraph("On Track" if breakdown.get('topic_completion', 0) >= 60 else "Requires Acceleration", td_style)
        ],
        [
            Paragraph("Spaced Repetition & Retention", td_bold),
            Paragraph("25%", td_style),
            Paragraph(f"{breakdown.get('revision_mastery', 0)}%", td_bold),
            Paragraph("Optimal Retention" if breakdown.get('revision_mastery', 0) >= 70 else "Review Overdue Queue", td_style)
        ],
        [
            Paragraph("Quiz & Assessment Accuracy", td_bold),
            Paragraph("20%", td_style),
            Paragraph(f"{breakdown.get('quiz_performance', 0)}%", td_bold),
            Paragraph("High Precision" if breakdown.get('quiz_performance', 0) >= 75 else "Practice Tricky MCQs", td_style)
        ],
        [
            Paragraph("Mistake Vault Resolution Rate", td_bold),
            Paragraph("15%", td_style),
            Paragraph(f"{breakdown.get('mistake_rate', 0)}%", td_bold),
            Paragraph("Error Traps Cleared" if breakdown.get('mistake_rate', 0) >= 70 else "Unresolved Errors Pending", td_style)
        ],
        [
            Paragraph("Study Consistency & Focus Habit", td_bold),
            Paragraph("10%", td_style),
            Paragraph(f"{breakdown.get('consistency', 0)}%", td_bold),
            Paragraph("Strong Daily Habit" if breakdown.get('consistency', 0) >= 60 else "Increase Daily Sprint Time", td_style)
        ]
    ]

    r_table = Table(readiness_rows, colWidths=[180, 70, 95, 187])
    r_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#4338CA")),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor("#FFFFFF"), colors.HexColor("#F8FAFC")]),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
    ]))
    story.append(r_table)
    story.append(Spacer(1, 14))

    # ══════════════════════════════════════════════════════════
    # SECTION 2: SUBJECT-BY-SUBJECT MASTERY
    # ══════════════════════════════════════════════════════════
    story.append(Paragraph("📚 Subject-by-Subject Mastery & Syllabus Distribution", section_heading))
    
    subj_rows = [
        [
            Paragraph("Subject", th_style),
            Paragraph("Topics Mastered", th_style),
            Paragraph("Completion", th_style),
            Paragraph("Avg Understanding", th_style),
            Paragraph("Revisions Done", th_style)
        ]
    ]

    if subjects_stats:
        for s in subjects_stats:
            tot = s.get("total_topics", 0)
            comp = s.get("completed", 0)
            pct = s.get("percent_completed", 0)
            avg_u = s.get("avg_understanding", 0)
            revs = s.get("revision_done", 0)
            
            subj_rows.append([
                Paragraph(f"<b>{s.get('name', 'General')}</b>", td_bold),
                Paragraph(f"{comp} / {tot}", td_style),
                Paragraph(f"{pct}%", td_bold),
                Paragraph(f"{avg_u}/5.0 ⭐", td_style),
                Paragraph(f"{revs} cycles", td_style)
            ])
    else:
        subj_rows.append([
            Paragraph("No subjects configured", td_style),
            Paragraph("-", td_style),
            Paragraph("-", td_style),
            Paragraph("-", td_style),
            Paragraph("-", td_style)
        ])

    s_table = Table(subj_rows, colWidths=[160, 95, 85, 105, 87])
    s_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#1E1B4B")),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor("#FFFFFF"), colors.HexColor("#F8FAFC")]),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
    ]))
    story.append(s_table)
    story.append(Spacer(1, 14))

    # ══════════════════════════════════════════════════════════
    # SECTION 3: DAILY STUDY TIME & FOCUS VELOCITY
    # ══════════════════════════════════════════════════════════
    story.append(Paragraph("⏱️ Daily Study Velocity & Deep Work Log", section_heading))
    
    focus_rows = [
        [
            Paragraph("Date", th_style),
            Paragraph("Day", th_style),
            Paragraph("Focus Duration", th_style),
            Paragraph("Deep Work Sessions", th_style),
            Paragraph("Productivity Target", th_style)
        ]
    ]

    if daily_focus:
        for df in daily_focus:
            d_str = df.get("date", "")
            mins = df.get("minutes", 0)
            hrs = round(mins / 60.0, 1)
            sess = df.get("sessions", 0)
            status = "Target Met 🎯" if mins >= 120 else ("Moderate ⚡" if mins >= 45 else "Light / Rest")
            
            try:
                dt_obj = datetime.datetime.strptime(d_str, "%Y-%m-%d")
                day_name = dt_obj.strftime("%A")
                date_fmt = dt_obj.strftime("%b %d")
            except Exception:
                day_name = "Day"
                date_fmt = d_str

            focus_rows.append([
                Paragraph(date_fmt, td_bold),
                Paragraph(day_name, td_style),
                Paragraph(f"{hrs} hrs ({mins}m)", td_bold),
                Paragraph(f"{sess} sessions", td_style),
                Paragraph(status, td_style)
            ])
    else:
        # Fallback if no specific sessions
        for i in range(days):
            cur = start_date + datetime.timedelta(days=i)
            focus_rows.append([
                Paragraph(cur.strftime("%b %d"), td_bold),
                Paragraph(cur.strftime("%A"), td_style),
                Paragraph("0.0 hrs", td_style),
                Paragraph("0", td_style),
                Paragraph("Rest / Offline", td_style)
            ])

    f_table = Table(focus_rows, colWidths=[95, 110, 115, 110, 102])
    f_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#312E81")),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 4.5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4.5),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor("#FFFFFF"), colors.HexColor("#F8FAFC")]),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
    ]))
    story.append(f_table)
    story.append(Spacer(1, 14))

    # ══════════════════════════════════════════════════════════
    # SECTION 4: AI PEDAGOGICAL RECOMMENDATIONS & NEXT WEEK ACTION PLAN
    # ══════════════════════════════════════════════════════════
    import re
    import html

    def _format_markdown_for_reportlab(text: str) -> str:
        if not text:
            return "Maintain consistent daily review momentum and practice active recall."
        lines = []
        for line in text.splitlines():
            line_str = line.strip()
            if not line_str:
                lines.append("")
                continue
            # Step 1: Escape raw XML/HTML entities
            escaped = html.escape(line_str)
            # Step 2: Convert markdown syntax safely
            if escaped.startswith("#"):
                clean_h = re.sub(r"^#+\s*", "", escaped)
                lines.append(f"<b>{clean_h}</b>")
            elif escaped.startswith("- ") or escaped.startswith("* "):
                clean_b = escaped[2:].strip()
                clean_b = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", clean_b)
                clean_b = re.sub(r"\*(.+?)\*", r"<i>\1</i>", clean_b)
                lines.append(f"• {clean_b}")
            elif escaped == "---":
                lines.append("<br/>────────────────────────────────────────<br/>")
            else:
                clean_line = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", escaped)
                clean_line = re.sub(r"\*(.+?)\*", r"<i>\1</i>", clean_line)
                lines.append(clean_line)
        return "<br/>".join(lines)

    clean_ai_text = _format_markdown_for_reportlab(ai_text)
    
    try:
        ai_para = Paragraph(f"<b>NEXUS AI STRATEGIC ACTION PLAN & RETENTION ROADMAP</b><br/><br/>{clean_ai_text}", body_style)
    except Exception:
        safe_fallback = html.escape(str(ai_text)[:500])
        ai_para = Paragraph(f"<b>NEXUS AI STRATEGIC ACTION PLAN & RETENTION ROADMAP</b><br/><br/>{safe_fallback}", body_style)

    ai_box_data = [[ai_para]]
    ai_table = Table(ai_box_data, colWidths=[532])
    ai_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#EEF2FF")),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor("#6366F1")),
        ('TOPPADDING', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ('LEFTPADDING', (0, 0), (-1, -1), 12),
        ('RIGHTPADDING', (0, 0), (-1, -1), 12),
    ]))
    story.append(KeepTogether([
        Paragraph("Autonomous Cognitive Interventions", section_heading),
        ai_table
    ]))

    # Build document with two-pass page numbering
    doc.build(story, canvasmaker=NumberedCanvas)
    pdf_bytes = buffer.getvalue()
    buffer.close()
    return pdf_bytes
