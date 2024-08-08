import random
import requests
import logging
import argparse
import time
from typing import List, Optional, Dict, Any

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s :: %(levelname)s :: %(message)s')
logger = logging.getLogger(__name__)


def arg_parser():
    parser = argparse.ArgumentParser(description="Create random Pokemon orders.")
    parser.add_argument('--num_orders', type=int, required=True, help='Number of orders to create')
    parser.add_argument('--delay', type=float, required=True, help='Delay between requests in seconds')
    parser.add_argument('--user_id', type=int, required=True, help='User ID for the orders')

    return parser.parse_args()

def read_countries(filename: str) -> List[str]:
    logger.info(f"Reading countries from file: {filename}")
    try:
        with open(filename, 'r') as file:
            return [line.strip() for line in file.readlines()]
    except FileNotFoundError:
        logger.error(f"File not found: {filename}")
        return []


def get_random_pokemon() -> Optional[str]:
    pokemon_id = random.randint(1, 1015)
    logger.info(f"Selected Pokemon ID: {pokemon_id}")
    try:
        response = requests.get(
            f"https://pokeapi.co/api/v2/pokemon/{pokemon_id}", timeout=1
        )
        response.raise_for_status()
        pokemon_name = response.json()["name"]
        logger.info(f"Pokemon Name: {pokemon_name}")
        return pokemon_name
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching Pokemon: {e}")
        return None


def create_order(user_id: int, pokemon: str, country: str, price: int) -> Dict[str, Any]:
    url = 'http://localhost:8000/orders/'
    headers = {
        'accept': 'application/json',
        'Content-Type': 'application/json'
    }
    payload = {
        'user_id': user_id,
        'pokemon': pokemon,
        'country': country,
        'price': price
    }

    response = requests.post(url, headers=headers, json=payload)

    return response.json()



def main():

    args = arg_parser()

    countries = read_countries('countries.txt')

    if not countries:
        logger.error("No countries available to select from. Exiting.")
        return

    for _ in range(args.num_orders):
        logger.info("Generating random Pokemon order...")
        pokemon = get_random_pokemon()
        if not pokemon:
            logger.error("Failed to get Pokemon. Skipping order creation.")
            continue

        country = random.choice(countries)
        price = random.randint(0, 300)

        order_response = create_order(user_id=args.user_id,
                                      pokemon=pokemon,
                                      country=country,
                                      price=price)
        logger.info(f"Order response: {order_response}")

        time.sleep(args.delay)


if __name__ == '__main__':
    main()
