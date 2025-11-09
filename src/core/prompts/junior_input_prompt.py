"""This function specifies the path for the input prompts of Junior."""

import os

ROOT_FOLDER_PATH = os.path.abspath("")


PROCESS_NARRATIVE_EQUIPMENT_OPERATING_CONDITIONS_JUNIOR_INPUT_PATH = os.path.join(
    ROOT_FOLDER_PATH,
    "src/prompts/process_narrative/junior_input_prompt/equipment_operating_conditions.md",
)

PROCESS_NARRATIVE_STREAM_CONDITIONS_JUNIOR_INPUT_PATH = os.path.join(
    ROOT_FOLDER_PATH,
    "src/prompts/process_narrative/junior_input_prompt/stream_conditions.md",
)
