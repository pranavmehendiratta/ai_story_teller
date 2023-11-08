from chains.story_chain.chains.refine_idea_chain import refine_idea_chain_v1
from chains.story_chain.chains.wikipedia_keywords_chain import wikipedia_keywords_chain_v1
from chains.story_chain.chains.outline_chain import outline_chain_v1  
from chains.story_chain.chains.chapter_consolidated_outline import chapter_consolidated_outline_chain_v1  
from chains.story_chain.chains.chapters_chain import chapters_chain_v1
from chains.story_chain.chains.logical_sequence_chain import logical_sequence_chain_v1
from chains.story_chain.chains.consolidated_chapters_chain import consolidated_chapters_summary_v1
from loaders.wikipedia_loader import WikipediaLoaderWrapper
from langchain.text_splitter import CharacterTextSplitter
from common.utils import to_snake_case, create_directories, read_text_files_from_directory, concatenate_documents, convert_int_to_word, concatenate_string_using_and, dict_to_document, document_to_dict
from typing import List, Dict, Any
from langchain.schema.document import Document
import json
import shutil
from langchain.callbacks import get_openai_callback
from dotenv import load_dotenv
import os

load_dotenv()

VERSION = "v0"

# MAX_WORDS = 14,000 words
MAX_CONTEXT_SIZE_GPT_3_5 = 50000 # words (7692 - 10000), pages (30.8 - 40.0)
OVERLAP_SIZE = 2000 # words (307 - 400), pages (1.2 - 1.6)

# Directories
REFINE_IDEA_DIR = f"{os.getenv('REFINE_IDEA_DIR')}/{VERSION}"
WIKIPEDIA_KEYWORDS_DIR = f"{os.getenv('WIKIPEDIA_KEYWORDS_DIR')}/{VERSION}"
WIKIPEDIA_DOCUMENTS_DIR = f"{os.getenv('WIKIPEDIA_DOCUMENTS_DIR')}/{VERSION}"
LOGICAL_SEQUENCE_DIR = f"{os.getenv('LOGICAL_SEQUENCE_DIR')}/{VERSION}"
OUTLINE_DIR = f"{os.getenv('OUTLINE_DIR')}/{VERSION}"
CHAPTER_CONSOLIDATED_OUTLINE_DIR = f"{os.getenv('CHAPTER_CONSOLIDATED_OUTLINE_DIR')}/{VERSION}"
CHAPTERS_DIR = f"{os.getenv('CHAPTERS_DIR')}/{VERSION}"
CONSOLIDATED_CHAPTER_DIR = f"{os.getenv('CONSOLIDATED_CHAPTER_DIR')}/{VERSION}"
REFINED_SUMMARY_DIR = f"{os.getenv('REFINED_SUMMARY_DIR')}/{VERSION}"
FINAL_SUMMARY_DIR = f"{os.getenv('FINAL_SUMMARY_DIR')}/{VERSION}"

def get_documents_from_list(
    keywords: List[str]
) -> List[Document]:
    documents_dict: Dict[str, Document] = {}
    for keyword in keywords:
        docs = WikipediaLoaderWrapper.load(
            query = keyword, 
            load_max_docs = 1,
            doc_content_chars_max = 10 * MAX_CONTEXT_SIZE_GPT_3_5
        )

        for doc in docs:
            if doc.metadata["source"] not in documents_dict:
                documents_dict[doc.metadata["source"]] = doc

    print(f"num docs = {len(documents_dict)}")

    split_docs = CharacterTextSplitter(
        chunk_size = MAX_CONTEXT_SIZE_GPT_3_5, 
        chunk_overlap = OVERLAP_SIZE
    ).split_documents(documents = documents_dict.values())

    print(f"num split docs = {len(split_docs)}")

    i = 0
    prev_source = ""
    prev_source_index = 1
    while (i < len(split_docs)):
        doc = split_docs[i]
        if prev_source == doc.metadata["source"]:
            prev_source_index += 1
            doc.metadata["part"] = prev_source_index
        else:
            doc.metadata["part"] = 1
            prev_source_index = 1
        prev_source = doc.metadata["source"]
        doc.metadata["formatted_source"] = f"{doc.metadata['source']}_part_{doc.metadata['part']}"
        i += 1

    for index, doc in enumerate(split_docs):
        print(f"doc {index} = {len(doc.page_content)}, source = {doc.metadata['source']}, part = {doc.metadata['part']}, formatted_source = {doc.metadata['formatted_source']}")
        
    return split_docs


def get_documents(
    topic: str
) -> List[Document]:
    documents = WikipediaLoaderWrapper.load(
        query = topic, 
        load_max_docs = 10,
        doc_content_chars_max = MAX_CONTEXT_SIZE_GPT_3_5
    )

    print(f"num docs = {len(documents)}")
    for index, doc in enumerate(documents):
        print(f"doc {index} = {len(doc.page_content)}, source = {doc.metadata['source']}")
        #print("\n\n")
        #print(doc.page_content)

    split_docs = CharacterTextSplitter(
        chunk_size = MAX_CONTEXT_SIZE_GPT_3_5, 
        chunk_overlap = OVERLAP_SIZE
    ).split_documents(documents = documents)

    print(f"num split docs = {len(split_docs)}")
    for index, doc in enumerate(split_docs):
        print(f"doc {index} = {len(doc.page_content)}, sources = {doc.metadata['source']}")

    concatenate_docs: List[Document] = concatenate_documents(
        documents = split_docs,
        context_size = MAX_CONTEXT_SIZE_GPT_3_5
    )

    print(f"num concatenated docs = {len(concatenate_docs)}")
    for index, doc in enumerate(concatenate_docs):
        print(f"doc {index} = {len(doc.page_content)}, combined_sources = {doc.metadata['combined_sources']}")

    return concatenate_docs

def format_outline(
    outlines_dicts: List[Dict[str, Any]]
) -> str:
    print("Inside format outline")
    formatted_outline = ""
    for outline in outlines_dicts:
        print(f"outline = {outline}")
        formatted_outline += f"source: {outline['source']}\ntitle: {outline['title']}\noutline:\n"
        for index, section in enumerate(outline["sections"]):
            print(f"section = {section}")
            formatted_outline += f"{(index + 1)}. {section['section_title']}\n"
            if "section_subtitles" in section:
                for subtitle in section["section_subtitles"]:
                    formatted_outline += f" - {subtitle}\n"
        formatted_outline += "\n"

    print("------------ Formatted Outline ------------")
    print(formatted_outline)
    print("------------ End Formatted Outline ------------")

    return formatted_outline

def write_outlines_from_docs(
    topic: str,
    language: str,
    document_type: str,
    documents: List[Document],
    outline_topic_dir: str
):   
    create_directories(outline_topic_dir)
    outlines = []
    for index, doc in enumerate(documents):
        outline_dict = outline_chain_v1(
            topic = topic,
            document_type = document_type, 
            doc = doc
        )
        outline_dict["source"] = doc.metadata["formatted_source"]
        outline_file_name = f"{outline_topic_dir}/{index}.json"
        with open(outline_file_name, "w") as f:
            json.dump(outline_dict, f)
        outlines.append(outline_dict)     

def write_formatted_outline(
    outlines_dicts: List[Dict[str, Any]],
    formatted_outline_topic_dir: str
):
    create_directories(formatted_outline_topic_dir)
    formatted_outline_file_name = f"{formatted_outline_topic_dir}/formatted_outline.txt"
    formatted_outline = format_outline(outlines_dicts)
    with open(formatted_outline_file_name, "w") as f:
        f.write(formatted_outline)

def write_chapter_consolidated_outline(
    topic: str,
    logical_sequence_dict: Dict[str, Any],
    formatted_outline: str,
    chapter_consolidated_outline_dir: str      
):
    create_directories(chapter_consolidated_outline_dir)
    chapter_consolidated_outline = chapter_consolidated_outline_chain_v1(
        topic = topic,
        logical_sequence_dict = logical_sequence_dict,
        formatted_outline = formatted_outline
    )
    chapter_consolidated_outline_filename = f"{chapter_consolidated_outline_dir}/chapter_consolidated_outline.json"
    with open(chapter_consolidated_outline_filename, "w") as f:
        json.dump(chapter_consolidated_outline, f)

def find_next_section_title(
    chapter_consolidated_outline: Dict[str, Any],
    current_chapter_index: int,
    current_section_index: int
) -> str:
    chapters = chapter_consolidated_outline["chapters"]
    if current_section_index < len(chapters[current_chapter_index]["sections"]) - 1:
        return chapters[current_chapter_index]["sections"][current_section_index + 1]["section_title"]
    elif current_chapter_index < len(chapters) - 1:
        return chapters[current_chapter_index + 1]["sections"][0]["section_title"]
    else:
        return "This is the last section of the last chapter in the summary so write a great conclusion"

def write_chapters(
    wikipedia_documents_dict: Dict[str, Document],
    chapter_consolidated_outline: Dict[str, Any],
    chapters_dir: str
):
    previous_section_title = "This is the first section of the summary so write a great introduction"
    previous_section_content = "This is the first section of the summary so write a great introduction"
    create_directories(chapters_dir)
    topic = chapter_consolidated_outline["summary_title"]
    chapters = chapter_consolidated_outline["chapters"]
    for chapter_index, chapter in enumerate(chapters):
        chapter_number = convert_int_to_word(
            num = chapter_index + 1,
            total = len(chapters)
        )
        chapter_name = chapter["chapter_name"]
        chapter_sectons = chapter["sections"]
        current_chapter_dir = f"{chapters_dir}/{to_snake_case(chapter_name)}"
        print("current_chapter_dir = ", current_chapter_dir)
        try:
            shutil.rmtree(current_chapter_dir)
            print("Remove current chapter dir")
        except:
            print("Unable to remove the dir")
        try:
            create_directories(current_chapter_dir)
            print("Create current chapter dir")
        except:
            print("Unable to create the dir")
        
        for section_index, section in enumerate(chapter_sectons):
            section_number = convert_int_to_word(
                num = section_index + 1, 
                total = len(chapter_sectons)
            )
            section_title = section["section_title"]
            ideas = section["ideas"]
            formatted_ideas = concatenate_string_using_and(ideas)
            next_section_title = find_next_section_title(
                chapter_consolidated_outline = chapter_consolidated_outline,
                current_chapter_index = chapter_index,
                current_section_index = section_index
            )
            sources = section["sources"]
            for source in sources:
                current_chapter_topic_filename = f"{current_chapter_dir}/{to_snake_case(f'{chapter_name}_{section_title}')}.json"
                section_summary_str = write_chapters_helper(
                    topic = topic,
                    section_number = section_number,
                    chapter_name = chapter_name,
                    chapter_number = chapter_number,
                    section_name = section_title,
                    ideas = formatted_ideas,
                    previous_section_title = previous_section_title,
                    previous_section_content = previous_section_content,
                    next_section_title = next_section_title,
                    document = wikipedia_documents_dict[source],
                    current_chapter_topic_filename = current_chapter_topic_filename
                )
                previous_section_content = section_summary_str
                previous_section_title = section_title
                if "summary" not in section:
                    section["summary"] = {}
                section["summary"][source] = section_summary_str
    
    with open (f"{chapters_dir}/chapters.json", "w") as f:
        json.dump(chapter_consolidated_outline, f)

def write_chapters_helper(
    topic: str,
    section_number: str,
    chapter_name: str,
    chapter_number: str,
    section_name: str,
    ideas: str,
    previous_section_title: str,
    previous_section_content: str,
    next_section_title: str,
    document: Document,
    current_chapter_topic_filename: str
) -> str:

    section_summary_str = chapters_chain_v1(
        topic = topic,
        section_number = section_number,
        chapter_name = chapter_name,
        chapter_number = chapter_number,
        section_name = section_name,
        ideas = ideas,
        previous_section_title = previous_section_title,
        previous_section_content = previous_section_content,
        next_section_title = next_section_title,
        content = document.page_content
    )
    section_summary_dict = {
        "topic": topic,
        "chapter_name": chapter_name,
        "section_name": section_name,
        "source": document.metadata["formatted_source"],
        "section_summary": section_summary_str
    }
    summary_list = []
    try:
        with open(current_chapter_topic_filename, "r") as f:
            content = f.read()
            if content:
                summary_list = json.loads(content)
                summary_list.append(section_summary_dict)
    except FileNotFoundError:
        summary_list.append(section_summary_dict)

    with open(current_chapter_topic_filename, "w") as f:
        json.dump(summary_list, f)

    return section_summary_str

def write_consolidated_chapters(
    chapters: Dict[str, Any],
    consolidated_chapters_dir: str
) -> None:
    print("\n\n\n")
    create_directories(consolidated_chapters_dir)
    consolidated_chapters_filename = f"{consolidated_chapters_dir}/consolidated_chapters.json"
    topic = chapters["summary_title"]
    previous_section_name = "This is the first section of the summary so write a great introduction"
    for chapter_index, chapter in enumerate(chapters["chapters"]):
        for section_index, section in enumerate(chapter["sections"]):
            summaries = "\n\n-- Next Summary --\n\n".join(section["summary"].values())
            ideas = section["ideas"]
            formatted_ideas = concatenate_string_using_and(ideas)
            section_name = section["section_title"]
            next_section_name = find_next_section_title(
                chapter_consolidated_outline = chapters,
                current_chapter_index = chapter_index,
                current_section_index = section_index 
            )

            consolidated_section_summary = consolidated_chapters_summary_v1(
                topic = topic,
                section_name = section_name,
                ideas = formatted_ideas,
                previous_section_name = previous_section_name,
                next_section_name = next_section_name,
                summaries = summaries
            )
            previous_section_name = section_name
            section["consolidated_summary"] = consolidated_section_summary

    with open(consolidated_chapters_filename, "w") as f:
        json.dump(chapters, f)    

def write_refined_summary(
    consolidated_chapters: Dict[str, Any],
    refined_summary_dir: str
):
    create_directories(refined_summary_dir)
    refined_summary_filename = f"{refined_summary_dir}/refined_summary.json"


def write_final_summary(
    refined_summary: Dict[str, Any],
    final_summary_dir: str
):
    print("\n\n\n")
    create_directories(final_summary_dir)
    final_summary_filename = f"{final_summary_dir}/final_summary.txt"
    final_summary = f"Title: {refined_summary['summary_title']}\n\n"
    for chapter in refined_summary["chapters"]:
        final_summary += f"Chapter: {chapter['chapter_name']}\n\n"
        for section in chapter["sections"]:
            final_summary += f"Section: {section['section_title']}\n\n"
            final_summary += section["consolidated_summary"] + "\n\n"
        final_summary += "\n\n"

    with open(final_summary_filename, "w") as f:
        f.write(final_summary)

def write_refined_ideas(
    topic: str,
    refined_ideas_dir: str
) -> None:
    create_directories(refined_ideas_dir)
    refined_ideas_dict = refine_idea_chain_v1(
        topic = topic
    )
    refined_ideas_filename = f"{refined_ideas_dir}/refined_ideas.json"
    with open(refined_ideas_filename, "w") as f:
        json.dump(refined_ideas_dict, f)


def write_wikipedia_keywords(
    idea: str,
    wikipedia_keywords_dir: str
) -> None:
    create_directories(wikipedia_keywords_dir)
    wikipedia_keywords = wikipedia_keywords_chain_v1(
        idea = idea
    )
    wikipedia_dict = {
        "idea": idea,
        "keywords": wikipedia_keywords
    } 
    #print("wikipedia_dict = ", wikipedia_dict)
    wikipedia_keywords_filename = f"{wikipedia_keywords_dir}/wikipedia_keywords_{to_snake_case(idea)}.json"
    with open(wikipedia_keywords_filename, "w") as f:
        json.dump(wikipedia_dict, f)

def write_wikipedia_documents(
    keywords: List[str],
    wikipedia_documents_dir: str
) -> None:
    create_directories(wikipedia_documents_dir)
    wikipedia_documents: List[Document] = get_documents_from_list(keywords = keywords)
    wikipedia_documents_dict = {doc.metadata["formatted_source"]: document_to_dict(doc) for doc in wikipedia_documents}
    with open(f"{wikipedia_documents_dir}/wikipedia_documents.json", "w") as f:
        json.dump(wikipedia_documents_dict, f)

def write_logical_sequence(
    topic: str,
    logical_sequence_dir: str
) -> None:
    create_directories(logical_sequence_dir)
    logical_sequence_dict = logical_sequence_chain_v1(
        topic = topic
    )
    logical_sequence_filename = f"{logical_sequence_dir}/logical_sequence.json"
    with open(logical_sequence_filename, "w") as f:
        json.dump(logical_sequence_dict, f)
            
topics = [
    "Mahatma Gandhi", 
    "History of Golf",
    "Snorkeling Mask",
    "Learning a foreign language",
    "International Space Station",
]

def create_podcast():
    language = "english"

    # Step: Select the topic
    for index, topic in enumerate(topics):
        print(f"{index}. {topic}")
    topic_index = int(input(f"Select the topic you want to create a podcast on (0 throught {len(topics) - 1}) : "))

    topic = topics[topic_index]
    topic_dir_name = f"{to_snake_case(topic)}"
    print(f"user input topic: {topic}")

    # Step: Refine the idea (narrowing it down to focus on certain aspects of the topic)
    refined_ideas_dir = f"{REFINE_IDEA_DIR}/{topic_dir_name}"
    write_refined_ideas(
        topic = topic,
        refined_ideas_dir = refined_ideas_dir
    )
    refined_ideas_list = json.loads(read_text_files_from_directory(refined_ideas_dir)[0])

    # Ask the user for which idea they want to expand on
    joined_refined_ideas = "\n".join([f"{index}. idea = {idea['idea']}, genre_tags = {idea['genre_tags']}" for index, idea in enumerate(refined_ideas_list)])
    print(f"{joined_refined_ideas}")
    idea_index = int(input(f"\n\nSelect the idea you want to expand on (0 throught {len(refined_ideas_list) - 1}) : "))
    idea = refined_ideas_list[idea_index]
    print("selected idea = ", idea)

    # Step: Renaming the topic_dir_name to not chanage the code below
    topic_dir_name = f"{to_snake_case(idea['idea'])}"

    # Step: Get keywords for wikipedia search
    wikipedia_keywords_dir = f"{WIKIPEDIA_KEYWORDS_DIR}/{topic_dir_name}"
    write_wikipedia_keywords(
        idea = idea["idea"],
        wikipedia_keywords_dir = wikipedia_keywords_dir
    )

    wikipedia_keywords_list = [json.loads(keywords) for keywords in read_text_files_from_directory(wikipedia_keywords_dir)]
    for index, wikipedia_keywords in enumerate(wikipedia_keywords_list):
        print(f"{index}.\nidea: {wikipedia_keywords['idea']}\nkeywords = {wikipedia_keywords['keywords']}")

    keyword_index = int(input(f"Select the keywords you want to use (0 throught {len(wikipedia_keywords_list) - 1}) :"))
    wikipedia_keywords = wikipedia_keywords_list[keyword_index]["keywords"]
    
    # Step: Get documents from wikipedia and create content only outline for each document
    wikipedia_documents_dir = f"{WIKIPEDIA_DOCUMENTS_DIR}/{topic_dir_name}"
    write_wikipedia_documents(
        keywords = wikipedia_keywords,
        wikipedia_documents_dir = wikipedia_documents_dir
    )
    wikipedia_documents_dict = json.loads(read_text_files_from_directory(wikipedia_documents_dir)[0])
    wikipedia_documents_dict = {key: dict_to_document(value) for key, value in wikipedia_documents_dict.items()}
    
    # Step: Find the logical sequence to summarize the topic in
    logical_sequence_dir = f"{LOGICAL_SEQUENCE_DIR}/{topic_dir_name}"
    write_logical_sequence(
        topic = idea["idea"],
        logical_sequence_dir = logical_sequence_dir
    )

    logical_sequence_dict = json.loads(read_text_files_from_directory(logical_sequence_dir)[0])

    # Step: Create outline for each document
    outline_topic_dir = f"{OUTLINE_DIR}/{topic_dir_name}"
    write_outlines_from_docs(
        topic = idea,
        language = language, 
        document_type = "wikipedia article",
        documents = wikipedia_documents_dict.values(),
        outline_topic_dir = outline_topic_dir
    )

    outlines = read_text_files_from_directory(outline_topic_dir)    
    outlines_dicts = [json.loads(outline) for outline in outlines]

    # Step: Format the combined outlines to write a chapter based outline
    formatted_outline_topic_dir = f"{OUTLINE_DIR}/{topic_dir_name}/formatted_outline"
    write_formatted_outline(
        outlines_dicts = outlines_dicts,
        formatted_outline_topic_dir = formatted_outline_topic_dir
    )
    formatted_outline = read_text_files_from_directory(formatted_outline_topic_dir)[0]

    # Step: Break the outline into chapters which makes sense based on the outline
    chapter_consolidated_outline_dir = f"{CHAPTER_CONSOLIDATED_OUTLINE_DIR}/{topic_dir_name}"
    write_chapter_consolidated_outline(
        topic = idea["idea"],
        logical_sequence_dict = logical_sequence_dict,
        formatted_outline = formatted_outline,
        chapter_consolidated_outline_dir = chapter_consolidated_outline_dir
    )

    chapter_consolidated_outline = json.loads(read_text_files_from_directory(chapter_consolidated_outline_dir)[0])

    # Step: Write individual chapters from the outline
    chapters_dir = f"{CHAPTERS_DIR}/{topic_dir_name}"
    write_chapters(
        wikipedia_documents_dict = wikipedia_documents_dict,
        chapter_consolidated_outline = chapter_consolidated_outline,
        chapters_dir = chapters_dir
    )

    chapters = json.loads(read_text_files_from_directory(chapters_dir)[0])

    # Step: Combine sections which are written by multiple sources
    consolidated_chapters_dir = f"{CONSOLIDATED_CHAPTER_DIR}/{topic_dir_name}"
    write_consolidated_chapters(
        chapters = chapters,
        consolidated_chapters_dir = consolidated_chapters_dir
    )

    consolidated_chapters = json.loads(read_text_files_from_directory(consolidated_chapters_dir)[0])

    # Step: Refine the summary
    refined_summary_dir = f"{REFINED_SUMMARY_DIR}/{topic_dir_name}"
    """
    write_refined_summary(
        consolidated_chapters = consolidated_chapters,
        refined_summary_dir = refined_summary_dir 
    )
    """
    #refined_summary = read_text_files_from_directory(refined_summary_dir)[0]

    # Step: Write the final summary for the podcast
    final_summary_dir = f"{FINAL_SUMMARY_DIR}/{topic_dir_name}"
    write_final_summary(
        refined_summary = consolidated_chapters,
        final_summary_dir = final_summary_dir
    )

    final_summary_text = read_text_files_from_directory(final_summary_dir)[0]
        
if __name__ == "__main__":
    with get_openai_callback() as cb:
        create_podcast()
        print(f"prompt_tokens = {cb.prompt_tokens}, completion_tokens = {cb.completion_tokens}, total_tokens = {cb.total_tokens}, total_cost = {cb.total_cost}, successful_requests = {cb.successful_requests}")