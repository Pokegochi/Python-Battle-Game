import requests
import time
import random
import os
import subprocess
import re

# Telegram Bot Configuration
TOKEN = ''  # You can input Token
CHAT_ID = ''  # You can input Chat id
TELEGRAM_URL = f"https://api.telegram.org/bot{TOKEN}/"
collection_address = ""
token_address = ""
shyft_api = ""

def send_message(text, winner_wallet, tx_id):
    """Sends a message to the specified Telegram chat with formatted links."""
    winner_link = f"https://solscan.io/account/{winner_wallet}"
    tx_link = f"https://solscan.io/tx/{tx_id}"

    formatted_message = f"{text}\n<b>Much proof:</b> <a href='{winner_link}'>{winner_wallet}</a>\n<b>Transaction:</b> <a href='{tx_link}'>{tx_id}</a>"

    url = TELEGRAM_URL + "sendAnimation"
    payload = {
        'chat_id': CHAT_ID,
        'animation': 'https://aquamarine-used-falcon-887.mypinata.cloud/ipfs/QmbEphBAMPHojmpDy9hGuzcWN6ykhqDjGd9ro1YZZL72GM',
        'caption': formatted_message,
        'parse_mode': 'HTML'
    }
    requests.post(url, data=payload)

def execute_command(command):
    """Executes a command and returns its output."""
    result = subprocess.run(command, shell=True, text=True, capture_output=True)
    return result.stdout, result.stderr

def find_transaction_signature(output):
    """Finds and returns the transaction signature from the command output."""
    match = re.search(r'Signature: (\S+)', output)
    return match.group(1) if match else None

def get_nft_holders(api_key, base_url):
    """Fetches the NFT holder data from the API."""
    owner_nft_count = {}
    page = 1
    max_pages = None

    while True:
        url = f"{base_url}&page={page}"
        headers = {'x-api-key': api_key}
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            data = response.json()
            if max_pages is None:
                max_pages = data.get("result", {}).get("total_pages", 0)

            nfts = data.get("result", {}).get("nfts", [])
            for nft in nfts:
                owner = nft.get("owner")
                if owner:
                    owner_nft_count[owner] = owner_nft_count.get(owner, 0) + 1

            if page >= max_pages:
                break
            page += 1
        else:
            print('Error:', response.status_code, response.text)
            break

    return owner_nft_count

def get_current_reward(block_number):
    """Calculates the current mining reward based on block number."""
    halvings = block_number // 4200
    return 10000

def select_winner(owner_nft_count):
    """Randomly selects a winner based on the number of NFTs they hold."""
    total_entries = sum(owner_nft_count.values())
    winner_ticket = random.randint(1, total_entries)
    current_ticket = 0
    for owner, count in owner_nft_count.items():
        current_ticket += count
        if current_ticket >= winner_ticket:
            return owner, count
    return None, 0

def main():
    api_key = shyft_api
    shyft_url = f"https://api.shyft.to/sol/v1/collections/get_nfts?network=mainnet-beta&collection_address={collection_address}&size=50" # Added correct collection
    block_number = 0

    while True:
        owner_nft_count = get_nft_holders(api_key, shyft_url)

        if owner_nft_count:
            current_reward = get_current_reward(block_number)
            winner, winner_tickets = select_winner(owner_nft_count)
            total_tickets = sum(owner_nft_count.values())

            if winner:
                winner_tickets = winner_tickets
                total_tickets = total_tickets
                message = f"<b>🎁 Wow! Reward Number {block_number} Much Found!</b>\n\n<b>Shibes Digging:</b> {total_tickets}\n<b>Reward:</b> {current_reward} $SOLGE\n<b>Team Size:</b> {winner_tickets} Shibes\n\n<a href='https://mine.doge-sol.io'> ⛏️ Much Mining! Such Start!</a>"

                command = f"spl-token transfer {token_address} {current_reward} {winner} --allow-unfunded-recipient --fund-recipient"

                for _ in range(3):  # Retry up to 3 times
                    stdout, stderr = execute_command(command)
                    if "Error" in stderr:
                        print("Error occurred:", stderr)
                        time.sleep(1)  # Wait before retrying
                    else:
                        signature = find_transaction_signature(stdout)
                        if signature:
                            print("Transaction Signature:", signature)
                            send_message(message, winner, signature)
                            break  # Break the loop if transaction signature is found
                        else:
                            print("Transaction Signature not found, retrying...")
                            time.sleep(1)

            block_number += 1

if _name_ == "_main_":
    main()