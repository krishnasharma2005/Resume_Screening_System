import os
import logging
from flask import Flask, render_template, redirect, url_for, flash, request, session
from flask_login import LoginManager, login_required, current_user, login_user, logout_user
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.middleware.proxy_fix import ProxyFix
from werkzeug.utils import secure_filename
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
import datetime
import os.path

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Create base class for SQLAlchemy models
class Base(DeclarativeBase):
    pass

# Initialize SQLAlchemy
db = SQLAlchemy(model_class=Base)

# Create the Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)  # needed for url_for to generate with https

# Configure the database
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///resumes.db")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}
app.config["UPLOAD_FOLDER"] = "uploads"
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16MB max upload size
app.config["ALLOWED_EXTENSIONS"] = {"pdf", "docx"}

# Initialize SQLAlchemy with the app
db.init_app(app)

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

# Create upload folder if it doesn't exist
if not os.path.exists(app.config["UPLOAD_FOLDER"]):
    os.makedirs(app.config["UPLOAD_FOLDER"])

# Import models (after db initialization to avoid circular imports)
with app.app_context():
    from models import User, Resume, Keyword, JobPosting
    db.create_all()

# Import other modules
from auth import *
from forms import *
from resume_parser import extract_resume_data
from resume_scorer import score_resume

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Home page route
@app.route("/")
def index():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))
    return render_template("index.html")

# Dashboard route
@app.route("/dashboard")
@login_required
def dashboard():
    job_postings = JobPosting.query.filter_by(user_id=current_user.id).all()
    return render_template("dashboard.html", job_postings=job_postings)

# Resume upload route
@app.route("/upload", methods=["GET", "POST"])
@login_required
def upload_resume():
    form = UploadResumeForm()
    if form.validate_on_submit():
        job_posting_id = form.job_posting.data
        
        # Check if job posting exists and belongs to user
        job_posting = JobPosting.query.filter_by(id=job_posting_id, user_id=current_user.id).first()
        if not job_posting:
            flash("Invalid job posting selected.", "danger")
            return redirect(url_for("upload_resume"))
        
        # Get the file from the form
        uploaded_file = form.resume.data
        filename = secure_filename(uploaded_file.filename)
        
        # Check if the file extension is allowed
        if not allowed_file(filename):
            flash("Invalid file format. Please upload a PDF or DOCX file.", "danger")
            return redirect(url_for("upload_resume"))
        
        # Save the file
        file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        uploaded_file.save(file_path)
        
        try:
            # Extract data from the resume
            resume_data = extract_resume_data(file_path)
            
            # Score the resume based on job posting keywords
            job_keywords = [keyword.word for keyword in job_posting.keywords]
            score, matches = score_resume(resume_data, job_keywords)
            
            # Create a new resume record
            resume = Resume(
                filename=filename,
                file_path=file_path,
                candidate_name=resume_data.get("name", "Unknown"),
                candidate_email=resume_data.get("email", ""),
                skills=resume_data.get("skills", []),
                education=resume_data.get("education", []),
                experience=resume_data.get("experience", []),
                content=resume_data.get("text", ""),
                score=score,
                job_posting_id=job_posting_id
            )
            
            db.session.add(resume)
            db.session.commit()
            
            flash(f"Resume uploaded and scored {score}/100 successfully!", "success")
            return redirect(url_for("view_resume", id=resume.id))
            
        except Exception as e:
            logging.error(f"Error processing resume: {e}")
            flash(f"Error processing resume: {str(e)}", "danger")
            return redirect(url_for("upload_resume"))
    
    # Get all job postings for the form dropdown
    job_postings = JobPosting.query.filter_by(user_id=current_user.id).all()
    form.job_posting.choices = [(jp.id, jp.title) for jp in job_postings]
    
    return render_template("upload_resume.html", form=form)

# Job posting creation route
@app.route("/job-posting/new", methods=["GET", "POST"])
@login_required
def new_job_posting():
    form = JobPostingForm()
    if form.validate_on_submit():
        # Create a new job posting
        job_posting = JobPosting(
            title=form.title.data,
            description=form.description.data,
            user_id=current_user.id
        )
        
        db.session.add(job_posting)
        db.session.commit()
        
        # Process keywords
        keywords_text = form.keywords.data
        keyword_list = [k.strip() for k in keywords_text.split(',') if k.strip()]
        
        for keyword in keyword_list:
            kw = Keyword(
                word=keyword.lower(),
                job_posting_id=job_posting.id
            )
            db.session.add(kw)
        
        db.session.commit()
        
        flash(f"Job posting '{form.title.data}' created successfully!", "success")
        return redirect(url_for("dashboard"))
    
    return render_template("job_posting_form.html", form=form, title="Create Job Posting")

# View job posting resumes
@app.route("/job-posting/<int:id>")
@login_required
def view_job_posting(id):
    job_posting = JobPosting.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    resumes = Resume.query.filter_by(job_posting_id=id).order_by(Resume.score.desc()).all()
    
    return render_template("job_posting_detail.html", job_posting=job_posting, resumes=resumes)

# View single resume
@app.route("/resume/<int:id>")
@login_required
def view_resume(id):
    resume = Resume.query.get_or_404(id)
    
    # Check if user has access to this resume
    job_posting = JobPosting.query.filter_by(id=resume.job_posting_id, user_id=current_user.id).first()
    if not job_posting:
        flash("You don't have permission to view this resume.", "danger")
        return redirect(url_for("dashboard"))
    
    # Get keywords for highlighting
    keywords = [kw.word for kw in job_posting.keywords]
    
    return render_template("view_resume.html", resume=resume, job_posting=job_posting, keywords=keywords)

# Admin dashboard route
@app.route("/admin")
@login_required
def admin_dashboard():
    # For simplicity, any authenticated user can access the admin dashboard
    job_postings = JobPosting.query.filter_by(user_id=current_user.id).all()
    
    # Get all resumes for the user's job postings
    resumes = []
    for job_posting in job_postings:
        job_resumes = Resume.query.filter_by(job_posting_id=job_posting.id).all()
        resumes.extend(job_resumes)
    
    # Sort resumes by score
    resumes.sort(key=lambda x: x.score, reverse=True)
    
    return render_template("admin_dashboard.html", job_postings=job_postings, resumes=resumes)

# Helper function to check if file extension is allowed
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config["ALLOWED_EXTENSIONS"]
