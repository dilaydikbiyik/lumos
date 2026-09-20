"""
A/B testing prompt versions.

The point is not to run experiments for their own sake — it is that "this
prompt feels better" is not a claim anyone can check, and prompt changes in
this app alter what a beginner is told about their money.

Three properties that matter more than the mechanism:

  STABLE PER READER. Assignment is a hash of the user id, not a coin flip per
  request. Someone mid-conversation must not have the prompt change under
  them between question three and question four — the quiz would contradict
  itself and the reader would think they had done something wrong.

  OFF BY DEFAULT. An experiment with no variants registered returns the
  control, and the control is the prompt the app already ships. Nothing
  becomes an experiment by accident.

  RECORDED, NOT INFERRED. Each response carries the variant that produced it,
  so a judgement can be made afterwards against real replies rather than
  against a memory of which version was live last week.

Deliberately NOT included: automatic promotion of a winner. Changing what a
financial-education app says to people is a decision a person should make,
having read both versions, not something a counter does at 3am.
"""

import hashlib
import logging
from dataclasses import dataclass, field
from typing import Optional

logger = logging.getLogger("lumos.prompt_experiments")


@dataclass(frozen=True)
class Experiment:
    """One prompt under test. `variants` maps a name to a transform."""
    key: str
    # name -> suffix appended to the control prompt. A transform rather than
    # a whole replacement prompt: a variant that forgets the disclaimers or
    # the language rule would be a regression wearing an experiment's hat.
    variants: dict[str, str] = field(default_factory=dict)
    enabled: bool = False


# Registered experiments. Empty variants, disabled, means every reader gets
# the control — which is exactly what should happen until somebody has
# written a variant worth testing and read it through.
EXPERIMENTS: dict[str, Experiment] = {
    "system_prompt": Experiment(key="system_prompt"),
    "advisor_prompt": Experiment(key="advisor_prompt"),
}

CONTROL = "control"


def _bucket(experiment_key: str, user_id: str, variant_count: int) -> int:
    """
    Stable bucket for this reader and this experiment.

    Hashed with the experiment key as well as the user id, so somebody in
    variant B of one experiment is not automatically in variant B of every
    other one — correlated assignment makes two experiments impossible to
    read apart.
    """
    digest = hashlib.sha256(f"{experiment_key}:{user_id}".encode()).digest()
    return int.from_bytes(digest[:4], "big") % variant_count


def assign(experiment_key: str, user_id: Optional[str]) -> str:
    """The variant name for this reader, or `control`."""
    experiment = EXPERIMENTS.get(experiment_key)
    if not experiment or not experiment.enabled or not experiment.variants:
        return CONTROL
    if not user_id:
        # No stable identity, no stable assignment — and an unstable one is
        # worse than none, because it contaminates the comparison.
        return CONTROL

    names = [CONTROL, *sorted(experiment.variants)]
    return names[_bucket(experiment_key, user_id, len(names))]


def apply(experiment_key: str, prompt: str, user_id: Optional[str]) -> tuple[str, str]:
    """
    (prompt, variant_name) for this reader.

    The variant only ever APPENDS to the control, so no variant can drop the
    disclaimers, the language rule or the quiz script by omission.
    """
    variant = assign(experiment_key, user_id)
    if variant == CONTROL:
        return prompt, CONTROL

    experiment = EXPERIMENTS[experiment_key]
    suffix = experiment.variants.get(variant)
    if not suffix:
        return prompt, CONTROL
    return f"{prompt}\n\n{suffix}", variant


def describe() -> dict:
    """What is running, for the admin screen and for the record."""
    return {
        key: {
            "enabled": exp.enabled,
            "variants": [CONTROL, *sorted(exp.variants)],
        }
        for key, exp in EXPERIMENTS.items()
    }
