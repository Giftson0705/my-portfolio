from fastapi import FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, EmailStr, field_validator
from typing import List, Optional
from contextlib import asynccontextmanager
from datetime import datetime
import sqlite3
import hashlib
import os
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database setup
DATABASE_PATH = "portfolio.db"

def init_database():
    """Initialize SQLite database with required tables"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    # Contact messages table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS contact_messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            subject TEXT NOT NULL,
            message TEXT NOT NULL,
            is_spam BOOLEAN DEFAULT FALSE,
            is_read BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            ip_address TEXT
        )
    ''')
    
    # Projects table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            image_url TEXT,
            github_url TEXT,
            live_url TEXT,
            technologies TEXT NOT NULL,
            featured BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Skills table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS skills (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT NOT NULL,
            name TEXT NOT NULL,
            description TEXT,
            icon_class TEXT,
            proficiency INTEGER DEFAULT 0
        )
    ''')
    
    conn.commit()
    conn.close()
    
    # Insert sample data
    insert_sample_data()

def insert_sample_data():
    """Insert sample projects and skills from your portfolio"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    # Check if data already exists
    cursor.execute("SELECT COUNT(*) FROM projects")
    if cursor.fetchone()[0] == 0:
        # Insert your projects
        projects_data = [
            (
                "Enhanced GAN-based Framework for Super Resolution of Satellite Images",
                "Developed an advanced deep learning framework using SRGAN to enhance the resolution of satellite imagery for applications in urban planning, environmental monitoring, and disaster management.",
                "assets/spacex.jpg",
                "https://github.com/Giftson0705/Enhanced-GAN-Based-Framework-for-Super-Resolution-of-Satellite-Images",
                None,
                "Python,GAN,DL Frameworks",
                True
            ),
            (
                "Cricket Score Predictor",
                "Developed a machine learning model using Python, XGBoost, Pandas, and Scikit-learn to forecast cricket scores based on historical match data.",
                "assets/Shane_Watson.jpg",
                "https://github.com/Giftson0705/Cricket-Score-Predictor",
                None,
                "Python,XGBoost,ML Frameworks",
                True
            )
        ]
        
        cursor.executemany('''
            INSERT INTO projects (title, description, image_url, github_url, live_url, technologies, featured)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', projects_data)
        
        # Insert your skills
        skills_data = [
            ("Frontend", "HTML5, CSS3, JavaScript", "Modern frontend technologies", "fab fa-html5", 85),
            ("Backend", "Python, RESTful APIs", "Server-side development", "fas fa-server", 90),
            ("Database", "MongoDB, MySQL", "Database management", "fas fa-database", 80),
            ("Tools", "Git, AWS", "Development tools", "fab fa-git-alt", 85)
        ]
        
        cursor.executemany('''
            INSERT INTO skills (category, description, name, icon_class, proficiency)
            VALUES (?, ?, ?, ?, ?)
        ''', skills_data)
    
    conn.commit()
    conn.close()

# Lifespan event handler (replaces deprecated on_event)
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    init_database()
    logger.info("Database initialized successfully")
    yield
    # Shutdown (if needed)

# Initialize FastAPI app with lifespan
app = FastAPI(
    title="Giftson's Portfolio API",
    description="API for portfolio website with contact form and project management",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware to allow frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# Pydantic models for request/response validation
class ContactMessage(BaseModel):
    name: str
    email: EmailStr
    subject: str
    message: str
    
    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        if len(v.strip()) < 2:
            raise ValueError('Name must be at least 2 characters long')
        if any(char.isdigit() for char in v):
            raise ValueError('Name should not contain numbers')
        return v.strip()
    
    @field_validator('message')
    @classmethod
    def validate_message(cls, v):
        if len(v.strip()) < 10:
            raise ValueError('Message must be at least 10 characters long')
        return v.strip()

class ContactMessageResponse(BaseModel):
    id: int
    name: str
    email: str
    subject: str
    message: str
    is_spam: bool
    is_read: bool
    created_at: datetime

class Project(BaseModel):
    title: str
    description: str
    image_url: Optional[str] = None
    github_url: Optional[str] = None
    live_url: Optional[str] = None
    technologies: str
    featured: bool = False

class ProjectResponse(BaseModel):
    id: int
    title: str
    description: str
    image_url: Optional[str]
    github_url: Optional[str]
    live_url: Optional[str]
    technologies: List[str]
    featured: bool
    created_at: datetime

class Skill(BaseModel):
    category: str
    name: str
    description: Optional[str] = None
    icon_class: Optional[str] = None
    proficiency: int = 0

class SkillResponse(BaseModel):
    id: int
    category: str
    name: str
    description: Optional[str]
    icon_class: Optional[str]
    proficiency: int

# Utility functions
def get_db_connection():
    """Get database connection"""
    return sqlite3.connect(DATABASE_PATH)

def detect_spam(message: str) -> bool:
    """Simple spam detection based on keywords"""
    spam_keywords = ['viagra', 'casino', 'lottery', 'winner', 'free money', 'click here']
    return any(keyword in message.lower() for keyword in spam_keywords)

def get_client_ip(request: Request):
    """Get client IP address"""
    return getattr(request.client, 'host', 'unknown')

# Rate limiting (simple implementation)
request_counts = {}

def check_rate_limit(ip: str, limit: int = 5) -> bool:
    """Check if IP has exceeded rate limit (5 requests per hour)"""
    current_time = datetime.now()
    
    if ip not in request_counts:
        request_counts[ip] = []
    
    # Remove old requests (older than 1 hour)
    request_counts[ip] = [
        timestamp for timestamp in request_counts[ip]
        if (current_time - timestamp).total_seconds() < 3600
    ]
    
    if len(request_counts[ip]) >= limit:
        return False
    
    request_counts[ip].append(current_time)
    return True

# API Routes

@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "Welcome to Giftson's Portfolio API", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now()}

# Contact Form Routes
@app.post("/api/contact", response_model=dict)
async def submit_contact_form(contact_data: ContactMessage, request: Request):
    """Submit contact form - matches your frontend form"""
    try:
        # Get client IP for rate limiting
        client_ip = get_client_ip(request)
        
        # Check rate limiting
        if not check_rate_limit(client_ip):
            raise HTTPException(
                status_code=429,
                detail="Too many requests. Please try again later."
            )
        
        # Detect spam
        is_spam = detect_spam(contact_data.message)
        
        # Save to database
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO contact_messages (name, email, subject, message, is_spam, ip_address)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            contact_data.name,
            contact_data.email,
            contact_data.subject,
            contact_data.message,
            is_spam,
            client_ip
        ))
        
        conn.commit()
        message_id = cursor.lastrowid
        conn.close()
        
        logger.info(f"Contact form submitted: ID {message_id}, Spam: {is_spam}")
        
        return {
            "success": True,
            "message": "Message sent successfully!",
            "id": message_id
        }
        
    except Exception as e:
        logger.error(f"Error submitting contact form: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/api/messages", response_model=List[ContactMessageResponse])
async def get_contact_messages(skip: int = 0, limit: int = 100, spam_only: bool = False):
    """Get all contact messages (admin endpoint)"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    query = "SELECT * FROM contact_messages"
    params = []
    
    if spam_only:
        query += " WHERE is_spam = 1"
    
    query += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
    params.extend([limit, skip])
    
    cursor.execute(query, params)
    messages = cursor.fetchall()
    conn.close()
    
    return [
        ContactMessageResponse(
            id=msg[0],
            name=msg[1],
            email=msg[2],
            subject=msg[3],
            message=msg[4],
            is_spam=bool(msg[5]),
            is_read=bool(msg[6]),
            created_at=datetime.fromisoformat(msg[7])
        )
        for msg in messages
    ]

@app.get("/api/projects", response_model=List[ProjectResponse])
async def get_projects(featured_only: bool = False):
    """Get all projects"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if featured_only:
        cursor.execute("SELECT * FROM projects WHERE featured = 1 ORDER BY created_at DESC")
    else:
        cursor.execute("SELECT * FROM projects ORDER BY created_at DESC")
    
    projects = cursor.fetchall()
    conn.close()
    
    return [
        ProjectResponse(
            id=proj[0],
            title=proj[1],
            description=proj[2],
            image_url=proj[3],
            github_url=proj[4],
            live_url=proj[5],
            technologies=proj[6].split(',') if proj[6] else [],
            featured=bool(proj[7]),
            created_at=datetime.fromisoformat(proj[8])
        )
        for proj in projects
    ]

@app.get("/api/skills", response_model=List[SkillResponse])
async def get_skills():
    """Get all skills"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM skills ORDER BY category, name")
    skills = cursor.fetchall()
    conn.close()
    
    return [
        SkillResponse(
            id=skill[0],
            category=skill[1],
            name=skill[2],
            description=skill[3],
            icon_class=skill[4],
            proficiency=skill[5]
        )
        for skill in skills
    ]

@app.get("/api/stats")
async def get_portfolio_stats():
    """Get portfolio statistics"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM contact_messages")
    total_messages = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM contact_messages WHERE is_read = 0")
    unread_messages = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM contact_messages WHERE is_spam = 1")
    spam_messages = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM projects")
    total_projects = cursor.fetchone()[0]
    
    conn.close()
    
    return {
        "total_messages": total_messages,
        "unread_messages": unread_messages,
        "spam_messages": spam_messages,
        "total_projects": total_projects
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("API:app", host="0.0.0.0", port=8000, reload=True)