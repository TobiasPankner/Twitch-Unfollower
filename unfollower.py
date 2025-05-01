import requests
import re  # Import the regular expression module


def main():
    # List of headers required for Twitch GQL API calls
    necessary_headers = [
        "Authorization",
        "Client-Id",
        "Client-Integrity",
        "X-Device-Id",
        "Content-Type",
    ]
    # Create a lowercase mapping for necessary headers for case-insensitive lookup
    necessary_headers_lower = {h.lower(): h for h in necessary_headers}
    headers = {}
    try:
        with open("headers.txt", "r", encoding="utf-8") as file:
            file_content = file.read()

            # Regex to find header lines in the format -H ^"Header-Name: Value^" (copied from Windows cmd)
            # It captures the key (group 1) and value (group 2)
            found_headers = re.findall(r"-H\s+\^\"([^:]+):\s*([^^]+)\^\"", file_content)

            # Process the found headers
            for key, value in found_headers:
                key_lower = key.strip().lower()  # Use lowercase key for matching
                value = value.strip()

                # Check if the lowercase key is one of the necessary headers
                if key_lower in necessary_headers_lower:
                    # Get the correctly capitalized header name for the requests library
                    correct_case_key = necessary_headers_lower[key_lower]
                    print(
                        f"  [Debug] Adding header: {correct_case_key}"
                    )  # Debug output
                    headers[correct_case_key] = value
                # else: # Optional: Uncomment to see skipped headers
                # print(f"  [Debug] Skipping header: {key.strip()}")

    except FileNotFoundError:
        print(
            "Error: headers.txt not found. Please create it and paste the curl command inside."
        )
        exit(1)
    except Exception as e:
        print("Failed to read or parse headers.txt.")
        print(f"Error: {e}")
        exit(1)

    print("--- [Debug] Final Headers Dictionary ---")
    print(headers)
    print("--------------------------------------")

    # Verify that all necessary headers were successfully extracted
    missing_headers = [h for h in necessary_headers if h not in headers]
    if missing_headers:
        print(f"Found headers: {list(headers.keys())}")
        print(f"Missing required headers in headers.txt: {missing_headers}")
        print(
            f'Please ensure the curl command in headers.txt includes lines like -H ^"Header-Name: Value^" for all required headers.'
        )
        exit(1)

    # Main loop to fetch followed channels and unfollow them
    done = False
    while not done:
        # Payload to fetch the list of followed channels
        get_channels_payload = [
            {
                "operationName": "ChannelFollows",
                "variables": {"limit": 100, "order": "DESC"},
                "extensions": {
                    "persistedQuery": {
                        "version": 1,
                        "sha256Hash": "eecf815273d3d949e5cf0085cc5084cd8a1b5b7b6f7990cf43cb0beadf546907",
                    }
                },
            }
        ]
        # Make the API call to get followed channels
        channels_resp = requests.post(
            "https://gql.twitch.tv/gql", headers=headers, json=get_channels_payload
        )
        if channels_resp.status_code != 200:
            print("Error getting followed channels")
            print(channels_resp.status_code)
            print(channels_resp.text)
            exit(1)

        channels_json_resp = channels_resp.json()
        # Extract channel IDs from the response
        try:
            channel_ids = set(
                [
                    c["node"]["id"]
                    for c in channels_json_resp[0]["data"]["user"]["follows"]["edges"]
                ]
            )
        except (IndexError, KeyError, TypeError) as e:
            print("Error parsing followed channels response.")
            print(f"Error: {e}")
            print("Response JSON:", channels_json_resp)
            exit(1)

        # If no more channels are found, exit the loop
        if len(channel_ids) == 0:
            print("No more channels to unfollow.")
            done = True
            continue

        print(f"Found {len(channel_ids)} channels in this batch.")

        # Iterate through the fetched channel IDs and unfollow each one
        for channel_id in channel_ids:
            # Payload to unfollow a specific user by ID
            unfollow_payload = [
                {
                    "operationName": "FollowButton_UnfollowUser",
                    "variables": {"input": {"targetID": channel_id}},
                    "extensions": {
                        "persistedQuery": {
                            "version": 1,
                            "sha256Hash": "f7dae976ebf41c755ae2d758546bfd176b4eeb856656098bb40e0a672ca0d880",
                        }
                    },
                }
            ]

            # Make the API call to unfollow the user
            resp = requests.post(
                "https://gql.twitch.tv/gql", headers=headers, json=unfollow_payload
            )
            if resp.status_code != 200:
                print(f"Error unfollowing: {channel_id}")
                print(resp.status_code)
                print(resp.text)
                # Continue to the next channel instead of exiting?
                # Consider adding a delay here if rate limited
                continue  # Continue to next channel on error

            # Parse the unfollow response
            try:
                json_resp = resp.json()
                # Check the response structure to confirm unfollow
                if json_resp[0]["data"]["unfollowUser"]["follow"] is None:
                    print(f"Already unfollowed or error: {channel_id}")
                else:
                    # Successfully unfollowed, print display name
                    display_name = json_resp[0]["data"]["unfollowUser"]["follow"][
                        "user"
                    ]["displayName"]
                    print(f"Unfollowed: {display_name} (ID: {channel_id})")
            except (IndexError, KeyError, TypeError) as e:
                print(f"Error parsing unfollow response for channel {channel_id}.")
                print(f"Error: {e}")
                print(
                    "Response JSON:", resp.text
                )  # Print raw text as it might not be JSON on error
                continue  # Continue to next channel

    print("Unfollowing process completed.")


if __name__ == "__main__":
    main()
