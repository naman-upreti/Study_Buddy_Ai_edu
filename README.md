# 📚 Study Buddy AI - AI-Powered Interactive Quiz Platform

An intelligent Streamlit-based web application that generates educational questions using AI-powered LLMs (Groq) and supports document-based question generation with comprehensive analytics.

---

## 🎯 Project Overview

**Study Buddy AI** is an interactive quiz platform designed to help students learn effectively through AI-generated questions. It leverages:

- **LangChain + Groq LLM** for intelligent question generation
- **Retrieval-Augmented Generation (RAG)** for document-based questions
- **Streamlit** for interactive web interface
- **Analytics Dashboard** for learning insights
- **Docker & Kubernetes** for cloud-native deployment

### Key Features

1. **Quiz Generation**
   - Generate MCQ or Fill-in-the-Blank questions
   - Support for 3 difficulty levels (Easy, Medium, Hard)
   - Batch question generation with exponential backoff retry logic
   - Pydantic validation for consistent output

2. **Document-Based Q&A (RAG)**
   - Upload PDF, DOCX, or TXT files (50MB max)
   - Automatic text extraction and chunking
   - Semantic search using embeddings
   - Generate questions from document content

3. **Analytics Dashboard**
   - Track quiz attempts with accuracy metrics
   - Topic-wise and difficulty-wise performance
   - Identify strong/weak areas
   - Recent attempts history with time tracking
   - Progress visualization

4. **Result Management**
   - Automatic answer evaluation
   - Case-insensitive matching for fill-blank questions
   - Detailed answer review with explanations
   - CSV export of results
   - Performance persistence

---

## 📋 Requirements

### System Requirements

- **OS**: Linux, macOS, or Windows
- **Python**: 3.10 or higher
- **RAM**: Minimum 2GB (4GB recommended)
- **Disk Space**: 500MB for application and dependencies

### Software Dependencies

- **Python Packages**:
  - `langchain` - LangChain framework
  - `langchain-groq` - Groq API integration
  - `langchain-core` - Core LangChain utilities
  - `streamlit` - Web UI framework
  - `pandas` - Data manipulation
  - `pydantic` - Data validation
  - `PyPDF2` - PDF text extraction
  - `python-docx` - DOCX text extraction
  - `python-dotenv` - Environment variable management
  - `numpy` - Vector math operations

### External Services

- **Groq API Key** - Required for LLM question generation
  - Sign up at [console.groq.com](https://console.groq.com)
  - Model: `llama-3.1-8b-instant`
  - Free tier available

### Deployment Requirements

- **Docker**: For containerization
- **Kubernetes**: For orchestration (optional)
- **Docker Hub Account**: For image registry (for CI/CD)
- **GitHub Account**: For version control and CI/CD

---

## 🚀 Quick Start

### 1. Installation

```bash
# Clone the repository
git clone https://github.com/naman-upreti/Study_Buddy_Ai_edu.git
cd Study_Buddy_Ai_edu

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -e .
```

### 2. Environment Setup

Create a `.env` file in the project root:

```bash
GROQ_API_KEY=your_groq_api_key_here
```

### 3. Run Application

```bash
streamlit run application.py
```

The application will be available at `http://localhost:8501`

### 4. Docker Deployment

```bash
# Build Docker image
docker build -t naman/studybuddy:v1 .

# Run Docker container
docker run -p 8501:8501 \
  -e GROQ_API_KEY=your_groq_api_key \
  naman/studybuddy:v1
```

### 5. Kubernetes Deployment

```bash
# Apply Kubernetes manifests
kubectl apply -f manifests/

# Check deployment status
kubectl get pods
kubectl get svc
```

---

## 📁 Project Structure

```
STUDY-BUDDY-AI-main/
├── src/
│   ├── analytics/
│   │   └── performance_tracker.py    # Quiz analytics & tracking
│   ├── common/
│   │   ├── custom_exception.py       # Custom error handling
│   │   └── logger.py                 # Logging configuration
│   ├── config/
│   │   └── settings.py               # App configuration
│   ├── generator/
│   │   └── question_generator.py     # Question generation logic
│   ├── llm/
│   │   └── groq_client.py            # Groq API integration
│   ├── models/
│   │   └── question_schemas.py       # Pydantic data models
│   ├── prompts/
│   │   └── templates.py              # LLM prompt templates
│   ├── rag/
│   │   ├── document_processor.py     # Document extraction
│   │   ├── retriever.py              # Semantic search
│   │   └── rag_question_generator.py # Document-based Q generation
│   └── utils/
│       └── helpers.py                # Quiz manager utilities
├── manifests/
│   ├── deployment.yaml               # Kubernetes deployment
│   └── service.yaml                  # Kubernetes service
├── application.py                    # Streamlit main app
├── Dockerfile                        # Docker configuration
├── Jenkinsfile                       # CI/CD pipeline
├── requirements.txt                  # Python dependencies
├── setup.py                          # Package installation
├── styles.css                        # Custom CSS styling
└── README.md                         # This file
```

---

## 🔧 Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `GROQ_API_KEY` | Groq API authentication key | Yes |

### Application Settings

Edit `src/config/settings.py`:

```python
MODEL_NAME = "llama-3.1-8b-instant"  # LLM model
TEMPERATURE = 0.9                     # Creativity level (0.0-1.0)
MAX_RETRIES = 3                       # Retry attempts
```

### Document Processing

- **Max File Size**: 50MB
- **Supported Formats**: TXT, PDF, DOCX
- **Chunk Size**: 1000 characters
- **Chunk Overlap**: 200 characters

---

## 📊 API & Usage

### QuestionGenerator

```python
from src.generator.question_generator import QuestionGenerator

generator = QuestionGenerator()

# Generate single MCQ
mcq = generator.generate_mcq(topic="Python", difficulty="medium")

# Generate single Fill-in-the-Blank
fib = generator.generate_fill_blank(topic="Data Science", difficulty="easy")

# Generate batch
questions = generator.generate_batch(
    topic="Machine Learning",
    count=5,
    question_type='mcq',
    difficulty='hard'
)
```

### RAGQuestionGenerator

```python
from src.rag.rag_question_generator import RAGQuestionGenerator

rag_gen = RAGQuestionGenerator()

# Load document
text = rag_gen.load_document(uploaded_file)

# Generate from document
question = rag_gen.generate_rag_mcq(
    query="What is supervised learning?",
    difficulty="medium"
)
```

### PerformanceTracker

```python
from src.analytics.performance_tracker import PerformanceTracker

tracker = PerformanceTracker()

# Record attempt
attempt = tracker.record_attempt(
    topic="Python",
    question_type="MCQ",
    difficulty="medium",
    total_questions=5,
    correct_answers=4,
    time_taken=120.5,
    questions_data=[]
)

# Get statistics
stats = tracker.get_overall_stats()
weak_areas = tracker.get_weak_areas()
strong_areas = tracker.get_strong_areas()
```

---

## 🔄 CI/CD Pipeline

The project uses Jenkins for CI/CD with the following stages:

1. **Checkout** - Clone from GitHub
2. **Build** - Build Docker image
3. **Push** - Push to Docker Hub
4. **Update YAML** - Update deployment manifest
5. **Commit** - Commit changes to GitHub
6. **Deploy** - Apply Kubernetes manifests
7. **Sync** - Sync with ArgoCD

### GitHub Integration

- Repository: `https://github.com/naman-upreti/Study_Buddy_Ai_edu`
- Branch: `main`
- Webhook triggers on push events

---

## 🧪 Testing

Run the application locally for testing:

```bash
# Development mode with hot reload
streamlit run application.py --logger.level=debug

# Test quiz generation
python -c "
from src.generator.question_generator import QuestionGenerator
gen = QuestionGenerator()
q = gen.generate_mcq('Python', 'easy')
print(q)
"
```

---

## 📝 Data Storage

- **Quiz Results**: `results/` directory (CSV files)
- **Performance Data**: `quiz_performance.json`
- **Logs**: `logs/` directory (daily log files)

---

## 🐛 Error Handling

The application includes comprehensive error handling:

- **CustomException**: Wraps all errors with file/line information
- **Logging**: Daily logs stored in `logs/` directory
- **Validation**: Pydantic models validate all data
- **Retry Logic**: Exponential backoff for API failures

---

## 🔒 Security Notes

- Never commit `.env` file with API keys
- Use GitHub secrets for sensitive data in CI/CD
- Groq API key should be treated as confidential
- Docker Hub credentials stored in Jenkins secrets

---

## 📈 Performance Optimizations

- Multi-stage Docker build (smaller images)
- Layer caching in Dockerfile
- Exponential backoff retry logic
- Batch question generation
- Semantic search with chunking
- Session state management in Streamlit

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Commit with clear messages
5. Push to your fork
6. Create a Pull Request

---

## 📄 License

This project is part of the Study Buddy AI educational initiative.

---

## 👨‍💻 Author

**Naman Upreti**
- GitHub: [@naman-upreti](https://github.com/naman-upreti)
- Repository: [Study_Buddy_Ai_edu](https://github.com/naman-upreti/Study_Buddy_Ai_edu)

---

## 📞 Support

For issues, feature requests, or questions:
1. Check existing issues on GitHub
2. Create a new issue with detailed description
3. Include error logs and steps to reproduce

---

## 🎓 Learning Resources

- [Streamlit Documentation](https://docs.streamlit.io)
- [LangChain Documentation](https://docs.langchain.com)
- [Groq API Documentation](https://console.groq.com/docs)
- [Kubernetes Documentation](https://kubernetes.io/docs)
- [Docker Documentation](https://docs.docker.com)

---

**Happy Learning! 🚀**
