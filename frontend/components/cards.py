"""
components/cards.py
====================
Recommendation card, empty state, error card.
"""
import random
import streamlit as st
from components.tyre import tyre_svg

RADIO_QUOTES = [
    "Those tyres have seen things, mate.",
    "We've gone from race pace to sightseeing pace.",
    "You're currently setting personal bests... for slow laps.",
    "This is literally the easiest decision you'll make today.",
    "Pit now unless you're trying to invent a new strategy.",
    "We can't invoice Pirelli for this level of abuse.",
    "Nature has entered the strategy meeting.",
    "We'd appreciate it if you stopped driving like you stole it.",
]


def _mode_content(mode: str, rec: dict) -> dict:
    """Returns all mode-specific display strings."""
    is_pit = rec["decision"] == "PIT"

    if mode == "Standard":
        return {
            "theme":          "standard",
            "mode_tag":       "",
            "show_tag":       False,
            "driver_text":    f"{rec['driver']} · Lap {rec['lap_number']}",
            "decision_text":  rec["decision"],
            "decision_cls":   "pit" if is_pit else "stay",
            "show_reasons":   True,
            "quote":          None,
            "quote_sub":      None,
            "compound_note":  None,
            "compound_label": rec["compound_recommendation"],
            "conf_label":     "Model Confidence",
            "stat_vals":      [f"P{rec['tyre_life']}", str(rec['laps_remaining']), f"{rec['confidence_pct']:.1f}%"],
            "stat_lbls":      ["Tyre Age", "Laps Left", "Confidence"],
            "footnote":       "XGBoost · Hybrid strategy engine · 2023 telemetry",
        }

    elif mode == "Toto Mode":
        return {
            "theme":          "toto",
            "mode_tag":       "TOTO WOLFF · MERCEDES AMG",
            "show_tag":       True,
            "driver_text":    f"{rec['driver']} · LAP {rec['lap_number']} · POSITION {rec.get('position','?')}",
            "decision_text":  "BOX THIS LAP",
            "decision_cls":   "toto",
            "show_reasons":   False,
            "quote":          '"The data is unambiguous. We box now."',
            "quote_sub":      f"{rec['reasons'][0]}. {rec['reasons'][1]}.",
            "compound_note":  f"Compound C3 — {rec['laps_remaining']} lap degradation delta optimal. We execute.",
            "compound_label": f"C3 — {rec['laps_remaining']}L optimal",
            "conf_label":     "Undercut Probability",
            "stat_vals":      ["0.21s", "8.2s", "73%"],
            "stat_lbls":      ["Deg/lap", "Gap to P4", "Win prob"],
            "footnote":       "Noted for the debrief.",
        }

    elif mode == "Ferrari Mode":
        return {
            "theme":          "ferrari",
            "mode_tag":       "FERRARI STRATEGY WALL",
            "show_tag":       True,
            "driver_text":    f"{rec['driver']} · GIRO {rec['lap_number']} · POSIZIONE {rec.get('position','?')}",
            "decision_text":  "MAMMA MIA — PIT!",
            "decision_cls":   "ferrari",
            "show_reasons":   False,
            "quote":          '"We had a plan. This is no longer the plan."',
            "quote_sub":      f"{rec['reasons'][0]}. Charles, we discuss this later.",
            "compound_note":  "Put on ANYTHING. The hard ones. White. Si. Just PIT.",
            "compound_label": "PUT ON ANYTHING",
            "conf_label":     "Panic Level",
            "stat_vals":      ["Morto", "ALTO", "100%"],
            "stat_lbls":      ["Tyre status", "Panico lvl", "Regret %"],
            "footnote":       "We will investigate this.",
        }

    else:  # Engineer Radio
        random.seed(rec["tyre_life"])
        quote = random.choice(RADIO_QUOTES)
        return {
            "theme":          "radio",
            "mode_tag":       "ENGINEER RADIO · LIVE",
            "show_tag":       True,
            "driver_text":    f"{rec['driver']} · LAP {rec['lap_number']} · P{rec.get('position','?')}",
            "decision_text":  "BOX BOX BOX",
            "decision_cls":   "radio",
            "show_reasons":   False,
            "quote":          f'"{quote}"',
            "quote_sub":      rec["reasons"][0],
            "compound_note":  "The white ones. Hard compound. Please. We are begging.",
            "compound_label": "THE HARD ONES. GO.",
            "conf_label":     "Vibes Check",
            "stat_vals":      ["Gone", "Mate", "Obv"],
            "stat_lbls":      ["Tyre vibes", "Trust level", "Decision"],
            "footnote":       "Don't @ us.",
        }


def recommendation_card(rec: dict, mode: str):
    """Renders the full recommendation card."""
    c = _mode_content(mode, rec)
    t = c["theme"]

    tag_html = f'<div class="mode-tag {t}">{c["mode_tag"]}</div>' if c["show_tag"] else ""

    compound_row = f"""
    <div class="compound-row {t}">
        <div style="display:flex;align-items:center;gap:8px">
            {tyre_svg(rec["current_compound"], size=36)}
            <div>
                <div class="compound-label {t}">Current</div>
                <div class="compound-name">{rec["current_compound"]}</div>
            </div>
        </div>
        <span class="compound-arrow {t}">→</span>
        <div style="display:flex;align-items:center;gap:8px">
            {tyre_svg(rec["compound_recommendation"], size=36, active=True)}
            <div>
                <div class="compound-label {t}">Switch to</div>
                <div class="compound-name-rec {t}">{c["compound_label"]}</div>
            </div>
        </div>
    </div>"""

    if c["show_reasons"]:
        content_html = '<div class="reasons-block">' + "".join([
            f'<div class="reason-item">{r}</div>' for r in rec["reasons"]
        ]) + "</div>"
    else:
        content_html = f"""
        <div class="quote-block">
            <div class="quote-text {t}">{c["quote"]}</div>
            <div class="quote-sub {t}">{c["quote_sub"]}</div>
        </div>
        <div class="compound-note {t}">{c["compound_note"]}</div>"""

    conf_pct = min(rec["confidence_pct"], 100)
    conf_html = f"""
    <div class="conf-label {t}">
        <span>{c["conf_label"]}</span><span>{rec["confidence_pct"]:.1f}%</span>
    </div>
    <div class="conf-bar-bg {t}">
        <div class="conf-bar-fill {t}" style="width:{conf_pct}%"></div>
    </div>"""

    stats_html = '<div class="stats-row">' + "".join([
        f'<div class="stat-chip {t}"><span class="stat-value">{c["stat_vals"][i]}</span>'
        f'<span class="stat-label {t}">{c["stat_lbls"][i]}</span></div>'
        for i in range(3)
    ]) + "</div>"

    st.markdown(f"""
    <div class="rec-card {t}">
        {tag_html}
        <div class="rec-driver {t}">{c["driver_text"]}</div>
        <div class="rec-decision {c["decision_cls"]}">{c["decision_text"]}</div>
        {compound_row}
        {content_html}
        {conf_html}
        {stats_html}
        <div class="footnote {t}">{c["footnote"]}</div>
    </div>""", unsafe_allow_html=True)


def empty_card():
    """Shown before first prediction."""
    from components.tyre import tyre_svg
    st.markdown(f"""
    <div class="empty-card">
        <div style="opacity:0.2">{tyre_svg("MEDIUM", size=72)}</div>
        <div class="empty-text">Configure the race situation<br>and hit the button</div>
    </div>""", unsafe_allow_html=True)


def error_card(message: str):
    """Shown when API call fails."""
    st.markdown(f"""
    <div class="error-card">
        <p class="error-text">{message}</p>
    </div>""", unsafe_allow_html=True)