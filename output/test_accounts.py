import unittest
from accounts import Account, get_share_price

class TestAccount(unittest.TestCase):

    def setUp(self):
        self.account = Account("test_user")

    def test_initial_balance(self):
        self.assertEqual(self.account.balance, 0.0)

    def test_deposit(self):
        response = self.account.deposit(100)
        self.assertEqual(response, "Successfully deposited $100.00.")
        self.assertEqual(self.account.balance, 100.0)

    def test_deposit_negative_amount(self):
        response = self.account.deposit(-50)
        self.assertEqual(response, "Deposit amount must be positive.")

    def test_withdraw(self):
        self.account.deposit(150)
        response = self.account.withdraw(100)
        self.assertEqual(response, "Successfully withdrew $100.00.")
        self.assertEqual(self.account.balance, 50.0)

    def test_withdraw_exceed_balance(self):
        response = self.account.withdraw(100)
        self.assertEqual(response, "Insufficient funds or invalid withdrawal amount.")

    def test_buy_shares(self):
        self.account.deposit(300)
        response = self.account.buy_shares('AAPL', 1)
        self.assertEqual(response, "Successfully bought 1 shares of AAPL.")
        self.assertIn('AAPL', self.account.holdings)
        self.assertEqual(self.account.holdings['AAPL'], 1)
        self.assertEqual(self.account.balance, 150.0)

    def test_buy_shares_insufficient_funds(self):
        response = self.account.buy_shares('AAPL', 2)
        self.assertEqual(response, "Insufficient funds to buy shares.")

    def test_sell_shares(self):
        self.account.deposit(300)
        self.account.buy_shares('AAPL', 1)
        response = self.account.sell_shares('AAPL', 1)
        self.assertEqual(response, "Successfully sold 1 shares of AAPL.")
        self.assertNotIn('AAPL', self.account.holdings)
        self.assertEqual(self.account.balance, 300.0)

    def test_sell_shares_insufficient(self):
        response = self.account.sell_shares('AAPL', 1)
        self.assertEqual(response, "You do not have enough shares to sell.")

    def test_calculate_portfolio_value(self):
        self.account.deposit(300)
        self.account.buy_shares('AAPL', 1)
        self.assertEqual(self.account.calculate_portfolio_value(), 450.0)

    def test_calculate_profit_loss(self):
        self.account.deposit(300)
        self.account.buy_shares('AAPL', 1)
        self.assertEqual(self.account.calculate_profit_loss(), 300.0)

    def test_get_holdings(self):
        self.account.deposit(300)
        self.account.buy_shares('AAPL', 1)
        self.assertEqual(self.account.get_holdings(), {'AAPL': 1})

    def test_get_profit_loss(self):
        self.account.deposit(300)
        self.account.buy_shares('AAPL', 1)
        self.assertEqual(self.account.get_profit_loss(), 300.0)

    def test_list_transactions(self):
        self.account.deposit(100)
        self.account.withdraw(50)
        transactions = self.account.list_transactions()
        self.assertEqual(transactions, [
            "Deposited: $100.00",
            "Withdrew: $50.00"
        ])

if __name__ == '__main__':
    unittest.main()