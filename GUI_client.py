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
    def __init__(self): # Calling the parent's class constructor with button text
        super().__init__()
        self.base_url = 'http://localhost:5000'  # Base URL for API requests
        self.current_user = None  # Store the current user
        self.market_data = None  # Store retrieved market data
        self.available_assets = []  # Initialize available assets to empty list
        
        # Set up a dark, modern theme with a custom stylesheet
        self.setup_theme()
        
        self.setWindowTitle('CryptoVault Trading Platform')  # Set window title
        self.setGeometry(100, 100, 1400, 900)  # Set window size and position
        
        # Main widget and layout
        main_widget = QWidget()  # Create main widget
        main_layout = QHBoxLayout()  # Set up horizontal layout
        main_widget.setLayout(main_layout)  # Set layout for main widget
        self.setCentralWidget(main_widget)  # Set main widget as central widget
        
        # Stacked widget for main content, which can change
        self.stacked_widget = QStackedWidget()  # Create stacked widget first to hold multiple pages
        main_layout.addWidget(self.stacked_widget)  # Add to main layout
        
        # Create pages with enhanced styling and layout
        self.create_pages()  # Create pages after stacked widget
        
        # Navigation sidebar with improved styling and layout
        nav_widget = self.create_nav_sidebar()  # Now this can access the pages
        main_layout.addWidget(nav_widget)  # Add to main layout
        
        # Start with login page by default
        self.stacked_widget.setCurrentWidget(self.login_page)
        
        # Add a shadow effect to the main window
        shadow = QGraphicsDropShadowEffect(self) # Create shadow effect for main
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 80))
        shadow.setOffset(0, 0)
        self.setGraphicsEffect(shadow)  # Set the shadow effect for the main window
    
    def setup_theme(self):
        """Set up a modern, sleek dark theme for the application
        """
        # Global styles for main window, widgets, labels, and text inputs
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
                background-color: {BACKGROUND_MEDIUM};
            }}
        
            QTableWidget::item:nth-child(even) {{
                background-color: {BACKGROUND_LIGHT};
            }}

            QTableWidget::item {{
                color: {TEXT_PRIMARY};
                padding: 8px;
                border-bottom: 1px solid {BACKGROUND_MEDIUM};
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
        # Create a widget for the navigation sidebar
        nav_widget = QWidget()
        nav_layout = QVBoxLayout()
        nav_widget.setLayout(nav_layout)
        # Set the width of the sidebar
        nav_widget.setFixedWidth(250)
        # Style the sidebar
        nav_widget.setStyleSheet(f"""
            QWidget {{
                background-color: {BACKGROUND_DARK};
                border-right: 1px solid {BACKGROUND_MEDIUM};
            }}
        """)

        # Add a logo or title
        logo_label = QLabel("CryptoVault")
        # Style the logo
        logo_label.setStyleSheet(f"""
            font-size: 28px;
            font-weight: bold;
            color: {PRIMARY_ACCENT};
            padding: 20px;
            text-align: center;
            font-family: '{FONT_PRIMARY}', sans-serif;
        """)
        # Add the logo to the sidebar
        nav_layout.addWidget(logo_label)

        # Create navigation buttons
        nav_buttons = [
            ("Dashboard", self.balance_page),
            ("Market Data", self.market_data_page),
            ("Portfolio", self.portfolio_page),
            ("Trade", self.trade_page),
            ("Transactions", self.transaction_page),
            ("Asset Trends", self.asset_trend_page)
        ]

        # Iterate through the buttons and add them to the sidebar
        for label, page in nav_buttons:
            # Create a styled button
            btn = StyledButton(label)
            # Add an event handler to switch to the page when clicked
            btn.clicked.connect(lambda checked, p=page: self.stacked_widget.setCurrentWidget(p))
            # Add the button to the sidebar
            nav_layout.addWidget(btn)

        # Add some stretch to the sidebar
        nav_layout.addStretch()

        # Create a logout button
        logout_btn = StyledButton("Logout", primary=False)
        # Add an event handler to log out when clicked
        logout_btn.clicked.connect(self.logout)
        # Add the logout button to the sidebar
        nav_layout.addWidget(logout_btn)

        # Add some padding and stretch
        nav_layout.addSpacing(20)

        # Return the sidebar
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

        # Create a Matplotlib canvas
        self.canvas = FigureCanvas(Figure())
        layout.addWidget(self.canvas)  # Add the canvas to the layout

        # Create a button to show the asset trend
        self.plot_button = StyledButton("Show Asset Trend", primary=True)
        self.plot_button.clicked.connect(self.view_asset_trend)  # Connect button to the plotting function
        layout.addWidget(self.plot_button)

        page.setLayout(layout)  # Set the layout for the page
        return page

    def update_sell_quantity_combo(self):
        """Update the sell quantity input based on the selected asset."""
        # Get the currently selected asset name
        asset_name = self.sell_asset_combo.currentText()
        if asset_name:
            # Prepare data to request the user's portfolio
            data = {'username': self.current_user}
            # Make a request to view the portfolio data
            response = self._make_request('/portfolio/view', method='post', data=data)
            if response:
                # Iterate through holdings to find the selected asset
                for holding in response.get('holdings', []):
                    if holding.get('asset') == asset_name:
                        # Update the sell quantity input with the asset's quantity
                        self.sell_quantity_input.setText(str(holding.get('quantity', 0)))
                        break
                else:
                    # Clear the input if the asset is not found in holdings
                    self.sell_quantity_input.clear()

    def display_asset_trend(self):
        """Fetch and display the trend for the selected asset.

        Connected to the 'currentIndexChanged' signal of the asset combo box
        on the asset trend page. When the selected asset changes, this method
        is called to fetch and display the trend data for the selected asset.

        If the asset name is not empty, makes a GET request to the server to
        fetch the trend data. If the request is successful, displays the trend
        data in the label on the asset trend page. Otherwise, displays an error
        message.
        """
        # Get the currently selected asset name
        asset_name = self.trend_asset_combo.currentText()
        if asset_name:
            # Make a GET request to the server to fetch the trend data
            response = self._make_request(f'/historical_prices/{asset_name}', method='get')
            if response:
                # Get the trend data from the response
                trend_data = response.get('trend_data', 'No data available.')
                # Display the trend data in the label on the asset trend page
                self.trend_display.setText(trend_data)
            else:
                # Display an error message if the request is not successful
                self.trend_display.setText("Error fetching trend data.")

    def _make_request(self, endpoint, method='get', data=None):
        """Make an HTTP request to the server

        Args:
            endpoint (str): The endpoint to make the request to
            method (str, optional): The HTTP method to use. Defaults to 'get'.
            data (dict, optional): The data to send in the request body. Defaults to None.

        Returns:
            dict: The JSON response from the server if the request is successful
        """
        try:
            # Construct full URL
            full_url = f"{self.base_url}{endpoint}"
            # Determine HTTP method
            if method.lower() == 'get':
                # Send GET request
                response = requests.get(full_url)
            elif method.lower() == 'post':
                # Send POST request with JSON data
                response = requests.post(full_url, json=data)
            else:
                # Raise error for unsupported methods
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            # Check for HTTP errors
            response.raise_for_status()
            # Return JSON response
            return response.json()
        except requests.exceptions.RequestException as e:
            # Handle request exceptions
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
        # Get username and password from input fields
        username = self.username_input.text()
        password = self.password_input.text()

        # Construct data to send to server
        data = {
            'username': username,
            'password': password
        }

        # Make POST request to /login
        response = self._make_request('/login', method='post', data=data)

        # Successful login
        if response and response.get('message') == 'Login successful.':
            self.current_user = username

            # Directly set the welcome message
            self.welcome_label.setText(f"Welcome back, {username}!")

            # Fetch balance
            balance_response = self._make_request(f'/account/{username}')
            if balance_response:
                balance = balance_response.get('balance', 0)
                self.balance_label.setText(f"Balance: ${balance:.2f}")

            # Switch to balance page
            self.stacked_widget.setCurrentWidget(self.balance_page)
        else:
            # Login failed
            self.show_error_message("Login failed.")

    def create_account(self):
        """Handle account creation

        This function creates a new account by making a POST request to the server
        with the username, password, and email.
        """
        # Retrieve username and password from input fields
        username = self.username_input.text()
        password = self.password_input.text()
    
        # Create a dialog for email input
        dialog = QDialog(self)
        dialog.setWindowTitle("Create Account")
        layout = QFormLayout()
    
        # Email input field
        email_input = QLineEdit()
        layout.addRow("Email:", email_input)
    
        # Dialog buttons for OK and Cancel actions
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(dialog.accept)  # Connect OK button to accept dialog
        buttons.rejected.connect(dialog.reject)  # Connect Cancel button to reject dialog
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addRow(buttons)
    
        # Set the dialog layout
        dialog.setLayout(layout)
    
        # Execute dialog and proceed if accepted
        if dialog.exec() == QDialog.DialogCode.Accepted:
            # Retrieve email from input field
            email = email_input.text()
            # Prepare data payload for account creation request
            data = {
                'username': username,
                'password': password,
                'email': email
            }
        
            # Send account creation request to server
            response = self._make_request('/create_account', method='post', data=data)
            if response:
                # Display success message if account creation is successful
                self.show_success_message(response.get('message', 'Account created successfully!'))

    def check_balance(self):
        """Fetch and display user balance after login."""
        
        # Check if the user is logged in
        if not self.current_user:
            self.show_error_message("Please login first.")
            return
        
        # Make a request to fetch the user's account balance
        response = self._make_request(f'/account/{self.current_user}')
        if response:
            # Retrieve and display the balance
            balance = response.get('balance', 0)
            self.balance_label.setText(f"Balance: ${balance:.2f}")
            
            # Display a welcome message
            self.welcome_label.setText(f"Welcome back, {self.current_user}!")

    def deposit_funds(self):
        """Handle fund deposit

        This function creates a dialog to get the deposit amount from the user.
        It then makes a POST request to the server with the username and deposit
        amount. If the request is successful, it shows a success message and
        updates the balance label on the balance page.
        """
        if not self.current_user:
            # Check if user is logged in
            self.show_error_message("Please login first.")
            return
    
        dialog = QDialog(self)
        dialog.setWindowTitle("Deposit Funds")
        layout = QFormLayout()
    
        # Input field for deposit amount
        amount_input = QLineEdit()
        layout.addRow("Amount:", amount_input)
    
        # Dialog buttons for OK and Cancel actions
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addRow(buttons)
    
        dialog.setLayout(layout)
    
        if dialog.exec() == QDialog.DialogCode.Accepted:
            try:
                # Convert user input to float
                amount = float(amount_input.text())
                data = {
                    'username': self.current_user,
                    'amount': amount
                }
            
                # Send deposit request to server
                response = self._make_request('/deposit', method='post', data=data)
                if response:
                    # Show success message and refresh balance
                    self.show_success_message(response.get('message', 'Deposit successful!'))
                    self.check_balance()
            except ValueError:
                # Handle invalid input
                self.show_error_message("Invalid amount entered.")


    def withdraw_funds(self):
        """Handle fund withdrawal

        This function creates a dialog to get the withdrawal amount from the user.
        It then makes a POST request to the server with the username and withdrawal
        amount. If the request is successful, it shows a success message and
        updates the balance label on the balance page.
        """
        # Check if user is logged in
        if not self.current_user:
            self.show_error_message("Please login first.")
            return
    
        # Create dialog to get withdrawal amount
        dialog = QDialog(self)
        dialog.setWindowTitle("Withdraw Funds")
        layout = QFormLayout()
    
        # Get withdrawal amount from user
        amount_input = QLineEdit()
        layout.addRow("Amount:", amount_input)
    
        # Add buttons to dialog
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addRow(buttons)
    
        # Set layout for dialog
        dialog.setLayout(layout)
    
        # Execute dialog and check if user accepted
        if dialog.exec() == QDialog.DialogCode.Accepted:
            try:
                # Convert input to float
                amount = float(amount_input.text())
                data = {
                    'username': self.current_user,
                    'amount': amount
                }
            
                # Make POST request to server
                response = self._make_request('/withdraw', method='post', data=data)
                if response:
                    # Show success message and update balance label
                    self.show_success_message(response.get('message', 'Withdrawal successful!'))
                    self.check_balance()
            except ValueError:
                # Show error message if input is invalid
                self.show_error_message("Invalid amount entered.")
    
    def view_portfolio(self):
        """Fetch and display user's portfolio"""
        if not self.current_user:
            # User is not logged in, show error message
            self.show_error_message("Please login first.")
            return

        # Send request to server to fetch user portfolio
        data = {'username': self.current_user}
        response = self._make_request('/portfolio/view', method='post', data=data)
        if response:
            # Clear existing data and update balance label
            self.portfolio_table.setRowCount(0)
            total_net_worth = response['total_net_worth']
            self.balance_label.setText(f"Balance: ${response['account_balance']:.2f} (Net Worth: ${total_net_worth:.2f})")

            # Populate the portfolio table
            for holding in response.get('holdings', []):
                row_position = self.portfolio_table.rowCount()
                self.portfolio_table.insertRow(row_position)
                self.portfolio_table.setItem(row_position, 0, QTableWidgetItem(holding.get('asset', 'N/A')))
                self.portfolio_table.setItem(row_position, 1, QTableWidgetItem(str(holding.get('quantity', 0))))
                self.portfolio_table.setItem(row_position, 2, QTableWidgetItem(f"${holding.get('current_price', 0):.2f}"))
                self.portfolio_table.setItem(row_position, 3, QTableWidgetItem(f"${holding.get('total_value', 0):.2f}"))
                self.portfolio_table.setItem(row_position, 4, QTableWidgetItem(f"{holding.get('profit_loss_percentage', 0):.2f}%"))

            # Resize columns to fit data
            self.portfolio_table.resizeColumnsToContents()

    def check_balance(self):
        """Fetch and display user balance
        
        This function sends a GET request to the server to fetch the user's
        current balance. If the request is successful, it updates the balance
        label on the balance page.
        
        If the user is not logged in, it shows an error message.
        """
        if not self.current_user:
            # User is not logged in, show error message
            self.show_error_message("Please login first.")
            return
        
        # Send request to server to fetch user balance
        response = self._make_request(f'/account/{self.current_user}')
        if response:
            # Update balance label on balance page
            balance = response.get('balance', 0)
            self.balance_label.setText(f"Balance: ${balance:.2f}")

    def deposit_funds(self):
        """Handle fund deposit

        This function creates a dialog to get the deposit amount from the user.
        It then makes a POST request to the server with the username and deposit
        amount. If the request is successful, it shows a success message and
        updates the balance label on the balance page.
        """
        if not self.current_user:
            self.show_error_message("Please login first.")
            return

        # Create dialog to get deposit amount from user
        dialog = QDialog(self)
        dialog.setWindowTitle("Deposit Funds")
        layout = QFormLayout()
    
        # Input field for deposit amount
        amount_input = QLineEdit()
        layout.addRow("Amount:", amount_input)
    
        # Dialog buttons for OK and Cancel actions
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addRow(buttons)
    
        dialog.setLayout(layout)
    
        # Execute dialog and process deposit if accepted
        if dialog.exec() == QDialog.DialogCode.Accepted:
            try:
                # Convert user input to float
                amount = float(amount_input.text())
                data = {
                    'username': self.current_user,
                    'amount': amount
                }
            
                # Make POST request to server
                response = self._make_request('/deposit', method='post', data=data)
                if response:
                    # Show success message and update balance label
                    self.show_success_message(response.get('message', 'Deposit successful!'))
                    self.check_balance()
            except ValueError:
                # Show error message if input is invalid
                self.show_error_message("Invalid amount entered.")


    def withdraw_funds(self):
        """Handle fund withdrawal"""
        # Ensure user is logged in
        if not self.current_user:
            self.show_error_message("Please login first.")
            return

        # Create withdrawal dialog
        dialog = QDialog(self)
        dialog.setWindowTitle("Withdraw Funds")
        layout = QFormLayout()

        # Input field for withdrawal amount
        amount_input = QLineEdit()
        layout.addRow("Amount:", amount_input)

        # Dialog buttons for OK and Cancel actions
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addRow(buttons)

        dialog.setLayout(layout)

        # Execute dialog and process withdrawal if accepted
        if dialog.exec() == QDialog.DialogCode.Accepted:
            try:
                # Convert user input to float
                amount = float(amount_input.text())
                # Prepare data for withdrawal request
                data = {
                    'username': self.current_user,
                    'amount': amount
                }

                # Send withdrawal request to server
                response = self._make_request('/withdraw', method='post', data=data)
                if response:
                    # Show success message and refresh balance
                    self.show_success_message(response.get('message', 'Withdrawal successful!'))
                    self.check_balance()
            except ValueError:
                # Handle invalid input
                self.show_error_message("Invalid amount entered.")

    def fetch_market_data(self):
        """Fetch and display current market data"""
        response = self._make_request('/market_data')
        if response and isinstance(response, list):  # Check if response is a list
            # Store response in instance variable
            self.market_data = response
            # Clear existing data in table
            self.market_table.setRowCount(0)
            # Clear combo box options
            self.buy_asset_combo.clear()
            self.sell_asset_combo.clear()
            self.trend_asset_combo.clear()

            # Populate table with up to 100 assets
            for asset in response[:100]:
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

            # Resize table columns to fit content
            self.market_table.resizeColumnsToContents()
            # Show success message
            self.show_success_message("Market data fetched successfully!")
        else:
            # Show error message
            self.show_error_message("Failed to fetch market data.")

    def view_portfolio(self):
        """Fetch and display user's portfolio"""
        if not self.current_user:
            # Show error message if user is not logged in
            self.show_error_message("Please login first.")
            return

        # Prepare data for request
        data = {'username': self.current_user}
        response = self._make_request('/portfolio/view', method='post', data=data)
        
        if response:
            # Clear existing data in table
            self.portfolio_table.setRowCount(0)
            # Update balance label
            total_net_worth = response['total_net_worth']
            self.balance_label.setText(f"Balance: ${response['account_balance']:.2f} (Net Worth: ${total_net_worth:.2f})")

            # Populate table with portfolio holdings
            for holding in response.get('holdings', []):
                # Insert new row
                row_position = self.portfolio_table.rowCount()
                self.portfolio_table.insertRow(row_position)
                
                # Set table items
                self.portfolio_table.setItem(row_position, 0, QTableWidgetItem(holding.get('asset', 'N/A')))
                self.portfolio_table.setItem(row_position, 1, QTableWidgetItem(str(holding.get('quantity', 0))))
                self.portfolio_table.setItem(row_position, 2, QTableWidgetItem(f"${holding.get('current_price', 0):.2f}"))
                
                # Calculate total value manually if not provided
                current_price = holding.get('current_price', 0)
                quantity = holding.get('quantity', 0)
                total_value = current_price * quantity
            
                # Set total value and profit/loss percentage
                self.portfolio_table.setItem(row_position, 3, QTableWidgetItem(f"${total_value:.2f}"))
                self.portfolio_table.setItem(row_position, 4, QTableWidgetItem(f"{holding.get('profit_loss_percentage', 0):.2f}%"))

            # Resize columns to fit data
            self.portfolio_table.resizeColumnsToContents()

    def buy_asset(self):
        """Handle buying an asset"""
        if not self.current_user:
            # Show error message if user is not logged in
            self.show_error_message("Please login first.")
            return

        asset_name = self.buy_asset_combo.currentText()
        try:
            # Get quantity from input field
            quantity = float(self.buy_quantity_input.text())
            
            # Check if quantity is valid
            if quantity <= 0:
                self.show_error_message("Quantity must be greater than 0.")
                return

            # Prepare data for request
            data = {
                'username': self.current_user,
                'asset_name': asset_name,
                'quantity': quantity
            }
            response = self._make_request('/trade/buy', method='post', data=data)
            if response:
                # Show success message and refresh balance
                self.show_success_message(response.get('message', 'Purchase successful!'))
                self.check_balance()
        except ValueError:
            # Invalid input, show error message
            self.show_error_message("Invalid quantity entered.")


    def sell_asset(self):
        """Sell an asset and gain virtual money"""
        try:
            # Get selected asset name and entered quantity
            asset_name = self.sell_asset_combo.currentText()
            quantity = float(self.sell_quantity_input.text())

            # Validate quantity
            if quantity <= 0:
                self.show_error_message("Quantity must be greater than zero.")
                return

            # Make request to sell asset
            response = requests.post(f"{self.base_url}/trade/sell", json={
                "username": self.current_user,
                "asset_name": asset_name,
                "quantity": quantity
            })

            # Check response status code
            if response.status_code == 200:
                # Show success message and refresh portfolio view
                data = response.json()
                self.show_success_message(data["message"])
                self.view_portfolio()
            else:
                # Show error message
                data = response.json()
                self.show_error_message(data.get("message", "Error selling asset."))

        # Catch invalid input and other exceptions
        except ValueError:
            self.show_error_message("Invalid quantity.")
        except Exception as e:
            self.show_error_message(f"Error: {str(e)}")

    def view_transaction_history(self):
        """Fetch and display transaction history"""
        if not self.current_user:
            self.show_error_message("Please login first.")
            return

        # Prepare request data
        data = {'username': self.current_user}
        
        # Send request to fetch transaction history
        response = self._make_request('/transactions/history', method='post', data=data)
        
        # Check if response contains transaction history
        if response and response.get('transaction_history'):
            self.transaction_table.setRowCount(0)  # Clear existing data in the table
            
            # Iterate through each transaction and populate the table
            for transaction in response['transaction_history']:
                row_position = self.transaction_table.rowCount()
                self.transaction_table.insertRow(row_position)
                
                # Set transaction details in the respective columns
                self.transaction_table.setItem(row_position, 0, QTableWidgetItem(transaction['timestamp']))
                self.transaction_table.setItem(row_position, 1, QTableWidgetItem(transaction['type']))
                self.transaction_table.setItem(row_position, 2, QTableWidgetItem(f"${transaction['amount']:.2f}"))
                self.transaction_table.setItem(row_position, 3, QTableWidgetItem(transaction['asset'] or 'N/A'))

    def view_asset_trend(self):
        """Fetch and display asset price trend"""
        self.trend_figure.clear()  # Clear any existing plots

        asset_name = self.trend_asset_combo.currentText()  # Get selected asset
        if not asset_name:
            self.show_error_message("Please select an asset.")
            return

        self.trend_display.setText("")  # Clear the trend display label

        try:
            response = self._make_request(f'/historical_prices/{asset_name}')  # Fetch historical prices
            if not response or not response.get('historical_prices'):
                self.trend_display.setText("")  # Clear display if no data
                return

            prices = response['historical_prices']  # Process historical prices
            timestamps = [datetime.fromisoformat(entry['timestamp']) for entry in prices]
            price_values = [entry['price'] for entry in prices]

            ax = self.trend_figure.add_subplot(111)  # Create subplot
            ax.clear()  # Clear plot area
            ax.plot(timestamps, price_values, label=asset_name, color=PRIMARY_ACCENT)  # Plot data
            ax.set_title(f"{asset_name} Price Trend", color=TEXT_PRIMARY)  # Set plot title
            ax.set_xlabel("Timestamp", color=TEXT_PRIMARY)  # Set x-axis label
            ax.set_ylabel("Price ($)", color=TEXT_PRIMARY)  # Set y-axis label
            ax.tick_params(axis='x', rotation=45, colors=TEXT_PRIMARY)  # Rotate x-axis labels
            ax.tick_params(axis='y', colors=TEXT_PRIMARY)  # Set y-axis tick colors
            ax.spines['bottom'].set_color(TEXT_PRIMARY)  # Style axis spines
            ax.spines['top'].set_color(TEXT_PRIMARY)
            ax.spines['right'].set_color(TEXT_PRIMARY)
            ax.spines['left'].set_color(TEXT_PRIMARY)
            ax.legend(labelcolor=TEXT_PRIMARY)  # Add legend

            self.trend_figure.patch.set_facecolor(BACKGROUND_DARK)  # Set figure background
            self.trend_canvas.setStyleSheet("background-color: " + BACKGROUND_DARK + ";")  # Set canvas background

            self.trend_figure.tight_layout()  # Adjust layout
            self.trend_canvas.draw()  # Render the canvas

        except Exception as e:
            self.show_error_message(f"Error displaying trend: {str(e)}")  # Handle exceptions

    def logout(self):
        """Handle user logout"""
        self.current_user = None  # Clear current user data
        self.username_input.clear()  # Clear username input field
        self.password_input.clear()  # Clear password input field
        self.balance_label.setText("Balance: $0.00")  # Reset balance label
        self.market_table.setRowCount(0)  # Clear market data table
        self.portfolio_table.setRowCount(0)  # Clear portfolio table
        self.transaction_table.setRowCount(0)  # Clear transaction table
        self.stacked_widget.setCurrentWidget(self.login_page)  # Navigate to login page

def main():
    """Main application entry point."""
    # Create application instance
    app = QApplication(sys.argv)
    # Create main window instance
    window = CryptoTradingGUI()
    # Show main window
    window.show()
    # Start application event loop
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
