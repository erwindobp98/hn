import asyncio
import aiohttp
import time
from colorama import init, Fore, Style

init(autoreset=True)

def animated_print(text, color=Fore.WHITE, delay=0.05):
    """Simulate an animated print."""
    for char in text:
        print(color + char, end='', flush=True)
        time.sleep(delay)
    print()  # New line after animation

# Define the headers for requests
headers = {
    'Accept': '*/*',
    'Content-Type': 'application/json',
    'User-Agent': "Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1"
}

# Utility function for making API requests
async def colay(session, url, method, payload_data=None):
    """Handles HTTP requests with given method, URL, and payload."""
    async with session.request(method, url, headers=headers, json=payload_data) as response:
        if response.status != 200:
            raise Exception(f'HTTP error! Status: {response.status}')
        return await response.json()

async def refresh_access_token(session, refresh_token):
    """Refreshes the access token using a refresh token."""
    api_key = "AIzaSyDipzN0VRfTPnMGhQ5PSzO27Cxm3DohJGY"
    async with session.post(
        f'https://securetoken.googleapis.com/v1/token?key={api_key}',
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data=f'grant_type=refresh_token&refresh_token={refresh_token}'
    ) as response:
        if response.status != 200:
            response_text = await response.text()
            animated_print(f"Error details: {response_text}", color=Fore.RED, delay=0.05)
            if "INVALID_REFRESH_TOKEN" in response_text:
                animated_print("The refresh token is invalid. Please provide a valid one.", color=Fore.RED, delay=0.05)
            raise Exception("Failed to refresh access token")
        data = await response.json()
        return data.get('access_token')

async def handle_grow_and_garden(session, refresh_token, api_url):
    """Handles the grow and garden actions."""
    new_access_token = await refresh_access_token(session, refresh_token)
    headers['authorization'] = f'Bearer {new_access_token}'

    info_query = {
        "query": """
        query getCurrentUser {
            currentUser { id totalPoint depositCount }
            getGardenForCurrentUser { gardenStatus { growActionCount gardenRewardActionCount } }
        }""",
        "operationName": "getCurrentUser"
    }

    # Fetch account details
    info = await colay(session, api_url, 'POST', info_query)
    balance = info['data']['currentUser']['totalPoint']
    grow = info['data']['getGardenForCurrentUser']['gardenStatus']['growActionCount']
    garden = info['data']['getGardenForCurrentUser']['gardenStatus']['gardenRewardActionCount']

    animated_print(f"POINTS: {balance} | Grow left: {grow} | Garden left: {garden}", color=Fore.GREEN, delay=0.05)

    # Automatically perform grow actions
    for i in range(grow):
        animated_print(f"Performing grow action {i + 1}/{grow}...", color=Fore.CYAN, delay=0.05)
        reward = await execute_grow_action(session, api_url)
        if reward:
            balance += reward
            animated_print(f"Rewards from grow: {reward} | New Balance: {balance} | Grow left: {grow - (i + 1)}", color=Fore.GREEN, delay=0.05)
        else:
            animated_print(f"No reward from grow action {i + 1}.", color=Fore.YELLOW, delay=0.05)
        await asyncio.sleep(1)

    # Automatically perform garden actions if available
    while garden >= 10:
        animated_print(f"Performing garden reward actions...", color=Fore.CYAN, delay=0.05)
        await execute_garden_action(session, api_url, 10)
        garden -= 10
        await asyncio.sleep(1)

async def execute_grow_action(session, api_url):
    """Executes the grow action and returns the reward."""
    grow_action_query = {
        "query": """
        mutation executeGrowAction {
            executeGrowAction(withAll: false) { totalValue }
        }""",
        "operationName": "executeGrowAction"
    }

    try:
        response = await colay(session, api_url, 'POST', grow_action_query)
        reward = response['data']['executeGrowAction']['totalValue']
        return reward
    except Exception as e:
        animated_print(f"Error during grow action: {str(e)}", color=Fore.RED, delay=0.05)
        return 0

async def execute_garden_action(session, api_url, limit):
    """Executes the garden reward action for a given limit."""
    garden_action_query = {
        "query": """
        mutation executeGardenRewardAction($limit: Int!) {
            executeGardenRewardAction(limit: $limit) { data { cardId } }
        }""",
        "variables": {"limit": limit},
        "operationName": "executeGardenRewardAction"
    }

    try:
        response = await colay(session, api_url, 'POST', garden_action_query)
        card_ids = [item['cardId'] for item in response['data']['executeGardenRewardAction']['data']]
        animated_print(f"Opened Garden: {card_ids}", color=Fore.GREEN, delay=0.05)
    except Exception as e:
        animated_print(f"Error during garden action: {str(e)}", color=Fore.RED, delay=0.05)

async def main():
    """Main loop for processing accounts."""
    api_url = "https://hanafuda-backend-app-520478841386.us-central1.run.app/graphql"

    # Input multiple refresh tokens
    refresh_tokens = []
    while True:
        refresh_token = input("Enter a refresh token (or type 'done' to finish): ")
        if refresh_token.lower() == 'done':
            break
        refresh_tokens.append(refresh_token)

    async with aiohttp.ClientSession() as session:
        while True:
            for refresh_token in refresh_tokens:
                await handle_grow_and_garden(session, refresh_token, api_url)
            animated_print(f"All accounts processed. Cooling down for 2 minutes...", color=Fore.MAGENTA, delay=0.05)
            await asyncio.sleep(120)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        animated_print("\nStopped by user.", color=Fore.RED, delay=0.05)
    finally:
        animated_print("Thank you for using this service! 🥳", color=Fore.YELLOW, delay=0.05)

