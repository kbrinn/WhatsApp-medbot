# Standard library import
import logging

import structlog
from decouple import config
from langchain.agents import AgentType, initialize_agent, load_tools
from langchain_community.chat_models import ChatOpenAI

# Third-party imports

# Set up structured logging
logging.basicConfig(level=logging.INFO)
structlog.configure(wrapper_class=structlog.make_filtering_bound_logger(logging.INFO))
logger = structlog.get_logger()


# def search_wikipedia(query):
#
#         """Search Wikipedia through the LangChain API
#            and use the OpenAI LLM wrapper and retrieve
#            the agent result based on the received query
#         """
#         llm = OpenAI(model_name = "gpt-3.5-turbo", temperature=0, openai_api_key=config("OPENAI_API_KEY"))
#         tools = load_tools(["wikipedia"], llm=llm)
#         agent = initialize_agent(tools, llm, agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION, verbose=False)
#         return agent.run(query)


def search_wikipedia(query):
    """Search Wikipedia through the LangChain API
    and use the OpenAI LLM wrapper and retrieve
    the agent result based on the received query
    """
    llm = ChatOpenAI(
        temperature=0,
        openai_api_key=config("OPENAI_API_KEY"),
        model="gpt-3.5-turbo",  # Specify the model explicitly
    )
    tools = load_tools(["wikipedia"], llm=llm)
    agent = initialize_agent(
        tools, llm, agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION, verbose=False
    )
    return agent.run(query)
