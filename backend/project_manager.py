import os
import json
from datetime import datetime
from agents import PPTCrew
from config import Config
import logging
from themes import ThemeConfig, PPTThemes
from flask import render_template_string

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# HTML template for presentations (copied from app.py)
PRESENTATION_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ presentation.title }}</title>
    <style>
        {{ theme_css | safe }}

        body {
            font-family: var(--font-body, Arial, sans-serif);
            margin: 0;
            padding: 0;
        }

        .slide {
            width: 100%;
            height: 100%;
            box-sizing: border-box;
            padding: 40px;
            page-break-after: always;
            display: flex;
            flex-direction: column;
            justify-content: center;
        }

        .slide h1, .slide h2, .slide h3 {
            font-family: var(--font-heading, Arial, sans-serif);
            margin-bottom: 20px;
        }

        .slide-body {
            margin-top: 20px;
        }

        .slide-body p {
            margin-bottom: 10px;
            line-height: 1.5;
        }

        .slide-body ul {
            padding-left: 20px;
            margin: 10px 0;
        }

        .slide-body blockquote {
            border-left: 4px solid #ccc;
            padding-left: 15px;
            color: #555;
            margin: 20px 0;
        }

        .grid {
            display: flex;
            gap: 20px;
        }
        .grid-item {
            flex: 1;
            border: 1px solid #ddd;
            padding: 10px;
            border-radius: 6px;
        }

        /* Ensure last slide doesn’t force an extra blank page */
        .slide:last-child {
            page-break-after: auto;
        }
    </style>
</head>
<body class="theme-{{ presentation.theme }}">
    {% for slide in presentation.slides %}
    <div class="slide"
         data-slide-type="{{ slide.type }}"
         data-layout="{{ slide.layout }}"
         {% if slide.background %}
         style="background-color: {{ slide.background.value if slide.background.type == 'solid' else '' }};
                background-image: url('{{ slide.background.value if slide.background.type == 'image' else '' }}');"
         {% endif %}
    >
        <div class="slide-content">
            {% if slide.title %}
            <h2>{{ slide.title }}</h2>
            {% endif %}

            {% if slide.subtitle %}
            <h3>{{ slide.subtitle }}</h3>
            {% endif %}

            {% if slide.content %}
            <div class="slide-body">
                {% for content_item in slide.content %}
                    {% if content_item.type == 'text' %}
                        <p>{{ content_item.value }}</p>
                    {% elif content_item.type == 'image' %}
                        <img src="{{ content_item.value }}" alt="" style="max-width: 100%; height: auto;">
                    {% elif content_item.type == 'bullet_points' or content_item.type == 'list' %}
                        <ul>
                        {% for point in content_item.value %}
                            <li>{{ point }}</li>
                        {% endfor %}
                        </ul>
                    {% elif content_item.type == 'quote' %}
                        <blockquote>
                            <p>{{ content_item.value.text }}</p>
                            {% if content_item.value.author %}
                            <footer>— {{ content_item.value.author }}</footer>
                            {% endif %}
                        </blockquote>
                    {% elif content_item.type == 'grid' %}
                        <div class="grid">
                            {% for item in content_item.value %}
                            <div class="grid-item">
                                {% if item.icon %}
                                <div class="icon">{{ item.icon }}</div>
                                {% endif %}
                                <h4>{{ item.title }}</h4>
                                <p>{{ item.content }}</p>
                            </div>
                            {% endfor %}
                        </div>
                    {% endif %}
                {% endfor %}
            </div>
            {% endif %}
        </div>
    </div>
    {% endfor %}
</body>
</html>
"""

class PPTProjectManager:

    @staticmethod
    def clean_html_code_block(content: str) -> str:
        """
        Removes leading ```html and trailing ``` from a string, returning the cleaned HTML content.
        """
        if not isinstance(content, str):
            return content
        content = content.strip()
        if content.startswith('```html'):
            content = content[len('```html'):]
        elif content.startswith('```'):
            content = content[len('```'):]
        if content.endswith('```'):
            content = content[:-3]
        return content.strip()

    def __init__(self, socketio=None):
        self.socketio = socketio
        self.crew = PPTCrew()
        self.projects = {}
        self.state_file = os.path.join(Config.TEMP_DIR, 'project_states.json')
        os.makedirs(Config.GENERATED_PPTS_DIR, exist_ok=True)
        os.makedirs(Config.TEMP_DIR, exist_ok=True)
        self._load_project_states()
        
    def get_pdf_path(self, project_id: str) -> str:
        """Get the path where the PDF file should be saved"""
        return os.path.join(Config.GENERATED_PPTS_DIR, f"presentation_{project_id}.pdf")

    def _load_project_states(self):
        try:
            if os.path.exists(self.state_file):
                with open(self.state_file, 'r') as f:
                    self.projects = json.load(f)
                logger.info(f"Loaded {len(self.projects)} project states from disk")
        except Exception as e:
            logger.warning(f"Failed to load project states: {e}")
            self.projects = {}

    def emit_progress(self, project_id, stage, message, type='info'):
        if self.socketio:
            data = {'stage': stage, 'message': message, 'type': type, 'timestamp': datetime.now().isoformat()}
            self.socketio.emit('status_update', data, room=project_id)
            if project_id in self.projects:
                self.projects[project_id]['stages'].append(data)

    @staticmethod
    def _log_agent_response(project_id: str, agent_name: str, response: str):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Check if the response contains HTML code blocks
        if "```html" in response or "<!DOCTYPE html" in response or "<html" in response:
            # Save HTML content to .html files
            html_dir = os.path.join(Config.TEMP_DIR, "html_outputs")
            os.makedirs(html_dir, exist_ok=True)
            
            # Split response into separate HTML code blocks
            slides = []
            if "```html" in response:
                # Split by ```html and ``` markers
                parts = response.split("```html")
                for part in parts[1:]:  # Skip first part (before first ```html)
                    end = part.find("```")
                    if end != -1:
                        slides.append(part[:end].strip())
            else:
                # Single HTML content
                slides = [response.strip()]
            
            html_files = []
            for i, slide_content in enumerate(slides, 1):
                html_file = os.path.join(html_dir, f"{timestamp}_slide{i}.html")
                with open(html_file, 'w', encoding='utf-8') as f:
                    f.write(slide_content)
                html_files.append(html_file)
            logger.info(f"Saved HTML output to {html_file}")
        else:
            # Save non-HTML responses to log file
            log_dir = Config.TEMP_DIR
            os.makedirs(log_dir, exist_ok=True)
            file_name = f"agent_response_{project_id}_{timestamp}.log"
            file_path = os.path.join(log_dir, file_name)
            
            with open(file_path, 'a') as f:
                f.write(f"[{datetime.now().isoformat()}] Agent: {agent_name}\n")
                f.write(f"Response:\n{response}\n\n")
            logger.info(f"Logged agent response to {file_path}")

    def generate_presentation(self, user_prompt, num_slides=5, project_id=None, theme_name='corporate_blue'):
        if not project_id:
            project_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        try:
            self.projects[project_id] = {
                'id': project_id, 'prompt': user_prompt, 'num_slides': num_slides,
                'theme_name': theme_name, 'status': 'started',
                'created_at': datetime.now().isoformat(), 'stages': []
            }
            
            self.emit_progress(project_id, 'initialization', 'Starting presentation generation...')
            
            self.emit_progress(project_id, 'planning', 'AI agents are working on your presentation...')
            
            # Create presentation with the required arguments
            style_prefs = {
                'num_slides': num_slides,
                'project_id': project_id,
                'theme': theme_name
            }
            presentation_plan = self.crew.create_presentation(
                topic=user_prompt,
                style_preferences=style_prefs
            )
            
            PPTProjectManager._log_agent_response(project_id, "Presentation Generator", str(presentation_plan))
            self.emit_progress(project_id, 'generation', 'AI generation complete, processing results...')

            theme = PPTThemes.get_theme(theme_name)
            if not theme:
                logger.warning(f"Theme '{theme_name}' not found, using default corporate_blue")
                theme = PPTThemes.get_theme('corporate_blue')
            
            logger.info(f"Using theme: {theme.display_name}")
            
            logger.info(f"Received presentation_plan type: {type(presentation_plan)}")
            logger.info(f"Presentation plan raw data: {str(presentation_plan)[:500]}")
            
            raw_result = self._extract_crew_result(presentation_plan)
            logger.info(f"Raw result type after extraction: {type(raw_result)}")
            logger.info(f"Raw result content: {str(raw_result)[:500]}")
            
            def clean_html_code_block(content: str) -> str:
                """
                Removes leading ```html and trailing ``` from a string, returning the cleaned HTML content.
                """
                if not isinstance(content, str):
                    return content
                content = content.strip()
                if content.startswith('```html'):
                    content = content[len('```html'):]
                elif content.startswith('```'):
                    content = content[len('```'):]
                if content.endswith('```'):
                    content = content[:-3]
                return content.strip()

            if isinstance(raw_result, str):
                # First try to clean HTML code block format
                if "```html" in raw_result or raw_result.strip().startswith("```"):
                    raw_result = PPTProjectManager.clean_html_code_block(raw_result)
                    logger.info("Cleaned HTML code block formatting")
                    # If it's HTML, we can process it directly
                    if raw_result.strip().startswith("<!DOCTYPE html") or raw_result.strip().startswith("<html"):
                        logger.info("Found valid HTML content")
                        html_content = raw_result
                        
                        # Store the cleaned HTML response for debugging
                        debug_dir = os.path.join(Config.TEMP_DIR, "debug_html")
                        os.makedirs(debug_dir, exist_ok=True)
                        html_file_path = os.path.join(debug_dir, f"presentation_{project_id}_cleaned.html")
                        
                        with open(html_file_path, 'w', encoding='utf-8') as f:
                            f.write(html_content)
                        logger.info(f"Stored cleaned HTML content in: {html_file_path}")
                        
                        self.emit_progress(project_id, 'processing', 'Processing HTML content...')
                        self.projects[project_id]['html_path'] = html_file_path  # Store the path in project data
                        return self._generate_pdf_from_html(project_id, html_content)
                
                # If not HTML, try to find JSON structure
                json_start = raw_result.find('{')
                json_end = raw_result.rfind('}')
                if json_start != -1 and json_end != -1:
                    potential_json = raw_result[json_start:json_end + 1]
                    logger.info(f"Found potential JSON: {potential_json[:200]}...")
                    try:
                        json.loads(potential_json)
                        raw_result = potential_json
                        logger.info("Successfully extracted JSON structure")
                    except json.JSONDecodeError as e:
                        logger.warning(f"Found JSON-like structure but failed to parse: {e}")
                
                cleaned_result = self._clean_json_content(raw_result)
                logger.info(f"Cleaned result: {cleaned_result[:500]}")
                
                try:
                    plan_data = json.loads(cleaned_result)
                except json.JSONDecodeError as json_err:
                    logger.warning(f"CrewOutput result is not valid JSON: {json_err}")
                    
                    plan_data = {}
            elif isinstance(raw_result, dict):
                plan_data = raw_result
            else:
                logger.warning(f"Unknown CrewOutput format: {type(raw_result)}, using empty plan")
                logger.debug(f"Raw result content: {str(raw_result)[:200]}...")
                plan_data = {}
            
            self._validate_plan_data(plan_data)
            # PPTProjectManager._log_agent_response(project_id, "Planner Agent", json.dumps(plan_data, indent=2))
            
            self.emit_progress(project_id, 'packaging', 'Creating presentation assets...')
            pdf_path = self._create_html_presentation(plan_data, project_id, theme)
            
            self.emit_progress(project_id, 'pdf_generation', 'PDF generated successfully.')

            self.emit_progress(project_id, 'finalization', 'Finalizing your presentation...')
            
            self.projects[project_id].update({
                'status': 'completed', 'plan': plan_data,
                'pdf_path': pdf_path,
                'completed_at': datetime.now().isoformat()
            })
            
            self.emit_progress(project_id, 'completed', 'Presentation generated successfully!')
            
            if self.socketio:
                self.socketio.emit('project_completed', {
                    'project_id': project_id,
                    'result': {'success': True, 'file_path': pdf_path, 'pdf_path': pdf_path}
                }, room=project_id)
            
            return {'success': True, 'project_id': project_id, 'file_path': pdf_path, 'pdf_path': pdf_path}
            
        except Exception as e:
            error_str = str(e)
            logger.error(f"Error generating presentation: {error_str}", exc_info=True)
            user_message = f"An error occurred during generation: {error_str}"
            self.emit_progress(project_id, 'failed', user_message)
            self.projects[project_id]['status'] = 'failed'
            self.projects[project_id]['error'] = error_str
            
            if self.socketio:
                self.socketio.emit('project_failed', {'project_id': project_id, 'error': error_str}, room=project_id)
            
            return {'success': False, 'project_id': project_id, 'error': error_str}

    def _extract_crew_result(self, crew_output):
        logger.info(f"CrewOutput type: {type(crew_output)}")
        available_attrs = [attr for attr in dir(crew_output) if not attr.startswith('_')]
        logger.info(f"CrewOutput public attributes: {available_attrs}")
        extraction_methods = [
            ('raw', lambda x: x.raw), ('result', lambda x: x.result),
            ('output', lambda x: x.output), ('text', lambda x: x.text),
            ('content', lambda x: x.content), ('str', lambda x: str(x))
        ]
        for method_name, method_func in extraction_methods:
            try:
                if method_name == 'str' or hasattr(crew_output, method_name.replace('str', '__str__')):
                    result = method_func(crew_output)
                    logger.info(f"Successfully extracted using method: {method_name}")
                    return result
            except Exception as e:
                logger.warning(f"Method {method_name} failed: {e}")
        logger.warning("All extraction methods failed, returning string representation")
        return str(crew_output)

    def _clean_json_content(self, content):
        if not isinstance(content, str):
            return content
            
        content = content.strip()
        
        # Handle various markdown code block formats
        code_block_starts = ['```json', '```html', '```javascript', '```js', '```']
        for start in code_block_starts:
            if content.startswith(start):
                content = content[len(start):]
                break
                
        # Remove ending code block markers
        if content.endswith('```'):
            content = content[:-3]
            
        # Clean the content and try to find JSON content
        content = content.strip()
        
        return content

    def _validate_plan_data(self, plan_data):
        if not isinstance(plan_data, dict):
            return False
        for key in ['presentation_title', 'presentation_description', 'slides']:
            if key not in plan_data:
                plan_data[key] = [] if key == 'slides' else 'Generated'
        if not isinstance(plan_data.get('slides'), list):
            plan_data['slides'] = []
        for i, slide in enumerate(plan_data['slides']):
            if not isinstance(slide, dict):
                plan_data['slides'][i] = {'title': f'Slide {i + 1}', 'content': 'Generated content'}
        return True

    def _create_html_presentation(self, plan_data: dict, project_id: str, theme: ThemeConfig) -> str:
        """Process and combine separate HTML slides into a PDF presentation"""
        logger.info(f"Processing HTML slides for theme: {theme.display_name}")
        
        html_dir = os.path.join(Config.TEMP_DIR, "html_outputs")
        
        # Get the latest set of slides based on timestamp
        slide_files = sorted([f for f in os.listdir(html_dir) if f.endswith('.html')])
        if not slide_files:
            logger.error("No HTML slides found. Falling back to old template method.")
            return self._create_html_presentation_fallback(plan_data, project_id, theme)
        
        # Get the latest timestamp
        latest_timestamp = slide_files[-1].split('_')[0]
        slide_files = sorted([f for f in slide_files if f.startswith(latest_timestamp)])
        
        logger.info(f"Processing {len(slide_files)} slides from timestamp {latest_timestamp}")
        
        # Read and process each slide
        combined_slides = []
        for slide_file in slide_files:
            with open(os.path.join(html_dir, slide_file), 'r', encoding='utf-8') as f:
                slide_content = f.read().strip()
                # Extract body content from each slide
                body_start = slide_content.find('<body')
                body_end = slide_content.find('</body>')
                if body_start != -1 and body_end != -1:
                    body_content = slide_content[body_start:body_end + 7]
                    combined_slides.append(body_content)
                else:
                    combined_slides.append(f'<div class="slide">{slide_content}</div>')

        # Create a complete HTML document with all slides
        html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Presentation - {plan_data.get('presentation_title', 'Generated Presentation')}</title>
    <style>
        {theme.get_css()}
        @page {{ size: 1920px 1080px; margin: 0; }}
        body {{ 
            margin: 0; 
            padding: 0;
            background-color: {theme.color_scheme.background_start};
        }}
        .slide {{ 
            width: 1920px; 
            height: 1080px; 
            margin: 0; 
            padding: 40px; 
            box-sizing: border-box;
            page-break-after: always;
            display: flex;
            flex-direction: column;
            justify-content: center;
            background-color: {theme.color_scheme.background_start};
            color: {theme.color_scheme.text};
        }}
    </style>
</head>
<body>
    {''.join(combined_slides)}
</body>
</html>"""

        # Store the HTML for debugging
        debug_dir = os.path.join(Config.TEMP_DIR, "debug_html")
        os.makedirs(debug_dir, exist_ok=True)
        html_path = os.path.join(debug_dir, f"presentation_{project_id}.html")
        
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        logger.info(f"Saved combined HTML presentation to: {html_path}")
        
        return html_content

    def _create_html_presentation_fallback(self, plan_data: dict, project_id: str, theme: ThemeConfig) -> str:
        """
        Creates an HTML presentation from the plan data and converts it to PDF.
        
        Args:
            plan_data (dict): The presentation plan data containing slides and content
            project_id (str): The unique identifier for the presentation
            theme (ThemeConfig): The theme configuration to use
            
        Returns:
            str: Path to the generated PDF file
        """
        logger.info(f"Creating HTML presentation data with theme: {theme.display_name}")

        # Structure the presentation data for the template
        presentation_data = {
            'id': project_id,
            'title': plan_data.get('presentation_title', 'Generated Presentation'),
            'theme': theme.name,
            'metadata': {
                'description': plan_data.get('presentation_description', 'Created with AI'),
                'author': plan_data.get('author', 'AI Presentation Generator'),
                'date': datetime.now().strftime("%Y-%m-%d")
            },
            'slides': []
        }

        # Process each slide
        for slide_data in plan_data.get('slides', []):
            html_slide = {
                "type": slide_data.get("content_type", "content"),
                "title": slide_data.get("title", ""),
                "subtitle": slide_data.get("subtitle", ""),
                "layout": slide_data.get("layout_style", "standard"),
                "background": {
                    "type": "solid",
                    "value": theme.color_scheme.background_start
                },
                "content": []
            }

            # Convert content based on type
            if slide_data.get("content_type") == "bullet_points" and slide_data.get("bullet_points"):
                html_slide["content"].append({
                    "type": "list",
                    "value": slide_data["bullet_points"]
                })
            elif slide_data.get("content_type") == "paragraph" and slide_data.get("content"):
                html_slide["content"].append({
                    "type": "text",
                    "value": slide_data["content"]
                })
            elif slide_data.get("content_type") == "two_column" and (slide_data.get("left_content") or slide_data.get("right_content")):
                html_slide["content"].append({
                    "type": "columns",
                    "value": {
                        "left": slide_data.get("left_content", ""),
                        "right": slide_data.get("right_content", "")
                    }
                })
            elif slide_data.get("content"):
                # Default text content
                html_slide["content"].append({
                    "type": "text",
                    "value": slide_data["content"]
                })

            presentation_data['slides'].append(html_slide)

        # Generate HTML using the template
        html_content = render_template_string(
            PRESENTATION_TEMPLATE,
            presentation=presentation_data,
            theme_css=theme.get_css()
        )

        # Store the HTML for debugging
        debug_dir = os.path.join(Config.TEMP_DIR, "debug_html")
        os.makedirs(debug_dir, exist_ok=True)
        html_path = os.path.join(debug_dir, f"presentation_{project_id}.html")
        
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        logger.info(f"Saved HTML presentation to: {html_path}")
        
        # Generate PDF from the HTML
        try:
            pdf_path = self._generate_pdf_from_html(project_id, html_content)
            logger.info(f"Generated PDF at: {pdf_path}")
            return pdf_path
        except Exception as e:
            logger.error(f"Error generating PDF: {str(e)}")
            raise

    def _generate_pdf_from_html(self, project_id: str, html_content: str) -> str:
        """Generate PDF from HTML content with proper styling for PDF output"""
        from weasyprint import HTML, CSS
        
        # Clean the HTML content if it has code block formatting
        html_content = PPTProjectManager.clean_html_code_block(html_content)
        logger.info(f"Processing cleaned HTML content for PDF generation: {html_content[:200]}...")
        
        project_data = self.projects.get(project_id, {})
        theme_name = project_data.get('theme_name', 'corporate_blue')
        theme = PPTThemes.get_theme(theme_name)
        theme_css = theme.get_css() if theme else ""

        pdf_css = f"""
        @page {{ size: 1920px 1080px; margin: 0; }}
        html, body {{ width: 1920px; height: 1080px; margin: 0; padding: 0;
                    background: {theme.color_scheme.background_start if theme else '#ffffff'}; }}
        /* Match the actual markup emitted by PRESENTATION_TEMPLATE */
        .slides section {{ break-after: page; }}
        """

        output_path = os.path.join(Config.GENERATED_PPTS_DIR, f"presentation_{project_id}.pdf")
        HTML(string=html_content, base_url=os.getcwd()).write_pdf(
            output_path, stylesheets=[CSS(string=theme_css + pdf_css)]
        )
        return output_path
