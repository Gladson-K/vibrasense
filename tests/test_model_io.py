import json

import model_io


def test_artifact_roundtrip(tmp_path):
    path = tmp_path / "model_test.json"
    payload = {"node": "test-node", "features": ["a", "b"], "mu": [0, 0], "sd": [1, 1], "layers": []}
    digest = model_io.write_artifact(path, payload)
    assert model_io.load_verified_artifact(path)["node"] == "test-node"
    assert path.with_suffix(".json.sha256").read_text().strip() == digest


def test_tampered_artifact_is_rejected(tmp_path):
    path = tmp_path / "model_test.json"
    payload = {"node": "test-node", "features": ["a", "b"], "mu": [0, 0], "sd": [1, 1], "layers": []}
    model_io.write_artifact(path, payload)
    data = json.loads(path.read_text())
    data["mu"] = [9, 9]
    path.write_text(json.dumps(data))
    try:
        model_io.load_verified_artifact(path)
    except ValueError as exc:
        assert "hash mismatch" in str(exc)
    else:
        raise AssertionError("tampered model was accepted")
