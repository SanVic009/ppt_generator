import time
import json
import logging

import google.generativeai as genai
from crewai import Agent, Task, Crew, Process

from config import Config
from scraper import google_search, scrape_webpage

try:
    from crewai.tools import tool
except ImportError:
    try:
        from crewai_tools import tool
    except ImportError:
        from langchain.tools import tool

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

                # Check if it's a retryable error (overload or network issues)
                is_retryable_error = any(
                    keyword in error_str.lower()
                    for keyword in [
                        "503",
                        "overloaded",
                        "unavailable",
                        "too many requests",
                        "rate limit",
                        "quota",
                        "temporary failure in name resolution",
                        "connection error",
                        "timeout",
                        "network",
                        "dns",
                        "resolve",
                        "connection refused",
                        "connection timeout",
                    ]
                )

                if is_retryable_error:
                    if attempt < max_retries:
                        wait_time = min(
                            delay * (backoff**attempt), Config.MAX_RETRY_DELAY
                        )
                        logger.warning(
                            f"API/Network error (attempt {attempt + 1}/{max_retries + 1}). "
                            f"Retrying in {wait_time:.1f} seconds..."
                        )
                        logger.info(f"Error details: {error_str}")
                        time.sleep(wait_time)
                        continue
                    else:
                        logger.error(
                            f"API/Network still unavailable after {max_retries} retries. "
                            f"Total wait time: {sum(min(delay * (backoff**i), Config.MAX_RETRY_DELAY) for i in range(max_retries)):.1f} seconds"
                        )
                        raise e
                else:
                    # For non-retryable errors, don't retry
                    logger.error(f"Non-retryable error: {error_str}")
                    raise e

        return None

    return wrapper


# Research functions for the Content Researcher Agent
@tool("Search Web")
def search_web_func(query: str) -> str:
    """Search the web using Tavily API for a given query. Use this to find real factual information."""
    try:
        logger.info(f"🔍 Searching web for: {query}")
        results = google_search(query, num=8)
        logger.info(f"✅ Found {len(results)} search results for: {query}")
        return json.dumps(
            {"query": query, "results": results, "total_found": len(results)}, indent=2
        )
    except Exception as e:
        logger.error(f"❌ Web search error for '{query}': {e}")
        # Return mock data if API fails - but clearly indicate it's mock data
        return json.dumps(
            {
                "query": query,
                "error": str(e),
                "results": [],
                "note": "Search API not available, using topic-based content generation",
            }
        )


@tool("Scrape Webpage")
def scrape_content_func(url: str) -> str:
    """Scrape content from a webpage URL to read the detailed information."""
    try:
        logger.info(f"📄 Scraping content from: {url}")
        result = scrape_webpage(url)
        logger.info(f"✅ Successfully scraped content from: {url}")
        return json.dumps(result, indent=2)
    except Exception as e:
        logger.error(f"❌ Scraping error for {url}: {e}")
        return json.dumps({"error": str(e), "url": url, "content": ""})


def analyze_topic_func(topic: str) -> str:
    """Analyze a topic and generate relevant research points when web search is not available."""
    logger.info(f"🧠 Analyzing topic: {topic}")

    # Create topic-specific research structure
    analysis = {
        "topic": topic,
        "analysis_method": "AI-based topic analysis",
        "suggested_research_areas": [
            f"Background and history of {topic}",
            f"Key achievements and milestones related to {topic}",
            f"Current status and recent developments about {topic}",
            f"Impact and significance of {topic}",
            f"Future outlook and implications of {topic}",
        ],
        "content_focus": f"Generate content specifically about '{topic}' and not generic presentation advice",
    }

    logger.info(f"✅ Topic analysis completed for: {topic}")
    return json.dumps(analysis, indent=2)


class PPTAgents:
    """
    Defines all the AI agents for PPT generation using CrewAI framework.
    Each agent has a specific role in the presentation creation pipeline.
    """

    def __init__(self, use_fallback_model=False):
        try:
            self.model = (
                Config.FALLBACK_MODEL if use_fallback_model else Config.CREWAI_MODEL
            )
            self.use_fallback = use_fallback_model
            if use_fallback_model:
                logger.info(f"Using fallback model: {self.model}")

            # Create model instance with generation settings
            self.model_instance = genai.GenerativeModel(
                self.model, generation_config=DEFAULT_GENERATION_CONFIG
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
            role="Presentation Generator",
            goal="Transform the design specifications into a polished, interactive presentation",
            backstory="""You are an expert presentation developer with years of experience in creating 
            stunning digital presentations. You understand modern web technologies, visual design principles,
            and how to create engaging, interactive presentations. Your skills include implementing smooth
            transitions, responsive layouts, and ensuring the final presentation is both visually appealing
            and functionally robust. You excel at converting complex design specifications into polished,
            professional presentations that effectively communicate the intended message.""",
            verbose=True,
            allow_delegation=False,
            llm=getattr(
                self, "model_instance", self.model
            ),  # Fallback to self.model if model_instance isn't available
        )

    def content_researcher_agent(self):
        """
        Content Researcher Agent: Searches and analyzes web content to create presentation structure.
        """
        return Agent(
            role="Content Researcher",
            goal="Research and gather specific information about the given topic, not generic presentation advice",
            backstory="""You are an expert content researcher who specializes in gathering specific 
            information about requested topics. You MUST focus on the exact topic provided by the user 
            and gather real, factual information about that specific subject. You have access to web 
            search capabilities to find current, relevant information. Your job is to research the 
            SPECIFIC TOPIC requested, not to provide generic presentation advice or unrelated content. 
            You ALWAYS start by analyzing the exact topic requested and gathering relevant facts and 
            information about that specific subject.""",
            verbose=True,
            allow_delegation=False,
            tools=[search_web_func, scrape_content_func],
            llm=getattr(self, "model_instance", self.model),
        )

    def planner_agent(self):
        """
        Planner Agent: Creates presentation structure based on researched content.
        """
        return Agent(
            role="Presentation Planner",
            goal="Analyze researched content and create an engaging presentation structure",
            backstory="""You are a professional presentation strategist who excels at organizing 
            information into clear, compelling narratives. You analyze provided research content 
            to identify key themes and create a logical presentation structure. You know how to 
            break down complex topics into digestible slides and ensure the presentation flows 
            naturally while maintaining audience engagement.""",
            verbose=True,
            allow_delegation=False,
            llm=getattr(self, "model_instance", self.model),
        )

    def content_creator_agent(self):
        """
        Content Creator Agent: Generates actual textual content for each slide based on the blueprint.
        """
        return Agent(
            role="Content Creator",
            goal="Generate engaging and relevant plain-text content for each slide based on the presentation plan",
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
            llm=self.model,
        )

    def designer_agent(self):
        """
        Designer Agent: Defines visual presentation, layout, and styling for each slide.
        """
        return Agent(
            role="Presentation Designer",
            goal="Create visually appealing and professional slide designs that enhance content delivery",
            backstory="""You are a professional presentation designer with extensive experience in 
            visual communication and graphic design. You understand color theory, typography, 
            layout principles, and how to create slides that are both beautiful and functional. 
            You know how to balance text and visuals, choose appropriate color schemes, and 
            create layouts that guide the viewer's attention effectively. Your designs always 
            maintain consistency and professionalism while being visually engaging.""",
            verbose=True,
            allow_delegation=False,
            llm=self.model,
        )


class PPTTasks:
    """
    Defines all the tasks that agents will perform in the PPT generation pipeline.
    """

    def research_task(self, agent, topic, num_slides):
        """
        Task for the Content Researcher Agent to gather and analyze web content.
        """
        # Ensure num_slides is an integer
        num_slides = int(num_slides) if isinstance(num_slides, str) else num_slides

        return Task(
            description=f"""
            You are a research agent. Your sole objective is to gather factual, structured information about the following topic:

            TOPIC: "{topic}"
            TARGET SLIDES: {num_slides}

            ---

            RESEARCH SCOPE:
            Investigate the following dimensions of "{topic}":
            - Origins and historical background
            - Key facts, milestones, and achievements
            - Current status and recent developments (as of your knowledge cutoff)
            - Broader impact, significance, and influence
            - Any notable figures, events, or data points closely associated with it

            ---

            OUTPUT: Return a single valid JSON object with this schema:

            {{
                "researched_topic": "{topic}",
                "main_themes": [
                    {{
                        "theme": "<theme title>",
                        "importance": <integer 1-10>,
                        "content": "<2-4 sentences of actual factual content about this theme>",
                        "key_points": ["<specific fact>", "<specific fact>", "<specific fact>"]
                    }}
                ],
                "key_facts": [
                    {{
                        "fact": "<a specific, verifiable fact about {topic}>",
                        "context": "<why this fact matters in the broader picture>",
                        "relevance": "<how this supports understanding {topic}>"
                    }}
                ],
                "suggested_slide_topics": [
                    "<slide title 1>",
                    "<slide title 2>"
                ]
            }}

            Generate exactly {num_slides} entries in suggested_slide_topics.
            All content must be factual and specific to "{topic}".
            Do not include meta-commentary, filler text, or template placeholders in the output.
            """,
            agent=agent,
            expected_output=f"Comprehensive factual research specifically about '{topic}'",
        )

    def planning_task(self, agent, research_result, num_slides):
        """
        Task for the Planner Agent to create presentation structure from research.
        """
        # Ensure num_slides is an integer
        num_slides = int(num_slides) if isinstance(num_slides, str) else num_slides

        return Task(
            description=f"""
            You are a presentation structure agent. Your job is to convert the research data below into a clean, slide-by-slide JSON structure.

            RESEARCH DATA:
            {research_result}

            ---

            TASK:
            Create a {num_slides}-slide presentation based strictly on the research data above.

            SLIDE STRUCTURE RULES:
            - Slide 1: Title/intro slide for the topic
            - Slides 2 to {num_slides - 1}: One slide per major theme or fact cluster from the research
            - Slide {num_slides}: Conclusion or summary slide

            CONTENT CONSTRAINTS:
            - Slide titles: 10 words or fewer
            - bullet_points type: 5 to 6 bullet points, each under 15 words
            - paragraph type: 40 to 50 words total
            - two_column type: 3 points per column, each under 12 words
            - Do not pad content. If a theme only supports 3 bullets, use 3.

            content_type must be exactly one of: "title_only", "bullet_points", "paragraph", "two_column"
            Assign content_type based on what best suits the slide's content, not randomly.

            ---

            OUTPUT: A single valid JSON object. No markdown, no commentary outside the JSON.

            {{
            "presentation_title": "<concise title derived from the topic>",
            "target_topic": "<exact topic from research data>",
            "total_slides": {num_slides},
            "slides": [
                {{
                    "slide_number": <integer>,
                    "title": "<slide title, max 10 words>",
                    "content_type": "<one of: title_only | bullet_points | paragraph | two_column>",
                    "research_theme": "<which theme from the research this slide covers>",
                    "content": {{
                        "bullet_points": ["<point>", "<point>"],
                        "paragraph": "<paragraph text if content_type is paragraph, else null>",
                        "columns": {{
                            "left": ["<point>", "<point>"],
                            "right": ["<point>", "<point>"]
                        }}
                    }}
                }}
            ]
            }}

            Populate only the content fields relevant to the chosen content_type. Set unused fields to null.
            Every slide must trace back to a specific theme or fact in the research data. Do not invent content.
            """,
            agent=agent,
            expected_output="Presentation structure based ONLY on the researched topic",
        )

    def content_creation_task(self, agent, planning_result, research_data):
        """
        Task for the Content Creator Agent to generate content for each slide based on research and planning.
        """
        return Task(
            description=f"""
                You are a slide content generation agent. Your job is to populate each slide with real content drawn strictly from the research data.

                PLANNING STRUCTURE:
                {planning_result}

                RESEARCH DATA:
                {research_data}

                ---

                RULES:
                - Use only facts and themes present in the research data
                - No markdown formatting — plain text only
                - No invented content, generic advice, or filler
                - Match content_type exactly as defined in the planning structure

                CONTENT CONSTRAINTS BY TYPE:
                - title_only: title only, no additional content fields needed
                - bullet_points: 3 to 6 bullets, each a single plain-text sentence under 12 words
                - paragraph: one block of plain text, 40 to 50 words
                - two_column: left and right arrays, 3 items each, each item under 12 words

                ---

                OUTPUT: Single valid JSON object, no markdown, no commentary.

                {{
                    "presentation_title": "<from planning structure, max 10 words>",
                    "slides": [
                        {{
                            "slide_number": <integer>,
                            "title": "<max 10 words, plain text>",
                            "content_type": "<must match planning: title_only | bullet_points | paragraph | two_column>",
                            "content": {{
                                "bullets": ["<point>", "<point>"] ,
                                "paragraph": "<paragraph text or null>",
                                "columns": {{
                                    "left": ["<point>", "<point>", "<point>"],
                                    "right": ["<point>", "<point>", "<point>"]
                                }}
                            }}
                        }}
                    ]
                }}

                Set unused content fields to null based on content_type.
                Do not add fields not present in this schema.
                Every piece of content must be traceable to a theme or fact in the research data.
                """,
            agent=agent,
            expected_output="Slide content based strictly on research data about the specific topic",
        )

    def design_task(self, agent, content_result, research_data):
        """
        Task for the Designer Agent to define visual styling and layout using research insights.
        """
        return Task(
            description=f"""
            You are a slide design agent. Your job is to assign concrete visual design specifications to each slide based on its content type and subject matter.

            SLIDE CONTENT:
            {content_result}

            ---

            RULES:
            - Assign a layout_type that matches the slide's content_type
            - Choose a color_theme from the allowed list only
            - Suggest visual_element only if the slide content contains a statistic, process, or comparison — otherwise set to null
            - Do not invent sources, citations, or data not present in the content

            ALLOWED VALUES:

            layout_type (pick one per slide):
            - "title_centered" — for title_only slides
            - "title_left_bullets_right" — for bullet_points slides
            - "full_text" — for paragraph slides
            - "two_column_equal" — for two_column slides

            color_theme (pick one for the whole presentation, based on topic domain):
            - "corporate_blue"    — business, finance, strategy
            - "deep_green"        — environment, health, science
            - "slate_gray"        — technology, engineering, AI
            - "warm_amber"        — culture, history, social topics
            - "academic_navy"     — research, academia, policy

            visual_element type (only if content justifies it):
            - "bar_chart" — for numerical comparisons
            - "timeline"  — for historical or sequential content
            - "icon_row"  — for listing 3–5 discrete concepts
            - "image_placeholder" — for slides needing visual context

            ---

            OUTPUT: Single valid JSON object, no markdown.

            {{
                "color_theme": "<one from allowed list>",
                "font_pairing": {{
                    "heading": "Montserrat",
                    "body": "Open Sans"
                }},
                "slides": [
                    {{
                        "slide_number": <integer>,
                        "layout_type": "<one from allowed list>",
                        "visual_element": {{
                            "type": "<one from allowed list or null>",
                            "placement": "top | bottom | left | right | null",
                            "purpose": "<one sentence describing what it visualizes>"
                        }}
                    }}
                ]
            }}

            Set visual_element to null if the slide content does not contain data, a process, or a comparison.
            font_pairing is global — apply the same fonts across all slides.
            Do not add fields not in this schema.
            """,
            agent=agent,
            expected_output="Complete JSON with content and comprehensive design specifications",
        )

    def presentation_generation_task(self, agent, design_result):
        """
        Task for the Presentation Generator Agent to create the final presentation.
        """
        return Task(
            description=f"""
You are a slide content agent. Your job is to select the right component type for each slide and extract the content into structured slots. You do not write HTML. You do not design layouts. You only decide what component fits the content and what the slot values are.

SLIDE CONTENT AND DESIGN DATA:
{design_result}

---

COMPONENT TYPES AND WHEN TO USE THEM:
- hero — Use for the opening slide, closing slide, or any section title slide. Content is a title, optional subtitle, optional short description.
- bullets_accented — Use when the slide has 3 to 6 distinct bullet points. Content is a title and a list of points.
- two_column_card — Use when the slide compares two things, lists pros and cons, or covers two distinct subtopics side by side.
- stat_highlight — Use when the slide contains numbers, percentages, metrics, counts, or any quantitative data. Content is 2 to 4 stat value/label pairs plus optional supporting points.
- quote_feature — Use when the slide features a key statement, mission, finding, or impactful idea that deserves full visual emphasis.
- timeline_simple — Use when the slide covers sequential steps, a process, a historical progression, or chronological events. Content is 3 to 5 steps.
- image_text_split — Use when the slide introduces a single concept, feature, or topic that benefits from a visual symbol alongside explanatory points. Pick a relevant emoji for the concept.
- full_text_card — Use when the slide content is primarily a single explanatory paragraph. Use this as a last resort only — prefer other components when possible.

SLOT RULES:
- Only include slots defined for the chosen component
- Never add extra fields not in the component's slot definition
- If a slot is marked optional and you have no content for it, set it to null
- All text values must be plain text — no HTML tags, no markdown
- For stat_highlight, value must be the actual number or metric as a string, label must be a short descriptive label
- For timeline_simple, number must be the step number as an integer, title must be short (3 to 5 words), description must be one sentence
- For image_text_split, visual_symbol must be a single emoji character that meaningfully represents the slide topic

SLOT DEFINITIONS:
hero: title, subtitle (optional), description (optional)
bullets_accented: title, points (list of 3-6 strings), footer_note (optional)
two_column_card: left_title, left_points (list), right_title, right_points (list), slide_title (optional)
stat_highlight: slide_title, stats (list of objects with "value" and "label"), supporting_points (optional list)
quote_feature: quote, attribution (optional), context (optional)
timeline_simple: slide_title, steps (list of objects with "number", "title", "description")
image_text_split: visual_symbol (single emoji), visual_label, title, points (list of 2-5 strings)
full_text_card: title, body (paragraph 40-80 words), highlight (optional single sentence)

DISTRIBUTION RULES:
- Slide 1 must always use hero
- No component type may be used more than 3 times across the whole presentation
- If the presentation has 8 or more slides, ensure at least 5 distinct component types are used
- The last slide should use hero or quote_feature

OUTPUT: Single valid JSON object, no markdown wrapper, no code fences, no triple backticks.

{{
    "color_theme": "<carry over from design_result>",
    "slides": [
        {{
            "slide_number": 1,
            "component": "hero",
            "slots": {{
                "title": "Slide title here",
                "subtitle": "Optional subtitle here",
                "description": null
            }}
        }},
        {{
            "slide_number": 2,
            "component": "bullets_accented",
            "slots": {{
                "title": "Slide title here",
                "points": ["Point one", "Point two", "Point three"],
                "footer_note": null
            }}
        }}
    ]
}}

Every slide must have slide_number, component, and slots. The slots object must match exactly the slot definition for the chosen component.
            """,
            agent=agent,
            expected_output="A single valid JSON object with color_theme and slides array, each slide having slide_number, component, and slots.",
        )


    @staticmethod
    def validate_content_length(content_data):
        """
        Validate that content adheres to length constraints.

        Args:
            content_data (dict): Content data with slides

        Returns:
            tuple: (is_valid, validation_errors)
        """
        errors = []

        # Check presentation title
        if "presentation_title" in content_data:
            title_words = len(content_data["presentation_title"].split())
            if title_words > 10:
                errors.append(
                    f"Presentation title too long: {title_words} words (max 10)"
                )

        # Check each slide
        if "slides" in content_data:
            for slide in content_data["slides"]:
                slide_num = slide.get("slide_number", "Unknown")

                # Check slide title
                if "title" in slide:
                    title_words = len(slide["title"].split())
                    if title_words > 10:
                        errors.append(
                            f"Slide {slide_num} title too long: {title_words} words (max 10)"
                        )

                # Check content based on type
                if "main_content" in slide and "content_type" in slide:
                    content = slide["main_content"]
                    content_type = slide["content_type"]

                    if content_type == "bullet_points":
                        # Count bullet points (assuming each line is a bullet)
                        bullet_count = len(
                            [line for line in content.split("\n") if line.strip()]
                        )
                        if bullet_count > 6:
                            errors.append(
                                f"Slide {slide_num} has too many bullet points: {bullet_count} (max 6)"
                            )

                    elif content_type == "paragraph":
                        # Count words in paragraph
                        word_count = len(content.split())
                        if word_count > 50:
                            errors.append(
                                f"Slide {slide_num} paragraph too long: {word_count} words (max 50)"
                            )

        return len(errors) == 0, errors


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
        logger.info(f"🚀 PPTCrew starting presentation creation for topic: '{topic}'")

        # Initialize agents
        researcher = self.agents.content_researcher_agent()
        planner = self.agents.planner_agent()
        content_creator = self.agents.content_creator_agent()
        designer = self.agents.designer_agent()
        generator = self.agents.presentation_generator_agent()

        # Ensure num_slides is an integer
        num_slides = style_preferences.get("num_slides", 5)
        num_slides = int(num_slides) if isinstance(num_slides, str) else num_slides
        logger.info(f"📊 Creating {num_slides} slides about: '{topic}'")

        # Research Phase: Gather and analyze web content
        logger.info(f"🔍 PHASE 1: Starting research for topic: '{topic}'")
        research_task = self.tasks.research_task(researcher, topic, num_slides)

        crew = Crew(
            agents=[researcher],
            tasks=[research_task],
            process=Process.sequential,
            verbose=True,
        )

        logger.info(f"🔍 Executing research phase for: '{topic}'")
        research_result = crew.kickoff()
        logger.info(f"✅ Research phase completed for: '{topic}'")

        # Planning Phase: Create structure based on research
        logger.info(f"📋 PHASE 2: Starting planning based on research about: '{topic}'")
        planning_task = self.tasks.planning_task(planner, research_result, num_slides)
        planning_task.context = [research_task]

        crew = Crew(
            agents=[planner],
            tasks=[planning_task],
            process=Process.sequential,
            verbose=True,
        )

        logger.info(f"📋 Executing planning phase for: '{topic}'")
        planning_result = crew.kickoff()
        logger.info(f"✅ Planning phase completed for: '{topic}'")

        # Content Creation Phase
        logger.info(f"✍️ PHASE 3: Creating content for: '{topic}'")
        content_task = self.tasks.content_creation_task(
            content_creator, planning_result, research_result
        )
        content_task.context = [planning_task, research_task]

        crew = Crew(
            agents=[content_creator],
            tasks=[content_task],
            process=Process.sequential,
            verbose=True,
        )

        logger.info(f"✍️ Executing content creation for: '{topic}'")
        content_result = crew.kickoff()
        logger.info(f"✅ Content creation completed for: '{topic}'")

        # Design Phase
        logger.info(f"🎨 PHASE 4: Designing presentation for: '{topic}'")
        design_task = self.tasks.design_task(designer, content_result, research_result)
        design_task.context = [content_task, research_task]

        crew = Crew(
            agents=[designer],
            tasks=[design_task],
            process=Process.sequential,
            verbose=True,
        )

        logger.info(f"🎨 Executing design phase for: '{topic}'")
        design_result = crew.kickoff()
        logger.info(f"✅ Design phase completed for: '{topic}'")

        # Generation Phase
        logger.info(f"🏗️ PHASE 5: Generating final presentation for: '{topic}'")
        generation_task = self.tasks.presentation_generation_task(
            generator, design_result
        )
        generation_task.context = [design_task]

        crew = Crew(
            agents=[generator],
            tasks=[generation_task],
            process=Process.sequential,
            verbose=True,
        )

        logger.info(f"🏗️ Executing final generation for: '{topic}'")
        final_result = crew.kickoff()
        logger.info(f"🎉 Presentation generation COMPLETED for: '{topic}'")
        import subprocess

        subprocess.run(
            [
                "notify-send",
                "--icon=dialog-information",
                "PPT Generator",
            ]
        )

        return final_result
