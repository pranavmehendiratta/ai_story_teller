from langchain.chains import LLMChain
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from chains.story_chain.prompts.outline.outline_human_prompt import human_prompt
from chains.story_chain.prompts.outline.outline_system_prompt import system_prompt
from common.models.base.base_content import BaseContent
from langchain.chains.sequential import SequentialChain
from typing import List, Dict
from langchain.schema.document import Document
import json
from common.utils import to_snake_case

_messages = [
    SystemMessagePromptTemplate(prompt = system_prompt), 
    HumanMessagePromptTemplate(prompt = human_prompt)
]
_llm = ChatOpenAI(temperature = 0, model = "gpt-3.5-turbo-16k")
_chat_prompt = ChatPromptTemplate.from_messages(messages = _messages)
_outline_chain = LLMChain(
    llm = _llm,
    prompt = _chat_prompt,
    verbose = True
)

def outline_chain_v1(
    topic: str,
    language: str,
    documents: List[Document]
) -> List[Dict[str, str]]:
    outlines = []
    for doc in documents:
        outline_str = _outline_chain.run(
            {
                "document_type": "wikipedia website",
                "page_content": doc.page_content
            }
        )
        print(f"---------- Outline {doc.metadata['source']} ----------")
        print(f"{outline_str}")
        print("---------- End Outline ----------")
        outlines.append(
            {
                "source": doc.metadata["source"],
                "content": doc.page_content, 
                "outline": json.loads(outline_str)
            }
        )
    return outlines
