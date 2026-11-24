from models import FEATURES, Scorer


def test_seeded_fault_detection_rate():
    rng = __import__("numpy").random.default_rng(11)
    node = "l2-seed-01"
    scorer = Scorer()
    for _ in range(240):
        row = {
            "rms_vel": 1.0 + rng.normal(0, 0.02),
            "peak": 1.2 + rng.normal(0, 0.02),
            "crest": 1.2 + rng.normal(0, 0.01),
            "kurt": 3.0 + rng.normal(0, 0.05),
            "cur_rms": 4.0 + rng.normal(0, 0.03),
            "temp": 40.0 + rng.normal(0, 0.1),
            "b1": 0.01 + rng.normal(0, 0.002),
            "b2": 0.02 + rng.normal(0, 0.002),
            "b3": 0.01 + rng.normal(0, 0.002),
        }
        scorer.on_telemetry(node, row)

    states = []
    for _ in range(40):
        row = {
            "rms_vel": 2.4 + rng.normal(0, 0.02),
            "peak": 3.0 + rng.normal(0, 0.02),
            "crest": 2.5 + rng.normal(0, 0.01),
            "kurt": 8.0 + rng.normal(0, 0.05),
            "cur_rms": 6.5 + rng.normal(0, 0.03),
            "temp": 49.0 + rng.normal(0, 0.1),
            "b1": 0.9 + rng.normal(0, 0.01),
            "b2": 1.1 + rng.normal(0, 0.01),
            "b3": 0.7 + rng.normal(0, 0.01),
        }
        scorer.on_telemetry(node, row)
        states.append(scorer.fsm[node].state)

    assert len(FEATURES) == 9
    assert states.count("ALARM") / len(states) >= 0.90
