# Twitch-Unfollower

[![GitHub stars](https://img.shields.io/github/stars/TobiasPankner/Twitch-Unfollower.svg?style=social&label=Star)](https://GitHub.com/TobiasPankner/Twitch-Unfollower/stargazers/)
[![Donate](https://img.shields.io/badge/Donate-PayPal-green.svg)](https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=3TU2XDBK2JFU4&source=url)

- [Prerequisites](#prerequisites)
- [Getting your twitch authorization](#getting-your-twitch-authorization)
- [Run the script](#run-the-script)

Python script to mass unfollow twitch channels.  
Since websites that used to do the same don't work anymore, I created this simple Web Automation program to quickly unfollow alot of channels.

## Prerequisites

- Python3 ([Download](https://www.python.org/downloads/))

## Getting your twitch authorization

**Treat these headers like your password!**

1. Log into your Twitch account
2. Open Chrome dev tools (F12) -> Network tab
3. Refresh the page (F5)
4. Find a request to `https://gql.twitch.tv/gql` in the list.
5. Right-click on the request -> Copy -> Copy as cURL (bash)

![demo](https://github.com/user-attachments/assets/54c8adbd-d1cf-4d19-8402-7802a6323d23)


## Run the script

1. Install dependencies: `pip install -r requirements.txt`
2. [Get your twitch authorization](#getting-your-twitch-authorization) by copying the request as cURL (bash).
3. Create a file called "curl.txt" in the same directory as the script.
4. Paste the copied cURL command into `curl.txt`.
5. Run [unfollower.py](unfollower.py): `python unfollower.py`
