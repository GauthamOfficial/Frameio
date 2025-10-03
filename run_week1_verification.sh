#!/bin/bash

echo "🎯 Week 1 Complete Verification - Team Member 3"
echo "============================================="

echo ""
echo "1. Activating virtual environment..."
source startup_env/bin/activate

echo ""
echo "2. Installing dependencies..."
pip install banana-dev==6.3.0

echo ""
echo "3. Running database migrations..."
cd backend
python manage.py makemigrations
python manage.py migrate

echo ""
echo "4. Setting up AI services..."
python manage.py setup_ai

echo ""
echo "5. Running final verification..."
python final_week1_verification.py

echo ""
echo "6. Testing API endpoints..."
python test_ai_endpoints.py

echo ""
echo "============================================="
echo "🎉 Week 1 Verification Complete!"
echo "============================================="

