#!/usr/bin/env python3
"""
Interactive Smart Engine Test Interface
Real-time currency conversion testing with user input
"""

import asyncio
import sys
import os
from colorama import init, Fore, Style, Back
from datetime import datetime

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

class InteractiveTestInterface:
    def __init__(self):
        self.cache_manager = MockCacheManager()
        self.client = MockTwelveDataClient()
        self.engine = SmartConvertEngine(self.client, self.cache_manager)
        self.session_stats = {
            'total_conversions': 0,
            'successful_conversions': 0,
            'start_time': datetime.now()
        }
    
    def print_header(self):
        """Print the interface header"""
        print(f"{Back.CYAN}{Fore.BLACK} Smart Currency Engine v2.2 - Interactive Test Interface {Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*70}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}🔧 Enhanced Hybrid API Strategy: ExchangeRates + CoinMarketCap{Style.RESET_ALL}")
        print(f"{Fore.GREEN}✅ ExchangeRates API: {'Configured' if self.engine.exchange_api_key else 'Missing'}{Style.RESET_ALL}")
        print(f"{Fore.GREEN}✅ CoinMarketCap API: {'Configured' if self.engine.cmc_api_key else 'Missing'}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}📊 Assets: {len(self.engine.crypto_assets)} crypto + {len(self.engine.fiat_assets)} fiat{Style.RESET_ALL}")
        print()
    
    def print_help(self):
        """Print help information"""
        print(f"{Fore.YELLOW}📋 Available Commands:{Style.RESET_ALL}")
        print(f"  {Fore.GREEN}convert{Style.RESET_ALL} - Convert currencies (e.g., 'convert BTC USD 0.5')")
        print(f"  {Fore.GREEN}quick{Style.RESET_ALL}   - Quick conversion (e.g., 'quick ETH EUR')")
        print(f"  {Fore.GREEN}stats{Style.RESET_ALL}   - Show performance statistics")
        print(f"  {Fore.GREEN}health{Style.RESET_ALL}  - Show engine health status")
        print(f"  {Fore.GREEN}assets{Style.RESET_ALL}  - List supported assets")
        print(f"  {Fore.GREEN}reset{Style.RESET_ALL}   - Reset statistics")
        print(f"  {Fore.GREEN}help{Style.RESET_ALL}    - Show this help")
        print(f"  {Fore.GREEN}exit{Style.RESET_ALL}    - Exit the interface")
        print()
        print(f"{Fore.CYAN}💡 Examples:{Style.RESET_ALL}")
        print(f"  convert BTC USD 0.1    - Convert 0.1 BTC to USD")
        print(f"  convert 12 ADA IDR     - Convert 12 ADA to IDR")
        print(f"  quick ETH EUR          - Quick convert 1 ETH to EUR")
        print(f"  convert USD JPY 100    - Convert 100 USD to JPY")
        print()
    
    async def handle_convert(self, parts):
        """Handle conversion command"""
        if len(parts) < 3:
            print(f"{Fore.RED}❌ Usage: convert <from> <to> [amount] OR convert <amount> <from> <to>{Style.RESET_ALL}")
            return
        
        # Handle both formats: "convert BTC USD 0.5" and "convert 12 ADA IDR"
        try:
            # Try format: convert <amount> <from> <to>
            amount = float(parts[1])
            base = parts[2].upper()
            quote = parts[3].upper()
        except (ValueError, IndexError):
            # Try format: convert <from> <to> [amount]
            try:
                base = parts[1].upper()
                quote = parts[2].upper()
                amount = float(parts[3]) if len(parts) > 3 else 1.0
            except (ValueError, IndexError):
                print(f"{Fore.RED}❌ Usage: convert <from> <to> [amount] OR convert <amount> <from> <to>{Style.RESET_ALL}")
                return
        
        print(f"{Fore.CYAN}🔄 Converting {amount} {base} → {quote}...{Style.RESET_ALL}")
        
        start_time = datetime.now()
        result = await self.engine.convert(base, quote, amount)
        end_time = datetime.now()
        
        self.session_stats['total_conversions'] += 1
        
        if result.rate is not None:
            self.session_stats['successful_conversions'] += 1
            print(f"{Fore.GREEN}✅ SUCCESS{Style.RESET_ALL}")
            print(f"   💰 {amount} {base} = {Fore.YELLOW}{result.amount:,.6f} {quote}{Style.RESET_ALL}")
            print(f"   📈 Rate: 1 {base} = {result.rate:,.6f} {quote}")
            print(f"   🎯 Method: {result.method.value}")
            print(f"   🔒 Confidence: {result.confidence:.1%}")
            print(f"   ⚡ Latency: {result.latency_ms:.1f}ms")
            if result.cached:
                print(f"   {Fore.CYAN}📦 CACHED{Style.RESET_ALL}")
        else:
            print(f"{Fore.RED}❌ FAILED{Style.RESET_ALL}")
            print(f"   Error: {result.error}")
            print(f"   Method: {result.method.value}")
    
    async def handle_quick(self, parts):
        """Handle quick conversion command"""
        if len(parts) < 3:
            print(f"{Fore.RED}❌ Usage: quick <from> <to>{Style.RESET_ALL}")
            return
        
        await self.handle_convert(['convert'] + parts[1:] + ['1'])
    
    async def handle_stats(self):
        """Handle stats command with enhanced analytics"""
        print(f"{Fore.YELLOW}📊 Session Statistics{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*50}{Style.RESET_ALL}")
        
        session_duration = datetime.now() - self.session_stats['start_time']
        success_rate = (self.session_stats['successful_conversions'] / self.session_stats['total_conversions'] * 100) if self.session_stats['total_conversions'] > 0 else 0
        
        print(f"Session Duration: {session_duration}")
        print(f"Total Conversions: {self.session_stats['total_conversions']}")
        print(f"Successful: {self.session_stats['successful_conversions']}")
        print(f"Success Rate: {success_rate:.1f}%")
        print()
        
        # Enhanced engine stats
        engine_stats = self.engine.get_performance_stats()
        print(f"{Fore.YELLOW}🔧 Enhanced Engine Analytics{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'-'*50}{Style.RESET_ALL}")
        
        # Core metrics
        print(f"Total Engine Conversions: {engine_stats['total_conversions']}")
        print(f"Engine Version: v2.3 (Enhanced Hybrid with Analytics)")
        print(f"Engine Success Rate: {engine_stats['success_rate']}")
        print(f"API Calls Made: {engine_stats['api_calls']}")
        print(f"Cache Hit Rate: {engine_stats['cache_hit_rate']}")
        print(f"Average Latency: {engine_stats['avg_latency_ms']}")
        print(f"Fallback Uses: {engine_stats['fallback_uses']}")
        
        # API usage breakdown
        print(f"\n{Fore.GREEN}📡 API Usage Breakdown:{Style.RESET_ALL}")
        for api, count in engine_stats['api_call_breakdown'].items():
            percentage = engine_stats['api_usage_distribution'][api]
            print(f"  {api}: {count} calls ({percentage})")
        
        # Conversion types
        print(f"\n{Fore.BLUE}🔄 Conversion Types:{Style.RESET_ALL}")
        for conv_type, count in engine_stats['conversion_types'].items():
            print(f"  {conv_type.replace('_', '-to-')}: {count}")
        
        # Error breakdown
        total_errors = sum(engine_stats['error_breakdown'].values())
        if total_errors > 0:
            print(f"\n{Fore.RED}⚠️  Error Breakdown ({total_errors} total):{Style.RESET_ALL}")
            for error_type, count in engine_stats['error_breakdown'].items():
                if count > 0:
                    print(f"  {error_type.replace('_', ' ')}: {count}")
    
    async def handle_health(self):
        """Handle health command"""
        print(f"{Fore.YELLOW}🏥 Engine Health Check{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*40}{Style.RESET_ALL}")
        
        health = await self.engine.health_check()
        
        status_color = Fore.GREEN if health['status'] == 'healthy' else Fore.RED
        print(f"Status: {status_color}{health['status']}{Style.RESET_ALL}")
        print(f"Version: {health['version']}")
        print(f"Timestamp: {health['timestamp']}")
        
        # API Status
        api_status = health['api_status']
        print(f"\n{Fore.CYAN}API Status:{Style.RESET_ALL}")
        
        er_status = api_status['exchangerates_api']['status']
        er_color = Fore.GREEN if er_status == 'configured' else Fore.RED
        print(f"  ExchangeRates: {er_color}{er_status}{Style.RESET_ALL}")
        
        cmc_status = api_status['coinmarketcap_api']['status']
        cmc_color = Fore.GREEN if cmc_status == 'configured' else Fore.RED
        print(f"  CoinMarketCap: {cmc_color}{cmc_status}{Style.RESET_ALL}")
        
        # Cache Status
        cache_status = health['cache_manager']
        cache_color = Fore.GREEN if cache_status == 'operational' else Fore.RED
        print(f"  Cache Manager: {cache_color}{cache_status}{Style.RESET_ALL}")
    
    def handle_assets(self):
        """Handle assets command"""
        print(f"{Fore.YELLOW}💰 Supported Assets{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*40}{Style.RESET_ALL}")
        
        print(f"{Fore.GREEN}Cryptocurrencies ({len(self.engine.crypto_assets)}):{Style.RESET_ALL}")
        crypto_list = sorted(list(self.engine.crypto_assets))
        for i in range(0, len(crypto_list), 10):
            print("  " + " ".join(crypto_list[i:i+10]))
        
        print(f"\n{Fore.BLUE}Fiat Currencies ({len(self.engine.fiat_assets)}):{Style.RESET_ALL}")
        fiat_list = sorted(list(self.engine.fiat_assets))
        for i in range(0, len(fiat_list), 15):
            print("  " + " ".join(fiat_list[i:i+15]))
    
    def handle_reset(self):
        """Handle reset command"""
        self.engine.reset_stats()
        self.session_stats = {
            'total_conversions': 0,
            'successful_conversions': 0,
            'start_time': datetime.now()
        }
        print(f"{Fore.GREEN}✅ Statistics reset successfully{Style.RESET_ALL}")
    
    async def run(self):
        """Run the interactive interface"""
        self.print_header()
        self.print_help()
        
        print(f"{Fore.GREEN}🚀 Enhanced interactive test interface ready! Type 'help' for commands.{Style.RESET_ALL}")
        print()
        
        while True:
            try:
                # Get user input
                user_input = input(f"{Fore.CYAN}💱 SmartEngine> {Style.RESET_ALL}").strip()
                
                if not user_input:
                    continue
                
                parts = user_input.split()
                command = parts[0].lower()
                
                if command == 'exit' or command == 'quit':
                    print(f"{Fore.YELLOW}👋 Thanks for testing Smart Engine v2.2!{Style.RESET_ALL}")
                    break
                elif command == 'help':
                    self.print_help()
                elif command == 'convert':
                    await self.handle_convert(parts)
                elif command == 'quick':
                    await self.handle_quick(parts)
                elif command == 'stats':
                    await self.handle_stats()
                elif command == 'health':
                    await self.handle_health()
                elif command == 'assets':
                    self.handle_assets()
                elif command == 'reset':
                    self.handle_reset()
                else:
                    print(f"{Fore.RED}❌ Unknown command: {command}. Type 'help' for available commands.{Style.RESET_ALL}")
                
                print()  # Add spacing between commands
                
            except KeyboardInterrupt:
                print(f"\n{Fore.YELLOW}👋 Goodbye!{Style.RESET_ALL}")
                break
            except Exception as e:
                print(f"{Fore.RED}💥 Error: {str(e)}{Style.RESET_ALL}")

async def main():
    """Main function"""
    interface = InteractiveTestInterface()
    await interface.run()

if __name__ == "__main__":
    asyncio.run(main())
