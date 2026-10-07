# Bot de Arbitraje Automatizado - Dólar MEP (ArQuants SDK)

Este repositorio contiene un **Bot de Trading Algorítmico institucional** desarrollado en Python para la operatoria y ejecución simulada (*Paper Trading*) de **Dólar MEP**, utilizando la arquitectura orientada a eventos del SDK de **ArQuants**.

El proyecto aplica los estándares técnicos y de gestión de riesgos requeridos en las mesas de dinero y ALyCs del mercado financiero argentino (Matba Rofex / BYMA).

## 📊 Lógica Financiera de la Estrategia

El algoritmo monitorea constantemente la información del libro de órdenes (*Market Data*) de forma asincrónica e interactiva para calcular el tipo de cambio implícito entre un activo que cotiza en Pesos (ARS) y su versión en Dólares (USD).

### 🧮 Fórmula Cuantitativa
El Tipo de Cambio (TC) implícito se calcula cruzando las puntas del libro (*Top of Book - TOB*):

\[\text{TC Implícito} = \frac{\text{Precio de Venta en Pesos (OFFER px ARS)}}{\text{Precio de Compra en Dólares (BID px USD)}}\]

Si el TC Implícito < Umbral Máximo Configurado, el bot identifica una oportunidad de arbitraje y procede a calcular el tamaño ejecutable analizando la profundidad de ambas puntas:

\[\text{Size Ejecutable} = \min(\text{Size OFFER ARS}, \text{Size BID USD}, \text{Límite Parametrizado})\]

## 🛠️ Arquitectura y Características Técnicas

* **Estructura Orientada a Eventos (*Interrupt-Driven*):** El bot no realiza *polling* de datos. Utiliza el método `next()` del framework para reaccionar inmediatamente ante cada actualización del libro de órdenes enviado por el mercado.
* **Mitigación y Control de Riesgos (Circuit Breaker):** Implementación de la función `notify_order()` para rastrear los estados de ejecución de las órdenes. Ante un rechazo de orden de mercado o cancelación inesperada, el bot ejecuta un método `on_pause()` automático para evitar descalces de inventario o desarbitrajes perjudiciales.
* **Configuración Dinámica Externa:** Los parámetros operativos (tickers como AL30/AL30D, límites de nominales y umbrales de precios) están desacoplados del código fuente mediante archivos JSON (`config/settings.json`), permitiendo modificaciones en caliente desde la terminal de la mesa de dinero.
* **Cumplimiento de Seguridad Financiera:** Inclusión de políticas estrictas de exclusión en `.gitignore` para garantizar que las credenciales de los entornos de simulación o producción jamás se expongan en repositorios públicos.

## 📂 Estructura del Proyecto

```text
mep-trading-bot-arquants/
│
├── .gitignore               # Exclusión de entornos virtuales y credenciales locales
├── README.md                # Documentación técnica e institucional del proyecto
├── requirements.txt         # Gestión de dependencias y librerías del proyecto
│
├── config/
│   └── settings.json        # Parámetros operativos y umbrales de riesgo del bot
│
└── src/
    ├── main.py              # Punto de entrada y conexión al cliente de mercado
    └── strategy.py          # Lógica algorítmica y control del ciclo de vida de órdenes
```

## 🚀 Instalación y Despliegue

1. Clonar este repositorio:
   ```bash
   git clone https://github.com
   cd mep-trading-bot-arquants
   ```

2. Instalar las dependencias del ecosistema cuantitativo:
   ```bash
   pip install -r requirements.txt
   ```

3. Configurar los parámetros en `config/settings.json` y ejecutar el bot:
   ```bash
   python src/main.py
   ```

---
*Desarrollado como proyecto de aplicación avanzada en Trading Algorítmico utilizando el ecosistema tecnológico de ArQuants.*
