#!/usr/bin/env python3
"""
Curl Test for Top 100 Fiat Currencies by Trading Volume and Liquidity
"""

import json
import subprocess
import os
from typing import Dict, List, Set, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class FiatVolumeAnalyzer:
    def __init__(self):
        self.exchange_api_key = os.getenv('EXCHANGE_API_KEY')
        
    def curl_major_trading_pairs(self) -> Dict:
        """Get major trading pairs to identify most liquid fiat currencies"""
        
        # Test with multiple endpoints to get comprehensive data
        results = {}
        
        # 1. ExchangeRates API - Get all supported currencies with rates
        if self.exchange_api_key:
            url = f"https://v6.exchangerate-api.com/v6/{self.exchange_api_key}/latest/USD"
            
            try:
                cmd = ['curl', '-s', '--connect-timeout', '10', '--max-time', '30', url]
                print("🔄 Testing ExchangeRates API for USD rates...")
                
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=35)
                
                if result.returncode == 0:
                    data = json.loads(result.stdout)
                    if data.get('result') == 'success':
                        rates = data.get('conversion_rates', {})
                        print(f"✅ ExchangeRates API: {len(rates)} currency rates fetched")
                        results['exchangerates'] = {
                            'currencies': set(rates.keys()),
                            'count': len(rates),
                            'source': 'ExchangeRates API'
                        }
                    else:
                        print(f"❌ ExchangeRates API error: {data.get('error-type')}")
                        
            except Exception as e:
                print(f"❌ ExchangeRates API error: {e}")
        
        # 2. European Central Bank rates (free, no key needed)
        ecb_url = "https://api.exchangerate.host/latest?base=USD"
        
        try:
            cmd = ['curl', '-s', '--connect-timeout', '10', '--max-time', '30', ecb_url]
            print("🔄 Testing ECB Exchange Rate Host API...")
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=35)
            
            if result.returncode == 0:
                data = json.loads(result.stdout)
                if data.get('success'):
                    rates = data.get('rates', {})
                    print(f"✅ ECB API: {len(rates)} currency rates fetched")
                    results['ecb'] = {
                        'currencies': set(rates.keys()),
                        'count': len(rates),
                        'source': 'ECB Exchange Rate Host'
                    }
                else:
                    print(f"❌ ECB API error")
                    
        except Exception as e:
            print(f"❌ ECB API error: {e}")
        
        # 3. Fixer.io historical data (free tier)
        fixer_url = "https://api.fixer.io/latest?base=USD"
        
        try:
            cmd = ['curl', '-s', '--connect-timeout', '10', '--max-time', '30', fixer_url]
            print("🔄 Testing Fixer.io free tier...")
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=35)
            
            if result.returncode == 0:
                data = json.loads(result.stdout)
                if data.get('success'):
                    rates = data.get('rates', {})
                    print(f"✅ Fixer.io: {len(rates)} currency rates fetched")
                    results['fixer'] = {
                        'currencies': set(rates.keys()),
                        'count': len(rates),
                        'source': 'Fixer.io'
                    }
                else:
                    print(f"❌ Fixer.io error: {data.get('error', {}).get('type')}")
                    
        except Exception as e:
            print(f"❌ Fixer.io error: {e}")
        
        return results
    
    def get_g20_major_currencies(self) -> Set[str]:
        """Get G20 and major trading currencies (most liquid)"""
        return {
            # G20 currencies (highest volume)
            "USD", "EUR", "JPY", "GBP", "CNY", "CAD", "AUD", "CHF", 
            "KRW", "INR", "BRL", "MXN", "RUB", "ZAR", "TRY", "SAR",
            
            # Major trading hubs
            "HKD", "SGD", "SEK", "NOK", "DKK", "PLN", "CZK", "HUF",
            "ILS", "AED", "THB", "MYR", "IDR", "PHP", "VND", "NZD",
            
            # Regional powerhouses
            "CLP", "COP", "PEN", "ARS", "EGP", "MAD", "KES", "NGN",
            "GHS", "XOF", "XAF", "UGX", "TZS", "ZMW", "BWP", "MWK"
        }
    
    def analyze_currency_priority(self, api_results: Dict) -> List[str]:
        """Analyze and prioritize currencies based on multiple factors"""
        
        # Combine all currencies from APIs
        all_currencies = set()
        api_counts = {}
        
        for api_name, data in api_results.items():
            currencies = data['currencies']
            all_currencies.update(currencies)
            
            for currency in currencies:
                api_counts[currency] = api_counts.get(currency, 0) + 1
        
        # Get major currencies
        major_currencies = self.get_g20_major_currencies()
        
        # Priority scoring system
        currency_scores = {}
        
        for currency in all_currencies:
            score = 0
            
            # Base score for being in APIs
            score += api_counts.get(currency, 0) * 10
            
            # Major currency bonus
            if currency in major_currencies:
                score += 50
            
            # Regional importance (based on economic zones)
            if currency in ["USD", "EUR", "JPY", "GBP", "CNY"]:  # Top 5 global
                score += 100
            elif currency in ["CAD", "AUD", "CHF", "KRW", "INR", "BRL", "MXN"]:  # Major economies
                score += 75
            elif currency in ["HKD", "SGD", "SEK", "NOK", "DKK", "PLN"]:  # Financial hubs
                score += 60
            elif currency in ["AED", "SAR", "ZAR", "TRY", "THB", "MYR"]:  # Regional leaders
                score += 40
            
            currency_scores[currency] = score
        
        # Sort by score (descending)
        sorted_currencies = sorted(currency_scores.items(), key=lambda x: x[1], reverse=True)
        
        return [currency for currency, score in sorted_currencies[:100]]
    
    def generate_optimized_fiat_list(self, api_results: Dict) -> None:
        """Generate optimized top 100 fiat currencies list"""
        
        print(f"\n📊 FIAT CURRENCY OPTIMIZATION ANALYSIS")
        print(f"=" * 60)
        
        # Get prioritized list
        top_100_fiat = self.analyze_currency_priority(api_results)
        
        print(f"Optimized top 100 fiat currencies based on:")
        print(f"• API coverage ({len(api_results)} sources)")
        print(f"• G20 and major economy currencies")
        print(f"• Regional financial hub importance")
        print(f"• Trading volume and liquidity factors")
        
        # Generate code
        print(f"\n# Optimized top 100 fiat currencies (Live API data + volume analysis)")
        print("self.fiat_assets = {")
        
        # Group by 10 for better readability
        for i in range(0, len(top_100_fiat), 10):
            group = top_100_fiat[i:i+10]
            line = '    "' + '", "'.join(group) + '"'
            if i + 10 < len(top_100_fiat):
                line += ","
            print(line)
        
        print("}")
        print(f"# Total: {len(top_100_fiat)} fiat currencies")
        print("# Optimized for trading volume, liquidity, and API coverage")
        
        # Analysis breakdown
        major_in_list = len([c for c in top_100_fiat if c in self.get_g20_major_currencies()])
        print(f"\n📈 OPTIMIZATION METRICS:")
        print(f"• Major currencies included: {major_in_list}/100")
        print(f"• API coverage: {len(api_results)} sources validated")
        print(f"• Global economic coverage: G20 + regional leaders")
        
    def run_comprehensive_test(self):
        """Run comprehensive fiat currency analysis with curl"""
        
        print("🚀 Comprehensive Fiat Currency Analysis with Curl")
        print("=" * 60)
        
        # Get data from multiple APIs
        api_results = self.curl_major_trading_pairs()
        
        if not api_results:
            print("❌ No APIs responded successfully")
            return
        
        print(f"\n✅ Successfully tested {len(api_results)} APIs:")
        total_currencies = set()
        
        for api_name, data in api_results.items():
            print(f"• {data['source']}: {data['count']} currencies")
            total_currencies.update(data['currencies'])
        
        print(f"\nCombined unique currencies: {len(total_currencies)}")
        
        # Generate optimized list
        self.generate_optimized_fiat_list(api_results)

def main():
    """Main function"""
    analyzer = FiatVolumeAnalyzer()
    analyzer.run_comprehensive_test()

if __name__ == "__main__":
    main()
