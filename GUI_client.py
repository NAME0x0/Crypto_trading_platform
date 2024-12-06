import sys
import requests
import json
import matplotlib.pyplot as plt
from datetime import datetime
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QStackedWidget, QPushButton, QLabel, QLineEdit, QMessageBox, 
    QTableWidget, QTableWidgetItem, QDialog, QFormLayout, 
    QComboBox, QDialogButtonBox, QScrollArea
)
from PyQt6.QtGui import QFont, QIcon
from PyQt6.QtCore import Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

class CryptoTradingGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.base_url = 'http://localhost:5000'
        self.current_user = None
        self.market_data = None
        
        self.setWindowTitle('Crypto Trading Platform')
        self.setGeometry(100, 100, 1200, 800)
        
        # Main widget and layout
        main_widget = QWidget()
        main_layout = QHBoxLayout()
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)
        
        # Navigation sidebar
        nav_layout = QVBoxLayout()
        nav_widget = QWidget()
        nav_widget.setLayout(nav_layout)
        nav_widget.setFixedWidth(200)
        main_layout.addWidget(nav_widget)
        
        # Stacked widget for main content
        self.stacked_widget = QStackedWidget()
        main_layout.addWidget(self.stacked_widget)
        
        # Create pages
        self.create_pages()
        
        # Create navigation buttons
        self.create_nav_buttons(nav_layout)
        
        # Start with login page
        self.stacked_widget.setCurrentWidget(self.login_page)
    
    def create_pages(self):
        """Create all pages for the application"""
        # Login Page
        self.login_page = QWidget()
        login_layout = QVBoxLayout()
        self.login_page.setLayout(login_layout)
        
        # Login inputs
        username_label = QLabel("Username:")
        self.username_input = QLineEdit()
        password_label = QLabel("Password:")
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        
        login_btn = QPushButton("Login")
        login_btn.clicked.connect(self.login)
        create_account_btn = QPushButton("Create Account")
        create_account_btn.clicked.connect(self.create_account)
        
        login_layout.addWidget(username_label)
        login_layout.addWidget(self.username_input)
        login_layout.addWidget(password_label)
        login_layout.addWidget(self.password_input)
        login_layout.addWidget(login_btn)
        login_layout.addWidget(create_account_btn)
        login_layout.addStretch()
        
        # Balance Page
        self.balance_page = QWidget()
        balance_layout = QVBoxLayout()
        self.balance_page.setLayout(balance_layout)
        
        self.balance_label = QLabel("Balance: $0.00")
        balance_deposit_btn = QPushButton("Deposit Funds")
        balance_deposit_btn.clicked.connect(self.deposit_funds)
        balance_withdraw_btn = QPushButton("Withdraw Funds")
        balance_withdraw_btn.clicked.connect(self.withdraw_funds)
        
        balance_layout.addWidget(self.balance_label)
        balance_layout.addWidget(balance_deposit_btn)
        balance_layout.addWidget(balance_withdraw_btn)
        balance_layout.addStretch()
        
        # Market Data Page
        self.market_data_page = QWidget()
        market_data_layout = QVBoxLayout()
        self.market_data_page.setLayout(market_data_layout)
        
        fetch_market_btn = QPushButton("Fetch Market Data")
        fetch_market_btn.clicked.connect(self.fetch_market_data)
        self.market_table = QTableWidget()
        self.market_table.setColumnCount(4)
        self.market_table.setHorizontalHeaderLabels(["Name", "Symbol", "Current Price", "Market Cap"])
        
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(self.market_table)

        market_data_layout.addWidget(fetch_market_btn)
        market_data_layout.addWidget(self.market_table)
        
        # Portfolio Page
        self.portfolio_page = QWidget()
        portfolio_layout = QVBoxLayout()
        self.portfolio_page.setLayout(portfolio_layout)
        
        view_portfolio_btn = QPushButton("View Portfolio")
        view_portfolio_btn.clicked.connect(self.view_portfolio)
        self.portfolio_table = QTableWidget()
        self.portfolio_table.setColumnCount(5)
        self.portfolio_table.setHorizontalHeaderLabels(["Asset", "Quantity", "Current Price", "Total Value", "Profitability"])
        
        portfolio_layout.addWidget(view_portfolio_btn)
        portfolio_layout.addWidget(self.portfolio_table)
        
        # Trade Page
        self.trade_page = QWidget()
        trade_layout = QVBoxLayout()
        self.trade_page.setLayout(trade_layout)
        
        # Buy section
        buy_group = QWidget()
        buy_layout = QFormLayout()
        self.buy_asset_combo = QComboBox()
        self.buy_quantity_input = QLineEdit()
        buy_btn = QPushButton("Buy Asset")
        buy_btn.clicked.connect(self.buy_asset)
        
        buy_layout.addRow("Asset:", self.buy_asset_combo)
        buy_layout.addRow("Quantity:", self.buy_quantity_input)
        buy_layout.addRow(buy_btn)
        buy_group.setLayout(buy_layout)
        
        # Sell section
        sell_group = QWidget()
        sell_layout = QFormLayout()
        self.sell_asset_combo = QComboBox()
        self.sell_quantity_input = QLineEdit()
        sell_btn = QPushButton("Sell Asset")
        sell_btn.clicked.connect(self.sell_asset)
        
        sell_layout.addRow("Asset:", self.sell_asset_combo)
        sell_layout.addRow("Quantity:", self.sell_quantity_input)
        sell_layout.addRow(sell_btn)
        sell_group.setLayout(sell_layout)
        
        trade_layout.addWidget(QLabel("<h2>Buy Assets</h2>"))
        trade_layout.addWidget(buy_group)
        trade_layout.addWidget(QLabel("<h2>Sell Assets</h2>"))
        trade_layout.addWidget(sell_group)
        trade_layout.addStretch()
        
        # Transaction History Page
        self.transaction_page = QWidget()
        transaction_layout = QVBoxLayout()
        self.transaction_page.setLayout(transaction_layout)
        
        view_transactions_btn = QPushButton("View Transaction History")
        view_transactions_btn.clicked.connect(self.view_transaction_history)
        self.transaction_table = QTableWidget()
        self.transaction_table.setColumnCount(4)
        self.transaction_table.setHorizontalHeaderLabels(["Timestamp", "Type", "Amount", "Asset"])
        
        transaction_layout.addWidget(view_transactions_btn)
        transaction_layout.addWidget(self.transaction_table)
        
        # Asset Trend Page
        self.asset_trend_page = QWidget()
        trend_layout = QVBoxLayout()
        self.asset_trend_page.setLayout(trend_layout)
        
        self.trend_asset_combo = QComboBox()
        view_trend_btn = QPushButton("View Asset Trend")
        view_trend_btn.clicked.connect(self.view_asset_trend)
        
        trend_layout.addWidget(self.trend_asset_combo)
        trend_layout.addWidget(view_trend_btn)
        
        # Add pages to stacked widget
        self.stacked_widget.addWidget(self.login_page)
        self.stacked_widget.addWidget(self.balance_page)
        self.stacked_widget.addWidget(self.market_data_page)
        self.stacked_widget.addWidget(self.portfolio_page)
        self.stacked_widget.addWidget(self.trade_page)
        self.stacked_widget.addWidget(self.transaction_page)
        self.stacked_widget.addWidget(self.asset_trend_page)

        self.fetch_market_data()
    
    def create_nav_buttons(self, nav_layout):
        """Create navigation buttons"""
        nav_buttons = [
            ("Login", self.login_page),
            ("Balance", self.balance_page),
            ("Market Data", self.market_data_page),
            ("Portfolio", self.portfolio_page),
            ("Trade", self.trade_page),
            ("Transactions", self.transaction_page),
            ("Asset Trend", self.asset_trend_page)
        ]
        
        for label, page in nav_buttons:
            btn = QPushButton(label)
            btn.clicked.connect(lambda checked, p=page: self.stacked_widget.setCurrentWidget(p))
            nav_layout.addWidget(btn)

        nav_layout.addStretch()
        
        # Logout button
        logout_btn = QPushButton("Logout")
        logout_btn.clicked.connect(self.logout)
        nav_layout.addWidget(logout_btn)
        
        # Add stretch to push buttons to top
        nav_layout.addStretch()
    
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
            self.show_error_message(f"Error making request: {e}")
            return None
    
    def show_error_message(self, message):
        """Display error message"""
        QMessageBox.critical(self, "Error", message)
    
    def show_success_message(self, message):
        """Display success message"""
        QMessageBox.information(self, "Success", message)
    
    def login(self):
        """Handle user login"""
        username = self.username_input.text()
        password = self.password_input.text()
        
        data = {
            'username': username,
            'password': password }
        
        response = self._make_request('/login', method='post', data=data)
        if response and response.get('message') == 'Login successful.':
            self.current_user = username
            self.show_success_message(f"Welcome, {username}!")
            self.check_balance()
            self.stacked_widget.setCurrentWidget(self.balance_page)
        else:
            self.show_error_message("Login failed.")
    
    def create_account(self):
        """Handle account creation"""
        username = self.username_input.text()
        password = self.password_input.text()
        
        # Open dialog for additional details
        dialog = QDialog(self)
        dialog.setWindowTitle("Create Account")
        layout = QFormLayout()
        
        email_input = QLineEdit()
        layout.addRow("Email:", email_input)
        
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addRow(buttons)
        
        dialog.setLayout(layout)
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            email = email_input.text()
            data = {
                'username': username,
                'password': password,
                'email': email
            }
            
            response = self._make_request('/create_account', method='post', data=data)
            if response:
                self.show_success_message(response.get('message', 'Account created successfully!'))
    
    def deposit_funds(self):
        """Handle fund deposit"""
        if not self.current_user:
            self.show_error_message("Please login first.")
            return
        
        dialog = QDialog(self)
        dialog.setWindowTitle("Deposit Funds")
        layout = QFormLayout()
        
        amount_input = QLineEdit()
        layout.addRow("Amount:", amount_input)
        
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addRow(buttons)
        
        dialog.setLayout(layout)
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            try:
                amount = float(amount_input.text())
                data = {
                    'username': self.current_user,
                    'amount': amount
                }
                
                response = self._make_request('/deposit', method='post', data=data)
                if response:
                    self.show_success_message(response.get('message', 'Deposit successful!'))
                    # Refresh balance
                    self.check_balance()
            except ValueError:
                self.show_error_message("Invalid amount entered.")
    
    def withdraw_funds(self):
        """Handle fund withdrawal"""
        if not self.current_user:
            self.show_error_message("Please login first.")
            return
        
        dialog = QDialog(self)
        dialog.setWindowTitle("Withdraw Funds")
        layout = QFormLayout()
        
        amount_input = QLineEdit()
        layout.addRow("Amount:", amount_input)
        
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addRow(buttons)
        
        dialog.setLayout(layout)
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            try:
                amount = float(amount_input.text())
                data = {
                    'username': self.current_user,
                    'amount': amount
                }
                
                response = self._make_request('/withdraw', method='post', data=data)
                if response:
                    self.show_success_message(response.get('message', 'Withdrawal successful!'))
                    # Refresh balance
                    self.check_balance()
            except ValueError:
                self.show_error_message("Invalid amount entered.")
    
    def check_balance(self):
        """Fetch and display user balance"""
        if not self.current_user:
            self.show_error_message("Please login first.")
            return
        
        response = self._make_request(f'/account/{self.current_user}')
        if response:
            balance = response.get('balance', 0)
            self.balance_label.setText(f"Balance: ${balance:.2f}")
    
    def fetch_market_data(self):
        """Fetch and display current market data"""
        response = self._make_request('/market_data')
        if response:
            self.market_data = response
            self.market_table.setRowCount(0)
            self.buy_asset_combo.clear()
            self.sell_asset_combo.clear()
            self.trend_asset_combo.clear()

            for asset in response[:50]:
                row_position = self.market_table.rowCount()
                self.market_table.insertRow(row_position)
                self.market_table.setItem(row_position, 0, QTableWidgetItem(asset['name']))
                self.market_table.setItem(row_position, 1, QTableWidgetItem(asset['symbol'].upper()))
                self.market_table .setItem(row_position, 2, QTableWidgetItem(f"${asset['current_price']:.2f}"))
                self.market_table.setItem(row_position, 3, QTableWidgetItem(f"${asset.get('market_cap', 'N/A')}"))

                self.buy_asset_combo.addItem(asset['name'])
                self.sell_asset_combo.addItem(asset['name'])
                self.trend_asset_combo.addItem(asset['name'])

    def view_portfolio(self):
        """Fetch and display user's portfolio"""
        if not self.current_user:
            self.show_error_message("Please login first.")
            return

        data = {'username': self.current_user}
        response = self._make_request('/portfolio/view', method='post', data=data)
        if response:
            self.portfolio_table.setRowCount(0)  # Clear existing data
            total_net_worth = response['total_net_worth']
            self.balance_label.setText(f"Balance: ${response['account_balance']:.2f} (Net Worth: ${total_net_worth:.2f})")

            for holding in response.get('holdings', []):
                row_position = self.portfolio_table.rowCount()
                self.portfolio_table.insertRow(row_position)
                self.portfolio_table.setItem(row_position, 0, QTableWidgetItem(holding.get('asset', 'N/A')))
                self.portfolio_table.setItem(row_position, 1, QTableWidgetItem(str(holding.get('quantity', 0))))
                self.portfolio_table.setItem(row_position, 2, QTableWidgetItem(f"${holding.get('current_price', 0):.2f}"))
                self.portfolio_table.setItem(row_position, 3, QTableWidgetItem(f"${holding.get('total_value', 0):.2f}"))
                self.portfolio_table.setItem(row_position, 4, QTableWidgetItem(f"{holding.get('profit_loss_percentage', 0):.2f}%"))

    def buy_asset(self):
        """Handle buying an asset"""
        if not self.current_user:
            self.show_error_message("Please login first.")
            return

        asset_name = self.buy_asset_combo.currentText()
        try:
            quantity = float(self.buy_quantity_input.text())
            data = {
                'username': self.current_user,
                'asset_name': asset_name,
                'quantity': quantity
            }
            response = self._make_request('/trade/buy', method='post', data=data)
            if response:
                self.show_success_message(response.get('message', 'Purchase successful!'))
                self.check_balance()  # Refresh balance
        except ValueError:
            self.show_error_message("Invalid quantity entered.")

    def sell_asset(self):
        """Handle selling an asset"""
        if not self.current_user:
            self.show_error_message("Please login first.")
            return

        asset_name = self.sell_asset_combo.currentText()
        try:
            quantity = float(self.sell_quantity_input.text())
            data = {
                'username': self.current_user,
                'asset_name': asset_name,
                'quantity': quantity
            }
            response = self._make_request('/trade/sell', method='post', data=data)
            if response:
                self.show_success_message(response.get('message', 'Sale successful!'))
                self.check_balance()  # Refresh balance
        except ValueError:
            self.show_error_message("Invalid quantity entered.")

    def view_transaction_history(self):
        """Fetch and display transaction history"""
        if not self.current_user:
            self.show_error_message("Please login first.")
            return

        data = {'username': self.current_user}
        response = self._make_request('/transactions/history', method='post', data=data)
        if response and response.get('transaction_history'):
            self.transaction_table.setRowCount(0)  # Clear existing data
            for transaction in response['transaction_history']:
                row_position = self.transaction_table.rowCount()
                self.transaction_table.insertRow(row_position)
                self.transaction_table.setItem(row_position, 0, QTableWidgetItem(transaction['timestamp']))
                self.transaction_table.setItem(row_position, 1, QTableWidgetItem(transaction['type']))
                self.transaction_table.setItem(row_position, 2, QTableWidgetItem(f"${transaction['amount']:.2f}"))
                self.transaction_table.setItem(row_position, 3, QTableWidgetItem(transaction['asset'] or 'N/A'))

    def view_asset_trend(self):
        """Fetch and display asset price trend"""
        asset_name = self.trend_asset_combo.currentText()
        response = self._make_request(f'/historical_prices/{asset_name}')

        if response and response.get('historical_prices'):
            prices = response['historical_prices']
            timestamps = [datetime.fromisoformat(entry['timestamp']) for entry in prices]
            price_values = [entry['price'] for entry in prices]

            # Create a matplotlib figure
            plt.figure(figsize=(10, 6))
            plt.plot(timestamps, price_values, label=asset_name)
            plt.title(f"{asset_name} Price Trend")
            plt.xlabel("Timestamp")
            plt.ylabel("Price ($)")
            plt.xticks(rotation=45)
            plt.tight_layout()
            plt.show()

    def logout(self):
        """Handle user logout"""
        self.current_user = None
        self.username_input.clear()
        self.password_input.clear()
        self.balance_label.setText("Balance: $0.00")
        self.market_table.setRowCount(0)
        self.portfolio_table.setRowCount(0)
        self.transaction_table.setRowCount(0)
        self.stacked_widget.setCurrentWidget(self.login_page)

def main():
    app = QApplication(sys.argv)
    window = CryptoTradingGUI()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
