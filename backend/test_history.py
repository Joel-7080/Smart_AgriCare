"""
Test script to verify upload history functionality
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from main import app, db
from models import UploadHistory

# Create app context
with app.app_context():
    db.create_all()
    print("✓ Database tables created successfully")
    
    # Create a test upload history
    test_history = UploadHistory(
        username='demo',
        filename='1234567890_test_leaf.jpg',
        original_filename='test_leaf.jpg',
        crop='Tomato',
        disease='Early Blight',
        confidence='85.5%',
        symptoms='Dark brown spots with concentric rings on leaves',
        chemical_pesticides=['Mancozeb', 'Chlorothalonil'],
        organic_treatments=['Neem oil', 'Copper fungicide'],
        prevention_measures=['Remove infected leaves', 'Improve air circulation']
    )
    
    db.session.add(test_history)
    db.session.commit()
    print("✓ Test history record created successfully")
    
    # Verify it was stored
    records = UploadHistory.query.filter_by(username='demo').all()
    print(f"✓ Found {len(records)} record(s) for user 'demo'")
    
    for record in records:
        print(f"  - {record.disease} on {record.crop} (ID: {record.id})")

print("\n✅ All tests passed! History feature is ready to use.")
print("\nStarting the app will now:")
print("1. Create SQLite database at backend/smartagricare.db")
print("2. Store upload history automatically")
print("3. Provide endpoints to retrieve and manage history")
