"""
01 - Create a Speckle Model within an existing Project

The project already exists, so we need to provide its ID

"""

from pyexpat import model
from main import get_client
from specklepy.core.api.inputs.model_inputs import CreateModelInput

# Replace with your existing project ID
PROJECT_ID = "128262a20c" #CW26-Sessions

# Customize your model name using "/" to create folders
MODEL_NAME = "homework/session03/Team_03.3_ac"
MODEL_DESCRIPTION = "Homework_Sessione03"

def main():
    # Authenticate
    client = get_client()
    
    # Create a new model inside the existing project
    model_input = CreateModelInput(
        project_id=PROJECT_ID,
        name=MODEL_NAME,  # <-- The key part!
        description=MODEL_DESCRIPTION
    )

    model = client.model.create(model_input)
    
    # Get the created model details
    print(f"Created model: {model.id}")
    print(f"Model name: {model.name}")
    print(f"Model description: {model.description}")


if __name__ == "__main__":
    main()
