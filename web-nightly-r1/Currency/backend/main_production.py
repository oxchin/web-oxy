#!/usr/bin/env python3
"""
Kconvert - Production-Grade Currency Converter API
Enhanced security, performance, and filtering engine

Copyright (c) 2025 Team 6
All rights reserved.
"""

from fastapi import FastAPI, HTTPException, Query, Request, Header, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import Response
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from dotenv import load_dotenv
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from pydantic import BaseModel, field_validator, Field
import os
import time
import httpx
import asyncio
import re
import hashlib
from typing import Optional, Dict, List, Set, Union
from datetime import datetime, timedelta
import logging
from contextlib import asynccontextmanager
import json
from smart_convert_engine import SmartConvertEngine, ConversionResult

# Load environment variables
load_dotenv()

# Enhanced logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Production configuration
SECRET_KEY = os.getenv("JWT_SECRET_KEY")
TWELVE_DATA_API_KEY = os.getenv("TWELVE_DATA_API_KEY")
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")

if not SECRET_KEY or not TWELVE_DATA_API_KEY:
    raise ValueError("JWT_SECRET_KEY and TWELVE_DATA_API_KEY are required")

# Enhanced configuration
TOKEN_EXP_MINUTES = int(os.getenv("TOKEN_EXP_MINUTES", "60"))
RATE_LIMIT = int(os.getenv("RATE_LIMIT_PER_MINUTE", "120"))
AUTH_RATE_LIMIT = int(os.getenv("AUTH_RATE_LIMIT_PER_MINUTE", "60"))
CACHE_TTL = int(os.getenv("CACHE_TTL_SECONDS", "300"))
MAX_CONCURRENT_REQUESTS = int(os.getenv("MAX_CONCURRENT_REQUESTS", "50"))

# Enhanced CORS configuration
CORS_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "https://kconvert.vercel.app",
    "https://*.vercel.app"
]

# Curated 100+ countries currencies (production-grade filtering)
SUPPORTED_CURRENCIES = {
    # Major World Currencies (G20)
    "USD": {"name": "US Dollar", "country": "United States", "region": "North America", "type": "fiat"},
    "EUR": {"name": "Euro", "country": "European Union", "region": "Europe", "type": "fiat"},
    "GBP": {"name": "British Pound", "country": "United Kingdom", "region": "Europe", "type": "fiat"},
    "JPY": {"name": "Japanese Yen", "country": "Japan", "region": "Asia", "type": "fiat"},
    "CNY": {"name": "Chinese Yuan", "country": "China", "region": "Asia", "type": "fiat"},
    "CAD": {"name": "Canadian Dollar", "country": "Canada", "region": "North America", "type": "fiat"},
    "AUD": {"name": "Australian Dollar", "country": "Australia", "region": "Oceania", "type": "fiat"},
    "CHF": {"name": "Swiss Franc", "country": "Switzerland", "region": "Europe", "type": "fiat"},
    "KRW": {"name": "South Korean Won", "country": "South Korea", "region": "Asia", "type": "fiat"},
    "INR": {"name": "Indian Rupee", "country": "India", "region": "Asia", "type": "fiat"},
    "BRL": {"name": "Brazilian Real", "country": "Brazil", "region": "South America", "type": "fiat"},
    "RUB": {"name": "Russian Ruble", "country": "Russia", "region": "Europe", "type": "fiat"},
    "MXN": {"name": "Mexican Peso", "country": "Mexico", "region": "North America", "type": "fiat"},
    "ZAR": {"name": "South African Rand", "country": "South Africa", "region": "Africa", "type": "fiat"},
    "TRY": {"name": "Turkish Lira", "country": "Turkey", "region": "Asia", "type": "fiat"},
    "SAR": {"name": "Saudi Riyal", "country": "Saudi Arabia", "region": "Middle East", "type": "fiat"},
    "ARS": {"name": "Argentine Peso", "country": "Argentina", "region": "South America", "type": "fiat"},
    "IDR": {"name": "Indonesian Rupiah", "country": "Indonesia", "region": "Asia", "type": "fiat"},
    
    # European Currencies
    "SEK": {"name": "Swedish Krona", "country": "Sweden", "region": "Europe", "type": "fiat"},
    "NOK": {"name": "Norwegian Krone", "country": "Norway", "region": "Europe", "type": "fiat"},
    "DKK": {"name": "Danish Krone", "country": "Denmark", "region": "Europe", "type": "fiat"},
    "PLN": {"name": "Polish Zloty", "country": "Poland", "region": "Europe", "type": "fiat"},
    "CZK": {"name": "Czech Koruna", "country": "Czech Republic", "region": "Europe", "type": "fiat"},
    "HUF": {"name": "Hungarian Forint", "country": "Hungary", "region": "Europe", "type": "fiat"},
    "RON": {"name": "Romanian Leu", "country": "Romania", "region": "Europe", "type": "fiat"},
    "BGN": {"name": "Bulgarian Lev", "country": "Bulgaria", "region": "Europe", "type": "fiat"},
    "HRK": {"name": "Croatian Kuna", "country": "Croatia", "region": "Europe", "type": "fiat"},
    "ISK": {"name": "Icelandic Krona", "country": "Iceland", "region": "Europe", "type": "fiat"},
    
    # Asia-Pacific
    "SGD": {"name": "Singapore Dollar", "country": "Singapore", "region": "Asia", "type": "fiat"},
    "HKD": {"name": "Hong Kong Dollar", "country": "Hong Kong", "region": "Asia", "type": "fiat"},
    "TWD": {"name": "Taiwan Dollar", "country": "Taiwan", "region": "Asia", "type": "fiat"},
    "THB": {"name": "Thai Baht", "country": "Thailand", "region": "Asia", "type": "fiat"},
    "MYR": {"name": "Malaysian Ringgit", "country": "Malaysia", "region": "Asia", "type": "fiat"},
    "PHP": {"name": "Philippine Peso", "country": "Philippines", "region": "Asia", "type": "fiat"},
    "VND": {"name": "Vietnamese Dong", "country": "Vietnam", "region": "Asia", "type": "fiat"},
    "NZD": {"name": "New Zealand Dollar", "country": "New Zealand", "region": "Oceania", "type": "fiat"},
    "PKR": {"name": "Pakistani Rupee", "country": "Pakistan", "region": "Asia", "type": "fiat"},
    "BDT": {"name": "Bangladeshi Taka", "country": "Bangladesh", "region": "Asia", "type": "fiat"},
    "LKR": {"name": "Sri Lankan Rupee", "country": "Sri Lanka", "region": "Asia", "type": "fiat"},
    "MMK": {"name": "Myanmar Kyat", "country": "Myanmar", "region": "Asia", "type": "fiat"},
    
    # Middle East & Africa
    "AED": {"name": "UAE Dirham", "country": "United Arab Emirates", "region": "Middle East", "type": "fiat"},
    "QAR": {"name": "Qatari Riyal", "country": "Qatar", "region": "Middle East", "type": "fiat"},
    "KWD": {"name": "Kuwaiti Dinar", "country": "Kuwait", "region": "Middle East", "type": "fiat"},
    "BHD": {"name": "Bahraini Dinar", "country": "Bahrain", "region": "Middle East", "type": "fiat"},
    "OMR": {"name": "Omani Rial", "country": "Oman", "region": "Middle East", "type": "fiat"},
    "JOD": {"name": "Jordanian Dinar", "country": "Jordan", "region": "Middle East", "type": "fiat"},
    "ILS": {"name": "Israeli Shekel", "country": "Israel", "region": "Middle East", "type": "fiat"},
    "EGP": {"name": "Egyptian Pound", "country": "Egypt", "region": "Africa", "type": "fiat"},
    "NGN": {"name": "Nigerian Naira", "country": "Nigeria", "region": "Africa", "type": "fiat"},
    "KES": {"name": "Kenyan Shilling", "country": "Kenya", "region": "Africa", "type": "fiat"},
    "GHS": {"name": "Ghanaian Cedi", "country": "Ghana", "region": "Africa", "type": "fiat"},
    "MAD": {"name": "Moroccan Dirham", "country": "Morocco", "region": "Africa", "type": "fiat"},
    "TND": {"name": "Tunisian Dinar", "country": "Tunisia", "region": "Africa", "type": "fiat"},
    "ETB": {"name": "Ethiopian Birr", "country": "Ethiopia", "region": "Africa", "type": "fiat"},
    "UGX": {"name": "Ugandan Shilling", "country": "Uganda", "region": "Africa", "type": "fiat"},
    
    # Americas
    "CLP": {"name": "Chilean Peso", "country": "Chile", "region": "South America", "type": "fiat"},
    "COP": {"name": "Colombian Peso", "country": "Colombia", "region": "South America", "type": "fiat"},
    "PEN": {"name": "Peruvian Sol", "country": "Peru", "region": "South America", "type": "fiat"},
    "UYU": {"name": "Uruguayan Peso", "country": "Uruguay", "region": "South America", "type": "fiat"},
    "BOB": {"name": "Bolivian Boliviano", "country": "Bolivia", "region": "South America", "type": "fiat"},
    "PYG": {"name": "Paraguayan Guarani", "country": "Paraguay", "region": "South America", "type": "fiat"},
    "GTQ": {"name": "Guatemalan Quetzal", "country": "Guatemala", "region": "Central America", "type": "fiat"},
    "CRC": {"name": "Costa Rican Colon", "country": "Costa Rica", "region": "Central America", "type": "fiat"},
    "PAB": {"name": "Panamanian Balboa", "country": "Panama", "region": "Central America", "type": "fiat"},
    "DOP": {"name": "Dominican Peso", "country": "Dominican Republic", "region": "Caribbean", "type": "fiat"},
    "JMD": {"name": "Jamaican Dollar", "country": "Jamaica", "region": "Caribbean", "type": "fiat"},
    "TTD": {"name": "Trinidad Dollar", "country": "Trinidad and Tobago", "region": "Caribbean", "type": "fiat"},
}

# Top 30 Cryptocurrencies (production filtering)
SUPPORTED_CRYPTO = {
    "BTC": {"name": "Bitcoin", "symbol": "BTC/USD", "type": "crypto", "market_cap_rank": 1},
    "ETH": {"name": "Ethereum", "symbol": "ETH/USD", "type": "crypto", "market_cap_rank": 2},
    "USDT": {"name": "Tether", "symbol": "USDT/USD", "type": "crypto", "market_cap_rank": 3},
    "BNB": {"name": "BNB", "symbol": "BNB/USD", "type": "crypto", "market_cap_rank": 4},
    "SOL": {"name": "Solana", "symbol": "SOL/USD", "type": "crypto", "market_cap_rank": 5},
    "USDC": {"name": "USD Coin", "symbol": "USDC/USD", "type": "crypto", "market_cap_rank": 6},
    "XRP": {"name": "XRP", "symbol": "XRP/USD", "type": "crypto", "market_cap_rank": 7},
    "DOGE": {"name": "Dogecoin", "symbol": "DOGE/USD", "type": "crypto", "market_cap_rank": 8},
    "ADA": {"name": "Cardano", "symbol": "ADA/USD", "type": "crypto", "market_cap_rank": 9},
    "TRX": {"name": "TRON", "symbol": "TRX/USD", "type": "crypto", "market_cap_rank": 10},
    "AVAX": {"name": "Avalanche", "symbol": "AVAX/USD", "type": "crypto", "market_cap_rank": 11},
    "SHIB": {"name": "Shiba Inu", "symbol": "SHIB/USD", "type": "crypto", "market_cap_rank": 12},
    "TON": {"name": "Toncoin", "symbol": "TON/USD", "type": "crypto", "market_cap_rank": 13},
    "LINK": {"name": "Chainlink", "symbol": "LINK/USD", "type": "crypto", "market_cap_rank": 14},
    "DOT": {"name": "Polkadot", "symbol": "DOT/USD", "type": "crypto", "market_cap_rank": 15},
    "MATIC": {"name": "Polygon", "symbol": "MATIC/USD", "type": "crypto", "market_cap_rank": 16},
    "BCH": {"name": "Bitcoin Cash", "symbol": "BCH/USD", "type": "crypto", "market_cap_rank": 17},
    "ICP": {"name": "Internet Computer", "symbol": "ICP/USD", "type": "crypto", "market_cap_rank": 18},
    "UNI": {"name": "Uniswap", "symbol": "UNI/USD", "type": "crypto", "market_cap_rank": 19},
    "LTC": {"name": "Litecoin", "symbol": "LTC/USD", "type": "crypto", "market_cap_rank": 20},
    "NEAR": {"name": "NEAR Protocol", "symbol": "NEAR/USD", "type": "crypto", "market_cap_rank": 21},
    "APT": {"name": "Aptos", "symbol": "APT/USD", "type": "crypto", "market_cap_rank": 22},
    "STX": {"name": "Stacks", "symbol": "STX/USD", "type": "crypto", "market_cap_rank": 23},
    "XLM": {"name": "Stellar", "symbol": "XLM/USD", "type": "crypto", "market_cap_rank": 24},
    "ATOM": {"name": "Cosmos", "symbol": "ATOM/USD", "type": "crypto", "market_cap_rank": 25},
    "HBAR": {"name": "Hedera", "symbol": "HBAR/USD", "type": "crypto", "market_cap_rank": 26},
    "FIL": {"name": "Filecoin", "symbol": "FIL/USD", "type": "crypto", "market_cap_rank": 27},
    "VET": {"name": "VeChain", "symbol": "VET/USD", "type": "crypto", "market_cap_rank": 28},
    "ETC": {"name": "Ethereum Classic", "symbol": "ETC/USD", "type": "crypto", "market_cap_rank": 29},
    "ALGO": {"name": "Algorand", "symbol": "ALGO/USD", "type": "crypto", "market_cap_rank": 30},
}

# Combine all supported assets
ALL_SUPPORTED_ASSETS = {**SUPPORTED_CURRENCIES, **SUPPORTED_CRYPTO}

# Optimized in-memory rate limiter for pure Python performance
limiter = Limiter(key_func=get_remote_address)

# Ultra-fast HTTP client optimized for pure Python performance
http_client = httpx.AsyncClient(
    timeout=httpx.Timeout(10.0, connect=3.0),
    limits=httpx.Limits(
        max_keepalive_connections=100,
        max_connections=500,
        keepalive_expiry=60.0
    ),
    headers={
        "User-Agent": "Kconvert/4.0 (FastAPI-Optimized)",
        "Accept-Encoding": "gzip, deflate",
        "Connection": "keep-alive"
    },
    http2=True
)

# Optimized in-memory cache for pure Python performance
class FastCacheManager:
    def __init__(self):
        self.cache = {}
        self.timestamps = {}
        logger.info("FastAPI in-memory cache initialized")
    
    async def get(self, key: str) -> Optional[Dict]:
        if key in self.cache:
            if time.time() - self.timestamps[key] < CACHE_TTL:
                return self.cache[key]
            else:
                # Auto-cleanup expired entries
                del self.cache[key]
                del self.timestamps[key]
        return None
    
    async def set(self, key: str, value: Dict, ttl: int = CACHE_TTL):
        self.cache[key] = value
        self.timestamps[key] = time.time()
        
        # Periodic cleanup to prevent memory bloat
        if len(self.cache) % 100 == 0:
            await self._cleanup_expired()
    
    async def delete(self, pattern: str = None):
        if pattern:
            keys_to_delete = [k for k in self.cache.keys() if pattern in k]
            for k in keys_to_delete:
                self.cache.pop(k, None)
                self.timestamps.pop(k, None)
        else:
            self.cache.clear()
            self.timestamps.clear()
    
    async def _cleanup_expired(self):
        """Remove expired cache entries"""
        current_time = time.time()
        expired_keys = [
            k for k, ts in self.timestamps.items() 
            if current_time - ts >= CACHE_TTL
        ]
        for k in expired_keys:
            self.cache.pop(k, None)
            self.timestamps.pop(k, None)

cache_manager = FastCacheManager()

# Initialize Smart Convert Engine
smart_engine = SmartConvertEngine(None, cache_manager)

# Enhanced security models
security = HTTPBearer(auto_error=False)

class EnhancedConvertRequest(BaseModel):
    amount: float = Field(..., gt=0, le=1000000000, description="Amount to convert")
    from_currency: str = Field(..., min_length=3, max_length=10, description="Source currency")
    to_currency: str = Field(..., min_length=3, max_length=10, description="Target currency")
    
    @field_validator('from_currency', 'to_currency')
    @classmethod
    def validate_currency(cls, v):
        v = v.upper().strip()
        if v not in ALL_SUPPORTED_ASSETS:
            raise ValueError(f'Unsupported currency: {v}')
        return v

# Enhanced lifespan management
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("🚀 Kconvert Production Engine starting...")
    yield
    # Shutdown
    await http_client.aclose()
    logger.info("🛑 Kconvert Production Engine stopped")

# Ultra-optimized FastAPI app for maximum performance
app = FastAPI(
    title="Kconvert FastAPI Engine",
    description="Ultra-fast currency converter optimized for pure Python performance",
    version="5.0.0",
    docs_url="/docs" if ENVIRONMENT == "development" else None,
    redoc_url="/redoc" if ENVIRONMENT == "development" else None,
    lifespan=lifespan,
    # Performance optimizations
    generate_unique_id_function=lambda route: f"{route.tags[0] if route.tags else 'default'}-{route.name}",
    swagger_ui_parameters={"syntaxHighlight": False, "tryItOutEnabled": False}
)

# Enhanced middleware stack
app.add_middleware(GZipMiddleware, minimum_size=1000)
app.add_middleware(TrustedHostMiddleware, allowed_hosts=["*"])
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
    max_age=3600,
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Enhanced JWT functions
def create_jwt(owner: str = "oxchin", additional_claims: Dict = None) -> str:
    now = time.time()
    payload = {
        "owner": owner,
        "iat": now,
        "exp": now + (TOKEN_EXP_MINUTES * 60),
        "jti": hashlib.md5(f"{owner}{now}".encode()).hexdigest()[:16]
    }
    if additional_claims:
        payload.update(additional_claims)
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")

async def verify_jwt(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict:
    if not credentials:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        if payload.get("exp", 0) < time.time():
            raise HTTPException(status_code=401, detail="Token expired")
        if payload.get("owner") != "oxchin":
            raise HTTPException(status_code=403, detail="Invalid token owner")
        return payload
    except JWTError as e:
        logger.warning(f"JWT verification failed: {str(e)}")
        raise HTTPException(status_code=403, detail="Invalid token")

# Enhanced API endpoints
@app.get("/health")
async def health_check():
    """Enhanced health check with Smart Engine status"""
    start_time = time.time()
    
    # Test smart engine
    engine_health = await smart_engine.health_check()
    
    health_status = {
        "status": "healthy",
        "timestamp": time.time(),
        "version": "5.0.0",
        "environment": ENVIRONMENT,
        "smart_engine": engine_health
    }

@app.get("/")
async def root():
    return {
        "service": "Kconvert Production Engine",
        "status": "operational",
        "version": "5.0.0",
        "features": [
            "enhanced_security",
            "fast_memory_caching", 
            "connection_pooling",
            "rate_limiting",
            "filtered_assets",
            "production_grade"
        ],
        "supported_assets": {
            "fiat_currencies": len(SUPPORTED_CURRENCIES),
            "cryptocurrencies": len(SUPPORTED_CRYPTO),
            "total": len(ALL_SUPPORTED_ASSETS)
        },
        "environment": ENVIRONMENT,
        "timestamp": time.time()
    }

@app.post("/api/convert")
@limiter.limit(f"{RATE_LIMIT}/minute")
async def convert_currency(
    request: Request,
    convert_request: EnhancedConvertRequest,
    payload: Dict = Depends(verify_jwt)
):
    """Smart multi-hop currency conversion with advanced fallback strategies"""
    try:
        start_time = time.time()
        
        from_currency = convert_request.from_currency.upper()
        to_currency = convert_request.to_currency.upper()
        amount = convert_request.amount
        
        # Use Smart Convert Engine
        result: ConversionResult = await smart_engine.convert(from_currency, to_currency, amount)
        
        if result.rate is None:
            raise HTTPException(status_code=500, detail=f"Conversion not available for {from_currency}/{to_currency}: {result.error}")
        
        conversion_result = {
            "rate": result.rate,
            "converted_amount": result.amount,
            "conversion_path": result.method.value,
            "confidence": result.confidence,
            "latency_ms": result.latency_ms,
            "bridge_rates": result.bridge_rates,
            "cached": result.cached,
            "metadata": {
                "conversion_type": "smart_engine",
                "method": result.method.value,
                "confidence_score": result.confidence,
                "engine_version": "5.0.0"
            }
        }
        
        response_time = time.time() - start_time
        
        return {
            "from_currency": from_currency,
            "to_currency": to_currency,
            "amount": amount,
            "rate": conversion_result["rate"],
            "converted_amount": conversion_result["converted_amount"],
            "conversion_method": conversion_result["conversion_path"],
            "confidence_score": conversion_result["confidence"],
            "engine_latency_ms": conversion_result["latency_ms"],
            "total_response_time_ms": response_time * 1000,
            "bridge_rates": conversion_result.get("bridge_rates"),
            "cached": conversion_result.get("cached", False),
            "metadata": conversion_result.get("metadata", {}),
            "data_source": "smart-convert-engine-v5"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Smart conversion error: {str(e)}")
        raise HTTPException(status_code=500, detail="Smart conversion service temporarily unavailable")

# Enhanced batch conversion endpoint for comprehensive testing
@app.post("/api/convert/batch")
@limiter.limit(f"{RATE_LIMIT}/minute")
async def batch_convert_currencies(
    request: Request,
    credentials: Dict = Depends(verify_jwt)
):
    """Batch conversion endpoint for testing multiple cross-asset pairs"""
    start_time = time.time()
    
    # Parse request body
    try:
        body = await request.json()
        conversions = body.get("conversions", [])
        if not conversions:
            raise HTTPException(status_code=400, detail="No conversions provided")
        
        if len(conversions) > 50:  # Limit batch size
            raise HTTPException(status_code=400, detail="Maximum 50 conversions per batch")
    except Exception as e:
        raise HTTPException(status_code=400, detail="Invalid request format")
    
    # Enhanced batch processing with concurrency control
    semaphore = asyncio.Semaphore(20)  # Limit concurrent conversions
    
    async def process_conversion(conversion_data: Dict) -> Dict:
        async with semaphore:
            try:
                from_currency = conversion_data.get("from_currency", "").upper()
                to_currency = conversion_data.get("to_currency", "").upper()
                amount = float(conversion_data.get("amount", 1.0))
                
                if not from_currency or not to_currency:
                    return {
                        "from_currency": from_currency,
                        "to_currency": to_currency,
                        "error": "Missing currency codes",
                        "success": False
                    }
                
                conversion_result = await convert_cross_assets(from_currency, to_currency, amount)
                
                return {
                    "from_currency": from_currency,
                    "to_currency": to_currency,
                    "amount": amount,
                    "converted_amount": conversion_result["converted_amount"],
                    "exchange_rate": conversion_result["rate"],
                    "conversion_path": conversion_result["conversion_path"],
                    "conversion_steps": conversion_result["steps"],
                    "symbol_used": conversion_result.get("symbol_used"),
                    "bridge_rates": conversion_result.get("bridge_rates"),
                    "metadata": conversion_result.get("metadata", {}),
                    "success": True
                }
                
            except Exception as e:
                return {
                    "from_currency": conversion_data.get("from_currency", ""),
                    "to_currency": conversion_data.get("to_currency", ""),
                    "error": str(e),
                    "success": False
                }
    
    # Execute batch conversions
    tasks = [process_conversion(conv) for conv in conversions]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # Process results
    successful_conversions = [r for r in results if isinstance(r, dict) and r.get("success", False)]
    failed_conversions = [r for r in results if isinstance(r, dict) and not r.get("success", False)]
    
    processing_time = time.time() - start_time
    
    return {
        "results": results,
        "summary": {
            "total_requested": len(conversions),
            "successful": len(successful_conversions),
            "failed": len(failed_conversions),
            "success_rate": f"{(len(successful_conversions)/len(conversions)*100):.1f}%" if conversions else "0%",
            "processing_time_ms": round(processing_time * 1000, 2)
        },
        "timestamp": time.time(),
        "data_source": "twelve-data-cross-asset"
    }

@app.get("/api/timeseries/{symbol}")
@limiter.limit(f"{RATE_LIMIT}/minute")
async def get_timeseries(
    request: Request,
    symbol: str,
    interval: str = Query("1h", regex="^(1min|5min|15min|1h|4h|1day)$"),
    outputsize: int = Query(100, ge=1, le=5000),
    credentials: Dict = Depends(verify_jwt)
):
    """Get historical timeseries data with enhanced caching"""
    
    # Validate symbol format
    symbol = symbol.upper().replace("-", "/")
    if not re.match(r'^[A-Z]{2,10}/[A-Z]{2,10}$', symbol):
        raise HTTPException(status_code=400, detail="Invalid symbol format")
    
    base, target = symbol.split("/")
    if base not in ALL_SUPPORTED_ASSETS or target not in ALL_SUPPORTED_ASSETS:
        raise HTTPException(status_code=400, detail="Unsupported currency pair")
    
    try:
        data = await fetch_twelve_data_optimized(
            symbol,
            "time_series",
            interval=interval,
            outputsize=outputsize,
            timezone="UTC"
        )
        
        # Transform for frontend consumption
        if "values" in data and data["values"]:
            # Reverse chronological order for charts
            values = list(reversed(data["values"]))
            
            chart_data = {
                "symbol": symbol,
                "interval": interval,
                "meta": data.get("meta", {}),
                "values": values,
                "count": len(values),
                "timestamp": time.time(),
                "processing_time_ms": data.get("_meta", {}).get("response_time", 0) * 1000,
                "cached": data.get("_meta", {}).get("cached", False),
                "data_source": "twelve-data"
            }
        else:
            # Generate fallback data
            chart_data = await generate_fallback_timeseries(symbol, interval, outputsize)
        
        return chart_data
        
    except Exception as e:
        logger.error(f"Timeseries error for {symbol}: {str(e)}")
        return await generate_fallback_timeseries(symbol, interval, outputsize)

async def generate_fallback_timeseries(symbol: str, interval: str, outputsize: int) -> Dict:
    """Generate realistic fallback timeseries data"""
    import random
    from datetime import datetime, timedelta
    
    base, target = symbol.split("/")
    
    # Base rates for common pairs
    base_rates = {
        "USD/EUR": 0.85, "USD/GBP": 0.73, "USD/JPY": 150.0, "USD/SGD": 1.35,
        "EUR/USD": 1.18, "GBP/USD": 1.27, "BTC/USD": 45000.0, "ETH/USD": 2500.0
    }
    
    base_rate = base_rates.get(symbol, 1.0)
    
    # Time intervals in minutes
    interval_minutes = {
        "1min": 1, "5min": 5, "15min": 15, "1h": 60, "4h": 240, "1day": 1440
    }
    
    minutes = interval_minutes.get(interval, 60)
    now = datetime.utcnow()
    
    values = []
    current_price = base_rate
    
    for i in range(outputsize):
        # Realistic price movement
        volatility = 0.001 if "USD" in symbol else 0.02  # Crypto more volatile
        change = random.uniform(-volatility, volatility)
        current_price *= (1 + change)
        
        timestamp = now - timedelta(minutes=minutes * (outputsize - 1 - i))
        
        # Generate OHLC
        high = current_price * random.uniform(1.001, 1.01)
        low = current_price * random.uniform(0.99, 0.999)
        open_price = current_price * random.uniform(0.995, 1.005)
        
        values.append({
            "datetime": timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            "open": str(round(open_price, 6)),
            "high": str(round(high, 6)),
            "low": str(round(low, 6)),
            "close": str(round(current_price, 6)),
            "volume": "0"
        })
    
    return {
        "symbol": symbol,
        "interval": interval,
        "values": values,
        "count": len(values),
        "timestamp": time.time(),
        "source": "fallback-mock"
    }
if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(
        "main_production:app",
        host="0.0.0.0",
        port=port,
        reload=False,
        workers=1,
        access_log=True,
        log_level="info"
    )
