import os
import re
import logging
from PyPDF2 import PdfReader
import docx
from nltk.tokenize import word_tokenize, sent_tokenize
import nltk

# Download NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

def extract_resume_data(file_path):
    """
    Extract data from a resume file (PDF or DOCX).
    
    Args:
        file_path: Path to the resume file
        
    Returns:
        dict: Dictionary containing extracted resume data
    """
    file_ext = os.path.splitext(file_path)[1].lower()
    
    if file_ext == '.pdf':
        return extract_from_pdf(file_path)
    elif file_ext == '.docx':
        return extract_from_docx(file_path)
    else:
        raise ValueError(f"Unsupported file format: {file_ext}")

def extract_from_pdf(file_path):
    """Extract text and data from a PDF file"""
    try:
        reader = PdfReader(file_path)
        text = ""
        
        for page in reader.pages:
            text += page.extract_text() + "\n"
            
        return process_text(text)
    except Exception as e:
        logging.error(f"Error extracting text from PDF: {e}")
        raise

def extract_from_docx(file_path):
    """Extract text and data from a DOCX file"""
    try:
        doc = docx.Document(file_path)
        text = ""
        
        for para in doc.paragraphs:
            text += para.text + "\n"
            
        return process_text(text)
    except Exception as e:
        logging.error(f"Error extracting text from DOCX: {e}")
        raise

def process_text(text):
    """Process the extracted text to get structured resume data"""
    # Create the base resume data structure
    resume_data = {
        "text": text,
        "name": extract_name(text),
        "email": extract_email(text),
        "skills": extract_skills(text),
        "education": extract_education(text),
        "experience": extract_experience(text)
    }
    
    return resume_data

def extract_name(text):
    """Extract candidate name from the text (usually from the top of the resume)"""
    # Simple approach: take the first line that's not empty
    lines = text.split('\n')
    for line in lines:
        if line.strip() and len(line.strip().split()) <= 4:
            # Most likely a name if it's at the top and has 1-4 words
            return line.strip()
    
    return "Unknown"

def extract_email(text):
    """Extract email address from text"""
    # Email regex pattern
    email_regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    match = re.search(email_regex, text)
    
    if match:
        return match.group()
    return ""

def extract_skills(text):
    """Extract skills from the resume text"""
    # Common skill section headers
    skill_headers = ['skills', 'technical skills', 'core competencies', 'technologies']
    
    skills = []
    
    # Split into sentences
    sentences = sent_tokenize(text.lower())
    
    # Look for skill sections
    for i, sentence in enumerate(sentences):
        for header in skill_headers:
            if header in sentence:
                # If a skill section is found, look at the next few sentences
                for j in range(i+1, min(i+10, len(sentences))):
                    # Split by commas, semicolons, or new lines
                    skill_parts = re.split(r'[,;\n]', sentences[j])
                    for part in skill_parts:
                        part = part.strip()
                        if part and len(part.split()) <= 5:  # Most skills are 1-5 words
                            skills.append(part)
    
    # If no skills were found using headers, try a more generic approach
    if not skills:
        # Look for bullet points or similar patterns
        skill_patterns = re.findall(r'[•\-\*] ([^•\-\*\n]+)', text)
        for pattern in skill_patterns:
            pattern = pattern.strip()
            if pattern and len(pattern.split()) <= 5:
                skills.append(pattern)
    
    # Deduplicate skills
    return list(set(skills))

def extract_education(text):
    """Extract education information from the resume text"""
    education = []
    
    # Common education section headers
    edu_headers = ['education', 'academic background', 'qualifications']
    
    # Split into sentences
    sentences = sent_tokenize(text.lower())
    
    # Common degree names
    degree_patterns = [
        'bachelor', 'master', 'phd', 'doctorate', 'mba', 
        'bs', 'ba', 'ms', 'ma', 'btech', 'mtech'
    ]
    
    # Look for education sections or degree mentions
    edu_section = False
    for i, sentence in enumerate(sentences):
        # Check for education section headers
        for header in edu_headers:
            if header in sentence:
                edu_section = True
                break
        
        if edu_section:
            # Look for degree patterns in this and the next few sentences
            for j in range(i, min(i+15, len(sentences))):
                for degree in degree_patterns:
                    if degree in sentences[j].lower():
                        education.append(sentences[j].strip())
                        break
        
        # Exit education section when we hit another section header
        if edu_section and i > 0 and sentences[i-1].strip().endswith(':'):
            edu_section = False
    
    # Deduplicate education entries
    return list(set(education))

def extract_experience(text):
    """Extract work experience information from the resume text"""
    experience = []
    
    # Common experience section headers
    exp_headers = ['experience', 'work experience', 'employment history', 'work history']
    
    # Split into sentences
    sentences = sent_tokenize(text.lower())
    
    # Look for experience sections
    exp_section = False
    for i, sentence in enumerate(sentences):
        # Check for experience section headers
        for header in exp_headers:
            if header in sentence:
                exp_section = True
                break
        
        if exp_section:
            # Add sentences that might be job titles or companies
            if len(sentence.split()) <= 10 and not sentence.strip().endswith(':'):
                experience.append(sentence.strip())
        
        # Exit experience section when we hit another section header
        if exp_section and i > 0 and sentences[i-1].strip().endswith(':'):
            exp_section = False
    
    # If we didn't find much, look for date patterns which often indicate job experiences
    if len(experience) < 2:
        date_pattern = r'(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec|January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4}\s*(-|–|to)\s*(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec|January|February|March|April|May|June|July|August|September|October|November|December)?\s*\d{0,4}|(\d{4}\s*(-|–|to)\s*\d{0,4}|\d{4}\s*(-|–|to)\s*(Present|present|Current|current))'
        date_matches = re.finditer(date_pattern, text)
        
        for match in date_matches:
            # Get the sentence containing this date
            start_pos = max(0, match.start() - 100)
            end_pos = min(len(text), match.end() + 100)
            context = text[start_pos:end_pos]
            
            # Split into sentences and take the one with the date
            context_sentences = sent_tokenize(context)
            for sent in context_sentences:
                if match.group() in sent:
                    experience.append(sent.strip())
                    break
    
    # Deduplicate experience entries
    return list(set(experience))
