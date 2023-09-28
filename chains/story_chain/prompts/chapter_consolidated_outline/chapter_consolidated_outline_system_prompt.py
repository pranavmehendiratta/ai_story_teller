from langchain.prompts import StringPromptTemplate

system_prompt_template_v0 = """You are summarizing a set of articles, books, blogs, etc. Let's collectively call them documents. You have created an outline of each individual document you have read. Before making a consolidated summary of the documents, you want to group together similar ideas/topics into a chapter wise consolidated outline. Use the given topic as your guide for what to include/exclude. You should give a catchy name for every chapter. For every chapter add list of source for that chapter.

Output as a JSON (only output JSON nothing else!):
{{
    "chapters": [
        "name": catchy name of the chapter,
        "topics": [ // list of topics that make up this idea
            {{
                "topic": topic to cover,
                "sources: list of sources for this topic
            }}
        ],
       
    ]
}}"""

class SystemPromptTemplate(StringPromptTemplate):
    template: str

    def format(self, **kwargs):
        kwargs.update(self.partial_variables)
        return self.template.format(**kwargs)

system_prompt = SystemPromptTemplate(
    template = system_prompt_template_v0,
    input_variables=[],
    partial_variables={}
)   