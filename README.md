# AI Learning & Skill Mastery Platform

A complete Python + Streamlit based platform for AI-powered learning assessment with user authentication, automatic question generation, AI evaluation, and downloadable PDF reports.

## Features

- **User Authentication**: Email/password login and registration with SQLite or MongoDB
- **Skill Management**: Select from existing skills or add new ones dynamically
- **AI Question Generation**: Automatic generation of 5 diagnostic questions (MCQ + short-answer) using Google Gemini API
- **AI Evaluation**: Comprehensive evaluation with scores, feedback, strengths, weaknesses, and recommendations
- **Session History**: Track all past attempts with detailed evaluation data
- **Dashboard**: View latest scores, history table, and score progression graphs
- **PDF Reports**: Downloadable reports with graphs (score progression, question-wise performance) and recommendations
- **Clean UI**: Modern Streamlit interface with separate pages for all features

## Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment

Create a `.env` file in the root directory:

```env
GEMINI_API_KEY=your_gemini_api_key_here
DATABASE_TYPE=sqlite
GEMINI_MODEL=gemini-1.5-flash
MONGODB_URI=mongodb://localhost:27017/
DATABASE_NAME=ai_learning_platform
```

**Note**: 
- Get your Gemini API key from [Google AI Studio](https://makersuite.google.com/app/apikey)
- For SQLite (default), you only need `GEMINI_API_KEY` and `DATABASE_TYPE=sqlite`
- For MongoDB, also set `MONGODB_URI` and `DATABASE_NAME`
- **Model Options**: The app automatically detects and uses available models. Default: `models/gemini-2.5-flash` (latest). Also supports `models/gemini-2.0-flash`, `models/gemini-2.5-pro`, etc.

### 3. Run the Application

```bash
streamlit run app.py
```

The application will open in your browser at `http://localhost:8501`

## Project Structure

```
.
├── app.py                      # Main Streamlit application
├── requirements.txt            # Python dependencies
├── .env                        # Environment variables (create this)
├── .env.example               # Example environment file
├── skills.json                # Available skills list
├── backend/
│   ├── database.py            # Database management (SQLite/MongoDB)
│   ├── auth.py                # Authentication logic
│   ├── ai_service.py          # Google Gemini API integration
│   ├── quiz_generator.py      # Question generation
│   ├── evaluator.py           # Answer evaluation
│   ├── report_generator.py    # PDF report generation
│   └── utils.py               # Utility functions
└── README.md                  # This file
```

## Usage Guide

1. **Register/Login**: Create an account or login with existing credentials
2. **Select Skill**: Choose a skill from the dropdown or add a new one
3. **Take Quiz**: Answer 5 automatically generated questions
4. **View Results**: See detailed evaluation with scores, feedback, and recommendations
5. **Download Report**: Generate and download a PDF report with graphs
6. **View History**: Check your past attempts and progress over time

## Database

- **SQLite** (default): Automatically creates `ai_learning.db` file
- **MongoDB**: Configure connection string in `.env` file

## API Requirements

- **Google Gemini API**: Required for question generation and evaluation
- Get your API key from: https://makersuite.google.com/app/apikey

## Notes

- All user data is stored locally in the database
- PDF reports are generated on-demand and can be downloaded
- The application runs entirely locally (no external services except Gemini API)
- Skills can be added dynamically and are saved to `skills.json`

## Troubleshooting

1. **API Key Error**: Make sure `GEMINI_API_KEY` is set in `.env` file
2. **Model 404 Error**: If you see "404 models/... is not found":
   - **Update the SDK**: Run `pip install --upgrade google-generativeai`
   - **Test your API key**: Run `python test_model.py` to see which models work with your API key
   - The app automatically detects available models and uses the latest (Gemini 2.5/2.0)
   - Old models (gemini-1.5, gemini-pro) are deprecated and no longer available
   - The app will automatically try: `models/gemini-2.5-flash`, `models/gemini-2.0-flash`, etc.
   - Ensure your API key is valid and from Google AI Studio
3. **Database Error**: For SQLite, ensure write permissions in the directory
4. **Import Errors**: Make sure all dependencies are installed: `pip install -r requirements.txt`
5. **MongoDB Connection**: If using MongoDB, ensure the service is running
6. **JSON Parsing Errors**: Try using `gemini-1.5-pro` model for better structured JSON output

## License

This project is provided as-is for educational and development purposes.

