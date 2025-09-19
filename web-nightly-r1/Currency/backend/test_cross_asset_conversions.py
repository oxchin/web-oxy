#!/usr/bin/env python3
"""
Comprehensive Cross-Asset Conversion Test Suite
Tests all the enhanced conversion features implemented in main_production.py
"""

import asyncio
import sys
import os
import time
from typing import Dict, List, Tuple

# Add the backend directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import our enhanced conversion functions
from main_production import (
    convert_cross_assets,
    try_direct_crypto_conversion,
    try_usd_bridge_conversion,
    try_eur_bridge_conversion,
    try_btc_bridge_conversion,
    handle_btc_all_currency_conversion,
    ALL_SUPPORTED_ASSETS,
    SUPPORTED_CURRENCIES,
    SUPPORTED_CRYPTO
)

class CrossAssetConversionTester:
    def __init__(self):
        self.test_results = []
        self.total_tests = 0
        self.successful_tests = 0
        
    async def run_test(self, test_name: str, from_asset: str, to_asset: str, amount: float = 1.0) -> Dict:
        """Run a single conversion test"""
        self.total_tests += 1
        start_time = time.time()
        
        try:
            result = await convert_cross_assets(from_asset, to_asset, amount)
            test_time = time.time() - start_time
            
            self.successful_tests += 1
            test_result = {
                "test_name": test_name,
                "pair": f"{from_asset}/{to_asset}",
                "amount": amount,
                "rate": result["rate"],
                "converted_amount": result["converted_amount"],
                "conversion_path": result["conversion_path"],
                "steps": result["steps"],
                "strategy": result.get("metadata", {}).get("strategy", "standard"),
                "bridge_currency": result.get("metadata", {}).get("bridge_currency"),
                "test_time_ms": round(test_time * 1000, 2),
                "success": True
            }
            
            print(f"✅ {test_name}: {from_asset} → {to_asset} | Rate: {result['rate']:.8f} | Path: {result['conversion_path']} | Time: {test_time*1000:.1f}ms")
            
        except Exception as e:
            test_time = time.time() - start_time
            test_result = {
                "test_name": test_name,
                "pair": f"{from_asset}/{to_asset}",
                "amount": amount,
                "error": str(e),
                "test_time_ms": round(test_time * 1000, 2),
                "success": False
            }
            
            print(f"❌ {test_name}: {from_asset} → {to_asset} | Error: {str(e)[:100]}")
        
        self.test_results.append(test_result)
        return test_result
    
    async def test_btc_all_currency_pairs(self):
        """Test BTC/all currency pairs support"""
        print("\n🔸 Testing BTC/All Currency Pairs Support")
        print("=" * 60)
        
        # BTC to major fiat currencies
        major_fiats = ["USD", "EUR", "GBP", "JPY", "CAD", "AUD", "CHF", "CNY", "KRW"]
        for fiat in major_fiats:
            await self.run_test(f"BTC to {fiat}", "BTC", fiat, 0.1)
            await self.run_test(f"{fiat} to BTC", fiat, "BTC", 50000)
        
        # BTC to exotic fiat currencies
        exotic_fiats = ["SGD", "THB", "MYR", "AED", "ZAR", "INR"]
        for fiat in exotic_fiats:
            await self.run_test(f"BTC to {fiat} (exotic)", "BTC", fiat, 0.05)
    
    async def test_crypto_to_crypto_conversions(self):
        """Test comprehensive crypto-to-crypto conversions"""
        print("\n🔸 Testing Crypto-to-Crypto Conversions")
        print("=" * 60)
        
        # Major crypto pairs
        crypto_pairs = [
            ("BTC", "ETH", 0.1),
            ("ETH", "BTC", 5.0),
            ("BTC", "ADA", 0.01),
            ("ETH", "ADA", 1.0),
            ("ADA", "SOL", 100),
            ("SOL", "DOGE", 10),
            ("DOGE", "LINK", 1000),
            ("LINK", "UNI", 5),
            ("UNI", "DOT", 2),
            ("DOT", "MATIC", 3)
        ]
        
        for from_crypto, to_crypto, amount in crypto_pairs:
            await self.run_test(f"{from_crypto} to {to_crypto}", from_crypto, to_crypto, amount)
    
    async def test_crypto_to_all_currency(self):
        """Test crypto-to-all-currency conversions"""
        print("\n🔸 Testing Crypto-to-All-Currency Conversions")
        print("=" * 60)
        
        # Major cryptos to various fiat currencies
        test_cases = [
            ("ETH", "USD", 1.0),
            ("ETH", "EUR", 1.0),
            ("ETH", "GBP", 1.0),
            ("ADA", "USD", 100),
            ("ADA", "EUR", 100),
            ("SOL", "JPY", 10),
            ("SOL", "CAD", 10),
            ("DOGE", "AUD", 1000),
            ("LINK", "CHF", 5),
            ("UNI", "SGD", 3)
        ]
        
        for from_crypto, to_fiat, amount in test_cases:
            await self.run_test(f"{from_crypto} to {to_fiat}", from_crypto, to_fiat, amount)
    
    async def test_all_currency_to_all_crypto(self):
        """Test all-currency-to-all-crypto conversions"""
        print("\n🔸 Testing All-Currency-to-All-Crypto Conversions")
        print("=" * 60)
        
        # Various fiat currencies to different cryptos
        test_cases = [
            ("USD", "ETH", 2500),
            ("EUR", "ADA", 200),
            ("GBP", "SOL", 500),
            ("JPY", "DOGE", 10000),
            ("CAD", "LINK", 300),
            ("AUD", "UNI", 400),
            ("CHF", "DOT", 250),
            ("SGD", "MATIC", 150),
            ("KRW", "AVAX", 50000),
            ("INR", "ATOM", 5000)
        ]
        
        for from_fiat, to_crypto, amount in test_cases:
            await self.run_test(f"{from_fiat} to {to_crypto}", from_fiat, to_crypto, amount)
    
    async def test_enhanced_currency_to_currency(self):
        """Test enhanced currency-to-currency conversions with all pairs"""
        print("\n🔸 Testing Enhanced Currency-to-Currency Conversions")
        print("=" * 60)
        
        # Major currency pairs
        major_pairs = [
            ("USD", "EUR", 100),
            ("EUR", "GBP", 100),
            ("GBP", "JPY", 100),
            ("JPY", "CNY", 10000),
            ("CNY", "KRW", 1000),
            ("KRW", "INR", 1000)
        ]
        
        for from_curr, to_curr, amount in major_pairs:
            await self.run_test(f"{from_curr} to {to_curr}", from_curr, to_curr, amount)
        
        # Exotic currency pairs
        exotic_pairs = [
            ("SGD", "THB", 100),
            ("AED", "MYR", 500),
            ("ZAR", "MXN", 1000),
            ("TRY", "BRL", 200),
            ("PLN", "CZK", 300)
        ]
        
        for from_curr, to_curr, amount in exotic_pairs:
            await self.run_test(f"{from_curr} to {to_curr} (exotic)", from_curr, to_curr, amount)
    
    async def test_bridge_conversion_strategies(self):
        """Test different bridge conversion strategies"""
        print("\n🔸 Testing Bridge Conversion Strategies")
        print("=" * 60)
        
        # Test USD bridge for crypto-to-crypto
        await self.run_test("USD Bridge: SHIB to ALGO", "SHIB", "ALGO", 1000000)
        await self.run_test("USD Bridge: VET to FIL", "VET", "FIL", 1000)
        
        # Test EUR bridge fallback
        await self.run_test("EUR Bridge: HBAR to NEAR", "HBAR", "NEAR", 1000)
        
        # Test BTC bridge for altcoins
        await self.run_test("BTC Bridge: APT to STX", "APT", "STX", 2)
        await self.run_test("BTC Bridge: XLM to ATOM", "XLM", "ATOM", 100)
    
    async def run_comprehensive_test_suite(self):
        """Run the complete comprehensive test suite"""
        print("🚀 Starting Comprehensive Cross-Asset Conversion Test Suite")
        print("=" * 80)
        print(f"📊 Total Supported Assets: {len(ALL_SUPPORTED_ASSETS)}")
        print(f"💰 Fiat Currencies: {len(SUPPORTED_CURRENCIES)}")
        print(f"🪙 Cryptocurrencies: {len(SUPPORTED_CRYPTO)}")
        print("=" * 80)
        
        start_time = time.time()
        
        # Run all test categories
        await self.test_btc_all_currency_pairs()
        await self.test_crypto_to_crypto_conversions()
        await self.test_crypto_to_all_currency()
        await self.test_all_currency_to_all_crypto()
        await self.test_enhanced_currency_to_currency()
        await self.test_bridge_conversion_strategies()
        
        total_time = time.time() - start_time
        
        # Generate comprehensive report
        self.generate_test_report(total_time)
    
    def generate_test_report(self, total_time: float):
        """Generate comprehensive test report"""
        print("\n" + "=" * 80)
        print("📋 COMPREHENSIVE CROSS-ASSET CONVERSION TEST REPORT")
        print("=" * 80)
        
        success_rate = (self.successful_tests / self.total_tests * 100) if self.total_tests > 0 else 0
        
        print(f"📊 Overall Results:")
        print(f"   • Total Tests: {self.total_tests}")
        print(f"   • Successful: {self.successful_tests}")
        print(f"   • Failed: {self.total_tests - self.successful_tests}")
        print(f"   • Success Rate: {success_rate:.1f}%")
        print(f"   • Total Time: {total_time:.2f}s")
        print(f"   • Average Time per Test: {(total_time/self.total_tests)*1000:.1f}ms")
        
        # Analyze by conversion path
        path_analysis = {}
        strategy_analysis = {}
        
        for result in self.test_results:
            if result["success"]:
                path = result.get("conversion_path", "unknown")
                strategy = result.get("strategy", "standard")
                
                path_analysis[path] = path_analysis.get(path, 0) + 1
                strategy_analysis[strategy] = strategy_analysis.get(strategy, 0) + 1
        
        print(f"\n🛤️  Conversion Path Analysis:")
        for path, count in sorted(path_analysis.items()):
            percentage = (count / self.successful_tests * 100) if self.successful_tests > 0 else 0
            print(f"   • {path}: {count} tests ({percentage:.1f}%)")
        
        print(f"\n🔧 Strategy Analysis:")
        for strategy, count in sorted(strategy_analysis.items()):
            percentage = (count / self.successful_tests * 100) if self.successful_tests > 0 else 0
            print(f"   • {strategy}: {count} tests ({percentage:.1f}%)")
        
        # Show failed tests
        failed_tests = [r for r in self.test_results if not r["success"]]
        if failed_tests:
            print(f"\n❌ Failed Tests ({len(failed_tests)}):")
            for test in failed_tests[:10]:  # Show first 10 failures
                print(f"   • {test['test_name']}: {test.get('error', 'Unknown error')[:80]}")
            if len(failed_tests) > 10:
                print(f"   ... and {len(failed_tests) - 10} more")
        
        # Performance metrics
        successful_times = [r["test_time_ms"] for r in self.test_results if r["success"]]
        if successful_times:
            print(f"\n⚡ Performance Metrics:")
            print(f"   • Fastest Test: {min(successful_times):.1f}ms")
            print(f"   • Slowest Test: {max(successful_times):.1f}ms")
            print(f"   • Median Time: {sorted(successful_times)[len(successful_times)//2]:.1f}ms")
        
        print("\n" + "=" * 80)
        if success_rate >= 90:
            print("🎉 EXCELLENT: Cross-asset conversion system is working exceptionally well!")
        elif success_rate >= 80:
            print("✅ GOOD: Cross-asset conversion system is working well with minor issues.")
        elif success_rate >= 70:
            print("⚠️  WARNING: Cross-asset conversion system has some issues that need attention.")
        else:
            print("🚨 CRITICAL: Cross-asset conversion system needs significant improvements.")
        print("=" * 80)

async def main():
    """Main test execution function"""
    print("🔧 Initializing Cross-Asset Conversion Test Environment...")
    
    tester = CrossAssetConversionTester()
    await tester.run_comprehensive_test_suite()

if __name__ == "__main__":
    asyncio.run(main())
