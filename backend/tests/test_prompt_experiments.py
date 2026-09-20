"""
A/B testing prompt versions.

The properties that matter are not "does it split traffic" but "can the
result be trusted and can it hurt anyone": assignment must be stable for a
reader mid-conversation, it must be off unless somebody turned it on, and no
variant may drop the disclaimers or the language rule by omission.
"""
from backend.services import prompt_experiments as pe


def test_nothing_is_an_experiment_by_accident():
    """Registered but disabled, with no variants, means everyone gets control."""
    for key in pe.EXPERIMENTS:
        assert pe.assign(key, "user_123") == pe.CONTROL


def test_assignment_is_stable_for_the_same_reader():
    """
    Someone mid-quiz must not have the prompt change between question three
    and question four — the conversation would contradict itself and they
    would think they had done something wrong.
    """
    exp = pe.Experiment(key="t", variants={"b": "extra"}, enabled=True)
    original = pe.EXPERIMENTS.get("t")
    pe.EXPERIMENTS["t"] = exp
    try:
        first = pe.assign("t", "user_stable")
        for _ in range(50):
            assert pe.assign("t", "user_stable") == first
    finally:
        if original is None:
            pe.EXPERIMENTS.pop("t", None)
        else:
            pe.EXPERIMENTS["t"] = original


def test_two_experiments_do_not_assign_in_lockstep():
    """
    Correlated assignment makes two experiments impossible to read apart, so
    the experiment key is hashed alongside the user id.
    """
    pe.EXPERIMENTS["x"] = pe.Experiment(key="x", variants={"b": "x"}, enabled=True)
    pe.EXPERIMENTS["y"] = pe.Experiment(key="y", variants={"b": "y"}, enabled=True)
    try:
        users = [f"user_{i}" for i in range(200)]
        same = sum(1 for u in users if pe.assign("x", u) == pe.assign("y", u))
        # Independent assignment lands near half; lockstep would be all 200.
        assert 60 < same < 140, same
    finally:
        pe.EXPERIMENTS.pop("x", None)
        pe.EXPERIMENTS.pop("y", None)


def test_a_variant_can_only_add_never_replace():
    """
    A variant that forgot the disclaimers or the language rule would be a
    regression wearing an experiment's hat, so variants append to the control
    rather than replacing it.
    """
    control = "CONTROL PROMPT with disclaimers and the language rule"
    pe.EXPERIMENTS["z"] = pe.Experiment(key="z", variants={"b": "ALSO BE BRIEF"}, enabled=True)
    try:
        for user in (f"user_{i}" for i in range(40)):
            prompt, variant = pe.apply("z", control, user)
            assert control in prompt, variant
            if variant != pe.CONTROL:
                assert "ALSO BE BRIEF" in prompt
    finally:
        pe.EXPERIMENTS.pop("z", None)


def test_no_user_id_means_control_rather_than_a_random_bucket():
    """An unstable assignment is worse than none: it contaminates the result."""
    pe.EXPERIMENTS["w"] = pe.Experiment(key="w", variants={"b": "x"}, enabled=True)
    try:
        assert pe.assign("w", None) == pe.CONTROL
        assert pe.assign("w", "") == pe.CONTROL
    finally:
        pe.EXPERIMENTS.pop("w", None)


def test_an_unknown_experiment_is_not_an_error():
    assert pe.assign("never-registered", "user_1") == pe.CONTROL
    prompt, variant = pe.apply("never-registered", "P", "user_1")
    assert prompt == "P" and variant == pe.CONTROL


def test_describe_reports_what_is_running():
    described = pe.describe()
    assert "system_prompt" in described
    assert described["system_prompt"]["enabled"] is False
    assert pe.CONTROL in described["system_prompt"]["variants"]
