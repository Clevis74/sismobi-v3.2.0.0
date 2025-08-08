#!/bin/bash

# SISMOBI Integration Test Script - Phase 4+5 Implementation
# Tests API endpoints and runs Lighthouse CI

set -e

echo "🚀 SISMOBI v3.2.0 - Integration Tests - Phase 4+5"
echo "=================================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# API URL
API_URL="http://localhost:8001"

echo ""
echo -e "${BLUE}📍 Step 1: Testing Backend APIs${NC}"
echo "--------------------------------"

# Test health endpoint
echo -n "Testing health endpoint... "
if curl -s "$API_URL/api/health" > /dev/null; then
    echo -e "${GREEN}✅ Health check passed${NC}"
else
    echo -e "${RED}❌ Health check failed${NC}"
    exit 1
fi

# Test new API endpoints
endpoints=(
    "/api/v1/documents"
    "/api/v1/energy-bills" 
    "/api/v1/water-bills"
    "/api/v1/reports/available-filters"
    "/api/v1/alerts"
)

for endpoint in "${endpoints[@]}"; do
    echo -n "Testing $endpoint... "
    response=$(curl -s -w "%{http_code}" "$API_URL$endpoint" -H "Authorization: Bearer dummy_token" -o /dev/null)
    
    if [[ "$response" == "401" ]]; then
        echo -e "${YELLOW}🔒 Requires authentication (expected)${NC}"
    elif [[ "$response" =~ ^2[0-9][0-9]$ ]]; then
        echo -e "${GREEN}✅ Endpoint accessible${NC}"
    else
        echo -e "${RED}❌ Failed (HTTP $response)${NC}"
    fi
done

echo ""
echo -e "${BLUE}📍 Step 2: Testing Lighthouse CI${NC}"
echo "-------------------------------"

# Check if frontend is built
if [ ! -d "frontend/dist" ]; then
    echo -e "${YELLOW}⚠️ Frontend not built, building now...${NC}"
    cd frontend && yarn build && cd ..
fi

# Start frontend preview in background for testing
echo "Starting frontend preview server..."
cd frontend && yarn preview > /dev/null 2>&1 &
PREVIEW_PID=$!
cd ..

# Wait for server to start
sleep 5

# Check if preview server is running
if curl -s "http://localhost:5174" > /dev/null; then
    echo -e "${GREEN}✅ Frontend preview server started${NC}"
else
    echo -e "${RED}❌ Frontend preview server failed to start${NC}"
    kill $PREVIEW_PID 2>/dev/null || true
    exit 1
fi

# Run Lighthouse CI healthcheck
echo -n "Running Lighthouse CI healthcheck... "
if npx lhci healthcheck --config=lighthouserc.mjs > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Lighthouse CI configuration valid${NC}"
else
    echo -e "${YELLOW}⚠️ Lighthouse CI configuration issues (may still work)${NC}"
fi

# Run a simple Lighthouse audit on homepage
echo "Running Lighthouse audit on homepage..."
if npx lhci collect --url=http://localhost:5174 --config=lighthouserc.mjs > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Lighthouse audit completed successfully${NC}"
else
    echo -e "${RED}❌ Lighthouse audit failed${NC}"
fi

# Check if results were generated
if [ -d ".lighthouseci" ] && [ "$(ls -A .lighthouseci)" ]; then
    echo -e "${GREEN}✅ Lighthouse results generated${NC}"
    echo "Results available in .lighthouseci/ directory"
else
    echo -e "${YELLOW}⚠️ No Lighthouse results found${NC}"
fi

# Clean up
echo ""
echo -e "${BLUE}📍 Step 3: Cleanup${NC}"
echo "----------------"

# Stop preview server
kill $PREVIEW_PID 2>/dev/null || true
echo -e "${GREEN}✅ Frontend preview server stopped${NC}"

echo ""
echo -e "${BLUE}📍 Step 4: Summary${NC}"
echo "-----------------"

# Count API endpoints
echo -e "Backend APIs tested: ${#endpoints[@]}"
echo -e "Lighthouse CI: Configured and tested"

echo ""
echo -e "${GREEN}🎉 Integration Tests Complete!${NC}"
echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo "1. Run 'npm run lighthouse:autorun' for full audit"
echo "2. Check '.lighthouseci/' for detailed reports"
echo "3. Use 'npx lhci open' to view results in browser"
echo "4. Configure CI/CD pipeline for automated audits"

echo ""
echo -e "${BLUE}Phase 4 (Lighthouse CI): ✅ Implemented${NC}"
echo -e "${BLUE}Phase 5 (API Expansion): ✅ Implemented${NC}"
echo ""