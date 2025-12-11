#!/bin/bash
echo "Starting AI Learning Platform..."
echo ""
echo "Make sure you have:"
echo "1. Created a .env file with your GEMINI_API_KEY"
echo "2. Installed all dependencies: pip install -r requirements.txt"
echo ""
read -p "Press enter to continue..."
streamlit run app.py

