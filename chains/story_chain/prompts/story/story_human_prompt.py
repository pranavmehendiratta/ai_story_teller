from langchain.prompts import StringPromptTemplate

human_promp_template_v1 = """ Write a short story about {topic}"""
input_variables_v1 = ["topic"]

human_promp_template_v2 = """category: {category}
type: {type}
topic: {topic}
length: {length}
tone: {tone}
style: {style}
format: {format}
headers: {headers}
plan: """
input_variables_v2 = ["category", "type", "topic", "length", "tone", "style", "format", "headers"]

class HumanPromptTemplate(StringPromptTemplate):
    template: str

    def format(self, **kwargs):
        kwargs.update(self.partial_variables)
        return self.template.format(**kwargs)

human_prompt = HumanPromptTemplate(
    template = human_promp_template_v2,
    input_variables = input_variables_v2
)