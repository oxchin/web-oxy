#!/usr/bin/env python3
"""
Test Hybrid API Integration
ExchangeRates API + CoinMarketCap API Strategy
"""

import asyncio
import sys
import os
from colorama import init, Fore, Style

# Add the backend directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from smart_convert_engine import SmartConvertEngine

# Initialize colorama for cross-platform colored output
init(autoreset=True)

class MockCacheManager:
    """Mock cache manager for testing"""
    def __init__(self):
        self.cache = {}
    
    async def get(self, key):
        return self.cache.get(key)
    
    async def set(self, key, value, ttl=None):
        self.cache[key] = value

class MockTwelveDataClient:
    """Mock client for testing"""
    pass

async def test_hybrid_api_integration():
    """Test the hybrid API integration strategy"""
    print(f"{Fore.CYAN}🔧 Hybrid API Integration Test{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}ExchangeRates API + CoinMarketCap API Strategy{Style.RESET_ALL}")
    print("=" * 60)
    
    # Initialize engine
    cache_manager = MockCacheManager()
    client = MockTwelveDataClient()
    engine = SmartConvertEngine(client, cache_manager)
    
    # Check API key configuration
    print(f"{Fore.YELLOW}API Configuration:{Style.RESET_ALL}")
    print(f"ExchangeRates API: {'✅ Configured' if engine.exchange_api_key else '❌ Missing'}")
    print(f"CoinMarketCap API: {'✅ Configured' if engine.cmc_api_key else '❌ Missing'}")
    print(f"Engine Version: v2.2 (Hybrid)")
    print()
    
    # Test conversion categories
    test_categories = [
        {
            'name': 'Fiat-to-Fiat (ExchangeRates API)',
            'pairs': [('USD', 'EUR'), ('GBP', 'JPY'), ('CAD', 'AUD')],
            'api': 'ExchangeRates'
        },
        {
            'name': 'Crypto-to-Fiat (CoinMarketCap API)', 
            'pairs': [('BTC', 'USD'), ('ETH', 'EUR'), ('ADA', 'GBP')],
            'api': 'CoinMarketCap'
        },
        {
            'name': 'Fiat-to-Crypto (CoinMarketCap API)',
            'pairs': [('USD', 'BTC'), ('EUR', 'ETH'), ('JPY', 'SOL')],
            'api': 'CoinMarketCap'
        },
        {
            'name': 'Crypto-to-Crypto (CoinMarketCap API)',
            'pairs': [('BTC', 'ETH'), ('ETH', 'ADA'), ('SOL', 'DOGE')],
            'api': 'CoinMarketCap'
        }
    ]
    
    total_tests = 0
    successful_tests = 0
    
    for category in test_categories:
        print(f"{Fore.YELLOW}🧪 {category['name']}{Style.RESET_ALL}")
        print(f"Expected API: {category['api']}")
        print("-" * 50)
        
        for base, quote in category['pairs']:
            total_tests += 1
            print(f"\nTest: {base} → {quote}")
            
            try:
                result = await engine.convert(base, quote, 1.0)
                
                if result.rate is not None:
                    print(f"  ✅ {Fore.GREEN}SUCCESS{Style.RESET_ALL}")
                    print(f"     Rate: 1 {base} = {result.rate:,.6f} {quote}")
                    print(f"     Method: {result.method.value}")
                    print(f"     Confidence: {result.confidence:.1%}")
                    print(f"     Latency: {result.latency_ms:.1f}ms")
                    if hasattr(result, 'source'):
                        print(f"     Source: {result.source}")
                    successful_tests += 1
                else:
                    print(f"  ❌ {Fore.RED}FAILED{Style.RESET_ALL}")
                    print(f"     Error: {result.error}")
                    print(f"     Method: {result.method.value}")
                    
            except Exception as e:
                print(f"  💥 {Fore.RED}EXCEPTION{Style.RESET_ALL}")
                print(f"     Error: {str(e)}")
        
        print()
    
    # Summary
    print(f"{Fore.YELLOW}📊 TEST SUMMARY{Style.RESET_ALL}")
    print("=" * 50)
    
    success_rate = (successful_tests / total_tests) * 100 if total_tests > 0 else 0
    print(f"Total Tests: {total_tests}")
    print(f"Successful: {successful_tests}")
    print(f"Success Rate: {success_rate:.1f}%")
    
    # Performance stats
    stats = engine.get_performance_stats()
    print(f"\n{Fore.CYAN}Performance Statistics:{Style.RESET_ALL}")
    print(f"  - Total Conversions: {stats['total_conversions']}")
    print(f"  - Success Rate: {stats['success_rate']}")
    print(f"  - API Calls: {stats['api_calls']}")
    print(f"  - Cache Hit Rate: {stats['cache_hit_rate']}")
    print(f"  - Average Latency: {stats['avg_latency_ms']}")
    print(f"  - APIs Configured:")
    print(f"    - ExchangeRates: {'✅' if stats['apis_configured']['exchangerates'] else '❌'}")
    print(f"    - CoinMarketCap: {'✅' if stats['apis_configured']['coinmarketcap'] else '❌'}")
    
    # Health check
    print(f"\n{Fore.YELLOW}🏥 HEALTH CHECK{Style.RESET_ALL}")
    print("-" * 50)
    
    health = await engine.health_check()
    print(f"Engine Status: {Fore.GREEN if health['status'] == 'healthy' else Fore.RED}{health['status']}{Style.RESET_ALL}")
    print(f"Version: {health['version']}")
    
    # API status
    api_status = health['api_status']
    
    print(f"\nExchangeRates API:")
    er_status = api_status['exchangerates_api']['status']
    er_color = Fore.GREEN if er_status == 'configured' else Fore.RED
    print(f"  Status: {er_color}{er_status}{Style.RESET_ALL}")
    print(f"  Supports: {api_status['exchangerates_api']['supports']}")
    
    print(f"\nCoinMarketCap API:")
    cmc_status = api_status['coinmarketcap_api']['status']
    cmc_color = Fore.GREEN if cmc_status == 'configured' else Fore.RED
    print(f"  Status: {cmc_color}{cmc_status}{Style.RESET_ALL}")
    print(f"  Supports: {api_status['coinmarketcap_api']['supports']}")
    
    # Cache status
    cache_status = health['cache_manager']
    cache_color = Fore.GREEN if cache_status == 'operational' else Fore.RED
    print(f"\nCache Manager: {cache_color}{cache_status}{Style.RESET_ALL}")
    
    print(f"\n{Fore.GREEN}🎉 Hybrid API Integration Test Complete!{Style.RESET_ALL}")
    
    if engine.exchange_api_key and engine.cmc_api_key:
        print(f"{Fore.CYAN}✨ Ready for production with hybrid API strategy (no rate limits!){Style.RESET_ALL}")
    else:
        print(f"{Fore.YELLOW}⚠️  Configure API keys for live data:{Style.RESET_ALL}")
        if not engine.exchange_api_key:
            print(f"   - ExchangeRates API: https://exchangerate-api.com/")
        if not engine.cmc_api_key:
            print(f"   - CoinMarketCap API: https://coinmarketcap.com/api/")

if __name__ == "__main__":
    asyncio.run(test_hybrid_api_integration())
