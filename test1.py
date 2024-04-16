import os
from langchain.llms import OpenAI
from langchain import PromptTemplate, LLMChain

os.environ['OPENAI_API_KEY'] = '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'

# build prompt template for simple question-answering
template = """Question: {question}

Answer: """
prompt = PromptTemplate(template=template, input_variables=["question"])

davinci = OpenAI(model_name='text-davinci-003')
llm_chain = LLMChain(
    prompt=prompt,
    llm=davinci
)
question = "Which NFL team won the Super Bowl in the 2010 season?"
print(llm_chain.run(question))
