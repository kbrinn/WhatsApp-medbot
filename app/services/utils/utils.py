# Standard library import
import logging
import os

import structlog
from decouple import config
from langchain.agents import AgentType, initialize_agent, load_tools
from langchain.llms import OpenAI
from langchain_community.chat_models import ChatOpenAI

# Third-party imports
from twilio.rest import Client

# Find your Account SID and Auth Token at twilio.com/console
# and set the environment variables. See http://twil.io/secure
account_sid = config("TWILIO_ACCOUNT_SID")
auth_token = config("TWILIO_AUTH_TOKEN")
client = Client(account_sid, auth_token)
twilio_number = config("TWILIO_PHONE_NUMBER")

# Set up structured logging
logging.basicConfig(level=logging.INFO)
structlog.configure(wrapper_class=structlog.make_filtering_bound_logger(logging.INFO))
logger = structlog.get_logger()


# Sending message logic through Twilio Messaging API
def send_message(to_number, body_text):
    """Send a WhatsApp message and log minimal metadata."""
    masked_to = f"{to_number[:2]}***" if to_number else "***"
    try:
        message = client.messages.create(
            from_=f"whatsapp:{twilio_number}",
            body=body_text,
            to=f"whatsapp:{to_number}",
        )
        logger.info(
            "message_sent", to=masked_to, sid=getattr(message, "sid", "unknown")
        )
    except Exception as e:
        logger.error("send_message_failed", to=masked_to, error=str(e))


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
