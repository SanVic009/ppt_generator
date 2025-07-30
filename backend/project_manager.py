import os
import json
import uuid
import zipfile
from datetime import datetime
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from agents import PPTCrew
from config import Config
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PPTProjectManager:
    """
    Manages the complete PPT generation process from user input to final deliverable.
    Coordinates AI agents and handles file generation.
    """
    
    def __init__(self, socketio=None):
        self.socketio = socketio
        self.crew = PPTCrew()
        self.projects = {}  # Store project information
        self.state_file = os.path.join(Config.TEMP_DIR, 'project_states.json')
        
        # Ensure directories exist
        os.makedirs(Config.GENERATED_PPTS_DIR, exist_ok=True)
        os.makedirs(Config.TEMP_DIR, exist_ok=True)
        
        # Load persisted project states
        self._load_project_states()
    
    def _save_project_state(self, project_id):
        """Save project state to disk to survive restarts."""
        try:
            # Only save essential state information
            state_data = {}
            if project_id in self.projects:
                project = self.projects[project_id].copy()
                # Remove non-serializable objects
                project.pop('socketio', None)
                state_data[project_id] = project
            
            # Load existing states and update
            existing_states = {}
            if os.path.exists(self.state_file):
                try:
                    with open(self.state_file, 'r') as f:
                        existing_states = json.load(f)
                except (json.JSONDecodeError, IOError):
                    pass
            
            existing_states.update(state_data)
            
            with open(self.state_file, 'w') as f:
                json.dump(existing_states, f, indent=2)
                
        except Exception as e:
            logger.warning(f"Failed to save project state: {e}")
    
    def _validate_plan_data(self, plan_data):
        """
        Validate and fix plan_data structure to ensure it has all required fields.
        """
        if not isinstance(plan_data, dict):
            logger.error(f"plan_data is not a dictionary: {type(plan_data)}")
            return False
        
        # Ensure required top-level keys exist
        required_keys = ['presentation_title', 'presentation_description', 'slides']
        for key in required_keys:
            if key not in plan_data:
                logger.warning(f"Missing required key '{key}' in plan_data")
                if key == 'presentation_title':
                    plan_data[key] = 'Generated Presentation'
                elif key == 'presentation_description':
                    plan_data[key] = 'Created with AI'
                elif key == 'slides':
                    plan_data[key] = []
        
        # Ensure slides is a list
        if not isinstance(plan_data.get('slides'), list):
            logger.warning("'slides' is not a list, converting or creating empty list")
            plan_data['slides'] = []
        
        # Validate each slide
        for i, slide in enumerate(plan_data['slides']):
            if not isinstance(slide, dict):
                logger.warning(f"Slide {i} is not a dictionary: {type(slide)}")
                plan_data['slides'][i] = {
                    'title': f'Slide {i + 1}',
                    'content': 'Generated content',
                    'content_type': 'bullet_points',
                    'bullet_points': ['Point 1', 'Point 2', 'Point 3']
                }
                continue
            
            # Ensure required slide keys
            slide_defaults = {
                'title': f'Slide {i + 1}',
                'content': 'Generated content',
                'content_type': 'bullet_points',
                'bullet_points': ['Point 1', 'Point 2', 'Point 3'],
                'color_scheme': 'professional_blue'
            }
            
            for key, default_value in slide_defaults.items():
                if key not in slide:
                    slide[key] = default_value
        
        return True
    
    def _clean_json_content(self, content):
        """
        Clean JSON content that might be wrapped in markdown code blocks.
        CrewAI often returns JSON wrapped in ```json ... ``` blocks.
        """
        if not isinstance(content, str):
            return content
        
        # Remove markdown code block formatting
        content = content.strip()
        
        # Remove ```json at the beginning
        if content.startswith('```json'):
            content = content[7:]  # Remove '```json'
        elif content.startswith('```'):
            content = content[3:]   # Remove '```'
        
        # Remove ``` at the end
        if content.endswith('```'):
            content = content[:-3]
        
        # Strip any remaining whitespace
        content = content.strip()
        
        return content
    
    def _extract_crew_result(self, crew_output):
        """
        Extract the actual result from a CrewOutput object.
        CrewAI returns a special CrewOutput object that needs to be handled properly.
        """
        logger.info(f"CrewOutput type: {type(crew_output)}")
        
        # Try to get available attributes (filter out private ones for cleaner output)
        available_attrs = [attr for attr in dir(crew_output) if not attr.startswith('_')]
        logger.info(f"CrewOutput public attributes: {available_attrs}")
        
        try:
            # Try different ways to extract the result in order of preference
            extraction_methods = [
                ('raw', lambda x: x.raw),
                ('result', lambda x: x.result),
                ('output', lambda x: x.output),
                ('text', lambda x: x.text),
                ('content', lambda x: x.content),
                ('str', lambda x: str(x))
            ]
            
            for method_name, method_func in extraction_methods:
                try:
                    if method_name == 'str' or hasattr(crew_output, method_name.replace('str', '__str__')):
                        result = method_func(crew_output)
                        logger.info(f"Successfully extracted using method: {method_name}")
                        logger.info(f"Extracted result type: {type(result)}")
                        if isinstance(result, str) and len(result) > 200:
                            logger.info(f"Result preview: {result[:200]}...")
                        else:
                            logger.info(f"Result: {result}")
                        return result
                except AttributeError:
                    continue
                except Exception as e:
                    logger.warning(f"Method {method_name} failed: {e}")
                    continue
            
            # If all methods fail, return a string representation
            logger.warning("All extraction methods failed, returning string representation")
            return str(crew_output)
                
        except Exception as e:
            logger.error(f"Failed to extract result from CrewOutput: {e}")
            return f"Error extracting result: {str(e)}"
    
    def _load_project_states(self):
        """Load project states from disk."""
        try:
            if os.path.exists(self.state_file):
                with open(self.state_file, 'r') as f:
                    self.projects = json.load(f)
                logger.info(f"Loaded {len(self.projects)} project states from disk")
        except Exception as e:
            logger.warning(f"Failed to load project states: {e}")
            self.projects = {}
        os.makedirs(Config.TEMP_DIR, exist_ok=True)
    
    def emit_progress(self, project_id, stage, message):
        """Emit progress updates via WebSocket and persist state"""
        # Update project stage in memory
        if project_id in self.projects:
            self.projects[project_id]['current_stage'] = stage
            self.projects[project_id]['last_message'] = message
            self.projects[project_id]['last_update'] = datetime.now().isoformat()
        
        if self.socketio:
            self.socketio.emit('progress_update', {
                'project_id': project_id,
                'stage': stage,
                'message': message,
                'timestamp': datetime.now().isoformat()
            }, room=project_id)
        
        # Persist state after each progress update
        self._save_project_state(project_id)
        logger.info(f"[{project_id}] {stage}: {message}")
    
    def generate_presentation(self, user_prompt, num_slides=5, project_id=None):
        """
        Main method to generate a complete presentation.
        """
        if not project_id:
            project_id = str(uuid.uuid4())
        
        try:
            # Initialize project
            self.projects[project_id] = {
                'id': project_id,
                'prompt': user_prompt,
                'num_slides': num_slides,
                'status': 'started',
                'created_at': datetime.now().isoformat(),
                'stages': []
            }
            
            self.emit_progress(project_id, 'initialization', 'Starting presentation generation...')
            
            # Stage 1: Planning
            self.emit_progress(project_id, 'planning', 'Planning Agent is analyzing your requirements...')
            presentation_plan = self.crew.create_presentation_plan(user_prompt, num_slides)
            
            # Parse the result - CrewOutput object needs special handling
            try:
                # Extract the actual result from CrewOutput object
                raw_result = self._extract_crew_result(presentation_plan)
                
                # Now try to parse the extracted result
                if isinstance(raw_result, str):
                    # Clean any markdown formatting from the JSON
                    cleaned_result = self._clean_json_content(raw_result)
                    
                    # Try to parse as JSON
                    try:
                        plan_data = json.loads(cleaned_result)
                        logger.info("Successfully parsed CrewOutput as JSON after cleaning")
                    except json.JSONDecodeError as json_err:
                        # If not valid JSON, create fallback plan
                        logger.warning(f"CrewOutput result is not valid JSON after cleaning: {json_err}")
                        logger.debug(f"Cleaned result was: {cleaned_result[:500]}...")
                        plan_data = self._create_fallback_plan(user_prompt, num_slides)
                elif isinstance(raw_result, dict):
                    # Already a dictionary
                    plan_data = raw_result
                    logger.info("CrewOutput was already a dictionary")
                else:
                    # Unknown format, use fallback
                    logger.warning(f"Unknown CrewOutput format: {type(raw_result)}, using fallback plan")
                    plan_data = self._create_fallback_plan(user_prompt, num_slides)
                    
            except Exception as e:
                # If all parsing fails, create a basic structure
                logger.error(f"Failed to parse CrewOutput: {e}, using fallback plan")
                plan_data = self._create_fallback_plan(user_prompt, num_slides)
            
            # Validate and fix plan_data structure
            logger.info(f"Validating plan data structure... Type: {type(plan_data)}")
            
            # Additional check: if plan_data is still a CrewOutput, extract it
            if hasattr(plan_data, 'raw') or str(type(plan_data)).lower().find('crewoutput') != -1:
                logger.warning("plan_data is still a CrewOutput object, extracting content...")
                plan_data = self._extract_crew_result(plan_data)
                
                if isinstance(plan_data, str):
                    cleaned_result = self._clean_json_content(plan_data)
                    try:
                        plan_data = json.loads(cleaned_result)
                        logger.info("Successfully parsed nested CrewOutput as JSON")
                    except json.JSONDecodeError:
                        logger.warning("Nested CrewOutput is not valid JSON, using fallback")
                        plan_data = self._create_fallback_plan(user_prompt, num_slides)
            
            if not self._validate_plan_data(plan_data):
                logger.warning("Plan data validation failed, using fallback plan")
                plan_data = self._create_fallback_plan(user_prompt, num_slides)
                self._validate_plan_data(plan_data)  # Ensure fallback is also valid
            
            logger.info(f"Final plan_data type before PowerPoint creation: {type(plan_data)}")
            logger.info(f"Plan_data keys: {list(plan_data.keys()) if isinstance(plan_data, dict) else 'Not a dictionary'}")
            
            self.emit_progress(project_id, 'content_creation', 'Content Creator is generating slide content...')
            
            # Stage 2: Generate PowerPoint
            self.emit_progress(project_id, 'design', 'Designer is creating the visual presentation...')
            ppt_path = self._create_powerpoint(plan_data, project_id)
            
            # Stage 3: Finalization
            self.emit_progress(project_id, 'packaging', 'Finalizing your presentation...')
            
            # Update project with results
            self.projects[project_id].update({
                'status': 'completed',
                'plan': plan_data,
                'ppt_path': ppt_path,
                'completed_at': datetime.now().isoformat()
            })
            
            self.emit_progress(project_id, 'completed', 'Presentation generated successfully!')
            
            if self.socketio:
                self.socketio.emit('project_completed', {
                    'project_id': project_id,
                    'result': {
                        'success': True,
                        'presentation_plan': plan_data,
                        'file_path': ppt_path
                    }
                }, room=project_id)
            
            return {
                'success': True,
                'project_id': project_id,
                'plan': plan_data,
                'file_path': ppt_path
            }
            
        except Exception as e:
            error_str = str(e)
            logger.error(f"Error generating presentation: {error_str}")
            logger.error(f"Error type: {type(e)}")
            
            # Provide specific error messages for common issues
            if "CrewOutput" in error_str and "get" in error_str:
                user_message = "There was an issue processing the AI-generated content. The system will use a fallback approach."
                self.emit_progress(project_id, 'failed', user_message)
            elif "503" in error_str or "overloaded" in error_str.lower() or "unavailable" in error_str.lower():
                user_message = "The AI service is currently overloaded. This is a temporary issue. Please try again in a few minutes."
                self.emit_progress(project_id, 'failed', user_message)
            elif "api key" in error_str.lower() and ("invalid" in error_str.lower() or "expired" in error_str.lower()):
                user_message = "API key issue detected. Please check your API key configuration."
                self.emit_progress(project_id, 'failed', user_message)
            else:
                user_message = f"An error occurred during generation: {error_str}"
                self.emit_progress(project_id, 'failed', user_message)
            
            self.projects[project_id]['status'] = 'failed'
            self.projects[project_id]['error'] = error_str
            self.projects[project_id]['user_message'] = user_message
            
            if self.socketio:
                self.socketio.emit('project_failed', {
                    'project_id': project_id,
                    'error': error_str,
                    'user_message': user_message
                }, room=project_id)
            
            return {
                'success': False,
                'project_id': project_id,
                'error': error_str,
                'user_message': user_message
            }
    
    def _create_fallback_plan(self, user_prompt, num_slides):
        """Create a basic presentation plan if AI generation fails"""
        return {
            "presentation_title": f"Presentation: {user_prompt[:50]}...",
            "presentation_description": f"A presentation about {user_prompt}",
            "total_slides": num_slides,
            "slides": [
                {
                    "slide_number": i + 1,
                    "title": f"Slide {i + 1}",
                    "description": f"Content for slide {i + 1}",
                    "content_type": "bullet_points",
                    "content": f"Content related to: {user_prompt}",
                    "bullet_points": [
                        f"Key point {j + 1} about {user_prompt}"
                        for j in range(3)
                    ],
                    "layout": "content_slide",
                    "color_scheme": "professional_blue"
                }
                for i in range(num_slides)
            ]
        }
    
    def _create_powerpoint(self, plan_data, project_id):
        """
        Create the actual PowerPoint file from the plan data.
        """
        logger.info(f"Creating PowerPoint with plan_data type: {type(plan_data)}")
        
        # Safety check: if plan_data is still a CrewOutput, extract and parse it
        if hasattr(plan_data, 'raw') or str(type(plan_data)).lower().find('crewoutput') != -1:
            logger.warning("plan_data is a CrewOutput in _create_powerpoint, extracting...")
            raw_result = self._extract_crew_result(plan_data)
            
            if isinstance(raw_result, str):
                cleaned_result = self._clean_json_content(raw_result)
                try:
                    plan_data = json.loads(cleaned_result)
                    logger.info("Successfully extracted and parsed CrewOutput in PowerPoint creation")
                except json.JSONDecodeError:
                    logger.error("Failed to parse CrewOutput in PowerPoint creation, using fallback")
                    plan_data = self._create_fallback_plan("Generated Presentation", 5)
            elif isinstance(raw_result, dict):
                plan_data = raw_result
            else:
                logger.error("Unknown CrewOutput format in PowerPoint creation, using fallback")
                plan_data = self._create_fallback_plan("Generated Presentation", 5)
        
        # Ensure plan_data is a dictionary
        if not isinstance(plan_data, dict):
            logger.error(f"plan_data is not a dictionary: {type(plan_data)}, using fallback")
            plan_data = self._create_fallback_plan("Generated Presentation", 5)
        
        logger.info(f"Final plan_data type in PowerPoint creation: {type(plan_data)}")
        logger.info(f"Available keys: {list(plan_data.keys()) if isinstance(plan_data, dict) else 'None'}")
        
        # Create presentation
        prs = Presentation()
        
        # Set slide size (16:9 aspect ratio)
        prs.slide_width = Inches(13.33)
        prs.slide_height = Inches(7.5)
        
        # Title slide
        title_slide_layout = prs.slide_layouts[0]  # Title slide layout
        slide = prs.slides.add_slide(title_slide_layout)
        
        title = slide.shapes.title
        subtitle = slide.placeholders[1]
        
        title.text = plan_data.get('presentation_title', 'Generated Presentation')
        subtitle.text = plan_data.get('presentation_description', 'Created with AI')
        
        # Style title slide
        self._style_title_slide(title, subtitle)
        
        # Content slides
        for slide_data in plan_data.get('slides', []):
            self._create_content_slide(prs, slide_data)
        
        # Save presentation
        filename = f"presentation_{project_id}.pptx"
        file_path = os.path.join(Config.GENERATED_PPTS_DIR, filename)
        prs.save(file_path)
        
        return file_path
    
    def _style_title_slide(self, title, subtitle):
        """Apply styling to title slide"""
        # Title styling
        title_font = title.text_frame.paragraphs[0].font
        title_font.name = 'Poppins'
        title_font.size = Pt(44)
        title_font.bold = True
        title_font.color.rgb = RGBColor(25, 25, 112)  # Midnight blue
        
        # Subtitle styling
        subtitle_font = subtitle.text_frame.paragraphs[0].font
        subtitle_font.name = 'Inter'
        subtitle_font.size = Pt(24)
        subtitle_font.color.rgb = RGBColor(70, 70, 70)  # Dark gray
    
    def _create_content_slide(self, prs, slide_data):
        """Create a content slide based on slide data"""
        # Use content slide layout
        content_slide_layout = prs.slide_layouts[1]  # Title and content layout
        slide = prs.slides.add_slide(content_slide_layout)
        
        # Set title
        title = slide.shapes.title
        title.text = slide_data.get('title', 'Slide Title')
        
        # Style title
        title_font = title.text_frame.paragraphs[0].font
        title_font.name = 'Poppins'
        title_font.size = Pt(32)
        title_font.bold = True
        title_font.color.rgb = RGBColor(25, 25, 112)  # Midnight blue
        
        # Add content
        content_placeholder = slide.placeholders[1]
        content_frame = content_placeholder.text_frame
        content_frame.clear()  # Clear default text
        
        # Add content based on type
        content_type = slide_data.get('content_type', 'bullet_points')
        
        if content_type == 'bullet_points' and slide_data.get('bullet_points'):
            for point in slide_data['bullet_points']:
                p = content_frame.add_paragraph()
                p.text = point
                p.level = 0
                p.font.name = 'Inter'
                p.font.size = Pt(18)
                p.font.color.rgb = RGBColor(50, 50, 50)
        
        elif slide_data.get('content'):
            p = content_frame.add_paragraph()
            p.text = slide_data['content']
            p.font.name = 'Inter'
            p.font.size = Pt(18)
            p.font.color.rgb = RGBColor(50, 50, 50)
        
        # Apply background color based on design
        self._apply_slide_background(slide, slide_data.get('color_scheme', 'professional_blue'))
    
    def _apply_slide_background(self, slide, color_scheme):
        """Apply background styling to slide"""
        # This is a simplified version - in a full implementation,
        # you would apply more sophisticated styling based on the color scheme
        background = slide.background
        fill = background.fill
        fill.solid()
        
        # Color schemes
        if color_scheme == 'professional_blue':
            fill.fore_color.rgb = RGBColor(248, 249, 250)  # Light gray background
        elif color_scheme == 'modern_green':
            fill.fore_color.rgb = RGBColor(240, 253, 244)  # Light green background
        else:
            fill.fore_color.rgb = RGBColor(255, 255, 255)  # White background
    
    def get_project_status(self, project_id):
        """Get the current status of a project"""
        return self.projects.get(project_id, {'status': 'not_found'})
    
    def download_project(self, project_id):
        """Prepare project for download"""
        project = self.projects.get(project_id)
        if not project or project['status'] != 'completed':
            return None
        
        return project.get('ppt_path')
    
    def list_projects(self):
        """List all projects"""
        return list(self.projects.values())
    
    def delete_project(self, project_id):
        """Delete a project and its files"""
        project = self.projects.get(project_id)
        if project:
            # Delete files
            if 'ppt_path' in project and os.path.exists(project['ppt_path']):
                os.remove(project['ppt_path'])
            
            # Remove from memory
            del self.projects[project_id]
            return True
        return False

