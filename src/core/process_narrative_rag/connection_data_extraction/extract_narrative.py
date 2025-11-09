"""Extaract narrative data from pdf file."""

import os
import tempfile
from PyPDF2 import PdfReader
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from src.utils.storage_utils import (
    fetch_file_via_adapter,
    upload_file_to_storage
)
from src.process_narrative_rag.connection_data_extraction.narrative_llm import (
    get_prompt,
    llm_extraction,
)
from src.process_narrative_rag.connection_data_extraction.generate_process_narrative_adm import (
    get_process_narrative_adm,
)
from src.utils.log import logger
from src.utils.s3_download_upload import (
    download_storage_file,
)
from src.utils.local_utils import load_local_json
from src.utils.get_source_destination import (
    process_equipment_connectivity,
)
from src.prompts.prompt import PROCESS_NARRATIVE_PROMPT_RAG_PATH


async def _get_text_from_pdf(bucket_name, pdf_file_path, local_input_files):
    """
    Reads text from a PDF file and concatenates the content of all pages.
    """
    logger.info(f"Init: Reading text from {pdf_file_path}")
    is_scanned = True
    if local_input_files:
        pdf_reader = PdfReader(pdf_file_path)
    else:
        with tempfile.TemporaryDirectory() as temp_dir:
            local_path = os.path.join(temp_dir, "process_narrative.pdf")
            await download_storage_file(bucket_name, pdf_file_path, local_path)
            pdf_reader = PdfReader(local_path)

    raw_text = ""
    for _, page in enumerate(pdf_reader.pages):
        content = page.extract_text()
        if content:
            raw_text += content
            is_scanned = False
    if is_scanned:
        logger.error(
            f"The PDF at {pdf_file_path} appears to be scanned (contains no text)."
        )
        return None
    logger.info(f"Done: Read text from {pdf_file_path}")
    return raw_text


def split_text_into_chunks(raw_text, chunk_size=800, chunk_overlap=200, separator="."):
    """
    Splits the given text into chunks based on the specified parameters.
    """
    logger.info("Init: Splitting text into chunks")
    text_splitter = CharacterTextSplitter(
        separator=separator,
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
    )
    texts = text_splitter.split_text(raw_text)
    logger.info("Done: Split text into chunks")
    return texts


def create_document_search(texts):
    """
    Creates a FAISS document search index from a list of texts using OpenAI embeddings.
    """
    logger.info("Init: Creating FAISS document search index")
    embeddings = OpenAIEmbeddings()
    document_search = FAISS.from_texts(texts, embeddings)
    logger.info("Done: Creating document search")
    return document_search


def search_documents(document_search, query, k=5):
    """
    Searches for documents similar to the query and concatenates their content.
    """
    logger.info("Init: Searching for text similar to the query from document")
    docs = document_search.similarity_search(query, k)
    data = "".join([doc.page_content for doc in docs])
    logger.info("Done: Searching for text similar to the query from document")
    return data


def extracted_data_for_a_query(
    model_name, document_search, connection, prompt_template
):
    """Extract narrative data using LLM models."""
    logger.info("Init: Extracting narrative data using LLM models")
    sources_asset_name = connection.get("source_asset_name")
    destination_asset_name = connection.get("destination_asset_name")
    search_query = f"'{sources_asset_name}' and '{destination_asset_name}'"
    llm_query = (
        f"source_asset_name: {sources_asset_name}\n"
        f"destination_asset_name: {destination_asset_name}"
    )
    data = search_documents(document_search, search_query)
    # print("length", len(data))
    # llm_extracted_output = None
    llm_extracted_output = llm_extraction(model_name, data, llm_query, prompt_template)
    logger.info(f"Query: {search_query}")
    logger.info("Done: Extracting narrative data using LLM models")
    return llm_extracted_output


def _get_extracted_data_for_all_query(
    pdf_text, model_name, pid_source_destination_connection_data
):
    """Extract narrative data from the PDF file."""
    logger.info("Init: Extracting narrative data from the PDF file for all the queries")
    separator = "."
    chunk_size = 1000
    chunk_overlap = 200
    texts = split_text_into_chunks(pdf_text, chunk_size, chunk_overlap, separator)
    document_search = create_document_search(texts)
    prompt_template = get_prompt(PROCESS_NARRATIVE_PROMPT_RAG_PATH)
    output = []
    for connection in pid_source_destination_connection_data:
        query_extract_data = extracted_data_for_a_query(
            model_name, document_search, connection, prompt_template
        )
        if query_extract_data:
            logger.info(f"Extracted data: {query_extract_data}")
            output.extend(query_extract_data)
    logger.info("Done: Extracting narrative data from the PDF file for all the queries")
    return output


async def get_pid_source_destination_connection_data(
    bucket_name, plant_id, pnid_connections_json_path, local_input_files=False
):
    """Load PID source-destination connection data"""
    if local_input_files:
        pid_source_destination_connection_data = load_local_json(
            pnid_connections_json_path
        )
    else:
        await process_equipment_connectivity(
            bucket_name, plant_id, pnid_connections_json_path
        )
        pid_source_destination_connection_data = await fetch_file_via_adapter(
            bucket_name, pnid_connections_json_path
        )

    if pid_source_destination_connection_data is None:
        logger.error(
            "PID source-destination connection data is either unavailable or empty"
        )
    return pid_source_destination_connection_data


async def get_data(
    input_files_path,
    model_name,
    adm_json_path,
    save_to_local=False,
    local_input_files=False,
):
    """Get data"""
    pid_connections_json_path = input_files_path.get(
        "pid_source_destination_connection_path"
    )
    pdf_file_path = input_files_path.get("pdf_file_path")
    bucket_name = input_files_path.get("bucket_name")
    plant_id = input_files_path.get("plant_id")
    document_id = input_files_path.get("document_id")
    pid_source_destination_connection_data = (
        await get_pid_source_destination_connection_data(
            bucket_name, plant_id, pid_connections_json_path, local_input_files
        )
    )

    json_data = {
        "meta_data": {},
        "connections": [],
    }

    pdf_text = await _get_text_from_pdf(bucket_name, pdf_file_path, local_input_files)
    if pdf_text:
        connection_data = _get_extracted_data_for_all_query(
            pdf_text, model_name, pid_source_destination_connection_data
        )
        json_data = get_process_narrative_adm(json_data, connection_data, document_id)
        storage_type = "local" if save_to_local else "storage"
        logger.info(f"Saving to {storage_type} in {adm_json_path}")
        await upload_file_to_storage(
            bucket_name,
            adm_json_path,
            json_data,
        )
