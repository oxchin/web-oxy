#!/usr/bin/env python3
"""
Test and Validate Top 100 Fiat Currencies using curl and live APIs
"""

import os
import json
import subprocess
import asyncio
from typing import Dict, List, Set, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Current fiat assets from SmartConvertEngine
CURRENT_FIAT_ASSETS = {
    # Major currencies (G20 + most traded)
    "USD", "EUR", "GBP", "JPY", "CNY", "CAD", "AUD", "CHF", "KRW", "INR",
    "BRL", "MXN", "RUB", "ZAR", "TRY", "SEK", "NOK", "DKK", "PLN", "SGD",
    
    # Regional powerhouses
    "HKD", "NZD", "THB", "MYR", "PHP", "IDR", "VND", "CLP", "COP", "PEN",
    "ARS", "UYU", "BOB", "PYG", "VES", "GYD", "SRD", "FKP", "GGP", "JEP",
    
    # Middle East & Africa
    "AED", "SAR", "QAR", "KWD", "BHD", "OMR", "JOD", "ILS", "EGP", "MAD",
    "TND", "DZD", "LYD", "ETB", "KES", "UGX", "TZS", "RWF", "MWK", "ZMW",
    
    # Europe (non-EU)
    "ISK", "CZK", "HUF", "RON", "BGN", "HRK", "RSD", "MKD", "ALL", "BAM",
    "MDL", "UAH", "BYN", "GEL", "AMD", "AZN", "KZT", "UZS", "KGS", "TJS",
    
    # Asia-Pacific
    "NPR", "BTN", "LKR", "MVR", "PKR", "AFN", "BDT", "MMK", "LAK", "KHR",
    "BND", "FJD", "PGK", "SBD", "VUV", "WST", "TOP", "XPF", "NCL", "TVD"
}

class FiatCurrencyTester:
    def __init__(self):
        self.exchange_api_key = os.getenv('EXCHANGE_API_KEY')
        self.results = {}
        
    def curl_exchangerates_api(self) -> Optional[Dict]:
        """Test curl with ExchangeRates API to get supported currencies"""
        if not self.exchange_api_key:
            print("❌ EXCHANGE_API_KEY not found")
            return None
            
        url = f"https://v6.exchangerate-api.com/v6/{self.exchange_api_key}/codes"
        
        try:
            cmd = [
                'curl', '-s', '-H', 'Accept: application/json',
                '--connect-timeout', '10', '--max-time', '30',
                url
            ]
            
            print(f"🔄 Testing curl with ExchangeRates API...")
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=35)
            
            if result.returncode == 0:
                data = json.loads(result.stdout)
                if data.get('result') == 'success':
                    currencies = {code for code, name in data.get('supported_codes', [])}
                    print(f"✅ ExchangeRates API: {len(currencies)} currencies fetched")
                    return {
                        'source': 'ExchangeRates API',
                        'currencies': currencies,
                        'count': len(currencies)
                    }
                else:
                    print(f"❌ ExchangeRates API error: {data.get('error-type', 'Unknown')}")
            else:
                print(f"❌ Curl failed: {result.stderr}")
                
        except Exception as e:
            print(f"❌ Error with ExchangeRates API: {e}")
            
        return None
    
    def curl_fixer_api(self) -> Optional[Dict]:
        """Test curl with Fixer.io API for currency symbols"""
        url = "http://data.fixer.io/api/symbols?access_key=demo"
        
        try:
            cmd = [
                'curl', '-s', '-H', 'Accept: application/json',
                '--connect-timeout', '10', '--max-time', '30',
                url
            ]
            
            print(f"🔄 Testing curl with Fixer.io API...")
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=35)
            
            if result.returncode == 0:
                data = json.loads(result.stdout)
                if data.get('success'):
                    currencies = set(data.get('symbols', {}).keys())
                    print(f"✅ Fixer.io API: {len(currencies)} currencies fetched")
                    return {
                        'source': 'Fixer.io API',
                        'currencies': currencies,
                        'count': len(currencies)
                    }
                else:
                    print(f"❌ Fixer.io API error: {data.get('error', {}).get('type', 'Unknown')}")
            else:
                print(f"❌ Curl failed: {result.stderr}")
                
        except Exception as e:
            print(f"❌ Error with Fixer.io API: {e}")
            
        return None
    
    def curl_currencylayer_api(self) -> Optional[Dict]:
        """Test curl with CurrencyLayer API for supported currencies"""
        url = "http://api.currencylayer.com/list?access_key=demo"
        
        try:
            cmd = [
                'curl', '-s', '-H', 'Accept: application/json',
                '--connect-timeout', '10', '--max-time', '30',
                url
            ]
            
            print(f"🔄 Testing curl with CurrencyLayer API...")
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=35)
            
            if result.returncode == 0:
                data = json.loads(result.stdout)
                if data.get('success'):
                    currencies = set(data.get('currencies', {}).keys())
                    print(f"✅ CurrencyLayer API: {len(currencies)} currencies fetched")
                    return {
                        'source': 'CurrencyLayer API',
                        'currencies': currencies,
                        'count': len(currencies)
                    }
                else:
                    print(f"❌ CurrencyLayer API error: {data.get('error', {}).get('type', 'Unknown')}")
            else:
                print(f"❌ Curl failed: {result.stderr}")
                
        except Exception as e:
            print(f"❌ Error with CurrencyLayer API: {e}")
            
        return None
    
    def curl_openexchangerates_api(self) -> Optional[Dict]:
        """Test curl with Open Exchange Rates API"""
        url = "https://openexchangerates.org/api/currencies.json"
        
        try:
            cmd = [
                'curl', '-s', '-H', 'Accept: application/json',
                '--connect-timeout', '10', '--max-time', '30',
                url
            ]
            
            print(f"🔄 Testing curl with Open Exchange Rates API...")
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=35)
            
            if result.returncode == 0:
                data = json.loads(result.stdout)
                currencies = set(data.keys()) if isinstance(data, dict) else set()
                print(f"✅ Open Exchange Rates: {len(currencies)} currencies fetched")
                return {
                    'source': 'Open Exchange Rates',
                    'currencies': currencies,
                    'count': len(currencies)
                }
            else:
                print(f"❌ Curl failed: {result.stderr}")
                
        except Exception as e:
            print(f"❌ Error with Open Exchange Rates: {e}")
            
        return None
    
    def validate_against_sources(self, sources: List[Dict]) -> Dict:
        """Validate current fiat assets against multiple sources"""
        print(f"\n📊 FIAT CURRENCIES VALIDATION REPORT")
        print(f"=" * 60)
        print(f"Current fiat assets count: {len(CURRENT_FIAT_ASSETS)}")
        
        # Combine all sources
        all_live_currencies = set()
        source_names = []
        
        for source in sources:
            if source:
                all_live_currencies.update(source['currencies'])
                source_names.append(source['source'])
                print(f"{source['source']}: {source['count']} currencies")
        
        print(f"\nCombined live currencies: {len(all_live_currencies)}")
        print(f"Sources: {', '.join(source_names)}")
        
        # Analysis
        matching = CURRENT_FIAT_ASSETS & all_live_currencies
        missing = all_live_currencies - CURRENT_FIAT_ASSETS
        deprecated = CURRENT_FIAT_ASSETS - all_live_currencies
        
        coverage = len(matching) / len(CURRENT_FIAT_ASSETS) * 100
        
        print(f"\n✅ Matching currencies: {len(matching)}/{len(CURRENT_FIAT_ASSETS)}")
        print(f"📈 Coverage: {coverage:.1f}%")
        
        if missing:
            print(f"\n⚠️  Missing from current list ({len(missing)}):")
            for curr in sorted(list(missing)[:20]):  # Show first 20
                print(f"   + {curr}")
            if len(missing) > 20:
                print(f"   ... and {len(missing) - 20} more")
        
        if deprecated:
            print(f"\n🔄 Not found in live sources ({len(deprecated)}):")
            for curr in sorted(deprecated):
                print(f"   - {curr}")
        
        # Validation status
        if coverage >= 95:
            print(f"\n🎉 VALIDATION PASSED: {coverage:.1f}% coverage is excellent!")
        elif coverage >= 85:
            print(f"\n✅ VALIDATION GOOD: {coverage:.1f}% coverage is acceptable")
        else:
            print(f"\n⚠️  VALIDATION WARNING: {coverage:.1f}% coverage may need update")
        
        return {
            'coverage_percent': coverage,
            'matching_count': len(matching),
            'missing_currencies': list(missing),
            'deprecated_currencies': list(deprecated),
            'total_live_currencies': len(all_live_currencies),
            'sources_tested': len([s for s in sources if s])
        }
    
    async def run_all_tests(self):
        """Run all curl tests and validate results"""
        print("🚀 Starting comprehensive fiat currency validation with curl...")
        print("=" * 60)
        
        # Test all APIs with curl
        sources = []
        
        # Test each API
        sources.append(self.curl_exchangerates_api())
        sources.append(self.curl_fixer_api())
        sources.append(self.curl_currencylayer_api())
        sources.append(self.curl_openexchangerates_api())
        
        # Filter successful sources
        successful_sources = [s for s in sources if s is not None]
        
        if not successful_sources:
            print("❌ No APIs responded successfully")
            return
        
        # Validate against all sources
        validation_result = self.validate_against_sources(successful_sources)
        
        # Recommendations
        print(f"\n💡 RECOMMENDATIONS:")
        if validation_result['coverage_percent'] < 90:
            print(f"• Consider updating fiat currency list")
            print(f"• Current coverage: {validation_result['coverage_percent']:.1f}%")
        
        if validation_result['sources_tested'] < 2:
            print(f"• Only {validation_result['sources_tested']} API(s) responded")
            print(f"• Consider checking API keys and network connectivity")
        
        print(f"\n📋 SUMMARY:")
        print(f"• APIs tested: 4")
        print(f"• APIs successful: {validation_result['sources_tested']}")
        print(f"• Total live currencies found: {validation_result['total_live_currencies']}")
        print(f"• Current list coverage: {validation_result['coverage_percent']:.1f}%")
        print(f"• Matching currencies: {validation_result['matching_count']}")

async def main():
    """Main test function"""
    tester = FiatCurrencyTester()
    await tester.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())
