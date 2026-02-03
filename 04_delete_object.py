"""
04 - Delete an Object by applicationId

This script demonstrates how to find and delete an object by its applicationId
from a Speckle model.
"""

from main import get_client
from specklepy.transports.server import ServerTransport
from specklepy.api import operations
from specklepy.objects.base import Base
from specklepy.core.api.inputs.version_inputs import CreateVersionInput


PROJECT_ID = "128262a20c"
MODEL_ID = "9ec0d0a2a2"

# Replace with the applicationId of the object to delete
TARGET_APPLICATION_ID = "faf44926-0984-4566-b681-95c457ac42fc"


def find_and_delete_object(obj, target_id: str):
    """
    Recursively search for and delete an object with the given applicationId.
    Returns True if object was found and deleted, False otherwise.
    """
    if not isinstance(obj, Base):
        return False
    
    # Check direct elements
    elements = getattr(obj, "@elements", None) or getattr(obj, "elements", None)
    if elements:
        # Find and remove the object
        for i, element in enumerate(elements):
            app_id = getattr(element, "applicationId", None)
            if app_id == target_id:
                elements.pop(i)
                return True
        
        # Recursively search in child elements
        for element in elements:
            if find_and_delete_object(element, target_id):
                return True
    
    return False


def main():
    # Authenticate
    client = get_client()
    
    # Get the latest version
    versions = client.version.get_versions(MODEL_ID, PROJECT_ID, limit=1)
    if not versions.items:
        print("No versions found.")
        return
    
    latest_version = versions.items[0]
    print(f"✓ Fetching version: {latest_version.id}")
    
    # Receive the full data tree
    transport = ServerTransport(client=client, stream_id=PROJECT_ID)
    data = operations.receive(latest_version.referenced_object, transport)
    
    # Find and delete the target object
    print(f"\n--- Delete object {TARGET_APPLICATION_ID} ---")
    
    if find_and_delete_object(data, TARGET_APPLICATION_ID):
        print(f"✓ Object deleted successfully")
    else:
        print(f"✗ Could not find object with applicationId: {TARGET_APPLICATION_ID}")
        return
    
    # Send the modified data back
    object_id = operations.send(data, [transport])
    print(f"✓ Sent object: {object_id}")
    
    # Create a new version
    version = client.version.create(CreateVersionInput(
        projectId=PROJECT_ID,
        modelId=MODEL_ID,
        objectId=object_id,
        message=f"Deleted object {TARGET_APPLICATION_ID}"
    ))
    
    print(f"✓ Created version: {version.id}")


if __name__ == "__main__":
    main()
