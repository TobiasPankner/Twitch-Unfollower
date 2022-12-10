import requests


def main():
    necessary_headers = ['Authorization', 'Client-Id', 'Client-Integrity', 'X-Device-Id', 'Content-Type']
    try:
        with open('headers.txt', 'r') as file:
            headers = dict(
                [(h.split(':', 1)[0], h.split(':', 1)[1].strip()) for h in file.read().split('\n')[1:] if
                 len(h) > 1 and h.split(':', 1)[0] in necessary_headers])
    except:
        print("Failed to read headers.txt, have you created the file?")
        exit(1)

    done = False
    while not done:
        get_channels_payload = [
            {
                "operationName": "ChannelFollows",
                "variables": {
                    "limit": 100,
                    "order": "DESC"
                },
                "extensions": {
                    "persistedQuery": {
                        "version": 1,
                        "sha256Hash": "eecf815273d3d949e5cf0085cc5084cd8a1b5b7b6f7990cf43cb0beadf546907"
                    }
                }
            }
        ]
        channels_resp = requests.post('https://gql.twitch.tv/gql', headers=headers, json=get_channels_payload)
        if channels_resp.status_code != 200:
            print("Error getting followed channels")
            exit(1)

        channels_json_resp = channels_resp.json()
        channel_ids = set([c['node']['id'] for c in channels_json_resp[0]['data']['user']['follows']['edges']])
        if len(channel_ids) == 0:
            done = True
            continue

        for channel_id in channel_ids:
            unfollow_payload = [
                {
                    "operationName": "FollowButton_UnfollowUser",
                    "variables": {
                        "input": {
                            "targetID": channel_id
                        }
                    },
                    "extensions": {
                        "persistedQuery": {
                            "version": 1,
                            "sha256Hash": "f7dae976ebf41c755ae2d758546bfd176b4eeb856656098bb40e0a672ca0d880"
                        }
                    }
                }
            ]

            resp = requests.post('https://gql.twitch.tv/gql', headers=headers, json=unfollow_payload)
            if resp.status_code != 200:
                print(f"Error unfollowing: {channel_id}")
                return None

            json_resp = resp.json()

            if json_resp[0]['data']['unfollowUser']['follow'] is None:
                print(f"Already unfollowed: {channel_id}")
            else:
                print(f"Unfollowed: {json_resp[0]['data']['unfollowUser']['follow']['user']['displayName']}")


if __name__ == '__main__':
    main()
