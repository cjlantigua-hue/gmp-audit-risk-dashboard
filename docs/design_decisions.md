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

**Decision:** Use Critical, Major, and Minor as severity levels. **Why:** EU inspectorates officially call the lowest tier "Other," but most company audit programs use "Minor," and this dashboard models a company's internal view. The two terms describe the same level (see domain_background.md).

## D5: Risk score formula deferred to Phase 3

**Decision:** Define risk_score and risk_tier now as derived columns, but set the exact formula, weights, and tier cut-offs in Phase 3. **Why:** The score should be designed after the synthetic data exists, so the weights can be checked against realistic distributions. It will follow ICH Q9(R1), where risk combines probability of harm and severity.
