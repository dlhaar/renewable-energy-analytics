# Data Quality Notes

Findings from Sprint 1 cleaning and EDA. These inform modeling decisions in Sprint 2.

## Germany (SMARD)
- **Nuclear is structurally zero** — Germany phased out nuclear power in April 2023. Kept in the schema (not dropped) because it's relevant for cross-country comparison, even though it contributes nothing to Germany's own mix.
- **Comma-separated thousands** in generation export required explicit cleanup (`str.replace(',', '')`) before numeric conversion — not all columns were affected, only those regularly exceeding 1,000 MWh.
- **Day-ahead prices are 15-minute resolution**, not hourly — reflects an EU-wide market settlement change in late 2025. Matches SMARD generation's native resolution, simplifying the Germany-only merit-order join.
- **Negative prices confirmed present** (as low as ~-€500/MWh) — genuine oversupply events, not data errors.

## France (ENTSO-E)
- **Nuclear dominates** (~744M MW total over 2 years vs. ~85M for the next-largest source, Wind Onshore) — the direct inverse of Germany's zero-nuclear profile. This is the core cross-country contrast the schema is built to support.
- **Reporting resolution shifted from hourly to 15-minute on 2024-12-19** — a distinct RTE (French grid operator) reporting change, unrelated to the EU market settlement shift seen in SMARD's price data despite the superficial similarity. Resolved by **resampling all ENTSO-E generation to hourly**, which becomes the standard grain for any cross-country fact table.
- **Partial coverage on some sources**: `Energy storage` (~62% of possible hours) and `Fossil Hard coal` (~30%) — legitimately intermittent/minor generation sources for France, not data gaps to fill. Documented, not imputed.
- **Units differ from SMARD**: ENTSO-E generation is reported in MW (average power), while SMARD's export is in MWh (energy). These are not directly comparable without explicit conversion — flagged for the intermediate dbt layer, not resolved yet.
- **MultiIndex columns and tz-aware DatetimeIndex do not survive a plain CSV round-trip** — required explicit `header=[0,1]` on reload and `pd.to_datetime(..., utc=True)` to reconstruct correctly. All timestamps standardized to UTC internally to avoid DST-related misalignment between countries.

## General
- **A 1-month sample (July 2026) gave a misleading picture** for Germany — Photovoltaics appeared to dominate generation, but this was a seasonal artifact of summer-only data. Wind Onshore actually leads once the full 2-year range is included. Lesson: don't draw mix/ranking conclusions from a partial time range without checking against a fuller period.

## Decisions Carried Into Sprint 2
- Cross-country facts (`fact_generation`) standardize on **hourly** grain and **UTC** timestamps
- Germany-only price analysis can use native 15-min grain where finer detail matters
- Unit reconciliation (MW vs. MWh) handled explicitly in the intermediate layer, not silently assumed
- Eurostat and the 3-grain conformed rollup are **out of scope** for the current MVP (see plan doc scope reduction)