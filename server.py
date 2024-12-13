import os
import sqlite3
import requests
import time
import logging
from flask import Flask, request, jsonify
from flask_cors import CORS

# Logging Configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('server.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Single Database Configuration
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_PATH = os.path.join(BASE_DIR, 'database.db')

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Configuration
CRYPTO_API_URL = "https://api.coingecko.com/api/v3/coins/markets"
API_KEY = "CG-Ew2XmhKD9kogA8bKSYrn8Hah"

# Global variable to store last update time and market data
last_update_time = 0
market_data_cache = None

def init_db():
    """Initialize the database and create necessary tables"""
    try:
        with sqlite3.connect(DATABASE_PATH) as conn:
            cursor = conn.cursor()
            
            # Accounts Table
            cursor.execute(""" 
            CREATE TABLE IF NOT EXISTS accounts (
                username TEXT PRIMARY KEY,
                password TEXT NOT NULL,
                email TEXT UNIQUE,
                balance REAL NOT NULL DEFAULT 1000.0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )""")
            
            # Transactions Table
            cursor.execute(""" 
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                transaction_type TEXT NOT NULL,
                amount REAL NOT NULL,
                asset_name TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )""")
            
            # Assets Table
            cursor.execute(""" 
            CREATE TABLE IF NOT EXISTS assets (
                name TEXT PRIMARY KEY,
                symbol TEXT NOT NULL,
                current_price REAL NOT NULL,
                market_cap REAL NOT NULL,
                last_updated DATETIME DEFAULT CURRENT_TIMESTAMP
            )""")
            
            # Portfolios Table
            cursor.execute(""" 
            CREATE TABLE IF NOT EXISTS portfolios (
                username TEXT NOT NULL,
                asset_name TEXT NOT NULL,
                quantity REAL NOT NULL DEFAULT 0.0,
                avg_purchase_price REAL NOT NULL DEFAULT 0.0,
                PRIMARY KEY (username, asset_name)
            )""")

            # Historical Prices Table
            cursor.execute(""" 
            CREATE TABLE IF NOT EXISTS historical_prices (
                asset_name TEXT NOT NULL,
                price REAL NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (asset_name, timestamp)
            )""")
        
        logger.info(f"Database initialized at {DATABASE_PATH}")
    
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        raise

def authenticate(username, password):
    """Authenticate user credentials"""
    try:
        with sqlite3.connect(DATABASE_PATH) as conn:
            cursor = conn.cursor()
            # Execute query to check if user exists with provided credentials
            cursor.execute(
                "SELECT * FROM accounts WHERE username = ? AND password = ?", 
                (username, password)
            )
            # Return True if user is found, otherwise False
            return cursor.fetchone() is not None
    except sqlite3.Error as e:
        # Log any database errors encountered during authentication
        logger.error(f"Authentication error: {e}")
        return False

def update_market_data():
    global last_update_time, market_data_cache
    current_time = time.time()
    
    # Check if 45 seconds have passed since the last update
    if current_time - last_update_time < 45:
        return market_data_cache  # Return cached data if it's still valid
    
    try:
        headers = {
            "accept": "application/json",
            "x-cg-demo-api-key": API_KEY
        }
        # Request market data from the API
        response = requests.get(CRYPTO_API_URL, headers=headers, params={"vs_currency": "usd"})
        response.raise_for_status()  # Raise an error for bad responses
        market_data = response.json()

        # Update the cache and last update time
        market_data_cache = market_data
        last_update_time = current_time
        
        # Store the data in the database
        with sqlite3.connect(DATABASE_PATH) as conn:
            cursor = conn.cursor()
            for asset in market_data:
                # Insert or replace current asset data
                cursor.execute(""" 
                    INSERT OR REPLACE INTO assets
                    (name, symbol, current_price, market_cap, last_updated) 
                    VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
                """, (
                    asset['name'], 
                    asset['symbol'], 
                    asset['current_price'], 
                    asset['market_cap']
                ))

                # Insert historical price data
                cursor.execute(""" 
                    INSERT INTO historical_prices (asset_name, price)
                    VALUES (?, ?)
                """, (asset['name'], asset['current_price']))
                
            conn.commit()  # Commit changes to the database
        
        return market_data  # Return the updated market data
    except Exception as e:
        logger.error(f"Error updating market data: {e}")
        return market_data_cache  # Return cached data in case of an error

def log_transaction(username, transaction_type, amount, asset_name=None):
    """Log transactions for audit and tracking"""
    # Insert transaction into database
    with sqlite3.connect(DATABASE_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute(""" 
            INSERT INTO transactions 
            (username, transaction_type, amount, asset_name) 
            VALUES (?, ?, ?, ?)
        """, (username, transaction_type, amount, asset_name))
        conn.commit()  # Commit changes to the database

# Account-related Routes
@app.route('/create_account', methods=['POST'])
def create_account():
    """Create a new user account"""
    try:
        data = request.json
        username = data.get('username')
        password = data.get('password')
        email = data.get('email')

        # Create a new account in the database
        with sqlite3.connect(DATABASE_PATH) as conn:
            cursor = conn.cursor()
            try:
                cursor.execute(
                    """ 
                    INSERT INTO accounts (username, password, email) VALUES (?, ?, ?) 
                    """, 
                    (username, password, email)
                )
                conn.commit()
                logger.info(f"Account created for username: {username}")
                return jsonify({"message": f"Account for {username} created successfully."}), 201
            except sqlite3.IntegrityError:
                # Handle duplicate username or email
                logger.warning(f"Account creation failed: Username or email already exists - {username}")
                return jsonify({"message": "Username or email already exists!"}), 400
    except Exception as e:
        # Handle any other exceptions
        logger.error(f"Account creation error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/login', methods=['POST'])
def login():
    """
    User  login endpoint
    Returns a JSON response indicating success or failure of login
    """
    try:
        data = request.json
        username = data.get('username')
        password = data.get('password')

        if authenticate(username, password):
            # Successful login
            logger.info(f"Successful login for username: {username}")
            return jsonify({
                "message": "Login successful.", 
                "username": username
            }), 200
        else:
            # Invalid credentials
            logger.warning(f"Failed login attempt for username: {username}")
            return jsonify({"message": "Invalid credentials."}), 401
    except Exception as e:
        # Handle any unexpected errors
        logger.error(f"Login error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/account/<username>', methods=['GET'])
def get_account(username):
    """Retrieve user account balance"""
    # Check for invalid or insufficient username
    if not username or len(username) < 3:
        return jsonify({"error": "Invalid username."}), 400

    try:
        # Connect to the database
        with sqlite3.connect(DATABASE_PATH) as conn:
            # Retrieve the account balance
            cursor = conn.cursor()
            cursor.execute("SELECT balance FROM accounts WHERE username = ?", (username,))
            account = cursor.fetchone()

            # Return account balance if found
            if account:
                return jsonify({"balance": account[0]}), 200
            else:
                # Return 404 if account not found
                return jsonify({"error": "Account not found."}), 404
    except Exception as e:
        # Handle any unexpected errors
        return jsonify({"error": str(e)}), 500

@app.route('/deposit', methods=['POST'])
def deposit():
    """Deposit virtual funds into user account"""
    try:
        data = request.json
        username = data.get('username')  # Extract username from request
        amount = float(data.get('amount', 0))  # Extract and convert amount

        if amount <= 0:
            # Validate deposit amount
            return jsonify({"message": "Deposit amount must be greater than zero."}), 400

        with sqlite3.connect(DATABASE_PATH) as conn:
            cursor = conn.cursor()
            # Update user balance in database
            cursor.execute("UPDATE accounts SET balance = balance + ? WHERE username = ?", (amount, username))
            if cursor.rowcount == 0:
                # Handle case where account is not found
                return jsonify({"message": "Account not found."}), 404

            conn.commit()  # Commit transaction
            
            # Log the deposit transaction
            log_transaction(username, 'deposit', amount)
            
            # Return success message
            return jsonify({"message": f"Deposited ${amount:.2f}."}), 200
    except ValueError:
        # Handle invalid amount errors
        return jsonify({"message": "Invalid deposit amount."}), 400
    except Exception as e:
        # Handle unexpected errors
        return jsonify({"error": str(e)}), 500

@app.route('/withdraw', methods=['POST'])
def withdraw():
    """Withdraw funds from user account"""
    try:
        data = request.json  # Get JSON data from the request
        username = data.get('username')  # Extract username
        amount = float(data.get('amount', 0))  # Extract and convert amount

        with sqlite3.connect(DATABASE_PATH) as conn:
            cursor = conn.cursor()

            # Retrieve user's current balance
            cursor.execute("SELECT balance FROM accounts WHERE username = ?", (username,))
            balance = cursor.fetchone()[0]

            if balance >= amount:
                # Deduct amount from balance if sufficient
                cursor.execute("UPDATE accounts SET balance = balance - ? WHERE username = ?", (amount, username))
                conn.commit()  # Commit changes to the database
                
                # Log the withdrawal transaction
                log_transaction(username, 'withdraw', amount)

                # Return success message with updated balance
                return jsonify({
                    "message": f"Withdrew ${amount:.2f}.", 
                    "current_balance": balance - amount
                }), 200
            # Return error if funds are insufficient
            return jsonify({"message": "Insufficient funds."}), 400
    except ValueError:
        # Handle invalid amount input
        return jsonify({"message": "Invalid withdrawal amount."}), 400
    except Exception as e:
        # Handle any unexpected errors
        return jsonify({"error": str(e)}), 500

@app.route('/market_data', methods=['GET'])
def get_market_data():
    """Retrieve current market data"""
    try:
        # Update market data before fetching (if required)
        market_data = update_market_data()
        
        # Return market data as JSON
        return jsonify(market_data), 200
    except Exception as e:
        # Handle any exceptions and return error message
        return jsonify({"error": str(e)}), 500


@app.route('/portfolio/add_asset', methods=['POST'])
def add_asset():
    """Add asset to user portfolio"""
    try:
        data = request.json
        username = data.get('username')
        asset_name = data.get('asset_name')
        quantity = float(data.get('quantity', 0))

        with sqlite3.connect(DATABASE_PATH) as conn:
            cursor = conn.cursor()

            # Check if asset exists
            cursor.execute("SELECT current_price FROM assets WHERE name = ?", (asset_name,))
            asset_data = cursor.fetchone()
            if not asset_data:
                return jsonify({"message": "Asset not found."}), 404

            current_price = asset_data[0]
            total_cost = current_price * quantity

            # Check user's balance
            cursor.execute("SELECT balance FROM accounts WHERE username = ?", (username,))
            balance = cursor.fetchone()[0]
            if balance < total_cost:
                return jsonify({"message": "Insufficient funds."}), 400

            # Deduct the cost from the user's balance
            cursor.execute("UPDATE accounts SET balance = balance - ? WHERE username = ?", (total_cost, username))
            conn.commit()

            # Update portfolio
            cursor.execute(""" 
                INSERT INTO portfolios (username, asset_name, quantity, avg_purchase_price)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(username, asset_name)
                DO UPDATE SET 
                    quantity = quantity + ?, 
                    avg_purchase_price = (avg_purchase_price * quantity + ? * ?) / (quantity + ?)
            """, (username, asset_name, quantity, current_price, quantity, current_price, quantity, quantity))
            conn.commit()

            # Log the transaction
            log_transaction(username, 'buy', total_cost, asset_name)

        return jsonify({
            "message": f"Purchased {quantity} units of {asset_name} for ${total_cost:.2f}.",
            "current_balance": balance - total_cost
        }), 200
    except ValueError:
        return jsonify({"message": "Invalid quantity."}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/portfolio/remove_asset', methods=['POST'])
def remove_asset():
    """Remove asset from user portfolio"""
    try:
        data = request.json
        username = data.get('username')
        asset_name = data.get('asset_name')
        quantity = float(data.get('quantity', 0))

        # Check if asset exists in user's portfolio
        with sqlite3.connect(DATABASE_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT quantity FROM portfolios WHERE username = ? AND asset_name = ?", (username, asset_name))
            current_quantity = cursor.fetchone()

            # Asset not found in portfolio
            if current_quantity is None:
                return jsonify({"message": "Asset not found in portfolio."}), 404

            # Check if user has sufficient quantity to remove
            current_quantity = current_quantity[0]
            if current_quantity < quantity:
                return jsonify({"message": "Insufficient quantity to remove."}), 400

            # Remove asset from portfolio
            if current_quantity == quantity:
                cursor.execute("DELETE FROM portfolios WHERE username = ? AND asset_name = ?", (username, asset_name))
            else:
                cursor.execute("UPDATE portfolios SET quantity = quantity - ? WHERE username = ? AND asset_name = ?", (quantity, username, asset_name))
            
            # Commit changes and log transaction
            conn.commit()
            log_transaction(username, 'remove_asset', quantity, asset_name)

        # Return success message
        return jsonify({"message": f"Removed {quantity} units of {asset_name} from portfolio."}), 200
    except ValueError:
        # Invalid quantity
        return jsonify({"message": "Invalid quantity."}), 400
    except Exception as e:
        # Handle any other exceptions
        return jsonify({"error": str(e)}), 500

@app.route('/portfolio/view', methods=['POST'])
def view_portfolio():
    """View user portfolio"""
    try:
        data = request.json
        username = data.get('username')

        with sqlite3.connect(DATABASE_PATH) as conn:
            cursor = conn.cursor()

            # Retrieve user's portfolio holdings
            cursor.execute("SELECT asset_name, quantity, avg_purchase_price FROM portfolios WHERE username = ?", (username,))
            user_portfolio = cursor.fetchall()

            holdings = []
            total_value = 0
            for asset_name, quantity, avg_purchase_price in user_portfolio:
                # Get current market price for each asset
                cursor.execute("SELECT current_price FROM assets WHERE name = ?", (asset_name,))
                current_price = cursor.fetchone()[0]
                # Calculate total value of each holding
                value = current_price * quantity
                # Compile holding details, including profit/loss percentage
                holdings.append({
                    "asset": asset_name,
                    "quantity": quantity,
                    "avg_purchase_price": avg_purchase_price,
                    "current_price": current_price,
                    "value": value,
                    "profit_loss_percentage": ((current_price - avg_purchase_price) / avg_purchase_price * 100) if avg_purchase_price > 0 else 0
                })
                total_value += value

            # Fetch user's total account balance
            cursor.execute("SELECT balance FROM accounts WHERE username = ?", (username,))
            account_balance = cursor.fetchone()[0]

        # Return portfolio summary, including net worth
        return jsonify({
            "holdings": holdings, 
            "total_portfolio_value": total_value,
            "account_balance": account_balance,
            "total_net_worth": total_value + account_balance
        }), 200
    except Exception as e:
        # Handle any errors that occur
        return jsonify({"error": str(e)}), 500

@app.route('/trade/buy', methods=['POST'])
def buy_asset():
    """Buy an asset using virtual money"""
    try:
        # Extract data from request
        data = request.json
        username = data.get('username')
        asset_name = data.get('asset_name')
        quantity = float(data.get('quantity', 0))

        # Validate quantity
        if quantity <= 0:
            return jsonify({"message": "Quantity must be greater than zero."}), 400

        # Connect to database
        with sqlite3.connect(DATABASE_PATH) as conn:
            cursor = conn.cursor()

            # Retrieve asset's current price
            cursor.execute("SELECT current_price FROM assets WHERE name = ?", (asset_name,))
            asset_data = cursor.fetchone()
            if not asset_data:
                return jsonify({"message": "Asset not found."}), 404

            current_price = asset_data[0]
            total_cost = current_price * quantity

            # Check user's balance
            cursor.execute("SELECT balance FROM accounts WHERE username = ?", (username,))
            balance = cursor.fetchone()[0]
            if balance < total_cost:
                return jsonify({"message": "Insufficient funds."}), 400

            # Deduct cost and update portfolio
            cursor.execute("UPDATE accounts SET balance = balance - ? WHERE username = ?", (total_cost, username))
            cursor.execute("""
                INSERT INTO portfolios (username, asset_name, quantity, avg_purchase_price)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(username, asset_name)
                DO UPDATE SET
                    quantity = quantity + ?,
                    avg_purchase_price = (avg_purchase_price * quantity + ? * ?) / (quantity + ?)
            """, (username, asset_name, quantity, current_price, quantity, current_price, quantity, quantity))
            conn.commit()

            # Log transaction
            log_transaction(username, 'buy', total_cost, asset_name)

        # Respond with purchase confirmation
        return jsonify({
            "message": f"Purchased {quantity} units of {asset_name} for ${total_cost:.2f}.",
            "current_balance": balance - total_cost
        }), 200
    except ValueError:
        # Handle invalid quantity
        return jsonify({"message": "Invalid quantity."}), 400
    except Exception as e:
        # Handle unexpected errors
        return jsonify({"error": str(e)}), 500

@app.route('/trade/sell', methods=['POST'])
def sell_asset():
    """Sell an asset and gain virtual money"""
    try:
        data = request.json
        username = data.get('username')
        asset_name = data.get('asset_name')
        quantity = float(data.get('quantity', 0))

        with sqlite3.connect(DATABASE_PATH) as conn:
            cursor = conn.cursor()

            # Validate user's portfolio
            cursor.execute("SELECT quantity, avg_purchase_price FROM portfolios WHERE username = ? AND asset_name = ?", (username, asset_name))
            portfolio_data = cursor.fetchone()

            if portfolio_data is None:
                return jsonify({"message": "Asset not found in portfolio."}), 404

            current_quantity, avg_purchase_price = portfolio_data
            if current_quantity < quantity:
                return jsonify({"message": "Insufficient quantity to sell."}), 400

            # Fetch current market price
            cursor.execute("SELECT current_price FROM assets WHERE name = ?", (asset_name,))
            current_price = cursor.fetchone()[0]
            total_revenue = current_price * quantity

            # Calculate profit/loss
            total_cost = avg_purchase_price * quantity
            profit_loss = total_revenue - total_cost

            # Update user's balance
            cursor.execute("UPDATE accounts SET balance = balance + ? WHERE username = ?", (total_revenue, username))
            conn.commit()

            # Update portfolio
            if current_quantity == quantity:
                # Remove the entire asset if selling all quantity
                cursor.execute("DELETE FROM portfolios WHERE username = ? AND asset_name = ?", (username, asset_name))
            else:
                # Update remaining quantity
                cursor.execute(""" 
                    UPDATE portfolios 
                    SET quantity = quantity - ?, 
                    avg_purchase_price = (avg_purchase_price * quantity - ? * avg_purchase_price) / (quantity - ?)
                    WHERE username = ? AND asset_name = ?
                """, (quantity, quantity, quantity, username, asset_name))
            
            conn.commit()

            # Log transaction
            log_transaction(username, 'sell', total_revenue, asset_name)

        return jsonify({
            "message": f"Sold {quantity} units of {asset_name} at ${current_price:.2f} each.", 
            "total_revenue": total_revenue,
            "profit_loss": profit_loss,
            "profit_loss_percentage": (profit_loss / total_cost) * 100 if total_cost > 0 else 0
        }), 200

    except ValueError:
        return jsonify({"message": "Invalid quantity."}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/transactions/history', methods=['POST'])
def get_transaction_history():
    """Retrieve user's transaction history"""
    try:
        data = request.json  # Get JSON data from the request
        username = data.get('username')  # Extract username

        with sqlite3.connect(DATABASE_PATH) as conn:
            cursor = conn.cursor()
            # Query to fetch the last 50 transactions for the user
            cursor.execute(""" 
                SELECT transaction_type, amount, asset_name, timestamp 
                FROM transactions 
                WHERE username = ? 
                ORDER BY timestamp DESC 
                LIMIT 50
            """, (username,))
            
            transactions = cursor.fetchall()  # Fetch all transaction records
            # Create a list of transactions with relevant details
            transaction_history = [
                {
                    "type": transaction[0],  # Transaction type
                    "amount": transaction[1],  # Transaction amount
                    "asset": transaction[2],  # Asset involved in transaction
                    "timestamp": transaction[3]  # Transaction timestamp
                } for transaction in transactions
            ]

        # Return JSON response with transaction history and total count
        return jsonify({
            "transaction_history": transaction_history,
            "total_transactions": len(transaction_history)
        }), 200

    except Exception as e:
        # Handle any exceptions and return error message
        return jsonify({"error": str(e)}), 500

@app.route('/historical_prices/<asset_name>', methods=['GET'])
def get_historical_prices(asset_name):
    """Retrieve historical prices for a specific asset"""
    try:
        # Connect to the database
        with sqlite3.connect(DATABASE_PATH) as conn:
            # Create a database cursor
            cursor = conn.cursor()

            # Query to fetch the historical prices for the given asset
            # Sort the data by timestamp in ascending order
            cursor.execute("SELECT price, timestamp FROM historical_prices WHERE asset_name = ? ORDER BY timestamp ASC", (asset_name,))

            # Fetch all the historical price records
            historical_data = cursor.fetchall()

            # If no records are found, return a 404 error
            if not historical_data:
                return jsonify({"message": "No historical data found for this asset."}), 404
            
            # Format the data for response
            prices = [{"price": row[0], "timestamp": row[1]} for row in historical_data]
        
        # Return JSON response with the historical prices
        return jsonify({"asset_name": asset_name, "historical_prices": prices}), 200
    except Exception as e:
        # Handle any exceptions and return error message
        return jsonify({"error": str(e)}), 500

@app.route('/trend_analysis/<asset_name>', methods=['GET'])
def analyze_trend(asset_name):
    """Analyze the trend of a specific asset

    Fetches historical prices and calculates price changes between each
    consecutive pair of prices.

    Returns a JSON response with the asset name and a list of
    dictionaries, each containing the timestamp and price change of a
    particular data point in the trend analysis.

    404 error if no historical data is found for the given asset.
    """
    try:
        with sqlite3.connect(DATABASE_PATH) as conn:
            cursor = conn.cursor()
            # Fetch historical prices sorted by timestamp in ascending order
            cursor.execute("SELECT price, timestamp FROM historical_prices WHERE asset_name = ? ORDER BY timestamp ASC", (asset_name,))
            historical_data = cursor.fetchall()

            if not historical_data:
                # No historical data found
                return jsonify({"message": "No historical data found for this asset."}), 404

            # Calculate price changes
            prices = [row[0] for row in historical_data]
            trend = []
            for i in range(len(prices) - 1):
                # Calculate price change between consecutive prices
                change = prices[i + 1] - prices[i]
                trend.append({"timestamp": historical_data[i + 1][1], "change": change})

            return jsonify({"asset_name": asset_name, "trend_analysis": trend}), 200
    except Exception as e:
        # Handle any exceptions and return error message
        return jsonify({"error": str(e)}), 500


# Main application initialization and startup
if __name__ == "__main__":
    # Ensure the database is initialized
    init_db()
    
    # Update market data on startup
    update_market_data()
    
    # Start the Flask application
    app.run(
        host="127.0.0.1", 
        port=5000, 
        debug=True
    )
