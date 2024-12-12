import sys
import requests
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from datetime import datetime
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QStackedWidget, QPushButton, QLabel, QLineEdit, QMessageBox, 
    QTableWidget, QTableWidgetItem, QDialog, QFormLayout, 
    QComboBox, QDialogButtonBox, QScrollArea, QGraphicsDropShadowEffect
)
from PyQt6.QtGui import QColor

# Color Palette
# Dark Mode Color Scheme
BACKGROUND_DARKEST = "#121212"  # Almost black, very dark background
BACKGROUND_DARK = "#1E1E1E"     # Slightly lighter dark background
BACKGROUND_MEDIUM = "#2C2C2C"   # Medium dark background
BACKGROUND_LIGHT = "#3A3A3A"    # Lighter dark background

# Accent Colors
PRIMARY_ACCENT = "#00B4D8"      # Vibrant cyan/blue
SECONDARY_ACCENT = "#0077B6"    # Deep blue
HIGHLIGHT_ACCENT = "#90E0EF"    # Light cyan
SUCCESS_COLOR = "#2ECC71"       # Bright green
WARNING_COLOR = "#F39C12"       # Amber
ERROR_COLOR = "#E74C3C"         # Bright red

# Text Colors
TEXT_PRIMARY = "#E0E0E0"        # Light gray
TEXT_SECONDARY = "#A0A0A0"      # Medium gray
TEXT_MUTED = "#6C6C6C"          # Dark gray

# Recommended Fonts
# Modern, clean fonts that work well in digital interfaces
FONT_PRIMARY = "AnekDevanagari-Regular"     # Clean, modern sans-serif
FONT_SECONDARY = "Montserrat"        # Very modern, tech-friendly
FONT_MONO = "Inter"    # For code or numeric displays

class StyledButton(QPushButton):
    """Custom styled button for a more modern look"""
    def __init__(self, text, primary=False):
        super().__init__(text)
        self.setMinimumHeight(40)
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {PRIMARY_ACCENT if primary else SECONDARY_ACCENT};
                color: {TEXT_PRIMARY};
                border-radius: 6px;
                font-weight: bold;
                padding: 8px;
                font-family: '{FONT_PRIMARY}', sans-serif;
                font-size: 14px;
            }}
            QPushButton:hover {{
                background-color: {HIGHLIGHT_ACCENT};
                color: {BACKGROUND_DARKEST};
            }}
            QPushButton:pressed {{
                background-color: {SECONDARY_ACCENT};
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
        """Set up a modern, sleek dark theme for the application"""
        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: {BACKGROUND_DARKEST};
                color: {TEXT_PRIMARY};
                font-family: '{FONT_PRIMARY}', sans-serif;
            }}
        
            QWidget {{
                background-color: {BACKGROUND_DARK};
                color: {TEXT_PRIMARY};
                font-family: '{FONT_PRIMARY}', sans-serif;
            }}
        
            QLabel {{
                color: {TEXT_PRIMARY};
                font-family: '{FONT_PRIMARY}', sans-serif;
            }}
        
            QLineEdit {{
                background-color: {BACKGROUND_MEDIUM};
                color: {TEXT_PRIMARY};
                border: 1px solid {BACKGROUND_LIGHT};
                border-radius: 6px;
                padding: 10px;
                font-family: '{FONT_PRIMARY}', sans-serif;
                font-size: 14px;
            }}
        
            QTableWidget {{
                background-color: {BACKGROUND_DARKEST};
                color: {TEXT_PRIMARY};
                font-family: '{FONT_PRIMARY}', sans-serif;
                gridline-color: {BACKGROUND_MEDIUM};
                border: none;
            }}
        
            QTableWidget::item:nth-child(odd) {{
                background-color: {BACKGROUND_MEDIUM};  /* Color for odd rows */
            }}
        
            QTableWidget::item:nth-child(even) {{
                background-color: {BACKGROUND_LIGHT};  /* Color for even rows */
            }}

            QTableWidget::item {{
                color: {TEXT_PRIMARY};
                padding: 8px;
                border-bottom: 1px solid 
                background-color: {BACKGROUND_MEDIUM};
            }}
        
            QHeaderView::section {{
                background-color: {BACKGROUND_MEDIUM};
                color: {PRIMARY_ACCENT};
                padding: 10px;
                border: none;
                font-weight: bold;
                font-family: '{FONT_PRIMARY}', sans-serif;
            }}
        
            QComboBox {{
                background-color: {BACKGROUND_MEDIUM};
                color: {TEXT_PRIMARY};
                border-radius: 6px;
                padding: 10px;
                font-family: '{FONT_PRIMARY}', sans-serif;
            }}
        
            QComboBox::drop-down {{
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 40px;
                border-left-width: 1px;
                border-left-color: {BACKGROUND_LIGHT};
                border-left-style: solid;
            }}
        
            QScrollArea {{
                border: none;
            }}
        """)
    
    def create_nav_sidebar(self):
        """Create a styled navigation sidebar"""
        nav_widget = QWidget()
        nav_layout = QVBoxLayout()
        nav_widget.setLayout(nav_layout)
        nav_widget.setFixedWidth(250)
        nav_widget.setStyleSheet(f"""
            QWidget {{
                background-color: {BACKGROUND_DARK};
                border-right: 1px solid {BACKGROUND_MEDIUM};
            }}
        """)

        # Logo or title
        logo_label = QLabel("CryptoVault")
        logo_label.setStyleSheet(f"""
            font-size: 28px;
            font-weight: bold;
            color: {PRIMARY_ACCENT};
            padding: 20px;
            text-align: center;
            font-family: '{FONT_PRIMARY}', sans-serif;
        """)
        nav_layout.addWidget(logo_label)

        # Navigation buttons
        nav_buttons = [
            ("Dashboard", self.balance_page),
            ("Market Data", self.market_data_page),
            ("Portfolio", self.portfolio_page),
            ("Trade", self.trade_page),
            ("Transactions", self.transaction_page),
            ("Asset Trends", self.asset_trend_page)
        ]

        for label, page in nav_buttons:
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
        self.login_page.setStyleSheet(f"background-color: {BACKGROUND_DARKEST};")

        login_title = QLabel("Welcome to CryptoVault")
        login_title.setStyleSheet(f"""
            font-size: 32px;
            font-weight: bold;
            color: {PRIMARY_ACCENT};
            margin-bottom: 20px;
            text-align: center;
            font-family: '{FONT_PRIMARY}', sans-serif;
        """)
        login_layout.addWidget(login_title)

        # Login inputs
        username_label = QLabel("Username:")
        username_label.setStyleSheet(f"color: {TEXT_PRIMARY}; font-family: '{FONT_PRIMARY}', sans-serif;")
        self.username_input = QLineEdit()
        self.username_input.setStyleSheet(f"""
            background-color: {BACKGROUND_MEDIUM};
            color: {TEXT_PRIMARY};
            border: 1px solid {BACKGROUND_LIGHT};
            border-radius: 6px;
            padding: 10px;
            font-family: '{FONT_PRIMARY}', sans-serif;
        """)

        password_label = QLabel("Password:")
        password_label.setStyleSheet(f"color: {TEXT_PRIMARY}; font-family: '{FONT_PRIMARY}', sans-serif;")
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setStyleSheet(f"""
            background-color: {BACKGROUND_MEDIUM};
            color: {TEXT_PRIMARY};
            border: 1px solid {BACKGROUND_LIGHT};
            border-radius: 6px;
            padding: 10px;
            font-family: '{FONT_PRIMARY}', sans-serif;
        """)

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
        self.balance_page.setStyleSheet(f"background-color: {BACKGROUND_DARK};")

        # Welcome message label
        self.welcome_label = QLabel("")
        self.welcome_label.setStyleSheet(f"""
            font-size: 24px;
            font-weight: bold;
            color: {PRIMARY_ACCENT};
            margin-bottom: 20px;
            text-align: center;
            font-family: '{FONT_PRIMARY}', sans-serif;
        """)
        balance_layout.addWidget(self.welcome_label)
        balance_layout.addSpacing(20)

        balance_title = QLabel("Account Dashboard")
        balance_title.setStyleSheet(f"""
            font-size: 28px;
            font-weight: bold;
            color: {PRIMARY_ACCENT};
            margin-bottom: 20px;
            font-family: '{FONT_PRIMARY}', sans-serif;
        """)

        self.balance_label = QLabel("Balance: $0.00")
        self.balance_label.setStyleSheet(f"""
            font-size: 20px;
            font-weight: bold;
            color: {SUCCESS_COLOR};
            font-family: '{FONT_PRIMARY}', sans-serif;
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
        self.market_data_page.setStyleSheet(f"background-color: {BACKGROUND_DARK};")

        market_title = QLabel("Market Overview")
        market_title.setStyleSheet(f"""
            font-size: 28px;
            font-weight: bold;
            color: {PRIMARY_ACCENT};
            margin-bottom: 20px;
            font-family: '{FONT_PRIMARY}', sans-serif;
        """)

        fetch_market_btn = StyledButton("Refresh Market Data", primary=True)
        fetch_market_btn.clicked.connect(self.fetch_market_data)
        self.market_table = QTableWidget()
        self.market_table.setStyleSheet(f"""
            background-color: {BACKGROUND_MEDIUM};
            color: {TEXT_PRIMARY};
            font-family: '{FONT_PRIMARY}', sans-serif;
            gridline-color: {BACKGROUND_LIGHT};
        """)
        self.market_table.setColumnCount(4)
        self.market_table.setHorizontalHeaderLabels(["Name", "Symbol", "Current Price", "Market Cap"])
        self.market_table.horizontalHeader().setStyleSheet(f"""
            background-color: {BACKGROUND_DARK};
            color: {PRIMARY_ACCENT};
            font-weight: bold;
        """)
        self.market_table.setAlternatingRowColors(True)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(self.market_table)
        scroll_area.setStyleSheet("border: none;")

        market_data_layout.addWidget(market_title)
        market_data_layout.addWidget(fetch_market_btn)
        market_data_layout.addWidget(scroll_area)

        # Portfolio Page
        self.portfolio_page = QWidget()
        portfolio_layout = QVBoxLayout()
        self.portfolio_page.setLayout(portfolio_layout)
        self.portfolio_page.setStyleSheet(f"background-color: {BACKGROUND_DARK};")

        portfolio_title = QLabel("Your Portfolio")
        portfolio_title.setStyleSheet(f"""
            font-size: 28px;
            font-weight: bold;
            color: {PRIMARY_ACCENT};
            margin-bottom: 20px;
            text-align: center;
            font-family: '{FONT_PRIMARY}', sans-serif;
        """)
        portfolio_layout.addWidget(portfolio_title)

        view_portfolio_btn = StyledButton("Refresh Portfolio", primary=True)
        view_portfolio_btn.clicked.connect(self.view_portfolio)
        portfolio_layout.addWidget(view_portfolio_btn)

        self.portfolio_table = QTableWidget()
        self.portfolio_table.setStyleSheet(f"""
            background-color: {BACKGROUND_MEDIUM};
            color: {TEXT_PRIMARY};
            font-family: '{FONT_PRIMARY}', sans-serif;
            gridline-color: {BACKGROUND_LIGHT};
        """)
        self.portfolio_table.setColumnCount(5)
        self.portfolio_table.setHorizontalHeaderLabels(["Asset", "Quantity", "Current Price", "Total Value", "Profitability"])
        self.portfolio_table.horizontalHeader().setStyleSheet(f"""
            background-color: {BACKGROUND_DARK};
            color: {PRIMARY_ACCENT};
            font-weight: bold;
        """)
    
        portfolio_scroll_area = QScrollArea()
        portfolio_scroll_area.setWidgetResizable(True)
        portfolio_scroll_area.setWidget(self.portfolio_table)
        portfolio_scroll_area.setStyleSheet("border: none;")
    
        portfolio_layout.addWidget(portfolio_scroll_area)

        # Trade Page
        self.trade_page = QWidget()
        trade_layout = QVBoxLayout()
        self.trade_page.setLayout(trade_layout)
        self.trade_page.setStyleSheet(f"background-color: {BACKGROUND_DARK};")

        trade_title = QLabel("Trading Center")
        trade_title.setStyleSheet(f"""
            font-size: 28px;
            font-weight: bold;
            color: {PRIMARY_ACCENT};
            margin-bottom: 20px;
            text-align: center;
            font-family: '{FONT_PRIMARY}', sans-serif;
        """)
        trade_layout.addWidget(trade_title)

        # Create a scroll area for the trade sections
        trade_scroll_area = QScrollArea()
        trade_scroll_area.setWidgetResizable(True)
        trade_scroll_area.setStyleSheet("border: none;")

        # Create a widget to hold the buy and sell sections
        trade_content_widget = QWidget()
        trade_content_layout = QVBoxLayout()
        trade_content_widget.setLayout(trade_content_layout)

        # Initialize buy and sell combo boxes
        self.buy_asset_combo = QComboBox()
        self.sell_asset_combo = QComboBox()

        # Buy Section
        buy_section = QWidget()
        buy_layout = QVBoxLayout()
        buy_section.setLayout(buy_layout)
        buy_section.setStyleSheet(f"background-color: {BACKGROUND_MEDIUM}; border-radius: 10px; padding: 15px;")

        buy_section_title = QLabel("Buy Cryptocurrency")
        buy_section_title.setStyleSheet(f"""
            font-size: 22px;
            font-weight: bold;
            color: {SECONDARY_ACCENT};
            margin-bottom: 15px;
            font-family: '{FONT_PRIMARY}', sans-serif;
        """)
        buy_layout.addWidget(buy_section_title)

        # Buy Asset Combo
        buy_asset_label = QLabel("Select Asset:")
        buy_asset_label.setStyleSheet(f"color: {TEXT_PRIMARY}; font-family: '{FONT_PRIMARY}', sans-serif;")
        self.buy_asset_combo = QComboBox()
        self.buy_asset_combo.setStyleSheet(f"""
            background-color: {BACKGROUND_LIGHT};
            color: {TEXT_PRIMARY};
            border-radius: 6px;
            padding: 8px;
            font-family: '{FONT_PRIMARY}', sans-serif;
        """)

        # Buy Quantity Input
        buy_quantity_label = QLabel("Quantity:")
        buy_quantity_label.setStyleSheet(f"color: {TEXT_PRIMARY}; font-family: '{FONT_PRIMARY}', sans-serif;")
        self.buy_quantity_input = QLineEdit()
        self.buy_quantity_input.setStyleSheet(f"""
            background-color: {BACKGROUND_LIGHT};
            color: {TEXT_PRIMARY};
            border-radius: 6px;
            padding: 8px;
            font-family: '{FONT_PRIMARY}', sans-serif;
        """)
        self.buy_quantity_input.setPlaceholderText("Enter quantity to buy")

        # Buy Button
        buy_btn = StyledButton("Buy Asset", primary=True)
        buy_btn.clicked.connect(self.buy_asset)

        buy_layout.addWidget(buy_asset_label)
        buy_layout.addWidget(self.buy_asset_combo)
        buy_layout.addWidget(buy_quantity_label)
        buy_layout.addWidget(self.buy_quantity_input)
        buy_layout.addWidget(buy_btn)

        trade_content_layout.addWidget(buy_section)

        # Sell Section
        sell_section = QWidget()
        sell_layout = QVBoxLayout()
        sell_section.setLayout(sell_layout)
        sell_section.setStyleSheet(f"background-color: {BACKGROUND_MEDIUM}; border-radius: 10px; padding: 15px;")

        sell_section_title = QLabel("Sell Cryptocurrency")
        sell_section_title.setStyleSheet(f"""
            font-size: 22px;
            font-weight: bold;
            color: {SECONDARY_ACCENT};
            margin-bottom: 15px;
            font-family: '{FONT_PRIMARY}', sans-serif;
        """)
        sell_layout.addWidget(sell_section_title)

        # Sell Asset Combo
        sell_asset_label = QLabel("Select Asset:")
        sell_asset_label.setStyleSheet(f"color: {TEXT_PRIMARY}; font-family: '{FONT_PRIMARY}', sans-serif;")
        self.sell_asset_combo = QComboBox()
        self.sell_asset_combo.setStyleSheet(f"""
            background-color: {BACKGROUND_LIGHT};
            color: {TEXT_PRIMARY};
            border-radius: 6px;
            padding: 8px;
            font-family: '{FONT_PRIMARY}', sans-serif;
        """)

        # Sell Quantity Input
        sell_quantity_label = QLabel("Quantity:")
        sell_quantity_label.setStyleSheet(f"color: {TEXT_PRIMARY}; font-family: '{FONT_PRIMARY}', sans-serif;")
        self.sell_quantity_input = QLineEdit()
        self.sell_quantity_input.setStyleSheet(f"""
            background-color: {BACKGROUND_LIGHT};
            color: {TEXT_PRIMARY};
            border-radius: 6px;
            padding: 8px;
            font-family: '{FONT_PRIMARY}', sans-serif;
        """)
        self.sell_quantity_input.setPlaceholderText("Enter quantity to sell")

        # Sell Button
        sell_btn = StyledButton("Sell Asset", primary=True)
        sell_btn.clicked.connect(self.sell_asset)

        sell_layout.addWidget(sell_asset_label)
        sell_layout.addWidget(self.sell_asset_combo)
        sell_layout.addWidget(sell_quantity_label)
        sell_layout.addWidget(self.sell_quantity_input)
        sell_layout.addWidget(sell_btn)

        trade_content_layout.addWidget(sell_section)

        # Trade Content Widget as a scrollabe area's widget
        trade_scroll_area.setWidget(trade_content_widget)

        # Scroll area being added to the main trade layout
        trade_layout.addWidget(trade_scroll_area)

        # Asset Trend Page
        self.asset_trend_page = QWidget()
        trend_layout = QVBoxLayout()
        self.asset_trend_page.setLayout(trend_layout)
        self.asset_trend_page.setStyleSheet(f"background-color: {BACKGROUND_DARK};")

        trend_title = QLabel("Asset Price Trends")
        trend_title.setStyleSheet(f"""
            font-size: 28px;
            font-weight: bold;
            color: {PRIMARY_ACCENT};
            margin-bottom: 20px;
            text-align: center;
            font-family: '{FONT_PRIMARY}', sans-serif;
        """)
        trend_layout.addWidget(trend_title)

        # Asset Selection Combo
        trend_asset_label = QLabel("Select Asset:")
        trend_asset_label.setStyleSheet(f"color: {TEXT_PRIMARY}; font-family: '{FONT_PRIMARY}', sans-serif;")
        self.trend_asset_combo = QComboBox()
        self.trend_asset_combo.setStyleSheet(f"""
            background-color: {BACKGROUND_MEDIUM};
            color: {TEXT_PRIMARY};
            border-radius: 6px;
            padding: 8px;
            font-family: '{FONT_PRIMARY}', sans-serif;
        """)

        # View Trend Button
        view_trend_btn = StyledButton("View Asset Trend", primary=True)
        view_trend_btn.clicked.connect(self.view_asset_trend)

        # Matplotlib Figure for Trend Visualization
        self.trend_figure = Figure(figsize=(10, 6), dpi=100)
        self.trend_canvas = FigureCanvas(self.trend_figure)
        self.trend_canvas.setStyleSheet("background-color: white;")

        trend_layout.addWidget(trend_asset_label)
        trend_layout.addWidget(self.trend_asset_combo)
        trend_layout.addWidget(view_trend_btn)
        trend_layout.addWidget(self.trend_canvas)                      

        # Add additional components for displaying trends
        self.trend_display = QLabel("Trend data will be displayed here.")
        trend_layout.addWidget(self.trend_display)

        # Connect the asset selection to a method that fetches and displays trends
        self.trend_asset_combo.currentIndexChanged.connect(self.display_asset_trend)

        # Transaction History Page
        self.transaction_page = QWidget()
        transaction_layout = QVBoxLayout()
        self.transaction_page.setLayout(transaction_layout)
        self.transaction_page.setStyleSheet(f"background-color: {BACKGROUND_DARK};")

        transaction_title = QLabel("Transaction History")
        transaction_title.setStyleSheet(f"""
            font-size: 28px;
            font-weight: bold;
            color: {PRIMARY_ACCENT};
            margin-bottom: 20px;
            text-align: center;
            font-family: '{FONT_PRIMARY}', sans-serif;
        """)
        transaction_layout.addWidget(transaction_title)

        # Transaction History Table
        self.transaction_table = QTableWidget()
        self.transaction_table.setStyleSheet(f"""
            background-color: {BACKGROUND_MEDIUM};
            color: {TEXT_PRIMARY};
            font-family: '{FONT_PRIMARY}', sans-serif;
            gridline-color: {BACKGROUND_LIGHT};
        """)
        self.transaction_table.setColumnCount(4)
        self.transaction_table.setHorizontalHeaderLabels(["Timestamp", "Type", "Amount", "Asset"])
        self.transaction_table.horizontalHeader().setStyleSheet(f"""
            background-color: {BACKGROUND_DARK};
            color: {PRIMARY_ACCENT};
            font-weight: bold;
        """)

        # View Transaction History Button
        view_transactions_btn = StyledButton("Refresh Transaction History", primary=True)
        view_transactions_btn.clicked.connect(self.view_transaction_history)

        # Scroll Area for Transaction Table
        transaction_scroll_area = QScrollArea()
        transaction_scroll_area.setWidgetResizable(True)
        transaction_scroll_area.setWidget(self.transaction_table)
        transaction_scroll_area.setStyleSheet("border: none;")

        transaction_layout.addWidget(view_transactions_btn)
        transaction_layout.addWidget(transaction_scroll_area)
        
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

    def create_asset_trend_page(self):
        """Create the asset trend page with embedded Matplotlib graph"""
        page = QWidget()
        layout = QVBoxLayout()

        self.canvas = FigureCanvas(Figure())  # Create a Matplotlib canvas
        layout.addWidget(self.canvas)  # Add the canvas to the layout

        self.plot_button = StyledButton("Show Asset Trend", primary=True)
        self.plot_button.clicked.connect(self.view_asset_trend)  # Connect button to the plotting function
        layout.addWidget(self.plot_button)

        page.setLayout(layout)  # Set the layout for the page
        return page

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
            response = self._make_request(f'/historical_prices/{asset_name}', method='get')
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
        """Display error message with modern styling"""
        error_dialog = QMessageBox(self)
        error_dialog.setIcon(QMessageBox.Icon.Critical)
        error_dialog.setWindowTitle("Error")
        error_dialog.setText(message)
        error_dialog.setStyleSheet(f"""
            QMessageBox {{
                background-color: {BACKGROUND_DARK};
                color: {TEXT_PRIMARY};
                font-family: '{FONT_PRIMARY}', sans-serif;
            }}
            QMessageBox QLabel {{
                color: {TEXT_PRIMARY};
                font-family: '{FONT_PRIMARY}', sans-serif;
            }}
            QMessageBox QPushButton {{
                background-color: {ERROR_COLOR};
                color: {TEXT_PRIMARY};
                border-radius: 6px;
                padding: 8px;
                font-family: '{FONT_PRIMARY}', sans-serif;
                min-width: 80px;
            }}
            QMessageBox QPushButton:hover {{
                background-color: {SECONDARY_ACCENT};
            }}
        """)
        error_dialog.exec()

    def show_success_message(self, message):
        """Display success message with modern styling"""
        success_dialog = QMessageBox(self)
        success_dialog.setIcon(QMessageBox.Icon.Information)
        success_dialog.setWindowTitle("Success")
        success_dialog.setText(message)
        success_dialog.setStyleSheet(f"""
            QMessageBox {{
                background-color: {BACKGROUND_DARK};
                color: {TEXT_PRIMARY};
                font-family: '{FONT_PRIMARY}', sans-serif;
            }}
            QMessageBox QLabel {{
                color: {TEXT_PRIMARY};
                font-family: '{FONT_PRIMARY}', sans-serif;
            }}
            QMessageBox QPushButton {{
                background-color: {SUCCESS_COLOR};
                color: {TEXT_PRIMARY};
                border-radius: 6px;
                padding: 8px;
                font-family: '{FONT_PRIMARY}', sans-serif;
                min-width: 80px;
            }}
            QMessageBox QPushButton:hover {{
                background-color: {PRIMARY_ACCENT};
            }}
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
        
            # Directly set the welcome message
            self.welcome_label.setText(f"Welcome back, {username}!")
        
            # Fetch balance
            balance_response = self._make_request(f'/account/{username}')
            if balance_response:
                balance = balance_response.get('balance', 0)
                self.balance_label.setText(f"Balance: ${balance:.2f}")
        
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
        
            # Add welcome message
            self.welcome_label.setText(f"Welcome back, {self.current_user}!")

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

            for asset in response[:100]:  # Display up to 100 assets
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
            
                # Calculate total value manually if not provided
                current_price = holding.get('current_price', 0)
                quantity = holding.get('quantity', 0)
                total_value = current_price * quantity
            
                self.portfolio_table.setItem(row_position, 3, QTableWidgetItem(f"${total_value:.2f}"))
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
        # Clear any existing plots
        self.trend_figure.clear()

        # Get selected asset
        asset_name = self.trend_asset_combo.currentText()
        if not asset_name:
            self.show_error_message("Please select an asset.")
            return

        # Clear the trend display label
        self.trend_display.setText("")  # Clear any previous messages

        try:
            # Fetch historical prices
            response = self._make_request(f'/historical_prices/{asset_name}')
            if not response or not response.get('historical_prices'):
                self.trend_display.setText("")  # Ensure nothing is displayed
                return

            # Process historical prices
            prices = response['historical_prices']
            timestamps = [datetime.fromisoformat(entry['timestamp']) for entry in prices]
            price_values = [entry['price'] for entry in prices]

            # Create subplot
            ax = self.trend_figure.add_subplot(111)
            ax.clear()
            ax.plot(timestamps, price_values, label=asset_name, color=PRIMARY_ACCENT)
            ax.set_title(f"{asset_name} Price Trend", color=TEXT_PRIMARY)
            ax.set_xlabel("Timestamp", color=TEXT_PRIMARY)
            ax.set_ylabel("Price ($)", color=TEXT_PRIMARY)
            ax.tick_params(axis='x', rotation=45, colors=TEXT_PRIMARY)
            ax.tick_params(axis='y', colors=TEXT_PRIMARY)
            ax.spines['bottom'].set_color(TEXT_PRIMARY)
            ax.spines['top'].set_color(TEXT_PRIMARY) 
            ax.spines['right'].set_color(TEXT_PRIMARY)
            ax.spines['left'].set_color(TEXT_PRIMARY)
            ax.legend(labelcolor=TEXT_PRIMARY)

            # Set the figure background color to dark
            self.trend_figure.patch.set_facecolor(BACKGROUND_DARK)  # Set figure background color
            self.trend_canvas.setStyleSheet("background-color: " + BACKGROUND_DARK + ";")  # Set canvas background color

            # Adjust layout and draw
            self.trend_figure.tight_layout()
            self.trend_canvas.draw()

        except Exception as e:
            self.show_error_message(f"Error displaying trend: {str(e)}")

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
