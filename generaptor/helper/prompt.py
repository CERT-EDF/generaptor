"""Prompt helpers module.

This module provides interactive command-line prompt functionality,
including confirmation and multi-select prompts.
"""

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
    """Prompt for confirmation.

    Args:
        warning (str): Warning message to display before prompting.

    Returns:
        bool: True if user confirmed (yes), False otherwise (no or interrupt).
    """
    print(warning)
    try:
        answer = input("Do you want to proceed? [yes/NO]: ")
    except KeyboardInterrupt:
        return False
    return answer.lower() == 'yes'


@dataclass(kw_only=True)
class Option:
    """Option.

    Represents a selectable option for multi-select prompts.

    Attributes:
        label (str): Display label for the option.
        value: The underlying value associated with this option.
    """

    label: str
    value: Any


def multiselect(title: str, options: list[Option]):
    """Pick multiselection wrapper.

    Provides interactive multi-selection using the pick library.

    Args:
        title (str): Title to display for the selection prompt.
        options (list[Option]): List of Option objects to choose from.

    Returns:
        list: List of selected option values.
    """
    return [
        options[index].value
        for _, index in _pick(
            [option.label for option in options],
            title,
            multiselect=True,
            min_selection_count=1,
        )
    ]
