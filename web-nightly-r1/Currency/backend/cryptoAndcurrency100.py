#!/usr/bin/env python3
"""
Unified Script to Generate Top 100 Crypto and Fiat Currency Lists
Outputs: crypto100.txt and fiat100.txt for SmartConvertEngine
"""

import os
import json
import asyncio
import subprocess
from typing import Dict, List, Set, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class CurrencyListGenerator:
    def __init__(self):
        self.exchange_api_key = os.getenv('EXCHANGE_API_KEY')
        self.cmc_api_key = os.getenv('COINMARKETCAP_API_KEY')
        
    async def fetch_top_100_crypto(self) -> List[str]:
        """Fetch top 100 cryptocurrencies from CoinMarketCap"""
        if not self.cmc_api_key:
            print("⚠️  COINMARKETCAP_API_KEY not found, using fallback list")
            return self.get_fallback_crypto_list()
        
        try:
            import httpx
            headers = {
                'X-CMC_PRO_API_KEY': self.cmc_api_key,
                'Accept': 'application/json'
            }
            
            url = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest"
            params = {'start': 1, 'limit': 100, 'convert': 'USD'}
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(url, headers=headers, params=params)
                
                if response.status_code == 200:
                    data = response.json()
                    crypto_list = [crypto['symbol'] for crypto in data['data']]
                    print(f"✅ Fetched {len(crypto_list)} cryptocurrencies from CoinMarketCap")
                    return crypto_list
                else:
                    print(f"❌ CoinMarketCap API error: {response.status_code}")
                    return self.get_fallback_crypto_list()
                    
        except ImportError:
            print("❌ httpx not available, using fallback crypto list")
            return self.get_fallback_crypto_list()
        except Exception as e:
            print(f"❌ Error fetching crypto data: {e}")
            return self.get_fallback_crypto_list()
    
    def get_fallback_crypto_list(self) -> List[str]:
        """Fallback crypto list (current validated top 100)"""
        return [
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
    
    def fetch_top_100_fiat_curl(self) -> List[str]:
        """Fetch top 100 fiat currencies using curl"""
        if not self.exchange_api_key:
            print("⚠️  EXCHANGE_API_KEY not found, using fallback fiat list")
            return self.get_fallback_fiat_list()
        
        try:
            # Use curl to fetch from ExchangeRates API
            url = f"https://v6.exchangerate-api.com/v6/{self.exchange_api_key}/codes"
            cmd = ['curl', '-s', '--connect-timeout', '10', '--max-time', '30', url]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=35)
            
            if result.returncode == 0:
                data = json.loads(result.stdout)
                if data.get('result') == 'success':
                    all_currencies = [code for code, name in data.get('supported_codes', [])]
                    
                    # Prioritize based on trading volume and importance
                    prioritized_fiat = self.prioritize_fiat_currencies(all_currencies)
                    print(f"✅ Fetched and prioritized {len(prioritized_fiat)} fiat currencies")
                    return prioritized_fiat[:100]  # Top 100
                else:
                    print(f"❌ ExchangeRates API error: {data.get('error-type')}")
                    return self.get_fallback_fiat_list()
            else:
                print(f"❌ Curl failed: {result.stderr}")
                return self.get_fallback_fiat_list()
                
        except Exception as e:
            print(f"❌ Error fetching fiat data: {e}")
            return self.get_fallback_fiat_list()
    
    def prioritize_fiat_currencies(self, all_currencies: List[str]) -> List[str]:
        """Prioritize fiat currencies based on trading volume and importance"""
        # Priority tiers
        tier1_major = ["USD", "EUR", "JPY", "GBP", "CNY"]  # Top 5 global
        tier2_g20 = ["CAD", "AUD", "CHF", "KRW", "INR", "BRL", "MXN", "RUB", "ZAR", "TRY", "SAR"]
        tier3_financial_hubs = ["HKD", "SGD", "SEK", "NOK", "DKK", "PLN", "CZK", "HUF", "ILS"]
        tier4_regional = ["AED", "THB", "MYR", "IDR", "PHP", "VND", "NZD", "CLP", "COP", "PEN"]
        tier5_others = ["ARS", "EGP", "MAD", "KES", "NGN", "GHS", "TZS", "UGX", "ZMW", "BWP"]
        
        # Build prioritized list
        prioritized = []
        all_currencies_set = set(all_currencies)
        
        # Add tiers in order
        for tier in [tier1_major, tier2_g20, tier3_financial_hubs, tier4_regional, tier5_others]:
            for currency in tier:
                if currency in all_currencies_set and currency not in prioritized:
                    prioritized.append(currency)
        
        # Add remaining currencies
        for currency in all_currencies:
            if currency not in prioritized:
                prioritized.append(currency)
        
        return prioritized
    
    def get_fallback_fiat_list(self) -> List[str]:
        """Fallback fiat list (current optimized top 100)"""
        return [
            "USD", "EUR", "GBP", "JPY", "CNY", "CAD", "AUD", "CHF", "KRW", "INR",
            "BRL", "MXN", "RUB", "ZAR", "TRY", "SEK", "NOK", "DKK", "PLN", "SGD",
            "HKD", "NZD", "THB", "MYR", "PHP", "IDR", "VND", "CLP", "COP", "PEN",
            "ARS", "UYU", "BOB", "PYG", "VES", "GYD", "SRD", "FKP", "GGP", "JEP",
            "AED", "SAR", "QAR", "KWD", "BHD", "OMR", "JOD", "ILS", "EGP", "MAD",
            "TND", "DZD", "LYD", "ETB", "KES", "UGX", "TZS", "RWF", "MWK", "ZMW",
            "ISK", "CZK", "HUF", "RON", "BGN", "HRK", "RSD", "MKD", "ALL", "BAM",
            "MDL", "UAH", "BYN", "GEL", "ARM", "AZN", "KZT", "UZS", "KGS", "TJS",
            "NPR", "BTN", "LKR", "MVR", "PKR", "AFN", "BDT", "MMK", "LAK", "KHR",
            "BND", "FJD", "PGK", "SBD", "VUV", "WST", "TOP", "XPF", "TVD", "AMD"
        ]
    
    def write_crypto_file(self, crypto_list: List[str]) -> None:
        """Write crypto100.txt file"""
        with open('crypto100.txt', 'w') as f:
            for crypto in crypto_list:
                f.write(f"{crypto}\n")
        print(f"✅ Generated crypto100.txt with {len(crypto_list)} cryptocurrencies")
    
    def write_fiat_file(self, fiat_list: List[str]) -> None:
        """Write fiat100.txt file"""
        with open('fiat100.txt', 'w') as f:
            for fiat in fiat_list:
                f.write(f"{fiat}\n")
        print(f"✅ Generated fiat100.txt with {len(fiat_list)} fiat currencies")
    
    async def generate_currency_files(self):
        """Main function to generate both currency files"""
        print("🚀 Generating Top 100 Crypto and Fiat Currency Files")
        print("=" * 60)
        
        # Fetch crypto currencies
        print("🔄 Fetching top 100 cryptocurrencies...")
        crypto_list = await self.fetch_top_100_crypto()
        
        # Fetch fiat currencies
        print("🔄 Fetching top 100 fiat currencies...")
        fiat_list = self.fetch_top_100_fiat_curl()
        
        # Write files
        print("\n📝 Writing currency files...")
        self.write_crypto_file(crypto_list)
        self.write_fiat_file(fiat_list)
        
        print(f"\n🎉 SUCCESS! Generated currency files:")
        print(f"• crypto100.txt: {len(crypto_list)} cryptocurrencies")
        print(f"• fiat100.txt: {len(fiat_list)} fiat currencies")
        print(f"\n💡 SmartConvertEngine will automatically read these files")
        print(f"🧪 Test with: python3 interactive_test.py")

async def main():
    """Main execution function"""
    generator = CurrencyListGenerator()
    await generator.generate_currency_files()

if __name__ == "__main__":
    asyncio.run(main())
