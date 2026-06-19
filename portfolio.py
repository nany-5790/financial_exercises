from abc import ABC, abstractmethod
from decimal import Decimal


# ===========================================================
# LECCIÓN 1 — La clase abstracta base: FinancialInstrument
#
# En Bank of America hay decenas de tipos de instrumentos:
# Acciones (Equity), Bonos (Bond), Derivados (Derivative), etc.
# Todos comparten una "forma" común pero se valoran distinto.
#
# ABC = Abstract Base Class: define el CONTRATO que todos deben cumplir.
# Es como un contrato legal: si eres un FinancialInstrument,
# DEBES implementar estos métodos. Si no, Python lanza un error.
# ===========================================================


class FinancialInstrument(ABC):
    """Base contract for any financial instrument."""

    def __init__(self, instrument_id: str, currency: str):
        self.instrument_id = instrument_id
        self.currency = currency

    @abstractmethod
    def calculate_value(self, market_data: dict) -> Decimal:
        """How much is this instrument worth right now?

        market_data: precios actuales del mercado, ej:
            {"AAPL": 185.50, "BOND_001": 98.50}

        Cada instrumento implementa esto distinto:
        - Una accion multiplica cantidad x precio
        - Un bono calcula valor presente de flujos futuros
        """
        ...

    @abstractmethod
    def get_risk_factor(self) -> Decimal:
        """How risky is this instrument? (0.0 = safe, 1.0 = full risk)

        El RiskSystem usa esto para monitorear la exposicion del portfolio.
        En produccion, esto alimenta los reportes regulatorios de Basilea III.
        """
        ...

    # __repr__ NO lleva @abstractmethod porque tiene implementacion concreta.
    # @abstractmethod = "no tienes cuerpo, obligo a subclases a implementarlo"
    # Si ya tienes un cuerpo, es un metodo concreto normal.
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(id={self.instrument_id}, currency={self.currency})"


# ===========================================================
# LECCION 2 — Instrumentos concretos
#
# Ahora creamos clases reales que HEREDAN de FinancialInstrument.
# Aqui aplicamos polimorfismo: mismo metodo (calculate_value),
# comportamiento diferente segun el tipo de instrumento.
# ===========================================================


class Equity(FinancialInstrument):
    """A stock/share in a publicly traded company.

    Ejemplo: 100 acciones de Apple (AAPL).
    Valor = cantidad * precio_actual_en_mercado
    """

    def __init__(self, instrument_id: str, currency: str, ticker: str, quantity: Decimal):
        # super().__init__ llama al __init__ de FinancialInstrument.
        # Es OBLIGATORIO para que instrument_id y currency se guarden correctamente.
        super().__init__(instrument_id, currency)
        self.ticker = ticker
        self.quantity = quantity

    def calculate_value(self, market_data: dict) -> Decimal:
        price = market_data.get(self.ticker)
        if price is None:
            raise ValueError(f"No market data found for ticker '{self.ticker}'")
        # REGLA CLAVE EN BANCA: NUNCA uses Decimal(float) directamente.
        # Decimal(0.1) => 0.1000000000000000055511...  (ERROR de punto flotante)
        # Decimal("0.1") => 0.1  (CORRECTO)
        # En banca, un centavo de error * millones de transacciones = problema grave.
        return self.quantity * Decimal(str(price))

    def get_risk_factor(self) -> Decimal:
        return Decimal("1.0")


class Bond(FinancialInstrument):
    """A fixed income instrument (government or corporate bond).

    Ejemplo: Bono del Tesoro de $1,000,000 al 5% de cupon.
    Valor = face_value * precio_mercado_porcentual / 100
    """

    def __init__(self, instrument_id: str, currency: str, face_value: Decimal, coupon_rate: Decimal):
        super().__init__(instrument_id, currency)
        self.face_value = face_value
        self.coupon_rate = coupon_rate

    def calculate_value(self, market_data: dict) -> Decimal:
        # Los bonos se cotizan como % del valor nominal.
        # Si el bono esta a 98.50, vale el 98.5% del face_value.
        price_pct = Decimal(str(market_data.get(self.instrument_id, "100")))
        return self.face_value * price_pct / Decimal("100")

    def get_risk_factor(self) -> Decimal:
        return Decimal("0.5")


# ===========================================================
# LECCION 3 — Patron Observer: RiskSystem
#
# El patron Observer resuelve este problema:
# "Cuando algo cambia en A, quiero que B sea notificado automaticamente"
# sin que A tenga que conocer los detalles de B.
#
# Portfolio (A) = "Subject" => el que emite el evento
# RiskSystem (B) = "Observer" => el que escucha y reacciona
#
# Por que no llamar a RiskSystem directamente desde Portfolio?
# Porque manana puedes tener ComplianceSystem, AuditSystem, AlertSystem...
# Con Observer, agregas mas listeners sin tocar el Portfolio. Eso es OOP.
# ===========================================================


class RiskSystem:
    """Monitors portfolio risk exposure. Observer of Portfolio events.

    En produccion, este sistema genera alertas que van al equipo de
    riesgo y potencialmente bloquean nuevas posiciones si se exceden
    los limites regulatorios (Basilea III, Dodd-Frank, etc.).
    """

    def __init__(self, risk_threshold: Decimal):
        self.risk_threshold = risk_threshold
        self._alerts: list[str] = []

    def on_instrument_added(self, instrument: FinancialInstrument) -> None:
        """Called automatically by Portfolio when a new instrument is added."""
        risk = instrument.get_risk_factor()
        print(f"[RiskSystem] Instrument added: {instrument} | Risk factor: {risk}")

        if risk >= self.risk_threshold:
            alert = (
                f"HIGH RISK: instrument '{instrument.instrument_id}' "
                f"has risk factor {risk} >= threshold {self.risk_threshold}"
            )
            self._alerts.append(alert)
            print(f"[RiskSystem] *** ALERT: {alert} ***")

    def get_alerts(self) -> list[str]:
        return list(self._alerts)


# ===========================================================
# LECCION 4 — Portfolio
#
# El Portfolio:
#   1. Contiene una lista de FinancialInstruments
#   2. Calcula el valor total de todos los instrumentos
#   3. Notifica a los observers cuando se agrega un instrumento
#
# Portfolio NO sabe COMO cada instrumento calcula su valor.
# Solo llama calculate_value() y cada uno hace lo suyo.
# Eso es polimorfismo en accion.
# ===========================================================


class Portfolio:
    """Collection of financial instruments owned by a trader or fund."""

    def __init__(self, portfolio_id: str, owner: str):
        self.portfolio_id = portfolio_id
        self.owner = owner
        # El _ al inicio indica "privado": no modificar desde fuera de la clase.
        self._instruments: list[FinancialInstrument] = []
        self._observers: list[RiskSystem] = []

    def register_observer(self, observer: RiskSystem) -> None:
        self._observers.append(observer)

    def add_instrument(self, instrument: FinancialInstrument) -> None:
        self._instruments.append(instrument)
        self._notify_observers(instrument)

    def _notify_observers(self, instrument: FinancialInstrument) -> None:
        for observer in self._observers:
            observer.on_instrument_added(instrument)

    def calculate_total_value(self, market_data: dict) -> Decimal:
        return sum(
            instrument.calculate_value(market_data)
            for instrument in self._instruments
        )

    def __repr__(self) -> str:
        return (
            f"Portfolio(id={self.portfolio_id}, "
            f"owner='{self.owner}', "
            f"instruments={len(self._instruments)})"
        )


# ===========================================================
# EJEMPLO DE USO
# ===========================================================

if __name__ == "__main__":
    portfolio = Portfolio(portfolio_id="PORT-001", owner="John Smith")

    risk_system = RiskSystem(risk_threshold=Decimal("0.8"))
    portfolio.register_observer(risk_system)

    apple_stock = Equity(
        instrument_id="EQ-AAPL-001",
        currency="USD",
        ticker="AAPL",
        quantity=Decimal("100"),
    )
    treasury_bond = Bond(
        instrument_id="BOND-US-T-001",
        currency="USD",
        face_value=Decimal("1000000"),
        coupon_rate=Decimal("0.05"),
    )

    print("=== Adding instruments to portfolio ===")
    portfolio.add_instrument(apple_stock)    # risk_factor=1.0 => dispara alerta
    portfolio.add_instrument(treasury_bond)  # risk_factor=0.5 => sin alerta

    market_data = {
        "AAPL": 185.50,
        "BOND-US-T-001": 98.50,
    }

    print("\n=== Portfolio Valuation ===")
    total_value = portfolio.calculate_total_value(market_data)
    print(f"Portfolio: {portfolio}")
    print(f"Total Value: ${total_value:,.2f} USD")
    # Esperado:
    # AAPL:  100 * $185.50    = $18,550.00
    # BOND:  $1,000,000 * 98.5% = $985,000.00
    # TOTAL: $1,003,550.00

    print("\n=== Risk Alerts ===")
    for alert in risk_system.get_alerts():
        print(f"  - {alert}")
