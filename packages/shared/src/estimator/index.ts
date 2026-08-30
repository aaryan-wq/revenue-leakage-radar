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

export interface EstimatorCalculationSummary {
  simulation_count: number;
  expected_value: number;
  median_run: number;
  pct_runs_with_leakage: number;
  conditional_mean: number;
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
  };
  monthly: { low: number; central: number; high: number };
  confidence: string;
  complexity: EstimatorComplexityPreview;
  top_hypotheses: EstimatorHypothesisBreakdown[];
  hypothesis_breakdown: EstimatorHypothesisBreakdown[];
  drivers: { key: string; label: string; influence: number }[];
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
  verification_preview?: EstimatorVerificationPreview[];
  calculation_summary?: EstimatorCalculationSummary;
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

export interface EstimatorAssessmentState {
  assessment_id: string;
  status: string;
  answers: Record<string, unknown>;
  progress: EstimatorProgress;
  current_section: string | null;
  next_question: EstimatorQuestion | null;
  complexity_preview?: EstimatorComplexityPreview | null;
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
