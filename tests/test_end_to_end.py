from bear_brain.router import choose_search_modes


def test_memory_is_default_entry_point() -> None:
    modes = choose_search_modes(task_type="general", repo=None, explicit_refs=False)
    assert modes[0] == "memory_db"
