def main():
    print("Hello from team03-3-session03!")


if __name__ == "__main__":
    main()
# my token is bc050b1dff53a2b4b667674ad5b2e7239b7318c4c3
from speckle.api.client import SpeckleClient

client = SpeckleClient(hosts="api.speckle.systems")

token = "bc050b1dff53a2b4b667674ad5b2e7239b7318c4c3"
client.authenticate_with_token(token)

print (f" Authenticated as {client.account.userInfo.name}")