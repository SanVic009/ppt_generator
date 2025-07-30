import os
import time
import google.generativeai as genai
from crewai import Agent, Task, Crew, Process
from config import Config
import logging

# Configure logging
logger = logging.getLogger(__name__)

# Configure Gemini API
genai.configure(api_key=Config.GEMINI_API_KEY)

def retry_with_backoff(func, max_retries=None, delay=None, backoff=None):
    """
    Retry decorator with exponential backoff for handling API overload errors.
    """
    if max_retries is None:
        max_retries = Config.MAX_RETRIES
    if delay is None:
        delay = Config.RETRY_DELAY
    if backoff is None:
        backoff = Config.RETRY_BACKOFF
    
    def wrapper(*args, **kwargs):
        for attempt in range(max_retries + 1):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                error_str = str(e)
                
                # Check if it's a 503 overload error or similar
                is_overload_error = any(keyword in error_str.lower() for keyword in [
                    "503", "overloaded", "unavailable", "too many requests", "rate limit", "quota"
                ])
                
                if is_overload_error:
                    if attempt < max_retries:
                        wait_time = min(delay * (backoff ** attempt), Config.MAX_RETRY_DELAY)
                        logger.warning(f"API overloaded (attempt {attempt + 1}/{max_retries + 1}). "
                                     f"Retrying in {wait_time:.1f} seconds...")
                        logger.info(f"Error details: {error_str}")
                        time.sleep(wait_time)
                        continue
                    else:
                        logger.error(f"API still overloaded after {max_retries} retries. "
                                   f"Total wait time: {sum(min(delay * (backoff ** i), Config.MAX_RETRY_DELAY) for i in range(max_retries)):.1f} seconds")
                        raise e
                else:
                    # For non-overload errors, don't retry
                    logger.error(f"Non-retryable error: {error_str}")
                    raise e
        
        return None
    
    return wrapper

class PPTAgents:
    """
    Defines all the AI agents for PPT generation using CrewAI framework.
    Each agent has a specific role in the presentation creation pipeline.
    """
    
    def __init__(self, use_fallback_model=False):
        self.model = Config.FALLBACK_MODEL if use_fallback_model else Config.CREWAI_MODEL
        self.use_fallback = use_fallback_model
        if use_fallback_model:
            logger.info(f"Using fallback model: {self.model}")
    
    def planner_agent(self):
        """
        Planner Agent: Analyzes user requirements and creates a detailed presentation blueprint.
        """
        return Agent(
            role='Presentation Planner',
            goal='Create a comprehensive presentation blueprint based on user requirements',
            backstory="""You are an expert presentation strategist with years of experience in creating 
            compelling presentations. You understand how to structure information effectively, 
            determine the right content flow, and plan visual elements that enhance the message. 
            Your expertise lies in breaking down complex topics into digestible slide-by-slide content.""",
            verbose=True,
            allow_delegation=False,
            llm=self.model
        )
    
    def content_creator_agent(self):
        """
        Content Creator Agent: Generates actual textual content for each slide based on the blueprint.
        """
        return Agent(
            role='Content Creator',
            goal='Generate engaging and relevant content for each slide based on the presentation plan',
            backstory="""You are a skilled content writer and researcher who specializes in creating 
            presentation content. You have the ability to transform abstract concepts into clear, 
            engaging text that resonates with audiences. You understand how to write compelling 
            headlines, informative bullet points, and descriptive text that supports the overall 
            presentation narrative. Your content is always well-researched, accurate, and tailored 
            to the intended audience.""",
            verbose=True,
            allow_delegation=False,
            llm=self.model
        )
    
    def designer_agent(self):
        """
        Designer Agent: Defines visual presentation, layout, and styling for each slide.
        """
        return Agent(
            role='Presentation Designer',
            goal='Create visually appealing and professional slide designs that enhance content delivery',
            backstory="""You are a professional presentation designer with extensive experience in 
            visual communication and graphic design. You understand color theory, typography, 
            layout principles, and how to create slides that are both beautiful and functional. 
            You know how to balance text and visuals, choose appropriate color schemes, and 
            create layouts that guide the viewer's attention effectively. Your designs always 
            maintain consistency and professionalism while being visually engaging.""",
            verbose=True,
            allow_delegation=False,
            llm=self.model
        )

class PPTTasks:
    """
    Defines all the tasks that agents will perform in the PPT generation pipeline.
    """
    
    def planning_task(self, agent, user_prompt, num_slides):
        """
        Task for the Planner Agent to create a presentation blueprint.
        """
        return Task(
            description=f"""
            Create a detailed presentation blueprint based on the following user request:
            "{user_prompt}"
            
            Number of slides requested: {num_slides}
            
            For each slide, determine:
            1. A suitable and engaging title
            2. A clear description of what the slide should convey
            3. The content type (paragraph, bullet points, numbered list, etc.)
            4. Whether visual elements like images, charts, or diagrams are needed
            5. The slide's role in the overall presentation flow
            
            Output your plan as a structured JSON with the following format:
            {{
                "presentation_title": "Main presentation title",
                "presentation_description": "Brief description of the presentation",
                "total_slides": {num_slides},
                "slides": [
                    {{
                        "slide_number": 1,
                        "title": "Slide title",
                        "description": "What this slide should convey",
                        "content_type": "bullet_points|paragraph|numbered_list|title_only",
                        "visual_elements": ["image", "chart", "diagram"] or [],
                        "key_points": ["point1", "point2", "point3"]
                    }}
                ]
            }}
            
            Ensure the presentation has a logical flow and covers the topic comprehensively.
            """,
            agent=agent,
            expected_output="A detailed JSON blueprint for the presentation structure"
        )
    
    def content_creation_task(self, agent, planning_result):
        """
        Task for the Content Creator Agent to generate actual content for each slide.
        """
        return Task(
            description=f"""
            Based on the presentation blueprint provided, generate detailed content for each slide.
            
            Blueprint: {planning_result}
            
            For each slide in the blueprint, create:
            1. Compelling and informative text content
            2. Appropriate headings and subheadings
            3. Bullet points, paragraphs, or lists as specified
            4. Captions or descriptions for visual elements
            5. Ensure content is engaging, accurate, and well-structured
            
            Enhance the existing JSON structure by adding content fields:
            - "content": Main text content for the slide
            - "bullet_points": Array of bullet points if applicable
            - "image_descriptions": Descriptions for any images needed
            - "notes": Speaker notes or additional context
            
            Maintain the original structure while enriching it with actual content.
            The content should be professional, informative, and appropriate for the intended audience.
            """,
            agent=agent,
            expected_output="Enhanced JSON with complete textual content for all slides"
        )
    
    def design_task(self, agent, content_result):
        """
        Task for the Designer Agent to define visual styling and layout.
        """
        return Task(
            description=f"""
            Based on the content-rich presentation structure provided, define the visual design 
            and layout for each slide to create a professional and visually appealing presentation.
            
            Content Structure: {content_result}
            
            For each slide, determine:
            1. Layout type (title slide, content slide, two-column, image-focused, etc.)
            2. Color scheme and theme
            3. Font choices and text styling
            4. Visual element placement and sizing
            5. Background design and overall aesthetic
            6. Consistency elements across all slides
            
            Add design specifications to the JSON structure:
            - "layout": Layout type for the slide
            - "color_scheme": Primary and secondary colors
            - "font_style": Font family and sizing information
            - "background": Background color or style
            - "visual_placement": How visual elements should be positioned
            - "design_notes": Additional styling instructions
            
            Ensure the design is:
            - Professional and modern
            - Consistent across all slides
            - Appropriate for the content and audience
            - Visually balanced and easy to read
            """,
            agent=agent,
            expected_output="Complete JSON with content and comprehensive design specifications"
        )

class PPTCrew:
    """
    Orchestrates the entire PPT generation process using CrewAI.
    """
    
    def __init__(self):
        self.agents = PPTAgents()
        self.tasks = PPTTasks()
        self.fallback_agents = None
    
    @retry_with_backoff
    def _execute_crew(self, crew):
        """
        Execute crew with retry logic for handling API overload.
        """
        return crew.kickoff()
    
    def create_presentation_plan(self, user_prompt, num_slides=5):
        """
        Execute the complete PPT planning and content creation process.
        """
        try:
            # Try with primary model first
            logger.info(f"Starting presentation generation with primary model: {self.agents.model}")
            return self._generate_with_agents(self.agents, user_prompt, num_slides)
            
        except Exception as e:
            error_str = str(e)
            
            # If primary model fails with overload, try fallback model
            if ("503" in error_str or "overloaded" in error_str.lower() or "unavailable" in error_str.lower()) and not self.agents.use_fallback:
                logger.warning(f"Primary model overloaded, trying fallback model...")
                
                if self.fallback_agents is None:
                    self.fallback_agents = PPTAgents(use_fallback_model=True)
                
                try:
                    return self._generate_with_agents(self.fallback_agents, user_prompt, num_slides)
                except Exception as fallback_error:
                    logger.error(f"Fallback model also failed: {str(fallback_error)}")
                    # If both fail, raise the original error
                    raise e
            else:
                # For non-overload errors or if already using fallback, just raise
                raise e
    
    def _generate_with_agents(self, agents, user_prompt, num_slides):
        """
        Generate presentation using the specified agents.
        """
        # Initialize agents
        planner = agents.planner_agent()
        content_creator = agents.content_creator_agent()
        designer = agents.designer_agent()
        
        # Create tasks
        planning_task = self.tasks.planning_task(planner, user_prompt, num_slides)
        content_task = self.tasks.content_creation_task(content_creator, planning_task)
        design_task = self.tasks.design_task(designer, content_task)
        
        # Create and execute crew
        crew = Crew(
            agents=[planner, content_creator, designer],
            tasks=[planning_task, content_task, design_task],
            process=Process.sequential,
            verbose=True
        )
        
        # Execute the crew with retry logic and return results
        result = self._execute_crew(crew)
        logger.info("Presentation generation completed successfully")
        return result

