"""This function sets the path for the prompts"""

import os

ROOT_FOLDER_PATH = os.path.abspath("")
PROCESS_NARRATIVE_PROMPT_PATH = os.path.join(
    ROOT_FOLDER_PATH, "src/prompts/new_execution_prompt.md"
)
PROCESS_NARRATIVE_PROMPT_RAG_PATH = os.path.join(
    ROOT_FOLDER_PATH, "src/prompts/process_narrative/process_narrative_rag.md"
)
PROCESS_NARRATIVE_PROMPT_RAG_JUNIOR_PATH = os.path.join(
    ROOT_FOLDER_PATH, "src/prompts/process_narrative/process_narrative_rag_junior.md"
)
PROCESS_NARRATIVE_EQUIPMENT_PROMPT_RAG_JUNIOR_PATH = os.path.join(
    ROOT_FOLDER_PATH,
    "src/prompts/process_narrative/pn_equipment_operating_conditions_prompt_rag_junior.md",
)
PROCESS_NARRATIVE_STREAM_CONDITIONS_PARAGRAPH_PROMPT_PATH = os.path.join(
    ROOT_FOLDER_PATH,
    "src/prompts/process_narrative/pn_stream_conditions_prompt_paragraph_rag_junior.md",
)
PROCESS_NARRATIVE_STREAM_CONDITIONS_WRAPPER_PROMPT_JUNIOR_PATH = os.path.join(
    ROOT_FOLDER_PATH,
    "src/prompts/process_narrative/pn_stream_conditions_prompt_wrapper_rag_junior.md",
)
CONTROL_NARRATIVE_INSTRUMENT_PROMPT_RAG_JUNIOR_PATH = os.path.join(
    ROOT_FOLDER_PATH,
    "src/prompts/control_narrative/control_narrative_instrument_prompt_rag_junior.md",
)
CONTROL_NARRATIVE_CONTROL_LOOPS_PROMPT_RAG_JUNIOR_PATH = os.path.join(
    ROOT_FOLDER_PATH,
    "src/prompts/control_narrative/control_narrative_control_loops_prompt_rag_junior.md",
)
CONTROL_NARRATIVE_CONTROLLER_PROMPT_RAG_JUNIOR_PATH = os.path.join(
    ROOT_FOLDER_PATH,
    "src/prompts/control_narrative/controller_prompt_rag_junior.md",
)
PROCESS_NARRATIVE_PROMPT_PNID_PATH = os.path.join(
    ROOT_FOLDER_PATH, "src/prompts/execution_prompt_pnid.md"
)
INSTRUMENT_PROMPT_PATH = os.path.join(
    ROOT_FOLDER_PATH, "src/prompts/control_narrative/prompt_instrument.md"
)
CONTROL_LOOPS_PROMPT_PATH = os.path.join(
    ROOT_FOLDER_PATH, "src/prompts/control_narrative/prompt_control_loops.md"
)
DATA_SHEET_NOZZLES_PROMPT_PATH = os.path.join(
    ROOT_FOLDER_PATH, "src/prompts/data_sheets/nozzles_table.md"
)
DATA_SHEET_TABLE_FORMAT_1_PROMPT_PATH = os.path.join(
    ROOT_FOLDER_PATH, "src/prompts/data_sheets/table_format_1.md"
)
DATA_SHEET_TABLE_FORMAT_2_PROMPT_PATH = os.path.join(
    ROOT_FOLDER_PATH, "src/prompts/data_sheets/table_format_2.md"
)
DATA_SHEET_TABLE_FORMAT_3_PROMPT_PATH = os.path.join(
    ROOT_FOLDER_PATH, "src/prompts/data_sheets/table_format_3.md"
)
PROPERTY_NAME_PROMPT_PATH = os.path.join(
    ROOT_FOLDER_PATH, "src/prompts/data_sheets/property_name.md"
)
