# PPT Generator - AI-Powered Presentation Builder

A complete multi-agent AI-based presentation generator system using CrewAI and Gemini API. Transform your ideas into beautiful presentations with the power of specialized AI agents.

## 🚀 Features

- **Multi-Agent AI System**: Three specialized agents work together to create your presentation
  - **Planner Agent**: Analyzes requirements and creates presentation blueprint
  - **Content Creator**: Generates engaging content for each slide
  - **Designer Agent**: Creates visually appealing slide designs
- **Real-time Progress Tracking**: WebSocket-based live updates during generation
- **Professional UI**: Modern React frontend with dark theme and smooth animations
- **PowerPoint Export**: Generates actual .pptx files ready for use
- **Customizable**: Specify number of slides (1-20) and detailed requirements

## 🏗️ System Architecture

### Backend (Flask + CrewAI)
- **Flask API**: RESTful endpoints for presentation management
- **WebSocket Support**: Real-time communication with frontend
- **CrewAI Integration**: Orchestrates multiple AI agents
- **Gemini API**: Powered by Google's Gemini 2.0 Flash model
- **PowerPoint Generation**: Creates actual .pptx files using python-pptx

### Frontend (React)
- **Modern UI**: Built with React, Tailwind CSS, and custom components
- **Real-time Updates**: Live progress tracking and logs
- **Responsive Design**: Works on desktop and mobile devices
- **Professional Styling**: Dark theme with gradient colors and animations

## 📋 Prerequisites

- Python 3.11+
- Node.js 20+
- Gemini API Key from Google AI Studio

## 🛠️ Installation & Setup

### 1. Extract the Project
```bash
# Extract the provided ZIP file
unzip ppt_generator_complete.tar.gz
cd ppt_generator
```

### 2. Backend Setup
```bash
cd backend

# Install Python dependencies
pip3 install -r requirements.txt

# Configure environment variables
# Edit .env file and add your Gemini API key:
# GEMINI_API_KEY=your_gemini_api_key_here

# Start the backend server (recommended for stable operation)
python3 start_server.py

# Alternative (may have auto-reload interruptions):
# python3 app.py
```

The backend will start on `http://localhost:5000`

**Note**: Use `start_server.py` for stable operation during long-running presentation generation tasks. This prevents Flask's auto-reload from interrupting the retry mechanism when the API is overloaded.

### 3. Frontend Setup
```bash
cd frontend/ppt-generator-ui

# Install dependencies
pnpm install

# Start the development server
pnpm run dev --host
```

The frontend will start on `http://localhost:5173`

## 🎯 Usage

1. **Open the Application**: Navigate to `http://localhost:5173`
2. **Enter Description**: Describe the presentation you want to create
3. **Set Slide Count**: Choose number of slides (1-20)
4. **Generate**: Click "Generate Presentation" and watch the AI agents work
5. **Download**: Once complete, download your .pptx file

### Example Prompts
- "Create a presentation about artificial intelligence and its impact on modern business"
- "Make a presentation on climate change solutions for corporate sustainability"
- "Generate slides about digital marketing strategies for small businesses"

## 🔧 Configuration

### Environment Variables (.env)
```
GEMINI_API_KEY=your_gemini_api_key_here
SECRET_KEY=your_secret_key_here
FLASK_ENV=development
FLASK_DEBUG=True
```

### API Configuration (config.py)
- `MAX_SLIDES`: Maximum slides allowed (default: 20)
- `DEFAULT_SLIDES`: Default slide count (default: 5)
- `AGENT_TIMEOUT`: Timeout for each agent (default: 300 seconds)

## 📡 API Endpoints

### REST API
- `POST /api/generate` - Start presentation generation
- `GET /api/projects/{id}/status` - Get project status
- `GET /api/projects/{id}/download` - Download presentation
- `GET /api/projects` - List all projects
- `DELETE /api/projects/{id}` - Delete project

### WebSocket Events
- `connect` - Client connection
- `join_project` - Join project room for updates
- `progress_update` - Real-time progress updates
- `project_completed` - Generation completed
- `project_failed` - Generation failed

## 🤖 AI Agents

### Planner Agent
- **Role**: Presentation Strategist
- **Responsibility**: Analyzes user requirements and creates detailed presentation blueprint
- **Output**: Structured JSON with slide titles, descriptions, and content types

### Content Creator Agent
- **Role**: Content Writer and Researcher
- **Responsibility**: Generates actual textual content for each slide
- **Output**: Enhanced JSON with complete content, bullet points, and speaker notes

### Designer Agent
- **Role**: Presentation Designer
- **Responsibility**: Defines visual styling, layouts, and design specifications
- **Output**: Complete JSON with design specifications and styling instructions

## 🎨 Customization

### Styling
- Modify `frontend/ppt-generator-ui/src/App.css` for custom themes
- Update color schemes in the CSS variables
- Customize component styles using Tailwind classes

### Agent Behavior
- Edit `backend/agents.py` to modify agent prompts and behavior
- Adjust agent roles and backstories for different output styles
- Customize the CrewAI workflow in `backend/project_manager.py`

### PowerPoint Templates
- Modify `backend/project_manager.py` to change slide layouts
- Update color schemes and fonts in the `_create_powerpoint` method
- Add custom slide templates and styling

## 🚀 Deployment

### Backend Deployment
```bash
# Install production dependencies
pip3 install gunicorn

# Run with Gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### Frontend Deployment
```bash
# Build for production
pnpm run build

# Serve static files
# Deploy the dist/ folder to your web server
```

## 🔍 Troubleshooting

### Common Issues

1. **Gemini API Key Error**
   - Ensure your API key is correctly set in `.env`
   - Verify the key has proper permissions

2. **Frontend Connection Issues**
   - Check if backend is running on port 5000
   - Verify CORS settings in Flask app

3. **PowerPoint Generation Fails**
   - Check if all Python dependencies are installed
   - Verify write permissions in `generated_ppts` directory

4. **WebSocket Connection Issues**
   - Ensure both frontend and backend are running
   - Check firewall settings for ports 5000 and 5173

5. **API Overload Errors (503 Service Unavailable)**
   - This is a temporary issue with Google's Gemini API being overloaded
   - The system will automatically retry with exponential backoff
   - **Important**: Use the stable startup method to prevent interruptions:
   
   ```bash
   # Instead of: python app.py
   # Use the stable startup script:
   cd backend
   python start_server.py
   ```
   
   This disables Flask's auto-reload feature which was interrupting retry attempts.

6. **Presentation Generation Interrupted**
   - If the server restarts during generation, the retry mechanism is interrupted
   - Always use `python start_server.py` instead of `python app.py`
   - Set `FLASK_USE_RELOADER=False` in your `.env` file
   - The system now persists project state and can recover from interruptions

## 📝 File Structure

```
ppt_generator/
├── backend/
│   ├── agents.py              # CrewAI agents definition
│   ├── app.py                 # Flask application
│   ├── config.py              # Configuration settings
│   ├── project_manager.py     # Main orchestration logic
│   ├── requirements.txt       # Python dependencies
│   ├── .env                   # Environment variables
│   ├── generated_ppts/        # Generated presentations
│   └── temp/                  # Temporary files
├── frontend/
│   └── ppt-generator-ui/      # React application
│       ├── src/
│       │   ├── App.jsx        # Main React component
│       │   ├── App.css        # Styling
│       │   └── components/    # UI components
│       ├── package.json       # Node dependencies
│       └── public/            # Static assets
├── README.md                  # This file
└── todo.md                    # Development progress
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

For support and questions:
- Check the troubleshooting section above
- Review the configuration options
- Ensure all dependencies are properly installed

## 🔮 Future Enhancements

- Support for more presentation formats (PDF, Google Slides)
- Additional AI models integration
- Custom template library
- Collaborative editing features
- Advanced styling options
- Image generation integration
- Voice narration support

---

**Built with ❤️ using CrewAI, Gemini API, React, and Flask**

