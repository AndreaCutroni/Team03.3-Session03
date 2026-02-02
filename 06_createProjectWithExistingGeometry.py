"""
06 - Create a Speckle Project on an Existing Project

The project already exists, so we need to provide its ID

"""

from pyexpat import model
from main import get_client
from specklepy.api.client import SpeckleClient
from specklepy.core.api.inputs.model_inputs import CreateModelInput
from specklepy.transports.server import ServerTransport
from specklepy.api import operations

# Replace with your existing project ID
PROJECT_ID = "128262a20c"

# Source model to copy geometry from
SOURCE_MODEL_ID = "7b2da20933"

# Customize your model name using "/" to create folders
MODEL_NAME = "homework/session03/Team_03.3_ac"
MODEL_DESCRIPTION = "My new model in session03 subfolder"

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
    print(f"Created model: {model.id}")

    # Get geometry from source model
    source_model = client.model.get(PROJECT_ID, SOURCE_MODEL_ID)
    latest_version = source_model.versions.items[0]
    
    # Download geometry
    transport = ServerTransport(client=client, stream_id=PROJECT_ID)
    geometry = operations.receive(
        obj_id=latest_version.referencedObject,
        remote_transport=transport
    )
    
    # Upload same geometry to new model
    obj_id = operations.send(base=geometry, transports=[transport])
    
    # Create version in new model
    version = client.version.create(
        model_id=model.id,
        object_id=obj_id,
        message="Copied geometry from source model"
    )




if __name__ == "__main__":
    main()
