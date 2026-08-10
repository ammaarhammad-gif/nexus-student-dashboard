"""
anki_export.py — Universal Anki & Spaced Repetition Flashcard Deck Exporter.

Supports exporting:
- Mistake Vault error patterns with prevention heuristics
- Active Recall Feynman comprehension prompts
- Formula Vault mathematical laws & derivations

Output Formats:
- Anki TSV (.tsv / .txt) with #separator:Tab, #html:true, tags column
- Universal CSV (.csv) for Quizlet, Notion, RemNote, Sheets
- Programmatic JSON (.json)
"""

import csv
import io
import json
import re
from models import (
    get_all_mistakes,
    get_all_formulas,
    get_recall_history,
    get_all_subjects
)


def _clean_html_text(text: str) -> str:
    """Safely converts plain text line breaks and formatting into Anki-safe HTML."""
    if not text:
        return ""
    # Convert newlines to <br/>
    html = str(text).replace("\r\n", "\n").replace("\r", "\n")
    html = html.replace("\n", "<br/>")
    # Preserve tabs/spaces
    html = html.replace("\t", "    ")
    return html.strip()


def export_mistakes_to_anki(user_id: int, subject_id: int = None, unreviewed_only: bool = False, format_type: str = "tsv") -> str:
    """
    Exports Mistake Vault questions into Anki flashcards.
    """
    mistakes = get_all_mistakes(user_id) or []
    if subject_id:
        mistakes = [m for m in mistakes if m.get("subject_id") == subject_id]
    if unreviewed_only:
        mistakes = [m for m in mistakes if not m.get("reviewed")]

    cards = []
    for m in mistakes:
        s_name = m.get("subject_name", "General").replace(" ", "_")
        c_name = m.get("chapter_name", "").replace(" ", "_")
        t_name = m.get("topic_name", "").replace(" ", "_")
        m_type = m.get("mistake_type", "General").replace(" ", "_")
        is_mastered = "Mastered" if m.get("reviewed") else "Pending_Review"
        
        q_text = m.get("question_text", "No question text")
        correct_ans = m.get("correct_answer", "")
        your_ans = m.get("user_answer", "")
        explanation = m.get("explanation", "")
        prevention = m.get("prevention_rule", m.get("notes", ""))
        
        # Build Front Card HTML
        front_html = f"""<div style="font-family: -apple-system, sans-serif; font-size: 16px; color: #1E293B;">
<div style="display: inline-block; background: #FEE2E2; color: #DC2626; font-size: 11px; font-weight: bold; padding: 2px 8px; border-radius: 4px; margin-bottom: 8px;">
❌ MISTAKE VAULT • {m.get('mistake_type', 'Error')}
</div>
<div style="font-size: 13px; color: #64748B; margin-bottom: 6px;"><b>Subject:</b> {m.get('subject_name', '')} &gt; {m.get('chapter_name', '')}</div>
<div style="font-weight: 600; line-height: 1.5; margin-bottom: 10px;">{_clean_html_text(q_text)}</div>
</div>"""

        # Build Back Card HTML
        back_html = f"""<div style="font-family: -apple-system, sans-serif; font-size: 15px; color: #1E293B; line-height: 1.5;">
<div style="background: #ECFDF5; border: 1px solid #10B981; border-radius: 6px; padding: 8px 12px; margin-bottom: 10px;">
<span style="color: #059669; font-weight: bold;">✅ Correct Answer:</span><br/>
<b>{_clean_html_text(correct_ans)}</b>
</div>"""

        if your_ans and your_ans != correct_ans:
            back_html += f"""<div style="background: #FEF2F2; border: 1px solid #EF4444; border-radius: 6px; padding: 8px 12px; margin-bottom: 10px;">
<span style="color: #DC2626; font-weight: bold;">⚠️ Your Past Error:</span> { _clean_html_text(your_ans) }<br/>
<span style="font-size: 12px; color: #7F1D1D;"><b>Root Trap:</b> {m.get('mistake_type', 'Misconception')}</span>
</div>"""

        if explanation:
            back_html += f"""<div style="margin-bottom: 10px;">
<b style="color: #4338CA;">💡 Step-by-Step Derivation / Solution:</b><br/>
{_clean_html_text(explanation)}
</div>"""

        if prevention:
            back_html += f"""<div style="background: #EEF2FF; border-left: 3px solid #6366F1; padding: 6px 10px; font-size: 13px;">
<b>🛡️ Prevention Checklist:</b> {_clean_html_text(prevention)}
</div>"""
        back_html += "</div>"

        deck_name = f"Nexus::Mistake_Vault::{s_name}"
        tags = f"Nexus MistakeVault {s_name} {c_name} {t_name} {m_type} {is_mastered}".strip()
        tags = re.sub(r'\s+', ' ', tags)

        cards.append({
            "front": front_html,
            "back": back_html,
            "deck": deck_name,
            "tags": tags,
            "subject": m.get("subject_name", ""),
            "type": "Mistake"
        })

    return _format_cards_output(cards, format_type, deck_default="Nexus::Mistake_Vault")


def export_active_recall_to_anki(user_id: int, subject_id: int = None, format_type: str = "tsv") -> str:
    """
    Exports Active Recall prompt cards into Anki flashcards.
    """
    recalls = get_recall_history(user_id) or []
    if subject_id:
        recalls = [r for r in recalls if r.get("subject_id") == subject_id]

    cards = []
    for r in recalls:
        s_name = r.get("subject_name", "General").replace(" ", "_")
        c_name = r.get("chapter_name", "").replace(" ", "_")
        t_name = r.get("topic_name", "").replace(" ", "_")
        score = r.get("score", r.get("understanding_score", 0))
        
        prompt = r.get("prompt", r.get("topic_name", "Recall Prompt"))
        user_response = r.get("user_response", "")
        feedback = r.get("ai_feedback", r.get("evaluation_feedback", ""))

        front_html = f"""<div style="font-family: -apple-system, sans-serif; font-size: 16px; color: #1E293B;">
<div style="display: inline-block; background: #F3E8FF; color: #9333EA; font-size: 11px; font-weight: bold; padding: 2px 8px; border-radius: 4px; margin-bottom: 8px;">
💡 ACTIVE RECALL • FEYNMAN RETRIEVAL
</div>
<div style="font-size: 13px; color: #64748B; margin-bottom: 6px;"><b>Subject:</b> {r.get('subject_name', '')} &gt; {r.get('chapter_name', '')}</div>
<div style="font-weight: 700; line-height: 1.5; color: #1E1B4B;">{_clean_html_text(prompt)}</div>
<div style="font-size: 12px; color: #6B7280; margin-top: 8px;"><i>⚡ Close your eyes and explain this concept from first principles before flipping!</i></div>
</div>"""

        back_html = f"""<div style="font-family: -apple-system, sans-serif; font-size: 15px; color: #1E293B; line-height: 1.5;">
<div style="background: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 6px; padding: 10px; margin-bottom: 10px;">
<b style="color: #4338CA;">🎯 Key Derivations & Model Solution:</b><br/>
{_clean_html_text(feedback or user_response)}
</div>
<div style="font-size: 12px; color: #64748B;">Last Benchmark Score: <b>{score}%</b></div>
</div>"""

        deck_name = f"Nexus::Active_Recall::{s_name}"
        tags = f"Nexus ActiveRecall {s_name} {c_name} {t_name}".strip()
        tags = re.sub(r'\s+', ' ', tags)

        cards.append({
            "front": front_html,
            "back": back_html,
            "deck": deck_name,
            "tags": tags,
            "subject": r.get("subject_name", ""),
            "type": "ActiveRecall"
        })

    return _format_cards_output(cards, format_type, deck_default="Nexus::Active_Recall")


def export_formulas_to_anki(user_id: int, subject_id: int = None, format_type: str = "tsv") -> str:
    """
    Exports Formula Vault items into Anki flashcards with KaTeX / MathJax formatting.
    """
    formulas = get_all_formulas(user_id) or []
    if subject_id:
        formulas = [f for f in formulas if f.get("subject_id") == subject_id]

    cards = []
    for f in formulas:
        s_name = f.get("subject_name", "General").replace(" ", "_")
        c_name = f.get("chapter_name", "").replace(" ", "_")
        title = f.get("title", "Formula")
        latex = f.get("latex_code", "")
        desc = f.get("description", "")

        front_html = f"""<div style="font-family: -apple-system, sans-serif; font-size: 16px; color: #1E293B;">
<div style="display: inline-block; background: #E0F2FE; color: #0284C7; font-size: 11px; font-weight: bold; padding: 2px 8px; border-radius: 4px; margin-bottom: 8px;">
📐 FORMULA VAULT • {f.get('subject_name', '')}
</div>
<div style="font-size: 13px; color: #64748B; margin-bottom: 6px;">{f.get('chapter_name', '')}</div>
<div style="font-size: 18px; font-weight: 700; color: #0369A1;">{_clean_html_text(title)}</div>
</div>"""

        math_display = latex if (latex.startswith("$$") or latex.startswith("$")) else f"$${latex}$$"
        back_html = f"""<div style="font-family: -apple-system, sans-serif; font-size: 15px; color: #1E293B; line-height: 1.5;">
<div style="background: #F0F9FF; border: 1px solid #BAE6FD; border-radius: 6px; padding: 14px; text-align: center; margin-bottom: 10px; font-size: 18px;">
{math_display}
</div>"""
        if desc:
            back_html += f"""<div style="font-size: 13px; color: #475569;">
<b>Notes & Conditions:</b> {_clean_html_text(desc)}
</div>"""
        back_html += "</div>"

        deck_name = f"Nexus::Formulas::{s_name}"
        tags = f"Nexus Formulas {s_name} {c_name}".strip()
        tags = re.sub(r'\s+', ' ', tags)

        cards.append({
            "front": front_html,
            "back": back_html,
            "deck": deck_name,
            "tags": tags,
            "subject": f.get("subject_name", ""),
            "type": "Formula"
        })

    return _format_cards_output(cards, format_type, deck_default="Nexus::Formulas")


def export_all_to_anki(user_id: int, format_type: str = "tsv") -> str:
    """Exports all flashcards across Mistakes, Active Recall, and Formulas into a master deck."""
    mistake_tsv = export_mistakes_to_anki(user_id, format_type="json")
    recall_tsv = export_active_recall_to_anki(user_id, format_type="json")
    formula_tsv = export_formulas_to_anki(user_id, format_type="json")

    cards = []
    cards.extend(json.loads(mistake_tsv))
    cards.extend(json.loads(recall_tsv))
    cards.extend(json.loads(formula_tsv))

    return _format_cards_output(cards, format_type, deck_default="Nexus::Master_Deck")


def _format_cards_output(cards: list, format_type: str, deck_default: str = "Nexus") -> str:
    """Converts card dictionary objects into the requested export format."""
    if format_type.lower() == "json":
        return json.dumps(cards, indent=2)

    elif format_type.lower() == "csv":
        out = io.StringIO()
        writer = csv.writer(out, quoting=csv.QUOTE_ALL)
        writer.writerow(["Front", "Back", "Deck", "Tags", "Subject", "Type"])
        for c in cards:
            writer.writerow([
                c.get("front", ""),
                c.get("back", ""),
                c.get("deck", deck_default),
                c.get("tags", ""),
                c.get("subject", ""),
                c.get("type", "")
            ])
        return out.getvalue()

    else:
        # Standard Anki TSV with official headers
        out = io.StringIO()
        out.write("#separator:Tab\n")
        out.write("#html:true\n")
        out.write("#tags column:4\n")
        out.write(f"#deck:{deck_default}\n")
        
        for c in cards:
            # Replace literal tabs with spaces in fields
            f = c.get("front", "").replace("\t", " ")
            b = c.get("back", "").replace("\t", " ")
            d = c.get("deck", deck_default).replace("\t", " ")
            t = c.get("tags", "").replace("\t", " ")
            out.write(f"{f}\t{b}\t{d}\t{t}\n")
            
        return out.getvalue()
