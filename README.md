# 🌐 Website Cloning System

A sophisticated web application that leverages AI to clone and replicate public websites with high fidelity. Built as part of the Orchids SWE Internship challenge, this project demonstrates the power of combining modern web technologies with advanced AI capabilities.

## 🚀 Features

- **AI-Powered Website Cloning**: Utilizes Claude AI to analyze and replicate website designs
- **Real-time Preview**: Instant visualization of cloned websites
- **Modern UI/UX**: Clean, responsive interface with glass-morphism design
- **Recent Clones History**: Track and revisit previously cloned websites
- **Cross-Platform Compatibility**: Works seamlessly across different devices and browsers

## 🛠 Tech Stack

### Frontend
- Next.js 14
- TypeScript
- Tailwind CSS
- Modern UI components with glass effects
- Responsive design

### Backend
- FastAPI (v0.115.12)
- Python 3.11+
- Key Dependencies:
  - anthropic==0.52.2 (Claude AI API)
  - beautifulsoup4==4.13.4 (Web scraping)
  - fastapi==0.115.12 (API framework)
  - uvicorn==0.34.3 (ASGI server)
  - python-dotenv==1.1.0 (Environment management)
  - requests==2.32.3 (HTTP client)
  - pydantic==2.11.5 (Data validation)

## 📋 Prerequisites

Before you begin, ensure you have the following installed:
- Node.js (v18 or higher)
- Python (v3.11 or higher)
- Git
- A modern web browser
- Claude AI API key

## 🚀 Getting Started

### 1. Clone the Repository
```bash
git clone [repository-url]
cd orchid_challenge
```

### 2. Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install all required dependencies from requirements.txt
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your Claude API key

# Start the backend server
uvicorn app.main:app --reload
```

The backend will be available at `http://localhost:8000`

### 3. Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Set up environment variables
cp .env.example .env
# Edit .env with your backend URL

# Start the development server
npm run dev
```

The frontend will be available at `http://localhost:3000`

## 🔧 Configuration

### Environment Variables

#### Backend (.env)
```
CLAUDE_API_KEY=your_api_key_here
ALLOWED_ORIGINS=http://localhost:3000
```

#### Frontend (.env)
```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## 📝 Usage

1. Open the application in your browser
2. Enter a public website URL in the input field
3. Click "Clone Website" to start the process
4. Wait for the AI to analyze and generate the clone
5. View the cloned website in the preview window
6. Access your recent clones from the history section

## 🧪 Testing

### Backend Tests
```bash
cd backend
pytest
```

### Frontend Tests
```bash
cd frontend
npm test
```


## 🙏 Acknowledgments

- Claude AI for providing the LLM capabilities
- Next.js team for the amazing framework
- FastAPI for the robust backend framework
- All contributors and supporters of the project

## 📞 Support

For support, please open an issue in the GitHub repository or contact the maintainers.

## 🔮 Future Improvements

- Enhanced JavaScript functionality cloning
- Better asset optimization
- Advanced caching mechanisms
- CDN integration
- User authentication system
- Custom styling options
- Batch processing capabilities

---

Made with ❤️ for the Orchids SWE Internship Challenge
