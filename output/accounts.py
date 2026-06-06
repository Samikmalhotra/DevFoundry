class Account:
    def __init__(self, username: str) -> None:
        self.username = username
        self.balance = 0.0
        self.holdings = {}
        self.transactions = []

    def deposit(self, amount: float) -> str:
        if amount > 0:
            self.balance += amount
            self.transactions.append(f"Deposited: ${amount:.2f}")
            return f"Successfully deposited ${amount:.2f}."
        return "Deposit amount must be positive."

    def withdraw(self, amount: float) -> str:
        if amount > 0 and self.balance >= amount:
            self.balance -= amount
            self.transactions.append(f"Withdrew: ${amount:.2f}")
            return f"Successfully withdrew ${amount:.2f}."
        return "Insufficient funds or invalid withdrawal amount."

    def buy_shares(self, symbol: str, quantity: int) -> str:
        if quantity <= 0:
            return "Quantity must be positive."
        price = get_share_price(symbol)
        total_cost = price * quantity
        if self.balance >= total_cost:
            self.balance -= total_cost
            self.holdings[symbol] = self.holdings.get(symbol, 0) + quantity
            self.transactions.append(f"Bought {quantity} shares of {symbol} at ${price:.2f} each.")
            return f"Successfully bought {quantity} shares of {symbol}."
        return "Insufficient funds to buy shares."

    def sell_shares(self, symbol: str, quantity: int) -> str:
        if quantity <= 0:
            return "Quantity must be positive."
        if symbol not in self.holdings or self.holdings[symbol] < quantity:
            return "You do not have enough shares to sell."
        price = get_share_price(symbol)
        total_value = price * quantity
        self.holdings[symbol] -= quantity
        if self.holdings[symbol] == 0:
            del self.holdings[symbol]
        self.balance += total_value
        self.transactions.append(f"Sold {quantity} shares of {symbol} at ${price:.2f} each.")
        return f"Successfully sold {quantity} shares of {symbol}."

    def calculate_portfolio_value(self) -> float:
        total_value = self.balance
        for symbol, quantity in self.holdings.items():
            total_value += get_share_price(symbol) * quantity
        return total_value

    def calculate_profit_loss(self) -> float:
        initial_investment = sum(
            get_share_price(symbol) * quantity for symbol, quantity in self.holdings.items()
        )
        return self.calculate_portfolio_value() - initial_investment

    def get_holdings(self) -> dict:
        return self.holdings

    def get_profit_loss(self) -> float:
        return self.calculate_profit_loss()

    def list_transactions(self) -> list:
        return self.transactions


def get_share_price(symbol: str) -> float:
    prices = {
        'AAPL': 150.0,
        'TSLA': 720.0,
        'GOOGL': 2800.0,
    }
    return prices.get(symbol, 0.0)  # Return 0.0 for any unspecified stock symbol.