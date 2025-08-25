"""Prompt helpers"""

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


def multiselect(title, options):
    """Pick multiselection wrapper"""
    return [
        option
        for option, _ in _pick(
            options, title, multiselect=True, min_selection_count=1
        )
    ]
