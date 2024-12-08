import sys
import requests
import json
import matplotlib.pyplot as plt
from datetime import datetime
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QStackedWidget, QPushButton, QLabel, QLineEdit, QMessageBox, 
    QTableWidget, QTableWidgetItem, QDialog, QFormLayout, 
    QComboBox, QDialogButtonBox, QScrollArea, QGraphicsDropShadowEffect,
)
from PyQt6.QtGui import QColor, QDoubleValidator
from PyQt6.QtCore import Qt

class StyledButton(QPushButton):
    """Custom styled button for a more modern look"""
    def __init__(self, text, primary=False):
        super().__init__(text)
        self.setMinimumHeight(40)
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {'#3498db' if primary else '#2ecc71'};
                color: white;
                border-radius: 5px;
                font-weight: bold;
                padding: 8px;
            }}
            QPushButton:hover {{
                background-color: {'#2980b9' if primary else '#27ae60'};
            }}
            QPushButton:pressed {{
                background-color: {'#21618c' if primary else '#1e8449'};
            }}
        """)

class CryptoTradingGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.base_url = 'http://localhost:5000'
        self.current_user = None
        self.market_data = None
        self.available_assets = []  # Initialize available assets
        
        # Set up a dark, modern theme
        self.setup_theme()
        
        self.setWindowTitle('CryptoVault Trading Platform')
        self.setGeometry(100, 100, 1400, 900)
        
        # Main widget and layout
        main_widget = QWidget()
        main_layout = QHBoxLayout()
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)
        
        # Stacked widget for main content
        self.stacked_widget = QStackedWidget()  # Create stacked widget first
        main_layout.addWidget(self.stacked_widget)
        
        # Create pages with enhanced styling
        self.create_pages()  # Create pages after stacked widget
        
        # Navigation sidebar with improved styling
        nav_widget = self.create_nav_sidebar()  # Now this can access the pages
        main_layout.addWidget(nav_widget)
        
        # Start with login page
        self.stacked_widget.setCurrentWidget(self.login_page)
        
        # Add shadow effect to the main window
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 80))
        shadow.setOffset(0, 0)
        self.setGraphicsEffect(shadow)
    
    def setup_theme(self):
        """Set up a dark, modern theme for the application"""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1e2329;
                color: #ffffff;
            }
            QWidget {
                background-color: #2c3036;
                color: #ffffff;
                font-family: Arial, sans-serif;
            }
            QLabel {
                color: #ffffff;
            }
            QLineEdit {
                background-color: #3c4048;
                border: 1px solid #4a4f57;
                color: #ffffff;
                border-radius: 5px;
                padding: 6px;
            }
            QTableWidget {
                background-color: #2c3036;
                alternate-background-color: #353b43;
                selection-background-color: #3498db;
            }
            QTableWidget::item {
                color: #ffffff;
                padding: 5px;
            }
            QHeaderView::section {
                background-color: #3c4048;
                color: #ffffff;
                padding: 5px;
                border: none;
            }
            QComboBox {
                background-color: #3c4048;
                color: #ffffff;
                border-radius: 5px;
                padding: 6px;
            }
            QScrollArea {
                border: none;
            }
        """)
    
    def create_nav_sidebar(self):
        """Create a styled navigation sidebar"""
        nav_widget = QWidget()
        nav_layout = QVBoxLayout()
        nav_widget.setLayout(nav_layout)
        nav_widget.setFixedWidth(250)
        nav_widget.setStyleSheet("""
            QWidget {
                background-color: #252932;
                border-right: 1px solid #3c4048;
            }
        """)
        
        # Logo or title
        logo_label = QLabel("CryptoVault")
        logo_label.setStyleSheet("""
            font-size: 24px;
            font-weight: bold;
            color: #3498db;
            padding: 20px;
            text-align: center;
        """)
        nav_layout.addWidget(logo_label)
        
        # Navigation buttons
        nav_buttons = [
            ("Dashboard", self.balance_page, "dashboard-icon"),
            ("Market Data", self.market_data_page, "market-icon"),
            ("Portfolio", self.portfolio_page, "portfolio-icon"),
            ("Trade", self.trade_page, "trade-icon"),
            ("Transactions", self.transaction_page, "transaction-icon"),
            ("Asset Trends", self.asset_trend_page, "trend-icon")
        ]
        
        for label, page, icon in nav_buttons:
            btn = StyledButton(label)
            btn.clicked.connect(lambda checked, p=page: self.stacked_widget.setCurrentWidget(p))
            nav_layout.addWidget(btn)
        
        nav_layout.addStretch()
        
        # Logout button
        logout_btn = StyledButton("Logout", primary=False)
        logout_btn.clicked.connect(self.logout)
        nav_layout.addWidget(logout_btn)
        
        # Add padding and stretch
        nav_layout.addSpacing(20)
        
        return nav_widget
    
    def create_pages(self):
        """Create pages with enhanced styling and layout"""
    
        # Login Page
        self.login_page = QWidget()
        login_layout = QVBoxLayout()
        self.login_page.setLayout(login_layout)

        login_title = QLabel("Welcome to CryptoVault")
        login_title.setStyleSheet("""
            font-size: 28px;
            font-weight: bold;
            color: #3498db;
            margin-bottom: 20px;
            text-align: center;
        """)
        login_layout.addWidget(login_title)

        # Login inputs
        username_label = QLabel("Username:")
        self.username_input = QLineEdit()
        password_label = QLabel("Password:")
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)

        login_btn = StyledButton("Login", primary=True)
        login_btn.clicked.connect(self.login)
        create_account_btn = StyledButton("Create Account")
        create_account_btn.clicked.connect(self.create_account)

        login_layout.addWidget(username_label)
        login_layout.addWidget(self.username_input)
        login_layout.addSpacing(10)
        login_layout.addWidget(password_label)
        login_layout.addWidget(self.password_input)
        login_layout.addSpacing(20)
        login_layout.addWidget(login_btn)
        login_layout.addWidget(create_account_btn)
        login_layout.addStretch()

        # Balance Page
        self.balance_page = QWidget()
        balance_layout = QVBoxLayout()
        self.balance_page.setLayout(balance_layout)

        balance_title = QLabel("Account Dashboard")
        balance_title.setStyleSheet("""
            font-size: 24px;
            font-weight: bold;
            color: #3498db;
            margin-bottom: 20px;
        """)

        self.balance_label = QLabel("Balance: $0.00")
        self.balance_label.setStyleSheet("""
            font-size: 18px;
            font-weight: bold;
            color: #2ecc71;
        """)

        balance_deposit_btn = StyledButton("Deposit Funds", primary=True)
        balance_deposit_btn.clicked.connect(self.deposit_funds)
        balance_withdraw_btn = StyledButton("Withdraw Funds")
        balance_withdraw_btn.clicked.connect(self.withdraw_funds)

        balance_layout.addWidget(balance_title)
        balance_layout.addWidget(self.balance_label)
        balance_layout.addSpacing(20)
        balance_layout.addWidget(balance_deposit_btn)
        balance_layout.addWidget(balance_withdraw_btn)
        balance_layout.addStretch()

        # Market Data Page
        self.market_data_page = QWidget()
        market_data_layout = QVBoxLayout()
        self.market_data_page.setLayout(market_data_layout)

        market_title = QLabel("Market Overview")
        market_title.setStyleSheet("""
            font-size: 24px;
            font-weight: bold;
            color: #3498db;
            margin-bottom: 20px;
        """)

        fetch_market_btn = StyledButton("Refresh Market Data", primary=True)
        fetch_market_btn.clicked.connect(self.fetch_market_data)
        self.market_table = QTableWidget()
        self.market_table.setColumnCount(4)
        self.market_table.setHorizontalHeaderLabels(["Name", "Symbol", "Current Price", "Market Cap"])
        self.market_table.setAlternatingRowColors(True)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(self.market_table)

        market_data_layout.addWidget(market_title)
        market_data_layout.addWidget(fetch_market_btn)
        market_data_layout.addWidget(scroll_area)

        # Portfolio Page
        self.portfolio_page = QWidget()
        portfolio_layout = QVBoxLayout()
        self.portfolio_page.setLayout(portfolio_layout)

        view_portfolio_btn = StyledButton("View Portfolio")
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
        buy_layout = QVBoxLayout()
        buy_group.setLayout(buy_layout)

        buy_title = QLabel("Buy Cryptocurrency")
        buy_title.setStyleSheet("""
            font-size: 24px;
            font-weight: bold;
            color: #3498db;
            margin-bottom: 20px;
        """)

        self.buy_asset_combo = QComboBox()
        self.buy_quantity_input = QLineEdit()
        buy_btn = StyledButton("Buy", primary=True)
        buy_btn.clicked.connect(self.buy_asset)

        buy_layout.addWidget(buy_title)
        buy_layout.addWidget(QLabel("Asset:"))
        buy_layout.addWidget(self.buy_asset_combo)
        buy_layout.addWidget(QLabel("Quantity:"))
        buy_layout.addWidget(self.buy_quantity_input)
        buy_layout.addWidget(buy_btn)

        trade_layout.addWidget(buy_group)

        # Sell section
        sell_group = QWidget()
        sell_layout = QVBoxLayout()
        sell_group.setLayout(sell_layout)

        sell_title = QLabel("Sell Cryptocurrency")
        sell_title.setStyleSheet("""
            font-size: 24px;
            font-weight: bold;
            color: #3498db;
            margin-bottom: 20px;
        """)

        self.sell_asset_combo = QComboBox()  # Combo box for selecting the asset to sell
        self.sell_quantity_input = QLineEdit()  # Change to QLineEdit for quantity input
        self.sell_quantity_input.setPlaceholderText("Enter quantity to sell")
        self.sell_quantity_input.setValidator(QDoubleValidator(0.99, 99.99, 2))  # Allow only numeric input

        sell_btn = StyledButton("Sell", primary=True)
        sell_btn.clicked.connect(self.sell_asset)

        sell_layout.addWidget(sell_title)
        sell_layout.addWidget(QLabel("Asset:"))
        sell_layout.addWidget(self.sell_asset_combo)
        sell_layout.addWidget(QLabel("Quantity:"))
        sell_layout.addWidget(self.sell_quantity_input)  # Use QLineEdit for quantity
        sell_layout.addWidget(sell_btn)

        trade_layout.addWidget(sell_group)

        # Asset Trends Page
        self.asset_trend_page = QWidget()  # Define asset_trend_page
        trend_layout = QVBoxLayout()
        self.asset_trend_page.setLayout(trend_layout)

        trend_title = QLabel("Asset Trends")
        trend_title.setStyleSheet("""
            font-size: 24px;
            font-weight: bold;
            color: #3498db;
            margin-bottom: 20px;
        """)

        # Create the combo box for selecting the asset for trend analysis
        self.trend_asset_combo = QComboBox()
        trend_layout.addWidget(trend_title)
        trend_layout.addWidget(QLabel("Select Asset:"))
        trend_layout.addWidget(self.trend_asset_combo)

        # Add additional components for displaying trends
        self.trend_display = QLabel("Trend data will be displayed here.")
        trend_layout.addWidget(self.trend_display)

        # Connect the asset selection to a method that fetches and displays trends
        self.trend_asset_combo.currentIndexChanged.connect(self.display_asset_trend)

        # Transaction History Page
        self.transaction_page = QWidget()
        transaction_layout = QVBoxLayout()
        self.transaction_page.setLayout(transaction_layout)

        transaction_title = QLabel("Transaction History")
        transaction_title.setStyleSheet("""
            font-size: 24px;
            font-weight: bold;
            color: #3498db;
            margin-bottom: 20px;
        """)

        self.transaction_table = QTableWidget()
        self.transaction_table.setColumnCount(4)
        self.transaction_table.setHorizontalHeaderLabels(["Timestamp", "Type", "Amount", "Asset"])

        view_transactions_btn = StyledButton("View Transaction History")
        view_transactions_btn.clicked.connect(self.view_transaction_history)

        transaction_layout.addWidget(transaction_title)
        transaction_layout.addWidget(view_transactions_btn)
        transaction_layout.addWidget(self.transaction_table)

        # Add all pages to the stacked widget
        self.stacked_widget.addWidget(self.login_page)
        self.stacked_widget.addWidget(self.balance_page)
        self.stacked_widget.addWidget(self.market_data_page)
        self.stacked_widget.addWidget(self.portfolio_page)
        self.stacked_widget.addWidget(self.trade_page)
        self.stacked_widget.addWidget(self.asset_trend_page)
        self.stacked_widget.addWidget(self.transaction_page)

        # Fetch market data to populate assets
        self.fetch_market_data()

    def update_sell_quantity_combo(self):
        """Update the sell quantity input based on the selected asset."""
        asset_name = self.sell_asset_combo.currentText()
        if asset_name:
            data = {'username': self.current_user}
            response = self._make_request('/portfolio/view', method='post', data=data)
            if response:
                for holding in response.get('holdings', []):
                    if holding.get('asset') == asset_name:
                        self.sell_quantity_input.setText(str(holding.get('quantity', 0)))
                        break
                else:
                    self.sell_quantity_input.clear()

    def display_asset_trend(self):
        """Fetch and display the trend for the selected asset."""
        asset_name = self.trend_asset_combo.currentText()
        if asset_name:
            response = self._make_request(f'/trends/{asset_name}', method='get')
            if response:
                trend_data = response.get('trend_data', 'No data available.')
                self.trend_display.setText(trend_data)
            else:
                self.trend_display.setText("Error fetching trend data.")

    def _make_request(self, endpoint, method='get', data=None):
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
        error_dialog = QMessageBox(self)
        error_dialog.setIcon(QMessageBox.Icon.Critical)
        error_dialog.setWindowTitle("Error")
        error_dialog.setText(message)
        error_dialog.setStyleSheet("""
            QMessageBox {
                background-color: #2c3036;
                color: #ffffff;
            }
            QMessageBox QLabel {
                color: #ffffff;
            }
            QMessageBox QPushButton {
                background-color: #3498db;
                color: white;
                border-radius: 5px;
                padding: 8px;
            }
        """)
        error_dialog.exec()

    def show_success_message(self, message):
        """Display success message"""
        success_dialog = QMessageBox(self)
        success_dialog.setIcon(QMessageBox.Icon.Information)
        success_dialog.setWindowTitle("Success")
        success_dialog.setText(message)
        success_dialog.setStyleSheet("""
            QMessageBox {
                background-color: #2c3036;
                color: #ffffff;
            }
            QMessageBox QLabel {
                color: #ffffff;
            }
            QMessageBox QPushButton {
                background-color: #2ecc71;
                color: white;
                border-radius: 5px;
                padding: 8px;
            }
        """)
        success_dialog.exec()

    def login(self):
        """Handle user login"""
        username = self.username_input.text()
        password = self.password_input.text()
    
        data = {
            'username': username,
            'password': password
        }
    
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

    def check_balance(self):
        """Fetch and display user balance"""
        if not self.current_user:
            self.show_error_message("Please login first.")
            return
    
        response = self._make_request(f'/account/{self.current_user}')
        if response:
            balance = response.get('balance', 0)
            self.balance_label.setText(f"Balance: ${balance:.2f}")

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
                    self.check_balance()
            except ValueError:
                self.show_error_message("Invalid amount entered.")

    def fetch_market_data(self):
        """Fetch and display current market data"""
        response = self._make_request('/market_data')
        if response and isinstance(response, list):  # Check if response is a list
            self.market_data = response
            self.market_table.setRowCount(0)  # Clear existing data
            self.buy_asset_combo.clear()     # Clear combo box options
            self.sell_asset_combo.clear()
            self.trend_asset_combo.clear()

            for asset in response[:50]:  # Display up to 50 assets
                row_position = self.market_table.rowCount()
                self.market_table.insertRow(row_position)
                self.market_table.setItem(row_position, 0, QTableWidgetItem(asset['name']))
                self.market_table.setItem(row_position, 1, QTableWidgetItem(asset['symbol'].upper()))
                self.market_table.setItem(row_position, 2, QTableWidgetItem(f"${asset['current_price']:.2f}"))
                self.market_table.setItem(row_position, 3, QTableWidgetItem(f"${asset.get('market_cap', 'N/A')}"))

                # Populate combo boxes for trading and trends
                self.buy_asset_combo.addItem(asset['name'])
                self.sell_asset_combo.addItem(asset['name'])
                self.trend_asset_combo.addItem(asset['name'])

            self.market_table.resizeColumnsToContents()
            self.show_success_message("Market data fetched successfully!")
        else:
            self.show_error_message("Failed to fetch market data.")

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

            self.portfolio_table.resizeColumnsToContents()

    def buy_asset(self):
        """Handle buying an asset"""
        if not self.current_user:
            self.show_error_message("Please login first.")
            return

        asset_name = self.buy_asset_combo.currentText()
        try:
            quantity = float(self.buy_quantity_input.text())
            if quantity <= 0:
                self.show_error_message("Quantity must be greater than 0.")
                return
            
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
        """Sell an asset and gain virtual money"""
        try:
            asset_name = self.sell_asset_combo.currentText()  # Use the combo box for asset name
            quantity = float(self.sell_quantity_input.text())  # Use the QLineEdit for quantity

            if quantity <= 0:
                self.show_error_message("Quantity must be greater than zero.")
                return

            response = requests.post(f"{self.base_url}/trade/sell", json={
                "username": self.current_user,
                "asset_name": asset_name,
                "quantity": quantity
            })

            if response.status_code == 200:
                data = response.json()
                self.show_success_message(data["message"])
                self.view_portfolio()  # Refresh the portfolio view after selling
            else:
                data = response.json()
                self.show_error_message(data.get("message", "Error selling asset."))

        except ValueError:
            self.show_error_message("Invalid quantity.")
        except Exception as e:
            self.show_error_message(f"Error: {str(e)}")

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
