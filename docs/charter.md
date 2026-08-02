# Project Charter: EU Renewable Energy Analytics

## Problem Statement
Germany's electricity grid has shifted heavily toward renewable generation over the past decade, but the public narrative around this transition is often qualitative ("Germany is a renewable leader") rather than grounded in the underlying generation and price data. This project builds a proper dimensional data model on top of real German and EU market data to answer concrete questions about renewable generation patterns, reliability, and their relationship to electricity prices — and to demonstrate end-to-end analytics engineering skill (modeling, transformation, analysis, and visualization) in a domain I want to work in.

## Goals
1. Build a portfolio project that demonstrates real dimensional modeling skill (grain, fact/dim design, conformed dimensions) — not just SQL querying
2. Practice Python as an analytical tool, not just a scripting convenience
3. Produce a project directly relevant to the German/EU energy sector job market
4. Produce a project structured to speak to two audiences: Data Analyst/BI interviewers and Analytics Engineering interviewers

## Scope

### In scope
- Germany generation & price data (SMARD), 15-minute grain
- Germany + 1 neighboring country generation & price data (ENTSO-E Transparency Platform), hourly grain — country TBD, likely France for the nuclear-vs-renewable contrast
- EU-wide annual energy balances (Eurostat) as a conformed rollup layer
- A dbt project on DuckDB implementing a star schema across these sources
- A Python analysis layer covering trend, volatility, and price-correlation questions
- A published Tableau Public dashboard
- A GitHub repo with a case-study README

### Out of scope
- Grid stability / physical infrastructure modeling
- Causal claims about renewable adoption drivers (correlation only, clearly labeled as such)
- Energy sources beyond electricity generation (no heating, transport, etc.)
- Real-time or streaming data — this is a batch/historical analysis project
- More than 2 countries in the ENTSO-E comparison unless time allows (see Open Decisions in the plan)

## Business Questions

**Descriptive (Tableau dashboard)**
1. How has Germany's renewable share of generation changed month-over-month and year-over-year since 2015?
2. Which renewable source (wind vs. solar) dominates generation by season?
3. How does Germany's generation mix compare to a neighboring country with a different energy strategy?
4. Is there a visible weekday/weekend or hour-of-day demand pattern?
5. How do day-ahead prices vary by season and time of day in Germany?
6. How do German prices compare to the comparison country's?

**Analytical (Python)**
7. How variable is renewable output at 15-minute resolution — average day vs. extreme low-output day?
8. What does a simple illustrative projection of Germany's renewable share look like over the next 1–2 years?
9. Does renewable share correlate with time-based patterns (season, day of week)?
10. How do countries compare on renewable share and generation volatility?
11. **The merit-order effect:** does higher renewable generation correlate with lower day-ahead prices, hour by hour?
12. How often do negative day-ahead prices occur, and under what conditions?
13. Is Germany's price more or less volatile than the comparison country's?

## Data Sources
| Source | Grain | What it provides |
|---|---|---|
| SMARD (Bundesnetzagentur) | 15-min | Germany generation by source + day-ahead prices |
| ENTSO-E Transparency Platform | Hourly | Germany + comparison country generation, load, prices |
| Eurostat | Annual | EU-wide official energy balances |

## Deliverables
- dbt project (DuckDB) implementing the star schema
- Python notebooks: EDA, cleaning, and analysis (questions 7–13)
- Published Tableau Public dashboard (questions 1–6)
- GitHub repository with case-study README, structured for both DA/BI and AE audiences

## Success Criteria (Definition of Done for the whole project)
- [ ] `dbt build` runs clean with passing tests on all models
- [ ] Schema demonstrably reconciles three different data grains (15-min, hourly, annual) through a documented conformed dimension approach
- [ ] At least one custom macro implemented in the dbt project
- [ ] All 13 business questions above are answered somewhere in the dashboard or notebook, with the answer clearly stated (not just a chart with no conclusion)
- [ ] Tableau dashboard is published and link-shareable
- [ ] README is readable cold by a stranger in under 2 minutes and clearly signals both a BI-facing and an engineering-facing entry point
- [ ] Resume bullets drafted for both DA/BI and AE framings

## Risks / Open Questions
- ENTSO-E API access requires registration — confirm this works early (Sprint 1) rather than discovering friction later
- Eurostat's annual grain may not align cleanly with the other two sources — if the conformed rollup proves impractical, fall back to using Eurostat purely as a validation/sanity-check layer (noted as an acceptable scope reduction, not a failure)
- Number of comparison countries may expand beyond 1 if time allows — default to 1 unless Sprint 3 is ahead of schedule