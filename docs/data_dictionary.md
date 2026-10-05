## 1. Overview
This is a synthetic dataset for **Meridian Pharma**, a fictional pharmaceutical
company with **5 manufacturing sites**. It covers audits conducted from
**2023-10-01 to 2026-09-30**.

All time-based calculations (open/overdue status, days open) use a fixed
**snapshot date of 2026-09-30**, so results don't change over time.

## 2. Data model
Tables are linked in a chain: sites → audits → findings → capas.

- Audit types: Internal, Corporate, and Regulatory. All audits are of the
  company's own sites; supplier audits are out of scope.
- Each finding has exactly one CAPA. In practice, one CAPA can address
  several findings; this was simplified to keep the model clear.
