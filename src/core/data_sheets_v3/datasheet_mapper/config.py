"""."""
import os
import pathlib
import json
import dotenv

dotenv.load_dotenv()

ROOT = pathlib.Path(__file__).parent
PROMPT_PATH = ROOT / "prompts" / "datasheet_mapper.txt"

# os.environ["OPENAI_API_TYPE"] = "azure"
# os.environ["OPENAI_API_KEY"] = None
# os.environ["AZURE_OPENAI_ENDPOINT"] = (
#     "https://smart-documents-drishya-openai-key.openai.azure.com/"
# )
# AZURE_DEPLOY = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4o")


def load_schema(path: pathlib.Path) -> dict:
    """."""
    return json.loads(path.read_text())
