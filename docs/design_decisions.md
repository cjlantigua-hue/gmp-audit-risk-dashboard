# Design Decisions

## D1: Fixed snapshot date (2026-09-30)
**Decision:** Calculate overdue and open status against a fixed date.

**Why:** Synthetic data is static; using the real current date would make
dashboard numbers change every day.

## D2: Supplier audits excluded
**Decision:** Only audits of the company's own sites are included.

**Why:** Supplier audits inspect outside companies, which would complicate
the site-based data model.

## D3: One CAPA per finding
**Decision:** Each finding links to exactly one CAPA.

**Why:** Simplifies joins and dashboard logic. Real CAPA systems are often
many-to-many; noted as a limitation.

## D4: "Minor" instead of "Other" for the lowest severity

**Decision:** Use Critical, Major, and Minor as severity levels. 

**Why:** EU inspectorates officially call the lowest tier "Other," but most company audit programs use "Minor," and this dashboard models a company's internal view. The two terms describe the same level (see domain_background.md).

## D5: Risk score formula deferred to Phase 3

**Decision:** Define risk_score and risk_tier now as derived columns, but set the exact formula, weights, and tier cut-offs in Phase 3. 

**Why:** The score should be designed after the synthetic data exists, so the weights can be checked against realistic distributions. It will follow ICH Q9(R1), where risk combines probability of harm and severity.

## D6: Recurrence judged on the affected item

**Decision:** Added `affected_item` to findings. A repeat is the same category on
the same item at the same site within 730 days.

**Why:** At category level, 94% of findings counted as recurrent, because common
categories are cited at every site constantly. This made the flag meaningless and hid
the link between failed CAPAs and repeat findings. Judging on the specific item
mirrors how auditors identify true repeat observations.

## D7: Risk score = Impact × Exposure
**Decision:** Score each finding as Impact (severity × area criticality) times
Exposure (CAPA status, overdue, recurrence), each 1–10. Tiers: High ≥ 40,
Medium 15–39.9, Low < 15, set from anchor scenarios (e.g., every open Critical
is High; no Minor is High) that the notebook checks automatically.

**Why:** Multiplying all four factors directly compressed scores into 0–30.
Impact × Exposure mirrors familiar QA risk matrices and ICH Q9's severity ×
probability. Recurrence is ignored once a CAPA is verified effective, so
resolved history does not crowd out active risk. A sensitivity test showed the
top 20 active findings stay stable (16–20 of 20) under single-weight changes.


## D8: ML target is recurrence, not overdue CAPAs
**Decision:** Predict whether a finding recurs on the same item within 12
months, using only information available when the finding is logged, with a
time-based train/test split (train Oct 2023–Dec 2024, test Jan–Sep 2025).

**Why:** An overdue-CAPA model reached only ROC-AUC 0.65, since the synthetic
data plants lateness mainly by site. The recurrence model reached ROC-AUC 0.84
and answers a more useful question: which CAPAs need deeper root-cause work.
It beats a prior-occurrence baseline (0.815) only slightly; this is reported
openly as a limitation.

## D9: Separate overdue and closed-late flags
**Decision:** `is_overdue` covers only open CAPAs past due; CAPAs closed
after their due date are flagged separately as `closed_late`.

**Why:** QA leadership needs to see what is late right now. Combining
both would inflate the active overdue count with already-resolved items.
