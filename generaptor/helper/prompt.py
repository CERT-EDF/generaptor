"""Prompt helpers"""

from dataclasses import dataclass
from typing import Any

from .logging import get_logger

_LOGGER = get_logger('helper.prompt')

try:
    from pick import pick as _pick

    _LOGGER.info("interactive prompt available")
    INTERACTIVE_PROMPT_AVAILABLE = True
except ImportError:

    def _pick(*args, **kwargs):
        raise RuntimeError("interactive prompt is not available!")

    _LOGGER.warning("interactive prompt is not available")
    INTERACTIVE_PROMPT_AVAILABLE = False


def confirm(warning):
    """Prompt for confirmation"""
    print(warning)
    try:
        answer = input("Do you want to proceed? [yes/NO]: ")
    except KeyboardInterrupt:
        return False
    return answer.lower() == 'yes'


@dataclass(kw_only=True)
class Option:
    """Option"""

    label: str
    value: Any


def multiselect(title: str, options: list[Option]):
    """Pick multiselection wrapper"""
    return [
        options[index].value
        for _, index in _pick(
            [option.label for option in options],
            title,
            multiselect=True,
            min_selection_count=1,
        )
    ]
