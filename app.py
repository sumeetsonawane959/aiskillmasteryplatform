"""
Main Streamlit application for AI Learning & Skill Mastery Platform.
"""
import streamlit as st
import os
import json
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from datetime import datetime
from dotenv import load_dotenv

# Backend imports
from backend.database import Database
from backend.auth import AuthManager
from backend.quiz_generator import QuizGenerator
from backend.evaluator import Evaluator
from backend.report_generator import ReportGenerator
from backend.utils import load_skills, save_skill

load_dotenv()

# Page configuration
st.set_page_config(
    page_title="AI Learning Platform",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Initialize session state
if 'user_id' not in st.session_state:
    st.session_state.user_id = None
if 'user_email' not in st.session_state:
    st.session_state.user_email = None
if 'current_quiz' not in st.session_state:
    st.session_state.current_quiz = None
if 'current_skill' not in st.session_state:
    st.session_state.current_skill = None
if 'user_answers' not in st.session_state:
    st.session_state.user_answers = []
if 'evaluation' not in st.session_state:
    st.session_state.evaluation = None

# Initialize database and services
@st.cache_resource
def init_database():
    db_type = os.getenv("DATABASE_TYPE", "sqlite")
    mongodb_uri = os.getenv("MONGODB_URI")
    db_name = os.getenv("DATABASE_NAME", "ai_learning_platform")
    return Database(db_type, mongodb_uri, db_name)

@st.cache_resource
def init_services():
    db = init_database()
    auth = AuthManager(db)
    quiz_gen = QuizGenerator()
    evaluator = Evaluator()
    report_gen = ReportGenerator()
    return db, auth, quiz_gen, evaluator, report_gen

try:
    db, auth, quiz_gen, evaluator, report_gen = init_services()
except Exception as e:
    st.error(f"Initialization error: {str(e)}")
    st.stop()


def login_page():
    """Login and registration page with modern UI."""
    # Hero section
    st.markdown("""
    <div style='text-align: center; padding: 2rem 0;'>
        <h1 style='font-size: 3.5rem; margin-bottom: 1rem; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                   -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-weight: 800;'>
            🚀 AI Learning Platform
        </h1>
        <p style='font-size: 1.2rem; color: #b8bcc8; margin-bottom: 2rem;'>
            Master Skills with AI-Powered Learning & Assessment
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Centered login card
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.container():
            st.markdown("""
            <div style='background: rgba(255, 255, 255, 0.08); backdrop-filter: blur(10px); 
                        border-radius: 20px; padding: 2.5rem; border: 1px solid rgba(255, 255, 255, 0.1);
                        box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);'>
            </div>
            """, unsafe_allow_html=True)
            
            tab1, tab2 = st.tabs(["🔐 Login", "✨ Register"])
            
            with tab1:
                st.markdown("<h3 style='text-align: center; margin-bottom: 2rem;'>Welcome Back!</h3>", unsafe_allow_html=True)
                email = st.text_input("📧 Email", key="login_email", placeholder="Enter your email")
                password = st.text_input("🔒 Password", type="password", key="login_password", placeholder="Enter your password")
                
                if st.button("🚀 Login", type="primary", use_container_width=True):
                    if email and password:
                        user_id, message = auth.login(email, password)
                        if user_id:
                            st.session_state.user_id = user_id
                            st.session_state.user_email = email
                            st.success(f"✨ {message}")
                            st.balloons()
                            st.rerun()
                        else:
                            st.error(f"❌ {message}")
                    else:
                        st.warning("⚠️ Please enter both email and password")
            
            with tab2:
                st.markdown("<h3 style='text-align: center; margin-bottom: 2rem;'>Join the Learning Journey!</h3>", unsafe_allow_html=True)
                reg_email = st.text_input("📧 Email", key="reg_email", placeholder="Create your email")
                reg_password = st.text_input("🔒 Password", type="password", key="reg_password", placeholder="Create a secure password")
                
                if st.button("✨ Register", type="primary", use_container_width=True):
                    if reg_email and reg_password:
                        success, message = auth.register(reg_email, reg_password)
                        if success:
                            st.success(f"🎉 {message}")
                            st.balloons()
                        else:
                            st.error(f"❌ {message}")
                    else:
                        st.warning("⚠️ Please enter both email and password")


def dashboard_page():
    """Main dashboard with latest score, history, and graphs."""
    st.markdown("""
    <div style='text-align: center; padding: 1rem 0 2rem 0;'>
        <h1 style='font-size: 2.5rem; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                   -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-weight: 700;'>
            📊 Your Learning Dashboard
        </h1>
    </div>
    """, unsafe_allow_html=True)
    
    # Get user sessions
    sessions = db.get_user_sessions(st.session_state.user_id)
    latest_session = db.get_latest_session(st.session_state.user_id)
    
    if not sessions:
        st.markdown("""
        <div style='text-align: center; padding: 3rem; background: rgba(255, 255, 255, 0.05); 
                    border-radius: 20px; border: 2px dashed rgba(102, 126, 234, 0.3);'>
            <h2 style='color: #667eea; margin-bottom: 1rem;'>👋 Welcome to Your Learning Journey!</h2>
            <p style='color: #b8bcc8; font-size: 1.1rem; margin-bottom: 2rem;'>
                No mastery data yet — take a diagnostic test to get started and track your progress!
            </p>
        </div>
        """, unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("🚀 Take Your First Diagnostic Test", type="primary", use_container_width=True):
                st.session_state.page = "skill_selection"
                st.rerun()
        return
    
    # Latest Score Cards with modern styling
    col1, col2, col3 = st.columns(3)
    with col1:
        if latest_session:
            score = latest_session['score']
            score_emoji = "🎯" if score >= 70 else "📈" if score >= 50 else "💪"
            st.markdown(f"""
            <div style='background: linear-gradient(135deg, rgba(102, 126, 234, 0.2) 0%, rgba(118, 75, 162, 0.2) 100%);
                        border-radius: 15px; padding: 1.5rem; border: 1px solid rgba(102, 126, 234, 0.3);'>
                <h3 style='color: #b8bcc8; margin: 0; font-size: 0.9rem;'>Latest Score</h3>
                <h1 style='color: #667eea; margin: 0.5rem 0; font-size: 2.5rem; font-weight: 700;'>{score:.1f}%</h1>
                <p style='color: #b8bcc8; margin: 0;'>{score_emoji} {latest_session['skill_name']}</p>
            </div>
            """, unsafe_allow_html=True)
    
    with col2:
        total_tests = len(sessions)
        st.markdown(f"""
        <div style='background: linear-gradient(135deg, rgba(79, 172, 254, 0.2) 0%, rgba(0, 242, 254, 0.2) 100%);
                    border-radius: 15px; padding: 1.5rem; border: 1px solid rgba(79, 172, 254, 0.3);'>
            <h3 style='color: #b8bcc8; margin: 0; font-size: 0.9rem;'>Total Tests</h3>
            <h1 style='color: #4facfe; margin: 0.5rem 0; font-size: 2.5rem; font-weight: 700;'>{total_tests}</h1>
            <p style='color: #b8bcc8; margin: 0;'>📚 Tests Completed</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        avg_score = sum(s['score'] for s in sessions) / len(sessions)
        st.markdown(f"""
        <div style='background: linear-gradient(135deg, rgba(245, 87, 108, 0.2) 0%, rgba(240, 147, 251, 0.2) 100%);
                    border-radius: 15px; padding: 1.5rem; border: 1px solid rgba(245, 87, 108, 0.3);'>
            <h3 style='color: #b8bcc8; margin: 0; font-size: 0.9rem;'>Average Score</h3>
            <h1 style='color: #f5576c; margin: 0.5rem 0; font-size: 2.5rem; font-weight: 700;'>{avg_score:.1f}%</h1>
            <p style='color: #b8bcc8; margin: 0;'>⭐ Your Average</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Score Progression Graph with modern styling
    if len(sessions) > 0:
        st.markdown("""
        <div style='margin: 2rem 0;'>
            <h2 style='color: #667eea; margin-bottom: 1rem;'>📈 Score Progression Over Time</h2>
        </div>
        """, unsafe_allow_html=True)
        sorted_sessions = sorted(sessions, key=lambda x: x['created_at'])
        dates = [datetime.fromisoformat(s['created_at']).strftime('%Y-%m-%d') for s in sorted_sessions]
        scores = [s['score'] for s in sorted_sessions]
        
        # Modern graph styling
        fig, ax = plt.subplots(figsize=(12, 6), facecolor='#0a0e27')
        ax.set_facecolor('#0a0e27')
        ax.plot(dates, scores, marker='o', linewidth=3, markersize=10, 
                color='#667eea', markerfacecolor='#764ba2', markeredgecolor='#667eea', markeredgewidth=2)
        ax.fill_between(range(len(dates)), scores, alpha=0.2, color='#667eea')
        ax.set_title('Your Learning Journey 📊', fontsize=16, fontweight='bold', color='#ffffff', pad=20)
        ax.set_xlabel('Date', fontsize=12, color='#b8bcc8')
        ax.set_ylabel('Score (%)', fontsize=12, color='#b8bcc8')
        ax.set_ylim(0, 100)
        ax.grid(True, alpha=0.2, color='#667eea', linestyle='--')
        ax.tick_params(colors='#b8bcc8')
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        st.pyplot(fig, use_container_width=True)
        plt.close()
    
    st.markdown("---")
    
    # History Table with modern styling
    st.markdown("""
    <div style='margin: 2rem 0 1rem 0;'>
        <h2 style='color: #667eea;'>📜 Recent Test History</h2>
    </div>
    """, unsafe_allow_html=True)
    if sessions:
        history_data = []
        for session in sessions[:10]:  # Show last 10
            history_data.append({
                "Date": datetime.fromisoformat(session['created_at']).strftime('%Y-%m-%d %H:%M'),
                "Skill": session['skill_name'],
                "Score": f"{session['score']:.1f}%",
            })
        
        df = pd.DataFrame(history_data)
        st.dataframe(df, use_container_width=True, hide_index=True, 
                    height=300)
    
    # Navigation buttons with modern styling
    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🚀 Take New Test", type="primary", use_container_width=True):
            st.session_state.page = "skill_selection"
            st.rerun()
    with col2:
        if st.button("📚 View Full History", use_container_width=True):
            st.session_state.page = "history"
            st.rerun()


def skill_selection_page():
    """Skill selection page with modern UI."""
    st.markdown("""
    <div style='text-align: center; padding: 1rem 0 2rem 0;'>
        <h1 style='font-size: 2.5rem; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                   -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-weight: 700;'>
            🎯 Choose Your Skill Challenge
        </h1>
        <p style='color: #b8bcc8; font-size: 1.1rem;'>Select a skill to test your knowledge!</p>
    </div>
    """, unsafe_allow_html=True)
    
    skills = load_skills()
    
    # Skill selection card
    with st.container():
        st.markdown("""
        <div style='background: rgba(255, 255, 255, 0.08); backdrop-filter: blur(10px); 
                    border-radius: 20px; padding: 2rem; border: 1px solid rgba(255, 255, 255, 0.1);
                    margin-bottom: 2rem;'>
        </div>
        """, unsafe_allow_html=True)
        
        selected_skill = st.selectbox("📚 Choose a skill to test:", [""] + skills, key="skill_select",
                                     help="Select from existing skills or add a new one below")
        
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("""
        <div style='text-align: center; color: #b8bcc8; margin: 1rem 0;'>
            <h3>✨ Or Create Your Own Skill</h3>
        </div>
        """, unsafe_allow_html=True)
        
        new_skill = st.text_input("➕ Enter new skill name:", key="new_skill", 
                                 placeholder="e.g., Machine Learning, Web Development...")
        
        if st.button("✨ Add New Skill", use_container_width=True):
            if new_skill:
                if save_skill(new_skill):
                    st.success(f"🎉 Skill '{new_skill}' added successfully!")
                    st.balloons()
                    st.rerun()
                else:
                    st.warning("⚠️ Skill already exists or invalid name")
            else:
                st.warning("⚠️ Please enter a skill name")
    
    # Generate quiz button
    if selected_skill:
        st.session_state.current_skill = selected_skill
        st.markdown("<br>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("🚀 Generate Diagnostic Quiz", type="primary", use_container_width=True):
                with st.spinner("✨ Generating personalized quiz questions with AI..."):
                    try:
                        questions = quiz_gen.generate_quiz(selected_skill, 5)
                        st.session_state.current_quiz = questions
                        st.session_state.user_answers = [""] * len(questions)
                        st.session_state.page = "quiz"
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Error generating quiz: {str(e)}")
    
    # Back button
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("← Back to Dashboard", use_container_width=True):
        st.session_state.page = "dashboard"
        st.rerun()


def quiz_page():
    """Quiz taking page with modern UI."""
    if not st.session_state.current_quiz:
        st.error("❌ No quiz available. Please select a skill first.")
        if st.button("Go to Skill Selection"):
            st.session_state.page = "skill_selection"
            st.rerun()
        return
    
    st.markdown(f"""
    <div style='text-align: center; padding: 1rem 0 2rem 0;'>
        <h1 style='font-size: 2.5rem; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                   -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-weight: 700;'>
            📝 {st.session_state.current_skill} Quiz
        </h1>
        <p style='color: #b8bcc8; font-size: 1.1rem;'>Answer all questions to complete the diagnostic test</p>
    </div>
    """, unsafe_allow_html=True)
    
    questions = st.session_state.current_quiz
    
    # Initialize answers if not set
    if len(st.session_state.user_answers) != len(questions):
        st.session_state.user_answers = [""] * len(questions)
    
    # Display questions with modern styling
    for i, question in enumerate(questions):
        with st.container():
            st.markdown(f"""
            <div style='background: rgba(255, 255, 255, 0.08); backdrop-filter: blur(10px); 
                        border-radius: 15px; padding: 2rem; border: 1px solid rgba(102, 126, 234, 0.3);
                        margin-bottom: 2rem;'>
                <h2 style='color: #667eea; margin-bottom: 1rem;'>Question {i+1} of {len(questions)}</h2>
                <p style='color: #ffffff; font-size: 1.1rem; line-height: 1.6;'>{question.get('question', '')}</p>
            </div>
            """, unsafe_allow_html=True)
            
            q_type = question.get('type', 'short_answer')
            
            if q_type == 'mcq':
                options = question.get('options', [])
                selected = st.radio(
                    "💭 Select your answer:",
                    options,
                    key=f"q_{i}",
                    index=options.index(st.session_state.user_answers[i]) if st.session_state.user_answers[i] in options else 0
                )
                st.session_state.user_answers[i] = selected
            else:
                answer = st.text_area(
                    "✍️ Your answer:",
                    value=st.session_state.user_answers[i],
                    key=f"q_{i}",
                    height=120,
                    placeholder="Type your answer here..."
                )
                st.session_state.user_answers[i] = answer
            
            if i < len(questions) - 1:
                st.markdown("<br>", unsafe_allow_html=True)
    
    # Submit button with progress indicator
    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("✅ Submit Quiz", type="primary", use_container_width=True):
            # Check if all questions answered
            if all(ans.strip() for ans in st.session_state.user_answers):
                with st.spinner("🤖 AI is evaluating your answers... This may take a moment."):
                    try:
                        evaluation = evaluator.evaluate(
                            st.session_state.current_skill,
                            st.session_state.current_quiz,
                            st.session_state.user_answers
                        )
                        st.session_state.evaluation = evaluation
                        
                        # Save to database
                        score = evaluation.get('overall_score', 0)
                        db.save_session(
                            st.session_state.user_id,
                            st.session_state.current_skill,
                            st.session_state.current_quiz,
                            st.session_state.user_answers,
                            evaluation,
                            score
                        )
                        
                        st.balloons()
                        st.session_state.page = "results"
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Error evaluating answers: {str(e)}")
            else:
                st.warning("⚠️ Please answer all questions before submitting.")
    
    with col2:
        if st.button("❌ Cancel", use_container_width=True):
            st.session_state.page = "skill_selection"
            st.rerun()


def results_page():
    """Results and evaluation page with modern UI."""
    if not st.session_state.evaluation:
        st.error("❌ No evaluation available.")
        if st.button("Go to Dashboard"):
            st.session_state.page = "dashboard"
            st.rerun()
        return
    
    evaluation = st.session_state.evaluation
    overall_score = evaluation.get('overall_score', 0)
    
    # Hero score display
    score_emoji = "🎯" if overall_score >= 70 else "📈" if overall_score >= 50 else "💪"
    score_color = "#4facfe" if overall_score >= 70 else "#f5576c" if overall_score >= 50 else "#ffa500"
    
    st.markdown(f"""
    <div style='text-align: center; padding: 2rem 0; background: rgba(255, 255, 255, 0.08); 
                border-radius: 20px; border: 2px solid {score_color}; margin-bottom: 2rem;'>
        <h1 style='font-size: 4rem; margin: 0; color: {score_color}; font-weight: 800;'>{overall_score:.1f}%</h1>
        <p style='font-size: 1.5rem; color: #b8bcc8; margin: 1rem 0;'>{score_emoji} {st.session_state.current_skill}</p>
        <p style='color: #b8bcc8;'>Overall Performance Score</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Question-wise breakdown
    st.markdown("""
    <div style='margin: 2rem 0 1rem 0;'>
        <h2 style='color: #667eea;'>📋 Question-wise Breakdown</h2>
    </div>
    """, unsafe_allow_html=True)
    
    breakdown = evaluation.get('question_wise_breakdown', [])
    for item in breakdown:
        q_idx = item.get('question_index', 0)
        q_score = item.get('score', 0)
        feedback = item.get('feedback', '')
        q_color = "#4facfe" if q_score >= 70 else "#f5576c" if q_score >= 50 else "#ffa500"
        
        with st.expander(f"📝 Question {q_idx + 1} - Score: {q_score:.1f}%", expanded=False):
            st.markdown(f"""
            <div style='background: rgba(255, 255, 255, 0.05); padding: 1rem; border-radius: 10px; margin-bottom: 1rem;'>
                <p style='color: #b8bcc8;'><strong>Your Answer:</strong></p>
                <p style='color: #ffffff;'>{st.session_state.user_answers[q_idx]}</p>
            </div>
            <div style='background: rgba(79, 172, 254, 0.1); padding: 1rem; border-radius: 10px; border-left: 4px solid {q_color};'>
                <p style='color: #b8bcc8;'><strong>AI Feedback:</strong></p>
                <p style='color: #ffffff;'>{feedback}</p>
            </div>
            """, unsafe_allow_html=True)
    
    # Strengths, Weaknesses, Recommendations in cards
    col1, col2 = st.columns(2)
    
    with col1:
        strengths = evaluation.get('strengths', [])
        if strengths:
            st.markdown("""
            <div style='background: rgba(79, 172, 254, 0.15); border-radius: 15px; padding: 1.5rem; 
                        border: 1px solid rgba(79, 172, 254, 0.3); margin-bottom: 1rem;'>
                <h3 style='color: #4facfe; margin-bottom: 1rem;'>✅ Your Strengths</h3>
            </div>
            """, unsafe_allow_html=True)
            for strength in strengths:
                st.markdown(f"<div style='padding: 0.5rem; color: #ffffff;'>✨ {strength}</div>", unsafe_allow_html=True)
    
    with col2:
        weaknesses = evaluation.get('weaknesses', [])
        if weaknesses:
            st.markdown("""
            <div style='background: rgba(245, 87, 108, 0.15); border-radius: 15px; padding: 1.5rem; 
                        border: 1px solid rgba(245, 87, 108, 0.3); margin-bottom: 1rem;'>
                <h3 style='color: #f5576c; margin-bottom: 1rem;'>⚠️ Areas for Improvement</h3>
            </div>
            """, unsafe_allow_html=True)
            for weakness in weaknesses:
                st.markdown(f"<div style='padding: 0.5rem; color: #ffffff;'>📌 {weakness}</div>", unsafe_allow_html=True)
    
    # Recommendations
    recommendations = evaluation.get('study_recommendations', [])
    if recommendations:
        st.markdown("""
        <div style='margin: 2rem 0 1rem 0;'>
            <h2 style='color: #667eea;'>📚 Study Recommendations</h2>
        </div>
        <div style='background: rgba(102, 126, 234, 0.15); border-radius: 15px; padding: 1.5rem; 
                    border: 1px solid rgba(102, 126, 234, 0.3);'>
        </div>
        """, unsafe_allow_html=True)
        for rec in recommendations:
            st.markdown(f"<div style='padding: 0.5rem; color: #ffffff;'>💡 {rec}</div>", unsafe_allow_html=True)
    
    # Action buttons
    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("📄 Download Report", type="primary", use_container_width=True):
            st.session_state.page = "report_download"
            st.rerun()
    with col2:
        if st.button("🚀 Take Another Test", use_container_width=True):
            st.session_state.page = "skill_selection"
            st.rerun()
    with col3:
        if st.button("🏠 View Dashboard", use_container_width=True):
            st.session_state.page = "dashboard"
            st.rerun()


def history_page():
    """Full history page."""
    st.title("📜 Test History")
    st.markdown("---")
    
    sessions = db.get_user_sessions(st.session_state.user_id)
    
    if not sessions:
        st.info("No test history available.")
        if st.button("Take Your First Test", type="primary"):
            st.session_state.page = "skill_selection"
            st.rerun()
        return
    
    # Filter by skill
    skills = list(set(s['skill_name'] for s in sessions))
    selected_skill_filter = st.selectbox("Filter by skill:", ["All"] + skills)
    
    filtered_sessions = sessions
    if selected_skill_filter != "All":
        filtered_sessions = [s for s in sessions if s['skill_name'] == selected_skill_filter]
    
    # Display sessions
    for session in filtered_sessions:
        with st.expander(f"{session['skill_name']} - {session['score']:.1f}% - {datetime.fromisoformat(session['created_at']).strftime('%Y-%m-%d %H:%M')}"):
            st.markdown(f"**Date:** {datetime.fromisoformat(session['created_at']).strftime('%Y-%m-%d %H:%M:%S')}")
            st.markdown(f"**Skill:** {session['skill_name']}")
            st.markdown(f"**Score:** {session['score']:.1f}%")
            
            eval_data = session.get('evaluation', {})
            if eval_data:
                st.markdown("**Strengths:**")
                for strength in eval_data.get('strengths', []):
                    st.markdown(f"- {strength}")
                
                st.markdown("**Weaknesses:**")
                for weakness in eval_data.get('weaknesses', []):
                    st.markdown(f"- {weakness}")
    
    st.markdown("---")
    if st.button("Back to Dashboard", use_container_width=True):
        st.session_state.page = "dashboard"
        st.rerun()


def report_download_page():
    """PDF report download page."""
    st.title("📄 Download Report")
    st.markdown("---")
    
    if not st.session_state.evaluation:
        st.error("No evaluation available to generate report.")
        if st.button("Go to Dashboard"):
            st.session_state.page = "dashboard"
            st.rerun()
        return
    
    # Get all sessions for this skill
    all_sessions = db.get_user_sessions(st.session_state.user_id)
    skill_sessions = [s for s in all_sessions if s['skill_name'] == st.session_state.current_skill]
    
    # Generate report
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("✨ Generate & Download PDF Report", type="primary", use_container_width=True):
            with st.spinner("🔄 Generating your personalized PDF report... This may take a moment."):
                try:
                    report_path = f"report_{st.session_state.user_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
                    report_gen.generate_pdf_report(
                        st.session_state.user_email,
                        st.session_state.current_skill,
                        st.session_state.evaluation,
                        skill_sessions,
                        report_path
                    )
                    
                    if os.path.exists(report_path):
                        with open(report_path, "rb") as pdf_file:
                            st.download_button(
                                label="📥 Download PDF Report",
                                data=pdf_file.read(),
                                file_name=f"Learning_Report_{st.session_state.current_skill}_{datetime.now().strftime('%Y%m%d')}.pdf",
                                mime="application/pdf",
                                type="primary",
                                use_container_width=True
                            )
                        st.success("✅ Report generated successfully! Click the button above to download.")
                        st.balloons()
                        # Cleanup
                        try:
                            os.remove(report_path)
                        except:
                            pass
                    else:
                        st.error("❌ Report generation failed. Please try again.")
                except Exception as e:
                    error_msg = str(e)
                    st.error(f"❌ Error generating report: {error_msg}")
                    # Show detailed error for debugging
                    with st.expander("🔍 Error Details (Click to expand)"):
                        import traceback
                        st.code(traceback.format_exc())
    
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("← Back to Results", use_container_width=True):
        st.session_state.page = "results"
        st.rerun()


# Main app routing
def main():
    """Main application router."""
    # Check authentication
    if st.session_state.user_id is None:
        login_page()
    else:
        # Sidebar navigation with modern styling
        with st.sidebar:
            st.markdown(f"""
            <div style='background: rgba(102, 126, 234, 0.2); border-radius: 10px; padding: 1rem; 
                        margin-bottom: 1rem; border: 1px solid rgba(102, 126, 234, 0.3);'>
                <p style='color: #667eea; margin: 0; font-weight: 600;'>👤 {st.session_state.user_email}</p>
            </div>
            """, unsafe_allow_html=True)
            st.markdown("---")
            
            if st.button("🏠 Dashboard", use_container_width=True):
                st.session_state.page = "dashboard"
                st.rerun()
            if st.button("🎯 Take Test", use_container_width=True):
                st.session_state.page = "skill_selection"
                st.rerun()
            if st.button("📜 History", use_container_width=True):
                st.session_state.page = "history"
                st.rerun()
            st.markdown("---")
            if st.button("🚪 Logout", use_container_width=True):
                st.session_state.user_id = None
                st.session_state.user_email = None
                st.session_state.current_quiz = None
                st.session_state.current_skill = None
                st.session_state.user_answers = []
                st.session_state.evaluation = None
                st.rerun()
        
        # Page routing
        if 'page' not in st.session_state:
            st.session_state.page = "dashboard"
        
        if st.session_state.page == "dashboard":
            dashboard_page()
        elif st.session_state.page == "skill_selection":
            skill_selection_page()
        elif st.session_state.page == "quiz":
            quiz_page()
        elif st.session_state.page == "results":
            results_page()
        elif st.session_state.page == "history":
            history_page()
        elif st.session_state.page == "report_download":
            report_download_page()


if __name__ == "__main__":
    main()

