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
