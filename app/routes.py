import os
import logging
from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from app.nlp_processor import NLPProcessor
from app.scoring_engine import ScoringEngine
from app.utils import allowed_file, extract_text_from_pdf
from app import extensions
from app.db import save_resume_version

logger = logging.getLogger(__name__)

bp = Blueprint('main', __name__)

# Initialize NLP processor and scoring engine
nlp_processor = NLPProcessor()
scoring_engine = ScoringEngine()

def perform_analysis(resume_text, job_description):
    """Run NLP analysis, scoring, and suggestions generation."""
    logger.info("Resume analysis started (resume_chars=%s, jd_chars=%s)", len(resume_text or ""), len(job_description or ""))
    logging.debug("Processing resume and job description with NLP...")
    resume_analysis = nlp_processor.analyze_text(resume_text, text_type='resume')
    jd_analysis = nlp_processor.analyze_text(job_description, text_type='job_description')
    
    # Calculate scores and comparisons
    logging.debug("Calculating job fit score...")
    score_data = scoring_engine.calculate_job_fit_score(resume_analysis, jd_analysis)
    
    # Generate improvement suggestions
    suggestions = scoring_engine.generate_suggestions(resume_analysis, jd_analysis, score_data)

    logger.info(
        "Resume analysis complete: overall_score=%s skill_score=%s",
        score_data.get("overall_score"),
        score_data.get("skill_score"),
    )

    payload = {
        'overall_score': score_data['overall_score'],
        'skill_score': score_data['skill_score'],
        'role_score': score_data['role_score'],
        'experience_score': score_data['experience_score'],
        'matched_keywords': score_data['matched_keywords'],
        'missing_keywords': score_data['missing_keywords'],
        'suggestions': suggestions,
        'resume_keywords': resume_analysis['keywords'],
        'jd_keywords': jd_analysis['keywords']
    }
    from app.services.resume_presentation import enrich_analysis
    user_id = ""
    try:
        from flask_login import current_user
        if getattr(current_user, "is_authenticated", False):
            user_id = current_user.id
    except Exception:
        pass
    return enrich_analysis(payload, resume_text, user_id=user_id)

@bp.route('/resume-analyzer')
@bp.route('/resume-analyzer/')
@login_required
def resume_analyzer():
    """Render the resume analyzer module page."""
    return render_template('resume_analyzer.html')

@bp.route('/analyze', methods=['POST'])
@login_required
def analyze():
    """Process the resume and job description, then show results."""
    try:
        # Check if file is uploaded
        if 'resume' not in request.files:
            flash('No resume file uploaded', 'error')
            return redirect(url_for('main.resume_analyzer'))
        
        file = request.files['resume']
        job_description = request.form.get('job_description', '').strip()
        
        # Validate inputs
        if file.filename == '':
            flash('No resume file selected', 'error')
            return redirect(url_for('main.resume_analyzer'))
        
        if not job_description:
            flash('Job description is required', 'error')
            return redirect(url_for('main.resume_analyzer'))
        
        if not allowed_file(file.filename):
            flash('Only PDF files are allowed', 'error')
            return redirect(url_for('main.resume_analyzer'))
        
        # Save uploaded file
        filename = secure_filename(file.filename)
        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        
        # Extract text from resume
        resume_text = extract_text_from_pdf(file_path)
        if not resume_text:
            flash('Could not extract text from the PDF. Please ensure it\'s not a scanned document.', 'error')
            os.remove(file_path)  # Clean up
            return redirect(url_for('main.resume_analyzer'))
        
        # Clean up uploaded file
        os.remove(file_path)
        
        # Process with NLP and calculate scores
        results_data = perform_analysis(resume_text, job_description)
        results_data['resume_text'] = resume_text
        results_data['job_description'] = job_description

        # Persist a versioned resume snapshot for "resume learning" (best effort).
        try:
            payload = {
                "source": "resume_analyzer_form",
                "resume_text": resume_text,
                "job_description": job_description,
                "analysis": results_data,
            }
            save_resume_version(current_user.id, payload)  # type: ignore[name-defined]
        except Exception:
            # Never block the main flow.
            pass
        
        return render_template('results.html', results=results_data)
        
    except Exception as e:
        logging.error(f"Error during analysis: {str(e)}")
        flash('An error occurred during analysis. Please try again.', 'error')
        return redirect(url_for('main.resume_analyzer'))

@bp.route('/api/analyze-text', methods=['POST'])
@login_required
def analyze_text_api():
    """API endpoint to re-analyze resume text and job description."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Invalid request data'}), 400
            
        resume_text = data.get('resume_text', '').strip()
        job_description = data.get('job_description', '').strip()
        
        if not resume_text:
            return jsonify({'error': 'Resume text is required'}), 400
        if not job_description:
            return jsonify({'error': 'Job description is required'}), 400
            
        results_data = perform_analysis(resume_text, job_description)
        results_data['resume_text'] = resume_text
        results_data['job_description'] = job_description

        try:
            save_resume_version(
                current_user.id,
                {
                    "source": "reanalyze_api",
                    "resume_text": resume_text,
                    "job_description": job_description,
                    "analysis": results_data,
                },
            )
        except Exception:
            pass
        
        return jsonify(results_data)
    except Exception as e:
        logging.error(f"Error during API analysis: {str(e)}")
        return jsonify({'error': 'An error occurred during analysis.'}), 500

@bp.route('/sample-jd')
def sample_jd():
    """Return a sample job description."""
    sample = {
        'job_description': """We are looking for a skilled Python Developer to join our team. The ideal candidate will have experience with web development using Flask or Django, and proficiency in Python programming.

Requirements:
- 3+ years of experience in Python development
- Strong knowledge of web frameworks (Flask, Django)
- Experience with databases (PostgreSQL, MySQL)
- Familiarity with version control (Git)
- Knowledge of REST APIs and microservices
- Experience with testing frameworks (pytest, unittest)

Responsibilities:
- Develop and maintain web applications using Python
- Collaborate with cross-functional teams
- Write clean, maintainable code
- Participate in code reviews
- Troubleshoot and debug applications

Nice to have:
- Experience with cloud platforms (AWS, Azure)
- Knowledge of containerization (Docker)
- Familiarity with CI/CD pipelines"""
    }
    return jsonify(sample)

@bp.route('/export-pdf')
def export_pdf():
    """Export results as PDF (simple print-friendly version)."""
    return render_template('results.html', results=request.args.to_dict(), print_mode=True)


@bp.route('/system-status')
def system_status():
    """System health check endpoint."""
    import os
    from datetime import datetime
    from app import extensions
    from app.config import Config
    from app.services.data_loader import load_question_bank

    status = {
        'flask': 'running',
        'timestamp': datetime.utcnow().isoformat(),
    }
    
    # MongoDB Status
    try:
        if extensions.mongo_client:
            extensions.mongo_client.admin.command('ping')
            status['mongodb'] = 'connected'
            status['mongodb_uri'] = f"{Config.MONGO_URI.split('@')[-1] if '@' in Config.MONGO_URI else Config.MONGO_URI}"
        else:
            status['mongodb'] = 'not_configured'
            status['mongodb_error'] = 'MongoDB client not initialized'
    except Exception as e:
        status['mongodb'] = 'error'
        status['mongodb_error'] = str(e)
    
    # Authentication Status
    try:
        status['authentication'] = 'configured'
        status['auth_provider'] = 'flask_login'
    except Exception as e:
        status['authentication'] = 'error'
        status['auth_error'] = str(e)
    
    # Resume Analyzer Status
    try:
        from app.nlp_processor import NLPProcessor
        from app.scoring_engine import ScoringEngine
        nlp_processor = NLPProcessor()
        scoring_engine = ScoringEngine()
        status['resume_analyzer'] = 'operational'
    except Exception as e:
        status['resume_analyzer'] = 'error'
        status['resume_analyzer_error'] = str(e)
    
    # Quiz Engine Status
    try:
        bank = load_question_bank()
        status['quiz_engine'] = 'operational'
        status['quiz_bank_subjects'] = list(bank.keys())
        status['quiz_bank_total_questions'] = sum(
            len(d.get(level, [])) for d in bank.values() for level in ['easy', 'medium', 'hard']
        )
    except Exception as e:
        status['quiz_engine'] = 'error'
        status['quiz_engine_error'] = str(e)
    
    return jsonify(status)


@bp.route('/system-status-page')
def system_status_page():
    """Render system status page."""
    return render_template('system_status.html')
