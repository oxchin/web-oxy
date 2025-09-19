#!/usr/bin/env python3
"""
Update Crypto Assets List with Real Top 100 from CoinMarketCap
"""

# Real top 100 cryptocurrencies from CoinMarketCap API (Live data)
TOP_100_CRYPTO_SYMBOLS = [
    "BTC", "ETH", "XRP", "USDT", "BNB", "SOL", "USDC", "DOGE", "TRX", "ADA",
    "HYPE", "LINK", "AVAX", "USDe", "SUI", "XLM", "BCH", "HBAR", "LTC", "LEO",
    "CRO", "TON", "SHIB", "DOT", "UNI", "WLFI", "MNT", "XMR", "DAI", "ENA",
    "AAVE", "PEPE", "OKB", "NEAR", "BGB", "TAO", "IP", "ONDO", "APT", "ETC",
    "WLD", "PI", "ARB", "POL", "USD1", "ICP", "PUMP", "M", "MYX", "PENGU",
    "KAS", "VET", "ATOM", "ALGO", "RENDER", "KCS", "SEI", "BONK", "SKY", "FIL",
    "FLR", "TRUMP", "IMX", "JUP", "FET", "OP", "INJ", "GT", "XDC", "TIA",
    "PYUSD", "SPX", "QNT", "STX", "FDUSD", "LDO", "ASTER", "AERO", "CRV", "PAXG",
    "GRT", "PYTH", "KAIA", "CAKE", "FLOKI", "CFX", "XAUt", "WIF", "ENS", "S",
    "FARTCOIN", "RAY", "PENDLE", "VIRTUAL", "NEXO", "THETA", "XTZ", "GALA", "ZEC", "ETHFI"
]

def generate_crypto_assets_code():
    """Generate the Python code for crypto assets set"""
    print("# Real top 100 crypto assets from CoinMarketCap (Live data)")
    print("self.crypto_assets = {")
    
    # Group by 10 for better readability
    for i in range(0, len(TOP_100_CRYPTO_SYMBOLS), 10):
        group = TOP_100_CRYPTO_SYMBOLS[i:i+10]
        line = '    "' + '", "'.join(group) + '"'
        if i + 10 < len(TOP_100_CRYPTO_SYMBOLS):
            line += ","
        print(line)
    
    print("}")
    print(f"\n# Total: {len(TOP_100_CRYPTO_SYMBOLS)} cryptocurrencies")
    print("# Updated with live CoinMarketCap data")

if __name__ == "__main__":
    generate_crypto_assets_code()
