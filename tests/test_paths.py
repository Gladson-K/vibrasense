import paths


def test_database_path_from_environment(tmp_path, monkeypatch):
    target = tmp_path / "custom.db"
    monkeypatch.setenv("VIBRASENSE_DB", str(target))
    assert paths.database_path() == target.resolve()


def test_model_dir_from_environment(tmp_path, monkeypatch):
    target = tmp_path / "models"
    monkeypatch.setenv("VIBRASENSE_MODEL_DIR", str(target))
    assert paths.model_dir() == target.resolve()
