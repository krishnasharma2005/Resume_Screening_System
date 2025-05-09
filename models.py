from app import db
from flask_login import UserMixin
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Float, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.ext.mutable import MutableList
from sqlalchemy.dialects.mysql import JSON

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    job_postings = db.relationship('JobPosting', backref='user', lazy=True)
    
    def __repr__(self):
        return f'<User {self.username}>'

class JobPosting(db.Model):
    __tablename__ = 'job_postings'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Relationships
    keywords = db.relationship('Keyword', backref='job_posting', lazy=True, cascade="all, delete-orphan")
    resumes = db.relationship('Resume', backref='job_posting', lazy=True)
    
    def __repr__(self):
        return f'<JobPosting {self.title}>'

class Keyword(db.Model):
    __tablename__ = 'keywords'
    
    id = db.Column(db.Integer, primary_key=True)
    word = db.Column(db.String(50), nullable=False)
    job_posting_id = db.Column(db.Integer, db.ForeignKey('job_postings.id'), nullable=False)
    
    def __repr__(self):
        return f'<Keyword {self.word}>'

class Resume(db.Model):
    __tablename__ = 'resumes'
    
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(100), nullable=False)
    file_path = db.Column(db.String(255), nullable=False)
    upload_date = db.Column(db.DateTime, default=datetime.utcnow)
    candidate_name = db.Column(db.String(100))
    candidate_email = db.Column(db.String(120))
    skills = db.Column(JSON)  # Stored as JSON array
    education = db.Column(JSON)  # Stored as JSON array
    experience = db.Column(JSON)  # Stored as JSON array
    content = db.Column(db.Text)  # Full text content of the resume
    score = db.Column(db.Float, default=0.0)  # Score from keyword matching
    job_posting_id = db.Column(db.Integer, db.ForeignKey('job_postings.id'), nullable=False)
    
    def __repr__(self):
        return f'<Resume {self.candidate_name}>'
