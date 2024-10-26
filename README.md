This bot is designed to interact with the HANA NETWORK on the Base network. It facilitates the deposit of a specified amount of ETH to a smart contract by executing multiple transactions.

## Features

- Connects to the Base network.
- Executes a specified number of deposit transactions.
- Monitors and reports transaction status.
- Handles transaction fees and wallet balance checks.
- Retries failed transactions (if implemented).

## Prerequisites

Before you run this bot, ensure you have the following:

```shell
git clone https://github.com/erwindobp98/hn.git
cd hn
```
Edit private_key,address,amount_in_eth,transaction_count di File bot.py
```shell
nano bot.py
```
Install
```shell
pip install web3
```
Run
```shell
python bot.py
```
