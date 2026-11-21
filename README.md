# 🌱 Smart AgriCare - Plant Disease Detection System

A web-based application that identifies crop diseases from leaf or fruit images and recommends appropriate pesticides (chemical and organic) and prevention measures.

## 📋 Features

- **Image Upload**: Upload photos of diseased leaves or fruits
- **AI-Powered Detection**: Uses Kindwise crop.health API for accurate disease identification
- **Crop Recognition**: Automatically identifies the crop type
- **Disease Diagnosis**: Detects and names the specific disease
- **Smart Recommendations**:
  - Chemical pesticide options
  - Organic treatment alternatives
  - Prevention measures
  - Symptom description
- **User-Friendly Interface**: Clean, responsive web interface
- **Real-Time Analysis**: Instant results after image upload

## 🏗️ Project Structure

```
Smart AgriCare/
├── backend/
│   ├── main.py                 # Flask API entry point
│   ├── requirements.txt        # Python dependencies
│   ├── .env                    # Environment variables (API key)
│   ├── services/
│   │   └── kindwise_service.py # Kindwise API integration
│   ├── data/
│   │   └── pesticide_db.json   # Disease-to-pesticide mapping
│   ├── templates/
│   │   └── index.html          # Frontend UI
│   ├── static/
│   │   ├── css/style.css       # Styling
│   │   └── js/script.js        # Frontend logic
│   └── uploads/                # Temporary image storage
└── README.md                   # This file
```

## 🛠️ Technology Stack

| Component | Technology |
|-----------|-----------|
| **Backend** | Python, Flask, Flask-CORS |
| **Frontend** | HTML5, CSS3, Vanilla JavaScript |
| **AI/ML** | Kindwise crop.health API |
| **Data** | JSON (disease-pesticide mapping) |
| **Security** | Environment variables (.env) |

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Internet connection (for Kindwise API)

### Installation

1. **Navigate to backend directory**:
   ```bash
   cd backend
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Verify environment setup**:
   - The `.env` file should already contain your API key
   - Check: `cat .env`

4. **Start the server**:
   ```bash
   python main.py
   ```

5. **Access the application**:
   - Open your browser and go to: `http://localhost:5000`

## 📖 How It Works

### Flow Diagram

```
User uploads image
       ↓
Backend receives and saves image
       ↓
Convert image to Base64
       ↓
Send to Kindwise crop.health API
       ↓
Kindwise returns crop & disease info
       ↓
Backend maps disease → pesticide data
       ↓
Frontend displays formatted results
```

### API Endpoints

#### 1. **POST /api/analyze**
Analyzes uploaded image and returns disease information.

**Request:**
```bash
curl -X POST http://localhost:5000/api/analyze \
  -F "file=@path/to/image.jpg"
```

**Response:**
```json
{
  "success": true,
  "crop": "Tomato",
  "disease": "Early Blight",
  "confidence": "85.3%",
  "analysis": {
    "symptoms": "Brown spots with concentric rings...",
    "chemical_pesticides": ["Chlorothalonil", "Mancozeb", ...],
    "organic_treatments": ["Neem oil spray", "Bordeaux mixture", ...],
    "prevention": ["Remove affected leaves", ...]
  }
}
```

#### 2. **GET /api/health**
Health check endpoint.

**Response:**
```json
{
  "status": "ok",
  "message": "Smart AgriCare API is running"
}
```

## 🗄️ Database Structure

The `pesticide_db.json` contains disease information with this structure:

```json
{
  "diseases": {
    "disease_key": {
      "crop": "Crop Name",
      "disease_name": "Disease Name",
      "symptoms": "Symptom description",
      "chemical_pesticides": ["Pesticide 1", "Pesticide 2"],
      "organic_treatments": ["Treatment 1", "Treatment 2"],
      "prevention": ["Prevention measure 1", ...]
    }
  }
}
```

### Supported Diseases

- Early Blight (Tomato)
- Late Blight (Tomato)
- Powdery Mildew (Grapes, Cucumber, Squash)
- Leaf Spot (Various crops)
- Rust (Wheat, Barley)
- Anthracnose (Mango, Chilli, Cotton)
- Bacterial Wilt (Cucumber, Squash, Melon)
- Fusarium Wilt (Cotton, Tomato, Banana)
- Mosaic Virus (Tomato, Pepper, Cucumber)

## 🔒 Security Considerations

- **API Key Protection**: Stored in `.env` file (never committed to version control)
- **File Upload Validation**: 
  - Maximum file size: 10 MB
  - Allowed formats: JPG, PNG, GIF, BMP
  - Secure filename handling
- **CORS Enabled**: For cross-origin requests (configurable)
- **Input Validation**: All user inputs are validated before processing

## 📱 Browser Compatibility

- Chrome/Edge (latest)
- Firefox (latest)
- Safari (latest)
- Mobile browsers (iOS Safari, Chrome Mobile)

## 🎨 Frontend Features

- **Responsive Design**: Works on desktop, tablet, and mobile
- **Image Preview**: Live preview before analysis
- **Loading Indicator**: Visual feedback during processing
- **Error Handling**: User-friendly error messages
- **Result Cards**: Organized presentation of recommendations
- **One-Click Reset**: Easy analysis of multiple images

## 🔧 Environment Variables

Create or update `.env` file in the `backend` directory:

```env
KINDWISE_API_KEY=your_api_key_here
FLASK_ENV=development
FLASK_DEBUG=True
```

## 📊 Sample Workflow

1. **User Action**: Uploads a photo of a tomato leaf with brown spots
2. **Backend Processing**:
   - Saves the image
   - Converts to Base64
   - Sends to Kindwise API
3. **Kindwise Response**: Returns crop="Tomato", disease="Early Blight"
4. **Database Lookup**: Retrieves pesticide recommendations
5. **Result Display**: Shows symptoms, treatments, and prevention

## 🚨 Troubleshooting

### API Connection Issues
- Verify internet connection
- Check API key in `.env`
- Ensure API rate limits not exceeded

### Port Already in Use
```bash
# Kill process on port 5000 (macOS/Linux)
lsof -ti:5000 | xargs kill -9

# Or use a different port
python main.py --port 5001
```

### File Upload Errors
- Check file size (max 10 MB)
- Verify file format (JPG, PNG, GIF, BMP)
- Ensure proper file permissions

### CORS Issues
- CORS is enabled by default
- Modify `main.py` if custom headers needed

## 🔮 Future Enhancements

- [ ] Mobile app (React Native/Flutter)
- [ ] Weather-based disease alerts
- [ ] Multi-language support (Hindi, Spanish, etc.)
- [ ] Historical analysis tracking
- [ ] IoT sensor integration
- [ ] Advanced crop calendar
- [ ] Community disease reporting
- [ ] Export reports (PDF/CSV)

## 📚 Learning Resources

### For Viva/Academic Purpose

**One-Liner Definition:**
"Smart AgriCare is a web-based plant disease detection system that uses the Kindwise crop.health API to identify crop diseases from images and provides both chemical and organic pesticide recommendations with prevention measures."

**Key Points:**
1. Uses deep learning via Kindwise API for disease identification
2. Rule-based mapping system for pesticide recommendations
3. Industry-standard architecture: separate frontend, backend, database
4. RESTful API design
5. Scalable and maintainable code structure

## 📄 License

This project is created for educational and agricultural purposes.

## 📧 Support

For issues or questions:
1. Check the troubleshooting section
2. Review Kindwise API documentation
3. Check application logs

## 🌍 Real-World Impact

This system helps farmers:
- Identify crop diseases quickly
- Make informed pesticide choices
- Adopt sustainable farming practices
- Reduce crop loss
- Improve agricultural yield

---

**Version**: 1.0  
**Last Updated**: February 2024  
**Status**: Production Ready
