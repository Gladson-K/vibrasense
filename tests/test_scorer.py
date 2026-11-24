import numpy as np

import model_io
from models import SafeMLP, Scorer


def make_payload():
    return {
        "node": "node-1",
        "features": ["a", "b"],
        "mu": [1.0, 2.0],
        "sd": [2.0, 4.0],
        "layers": [
            {"coefs": [[1.0, 0.0], [0.0, 1.0]], "intercepts": [0.0, 0.0], "activation": "relu"},
            {"coefs": [[1.0, 1.0], [1.0, -1.0]], "intercepts": [0.0, 0.0], "activation": "linear"},
        ],
    }


def test_safe_mlp_predicts_without_pickle():
    mlp = SafeMLP(make_payload())
    out = mlp.predict([[3.0, 6.0]])
    assert np.allclose(out, [[2.0, 0.0]])


def test_scorer_loads_verified_artifact_only(tmp_path):
    payload = make_payload()
    payload["features"] = [
        "rms_vel", "peak", "crest", "kurt", "cur_rms", "temp", "b1", "b2", "b3",
    ]
    payload["mu"] = [0.0] * 9
    payload["sd"] = [1.0] * 9
    payload["layers"] = [
        {"coefs": [[0.0] * 9], "intercepts": [0.0], "activation": "linear"},
    ]
    path = tmp_path / "model_node-1.json"
    model_io.write_artifact(path, payload)
    scorer = Scorer()
    scorer.load_autoencoders(tmp_path)
    assert "node-1" in scorer.aes


def test_invalid_node_is_ignored():
    scorer = Scorer()
    scorer.on_telemetry("../etc", {"rms_vel": 1.0})
    assert "../etc" not in scorer.fsm
