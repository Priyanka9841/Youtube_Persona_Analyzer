# YouTube Digital Mirror 🔮

Analyze your YouTube watch history and discover your algorithmic profile with this powerful tool. The application processes your YouTube Takeout data to reveal your viewing patterns, content preferences, and personalized recommendations.

## Features ✨

- **Personalized Analysis**: Discover your top content categories and viewing habits
- **Visual Insights**: Interactive charts showing your watch history distribution
- **Algorithm Profile**: See how YouTube's algorithm likely categorizes you
- **Recommendation Retraining**: Get suggestions to improve your recommendations
- **Privacy-Focused**: All processing happens locally - your data never leaves your device

## How It Works 🛠️

1. **Export Your Data**:
   - Visit [Google Takeout](https://takeout.google.com/)
   - Select only "YouTube and YouTube Music" data
   - Choose HTML format for watch history
   - Download the export (ZIP file)

2. **Upload & Analyze**:
   - Launch the application
   - Upload your Takeout ZIP file
   - View real-time processing status

3. **Explore Insights**:
   - Discover your content clusters
   - See your algorithm profile
   - Get personalized recommendations
   - Download full PDF report

## Installation & Setup ⚙️

### Prerequisites
- Python 3.8+
- pip package manager

### Installation Steps
1. Clone the repository:
```bash
git clone https://github.com/yourusername/youtube-digital-mirror.git
cd youtube-digital-mirror
```
2. Install dependencies:
```bash
pip install -r requirements.txt
```
3. Run the application:
```bash
    streamlit run app.py
```

## Project Structure 📂
youtube-digital-mirror/
├── backend/
│   ├── processing.py       # Data processing and analysis logic
│   └── __init__.py
├── frontend/
│   └── static/
│       └── styles.css      # Custom styles
├── app.py                  # Main Streamlit application
├── requirements.txt        # Python dependencies
└── README.md               # Project documentation



