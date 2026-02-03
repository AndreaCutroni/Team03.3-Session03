"""
05 - Import a Model into an Existing Model
"""

from main import get_client
from specklepy.transports.server import ServerTransport
from specklepy.api import operations
from specklepy.core.api.inputs.version_inputs import CreateVersionInput


SOURCE_PROJECT_ID = "128262a20c" #CW26-Sessions
SOURCE_MODEL_ID = "a1014e4b32" # Session02/ref-geo
TARGET_PROJECT_ID = "128262a20c"
TARGET_MODEL_ID = "9ec0d0a2a2" # Replace with the model ID you created in 01_create_model.py


def main():
    client = get_client()

    # Get latest version of source model
    source_version = client.version.get_versions(SOURCE_MODEL_ID, SOURCE_PROJECT_ID, limit=1)
    if not source_version.items:
        print("No versions found for source model.")
        return
    
    latest_version = source_version.items[0]
    print(f"✓ Fetching source model version: {latest_version.id}")

    ref_obj = getattr(latest_version, 'referenced_object', None) or getattr(latest_version, "referencedObject", None)
    
    # Receive the full data tree from source model
    source_transport = ServerTransport(client=client, stream_id=SOURCE_PROJECT_ID)
    target_transport = ServerTransport(client=client, stream_id=TARGET_PROJECT_ID)

    obj = operations.receive(ref_obj, source_transport)

    # Push to target
    object_id = operations.send(obj, [target_transport])

     # 🔹 Create version using API helper
    version = client.version.create(CreateVersionInput(
        projectId=TARGET_PROJECT_ID,
        modelId=TARGET_MODEL_ID,
        objectId=object_id,
        message="Model copied from homework/session02/_ref-geo"
    ))

    print(f"OK Model copied successfully! Version ID: {version.id}")


if __name__ == "__main__":
    main()
