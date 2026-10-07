import json
import logging
from config import settings
from arquants import ArQuantsClient
from src.strategy import MepArbitrageStrategy

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def load_config():
    with open('config/settings.json', 'r') as f:
        return json.load(f)


def run():
    logger.info("Iniciando el ruteador del Bot de Dólar MEP...")
    config = load_config()

    # Inicialización del cliente institucional de ArQuants (usa credenciales simuladas)
    client = ArQuantsClient(environment=config["ENVIRONMENT"])

    # Instancia de la estrategia pasándole los parámetros del JSON
    params = config["STRATEGY_PARAMETERS"]
    strategy = MepArbitrageStrategy(
        target_instrument_ars=params["TARGET_INSTRUMENT_ARS"],
        target_instrument_usd=params["TARGET_INSTRUMENT_USD"],
        max_tc_threshold=params["MAX_TC_THRESHOLD"],
        order_size_limit=params["ORDER_SIZE_LIMIT"]
    )

    # Conectar la estrategia al cliente de mercado asincrónico
    client.register_strategy(strategy)
    client.start_execution()


if __name__ == "__main__":
    run()
