import { VoiceAnalysisPayload } from '../types/backend';

export interface NormalizedVoiceScores {
  syntheticPercentage: number;
  bonaFidePercentage: number;
  rawSyntheticScore: number;
  rawBonaFideScore: number;
}

/**
 * Normalizes VoiceAnalysisPayload from AASIST-L into canonical 0-100% display values.
 * AASIST-L returns:
 *   - synthetic_score: probability of synthetic/spoof (0.0 to 1.0)
 *   - bona_fide_score: raw logit (can be negative or positive e.g. -12.84, +3.4)
 *   - bona_fide_probability: softmax probability of natural speech (0.0 to 1.0)
 */
export function normalizeVoiceScores(voice: VoiceAnalysisPayload | null | undefined): NormalizedVoiceScores {
  if (!voice) {
    return {
      syntheticPercentage: 0,
      bonaFidePercentage: 100,
      rawSyntheticScore: 0,
      rawBonaFideScore: 0,
    };
  }

  // 1. Raw synthetic probability (0.0 to 1.0)
  const rawSynth = typeof voice.synthetic_score === 'number' ? voice.synthetic_score : 0.0;
  const clampedSynth = Math.max(0.0, Math.min(1.0, rawSynth));
  const syntheticPercentage = Math.round(clampedSynth * 100);

  // 2. Canonical bona fide probability (0.0 to 1.0)
  let bonaProb: number;
  if (typeof voice.bona_fide_probability === 'number') {
    bonaProb = Math.max(0.0, Math.min(1.0, voice.bona_fide_probability));
  } else {
    // If bona_fide_score was passed as a probability [0, 1] vs raw logit:
    if (typeof voice.bona_fide_score === 'number' && voice.bona_fide_score >= 0.0 && voice.bona_fide_score <= 1.0) {
      bonaProb = voice.bona_fide_score;
    } else {
      bonaProb = 1.0 - clampedSynth;
    }
  }

  const bonaFidePercentage = Math.round(bonaProb * 100);

  return {
    syntheticPercentage,
    bonaFidePercentage,
    rawSyntheticScore: rawSynth,
    rawBonaFideScore: typeof voice.bona_fide_score === 'number' ? voice.bona_fide_score : 0.0,
  };
}
