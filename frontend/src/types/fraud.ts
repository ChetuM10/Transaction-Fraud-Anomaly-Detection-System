//this matches FeatureExplanation in routes.py
export interface FeatureExplanation {
    feature: string;
    shap_value: number;
    actual_value: number;
}

//this matches FalgOut in routes.py
export interface Flag {
    id: number;
    transaction_id: string;
    score: number;
    decision: string;
    top_features: FeatureExplanation[];
    outcome: string;
    reviewed_by: string | null;
    created_at: string;
    reviewed_at: string | null;
}

//this matches ReviewIn in routes.py
export interface ReviewSubmission {
    outcome: 'true_positive' | 'false_positive';
    reviewed_by: string;
}