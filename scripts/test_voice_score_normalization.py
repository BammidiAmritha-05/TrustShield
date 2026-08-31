import unittest

def normalize_voice_scores_py(synthetic_score, bona_fide_score, bona_fide_probability=None):
    raw_synth = synthetic_score if isinstance(synthetic_score, (int, float)) else 0.0
    clamped_synth = max(0.0, min(1.0, raw_synth))
    synth_pct = round(clamped_synth * 100)
    
    if isinstance(bona_fide_probability, (int, float)):
        bona_prob = max(0.0, min(1.0, bona_fide_probability))
    else:
        if isinstance(bona_fide_score, (int, float)) and 0.0 <= bona_fide_score <= 1.0:
            bona_prob = bona_fide_score
        else:
            bona_prob = 1.0 - clamped_synth
            
    bona_pct = round(bona_prob * 100)
    return synth_pct, bona_pct

class TestVoiceScoreNormalization(unittest.TestCase):
    def test_negative_logit_issue(self):
        # Case observed in bug report: synthetic_score=0.9999, bona_fide_score=-12.84
        synth_pct, bona_pct = normalize_voice_scores_py(0.9999, -12.84, bona_fide_probability=0.0001)
        self.assertEqual(synth_pct, 100)
        self.assertEqual(bona_pct, 0)
        self.assertGreaterEqual(bona_pct, 0)
        self.assertLessEqual(bona_pct, 100)

    def test_natural_speech_case(self):
        # Natural speech: synthetic_score=0.037, bona_fide_score=3.25, bona_fide_probability=0.963
        synth_pct, bona_pct = normalize_voice_scores_py(0.037, 3.25, bona_fide_probability=0.963)
        self.assertEqual(synth_pct, 4)
        self.assertEqual(bona_pct, 96)

    def test_missing_probability_fallback(self):
        # Fallback when bona_fide_probability is omitted
        synth_pct, bona_pct = normalize_voice_scores_py(0.85, -5.2)
        self.assertEqual(synth_pct, 85)
        self.assertEqual(bona_pct, 15)

if __name__ == '__main__':
    unittest.main()
