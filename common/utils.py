import os
import re
from typing import List, Dict
from langchain.schema.document import Document
from datetime import datetime


def get_filename_without_extension(filepath) -> str:
    base_name = os.path.basename(filepath)  # Get the filename with extension
    file_name, file_extension = os.path.splitext(base_name)  # Split filename and extension
    return file_name

def to_snake_case(sentence: str) -> str:
    sentence = sentence.replace('.', '')  # Remove periods
    sentence = re.sub(r'\s+', '_', sentence)  # Replace whitespace sequences with underscore
    return sentence.lower()

def create_directories(path):
    try:
        os.makedirs(path, exist_ok=True)
        print(f"Successfully created directories for path: {path}")
    except Exception as e:
        print(f"Failed to create directories for path: {path}. Reason: {e}")

def read_text_files_from_directory(directory_path) -> List[str]:
    # Check if the given path is a valid directory
    if not os.path.isdir(directory_path):
        print(f"'{directory_path}' is not a valid directory.")
        return []

    # List all files in the directory
    files = os.listdir(directory_path)

    files.sort()

    # Filter out files that are not text files (based on the .txt extension)
    text_files = [f for f in files if f.endswith('.json') or f.endswith('.txt')]

    # Read the contents of each text file and add to the list
    contents = []
    for text_file in text_files:
        with open(os.path.join(directory_path, text_file), 'r') as file:
            contents.append(file.read())

    return contents

def concatenate_documents(
    documents: List[Document], 
    context_size: int
) -> List[Document]:
    # sort the list of documents in ascending order of length
    documents.sort(key = lambda x: len(x.page_content))
    combined_documents: List[Document] = []
    combined_content = ""
    combined_sources = []
    current_size = 0
    source_label = "source: "
    content_label = "content: "

    for doc in documents:
        # Calculate the size of appending this document, considering two new lines
        additional_size = len(doc.page_content) + len(doc.metadata["source"]) + len(source_label) + len(content_label) + 4  # 4 for two new lines
        new_size = current_size + additional_size
        
        # Check if appending this document would exceed the limit
        if new_size <= context_size:
            combined_content += f"{source_label}{doc.metadata['source']}\n\n{content_label}{doc.page_content}\n\n"
            combined_sources.append(doc.metadata["source"])
            current_size = new_size
        else:
            combined_documents.append(
                Document(
                    page_content = combined_content,
                    metadata = {"combined_sources": combined_sources}
                )
            )
            new_size = additional_size
            current_size = additional_size
            combined_content = f"{source_label}{doc.metadata['source']}\n\n{content_label}{doc.page_content}\n\n"
            combined_sources = [doc.metadata["source"]]
            
    if combined_content != "":
        combined_documents.append(
            Document(
                page_content = combined_content,
                metadata = {"combined_sources": combined_sources}
            )
        )
    
    return combined_documents

def get_date_time_string() -> str:
    # Getting the current date and time
    now = datetime.now()
    
    # Formatting date and time as a string (e.g., "2023-09-19 12:34:56")
    date_time_str = now.strftime("%Y-%m-%d %H:%M:%S")
    
    return date_time_str

def concatenate_string_using_and(strings: List[str]) -> str:
    if not strings:
        return ""
    if len(strings) == 1:
        return strings[0]
    return ", ".join(strings[:-1]) + ", and " + strings[-1]

def convert_int_to_word(
    num: int,
    total: int
) -> str:
    if total == 1:
        return "only"
    
    label = ""

    if num == 1:
        label = "first"
    elif num == 2:
        label = "second"
    elif num == 3:
        label = "third"
    elif num == 4:
        label = "fourth"
    elif num == 5:
        label = "fifth"
    elif num == 6:
        label = "sixth"
    elif num == 7:
        label = "seventh"
    elif num == 8:
        label = "eighth"
    elif num == 9:
        label = "ninth"
    elif num == 10:
        label = "tenth"
    else:
        raise ValueError(f"Invalid number: {num}. Right now can only handle upto 10.")
    
    if num == total:
        label = "last"

    return label

def document_to_dict(doc: Document) -> Dict:
    return {
        "page_content": doc.page_content,
        "metadata": doc.metadata
    }

def dict_to_document(doc_dict: Dict) -> Document:
    return Document(
        page_content = doc_dict["page_content"],
        metadata = doc_dict["metadata"]
    )