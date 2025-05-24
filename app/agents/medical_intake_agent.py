# Add this at the top of your medical_intake_agent.py file
from typing import Dict, List, Any

# Global dictionary to store conversation history by user ID
user_conversations: Dict[str, List[Any]] = {}
from langchain_core.prompts import PromptTemplate, ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI
from langchain.agents import create_react_agent, AgentExecutor, AgentType
from langchain.agents import initialize_agent
from decouple import config
from pathlib import Path
from langchain.memory import ConversationBufferMemory
from langchain.output_parsers import PydanticOutputParser
import json
import os
from .schemas.patient_form_EN import PatientHistory
from datetime import datetime, date
from .tools_agent.pdf_filler_EN import fill_pdf

try:
    OPENAI_API_KEY = config("OPENAI_API_KEY")
except Exception as e:
    print(f"Error loading OPENAI_API_KEY from .env file: {e}")
    raise SystemExit("OPENAI_API_KEY not found. Please set it in your .env file.")


def intake_agent(query: str, user_id: str = "default_user") -> str:
    """
    Medical intake agent that collects patient information and validates it against the PatientHistory schema.
    
    Args:
        query: The patient's input message
        user_id: Unique identifier for the user (e.g., phone number)
        
    Returns:
        A response message from the agent, or validated patient data in JSON format when completed
    """
    llm = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0.0,
        openai_api_key=OPENAI_API_KEY,
    )

    llm_with_tools = llm.bind_tools([fill_pdf])

    # Set up the output parser for validation
    parser = PydanticOutputParser(pydantic_object=PatientHistory)
    
    # Get the directory of the current file (medical_intake_agent.py)
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Navigate to the system_templates directory relative to the current file
    templates_path = os.path.join(current_dir, "system_templates", "patient_intake.txt")
    
    # Load the system prompt template
    system_text = Path(templates_path).read_text(encoding="utf-8")
    
    # Create a chat prompt template
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_text),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{input}")
    ])
    
    # Initialize or get existing chat history for this user
    if user_id not in user_conversations:
        user_conversations[user_id] = []
    
    # Process the input
    chain = prompt | llm
    
    result = chain.invoke({
        "input": query,
        "chat_history": user_conversations[user_id]
    })
    
    # Update conversation history for this user
    user_conversations[user_id].append({"role": "human", "content": query})
    user_conversations[user_id].append({"role": "ai", "content": result.content})
    
    output = result.content
    
    # Check if this looks like the final JSON output (when patient says "done" or "END INTAKE")
    if "**END INTAKE**" in query or (output.strip().startswith("{") and output.strip().endswith("}")):
        try:
            # Try to parse the output as JSON
            # First, extract JSON if there's any text before or after it
            if "{" in output and "}" in output:
                json_start = output.find("{")
                json_end = output.rfind("}") + 1
                json_str = output[json_start:json_end]
            else:
                json_str = output
                
            # Parse the JSON to a dictionary
            patient_data_dict = json.loads(json_str)
            
            # Handle date field conversions (dob and signature_date)
            if "dob" in patient_data_dict and patient_data_dict["dob"]:
                patient_data_dict["dob"] = date.fromisoformat(patient_data_dict["dob"])
            
            if "signature_date" in patient_data_dict and patient_data_dict["signature_date"]:
                patient_data_dict["signature_date"] = date.fromisoformat(patient_data_dict["signature_date"])
            
            # Validate against PatientHistory model
            patient_data = PatientHistory(**patient_data_dict)
            
            # Convert back to JSON string for output
            validated_json = patient_data.model_dump_json(indent=2)
            print(f"Successfully validated patient data against schema")
            
            # Clear the conversation history after successful completion
            user_conversations[user_id] = []
            
            # After successfully validating:
            pdf_path = fill_pdf(patient_data)
            return f"Patient intake form completed and validated:\n{validated_json}\n\nPDF form generated at: {pdf_path}"
            
        except Exception as e:
            # If validation fails, return error and original output
            print(f"Error validating patient data: {e}")
            return f"Patient provided this information, but validation failed: {e}\n\n{output}"
    
    # For normal conversation turns, just return the agent's response
    return output