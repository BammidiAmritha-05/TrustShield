import { config } from '../config';
import { HealthResponse, InteractionType, SessionResponse } from '../types/backend';

export async function createSession(interactionType: InteractionType, consent: boolean): Promise<SessionResponse> {
  const response = await fetch(`${config.apiBaseUrl}/api/v1/sessions`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ interaction_type: interactionType, consent }),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || `Failed to create session (${response.status})`);
  }

  return response.json();
}

export async function getSession(sessionId: string): Promise<SessionResponse> {
  const response = await fetch(`${config.apiBaseUrl}/api/v1/sessions/${sessionId}`);
  if (!response.ok) {
    throw new Error(`Failed to fetch session (${response.status})`);
  }
  return response.json();
}

export async function endSession(sessionId: string): Promise<SessionResponse> {
  const response = await fetch(`${config.apiBaseUrl}/api/v1/sessions/${sessionId}/end`, {
    method: 'POST',
  });
  if (!response.ok) {
    throw new Error(`Failed to end session (${response.status})`);
  }
  return response.json();
}

export async function getSessions(): Promise<SessionResponse[]> {
  const response = await fetch(`${config.apiBaseUrl}/api/v1/sessions`);
  if (!response.ok) {
    throw new Error(`Failed to fetch sessions (${response.status})`);
  }
  return response.json();
}

export async function getHealth(): Promise<HealthResponse> {
  const response = await fetch(`${config.apiBaseUrl}/health`);
  if (!response.ok) {
    throw new Error(`Health check failed (${response.status})`);
  }
  return response.json();
}
