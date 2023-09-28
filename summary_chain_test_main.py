from chains.story_chain.chains.refine_idea_chain import refine_idea_chain_v1
from chains.story_chain.chains.wikipedia_keywords_chain import wikipedia_keywords_chain_v1
from chains.story_chain.chains.outline_chain import outline_chain_v1  
from chains.story_chain.chains.chapter_consolidated_outline import chapter_consolidated_outline_chain_v1  
from chains.story_chain.chains.chapters_chain import chapters_chain_v1
from chains.story_chain.chains.section_chain import section_chain_v1
from chains.story_chain.chains.style_chain import style_chain_v1
from loaders.wikipedia_loader import WikipediaLoaderWrapper
from langchain.text_splitter import CharacterTextSplitter
from common.utils import to_snake_case, create_directories, read_text_files_from_directory, concatenate_documents, get_date_time_string
from typing import List, Dict
from langchain.schema.document import Document
import json
import shutil

VERSION = "v0"

# MAX_WORDS = 14,000 words
MAX_CONTEXT_SIZE_GPT_3_5 = 50000 # words (7692 - 10000), pages (30.8 - 40.0)
OVERLAP_SIZE = 2000 # words (307 - 400), pages (1.2 - 1.6)

# Directories
REFINE_IDEA_DIR = f"/Users/pranavmehendiratta/Documents/projects/story_teller/chains/story_chain/text/refine_idea/{VERSION}"
WIKIPEDIA_KEYWORDS_DIR = f"/Users/pranavmehendiratta/Documents/projects/story_teller/chains/story_chain/text/wikipedia_keywords/{VERSION}"
OUTLINE_DIR = f"/Users/pranavmehendiratta/Documents/projects/story_teller/chains/story_chain/text/outlines/{VERSION}"
CHAPTER_CONSOLIDATED_OUTLINE_DIR = f"/Users/pranavmehendiratta/Documents/projects/story_teller/chains/story_chain/text/chapter_consolidated_outlines/{VERSION}"
CHAPTERS_DIR = f"/Users/pranavmehendiratta/Documents/projects/story_teller/chains/story_chain/text/chapters/{VERSION}"

"""
REFINED_OUTLINE_DIR = f"/Users/pranavmehendiratta/Documents/projects/story_teller/chains/story_chain/text/refined_outline/{VERSION}"  
STYLE_OUTLINE_DIR = f"/Users/pranavmehendiratta/Documents/projects/story_teller/chains/story_chain/text/style/{VERSION}"
SECTIONS_DIR = f"/Users/pranavmehendiratta/Documents/projects/story_teller/chains/story_chain/text/sections/{VERSION}"
SCRIPTS_DIR = f"/Users/pranavmehendiratta/Documents/projects/story_teller/chains/story_chain/text/scripts/{VERSION}"
"""
"""
def main_wikipedia():
    documents = WikipediaLoaderWrapper.load(
        query = topics[0], 
        load_max_docs = 4,
        doc_content_chars_max = 8000
    )
    print(f"num docs = {len(documents)}")
    split_docs = CharacterTextSplitter(chunk_size = 60000, chunk_overlap = 2000).split_documents(documents = documents)
    print(f"num split docs = {len(split_docs)}")
    
    for doc in documents:
        print("source = ", doc.metadata["source"])
        print("page_content = ", doc.page_content)
        print("\n\n")

    print("--> Creating ideas based on the context")
    print("\n\n")
    raw_ideas = ideas_chain_v1(
        topic = topics[0],
        split_docs = split_docs
    )
    print(f"raw_ideas = {raw_ideas}")
    print("\n\n")
    print("--> Refining ideas based on the context")
    outline_chain_v1(
        topic = topics[0],
        raw_ideas = raw_ideas,
        split_docs = split_docs
    )
"""

def get_documents_from_list(
    keywords: List[str]
) -> List[Document]:
    documents_dict: Dict[str, Document] = {}
    for keyword in keywords:
        docs = WikipediaLoaderWrapper.load(
            query = keyword, 
            load_max_docs = 1,
            doc_content_chars_max = MAX_CONTEXT_SIZE_GPT_3_5
        )

        for doc in docs:
            if doc.metadata["source"] not in documents_dict:
                documents_dict[doc.metadata["source"]] = doc

    print(f"num docs = {len(documents_dict)}")
    """
    for index, doc in enumerate(documents_dict.values()):
        print(f"doc {index} = {len(doc.page_content)}, source = {doc.metadata['source']}")
    """

    split_docs = CharacterTextSplitter(
        chunk_size = MAX_CONTEXT_SIZE_GPT_3_5, 
        chunk_overlap = OVERLAP_SIZE
    ).split_documents(documents = documents_dict.values())

    print(f"num split docs = {len(split_docs)}")

    """
    for index, doc in enumerate(split_docs):
        print(f"doc {index} = {len(doc.page_content)}, sources = {doc.metadata['source']}")
    """

    """
    concatenate_docs: List[Document] = concatenate_documents(
        documents = split_docs,
        context_size = MAX_CONTEXT_SIZE_GPT_3_5
    )
    print(f"num concatenated docs = {len(concatenate_docs)}")
    """

    for index, doc in enumerate(split_docs):
        print(f"doc {index} = {len(doc.page_content)}, source = {doc.metadata['source']}")
        
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

def write_outlines_from_docs(
    topic: str,
    language: str,
    documents: List[Document],
    outline_topic_dir: str
):   
    create_directories(outline_topic_dir)
    outlines = outline_chain_v1(
        topic = topic,
        language = language,
        documents = documents
    )
    for index, outline in enumerate(outlines):
        outline_file_name = f"{outline_topic_dir}/{index}.json"
        with open(outline_file_name, "w") as f:
            json.dump(outline, f)

def write_chapter_consolidated_outline(
    topic: str,
    conconcated_outline: str,
    chapter_consolidated_outline_dir: str      
):
    create_directories(chapter_consolidated_outline_dir)
    chapter_consolidated_outline = chapter_consolidated_outline_chain_v1(
        topic = topic,
        conconcated_outline = conconcated_outline
    )
    chapter_consolidated_outline_filename = f"{chapter_consolidated_outline_dir}/chapter_consolidated_outline.json"
    with open(chapter_consolidated_outline_filename, "w") as f:
        json.dump(chapter_consolidated_outline, f)

def write_chapters(
    summary_topic: str,
    wikipedia_documents_dict: Dict[str, Document],
    chapter_consolidated_outline: Dict[str, str],
    chapters_dir: str
):
    create_directories(chapters_dir)
    chapters = chapter_consolidated_outline["chapters"]
    for index, chapter in enumerate(chapters):
        chapter_name = chapter["name"]
        chapter_topics = chapter["topics"]
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
        for topic_with_source in chapter_topics:
            topic = topic_with_source["topic"]
            sources = topic_with_source["sources"]
            for source in sources:
                current_chapter_topic_filename = f"{current_chapter_dir}/{to_snake_case(f'{topic}')}.json"
                section_summary_str = write_chapters_helper(
                    summary_topic = summary_topic,
                    chapter_name = chapter_name,
                    section_topic = topic,
                    document = wikipedia_documents_dict[source],
                    current_chapter_topic_filename = current_chapter_topic_filename
                )
                if "summary" not in topic_with_source:
                    topic_with_source["summary"] = {}
                topic_with_source["summary"][source] = section_summary_str
    
    with open (f"{chapters_dir}/chapters.json", "w") as f:
        json.dump(chapters, f)

def write_chapters_helper(
    summary_topic: str,
    chapter_name: str,
    section_topic: str,
    document: Document,
    current_chapter_topic_filename: str
) -> str:
    section_summary_str = chapters_chain_v1(
        summary_topic = summary_topic,
        chapter_name = chapter_name,
        section_topic = section_topic,
        context = document.page_content
    )
    section_summary_dict = {
        "summary_topic": summary_topic,
        "chapter_name": chapter_name,
        "section_topic": section_topic,
        "source": document.metadata["source"],
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

"""
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

def write_styles(
    topic: str,
    outlines_dict: List[Dict[str, str]],
    style_topic_dir: str
) -> List[Dict[str, str]]:
    create_directories(style_topic_dir)
    styles: List[Dict[str, str]] = []
    for index, outline in enumerate(outlines_dict):
        style = style_chain_v1(
            topic = topic,
            outline = outline["outline"]
        )
        style_file_name = f"{style_topic_dir}/{index}.json"
        with open(style_file_name, "w") as f:
            f.write(style)
        
        styles.append(json.loads(style))
    return styles

def write_sections(
    topic: str,
    styles_dicts: List[Dict[str, str]],
    outline_dicts: List[Dict[str, str]],
    section_topic_dir: str,
    use_gpt_4: bool
):
    for index, style in enumerate(styles_dicts):
        style_dir_name = f"{section_topic_dir}/{index}"
        create_directories(style_dir_name)
        print(f"Working on outline - {index}")
        section_chain_v1(
            topic = topic,
            context = outline_dicts[index]["context"],
            structure = style["structure"],
            style = style["style"],
            narration = style["narration"],
            tone = style["tone"],
            initial_opening = style["opening"],
            section_description = style["sections_description"],
            section_topic_dir_path = style_dir_name,
            use_gpt_4 = use_gpt_4
        )

def make_style_scripts(
    num_sections: int,
    section_topic_dir: str,
    scripts_topic_dir: str
):
    create_directories(scripts_topic_dir)
    for style_index in range(num_sections):
        completed_script = ""
        style_dir_name = f"{section_topic_dir}/{style_index}"
        sections = read_text_files_from_directory(style_dir_name)
        section_dicts = [json.loads(section) for section in sections]
        for section_index, section in enumerate(section_dicts):
            completed_script += section["section_content"] + "\n\n"
            if section_index == len(section_dicts) - 1:
                completed_script += section["next_section_opening"]

        #print(f"---------- Completed Script {style_index} ----------")
        #print(completed_script)
        #print("---------- End Completed Script ----------")

        script_file_name = f"{scripts_topic_dir}/{style_index}.txt"
        with open(script_file_name, "w") as f:
            f.write(completed_script)
"""
            
topics = [
    "Mahatma Gandhi", 
    "History of Golf",
    "Snorkeling Mask",
    "Learning a foreign language"
]

def create_podcast():
    language = "english"
    topic = topics[0]
    topic_dir_name = f"{to_snake_case(topic)}"
    print(f"user input topic: {topic}")

    # Step: Refine the idea (narrowing it down to focus on certain aspects of the topic)
    refined_ideas_dir = f"{REFINE_IDEA_DIR}/{topic_dir_name}"
    write_refined_ideas(
        topic = topic,
        refined_ideas_dir = refined_ideas_dir
    )
    refined_ideas_dict = json.loads(read_text_files_from_directory(refined_ideas_dir)[0])
    ideas = refined_ideas_dict["ideas"]
    genre_tags = refined_ideas_dict["genre_tags"]

    print("genre_tags = ", genre_tags)

    # Ask the user for which idea they want to expand on
    joined_refined_ideas = "\n".join([f"{index}. {idea}" for index, idea in enumerate(ideas)])
    print(f"{joined_refined_ideas}")
    idea_index = int(input(f"\n\nSelect the idea you want to expand on (0 throught {len(ideas) - 1}) : "))
    idea = ideas[idea_index]
    print("selected idea = ", idea)

    # Step: Get keywords for wikipedia search
    wikipedia_keywords_dir = f"{WIKIPEDIA_KEYWORDS_DIR}/{topic_dir_name}"
    """
    write_wikipedia_keywords(
        idea = idea,
        wikipedia_keywords_dir = wikipedia_keywords_dir
    )
    """
    wikipedia_keywords_list = [json.loads(keywords) for keywords in read_text_files_from_directory(wikipedia_keywords_dir)]
    for index, wikipedia_keywords in enumerate(wikipedia_keywords_list):
        print(f"{index}.\nidea: {wikipedia_keywords['idea']}\nkeywords = {wikipedia_keywords['keywords']}")

    keyword_index = int(input(f"Select the keywords you want to use (0 throught {len(wikipedia_keywords_list) - 1}) :"))
    wikipedia_keywords = wikipedia_keywords_list[keyword_index]["keywords"]

    # Step: Get documents from wikipedia and create content only outline for each document
    wikipedia_documents: List[Document] = get_documents_from_list(keywords =  wikipedia_keywords)
    wikipedia_documents_dict = {doc.metadata["source"]: doc for doc in wikipedia_documents} 

    # Step: Create outline for each document
    outline_topic_dir = f"{OUTLINE_DIR}/{topic_dir_name}"
    """
    write_outlines_from_docs(
        topic = idea,
        language = language, 
        documents = wikipedia_documents,
        outline_topic_dir = outline_topic_dir
    )
    """
    outlines = read_text_files_from_directory(outline_topic_dir)    
    outlines_dicts = [json.loads(outline) for outline in outlines]

    # Step: Concatenate the outlines
    """
    concatenated_outlines = [{"source": outline["source"], "outline": outline["outline"] } for outline in outlines_dicts]

    formatted_outline = ""

    for outline in concatenated_outlines:
        formatted_outline += f"Source: {outline['source']}\nTitle: {outline['outline']['title']}Outline:\n"
        for index, section in enumerate(outline["outline"]["sections"]):
            formatted_outline += f"{(index + 1)}. {section['title']}\n"
            for topic in section["topics"]:
                formatted_outline += f" - {topic}\n"
        formatted_outline += "\n"

    for o in concatenated_outlines:
        print(f"source = {o['source']}")
        print(f"outline = {o['outline']}")
        print("\n\n")

    print(formatted_outline)
    """

    # Step: Break the outline into chapters which makes sense based on the outline
    chapter_consolidated_outline_dir = f"{CHAPTER_CONSOLIDATED_OUTLINE_DIR}/{topic_dir_name}"
    """
    write_chapter_consolidated_outline(
        topic = topic,
        conconcated_outline = formatted_outline,
        chapter_consolidated_outline_dir = chapter_consolidated_outline_dir
    )
    """
    chapter_consolidated_outline = json.loads(read_text_files_from_directory(chapter_consolidated_outline_dir)[0])

    print(chapter_consolidated_outline)

    # Step: Write individual chapters from the outline
    chapters_dir = f"{CHAPTERS_DIR}/{topic_dir_name}"
    write_chapters(
        summary_topic = idea,
        wikipedia_documents_dict = wikipedia_documents_dict,
        chapter_consolidated_outline = chapter_consolidated_outline,
        chapters_dir = chapters_dir
    )

    # Step: Combine the chapters



    # Step 3: Refine the outline
    #refined_outline_topic_dir = f"{REFINED_OUTLINE_DIR}/{topic_dir_name}"
    """
    write_refined_outline(
        topic = topic,
        outlines = outlines_dicts,
        refined_outline_topic_dir = refined_outline_topic_dir
    )
    """
    #refined_outline = read_text_files_from_directory(refined_outline_topic_dir)[0]

    # Step 4: Select style and write opening
    """
    style_topic_dir = f"{STYLE_OUTLINE_DIR}/{topic_dir_name}"
    write_styles(
        topic = topic,
        outlines_dict = outlines_dicts,
        style_topic_dir = style_topic_dir
    )

    styles = read_text_files_from_directory(style_topic_dir)
    styles_dicts = [json.loads(style) for style in styles]
    """

    # Step 5: Write a few paragraphs for each section
    """
    use_gpt_4 = False
    gpt_label = "gpt-4" if use_gpt_4 else "gpt-3.5"
    section_topic_dir = f"{SECTIONS_DIR}/{topic_dir_name}/{gpt_label}"
    write_sections(
        topic = topic,
        styles_dicts = styles_dicts,
        outline_dicts = outlines_dicts,
        section_topic_dir = section_topic_dir,
        use_gpt_4 = use_gpt_4
    )
    """

    # Step 6: Combine the sections to create the script
    """
    scripts_topic_dir = f"{SCRIPTS_DIR}/{topic_dir_name}/{gpt_label}"
    make_style_scripts(
        num_sections = len(styles_dicts),
        section_topic_dir = section_topic_dir,
        scripts_topic_dir = scripts_topic_dir
    )
    """
"""
def main_rss_feed():
    documents = RSSFeedLoaderWrapper.load_url(
        url = "https://news.ycombinator.com/rss",
        load_max_docs = 10
    )

    for doc in documents:
        print(doc)
        #print("source = ", doc.metadata["source"])
        #print("page_content = ", doc.page_content)
"""
        
if __name__ == "__main__":
    create_podcast()