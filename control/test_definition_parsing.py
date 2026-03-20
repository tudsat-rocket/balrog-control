"""Parse files with sequence definitions.

This module provide method to load sequence from a
file and construct a list of actions from that.
"""

import csv
import os

from .definitions import ActionType, str_to_action


def parse_csv(file: os.PathLike) -> list[tuple[str, int, ActionType]]:
    """Parse a test definition from a CSV file.

    With this CSV you can load a sequence of actions.
    """
    event_sequence = []

    with open(file, newline="") as test_definition:
        reader = csv.reader(test_definition, delimiter=",", quotechar="|")

        # Skip header line
        next(reader)

        for row in reader:
            try:
                actor_name = row[0]
                t_ms = int(row[1])
                action_str = row[2]
            except Exception as err:
                raise RuntimeError(f"Error parsing {file}: {err}") from err

            action = str_to_action(action_str)

            if action == ActionType.NOT_IMPLEMENTED:
                raise RuntimeError(f"Invalid Action Type: '{action_str}'")

            row_tuple = (actor_name, t_ms, action)
            event_sequence.append(row_tuple)

    event_sequence.sort(key=lambda x: x[1])
    return event_sequence
