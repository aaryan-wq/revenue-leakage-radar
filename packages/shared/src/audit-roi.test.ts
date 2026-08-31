import { strict as assert } from "node:assert";
import { describe, it } from "node:test";

import {
  AUDIT_ROI_BREAK_EVEN_ARR_USD,
  computeAuditRoi,
  formatPaybackPeriod,
} from "./audit-roi";

describe("computeAuditRoi", () => {
  it("returns null for zero recoverable ARR", () => {
    assert.equal(computeAuditRoi(0), null);
    assert.equal(computeAuditRoi(-100), null);
  });

  it("happy path at $50k recoverable ARR", () => {
    const roi = computeAuditRoi(50_000);
    assert.ok(roi);
    assert.equal(roi.totalCostUsd, 7500);
    assert.equal(roi.netAnnualGainUsd, 42500);
    assert.ok(roi.roiPercent > 566 && roi.roiPercent < 567);
    assert.equal(roi.baseFeePaybackPercent, 5);
    assert.equal(roi.valuationUpliftLowUsd, 250_000);
    assert.equal(roi.valuationUpliftHighUsd, 500_000);
    assert.equal(roi.isPositiveRoi, true);
    assert.equal(formatPaybackPeriod(roi), "55 days");
  });

  it("break-even edge near $2,778 recoverable ARR", () => {
    const roi = computeAuditRoi(Math.ceil(AUDIT_ROI_BREAK_EVEN_ARR_USD));
    assert.ok(roi);
    assert.ok(roi.isPositiveRoi);
    assert.ok(roi.netAnnualGainUsd >= 0);
  });

  it("below break-even shows negative ROI", () => {
    const roi = computeAuditRoi(2000);
    assert.ok(roi);
    assert.equal(roi.isPositiveRoi, false);
    assert.ok(roi.netAnnualGainUsd < 0);
    assert.equal(formatPaybackPeriod(roi), "");
  });
});
