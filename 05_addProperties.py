"""
05 - Add Properties to Objects in a Speckle Model

This script demonstrates how to receive objects from Speckle,
add custom properties, and send them back as a new version.

Use this model: https://app.speckle.systems/projects/YOUR_PROJECT_ID/models/YOUR_MODEL_ID
"""

from main import get_client
from specklepy.transports.server import ServerTransport
from specklepy.api import operations
from specklepy.objects.base import Base
from specklepy.core.api.inputs.version_inputs import CreateVersionInput

# TODO: Replace with your project, model, and version IDs
PROJECT_ID = "128262a20c"
MODEL_ID = "9ec0d0a2a2"


def main():
    # Authenticate
    client = get_client()

    # Get the latest version
    latest_version = client.version.get_versions(MODEL_ID, PROJECT_ID, limit=1).items[0]
    print(f"✓ Fetching version: {latest_version.id}")

    # Receive the data
    transport = ServerTransport(client=client, stream_id=PROJECT_ID)
    data = operations.receive(latest_version.referenced_object, transport)

    # Add root level properties
    data["custom_property"] = "Team03.3"
    data["analysis_date"] = "2026-02-03"
    data["processed_by"] = "Andrea Cutroni"

    # Find "Old modules" collection (search recursively)
    def find_collection(obj, name):
        elements = getattr(obj, "@elements", None) or getattr(obj, "elements", [])
        for el in elements or []:
            if getattr(el, "name", None) == name:
                return el
        found = find_collection(el, name)
        if found:
                return found
        return None


    old_modules = find_collection(data, "Layer 01")

    # Modify Designer names
    new_designers = ["Andrea Cutroni", "Eva Vasileska"]

    if old_modules:
        # Change collection name
        old_modules.name = "Old Modules"
        old_elements = getattr(old_modules, "@elements", None) or getattr(
            old_modules, "elements", []
    )
        for element, designer in zip(old_elements, new_designers):
            if isinstance(element, Base) and "properties" in element.get_member_names():
                element["properties"]["Designer"] = designer
    print(f"✓ Updated Designer names in 'Old modules' collection.")

    new_modules = find_collection(data, "Object_Copy")

    # Modify Designer names
    designers = ["Andrea Cutroni"]

    if new_modules:
        # Change collection name
        new_modules.name = "New Modules"
        new_elements = getattr(new_modules, "@elements", None) or getattr(
            new_modules, "elements", []
    )
        for element, designer in zip(new_elements, designers):
            if isinstance(element, Base) and "properties" in element.get_member_names():
                element["properties"]["Designer"] = designer
    print(f"✓ Updated Designer names in 'New modules' collection.")
    
    
    # Send the modified data back to Speckle
    object_id = operations.send(data, [transport])
    print(f"✓ Sent object: {object_id}")

    # Create a new version with the modified data
    from specklepy.core.api.inputs.version_inputs import CreateVersionInput

    version = client.version.create(CreateVersionInput(
        projectId=PROJECT_ID,
        modelId=MODEL_ID,
        objectId=object_id,
        message="Added custom properties via specklepy2"
    ))

    print(f"✓ Created version: {version.id}")


if __name__ == "__main__":
    main()
