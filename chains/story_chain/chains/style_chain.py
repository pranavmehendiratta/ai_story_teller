from langchain.chains import LLMChain
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from chains.story_chain.prompts.style.style_human_prompt import human_prompt
from chains.story_chain.prompts.style.style_system_prompt import system_prompt

_messages = [
    SystemMessagePromptTemplate(prompt = system_prompt), 
    HumanMessagePromptTemplate(prompt = human_prompt)
]
_llm = ChatOpenAI(temperature = 0.5, model = "gpt-4")
_chat_prompt = ChatPromptTemplate.from_messages(messages = _messages)
_style_chain = LLMChain(
    llm = _llm,
    prompt = _chat_prompt,
    verbose = True
)

def style_chain_v1(
    topic: str,
    outline: str
) -> str:
    style_str = _style_chain.run(
        {
            "topic": topic,
            "outline": outline
        }
    )
    print("---------- Style ----------")
    print(style_str)
    print("---------- End Style ----------")
    return style_str