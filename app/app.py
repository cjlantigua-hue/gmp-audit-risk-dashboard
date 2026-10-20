"""
GMP Finding Recurrence Predictor
Streamlit app for the GMP Audit Findings Risk Dashboard project (synthetic data).

Enter a new audit finding and get:
  1. The probability the same problem recurs on the same item within 12 months (ML model, Phase 6)
  2. Its initial risk score and tier (rule-based Impact x Exposure, Phase 3)
"""
import json
from pathlib import Path

import joblib
import pandas as pd
import sklearn
import streamlit as st

DASHBOARD_URL = ("https://public.tableau.com/app/profile/carlos.lantigua4534/viz/"
                 "GMPAuditFindingsRiskDashboard/1_Overview")
GITHUB_URL = "https://github.com/cjlantigua-hue/gmp-audit-risk-dashboard"

st.set_page_config(page_title="GMP Finding Recurrence Predictor", page_icon="🔁", layout="centered")


# ---------- Load the model and its settings ----------
def find_models_dir() -> Path:
    here = Path(__file__).resolve().parent
    for candidate in (here.parent / "models", here / "models"):
        if (candidate / "recurrence_model.joblib").exists():
            return candidate
    st.error("Could not find `models/recurrence_model.joblib`. Upload the models folder to the repository.")
    st.stop()


@st.cache_resource
def load_artifacts():
    models_dir = find_models_dir()
    model = joblib.load(models_dir / "recurrence_model.joblib")
    meta = json.loads((models_dir / "recurrence_model_meta.json").read_text())
    weights = json.loads((models_dir / "risk_weights.json").read_text())
    return model, meta, weights


model, meta, W = load_artifacts()

# ---------- Reference data (matches docs/data_dictionary.md) ----------
SITES = {
    "Raleigh, NC": "Sterile Injectables",
    "San Juan, PR": "Oral Solid Dose",
    "Cork, Ireland": "API",
    "Basel, Switzerland": "Sterile Injectables",
    "Hyderabad, India": "Oral Solid Dose",
}
CATEGORIES = {  # category -> (process area, 21 CFR 211 reference)
    "Inadequate deviation investigation": ("Quality System", "211.192"),
    "Ineffective CAPA": ("Quality System", "211.192"),
    "Change control deficiency": ("Quality System", "211.100(a)"),
    "Inadequate QC unit oversight": ("Quality System", "211.22"),
    "Complaint handling deficiency": ("Quality System", "211.198"),
    "Annual product review incomplete": ("Quality System", "211.180(e)"),
    "Training deficiency": ("Quality System", "211.25"),
    "Equipment cleaning / cleaning validation": ("Facilities & Equipment", "211.67"),
    "Equipment calibration / maintenance": ("Facilities & Equipment", "211.68(a)"),
    "Facility maintenance": ("Facilities & Equipment", "211.58"),
    "Environmental monitoring": ("Facilities & Equipment", "211.42(c)"),
    "Computerized system / data integrity": ("Facilities & Equipment", "211.68(b)"),
    "Component testing / supplier qualification": ("Materials", "211.84"),
    "Material storage and handling": ("Materials", "211.80"),
    "Batch record documentation (GDP)": ("Production", "211.188"),
    "Procedures not followed": ("Production", "211.100(b)"),
    "In-process control deficiency": ("Production", "211.110"),
    "Label control / reconciliation": ("Packaging & Labeling", "211.125"),
    "Line clearance deficiency": ("Packaging & Labeling", "211.130"),
    "Inadequate OOS investigation": ("Laboratory Controls", "211.192"),
    "Method validation deficiency": ("Laboratory Controls", "211.165(e)"),
    "Stability program deficiency": ("Laboratory Controls", "211.166"),
    "Laboratory records / data integrity": ("Laboratory Controls", "211.194"),
    "Lab instrument calibration": ("Laboratory Controls", "211.160(b)"),
}
SEVERITIES = ["Critical", "Major", "Minor"]
AUDIT_TYPES = ["Internal", "Corporate", "Regulatory"]
TIER_ICON = {"High": "🔴", "Medium": "🟠", "Low": "🟢"}


def predict_recurrence(site, category, severity, audit_type, prior, description=""):
    row = pd.DataFrame([{
        "site_name": site, "process_area": CATEGORIES[category][0], "category": category,
        "severity": severity, "audit_type": audit_type, "product_type": SITES[site],
        "prior_occurrence_count": prior, "description": description,
    }])
    return float(model.predict_proba(row[meta["features"]])[0, 1])


def initial_risk(site, category, severity, prior):
    """Phase 3 risk score for a newly logged finding (CAPA just opened, not overdue)."""
    area = CATEGORIES[category][0]
    sterile = SITES[site] == "Sterile Injectables" and area in W["sterile_boost_areas"]
    impact = min(W["severity_points"][severity] * W["area_criticality"][area]
                 * (W["sterile_boost"] if sterile else 1.0), 10)
    exposure = min(W["status_points"]["Open"]
                   + min(prior * W["recurrence_points_per_prior"], W["recurrence_points_max"]), 10)
    score = round(impact * exposure, 1)
    cut = W["tier_cutoffs"]
    tier = "High" if score >= cut["High"] else "Medium" if score >= cut["Medium"] else "Low"
    return score, tier, impact, exposure


# ---------- Page ----------
st.title("GMP Finding Recurrence Predictor")
st.caption(f"Part of the [GMP Audit Findings Risk Dashboard]({DASHBOARD_URL}) project · "
           f"[Code on GitHub]({GITHUB_URL}) · **All data is synthetic.**")
st.write("Enter a newly raised audit finding. The app estimates how likely the **same problem is to be cited again "
         "on the same item within 12 months**, and gives the finding's initial risk score.")

if sklearn.__version__ != meta["sklearn_version"]:
    st.warning(f"Model was trained with scikit-learn {meta['sklearn_version']} but the app is running "
               f"{sklearn.__version__}. Pin scikit-learn=={meta['sklearn_version']} in requirements.txt.")

with st.form("finding"):
    c1, c2 = st.columns(2)
    site = c1.selectbox("Site", list(SITES))
    audit_type = c2.selectbox("Audit type", AUDIT_TYPES)
    category = st.selectbox("Finding category", list(CATEGORIES),
                            index=list(CATEGORIES).index("Batch record documentation (GDP)"))
    c3, c4 = st.columns(2)
    severity = c3.selectbox("Severity", SEVERITIES, index=1)
    prior = c4.number_input("Times this problem was cited on the same item in the past 2 years",
                            min_value=0, max_value=20, value=1, step=1)
    st.caption(f"Process area: **{CATEGORIES[category][0]}** · 21 CFR {CATEGORIES[category][1]} · "
               f"Site product type: **{SITES[site]}**")
    submitted = st.form_submit_button("Predict", type="primary", width="stretch")

if submitted:
    p = predict_recurrence(site, category, severity, audit_type, int(prior))
    score, tier, impact, exposure = initial_risk(site, category, severity, int(prior))
    flagged = p >= meta["threshold"]

    m1, m2 = st.columns(2)
    m1.metric("Chance of recurrence within 12 months", f"{p:.0%}")
    m2.metric("Initial risk score (0–100)", f"{score:.0f}")
    m2.markdown(f"{TIER_ICON[tier]} **{tier} risk** tier")

    if flagged:
        st.error(f"**Priority for deeper root-cause analysis.** This finding is in the top half of predicted "
                 f"recurrence risk (threshold {meta['threshold']:.0%}). A quick fix is unlikely to stop it coming back.")
    else:
        st.info(f"**Not in the top-priority group** (below the {meta['threshold']:.0%} flag threshold). Recurrence is "
                f"still common: about two-thirds of past findings came back within a year, so a thorough CAPA and "
                f"effectiveness check still matter.")

    st.subheader("What if it had happened more often before?")
    what_if = pd.DataFrame({
        "Prior occurrences": [f"{k} prior" for k in range(6)],
        "Chance of recurrence (%)": [round(100 * predict_recurrence(site, category, severity, audit_type, k))
                                     for k in range(6)],
    })
    st.bar_chart(what_if, x="Prior occurrences", y="Chance of recurrence (%)", horizontal=True,
                 height=240, color="#2a78d6")
    st.caption("Same finding, varying only its history. Repeat history is the strongest single driver.")

    with st.expander("How the risk score was calculated"):
        st.write(f"**Impact {impact:.1f}** (severity × process-area criticality) × "
                 f"**Exposure {exposure:.0f}** (new CAPA = Open, plus repeat history) = **{score:.0f}**. "
                 f"Tiers: High ≥ {W['tier_cutoffs']['High']}, Medium ≥ {W['tier_cutoffs']['Medium']}.")

with st.expander("About the model"):
    tm = meta["test_metrics"]
    st.markdown(f"""
- **Model:** {meta['model']} (scikit-learn), trained on findings from {meta['train_period']}.
- **Validation:** time-based split; tested on {meta['test_period']}.
- **Test performance:** ROC-AUC **{tm['roc_auc']:.2f}**, PR-AUC **{tm['pr_auc']:.2f}**. A simple rule ranking findings
  by prior occurrences alone scores ROC-AUC {tm['baseline_prior_only_roc_auc']:.2f}, so most of the signal is repeat history.
- **Inputs:** only information available when a finding is logged (no CAPA outcome data), to avoid data leakage.
- **Limitation:** trained on synthetic data, so it rediscovers designed patterns. The pipeline is ready to retrain on real data.
""")
