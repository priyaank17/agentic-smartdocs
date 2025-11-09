"""This module contains functions for data sheet accuracy"""

import pandas as pd
from src.utils.log import logger


def save_accuracy_results_to_csv(accuracy_results, file_path):
    """Save accuracy results to csv."""
    logger.info(file_path)
    accuracy_df = pd.DataFrame(accuracy_results)
    accuracy_df.to_csv(file_path, index=False)
