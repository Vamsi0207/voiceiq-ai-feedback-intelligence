export type Complaint = {
  id: number;
  complaint_id: string;
  complaint_text: string;
  customer_id: string | null;
  source: string;
  created_at: string;
  category: string | null;
  sentiment: string | null;
  urgency: string | null;
  confidence: number | null;
  sentiment_confidence: number | null;
  urgency_reason: string | null;
  cluster_id: number | null;
  processing_status: string;
  processed_at: string | null;
  model_version: string | null;
};
export type Page = {
  items: Complaint[];
  total: number;
  page: number;
  page_size: number;
};
export type Overview = {
  total: number;
  negative_percentage: number;
  elevated_urgency: number;
  largest_category: string;
  recurring_clusters: number;
  categories: Record<string, number>;
  sentiments: Record<string, number>;
  urgencies: Record<string, number>;
  sources: string[];
  clusters: { id: number; label: string; count: number }[];
  pending: number;
};
export type Cluster = {
  id: number;
  representative_label: string;
  complaint_count: number;
  dominant_category: string;
  summary: string;
  method: string;
  sentiment_breakdown: Record<string, number>;
  representative_complaint: Complaint;
  members?: Complaint[];
  members_limit?: number;
};
export type Insight = {
  id: number;
  title: string;
  description: string;
  related_category: string;
  supporting_complaint_ids: string[];
  frequency: number;
  urgency: string;
  priority: string;
  priority_score: number;
  recommendation: string;
  success_metric: string;
  reasoning: string;
  provider: string;
  model_name: string;
};
export type AIStatus = {
  configured: boolean;
  provider: string;
  model: string;
  embedding_mode: string;
  embedding_model: string;
  message: string;
};
export type Job = {
  id: number;
  status: string;
  completed: number;
  total: number;
  error: string | null;
};
export type Batch = {
  total_records: number;
  successful_records: number;
  duplicate_records: number;
  failed_records: number;
  errors: { row: number; reason: string }[];
};
export type Evaluation = {
  model_version: string;
  training_records: number;
  evaluation_records: number;
  dataset: string;
  generated_at: string;
  category: {
    accuracy: number;
    macro_f1: number;
    macro_precision: number;
    macro_recall: number;
    labels: string[];
    confusion_matrix: number[][];
    per_class: Record<
      string,
      { precision: number; recall: number; "f1-score": number; support: number }
    >;
  };
  sentiment: { accuracy: number; macro_f1: number };
  clustering: {
    method: string;
    sample_size: number;
    clusters: number;
    noise_records: number;
    silhouette_cosine?: number;
    examples: { size: number; texts: string[] }[];
    limitation: string;
  };
};
