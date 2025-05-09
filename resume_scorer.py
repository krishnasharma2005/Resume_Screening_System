import logging
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import string
import re

# Download NLTK data
try:
    nltk.data.find('tokenizers/punkt')
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('punkt')
    nltk.download('stopwords')

def score_resume(resume_data, keywords):
    """
    Score a resume based on keyword matches.
    
    Args:
        resume_data: Dictionary containing parsed resume data
        keywords: List of keywords to match against
        
    Returns:
        tuple: (score, matched_keywords)
    """
    try:
        # Get the full text of the resume
        resume_text = resume_data['text'].lower()
        
        # Extract other relevant fields
        skills = [skill.lower() for skill in resume_data.get('skills', [])]
        education = [edu.lower() for edu in resume_data.get('education', [])]
        experience = [exp.lower() for exp in resume_data.get('experience', [])]
        
        # Combine all fields for comprehensive matching
        all_fields = resume_text + " " + " ".join(skills) + " " + " ".join(education) + " " + " ".join(experience)
        
        # Preprocess the text
        all_fields = preprocess_text(all_fields)
        
        # Initialize score calculation
        matched_keywords = []
        total_keywords = len(keywords)
        
        # Ensure we have keywords to match
        if total_keywords == 0:
            return 0, []
        
        # Check for each keyword
        for keyword in keywords:
            # Preprocess the keyword for consistent matching
            processed_keyword = preprocess_text(keyword.lower())
            
            # Look for exact matches
            if processed_keyword in all_fields:
                matched_keywords.append(keyword)
            else:
                # Look for partial matches (for multi-word keywords)
                keyword_parts = processed_keyword.split()
                if len(keyword_parts) > 1:
                    match_count = sum(1 for part in keyword_parts if part in all_fields.split())
                    if match_count / len(keyword_parts) >= 0.5:  # If at least half the parts match
                        matched_keywords.append(keyword)
        
        # Calculate score (0-100)
        match_count = len(matched_keywords)
        score = (match_count / total_keywords) * 100
        
        # Add bonus for high match percentage
        if match_count / total_keywords > 0.8:
            score += 10
            
        # Cap the score at 100
        score = min(score, 100)
        
        return round(score, 1), matched_keywords
        
    except Exception as e:
        logging.error(f"Error scoring resume: {e}")
        return 0, []

def preprocess_text(text):
    """
    Preprocess text for better keyword matching:
    - Remove punctuation
    - Convert to lowercase
    - Remove stopwords
    - Remove extra whitespace
    
    Args:
        text: Text to preprocess
        
    Returns:
        str: Preprocessed text
    """
    # Remove punctuation
    text = text.translate(str.maketrans('', '', string.punctuation))
    
    # Convert to lowercase
    text = text.lower()
    
    # Tokenize and remove stopwords
    stop_words = set(stopwords.words('english'))
    tokens = word_tokenize(text)
    filtered_tokens = [word for word in tokens if word not in stop_words]
    
    # Rejoin the tokens
    text = ' '.join(filtered_tokens)
    
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text
