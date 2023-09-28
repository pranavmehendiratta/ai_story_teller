from langchain.prompts import StringPromptTemplate

system_prompt_template_v1 = """You are writing a script for a podcast. You already have  detailed outline for the sub-topics you might want to cover in the podcast. Before writing the script, you want to come up style, tone, narration, structure and opening for the script so you can expand on it later. You are allowed to choose a subset of ideas from the outline. 

Podcast Information:
num_of_hosts: you are the only host
num_of_podcasts: this topic needs to be covered in one podcast episode of about 20 mins long

Output only json object (DO NOT ADD ANYTHING ELSE IN THE OUTPUT!):
{{
    "structure": write about the structure in detail,
    "style": write about the style in detail,
    "tone": write about the tone in detail,
    "narration": write about the narration in detail,
    "opening": write an engaging opening based on style, structure, tone and narration,
    "num_of_sections": write the number of sections based on structure, style, tone, and narration. Only write one number here
    "sections_description": list of section descriptions [write the a brief description on ideas you want cover in each sections]
}}
"""

"""
Output in the following format:
```JSON


"""
class SystemPromptTemplate(StringPromptTemplate):
    template: str

    def format(self, **kwargs):
        kwargs.update(self.partial_variables)
        return self.template.format(**kwargs)

system_prompt = SystemPromptTemplate(
    template = system_prompt_template_v1,
    input_variables=[],
    partial_variables={}
)   