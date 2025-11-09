"""This file contains functions for post-processing control narrative"""

import json
from src.utils.s3_download_upload import load_into_memory
from src.control_narrative_lambda.postprocessing import (
    postprocess_hallucinated_control_loops as hallucinated_control_loops,
)
from src.utils.log import logger
from src.control_narrative_lambda.postprocessing.postprocessing_control_loop import (
    removed_unnecessary_control_loop,
)
from src.utils.s3_download_upload import save_json_to_storage


async def postprocess_control_narrative(
    key_aggregated_control_loops,
    bucket_name,
    reconciled_control_loops_path,
    narrative_text,
    **kwargs
):
    """Processes control narrative data."""
    logger.info("INIT: Executing init functions of postprocess control narrative")
    n = kwargs.get("n")
    local_path = kwargs.get("local_path")
    if local_path:
        with open(key_aggregated_control_loops, "r", encoding="utf-8") as f:
            received_control_loop_data = json.load(f)
        reconciled_control_loops = _resolve_and_remove_control_loops(
            received_control_loop_data, narrative_text, n
        )

        with open(reconciled_control_loops_path, "w", encoding="utf-8") as f:
            json.dump(reconciled_control_loops, f)
    else:
        response = await load_into_memory(bucket=bucket_name, path=key_aggregated_control_loops)
        received_control_loop_data = json.loads(response)
        reconciled_control_loops = _resolve_and_remove_control_loops(
            received_control_loop_data, narrative_text, n
        )
        await save_json_to_storage(
            bucket_name, reconciled_control_loops_path, reconciled_control_loops
        )

        # removed_unnecessary_control_loop(bucket_name, reconciled_control_loops_path, n)
    logger.info("DONE: Executed init functions of postprocessing control narrative")


def _resolve_and_remove_control_loops(received_control_loop_data, narrative_text, n):
    """Resolves hallucinated control loops and removes unnecessary control loops."""
    control_loops_resolved = (
        hallucinated_control_loops.resolve_hallucinated_word_in_json(
            received_control_loop_data, narrative_text
        )
    )
    control_loops_final = removed_unnecessary_control_loop(control_loops_resolved, n)
    return control_loops_final
