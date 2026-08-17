import type { Flag, ReviewSubmission } from '../types/fraud';

const API_BASE_URL = 'http://localhost:8000';

export async function fetchFlags(decision?: string, outcome?: string): Promise<Flag[]> {
    const url = new URL(`${API_BASE_URL}/flags`);
    if (decision) url.searchParams.append('decision', decision);
    if (outcome) url.searchParams.append('outcome', outcome);

    const response = await fetch(url.toString());
    if (!response.ok) {
        throw new Error('Failed to fetch flags.');
    }

    return response.json()
}

export async function submitReview(flagId: number, review: ReviewSubmission):
    Promise<any> {
    const response = await fetch(`${API_BASE_URL}/flags/${flagId}/review`, {
        method: "POST",
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(review),
    });

    if (!response.ok) {
        throw new Error('Failed to submit review');
    }

    return response.json();
}