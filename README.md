# ResumeATS - Resume Tracking and Scoring System

## Overview
**ResumeATS** is a web application that helps recruiters and hiring managers streamline their candidate selection process by automatically parsing, analyzing, and scoring resumes against job postings. The system extracts key information from resumes and evaluates them based on keyword matching to quickly identify the most qualified candidates.

---

## Features

- **User Authentication**: Secure registration and login system  
- **Job Posting Management**: Create and manage job postings with specific keywords  
- **Resume Analysis**: Upload and automatically parse resumes in PDF or DOCX formats  
- **Intelligent Scoring**: Score resumes based on keyword matches with job requirements  
- **Candidate Management**: Track and review multiple candidates for each job posting  
- **Administrative Dashboard**: Overview of all job postings and top candidates  

---

## Tech Stack

- **Backend**: Flask (Python)  
- **Database**: SQLAlchemy with SQLite/PostgreSQL  
- **Frontend**: HTML, CSS, JavaScript (templates not included in the repository)  
- **Authentication**: Flask-Login  
- **Form Handling**: Flask-WTF, WTForms  
- **Resume Parsing**: PyPDF2, python-docx, NLTK  
- **Deployment**: Gunicorn, Replit  

---

## Installation

### Prerequisites
- Python 3.11 or higher  
- pip (Python package installer)  

### Setup

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd resumeats
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
   or using the project file:
   ```bash
   pip install -e .
   ```

3. **Set environment variables**:
   ```bash
   export SESSION_SECRET="your-secret-key"
   export DATABASE_URL="sqlite:///resumes.db"  # or your PostgreSQL connection string
   ```

4. **Initialize the database**:
   ```bash
   flask shell
   >>> from app import db
   >>> db.create_all()
   >>> exit()
   ```

5. **Run the application**:
   - For production:
     ```bash
     gunicorn --bind 0.0.0.0:5000 main:app
     ```
   - For development:
     ```bash
     flask run --debug
     ```

---

## Usage

### Registration and Login
- Register a new account at `/register`
- Log in with your credentials at `/login`

### Creating Job Postings
1. Navigate to the dashboard  
2. Click **"Create Job Posting"**  
3. Fill in the job title, description, and keywords  
4. Submit the form to create the posting  

### Analyzing Resumes
1. Go to the **"Upload Resume"** page  
2. Select a job posting from the dropdown  
3. Upload a candidate's resume (PDF or DOCX)  
4. The system will automatically parse and score the resume  
5. View the detailed analysis and matching score  

### Reviewing Candidates
1. Navigate to a specific job posting  
2. View all resumes submitted for the position, sorted by score  
3. Click on individual resumes to see detailed information  

---

## Application Structure

- `app.py`: Main application file with routes and configuration  
- `auth.py`: Authentication related routes  
- `forms.py`: Form classes for data validation  
- `models.py`: Database models  
- `resume_parser.py`: Logic for extracting data from resume files  
- `resume_scorer.py`: Algorithm for scoring resumes against keywords  
- `main.py`: Entry point for the application  
- `uploads/`: Directory for storing uploaded resume files  

---

## Resume Parsing Details

The system extracts the following information from resumes:

- Candidate name  
- Email address  
- Skills  
- Education history  
- Work experience  
- Full text content  

---

## Scoring Algorithm

Resumes are scored based on:

- Exact keyword matches with job posting requirements  
- Partial matches for multi-word keywords  
- Bonus points for high match percentages  
- Final score between 0–100  

---

## Deployment

The application is configured for deployment on **Replit** with the following setup:

- Gunicorn as the WSGI server  
- PostgreSQL database support  
- Automatic port binding  
- Environment variable configuration  

---

## Future Improvements

- Enhanced resume parsing with machine learning  
- More detailed candidate profiles  
- Interview scheduling and tracking  
- Email notifications for new applications  
- Customizable scoring algorithms  
- Integration with job boards  
