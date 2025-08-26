import time
import google.generativeai as genai
from crewai import Agent, Task, Crew, Process
from crewai_tools import tool
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
        # Define the tool as a dictionary with the required structure

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
    
    def planning_task(self, agent, user_prompt, num_slides):
        """
        Task for the Planner Agent to create a presentation blueprint.
        """
        return Task(
            description=f"""
            Based on the user request: "{user_prompt}"
            
            Create a presentation plan with exactly {num_slides} slides.
            
            Your response MUST be a valid JSON object with this exact structure:
            {{
                "presentation_title": "Title of the presentation",
                "presentation_description": "Brief description of the presentation",
                "slides": [
                    {{
                        "title": "Slide title",
                        "content_type": "one of: title_only, bullet_points, paragraph, numbered_list, two_column, comparison, image_focus",
                        "description": "Brief description of the slide's purpose",
                        "content": "For paragraph type",
                        "bullet_points": ["Point 1", "Point 2", "Point 3"],  // For bullet_points type
                        "layout_style": "standard"  // or any specific layout name
                    }}
                ]
            }}
            
            IMPORTANT RULES:
            1. Response must be ONLY the JSON object - no explanation text, no markdown formatting
            2. All text content must be plain text - no markdown, no formatting symbols
            3. Each slide must have at least title and content_type
            4. Use appropriate content_type based on the content:
               - title_only: For section dividers (large centered titles)
               - bullet_points: For key points and lists
               - paragraph: For detailed explanations
               - numbered_list: For steps or processes
               - two_column: For comparisons
               - comparison: For pros/cons
               - image_focus: For visual emphasis
            - Mix content types for variety (don't make all slides bullet_points)
            - Use paragraphs for explanations, stories, and detailed concepts
            - Use bullet_points for key highlights, features, benefits
            - Use comparison slides for contrasting ideas
            - Use title_only slides as section breaks for long presentations
            - Use two_column for showing relationships or parallel concepts
            
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
                        "content_type": "bullet_points|paragraph|numbered_list|title_only|two_column|comparison|image_focus",
                        "layout_style": "standard|creative|minimal",
                        "visual_elements": ["image", "chart", "diagram"] or [],
                        "key_points": ["point1", "point2", "point3"]
                    }}
                ]
            }}
            
            Ensure the presentation has a logical flow, varied slide types, and covers the topic comprehensively.
            """,
            agent=agent,
            expected_output="A detailed JSON blueprint with varied slide types for the presentation structure"
        )
    
    def content_creation_task(self, agent, planning_result):
        """
        Task for the Content Creator Agent to generate actual content for each slide.
        """
        # Ensure planning_result is properly formatted
        if isinstance(planning_result, str):
            try:
                # Clean up any markdown formatting
                planning_result = planning_result.replace('```json\n', '').replace('\n```', '')
            except Exception as e:
                logger.warning(f"Error cleaning planning result: {e}")
                
        return Task(
            description=f"""
            Based on the presentation blueprint provided, generate detailed and varied content for each slide.
            
            Blueprint: {planning_result}
            
            Your task is to generate complete, detailed content for each slide, including all text,
            bullet points, and descriptions. The output should be a complete JSON with no markdown formatting.
            
            CONTENT CREATION RULES:
            
            For BULLET_POINTS slides:
            - Create 3-5 concise, impactful bullet points
            - Each point should be 8-15 words maximum
            - Use action-oriented language
            - Focus on benefits, features, or key insights
            
            For PARAGRAPH slides:
            - Write 2-4 well-structured paragraphs
            - Each paragraph should be 30-60 words
            - Tell a story, explain a concept, or provide detailed analysis
            - Use engaging, conversational language
            - Include examples or analogies where helpful
            
            For NUMBERED_LIST slides:
            - Create 3-6 sequential steps or ranked items
            - Each item should be clear and actionable
            - Use imperative language for processes
            
            For TWO_COLUMN slides:
            - Provide content for both left_content and right_content
            - Create complementary or contrasting information
            - Balance the content length between columns
            
            For COMPARISON slides:
            - Provide left_points and right_points arrays
            - Create 3-4 points for each side
            - Use left_title and right_title fields
            - Focus on clear contrasts or before/after scenarios
            
            For TITLE_ONLY slides:
            - Just provide a powerful, section-dividing title
            - No additional content needed
            
            For IMAGE_FOCUS slides:
            - Write descriptive content about the visual concept
            - Add 2-3 supporting bullet points
            - Include image_description field
            
            IMPORTANT FORMATTING RULES:
            - Do NOT use markdown formatting (avoid **, *, __, _, ~~, `)
            - Use plain text only
            - For emphasis, use capital letters or rephrase the sentence
            - Write in active voice
            - Use specific, concrete language
            - Avoid jargon unless necessary
            
            CONTENT VARIETY:
            - Mix detailed explanations with concise points
            - Include statistics, examples, and actionable insights
            - Vary sentence structure and length
            - Use rhetorical questions where appropriate
            - Include call-to-action elements
            
            Enhance the existing JSON structure by adding content fields:
            - "content": Main text content (for paragraphs and descriptions)
            - "bullet_points": Array of bullet points (plain text, no markdown)
            - "numbered_points": Array for numbered lists (plain text)
            - "left_content" / "right_content": For two-column layouts
            - "left_points" / "right_points": For comparison layouts
            - "left_title" / "right_title": For comparison section headers
            - "image_description": Description for visual content
            - "notes": Speaker notes or additional context
            
            Example of good content formats:
            
            Bullet Points:
            - "Increase productivity by 40% with automation tools"
            - "Reduce operational costs through streamlined processes"
            - "Enhance customer satisfaction with faster response times"
            
            Paragraph:
            "Digital transformation is reshaping how businesses operate in the 21st century. Companies that embrace technology-driven solutions see significant improvements in efficiency and customer engagement. By implementing cloud-based systems and automated workflows, organizations can focus on strategic initiatives rather than routine tasks."
            
            Maintain the original structure while enriching it with actual content.
            The content should be professional, informative, and appropriate for the intended audience.
            """,
            agent=agent,
            expected_output="Complete JSON with detailed content for all slides, including text, bullet points, and descriptions"
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

    def presentation_generation_task(self, agent, design_result):
        """
        Task for the Presentation Generator Agent to create the final presentation.
        """
        return Task(
            description=f'''
            Based on the design specifications provided, generate a complete, single HTML file
            for the presentation.

            Design Specifications: {design_result}

            Your task is to create a single HTML file that includes all the necessary HTML, CSS to render the presentations. DO NOT use javascript

            Just create the html, css jss code for the presentation and presentation only. Do 
            not create anything else. The code will be converted into pdf then into ppt so dont 
            create anything extra such as buttons 

            The final output should be a single HTML code that will eventually be converted into
            a pdf or a pptx file.
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
        Create a presentation using multiple AI agents.
        """
        # Initialize agents
        planner = self.agents.planner_agent()
        content_creator = self.agents.content_creator_agent()
        designer = self.agents.designer_agent()
        generator = self.agents.presentation_generator_agent()

        # Create tasks using the task manager
        planning_task = self.tasks.planning_task(
            planner, topic, style_preferences.get('num_slides', 5)
        )

        content_task = self.tasks.content_creation_task(
            content_creator, "{planning_result}"  # Will be replaced with actual result
        )
        content_task.context = [planning_task]

        design_task = self.tasks.design_task(
            designer, "{content_result}"  # Will be replaced with actual result
        )
        design_task.context = [content_task]

        generation_task = self.tasks.presentation_generation_task(
            generator, "{design_result}"
        )
        generation_task.context = [design_task]

        # Create crew with sequential process and clear task dependencies
        crew = Crew(
            agents=[planner],  # Start with just the planner
            tasks=[planning_task],
            process=Process.sequential,
            verbose=True  # Enable verbosity for debugging
        )

        # Execute tasks one at a time with proper result handling
        logger.info("Starting planning phase...")
        planning_result = crew.kickoff()
        
        # Update content task with planning results and create new crew
        content_task.description = content_task.description.format(planning_result=planning_result)
        crew = Crew(
            agents=[content_creator],
            tasks=[content_task],
            process=Process.sequential,
            verbose=True
        )
        
        logger.info("Starting content creation phase...")
        content_result = crew.kickoff()
        
        # Update design task with content results and create new crew
        design_task.description = design_task.description.format(content_result=content_result)
        crew = Crew(
            agents=[designer],
            tasks=[design_task],
            process=Process.sequential,
            verbose=True
        )
        
        logger.info("Starting design phase...")
        design_result = crew.kickoff()

        # Update generation task with design results and create new crew
        generation_task.description = generation_task.description.format(design_result=design_result)
        crew = Crew(
            agents=[generator],
            tasks=[generation_task],
            process=Process.sequential,
            verbose=True
        )

        logger.info("Starting presentation generation phase...")
        return crew.kickoff()