import requests
import json
import matplotlib.pyplot as plt
from datetime import datetime

class CryptoTradingClient:
    def __init__(self, base_url='http://localhost:5000'):
        self.base_url = base_url
        self.current_user = None
        self.market_data = None

    def _make_request(self, endpoint, method='get', data=None):
        """Helper method to make HTTP requests"""
        try:
            full_url = f"{self.base_url}{endpoint}"
            if method.lower() == 'get':
                response = requests.get(full_url)
            elif method.lower() == 'post':
                response = requests.post(full_url, json=data)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error making request: {e}")
            return None

    def create_account(self):
        """Create a new user account"""
        print("\n--- Create New Account ---")
        username = input("Enter username: ")
        password = input("Enter password: ")
        email = input("Enter email: ")

        data = {
            'username': username,
            'password': password,
            'email': email
        }

        response = self._make_request('/create_account', method='post', data=data)
        if response:
            print(response.get('message', 'Account created successfully!'))
        
    def login(self):
        """User login"""
        print("\n--- Login ---")
        username = input("Enter username: ")
        password = input("Enter password: ")

        data = {
            'username': username,
            'password': password
        }

        response = self._make_request('/login', method='post', data=data)
        if response and response.get('message') == 'Login successful.':
            self.current_user = username
            print(f"Welcome, {username}!")
        else:
            print("Login failed.")

    def check_balance(self):
        """Check user account balance"""
        if not self.current_user:
            print("Please login first.")
            return

        response = self._make_request(f'/account/{self.current_user}')
        if response:
            print(f"Current Balance: ${response['balance']:.2f}")

    def deposit_funds(self):
        """Deposit funds into account"""
        if not self.current_user:
            print("Please login first.")
            return

        try:
            amount = float(input("Enter deposit amount: $"))
            data = {
                'username': self.current_user,
                'amount': amount
            }

            response = self._make_request('/deposit', method='post', data=data)
            if response:
                print(response.get('message', 'Deposit successful!'))
        except ValueError:
            print("Invalid amount entered.")

    def withdraw_funds(self):
        """Withdraw funds from account"""
        if not self.current_user:
            print("Please login first.")
            return

        try:
            amount = float(input("Enter withdrawal amount: $"))
            data = {
                'username': self.current_user,
                'amount': amount
            }

            response = self._make_request('/withdraw', method='post', data=data)
            if response:
                print(response.get('message', 'Withdrawal successful!'))
        except ValueError:
            print("Invalid amount entered.")

    def fetch_market_data(self):
        """Fetch and display current market data"""
        response = self._make_request('/market_data')
        if response:
            self.market_data = response
            print("\n--- Market Data ---")
            for asset in response[:50]:
                print(f"{asset['name']} ({asset['symbol'].upper()}): ${asset['current_price']:.2f}")

    def view_portfolio(self):
        """View user's portfolio"""
        if not self.current_user:
            print("Please login first.")
            return

        data = {'username': self.current_user}
        response = self._make_request('/portfolio/view', method='post', data=data)
        if response:
            print("\n--- Portfolio Summary ---")
            print(f"Account Balance: ${response['account_balance']:.2f}")
            print(f"Total Portfolio Value: ${response['total_portfolio_value']:.2f}")
            print(f"Total Net Worth: ${response['total_net_worth']:.2f}")
            
            print("\nHoldings:")
            for holding in response.get('holdings', []):
                print(f"{holding['asset']}: {holding['quantity']} units")
                print(f"  Current Price: ${holding['current_price']:.2f}")
                print(f"  Profit/Loss: {holding['profit_loss_percentage']:.2f}%")

    def buy_asset(self):
        """Buy an asset"""
        if not self.current_user:
            print("Please login first.")
            return

        if not self.market_data:
            print("Fetch market data first.")
            return

        print("\n--- Available Assets ---")
        for idx, asset in enumerate(self.market_data[:10], 1):
            print(f"{idx}. {asset['name']} ({asset['symbol'].upper()}): ${asset['current_price']:.2f}")

        try:
            selection = int(input("Select asset number: ")) - 1
            if 0 <= selection < len(self.market_data):
                asset_name = self.market_data[selection]['name']
                quantity = float(input("Enter quantity to buy: "))

                data = {
                    'username': self.current_user,
                    'asset_name': asset_name,
                    'quantity': quantity
                }

                response = self._make_request('/trade/buy', method='post', data=data)
                if response:
                    print(response.get('message', 'Purchase successful!'))
            else:
                print("Invalid selection.")
        except ValueError:
            print("Invalid input.")

    def sell_asset(self):
        """Sell an asset from portfolio"""
        if not self.current_user:
            print("Please login first.")
            return

        data = {'username': self.current_user}
        portfolio_response = self._make_request('/portfolio/view', method='post', data=data)
        
        if portfolio_response and portfolio_response.get('holdings'):
            print("\n--- Your Holdings ---")
            for idx, holding in enumerate(portfolio_response['holdings'], 1):
                print(f"{idx}. {holding['asset']}: {holding['quantity']} units")

            try:
                selection = int(input("Select asset number to sell: ")) - 1
                if 0 <= selection < len(portfolio_response['holdings']):
                    asset_name = portfolio_response['holdings'][selection]['asset']
                    quantity = float(input("Enter quantity to sell: "))

                    sell_data = {
                        'username': self.current_user,
                        'asset_name': asset_name,
                        'quantity': quantity
                    }

                    response = self._make_request('/trade/sell', method='post', data=sell_data)
                    if response:
                        print(response.get('message', 'Sale successful!'))
                        print(f"Total Revenue: ${response.get('total_revenue', 0):.2f}")
                        print(f"Profit/Loss: ${response.get('profit_loss', 0):.2f}")
                else:
                    print("Invalid selection.")
            except ValueError:
                print("Invalid input.")

    def view_transaction_history(self):
        """View transaction history"""
        if not self.current_user:
            print("Please login first.")
            return

        data = {'username': self.current_user}
        response = self._make_request('/transactions/history', method='post', data=data)
        
        if response and response.get('transaction_history'):
            print("\n--- Transaction History ---")
            for transaction in response['transaction_history']:
                print(f"{transaction['timestamp']}: {transaction['type']} - ${transaction['amount']:.2f} ({transaction['asset'] or 'N/A'})")

    def view_asset_trend(self):
        """View trend of a specific asset"""
        if not self.market_data:
            print("Fetch market data first.")
            return

        print("\n--- Available Assets ---")
        for idx, asset in enumerate(self.market_data[:50], 1):
            print(f"{idx}. {asset['name']} ({asset['symbol'].upper()})")

        try:
            selection = int(input("Select asset number: ")) - 1
            if 0 <= selection < len(self.market_data):
                asset_name = self.market_data[selection]['name']
                response = self._make_request(f'/historical_prices/{asset_name}')
                
                if response and response.get('historical_prices'):
                    prices = response['historical_prices']
                    timestamps = [datetime.fromisoformat(entry['timestamp']) for entry in prices]
                    price_values = [entry['price'] for entry in prices]

                    plt.figure(figsize=(10, 6))
                    plt.plot(timestamps, price_values, label=asset_name)
                    plt.title(f"{asset_name} Price Trend")
                    plt.xlabel("Timestamp")
                    plt.ylabel("Price ($)")
                    plt.xticks(rotation=45)
                    plt.tight_layout()
                    plt.show()
            else:
                print("Invalid selection.")
        except ValueError:
            print("Invalid input.")

    def main_menu(self):
        """Main application loop"""
        while True:
            print("\n--- Crypto Trading Platform ---")
            if not self.current_user:
                print("1. Create Account")
                print("2. Login")
                print("3. Exit")
            else:
                print(f"Logged in as: {self.current_user}")
                print("1. Check Balance")
                print("2. Deposit Funds")
                print("3. Withdraw Funds")
                print("4. Fetch Market Data")
                print("5. View Portfolio")
                print("6. Buy Asset")
                print("7. Sell Asset")
                print("8. Transaction History")
                print("9. Asset Price Trend")
                print("10. Logout")
                print("11. Exit")

            try:
                choice = int(input("Enter your choice: "))

                # Handling choices for non-logged-in state
                if not self.current_user:
                    if choice == 1:
                        self.create_account()
                    elif choice == 2:
                        self.login()
                    elif choice == 3:
                        print("Goodbye!")
                        break
                    else:
                        print("Invalid choice. Try again.")

                # Handling choices for logged-in state
                else:
                    if choice == 1:
                        self.check_balance()
                    elif choice == 2:
                        self.deposit_funds()
                    elif choice == 3:
                        self.withdraw_funds()
                    elif choice == 4:
                        self.fetch_market_data()
                    elif choice == 5:
                        self.view_portfolio()
                    elif choice == 6:
                        self.buy_asset()
                    elif choice == 7:
                        self.sell_asset()
                    elif choice == 8:
                        self.view_transaction_history()
                    elif choice == 9:
                        self.view_asset_trend()
                    elif choice == 10:
                        print(f"Goodbye, {self.current_user}!")
                        self.current_user = None
                    elif choice == 11:
                        print("Goodbye!")
                        break
                    else:
                        print("Invalid choice. Try again.")

            except ValueError:
                print("Please enter a valid number.")

def main():
    client = CryptoTradingClient()
    client.main_menu()

if __name__ == "__main__":
    main()
