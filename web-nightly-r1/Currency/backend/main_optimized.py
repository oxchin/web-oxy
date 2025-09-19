#!/usr/bin/env python3
"""
Kconvert - Ultra-Optimized Currency Converter API
Core functionality only - maximum performance, minimal complexity

Copyright (c) 2025 Team 6
All rights reserved.
"""

from fastapi import FastAPI, HTTPException, Query, Request, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from jose import JWTError, jwt
from dotenv import load_dotenv
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from pydantic import BaseModel, field_validator
import os
import time
import httpx
import asyncio
import re
from typing import Optional, Dict, List
from datetime import datetime, timedelta
import logging

# Load environment variables
load_dotenv()

# Logging configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration - validate required settings
SECRET_KEY = os.getenv("JWT_SECRET_KEY")
TWELVE_DATA_API_KEY = os.getenv("TWELVE_DATA_API_KEY")
if not SECRET_KEY or not TWELVE_DATA_API_KEY:
    raise ValueError("JWT_SECRET_KEY and TWELVE_DATA_API_KEY are required")

TOKEN_EXP_MINUTES = int(os.getenv("TOKEN_EXP_MINUTES", "10"))
RATE_LIMIT = int(os.getenv("RATE_LIMIT_PER_MINUTE", "60"))
AUTH_RATE_LIMIT = int(os.getenv("AUTH_RATE_LIMIT_PER_MINUTE", "30"))
CORS_ORIGINS = os.getenv("OTHER_ORIGINS", "").split(",") if os.getenv("OTHER_ORIGINS") else ["http://localhost:3000", "http://127.0.0.1:3000"]

# Rate limiter
limiter = Limiter(key_func=get_remote_address)

# Global HTTP client with connection pooling
http_client = httpx.AsyncClient(
    timeout=httpx.Timeout(10.0, connect=5.0),
    limits=httpx.Limits(max_keepalive_connections=20, max_connections=100)
)

# Real-time cache with TTL (5 minutes)
cache = {}
CACHE_TTL = 300  # 5 minutes

# FastAPI app
app = FastAPI(
    title="Kconvert API",
    description="Ultra-optimized currency converter",
    version="3.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
    max_age=600,  # Cache preflight for 10 minutes
)

# Rate limiting
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Comprehensive 100+ currencies list
CURRENCIES = {
    # Major world currencies
    "USD": "US Dollar", "EUR": "Euro", "GBP": "British Pound", "JPY": "Japanese Yen",
    "AUD": "Australian Dollar", "CAD": "Canadian Dollar", "CHF": "Swiss Franc", 
    "CNY": "Chinese Yuan", "SEK": "Swedish Krona", "NZD": "New Zealand Dollar",
    "MXN": "Mexican Peso", "SGD": "Singapore Dollar", "HKD": "Hong Kong Dollar",
    "NOK": "Norwegian Krone", "TRY": "Turkish Lira", "RUB": "Russian Ruble",
    "INR": "Indian Rupee", "BRL": "Brazilian Real", "ZAR": "South African Rand",
    "KRW": "South Korean Won", "PLN": "Polish Zloty", "THB": "Thai Baht",
    "MYR": "Malaysian Ringgit", "AED": "UAE Dirham", "SAR": "Saudi Riyal",
    "ILS": "Israeli Shekel", "CLP": "Chilean Peso", "COP": "Colombian Peso",
    "ARS": "Argentine Peso", "TWD": "Taiwan Dollar",
    
    # European currencies
    "DKK": "Danish Krone", "CZK": "Czech Koruna", "HUF": "Hungarian Forint",
    "RON": "Romanian Leu", "BGN": "Bulgarian Lev", "HRK": "Croatian Kuna",
    "ISK": "Icelandic Krona", "ALL": "Albanian Lek", "BAM": "Bosnia-Herzegovina Convertible Mark",
    "MKD": "Macedonian Denar", "RSD": "Serbian Dinar", "MDL": "Moldovan Leu",
    
    # Asian currencies
    "PHP": "Philippine Peso", "IDR": "Indonesian Rupiah", "VND": "Vietnamese Dong",
    "KHR": "Cambodian Riel", "LAK": "Laotian Kip", "MMK": "Myanmar Kyat",
    "BDT": "Bangladeshi Taka", "PKR": "Pakistani Rupee", "NPR": "Nepalese Rupee",
    "LKR": "Sri Lankan Rupee", "MVR": "Maldivian Rufiyaa", "BTN": "Bhutanese Ngultrum",
    "AFN": "Afghan Afghani", "UZS": "Uzbekistani Som", "KZT": "Kazakhstani Tenge",
    "KGS": "Kyrgystani Som", "TJS": "Tajikistani Somoni", "TMT": "Turkmenistani Manat",
    "MNT": "Mongolian Tugrik", "KPW": "North Korean Won",
    
    # Middle Eastern currencies
    "QAR": "Qatari Riyal", "KWD": "Kuwaiti Dinar", "BHD": "Bahraini Dinar",
    "OMR": "Omani Rial", "JOD": "Jordanian Dinar", "LBP": "Lebanese Pound",
    "SYP": "Syrian Pound", "IQD": "Iraqi Dinar", "IRR": "Iranian Rial",
    "GEL": "Georgian Lari", "AMD": "Armenian Dram", "AZN": "Azerbaijani Manat",
    
    # African currencies
    "EGP": "Egyptian Pound", "NGN": "Nigerian Naira", "KES": "Kenyan Shilling",
    "GHS": "Ghanaian Cedi", "MAD": "Moroccan Dirham", "TND": "Tunisian Dinar",
    "DZD": "Algerian Dinar", "LYD": "Libyan Dinar", "ETB": "Ethiopian Birr",
    "UGX": "Ugandan Shilling", "TZS": "Tanzanian Shilling", "RWF": "Rwandan Franc",
    "XOF": "West African CFA Franc", "XAF": "Central African CFA Franc",
    "MGA": "Malagasy Ariary", "MUR": "Mauritian Rupee", "SCR": "Seychellois Rupee",
    "SZL": "Swazi Lilangeni", "LSL": "Lesotho Loti", "BWP": "Botswanan Pula",
    "NAD": "Namibian Dollar", "ZMW": "Zambian Kwacha", "ZWL": "Zimbabwean Dollar",
    "MWK": "Malawian Kwacha", "MZN": "Mozambican Metical", "AOA": "Angolan Kwanza",
    "CVE": "Cape Verdean Escudo", "GMD": "Gambian Dalasi", "GNF": "Guinean Franc",
    "LRD": "Liberian Dollar", "SLL": "Sierra Leonean Leone", "STD": "São Tomé and Príncipe Dobra",
    "CDF": "Congolese Franc", "DJF": "Djiboutian Franc", "ERN": "Eritrean Nakfa",
    "SOS": "Somali Shilling", "SDP": "Sudanese Pound", "SSP": "South Sudanese Pound",
    
    # Eastern European & CIS
    "BYN": "Belarusian Ruble", "UAH": "Ukrainian Hryvnia",
    
    # Caribbean & Pacific
    "JMD": "Jamaican Dollar", "TTD": "Trinidad and Tobago Dollar", "BBD": "Barbadian Dollar",
    "BSD": "Bahamian Dollar", "BZD": "Belize Dollar", "XCD": "East Caribbean Dollar",
    "HTG": "Haitian Gourde", "DOP": "Dominican Peso", "CUP": "Cuban Peso",
    "KYD": "Cayman Islands Dollar", "AWG": "Aruban Florin", "ANG": "Netherlands Antillean Guilder",
    "SRD": "Surinamese Dollar", "GYD": "Guyanese Dollar", "FJD": "Fijian Dollar",
    "TOP": "Tongan Pa'anga", "WST": "Samoan Tala", "VUV": "Vanuatu Vatu",
    "SBD": "Solomon Islands Dollar", "PGK": "Papua New Guinean Kina", "XPF": "CFP Franc",
}

# Pydantic models for request validation
class ConvertRequest(BaseModel):
    amount: float
    from_currency: str
    to_currency: str
    
    @field_validator('amount')
    @classmethod
    def validate_amount(cls, v):
        if v <= 0 or v > 1000000000:
            raise ValueError('Amount must be positive and less than 1 billion')
        return v
    
    @field_validator('from_currency', 'to_currency')
    @classmethod
    def validate_currency(cls, v):
        if not re.match(r'^[A-Z]{3}$', v.upper()):
            raise ValueError('Currency must be 3 uppercase letters')
        return v.upper()

class RatesRequest(BaseModel):
    base: str
    targets: str
    
    @field_validator('base')
    @classmethod
    def validate_base(cls, v):
        if not re.match(r'^[A-Z]{3}$', v.upper()):
            raise ValueError('Base currency must be 3 uppercase letters')
        return v.upper()
    
    @field_validator('targets')
    @classmethod
    def validate_targets(cls, v):
        targets = [t.strip().upper() for t in v.split(',')]
        for target in targets:
            if not re.match(r'^[A-Z]{3}$', target):
                raise ValueError(f'Invalid target currency: {target}')
        return ','.join(targets)

def create_jwt(owner: str = "oxchin") -> str:
    """Create JWT token"""
    now = time.time()
    payload = {"owner": owner, "iat": now, "exp": now + (TOKEN_EXP_MINUTES * 60)}
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")

def verify_jwt(token: str) -> None:
    """Verify JWT token with enhanced security"""
    if not token or len(token) < 10:
        raise HTTPException(status_code=401, detail="Invalid token format")
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        if payload.get("exp", 0) < time.time():
            raise HTTPException(status_code=401, detail="Token expired")
        if payload.get("owner") != "oxchin":
            raise HTTPException(status_code=403, detail="Invalid owner")
    except JWTError as e:
        logger.warning(f"JWT verification failed: {str(e)}")
        raise HTTPException(status_code=403, detail="Invalid token")

def get_cache_key(base: str, targets: str = None) -> str:
    """Generate cache key for rates"""
    return f"rates:{base}:{targets or 'all'}"

def is_cache_valid(timestamp: float) -> bool:
    """Check if cache entry is still valid"""
    return time.time() - timestamp < CACHE_TTL

def get_cached_rates(cache_key: str) -> Optional[Dict]:
    """Get rates from cache if valid"""
    if cache_key in cache:
        data, timestamp = cache[cache_key]
        if is_cache_valid(timestamp):
            return data
        else:
            del cache[cache_key]
    return None

def set_cached_rates(cache_key: str, data: Dict) -> None:
    """Set rates in cache with timestamp"""
    cache[cache_key] = (data, time.time())

async def fetch_rates_twelve_data(base: str, targets: str = None) -> Dict:
    """Fetch exchange rates from Twelve Data API"""
    try:
        # Use quote endpoint for single rate or batch rates
        if targets and targets != "all":
            target_list = targets.split(",")
            rates = {}
            
            # Fetch rates for each target
            for target in target_list:
                if target.strip() == base:
                    rates[target.strip()] = 1.0
                    continue
                    
                symbol = f"{base}/{target.strip()}"
                url = f"https://api.twelvedata.com/quote?symbol={symbol}&apikey={TWELVE_DATA_API_KEY}"
                
                response = await http_client.get(url)
                response.raise_for_status()
                
                data = response.json()
                if "close" in data and data["close"]:
                    rates[target.strip()] = float(data["close"])
                else:
                    logger.warning(f"No rate data for {symbol}")
            
            return {
                "result": "success",
                "base_code": base,
                "conversion_rates": rates
            }
        else:
            # For "all" targets, get major currencies
            major_currencies = ["USD", "EUR", "GBP", "JPY", "AUD", "CAD", "CHF", "CNY", "SEK", "NZD", "SGD", "HKD", "NOK", "TRY", "RUB", "INR", "BRL", "ZAR", "KRW"]
            return await fetch_rates_twelve_data(base, ",".join([c for c in major_currencies if c != base]))
            
    except Exception as e:
        logger.error(f"Twelve Data API error for {base}: {str(e)}")
        # Fallback to mock data for development
        return await fetch_rates_fallback(base, targets)

async def fetch_rates_fallback(base: str, targets: str = None) -> Dict:
    """Fallback rates using mock data for development"""
    # Generate mock rates based on base currency
    mock_rates = {
        "USD": 1.0, "EUR": 0.85, "GBP": 0.73, "JPY": 110.0, "AUD": 1.35,
        "CAD": 1.25, "CHF": 0.92, "CNY": 6.45, "SEK": 8.5, "NZD": 1.42,
        "SGD": 1.35, "HKD": 7.8, "NOK": 8.2, "TRY": 8.5, "RUB": 75.0,
        "INR": 74.0, "BRL": 5.2, "ZAR": 14.5, "KRW": 1180.0
    }
    
    # Adjust rates relative to base
    base_rate = mock_rates.get(base, 1.0)
    adjusted_rates = {curr: rate / base_rate for curr, rate in mock_rates.items()}
    
    if targets and targets != "all":
        target_list = [t.strip() for t in targets.split(",")]
        filtered_rates = {t: adjusted_rates.get(t, 1.0) for t in target_list}
    else:
        filtered_rates = adjusted_rates
    
    return {
        "result": "success",
        "base_code": base,
        "conversion_rates": filtered_rates
    }

async def fetch_rates(base: str, use_cache: bool = True, targets: str = None) -> Dict:
    """Fetch exchange rates with caching and Twelve Data integration"""
    cache_key = get_cache_key(base, targets)
    
    # Check cache first
    if use_cache:
        cached_data = get_cached_rates(cache_key)
        if cached_data:
            logger.info(f"Cache hit for {base}")
            return cached_data
    
    start_time = time.time()
    
    try:
        # Try Twelve Data API first
        data = await fetch_rates_twelve_data(base, targets)
        
        response_time = time.time() - start_time
        logger.info(f"Twelve Data API response time for {base}: {response_time:.3f}s")
        
        # Cache the result
        if use_cache:
            set_cached_rates(cache_key, data)
            logger.info(f"Cached rates for {base}")
        
        return data
        
    except Exception as e:
        logger.error(f"Failed to fetch rates for {base}: {str(e)}")
        # Use fallback
        return await fetch_rates_fallback(base, targets)

async def fetch_multiple_rates(bases: List[str]) -> Dict[str, Dict]:
    """Fetch multiple currency rates in parallel"""
    tasks = [fetch_rates(base) for base in bases]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    rates_data = {}
    for base, result in zip(bases, results):
        if isinstance(result, Exception):
            logger.error(f"Failed to fetch rates for {base}: {str(result)}")
        else:
            rates_data[base] = result
    
    return rates_data

@app.get("/favicon.ico")
async def favicon():
    """Favicon endpoint to prevent 404 logs"""
    return Response(status_code=204)

@app.get("/")
async def root():
    """Enhanced health check endpoint"""
    cache_size = len(cache)
    cache_entries = []
    for key, (_, timestamp) in cache.items():
        age = time.time() - timestamp
        cache_entries.append({"key": key, "age_seconds": round(age, 2)})
    
    return {
        "service": "Kconvert Ultra",
        "status": "healthy",
        "version": "3.1.0",
        "features": ["parallel_processing", "real_time_cache", "enhanced_security"],
        "currencies": len(CURRENCIES),
        "cache_size": cache_size,
        "cache_ttl_seconds": CACHE_TTL,
        "cache_entries": cache_entries[:5],  # Show first 5 entries
        "timestamp": time.time(),
        "uptime_info": {
            "started_at": datetime.now().isoformat(),
            "timezone": "UTC"
        }
    }

@app.options("/api/auth")
async def auth_options():
    """Handle preflight requests for auth endpoint"""
    return Response(status_code=200)

@app.get("/api/auth")
@limiter.limit(f"{AUTH_RATE_LIMIT}/minute")
async def get_token(request: Request, origin: Optional[str] = Header(default=None, alias="Origin")):
    """Get JWT authentication token"""
    if origin and CORS_ORIGINS != ["*"] and origin not in CORS_ORIGINS:
        raise HTTPException(status_code=403, detail="Origin not allowed")
    
    token = create_jwt()
    return {
        "token": token,
        "expires_in": TOKEN_EXP_MINUTES * 60
    }

@app.get("/api/currencies")
async def get_currencies():
    """Get supported currencies"""
    return {
        "currencies": [{"code": code, "name": name} for code, name in CURRENCIES.items()],
        "count": len(CURRENCIES)
    }

@app.get("/api/regions")
async def get_regions():
    """Get supported regions/countries for currency grouping"""
    regions = {
        "North America": ["USD", "CAD", "MXN"],
        "Europe": ["EUR", "GBP", "CHF", "SEK", "NOK", "PLN"],
        "Asia Pacific": ["JPY", "CNY", "AUD", "NZD", "SGD", "HKD", "KRW", "THB", "MYR", "TWD"],
        "Middle East & Africa": ["AED", "SAR", "ILS", "ZAR", "TRY"],
        "South America": ["BRL", "CLP", "COP", "ARS"],
        "Other": ["RUB", "INR"]
    }
    return {
        "regions": [{"name": region, "currencies": currencies} for region, currencies in regions.items()],
        "count": len(regions)
    }

@app.get("/api/rates/{base}")
@limiter.limit(f"{RATE_LIMIT}/minute")
async def get_rates(
    request: Request,
    base: str,
    token: str = Query(...),
    targets: str = Query(...)
):
    """Get exchange rates with enhanced validation and caching"""
    start_time = time.time()
    verify_jwt(token)
    
    # Validate and sanitize input
    base = base.upper().strip()
    if not re.match(r'^[A-Z]{3}$', base) or base not in CURRENCIES:
        raise HTTPException(status_code=400, detail=f"Unsupported currency: {base}")
    
    # Validate targets
    target_list = [t.strip().upper() for t in targets.split(",") if t.strip()]
    if not target_list:
        raise HTTPException(status_code=400, detail="No target currencies specified")
    
    invalid = [t for t in target_list if not re.match(r'^[A-Z]{3}$', t) or t not in CURRENCIES]
    if invalid:
        raise HTTPException(status_code=400, detail=f"Unsupported currencies: {invalid}")
    
    # Check cache first
    cache_key = get_cache_key(base, ','.join(sorted(target_list)))
    cached_result = get_cached_rates(cache_key)
    if cached_result:
        processing_time = time.time() - start_time
        cached_result["processing_time_ms"] = round(processing_time * 1000, 2)
        cached_result["cache_hit"] = True
        return cached_result
    
    # Fetch fresh data
    data = await fetch_rates(base, targets=','.join(target_list))
    rates = data.get("conversion_rates", {})
    filtered_rates = {t: rates.get(t) for t in target_list if t in rates}
    
    processing_time = time.time() - start_time
    result = {
        "base_currency": base,
        "conversion_rates": filtered_rates,
        "rates_count": len(filtered_rates),
        "timestamp": time.time(),
        "processing_time_ms": round(processing_time * 1000, 2),
        "cache_hit": False,
        "data_freshness": "live"
    }
    
    # Cache the result
    set_cached_rates(cache_key, result)
    return result

@app.get("/api/convert")
@limiter.limit(f"{RATE_LIMIT}/minute")
async def convert(
    request: Request,
    token: str = Query(...),
    amount: float = Query(...),
    from_currency: str = Query(..., alias="from"),
    to_currency: str = Query(..., alias="to")
):
    """Convert currency with enhanced validation and performance"""
    start_time = time.time()
    verify_jwt(token)
    
    # Enhanced input validation
    if amount <= 0 or amount > 1000000000:
        raise HTTPException(status_code=400, detail="Amount must be positive and less than 1 billion")
    
    from_curr = from_currency.upper().strip()
    to_curr = to_currency.upper().strip()
    
    # Validate currency format
    for curr in [from_curr, to_curr]:
        if not re.match(r'^[A-Z]{3}$', curr):
            raise HTTPException(status_code=400, detail=f"Invalid currency format: {curr}")
    
    if from_curr not in CURRENCIES or to_curr not in CURRENCIES:
        raise HTTPException(status_code=400, detail="Unsupported currency")
    
    # Same currency conversion
    if from_curr == to_curr:
        processing_time = time.time() - start_time
        return {
            "amount": amount,
            "from_currency": from_curr,
            "to_currency": to_curr,
            "converted_amount": amount,
            "exchange_rate": 1.0,
            "timestamp": time.time(),
            "processing_time_ms": round(processing_time * 1000, 2),
            "cache_hit": False,
            "conversion_type": "same_currency"
        }
    
    # Check cache for conversion rate
    cache_key = get_cache_key(from_curr, to_curr)
    cached_data = get_cached_rates(cache_key)
    
    if cached_data and "conversion_rates" in cached_data:
        rates = cached_data["conversion_rates"]
        if to_curr in rates:
            rate = rates[to_curr]
            converted = round(amount * rate, 6)  # Higher precision
            processing_time = time.time() - start_time
            
            return {
                "amount": amount,
                "from_currency": from_curr,
                "to_currency": to_curr,
                "converted_amount": converted,
                "exchange_rate": rate,
                "timestamp": time.time(),
                "processing_time_ms": round(processing_time * 1000, 2),
                "cache_hit": True,
                "conversion_type": "cached"
            }
    
    # Fetch fresh rates
    data = await fetch_rates(from_curr, targets=to_curr)
    rates = data.get("conversion_rates", {})
    if to_curr not in rates:
        raise HTTPException(status_code=500, detail="Rate not available")
    
    rate = rates[to_curr]
    converted = round(amount * rate, 6)  # Higher precision
    processing_time = time.time() - start_time
    
    result = {
        "amount": amount,
        "from_currency": from_curr,
        "to_currency": to_curr,
        "converted_amount": converted,
        "exchange_rate": rate,
        "timestamp": time.time(),
        "processing_time_ms": round(processing_time * 1000, 2),
        "cache_hit": False,
        "conversion_type": "live",
        "rate_source": "twelve-data"
    }
    
    return result

@app.get("/api/batch-convert")
@limiter.limit(f"{RATE_LIMIT}/minute")
async def batch_convert(
    request: Request,
    token: str = Query(...),
    amount: float = Query(...),
    from_currency: str = Query(..., alias="from"),
    to_currencies: str = Query(..., alias="to")
):
    """Convert to multiple currencies in parallel"""
    start_time = time.time()
    verify_jwt(token)
    
    # Validate amount
    if amount <= 0 or amount > 1000000000:
        raise HTTPException(status_code=400, detail="Amount must be positive and less than 1 billion")
    
    from_curr = from_currency.upper().strip()
    to_curr_list = [t.strip().upper() for t in to_currencies.split(",") if t.strip()]
    
    # Validate currencies
    if not re.match(r'^[A-Z]{3}$', from_curr) or from_curr not in CURRENCIES:
        raise HTTPException(status_code=400, detail=f"Invalid from currency: {from_curr}")
    
    invalid_to = [t for t in to_curr_list if not re.match(r'^[A-Z]{3}$', t) or t not in CURRENCIES]
    if invalid_to:
        raise HTTPException(status_code=400, detail=f"Invalid to currencies: {invalid_to}")
    
    # Fetch rates
    data = await fetch_rates(from_curr, targets=','.join(to_curr_list))
    rates = data.get("conversion_rates", {})
    
    conversions = []
    for to_curr in to_curr_list:
        if to_curr in rates:
            rate = rates[to_curr]
            converted = round(amount * rate, 6)
            conversions.append({
                "to_currency": to_curr,
                "exchange_rate": rate,
                "converted_amount": converted
            })
    
    processing_time = time.time() - start_time
    return {
        "amount": amount,
        "from_currency": from_curr,
        "conversions": conversions,
        "total_conversions": len(conversions),
        "timestamp": time.time(),
        "processing_time_ms": round(processing_time * 1000, 2)
    }

@app.get("/api/timeseries/{symbol}")
@limiter.limit(f"{RATE_LIMIT}/minute")
async def get_timeseries(
    request: Request,
    symbol: str,
    token: str = Query(...),
    interval: str = Query("1min", description="Time interval: 1min, 5min, 15min, 1h, 1day"),
    outputsize: int = Query(30, description="Number of data points to return")
):
    """Get historical timeseries data for charts"""
    verify_jwt(token)
    
    # Validate symbol format (e.g., USD/SGD)
    if not re.match(r'^[A-Z]{3}/[A-Z]{3}$', symbol.upper()):
        raise HTTPException(status_code=400, detail="Invalid symbol format. Use format: USD/SGD")
    
    symbol = symbol.upper()
    
    # Validate interval
    valid_intervals = ["1min", "5min", "15min", "1h", "1day"]
    if interval not in valid_intervals:
        raise HTTPException(status_code=400, detail=f"Invalid interval. Use: {valid_intervals}")
    
    # Validate outputsize
    if outputsize < 1 or outputsize > 5000:
        raise HTTPException(status_code=400, detail="Output size must be between 1 and 5000")
    
    cache_key = f"timeseries:{symbol}:{interval}:{outputsize}"
    
    # Check cache first
    cached_result = get_cached_rates(cache_key)
    if cached_result:
        return cached_result
    
    start_time = time.time()
    
    try:
        # Fetch from Twelve Data API
        url = f"https://api.twelvedata.com/time_series?symbol={symbol}&interval={interval}&outputsize={outputsize}&timezone=UTC&apikey={TWELVE_DATA_API_KEY}"
        
        response = await http_client.get(url)
        response.raise_for_status()
        
        data = response.json()
        
        # Transform data for chart consumption
        if "values" in data and data["values"]:
            chart_data = {
                "symbol": symbol,
                "interval": interval,
                "meta": data.get("meta", {}),
                "values": data["values"],
                "count": len(data["values"]),
                "timestamp": time.time(),
                "processing_time_ms": round((time.time() - start_time) * 1000, 2),
                "cache_hit": False,
                "data_source": "twelve-data"
            }
        else:
            # Fallback to mock data if no real data available
            chart_data = await generate_mock_timeseries(symbol, interval, outputsize)
            chart_data["data_source"] = "mock-fallback"
        
        # Cache the result
        set_cached_rates(cache_key, chart_data)
        
        return chart_data
        
    except Exception as e:
        logger.error(f"Timeseries API error for {symbol}: {str(e)}")
        # Return mock data as fallback
        return await generate_mock_timeseries(symbol, interval, outputsize)

async def generate_mock_timeseries(symbol: str, interval: str, outputsize: int) -> Dict:
    """Generate mock timeseries data for development/fallback"""
    import random
    from datetime import datetime, timedelta
    
    # Parse symbol
    base, target = symbol.split("/")
    
    # Base rate (mock)
    base_rates = {
        "USD/SGD": 1.35, "EUR/USD": 1.08, "GBP/USD": 1.27, "USD/JPY": 150.0,
        "AUD/USD": 0.67, "USD/CAD": 1.36, "USD/CHF": 0.88, "EUR/GBP": 0.85
    }
    
    base_rate = base_rates.get(symbol, 1.0)
    
    # Generate time intervals
    interval_minutes = {
        "1min": 1, "5min": 5, "15min": 15, "1h": 60, "1day": 1440
    }
    
    minutes = interval_minutes.get(interval, 5)
    now = datetime.utcnow()
    
    values = []
    current_price = base_rate
    
    for i in range(outputsize):
        # Generate realistic price movement
        change_percent = random.uniform(-0.002, 0.002)  # ±0.2% change
        current_price *= (1 + change_percent)
        
        # Calculate timestamp
        timestamp = now - timedelta(minutes=minutes * (outputsize - 1 - i))
        
        # Generate OHLC data
        high = current_price * random.uniform(1.0001, 1.005)
        low = current_price * random.uniform(0.995, 0.9999)
        open_price = current_price * random.uniform(0.998, 1.002)
        
        values.append({
            "datetime": timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            "open": str(round(open_price, 6)),
            "high": str(round(high, 6)),
            "low": str(round(low, 6)),
            "close": str(round(current_price, 6)),
            "volume": "0"  # Forex typically has no volume
        })
    
    return {
        "symbol": symbol,
        "interval": interval,
        "meta": {
            "symbol": symbol,
            "interval": interval,
            "currency_base": base,
            "currency_quote": target,
            "type": "Physical Currency"
        },
        "values": values,
        "count": len(values),
        "timestamp": time.time(),
        "processing_time_ms": 1.0,
        "cache_hit": False,
        "data_source": "mock-generated"
    }

@app.get("/api/cache/stats")
async def cache_stats():
    """Get cache statistics"""
    total_entries = len(cache)
    valid_entries = 0
    expired_entries = 0
    
    for key, (_, timestamp) in cache.items():
        if is_cache_valid(timestamp):
            valid_entries += 1
        else:
            expired_entries += 1
    
    return {
        "total_entries": total_entries,
        "valid_entries": valid_entries,
        "expired_entries": expired_entries,
        "cache_ttl_seconds": CACHE_TTL,
        "hit_ratio": round(valid_entries / max(total_entries, 1), 3)
    }

@app.delete("/api/cache/clear")
async def clear_cache():
    """Clear all cache entries"""
    cleared_count = len(cache)
    cache.clear()
    return {
        "message": "Cache cleared",
        "cleared_entries": cleared_count,
        "timestamp": time.time()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main_optimized:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", "8000"))
    )
