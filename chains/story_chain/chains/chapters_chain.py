from langchain.chains import LLMChain
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from chains.story_chain.prompts.chapters.chapters_system_prompt import system_prompt
from chains.story_chain.prompts.chapters.chapters_human_prompt import human_prompt
from typing import List
import json

_messages = [
    SystemMessagePromptTemplate(prompt = system_prompt), 
    HumanMessagePromptTemplate(prompt = human_prompt)
]
_llm = ChatOpenAI(temperature = 0, model = "gpt-3.5-turbo-16k")
_chat_prompt = ChatPromptTemplate.from_messages(messages = _messages)
_chapters_chain = LLMChain(
    llm = _llm,
    prompt = _chat_prompt,
    verbose = True
)

def chapters_chain_v1(
    summary_topic: str,
    chapter_name: str,
    section_topic: str,
    context: str
) -> str:
    section_summary_str = _chapters_chain.run(
        {
            "topic": summary_topic,
            "chapter": chapter_name,
            "section": section_topic,
            "context": context
        }
    )
    print(f"---------- Section {section_topic} Summary ----------")
    print(section_summary_str)
    print("---------- End of Section Summary ----------")
    return section_summary_str