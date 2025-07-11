from langchain.prompts import PromptTemplate

prompt_template = PromptTemplate(
    input_variables=["data", "question"],
    template="""
You are a digital business analyst.

Here is some weekly sales and media performance data:

{data}

Answer this question using the data above: {question}
"""
)
