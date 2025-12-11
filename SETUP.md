# Quick Setup Guide

## Prerequisites
- Python 3.8 or higher
- Google Gemini API key

## Installation Steps

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Create .env File**
   Create a `.env` file in the root directory with:
   ```env
   GEMINI_API_KEY=your_gemini_api_key_here
   DATABASE_TYPE=sqlite
   GEMINI_MODEL=gemini-1.5-flash
   ```
   
   **Model Options (Free Tier - Default):**
   - `gemini-1.5-flash` (default, free, fast, latest free model)
   - `gemini-1.5-pro` (free, better quality, slower)
   
   **Model Options (Paid Tier):**
   - `gemini-2.0-flash` (paid, latest stable)
   - `gemini-2.0-flash-exp` (paid, experimental)
   - `gemini-2.5-flash-lite` (paid, optimized)
   
   For MongoDB (optional):
   ```env
   GEMINI_API_KEY=your_gemini_api_key_here
   DATABASE_TYPE=mongodb
   MONGODB_URI=mongodb://localhost:27017/
   DATABASE_NAME=ai_learning_platform
   GEMINI_MODEL=gemini-1.5-flash
   ```

3. **Get Gemini API Key**
   - Visit: https://makersuite.google.com/app/apikey
   - Create a new API key
   - Add it to your `.env` file

4. **Run the Application**
   ```bash
   streamlit run app.py
   ```
   
   Or use the provided scripts:
   - Windows: `run.bat`
   - Linux/Mac: `chmod +x run.sh && ./run.sh`

## First Time Usage

1. Register a new account with email and password
2. Select a skill from the dropdown or add a new one
3. Click "Generate Diagnostic Quiz"
4. Answer all 5 questions
5. Submit and view your results
6. Download PDF report if desired

## Troubleshooting

- **"GEMINI_API_KEY not found"**: Make sure `.env` file exists and contains the API key
- **"404 models/gemini-pro is not found"**: The app now defaults to `gemini-1.5-flash` (free tier). If you're using a free API key, this should work. For paid models, set `GEMINI_MODEL` in your `.env` file.
- **Import errors**: Run `pip install -r requirements.txt` again
- **Database errors**: For SQLite, ensure write permissions. For MongoDB, ensure the service is running.
- **JSON parsing errors**: If you see JSON decode errors, try using `gemini-1.5-pro` model for better structured output

