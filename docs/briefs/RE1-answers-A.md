# RE1 — Answers to RE-A open questions (tech spec §8) · 2026-11-15
Addendum to `RE1-decisions.md` rev 2. Same authority: wins over the plan and older briefs. Numbers match `RE1-tech-spec.md` §8.

1. **Momentum realized loss with partial exits:** keep the engine rule — per idea, per period, `max(0, −Σ exit events in the period)`. A partial win and a later loss inside the same idea net against each other; different ideas never net.
2. **Regime freshness:** use the data's own as-of date (last US session in `fundflow.json`), not a fetch timestamp. Fresh = as-of date within 4 **calendar** days of today (Asia/Bangkok). Missing date = not fresh.
3. **Compounder heat denominator:** week-start equity (same basis as every other limit). Also show the figure against current equity.
4. **Existing Compounder ladder cards:** never resized, never re-split. All existing filled lots count toward heat at their actual remaining risk. A card with more than two tranches, or accelerator lots, is flagged "legacy shape" and left as is. Any NEW buy on such a card must pass the Add-on rules and keep the ticker's total principal risk within the 1% plan. RE-B lists every such card.
5. **Satellite extras:**
   - Remove: weekly new-idea quota (4), fixed pyramid budgets 50/30/20 with 80/100% cumulative caps, old heat / orSat caps, Macro cut.
   - **Keep: TP1/TP2 exit split** (e.g. 50% at TP1, stop to entry on the rest). It is exit management, not sizing.
   - Keep: multiple entry levels inside ONE attempt (PB1 multi-entry). They share one effective RPT; the split per level is entered by the user; the attempt is still one result for step logic.
6. **Capital pools:** keep as an allocation display in Port, labelled "allocation — not the risk basis". Not an engine input.
7. **Satellite Starter ¼:** remove from the Satellite form. Starter stays for Momentum and Compounder.
8. **Week keys:** keep stored Sunday-based keys as data keys (no re-keying). Use `bkk` weeks for risk only.
9. **History:** one outcome rule everywhere — the strict sign rule, also for Journal badges on old trades. Old trades have no cost fields: use gross P&L and mark them "costs not recorded" (history only; new trades never assume zero). A trade with only an exit date is attributed to 12:00 Asia/Bangkok on that date. RE-B reports how many badges change.
10. **Port "Give-back to stops" panel:** keep as read-only information without caps; final placement decided in the RE-C mockup.
11. **Future swap:** no estimate. Projected result = realized + incurred fees/swap + estimated remaining exit fee. Re-evaluated on a cost edit.
12. **Daily slot / re-entry:** per product per account. Accounts never share state.
13. **Entry fee:** belongs to the idea; counted in exposure from the fill and attributed at close (engine default).
14. **Compounder Starter:** first entry 0.25% of the plan; top-up goes to 0.50% (the full Pilot), never straight to 1% unless the Add-on conditions are met.
15. **Event IDs:** deterministic `<acct>:<type>:<refId>:<seq>` (replay-safe).
