#!/bin/bash
# Simple curl test for top 100 fiat currencies - Latest Data

echo "🚀 Testing Top 100 Fiat Currencies with Curl"
echo "=============================================="

# Load environment variables
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

# Test 1: ExchangeRates API (if API key available)
if [ ! -z "$EXCHANGE_API_KEY" ]; then
    echo "🔄 Testing ExchangeRates API..."
    curl -s --connect-timeout 10 --max-time 30 \
         "https://v6.exchangerate-api.com/v6/$EXCHANGE_API_KEY/codes" \
         | jq -r '.supported_codes | length' 2>/dev/null \
         && echo "✅ ExchangeRates API: $(curl -s "https://v6.exchangerate-api.com/v6/$EXCHANGE_API_KEY/codes" | jq -r '.supported_codes | length') currencies" \
         || echo "❌ ExchangeRates API failed"
else
    echo "⚠️  EXCHANGE_API_KEY not found - skipping ExchangeRates API"
fi

# Test 2: ECB Exchange Rate Host (free, no key needed)
echo "🔄 Testing ECB Exchange Rate Host..."
curl -s --connect-timeout 10 --max-time 30 \
     "https://api.exchangerate.host/latest?base=USD" \
     | jq -r '.rates | keys | length' 2>/dev/null \
     && echo "✅ ECB API: $(curl -s "https://api.exchangerate.host/latest?base=USD" | jq -r '.rates | keys | length') currencies" \
     || echo "❌ ECB API failed"

# Test 3: Open Exchange Rates (free tier)
echo "🔄 Testing Open Exchange Rates..."
curl -s --connect-timeout 10 --max-time 30 \
     "https://openexchangerates.org/api/currencies.json" \
     | jq -r 'keys | length' 2>/dev/null \
     && echo "✅ Open Exchange Rates: $(curl -s "https://openexchangerates.org/api/currencies.json" | jq -r 'keys | length') currencies" \
     || echo "❌ Open Exchange Rates failed"

# Test 4: Currency API (free tier)
echo "🔄 Testing Currency API..."
curl -s --connect-timeout 10 --max-time 30 \
     "https://api.currencyapi.com/v3/currencies" \
     | jq -r '.data | keys | length' 2>/dev/null \
     && echo "✅ Currency API: $(curl -s "https://api.currencyapi.com/v3/currencies" | jq -r '.data | keys | length') currencies" \
     || echo "❌ Currency API failed"

echo ""
echo "📊 Current SmartConvertEngine fiat assets: 100 currencies"
echo "🎯 Target: Maintain 95%+ coverage with live data"
echo ""
echo "💡 To update fiat list, run: python3 curl_top_fiat_by_volume.py"
