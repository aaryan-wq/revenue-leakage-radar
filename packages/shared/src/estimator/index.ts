export type HypothesisId =
  | "H1"
  | "H2"
  | "H3"
  | "H4"
  | "H5"
  | "H6"
  | "H7"
  | "H8"
  | "H9"
  | "H10"
  | "H11"
  | "H12"
  | "H13"
  | "H14"
  | "H15"
  | "H16"
  | "H17"
  | "H18";

export interface EstimatorQuestionOption {
  value: string;
  label: string;
}

export interface EstimatorQuestion {
  id: string;
  section: string;
  type: "select" | "multiselect" | "currency" | "number" | "scale" | "boolean";
  label: string;
  required?: boolean;
  options?: EstimatorQuestionOption[];
  currencies?: string[];
  min?: number;
  max?: number;
  visibility?: { when: string; equals: unknown };
}

export interface EstimatorProgress {
  visible_count: number;
  answered_count: number;
  completion_rate: number;
  estimated_seconds_remaining: number;
  is_complete: boolean;
}

export interface EstimatorComplexityPreview {
  pricing: number;
  contract: number;
  systems: number;
  change: number;
  operations: number;
  total: number;
  label: string;
}

export interface EstimatorRuleBreakdown {
  rule_id: string;
  category: string;
  leak_family: string;
  hypothesis_ids: string[];
  posterior_probability: number;
  detectability: number;
  required_entities: string[];
  expected: number;
  low: number;
  high: number;
  p90: number;
  pct_of_arr: number;
  likelihood: number;
  share_of_total: number;
}

export interface EstimatorDisplayRollup {
  rollup_id: string;
  name: string;
  rule_ids: string[];
  expected: number;
}

export interface EstimatorCoverageBridge {
  high_priority_rules: string[];
  file_suggestions: string[];
  total_rules_modeled: number;
}

export interface EstimatorRuleInsight {
  rule_id: string;
  insight: string;
}

export interface EstimatorVerificationCategoryPreview {
  category: string;
  category_label: string;
  rules: {
    rule_id: string;
    name: string;
    expected: number;
    posterior_probability: number;
    detectability: number;
    required_entities: string[];
    hypothesis_ids: string[];
  }[];
}

export interface EstimatorHypothesisBreakdown {
  hypothesis_id: HypothesisId;
  name: string;
  rule_ids: string[];
  posterior_probability: number;
  expected: number;
  low: number;
  mid: number;
  high: number;
  pct_of_arr: number;
  likelihood: number;
  share_of_total: number;
}

export interface EstimatorProfileSummary {
  arr_usd: number;
  customer_count?: number;
  complexity_label: string;
  complexity_score: number;
  risk_flags: string[];
}

export interface EstimatorMechanismInsight {
  hypothesis_id: HypothesisId;
  insight: string;
}

export interface EstimatorVerificationRule {
  rule_id: string;
  name: string;
}

export interface EstimatorVerificationPreview {
  hypothesis_id: HypothesisId;
  hypothesis_name: string;
  rules: EstimatorVerificationRule[];
}

export interface EstimatorBenchmarkContext {
  source: string;
  pct_arr_low: number;
  pct_arr_high: number;
  pct_arr_average: number;
  low_usd: number;
  high_usd: number;
  average_usd: number;
  model_pct_of_arr: number;
  may_understate: boolean;
}

export interface EstimatorCalculationSummary {
  simulation_count: number;
  expected_value: number;
  median_run: number;
  pct_runs_with_leakage: number;
  conditional_mean: number;
  gross_expected?: number;
  net_recoverable?: number;
  pct_of_arr: number;
  scenario: string;
  scenario_band_label: string;
  range_low: number;
  range_high: number;
  explanation_bullets: string[];
}

export interface EstimatorResult {
  estimate: {
    low: number;
    central: number;
    high: number;
    median_run?: number;
    display_range: string;
    stress_p90?: number;
    theoretical_stack_p90?: number;
    recoverable?: number;
    at_risk?: number;
    overlap_discount?: number;
    arr_band_low?: number;
    arr_band_high?: number;
    gross_expected?: number;
    net_recoverable?: number;
    display_headline_usd?: number;
  };
  monthly: { low: number; central: number; high: number };
  confidence: string;
  complexity: EstimatorComplexityPreview;
  top_hypotheses: EstimatorHypothesisBreakdown[];
  hypothesis_breakdown: EstimatorHypothesisBreakdown[];
  rule_breakdown?: EstimatorRuleBreakdown[];
  display_rollups?: EstimatorDisplayRollup[];
  recoverable?: { expected: number; low: number; high: number };
  theoretical_stack?: { p90: number; overlap_discount: number };
  rule_insights?: EstimatorRuleInsight[];
  coverage_bridge?: EstimatorCoverageBridge;
  drivers: { key: string; label: string; influence: number; delta_expected?: number }[];
  detectable: { low: number; high: number };
  assumptions: {
    assumption_id: string;
    category: string;
    value: string;
    source: string;
    confidence: string;
  }[];
  /** @deprecated Use executive_summary instead */
  what_would_need_to_be_true?: string[];
  profile_summary?: EstimatorProfileSummary;
  mechanism_insights?: EstimatorMechanismInsight[];
  verification_preview?: EstimatorVerificationPreview[] | EstimatorVerificationCategoryPreview[];
  calculation_summary?: EstimatorCalculationSummary;
  benchmark_context?: EstimatorBenchmarkContext | null;
  executive_summary?: string;
  model_version: string;
  calibration_stage: number;
  scenario?: string;
  scenario_band?: [string, string];
  narrative?: EstimatorNarrative;
  arr_usd?: number;
  percentiles?: Record<string, number>;
  sensitivity?: { key: string; label: string; influence: number }[];
}

export interface EstimatorNarrative {
  headline: string;
  summary: string;
  drivers: string[];
  caveats: string[];
  recommended_next_step: string;
  confidence_decomposition?: Record<string, string>;
  view?: string;
}

export interface EstimatorResumeState {
  pending_question_ids: string[];
  pending_count: number;
  answered_count: number;
  has_pending_questions: boolean;
  requires_reanswer: boolean;
  is_resuming: boolean;
  questionnaire_version: string;
  current_questionnaire_version: string;
}

export interface EstimatorAssessmentState {
  assessment_id: string;
  status: string;
  answers: Record<string, unknown>;
  progress: EstimatorProgress;
  current_section: string | null;
  next_question: EstimatorQuestion | null;
  complexity_preview?: EstimatorComplexityPreview | null;
  visible_question_ids?: string[];
  resume?: EstimatorResumeState;
}

export const ESTIMATOR_ANALYTICS_EVENTS = {
  ESTIMATOR_VIEWED: "estimator_viewed",
  ESTIMATOR_STARTED: "estimator_started",
  SECTION_COMPLETED: "section_completed",
  QUESTION_ANSWERED: "question_answered",
  BRANCH_TRIGGERED: "branch_triggered",
  ESTIMATOR_COMPLETED: "estimator_completed",
  RESULT_VIEWED: "result_viewed",
  METHODOLOGY_VIEWED: "methodology_viewed",
  SCENARIO_CHANGED: "scenario_changed",
  RESULT_SHARED: "result_shared",
  FREE_SCAN_CLICKED: "free_scan_clicked",
  ASSESSMENT_EMAIL_SAVED: "assessment_email_saved",
} as const;

/** Published SaaS billing leakage survey band (landing slider + industry context). */
export const INDUSTRY_LEAKAGE_PCT_LOW = 0.03;
export const INDUSTRY_LEAKAGE_PCT_HIGH = 0.05;
export const INDUSTRY_LEAKAGE_PCT_AVERAGE = 0.042;

/** Headline for calculator results: benchmark-aware display when model may understate. */
export function getEstimatorHeadlineUsd(result: EstimatorResult): number {
  return result.estimate.display_headline_usd ?? result.estimate.high;
}

export function getIndustryLeakageHeadlineUsd(arrUsd: number): number {
  if (arrUsd <= 0) return 0;
  return Math.round(arrUsd * INDUSTRY_LEAKAGE_PCT_AVERAGE);
}
