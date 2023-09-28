from langchain.prompts import StringPromptTemplate

human_prompt_template_v1 = """You are writing a chapter wise summary on {topic}. Write a few paragraphs for the section: '{section}' of chapter: '{chapter}' using the context given below in between three back ticks(```). 
```
{context}
```"""

input_variables_v1 = [
    "topic", 
    "section",
    "chapter",
    "context"
]

class HumanPromptTemplate(StringPromptTemplate):
    template: str

    def format(self, **kwargs):
        kwargs.update(self.partial_variables)
        return self.template.format(**kwargs)

human_prompt = HumanPromptTemplate(
    template = human_prompt_template_v1,
    input_variables = input_variables_v1
)
