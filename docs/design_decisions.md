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
