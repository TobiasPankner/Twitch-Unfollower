import requests
import re


def main():
    necessary_headers = [
        "Authorization",
        "Client-Id",
        "Client-Integrity",
        "X-Device-Id",
        "Content-Type",
    ]
    necessary_headers_lower = {h.lower(): h for h in necessary_headers}
    headers = {}
    try:
        with open("curl.txt", "r", encoding="utf-8") as file:
            file_content = file.read()

            found_headers = re.findall(r"-H\s+\'([^:]+):\s*([^\']+)\'", file_content)

            for key, value in found_headers:
                key_lower = key.strip().lower()
                value = value.strip()

                if key_lower in necessary_headers_lower:
                    correct_case_key = necessary_headers_lower[key_lower]

                    headers[correct_case_key] = value

    except FileNotFoundError:
        print(
            "Error: curl.txt not found. Please create it and paste the curl command inside."
        )
        exit(1)
    except Exception as e:
        print("Failed to read or parse curl.txt.")
        print(f"Error: {e}")
        exit(1)

    missing_headers = [h for h in necessary_headers if h not in headers]
    if missing_headers:
        print(f"Found headers: {list(headers.keys())}")
        print(f"Missing required headers in curl.txt: {missing_headers}")
        print(
            "Please ensure the curl command in curl.txt includes lines like -H 'Header-Name: Value' for all required headers."
        )
        exit(1)

    done = False
    while not done:
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
        channels_resp = requests.post(
            "https://gql.twitch.tv/gql", headers=headers, json=get_channels_payload
        )
        if channels_resp.status_code != 200:
            print("Error getting followed channels")
            print(channels_resp.status_code)
            print(channels_resp.text)
            exit(1)

        channels_json_resp = channels_resp.json()
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

        if len(channel_ids) == 0:
            print("No more channels to unfollow.")
            done = True
            continue

        print(f"Found {len(channel_ids)} channels in this batch.")

        for channel_id in channel_ids:
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

            resp = requests.post(
                "https://gql.twitch.tv/gql", headers=headers, json=unfollow_payload
            )
            if resp.status_code != 200:
                print(f"Error unfollowing: {channel_id}")
                print(resp.status_code)
                print(resp.text)
                continue

            try:
                json_resp = resp.json()
                if json_resp[0]["data"]["unfollowUser"]["follow"] is None:
                    print(f"Already unfollowed or error: {channel_id}")
                else:
                    display_name = json_resp[0]["data"]["unfollowUser"]["follow"][
                        "user"
                    ]["displayName"]
                    print(f"Unfollowed: {display_name} (ID: {channel_id})")
            except (IndexError, KeyError, TypeError) as e:
                print(f"Error parsing unfollow response for channel {channel_id}.")
                print(f"Error: {e}")
                print("Response JSON:", resp.text)
                continue

    print("Unfollowing process completed.")


if __name__ == "__main__":
    main()
