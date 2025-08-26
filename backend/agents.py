import time
import json
import os
import requests
from bs4 import BeautifulSoup
import google.generativeai as genai
from crewai import Agent, Task, Crew, Process
from config import Config
import logging

# Configure logging
logger = logging.getLogger(__name__)

# Configure Gemini API
genai.configure(api_key=Config.GEMINI_API_KEY)

# Generation settings will be applied when creating the model
DEFAULT_GENERATION_CONFIG = {
    "temperature": 0.7,
    "top_p": 0.8,
    "top_k": 40,
    "max_output_tokens": 8192,
}

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
        try:
            self.model = Config.FALLBACK_MODEL if use_fallback_model else Config.CREWAI_MODEL
            self.use_fallback = use_fallback_model
            if use_fallback_model:
                logger.info(f"Using fallback model: {self.model}")
            
            # Create model instance with generation settings
            self.model_instance = genai.GenerativeModel(
                self.model,
                generation_config=DEFAULT_GENERATION_CONFIG
            )
            logger.info(f"Successfully initialized model: {self.model}")
        except Exception as e:
            logger.error(f"Error initializing agent model: {e}")
            raise
            
    def presentation_generator_agent(self):
        """
        Presentation Generator Agent: Creates the final presentation output from the content and design specifications.
        """
        return Agent(
            role='Presentation Generator',
            goal='Transform the design specifications into a polished, interactive presentation',
            backstory="""You are an expert presentation developer with years of experience in creating 
            stunning digital presentations. You understand modern web technologies, visual design principles,
            and how to create engaging, interactive presentations. Your skills include implementing smooth
            transitions, responsive layouts, and ensuring the final presentation is both visually appealing
            and functionally robust. You excel at converting complex design specifications into polished,
            professional presentations that effectively communicate the intended message.""",
            verbose=True,
            allow_delegation=False,
            llm=getattr(self, 'model_instance', self.model)  # Fallback to self.model if model_instance isn't available
        )
    
    def content_researcher_agent(self):
        """
        Content Researcher Agent: Searches and analyzes web content to create presentation structure.
        """
        return Agent(
            role='Content Researcher',
            goal='Research and analyze web content to create well-structured presentation outline',
            backstory="""You are an expert content researcher and analyst who excels at finding 
            relevant information and organizing it into meaningful structures. You know how to 
            identify key themes, extract important concepts, and organize information into a 
            logical flow. Your expertise lies in understanding complex topics and breaking them 
            down into clear, manageable sections that will form the basis of a presentation.""",
            verbose=True,
            allow_delegation=False,
            llm=getattr(self, 'model_instance', self.model)
        )

    def planner_agent(self):
        """
        Planner Agent: Creates presentation structure based on researched content.
        """
        return Agent(
            role='Presentation Planner',
            goal='Analyze researched content and create an engaging presentation structure',
            backstory="""You are a professional presentation strategist who excels at organizing 
            information into clear, compelling narratives. You analyze provided research content 
            to identify key themes and create a logical presentation structure. You know how to 
            break down complex topics into digestible slides and ensure the presentation flows 
            naturally while maintaining audience engagement.""",
            verbose=True,
            allow_delegation=False,
            llm=getattr(self, 'model_instance', self.model)
        )
    
    def content_creator_agent(self):
        """
        Content Creator Agent: Generates actual textual content for each slide based on the blueprint.
        """
        return Agent(
            role='Content Creator',
            goal='Generate engaging and relevant plain-text content for each slide based on the presentation plan',
            backstory="""You are a skilled content writer and researcher who specializes in creating 
            presentation content. You have the ability to transform abstract concepts into clear, 
            engaging text that resonates with audiences. You understand how to write compelling 
            headlines, informative bullet points, and descriptive text that supports the overall 
            presentation narrative. Your content is always well-researched, accurate, and tailored 
            to the intended audience. 
            
            IMPORTANT: You NEVER use markdown formatting like **, *, __, _, ~~, or ` in your content. 
            You write in plain text only, using clear language and proper sentence structure. 
            For emphasis, you use capital letters or rephrase sentences. You keep bullet points 
            concise and under 15 words each.""",
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
    
    def research_task(self, agent, topic, num_slides):
        """
        Task for the Content Researcher Agent to gather and analyze web content.
        """
        return Task(
            description=f'''
            Research the topic: "{topic}" and gather comprehensive content for a {num_slides}-slide presentation.
            
            Follow these steps:
            1. Search the topic using Google Custom Search API to find relevant URLs
            2. Scrape content from the top 10 most relevant URLs
            3. Analyze the scraped content to identify:
               - Key themes and concepts
               - Important facts and statistics
               - Main arguments or points
               - Supporting examples
               - Relevant quotes
            4. Organize the research into a structured format
            
            Output your research as a structured JSON:
            {{
                "topic": "Main research topic",
                "total_sources": "Number of sources scraped",
                "main_themes": [
                    {{
                        "theme": "Identified theme or concept",
                        "importance_score": 1-10,
                        "supporting_content": "Content from sources supporting this theme",
                        "source_urls": ["URLs that mention this theme"]
                    }}
                ],
                "key_facts": [
                    {{
                        "fact": "Important fact or statistic",
                        "context": "Brief context about the fact",
                        "source_url": "URL where fact was found"
                    }}
                ],
                "quotes": [
                    {{
                        "quote": "Notable quote from sources",
                        "source": "Source name/URL"
                    }}
                ],
                "scraped_content": {{
                    "url1": "Relevant content from URL1",
                    "url2": "Relevant content from URL2"
                }}
            }}
            ''',
            agent=agent,
            expected_output="A comprehensive JSON containing research data and organized themes"
        )

    def planning_task(self, agent, research_result, num_slides):
        """
        Task for the Planner Agent to create presentation structure from research.
        """
        return Task(
            description=f"""
            Based on the provided research data, create a {num_slides}-slide presentation structure.
            
            Research Data: {research_result}
            
            IMPORTANT RULES:
            1. Response must be ONLY the JSON object - no explanation text
            2. All text content must be plain text - no markdown
            3. Each slide must have all required fields
            4. Slides must be based on the research themes and facts
            5. Use appropriate content_type based on the research content:
               - title_only: For section dividers
               - bullet_points: For key facts and points
               - paragraph: For detailed explanations
               - numbered_list: For processes
               - two_column: For comparisons
               - quote: For notable quotes
               - image_focus: For visual topics
            
            Output Format:
            {{
                "presentation_title": "Title based on research topic",
                "presentation_description": "Overview based on main themes",
                "total_slides": {num_slides},
                "slides": [
                    {{
                        "slide_number": 1,
                        "title": "Title based on theme",
                        "subtitle": "Optional subtitle",
                        "content_type": "slide type",
                        "description": "Content description",
                        "layout_style": "standard|creative|minimal",
                        "research_themes": ["Related themes"],
                        "key_facts": ["Related facts"],
                        "sources": ["Source URLs"]
                    }}
                ]
            }}
            """,
            agent=agent,
            expected_output="A detailed presentation structure based on research data"
        )
    
    def content_creation_task(self, agent, planning_result, research_data):
        """
        Task for the Content Creator Agent to generate content for each slide based on research and planning.
        """
        # Clean up any markdown formatting if needed
        if isinstance(planning_result, str):
            try:
                planning_result = planning_result.replace('```json\n', '').replace('\n```', '')
            except Exception as e:
                logger.warning(f"Error cleaning planning result: {e}")
        
        return Task(
            description=f"""
            Create detailed content for each slide based on the planning structure and research data.
            
            Planning Structure: {planning_result}
            Research Data: {research_data}
            
            IMPORTANT RULES:
            1. Generate content that directly relates to the research findings
            2. Use research-backed facts and statistics
            3. Incorporate relevant quotes when appropriate
            4. All content must be plain text - no markdown formatting
            5. Follow slide's content_type requirements:
               - bullet_points: Short, clear points (max 15 words each)
               - paragraph: Clear, concise explanations
               - numbered_list: Sequential steps or points
               - quote: Use researched quotes with attribution
               - two_column: Parallel points or comparisons
               - title_only: Large impactful text
            6. Include source attribution when using specific facts or quotes
            
            Output Format:
            {{
                "slides": [
                    {{
                        "slide_number": 1,
                        "content": {{
                            "title": "Slide title text",
                            "subtitle": "Optional subtitle text",
                            "main_content": "Main slide content formatted according to content_type",
                            "notes": "Optional speaker notes or context",
                            "sources": ["Source URLs for facts/quotes used"]
                        }}
                    }}
                ]
            }}
            """,
            agent=agent,
            expected_output="Detailed slide content based on research and planning"
        )
    
    def design_task(self, agent, content_result, research_data):
        """
        Task for the Designer Agent to define visual styling and layout using research insights.
        """
        return Task(
            description=f"""
            Define the visual design and layout for a research-backed presentation.
            
            Content Structure: {content_result}
            Research Data: {research_data}
            
            For each slide:
            1. Choose layout based on content type and research data
            2. Determine appropriate visual elements:
               - Charts/graphs for statistics
               - Icons for key concepts
               - Images for visual support
               - Diagrams for processes
            3. Create a cohesive visual theme that:
               - Reflects the topic's domain
               - Supports data visualization
               - Enhances content readability
            4. Define data presentation formats:
               - Chart types for statistics
               - Visual hierarchy for facts
               - Quote styling for citations
               - Source attribution layouts
            
            Add design specifications:
            - "layout_type": Based on content and research
            - "visual_elements": {{"type": "chart|image|icon|diagram", "purpose": "data|concept|process"}}
            - "color_scheme": Primary and accent colors
            - "typography": Font choices and text hierarchy
            - "data_visualization": Chart types and formats
            - "source_styling": Citation and attribution design
            
            Design Guidelines:
            1. Academic and Professional:
               - Clean, data-focused layouts
               - Clear visual hierarchy
               - Prominent source attributions
            2. Research Emphasis:
               - Highlight key statistics
               - Visualize data effectively
               - Clear citation formatting
            3. Visual Balance:
               - Content-to-whitespace ratio
               - Text-to-visual balance
               - Consistent alignment
            """,
            agent=agent,
            expected_output="Complete JSON with content and comprehensive design specifications"
        )

    def presentation_generation_task(self, agent, design_result):
        """
        Task for the Presentation Generator Agent to create the final presentation.
        """
        return Task(
            description=f'''
            Based on the design specifications provided, generate separate HTML files for each slide.

            Design Specifications: {design_result}

            Your task is to create individual HTML/CSS code for EACH SLIDE SEPARATELY, maintaining
            consistent styling across all slides.

            Requirements:
            1. Generate separate HTML code blocks, one for each slide
            2. Each slide must include:
               - Complete HTML structure (doctype, head, body)
               - Embedded CSS for styling
               - 16:9 aspect ratio
               - Proper font scaling and layout
            3. Maintain consistent styling across all slides
            4. No JavaScript
            5. No extra elements like buttons or navigation
            6. Follow the aspect ratio. If there is more content, then change the font size according to it

            Format your response as a series of HTML code blocks, one for each slide:

            ```html
            <!-- Slide 1 -->
            [HTML for slide 1]
            ```

            ```html
            <!-- Slide 2 -->
            [HTML for slide 2]
            ```

            And so on for each slide.
            ''',
            agent=agent,
            expected_output="A single HTML file containing the complete presentation."
        )

class PPTCrew:
    """
    Orchestrates the AI agents in the presentation creation process.
    """
    
    def __init__(self, use_fallback_model=False):
        self.agents = PPTAgents(use_fallback_model)
        self.tasks = PPTTasks()  # Initialize tasks instance

    @retry_with_backoff
    def create_presentation(self, topic, style_preferences=None):
        """
        Create a research-driven presentation using multiple AI agents.
        """
        # Initialize agents
        researcher = self.agents.content_researcher_agent()
        planner = self.agents.planner_agent()
        content_creator = self.agents.content_creator_agent()
        designer = self.agents.designer_agent()
        generator = self.agents.presentation_generator_agent()

        num_slides = style_preferences.get('num_slides', 5)

        # Research Phase: Gather and analyze web content
        research_task = self.tasks.research_task(
            researcher, topic, num_slides
        )

        crew = Crew(
            agents=[researcher],
            tasks=[research_task],
            process=Process.sequential,
            verbose=True
        )

        logger.info("Starting research phase...")
        research_result = crew.kickoff()

        # Planning Phase: Create structure based on research
        planning_task = self.tasks.planning_task(
            planner, research_result, num_slides
        )
        planning_task.context = [research_task]

        crew = Crew(
            agents=[planner],
            tasks=[planning_task],
            process=Process.sequential,
            verbose=True
        )

        logger.info("Starting planning phase...")
        planning_result = crew.kickoff()

        # Content Creation Phase
        content_task = self.tasks.content_creation_task(
            content_creator, planning_result, research_result
        )
        content_task.context = [planning_task, research_task]

        crew = Crew(
            agents=[content_creator],
            tasks=[content_task],
            process=Process.sequential,
            verbose=True
        )

        logger.info("Starting content creation phase...")
        content_result = crew.kickoff()

        # Design Phase
        design_task = self.tasks.design_task(
            designer, content_result, research_result
        )
        design_task.context = [content_task, research_task]

        crew = Crew(
            agents=[designer],
            tasks=[design_task],
            process=Process.sequential,
            verbose=True
        )

        logger.info("Starting design phase...")
        design_result = crew.kickoff()

        # Generation Phase
        generation_task = self.tasks.presentation_generation_task(
            generator, design_result
        )
        generation_task.context = [design_task]

        crew = Crew(
            agents=[generator],
            tasks=[generation_task],
            process=Process.sequential,
            verbose=True
        )

        logger.info("Starting presentation generation phase...")
        return crew.kickoff()