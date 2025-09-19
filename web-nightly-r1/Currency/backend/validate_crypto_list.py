#!/usr/bin/env python3
"""
Validate Current Crypto Assets List Against Live CoinMarketCap Data
"""

import os
import asyncio
import httpx
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Current crypto assets from SmartConvertEngine
CURRENT_CRYPTO_ASSETS = {
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
}

async def fetch_live_top_100():
    """Fetch live top 100 cryptocurrencies from CoinMarketCap API"""
    cmc_api_key = os.getenv('COINMARKETCAP_API_KEY')
    
    if not cmc_api_key:
        print("❌ COINMARKETCAP_API_KEY not found in environment variables")
        return None
    
    headers = {
        'X-CMC_PRO_API_KEY': cmc_api_key,
        'Accept': 'application/json'
    }
    
    url = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest"
    params = {
        'start': 1,
        'limit': 100,
        'convert': 'USD'
    }
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(url, headers=headers, params=params)
            
            if response.status_code == 200:
                data = response.json()
                live_symbols = [crypto['symbol'] for crypto in data['data']]
                return set(live_symbols)
            else:
                print(f"❌ CoinMarketCap API error: {response.status_code}")
                print(f"Response: {response.text}")
                return None
                
    except Exception as e:
        print(f"❌ Error fetching live data: {e}")
        return None

def compare_crypto_lists(current_set, live_set):
    """Compare current crypto assets with live data"""
    if live_set is None:
        print("❌ Cannot validate - live data unavailable")
        return
    
    print(f"📊 CRYPTO ASSETS VALIDATION REPORT")
    print(f"=" * 50)
    print(f"Current assets count: {len(current_set)}")
    print(f"Live top 100 count: {len(live_set)}")
    
    # Find differences
    missing_from_current = live_set - current_set
    deprecated_in_current = current_set - live_set
    matching_assets = current_set & live_set
    
    print(f"\n✅ Matching assets: {len(matching_assets)}/100")
    print(f"📈 Coverage: {len(matching_assets)}%")
    
    if missing_from_current:
        print(f"\n⚠️  Missing from current list ({len(missing_from_current)}):")
        for symbol in sorted(missing_from_current):
            print(f"   + {symbol}")
    
    if deprecated_in_current:
        print(f"\n🔄 Deprecated in current list ({len(deprecated_in_current)}):")
        for symbol in sorted(deprecated_in_current):
            print(f"   - {symbol}")
    
    if len(matching_assets) >= 95:
        print(f"\n🎉 VALIDATION PASSED: {len(matching_assets)}% coverage is excellent!")
    elif len(matching_assets) >= 90:
        print(f"\n✅ VALIDATION GOOD: {len(matching_assets)}% coverage is acceptable")
    else:
        print(f"\n⚠️  VALIDATION WARNING: {len(matching_assets)}% coverage may need update")
    
    return {
        'matching': len(matching_assets),
        'missing': list(missing_from_current),
        'deprecated': list(deprecated_in_current),
        'coverage_percent': len(matching_assets)
    }

async def main():
    """Main validation function"""
    print("🔍 Validating crypto assets against live CoinMarketCap data...")
    
    live_top_100 = await fetch_live_top_100()
    validation_result = compare_crypto_lists(CURRENT_CRYPTO_ASSETS, live_top_100)
    
    if validation_result and validation_result['coverage_percent'] < 95:
        print(f"\n💡 RECOMMENDATION:")
        print(f"Consider updating crypto assets list to maintain 95%+ coverage")
        print(f"Run update_crypto_list.py to generate updated list")

if __name__ == "__main__":
    asyncio.run(main())
