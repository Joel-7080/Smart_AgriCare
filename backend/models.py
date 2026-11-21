from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()


class UploadHistory(db.Model):
    """Model to store upload history for each user"""
    __tablename__ = 'upload_history'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False, index=True)
    filename = db.Column(db.String(255), nullable=False)
    original_filename = db.Column(db.String(255), nullable=False)
    crop = db.Column(db.String(100), nullable=True)
    disease = db.Column(db.String(255), nullable=True)
    confidence = db.Column(db.String(50), nullable=True)
    symptoms = db.Column(db.Text, nullable=True)
    chemical_pesticides = db.Column(db.JSON, nullable=True)
    organic_treatments = db.Column(db.JSON, nullable=True)
    prevention_measures = db.Column(db.JSON, nullable=True)
    upload_date = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    notes = db.Column(db.Text, nullable=True)
    
    def to_dict(self):
        """Convert model instance to dictionary"""
        return {
            'id': self.id,
            'filename': self.filename,
            'original_filename': self.original_filename,
            'crop': self.crop,
            'disease': self.disease,
            'confidence': self.confidence,
            'symptoms': self.symptoms,
            'chemical_pesticides': self.chemical_pesticides,
            'organic_treatments': self.organic_treatments,
            'prevention_measures': self.prevention_measures,
            'upload_date': self.upload_date.isoformat() if self.upload_date else None,
            'notes': self.notes
        }
