# 🚀 Quick Start Guide - Smart AgriCare

## Step 1: Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

## Step 2: Verify API Key

Check that your Kindwise API key is in the `.env` file:

```bash
cat .env
```

You should see:
```
KINDWISE_API_KEY=lXzkiXjZmwnsQT1mfgojRgrzdn3Ck8JNhYDb94fAVvWKqaty44
FLASK_ENV=development
FLASK_DEBUG=True
```

## Step 3: Start the Application

```bash
python main.py
```

You should see:
```
============================================================
Smart AgriCare - Plant Disease Detection System
============================================================
API Key Configured: ✓
Pesticide Database Loaded: ✓
============================================================
Starting server on http://localhost:5000
============================================================
```

## Step 4: Open in Browser

Visit: **http://localhost:5000**

## Step 5: Use the Application

1. Click **"Choose Image"** to upload a leaf/fruit photo
2. Click **"Analyze Image"** to process
3. Wait for results (usually 5-10 seconds)
4. View:
   - Crop type detected
   - Disease identified
   - Chemical pesticides recommended
   - Organic treatments suggested
   - Prevention measures
5. Click **"← New Analysis"** to analyze another image

## 📸 Test Images

For testing, use images of:
- Diseased tomato leaves (early/late blight, spots)
- Cucumber/grape leaves with powdery mildew (white coating)
- Any plant with visible disease symptoms

## 🔧 Troubleshooting

### Port 5000 Already in Use

**macOS/Linux:**
```bash
lsof -ti:5000 | xargs kill -9
python main.py
```

**Windows:**
```bash
netstat -ano | findstr :5000
taskkill /PID <PID> /F
python main.py
```

### API Not Responding

1. Check internet connection
2. Verify API key in `.env`
3. Check Kindwise API status

### File Upload Issues

- Image must be under 10 MB
- Supported formats: JPG, PNG, GIF, BMP
- Ensure good image quality

## 📊 API Response Example

```json
{
  "success": true,
  "crop": "Tomato",
  "disease": "Early Blight",
  "confidence": "85.3%",
  "analysis": {
    "symptoms": "Brown spots with concentric rings on leaves...",
    "chemical_pesticides": [
      "Chlorothalonil (Bravo 750)",
      "Mancozeb (Dithane M-45)"
    ],
    "organic_treatments": [
      "Neem oil spray",
      "Sulfur dust"
    ],
    "prevention": [
      "Remove affected leaves immediately",
      "Improve air circulation"
    ]
  }
}
```

## 🛑 Stop the Application

Press `Ctrl + C` in the terminal

---

**Happy Farming! 🌾**
