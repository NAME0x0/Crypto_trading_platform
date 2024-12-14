---
# Crypto Trading Platform

## Description

The **Crypto Trading Platform** is a fully functional application designed to manage cryptocurrency trading and portfolio management. The platform allows users to create accounts, manage their funds, view real-time market data, and perform buy/sell operations with various cryptocurrencies. This project was developed in multiple phases, starting from a command-line interface (CLI), moving to a client-server architecture, and finally implementing a modern graphical user interface (GUI) using PyQt6. 

Key features include:
- Account management (creating accounts, depositing and withdrawing funds).
- Portfolio management (viewing and managing cryptocurrency assets).
- Real-time market data updates and trade execution.
- Interactive charts and asset price trends visualization using Matplotlib.

## Features

- **Account Creation & Login**: Users can create an account, log in, and manage their balances.
- **Portfolio Management**: Users can add and remove assets, view the current value of their portfolio, and track their holdings.
- **Real-Time Market Data**: The platform fetches the latest cryptocurrency prices and updates the user interface with real-time data.
- **Interactive Charts**: Users can view interactive price trend charts of assets.
- **Buy/Sell Functionality**: Users can purchase or sell assets based on live market data.

## Requirements

To run this project locally, ensure you have the following installed:

- Python 3.x
- pip (Python package installer)

### Install Dependencies

To install the required dependencies, run the following command:

```bash
pip install -r requirements.txt
```

### Dependencies List

The required dependencies are listed in the `requirements.txt` file. Key dependencies include:
- **Flask**: Web framework for the backend (API handling).
- **Flask-Cors**: CORS handling for the backend.
- **requests**: To make HTTP requests for real-time data fetching.
- **PyQt6**: GUI framework for the client-side interface.
- **matplotlib**: For real-time market charts and data visualization.
- **SQLAlchemy**: ORM for database handling.

## Project Structure

The project is organized as follows:

```
/CryptoTradingPlatform
    ├── /client
        ├── client_CLI.py     # Command-line interface client
        ├── client_GUI.py     # Graphical user interface client
    ├── /server
        ├── server.py         # Flask server for API handling
    ├── /assets
        ├── assets.py         # Data handling and asset management
    ├── /models
        ├── models.py         # Database models (for SQLAlchemy)
    ├── requirements.txt      # Project dependencies
    ├── README.md             # Project description and setup instructions
```

## Setup & Running the Project

### 1. Clone the repository:

```bash
git clone https://github.com/NAME0x0/CryptoTradingPlatform.git
cd CryptoTradingPlatform
```

### 2. Install dependencies:

```bash
pip install -r requirements.txt
```

### 3. Start the server:

```bash
python server/server.py
```

### 4. Run the client:

- **For CLI client:**

```bash
python client/client_CLI.py
```

- **For GUI client (recommended for better user experience):**

```bash
python client/client_GUI.py
```

## How It Works

- The **server** handles all the backend logic, including account management, transactions, and market data retrieval.
- The **client** (either CLI or GUI) sends HTTP requests to the server for various actions such as depositing funds, buying assets, and viewing portfolios.
- Market data is fetched periodically from external sources and is displayed on the client-side interface.
- The platform's backend ensures that users' portfolios and transaction histories are stored persistently in a database.

## Troubleshooting

- **Server Connection**: Ensure the server is running before attempting to interact with the client. If you encounter connection issues, make sure there are no network/firewall restrictions blocking the server-client communication.
- **API Errors**: If you receive errors while making requests from the client, check the server logs for any issues with the API routes or database connections.

## Future Improvements

This platform can be further enhanced with the following features:
- **Authentication**: Implement token-based authentication for secure login.
- **Advanced Trading Features**: Include automated trading strategies, additional charting tools (e.g., candlestick charts), and real-time alerts for price changes.
- **Security Enhancements**: Implement encrypted communications between the client and server, and secure database handling.

## Contributing

Feel free to fork this project and submit pull requests for any improvements or bug fixes you might suggest. If you have an idea for a new feature or enhancement, open an issue in the GitHub repository to discuss it.

## License

This project is open-source and available under the MIT License.

---

## References

- Python Documentation: [https://docs.python.org/](https://docs.python.org/)
- Flask Documentation: [https://flask.palletsprojects.com/](https://flask.palletsprojects.com/)
- PyQt6 Documentation: [https://riverbankcomputing.com/software/pyqt/](https://riverbankcomputing.com/software/pyqt/)

---
