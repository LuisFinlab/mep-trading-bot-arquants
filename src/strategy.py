import logging
from arquants import Strategy, Order

# Configuración de logging profesional para auditoría de la mesa de dinero
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class MepArbitrageStrategy(Strategy):
    """
    Estrategia de Arbitraje Automatizado para Compra/Venta de Dólar MEP.
    Diseñada para entornos de ejecución e interactuando con Market Data en tiempo real.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Parámetros parametrizables desde la plataforma
        self.target_instrument_ars = "AL30"
        self.target_instrument_usd = "AL30D"
        self.max_tc_threshold = 1350.0  # Umbral objetivo de Tipo de Cambio
        self.order_size_limit = 1000  # Límite máximo de nominales por orden

        # Estado interno del bot para control de riesgos y descalces
        self.active_order_ars = None
        self.active_order_usd = None
        self.is_paused = False

    def validate(self):
        """
        Validación previa al inicio de la estrategia.
        Evita ejecuciones erróneas si faltan parámetros críticos.
        """
        logger.info("Validando configuración de la estrategia...")
        if not self.target_instrument_ars or not self.target_instrument_usd:
            logger.error("Error: Instrumentos base no definidos.")
            return False
        return True

    def next(self, market_data):
        """
        Ciclo principal de ejecución (Interrupt-Driven).
        Se ejecuta de forma asincrónica ante cada actualización de Market Data.
        """
        if self.is_paused:
            return

        # 1. Extracción de Market Data en tiempo real para ambos instrumentos
        md_ars = market_data.get(self.target_instrument_ars)
        md_usd = market_data.get(self.target_instrument_usd)

        if not md_ars or not md_usd:
            return  # Esperar a tener datos completos de ambas puntas

        # 2. Captura de mejores precios del libro (Top of Book - TOB)
        best_offer_ars = md_ars.best_offer.price
        best_bid_usd = md_usd.best_bid.price

        size_offer_ars = md_ars.best_offer.size
        size_bid_usd = md_usd.best_bid.size

        if best_offer_ars == 0 or best_bid_usd == 0:
            return

        # 3. Cálculo matemático del Tipo de Cambio implícito
        implied_tc = best_offer_ars / best_bid_usd

        # 4. Evaluación de la oportunidad de arbitraje frente al umbral
        if implied_tc < self.max_tc_threshold:
            logger.info(f"Oportunidad detectada. TC Implícito: {implied_tc:.2f} < Umbral: {self.max_tc_threshold}")

            # Control de riesgos: Tomar el tamaño más chico disponible en el libro para mitigar desarbitrajes
            executable_size = min(size_offer_ars, size_bid_usd, self.order_size_limit)

            if executable_size > 0 and not self.active_order_ars and not self.active_order_usd:
                self.execute_mep_trade(executable_size, best_offer_ars, best_bid_usd)

    def execute_mep_trade(self, size, price_ars, price_usd):
        """
        Envío simultáneo o secuencial de órdenes al mercado.
        """
        logger.info(f"Enviando órdenes al mercado. Tamaño: {size} nominales.")

        # Enviar orden de compra en Pesos (Operatoria Directa/Agresiva)
        self.active_order_ars = self.buy(
            instrument=self.target_instrument_ars,
            price=price_ars,
            size=size,
            type=Order.TYPE_LIMIT
        )

        # Enviar orden de venta en Dólares
        self.active_order_usd = self.sell(
            instrument=self.target_instrument_usd,
            price=price_usd,
            size=size,
            type=Order.TYPE_LIMIT
        )

    def notify_order(self, order):
        """
        Callback del ciclo de vida de las órdenes.
        Esencial para la gestión de riesgos en la mesa y control de descalces.
        """
        logger.info(f"Notificación de orden recibida: ID {order.id} - Estado: {order.status}")

        if order.status == Order.STATUS_FILLED:
            if order.id == self.active_order_ars.id:
                logger.info("Pata en Pesos ejecutada por completo.")
                self.active_order_ars = None
            elif order.id == self.active_order_usd.id:
                logger.info("Pata en Dólares ejecutada por completo. Arbitraje cerrado exitosamente.")
                self.active_order_usd = None

        elif order.status in [Order.STATUS_REJECTED, Order.STATUS_CANCELLED]:
            logger.warning(f"Alerta de riesgo: Orden {order.id} rechazada/cancelada. Evaluando descalce técnico.")
            # Lógica institucional: Frenar el bot ante fallos técnicos o de mercado
            self.on_pause()

    def on_pause(self):
        """Manejador para pausar la estrategia de manera segura (Circuit Breaker)."""
        logger.warning("Estrategia PAUSADA de forma preventiva.")
        self.is_paused = True

    def on_error(self, error_message):
        """Captura de excepciones de conectividad o protocolo de mercado."""
        logger.error(f"Error crítico en el framework de ejecución: {error_message}")
        self.on_pause()

    def process_parameter_change(self, parameter, new_value):
        """Permite modificar límites o umbrales en vivo desde la UI de la mesa de dinero."""
        logger.info(f"Modificación dinámica de parámetro: {parameter} -> {new_value}")
        if hasattr(self, parameter):
            setattr(self, parameter, new_value)
