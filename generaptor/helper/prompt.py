"""Prompt helpers
"""
from pick import pick


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
        for option, _ in pick(
            options, title, multiselect=True, min_selection_count=1
        )
    ]
