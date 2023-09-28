from langchain.chains import LLMChain
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from chains.story_chain.prompts.story.story_human_prompt import human_prompt
from chains.story_chain.prompts.story.story_system_prompt import system_prompt
from common.models.base.base_content import BaseContent

_messages = [
    SystemMessagePromptTemplate(prompt = system_prompt), 
    HumanMessagePromptTemplate(prompt = human_prompt)
]
_llm = ChatOpenAI(temperature = 0.7, model = "gpt-4")
_chat_prompt = ChatPromptTemplate.from_messages(messages = _messages)
_story_chain = LLMChain(
    llm = _llm,
    prompt = _chat_prompt,
    verbose = True
)

def story_chain_v1(topic: str) -> str:
    return _story_chain.run(
        {
            "topic" : topic
        }
    )

def story_chain_v2(
    content: BaseContent,
    topic: str
) -> str:
    inputs = {
        "category" : content.content_category,
        "type" : content.content_type,
        "topic" : topic,
        "length" : content.length,
        "tone" : content.tone,
        "style" : content.style,
        "format" : content.format,
        "headers" : content.headers
    }
    print(inputs)
    print(_chat_prompt.format(**inputs))
    story = _story_chain.run(inputs)
    print(story)
    return story
    