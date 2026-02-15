"""
GQL Subscriptions with Speckle and Exporting Data to JSON when Updates Occur

This script demonstrates how to subscribe to real-time updates from a Speckle project ("project_id")
using GraphQL subscriptions and save the received data to a JSON file whenever an update occurs 
to have a backup of the latest data.
"""

import asyncio
import json
import os
from datetime import datetime
from gql import gql, Client
from gql.transport.websockets import WebsocketsTransport
from main import get_client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Your Speckle token
YOUR_TOKEN =  os.environ.get("SPECKLE_TOKEN")
PROJECT_ID = "128262a20c"
OBJECT_ID = "69a045a60359a4ff588faeb018e14f60"


def query_object_data_graphql(client, project_id: str, object_id: str) -> dict:
    """
    Query object data from Speckle using GraphQL API.
    
    Args:
        client: Authenticated SpeckleClient instance
        project_id: The Speckle project ID
        object_id: The Speckle object ID
    
    Returns:
        Dictionary containing the query result
    """
    query = gql("""
    query GetObjectDataJSON($objectId: String!, $projectId: String!) {
        project(id: $projectId) {
            object(id: $objectId) {
                id
                speckleType
                data
            }
        }
    }
    """)
    
    variables = {
        "projectId": project_id,
        "objectId": object_id
    }
    
    # Execute GraphQL query using the client's HTTP session
    result = client.httpclient.execute(query, variable_values=variables)
    return result

def save_object_data_to_json(PROJECT_ID: str, OBJECT_ID: str, data: dict, timestamp: str = None):
    
    output = {
        "projectId": PROJECT_ID,
        "objectId": OBJECT_ID,
        "timestamp": timestamp or datetime.now().isoformat(),
        "data": data
    }

    # Save to JSON file in the same directory as this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    timestamp_str = timestamp.replace(":", "-") if timestamp else datetime.now().strftime("%Y-%m-%dT%H-%M-%S")
    output_file = os.path.join(script_dir, f"object_data_{timestamp_str}.json")
    
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, default=str)
    
    print(f"✓ Saved object data to {output_file}")


# Define the subscription query
subscription_query = gql("""
    subscription ProjectVersionsUpdated($projectId: String!) {
        projectVersionsUpdated(id: $projectId) {
            id
            modelId
            type
            version {
                id
                message
                createdAt
            }
        }
    }
""")

async def subscribe_and_export():
    """
    Subscribe to project version updates using WebSocket and save each update to a JSON file
    """
    # Create a SpeckleClient instance for GraphQL HTTP queries
    http_client = get_client()
    
    # Create WebSocket transport with authentication
    transport = WebsocketsTransport(
        url="wss://app.speckle.systems/graphql",
        init_payload={
            "Authorization": f"Bearer {YOUR_TOKEN}"
        }
    )
    
    # Create a GraphQL client
    client = Client(
        transport=transport,
        fetch_schema_from_transport=False,
    )
    
    try:
        async with client as session:
            print(f"🔌 Connected to Speckle WebSocket")
            print(f"📡 Listening for updates on project: {PROJECT_ID}")
            print("Press Ctrl+C to stop\n")
            
            try:
                # Subscribe to the query
                async for result in session.subscribe(
                    subscription_query,
                    variable_values={"projectId": PROJECT_ID}
                ):
                    print("=" * 50)
                    print("📦 New Update Received!")
                    print("=" * 50)
                    
                    data = result.get("projectVersionsUpdated")
                    if data:
                        print(f"ID: {data.get('id')}")
                        print(f"Model ID: {data.get('modelId')}")
                        print(f"Type: {data.get('type')}")
                        
                        version = data.get('version')
                        if version:
                            print(f"\nVersion Details:")
                            print(f"  - Version ID: {version.get('id')}")
                            print(f"  - Message: {version.get('message')}")
                            print(f"  - Created At: {version.get('createdAt')}")
                        
                        print("\n")

                        # Query object data using GraphQL
                        try:
                            graphql_result = query_object_data_graphql(http_client, PROJECT_ID, OBJECT_ID)
                            print(f"✓ GraphQL query executed successfully")
                            
                            # Save the received data to JSON file
                            object_data = graphql_result["project"]["object"]["data"]
                            timestamp = version.get('createdAt') if version else None
                            save_object_data_to_json(PROJECT_ID, OBJECT_ID, object_data, timestamp)

                        except Exception as e:
                            print(f"⚠ Failed to query or save object data: {e}")

                        print("\n")
                    
            except asyncio.CancelledError:
                print("\n\n👋 Subscription cancelled")
                raise
            except KeyboardInterrupt:
                print("\n\n👋 Subscription stopped by user")
                raise
            
    except (KeyboardInterrupt, asyncio.CancelledError):
        pass
    except Exception as e:
        print(f"\n❌ Error: {e}")
    finally:
        # Ensure transport is properly closed
        await transport.close()
        print("🔌 Connection closed properly")

if __name__ == "__main__":
    # Run the subscription and export function
    asyncio.run(subscribe_and_export())