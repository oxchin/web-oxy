#!/usr/bin/env python3
"""
Test SmartConvertEngine with file-based currency data
"""

import asyncio
import sys
import os

# Add the backend directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from smart_convert_engine import SmartConvertEngine

class MockTwelveDataClient:
    """Mock client for testing"""
    pass

class MockCacheManager:
    """Mock cache manager for testing"""
    def __init__(self):
        self.cache = {}
    
    async def get(self, key):
        return self.cache.get(key)
    
    async def set(self, key, value, ttl=None):
        self.cache[key] = value

async def test_conversion():
    """Test specific conversion: 1 XAUt to SGD"""
    print("🚀 Testing SmartConvertEngine with file-based currency data")
    print("=" * 60)
    
    # Initialize engine with mock dependencies
    twelve_data_client = MockTwelveDataClient()
    cache_manager = MockCacheManager()
    engine = SmartConvertEngine(twelve_data_client, cache_manager)
    
    # Test conversion: 1 XAUt to SGD
    print("\n🧪 Testing conversion: 1 XAUt → SGD")
    try:
        result = await engine.convert("XAUt", "SGD", 1.0)
        
        print(f"✅ Conversion successful!")
        print(f"   Pair: {result.pair}")
        print(f"   Rate: {result.rate}")
        print(f"   Amount: {result.amount}")
        print(f"   Method: {result.method}")
        print(f"   Latency: {result.latency_ms}ms")
        
    except Exception as e:
        print(f"❌ Conversion failed: {e}")
    
    # Test a few more conversions
    test_pairs = [
        ("BTC", "USD", 1.0),
        ("USD", "EUR", 100.0),
        ("ETH", "SGD", 1.0),
        ("USDT", "JPY", 50.0)
    ]
    
    print(f"\n🧪 Testing additional conversions:")
    for base, quote, amount in test_pairs:
        try:
            result = await engine.convert(base, quote, amount)
            print(f"✅ {amount} {base} → {result.amount:.4f} {quote} (Rate: {result.rate:.6f})")
        except Exception as e:
            print(f"❌ {amount} {base} → {quote}: {e}")
    
    # Show engine statistics
    print(f"\n📊 Engine Statistics:")
    stats = engine.stats
    print(f"   Total conversions: {stats['total_conversions']}")
    print(f"   Successful conversions: {stats['successful_conversions']}")
    print(f"   Cache hits: {stats['cache_hits']}")
    print(f"   API calls: {stats['api_calls']}")
    print(f"   Average latency: {stats['avg_latency']:.2f}ms")

if __name__ == "__main__":
    asyncio.run(test_conversion())
