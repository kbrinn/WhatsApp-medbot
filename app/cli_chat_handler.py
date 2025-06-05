#!/usr/bin/env python3

# Import the necessary modules
from .agents.medical_intake_agent import intake_agent, user_patient_ids
from .services.secure_storage import store_conversation
from .services.utils.utils import logger


def run_cli_chat():
    """Run a command-line interface for the chatbot."""
    print("Welcome to the MedBot CLI. Type 'exit' to quit.")

    while True:
        user_input = input("\nYou: ")
        if user_input.lower() in ["exit", "quit"]:
            print("Goodbye!")
            break

        # Process the input through the medical intake agent
        response = intake_agent(user_input, user_id="cli_user")

        if "cli_user" in user_patient_ids:
            try:
                store_conversation(
                    "cli_user",
                    user_input,
                    response,
                    patient_id=user_patient_ids["cli_user"],
                )
                print(f"\nMedBot: {response}")
            except Exception as e:
                print(f"\nMedBot: {response}")
                logger.error(f"Error storing CLI conversation: {e}")
        else:
            print(f"\nMedBot: {response}")


if __name__ == "__main__":
    run_cli_chat()
