# Standard library import
import logging
import os

# Third-party imports
from twilio.rest import Client
from decouple import config
from langchain.agents import load_tools
from langchain.agents import initialize_agent
from langchain.agents import AgentType
from langchain.llms import OpenAI
from langchain_community.chat_models import ChatOpenAI



# Find your Account SID and Auth Token at twilio.com/console
# and set the environment variables. See http://twil.io/secure
account_sid = config("TWILIO_ACCOUNT_SID")
auth_token = config("TWILIO_AUTH_TOKEN")
client = Client(account_sid, auth_token)
twilio_number = config('TWILIO_PHONE_NUMBER')

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Sending message logic through Twilio Messaging API
def send_message(to_number, body_text):
    try:
        message = client.messages.create(
            from_=f"whatsapp:{twilio_number}",
            body=body_text,
            to=f"whatsapp:{to_number}"
            )
        logger.info(f"Message sent to {to_number}: {message.body}")
    except Exception as e:
        logger.error(f"Error sending message to {to_number}: {e}")

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
        model="gpt-3.5-turbo"  # Specify the model explicitly
    )
    tools = load_tools(["wikipedia"], llm=llm)
    agent = initialize_agent(tools, llm, agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION, verbose=False)
    return agent.run(query)
