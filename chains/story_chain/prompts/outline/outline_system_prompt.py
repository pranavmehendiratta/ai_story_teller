from langchain.prompts import StringPromptTemplate

system_prompt_template_v0 = """You are summarizing a set of articles, books, blogs, websites, etc. Before summarizing, you will be given content of a parsed {document_type} in between three back ticks(```). Write an outline for this content that you will later use for summarizing. Use topic as a guide for writing the outline. You should assume the content is not clean and contains metadata such as reference to other source could be websites, links etc.. - remember to remove exclude the metadata from the outline.

Output as a JSON:
{{
    "title": write a title based on the content of the document
    "section": [ // List of all the sections
        {{ // section format
            "title": section title
            "topics": list of topics to cover in the section
         }}
    ]
}}"""

input_variables_v0 = ["document_type"]

system_prompt_template_v1 = """You are an individual host for an audio only podcast which is popular for using only wikipedia as the source. You will be given a topic for which you need to write a detailed outline using the set of documents and their sources in between three back ticks (```). You always write citations in the outline so that you can easily refer back to the original sources when writing the script. You should remove any unrelated information from the outline.

Output as a JSON:
[ // List of all the sections
    {{ // section format
        "title": section title
        "topics": list of topics to cover in the section
    }}
]"""


class SystemPromptTemplate(StringPromptTemplate):
    template: str

    def format(self, **kwargs):
        kwargs.update(self.partial_variables)
        return self.template.format(**kwargs)

system_prompt = SystemPromptTemplate(
    template = system_prompt_template_v0,
    input_variables = input_variables_v0,
    partial_variables = {}
)   