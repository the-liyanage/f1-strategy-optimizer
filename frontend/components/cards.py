
import random
import streamlit as st
from components.tyre import tyre_svg

RADIO_QUOTES_PIT = [
    "Those tyres have seen better days, mate.",
    "We have gone from race pace to sightseeing pace.",
    "Currently setting personal bests for slow laps.",
    "Pit now unless you are inventing a new strategy.",
    "We cannot invoice Pirelli for this level of abuse.",
    "The tyres are not happy. We are not happy. Pit.",
    "This is literally the easiest decision today.",
]

RADIO_QUOTES_STAY = [
    "Tyres feel acceptable. We stay out for now.",
    "Delta is within tolerance. Holding position.",
    "Not yet. We are watching. Do not touch anything.",
    "Pace is still there. We will call it when ready.",
    "Copy that. Pushing on. Let us know if it changes.",
]


def _mode_content(mode: str, rec: dict) -> dict:
    """Returns all mode-specific display strings. Uses actual driver name throughout."""
    is_pit = rec["decision"] == "PIT"
    driver = rec["driver"]  # always use the real driver name

    if mode == "Standard":
        return {
            "theme":          "standard",
            "mode_tag":       "",
            "show_tag":       False,
            "driver_text":    f"{driver} · Lap {rec['lap_number']}",
            "decision_text":  rec["decision"],
            "decision_cls":   "pit" if is_pit else "stay",
            "show_reasons":   True,
            "quote":          None,
            "quote_sub":      None,
            "compound_note":  None,
            "compound_label": rec["compound_recommendation"],
            "conf_label":     "Model Confidence",
            "stat_vals":      [f"P{rec['tyre_life']}", str(rec["laps_remaining"]), f"{rec['confidence_pct']:.1f}%"],
            "stat_lbls":      ["Tyre Age", "Laps Left", "Confidence"],
            "footnote":       "XGBoost · Hybrid strategy engine · 2023 telemetry",
        }

    elif mode == "Toto Mode":
        if is_pit:
            quote = f"The data is unambiguous. {driver} boxes now."
            sub   = f"{rec['reasons'][0]}. Window is viable. We execute."
        else:
            quote = f"We stay out. The numbers do not support pitting yet."
            sub   = f"{rec['reasons'][0]}. Monitoring closely."
        return {
            "theme":          "toto",
            "mode_tag":       "TOTO WOLFF · MERCEDES AMG",
            "show_tag":       True,
            "driver_text":    f"{driver} · LAP {rec['lap_number']} · P{rec.get('position','?')}",
            "decision_text":  "BOX THIS LAP" if is_pit else "STAY OUT",
            "decision_cls":   "toto",
            "show_reasons":   False,
            "quote":          quote,
            "quote_sub":      sub,
            "compound_note":  f"Compound switch — {rec['laps_remaining']} laps remaining. Degradation delta confirms timing.",
            "compound_label": f"{rec['compound_recommendation']} — optimal",
            "conf_label":     "Undercut Probability",
            "stat_vals":      [f"{rec['tyre_life']}L", str(rec["laps_remaining"]), f"{rec['confidence_pct']:.1f}%"],
            "stat_lbls":      ["Tyre age", "Laps left", "Model conf"],
            "footnote":       "Noted for the debrief.",
        }

    elif mode == "Ferrari Mode":
        if is_pit:
            quote = f"We had a plan. This is no longer the plan."
            sub   = f"{driver}, we pit now and discuss this later. Much later."
            note  = f"Put on the {rec['compound_recommendation'].lower()} ones. Si. Just PIT."
        else:
            quote = f"We stay. We think. We are unsure but we stay."
            sub   = f"{driver}, hold for now. We are... investigating."
            note  = f"Current tyres are fine. Probably. We will monitor."
        return {
            "theme":          "ferrari",
            "mode_tag":       "FERRARI STRATEGY WALL",
            "show_tag":       True,
            "driver_text":    f"{driver} · GIRO {rec['lap_number']} · P{rec.get('position','?')}",
            "decision_text":  "MAMMA MIA — PIT!" if is_pit else "ASPETTA! STAY!",
            "decision_cls":   "ferrari",
            "show_reasons":   False,
            "quote":          quote,
            "quote_sub":      sub,
            "compound_note":  note,
            "compound_label": rec["compound_recommendation"],
            "conf_label":     "Panic Level",
            "stat_vals":      [f"{rec['tyre_life']}L", str(rec["laps_remaining"]), f"{rec['confidence_pct']:.0f}%"],
            "stat_lbls":      ["Tyre age", "Laps left", "Regret %"],
            "footnote":       "We will investigate this.",
        }

    else:  # Engineer Radio
        random.seed(rec["tyre_life"] + len(driver))
        if is_pit:
            quote = random.choice(RADIO_QUOTES_PIT)
            sub   = f"{rec['reasons'][0]}. Box this lap, {driver}."
            note  = f"Fitting {rec['compound_recommendation'].lower()} compound. {rec['laps_remaining']} laps to go."
        else:
            quote = random.choice(RADIO_QUOTES_STAY)
            sub   = f"{rec['reasons'][0]}. Stay out for now, {driver}."
            note  = f"Keep the {rec['current_compound'].lower()} on. We will call it."
        return {
            "theme":          "radio",
            "mode_tag":       "ENGINEER RADIO · LIVE",
            "show_tag":       True,
            "driver_text":    f"{driver} · LAP {rec['lap_number']} · P{rec.get('position','?')}",
            "decision_text":  "BOX BOX BOX" if is_pit else "STAY STAY STAY",
            "decision_cls":   "radio",
            "show_reasons":   False,
            "quote":          quote,
            "quote_sub":      sub,
            "compound_note":  note,
            "compound_label": rec["compound_recommendation"],
            "conf_label":     "Vibes Check",
            "stat_vals":      [f"{rec['tyre_life']}L", str(rec["laps_remaining"]), f"{rec['confidence_pct']:.1f}%"],
            "stat_lbls":      ["Tyre age", "Laps left", "Confidence"],
            "footnote":       "Trust the process.",
        }


def recommendation_card(rec: dict, mode: str):
    """Renders the full recommendation card. Each section is a separate st.markdown call."""
    c = _mode_content(mode, rec)
    t = c["theme"]

    # Open card
    st.markdown(f'<div class="rec-card {t}">', unsafe_allow_html=True)

    # Mode tag
    if c["show_tag"]:
        st.markdown(f'<div class="mode-tag {t}">{c["mode_tag"]}</div>', unsafe_allow_html=True)

    # Driver + Decision
    st.markdown(f'<div class="rec-driver {t}">{c["driver_text"]}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="rec-decision {c["decision_cls"]}">{c["decision_text"]}</div>', unsafe_allow_html=True)

    # Compound row
    cur_svg = tyre_svg(rec["current_compound"], size=38)
    rec_svg = tyre_svg(rec["compound_recommendation"], size=38, active=True)
    st.markdown(f"""
    <div class="compound-row {t}">
        <div style="display:flex;align-items:center;gap:10px">
            {cur_svg}
            <div>
                <div class="compound-label {t}">Current</div>
                <div class="compound-name">{rec["current_compound"]}</div>
            </div>
        </div>
        <span class="compound-arrow {t}">&#8594;</span>
        <div style="display:flex;align-items:center;gap:10px">
            {rec_svg}
            <div>
                <div class="compound-label {t}">Switch to</div>
                <div class="compound-name-rec {t}">{c["compound_label"]}</div>
            </div>
        </div>
    </div>""", unsafe_allow_html=True)

    # Content
    if c["show_reasons"]:
        items = "".join([f'<div class="reason-item">{r}</div>' for r in rec["reasons"]])
        st.markdown(f'<div class="reasons-block">{items}</div>', unsafe_allow_html=True)
    else:
        st.markdown(
            f'<div class="quote-block">'
            f'<div class="quote-text {t}">{c["quote"]}</div>'
            f'<div class="quote-sub {t}">{c["quote_sub"]}</div>'
            f'</div>',
            unsafe_allow_html=True
        )
        st.markdown(f'<div class="compound-note {t}">{c["compound_note"]}</div>', unsafe_allow_html=True)

  

    # Stat chips
    chips = "".join([
        f'<div class="stat-chip {t}">'
        f'<span class="stat-value">{c["stat_vals"][i]}</span>'
        f'<span class="stat-label {t}">{c["stat_lbls"][i]}</span>'
        f'</div>'
        for i in range(3)
    ])
    st.markdown(f'<div class="stats-row">{chips}</div>', unsafe_allow_html=True)

    # Footnote + close
    st.markdown(f'<div class="footnote {t}">{c["footnote"]}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)


def empty_card():
    st.markdown(f"""
    <div class="empty-card">
        <div style="opacity:0.2">{tyre_svg("MEDIUM", size=72)}</div>
        <div class="empty-text">Configure the race situation<br>and hit the button</div>
    </div>""", unsafe_allow_html=True)


def error_card(message: str):
    st.markdown(
        f'<div class="error-card"><p class="error-text">{message}</p></div>',
        unsafe_allow_html=True
    )