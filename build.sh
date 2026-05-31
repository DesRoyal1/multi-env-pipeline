#!/bin/bash
# Build script - installs dependencies into a build folder
# then packages everything for Lambda deployment

echo "Installing dependencies..."
pip install flask boto3 flask-cors -t ./build/

echo "Copying application files..."
cp app.py ./build/
cp lambda_handler.py ./build/
cp -r templates ./build/
cp -r lambda ./build/

echo "Creating deployment zip..."
cd build
zip -r ../app.zip . -x "*.pyc" -x "__pycache__/*"
cd ..

echo "Build complete: app.zip ready for Lambda"
