from hardcore.state import BOSS_NAMES, HardcoreState, DeathRecord, save_state, load_state

def test_default_state():
    state = HardcoreState()

    assert state.status == "STOPPED"

def test_default_run_number():
    state = HardcoreState()

    assert state.run_number == 1

def test_default_world_folder():
    state = HardcoreState()

    assert state.world_folder == "world"

def test_default_deaths():
    state = HardcoreState()

    assert state.deaths == []

def test_default_bosses():
    expected_bosses = {boss: False for boss in BOSS_NAMES}

    state = HardcoreState()

    assert state.bosses == expected_bosses

def test_state_round_trip(tmp_path):
    file_path = tmp_path / "state.json"

    original = HardcoreState(run_number=6, status="RUNNING")
    death = DeathRecord(run_number=5, player="TestPlayer", cause="creeper", message="TestPlayer was blown up by Creeper", timestamp="Test time")
    original.deaths.append(death)

    save_state(file_path, original)

    loaded=load_state(file_path)

    assert loaded == original

def test_load_missing_file_returns_default(tmp_path):
    missing_path = tmp_path / "missing.json"

    loaded=load_state(missing_path)

    assert loaded==HardcoreState()
    assert not missing_path.exists()