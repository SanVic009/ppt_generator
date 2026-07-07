from themes import ThemeConfig

DEFAULT_SLOTS = {
    "hero": {
        "title": "Untitled Slide",
        "subtitle": None,
        "description": None
    },
    "bullets_accented": {
        "title": "Key Points",
        "points": ["No content provided"],
        "footer_note": None
    },
    "two_column_card": {
        "left_title": "Left Column",
        "left_points": ["No content"],
        "right_title": "Right Column",
        "right_points": ["No content"],
        "slide_title": None
    },
    "stat_highlight": {
        "slide_title": "Key Metrics",
        "stats": [{"value": "0", "label": "No Data"}],
        "supporting_points": []
    },
    "quote_feature": {
        "quote": "No quote provided",
        "attribution": None,
        "context": None
    },
    "timeline_simple": {
        "slide_title": "Timeline",
        "steps": [{"number": 1, "title": "Step 1", "description": "No description"}]
    },
    "image_text_split": {
        "visual_symbol": "✨",
        "visual_label": "Highlight",
        "title": "Topic",
        "points": ["No points provided"]
    },
    "full_text_card": {
        "title": "Details",
        "body": "No content provided.",
        "highlight": None
    }
}

def hero(slots, theme: ThemeConfig):
    title = slots['title']
    subtitle = slots['subtitle']
    description = slots['description']
    
    bg = f"linear-gradient({theme.gradient_angle}deg, {theme.color_scheme.background_start}, {theme.color_scheme.background_end})"
    
    subtitle_html = ""
    if subtitle:
        subtitle_html = f'<div style="color: {theme.color_scheme.secondary}; font-size: 2.5rem; margin-top: 20px;">{subtitle}</div>'
        
    desc_html = ""
    if description:
        desc_html = f'<div style="color: {theme.color_scheme.text_secondary}; font-size: 1.6rem; margin-top: 30px; max-width: 1000px; text-align: center; line-height: 1.5;">{description}</div>'
    
    return f"""
    <div style="width: 100%; height: 100%; display: flex; flex-direction: column; justify-content: center; align-items: center; background: {bg};">
        <h1 style="color: {theme.color_scheme.primary}; font-size: 5rem; font-weight: bold; font-family: {theme.font_scheme.title_font}; margin: 0; text-align: center;">{title}</h1>
        <div style="width: 80px; height: 6px; background-color: {theme.color_scheme.accent}; margin-top: 30px;"></div>
        {subtitle_html}
        {desc_html}
    </div>
    """

def bullets_accented(slots, theme: ThemeConfig):
    title = slots['title']
    points = slots['points']
    footer_note = slots['footer_note']
    
    points_html = ""
    if isinstance(points, list):
        for p in points:
            points_html += f"""
            <div style="display: flex; align-items: flex-start; margin-bottom: 25px;">
                <div style="width: 18px; height: 18px; border-radius: 50%; background-color: {theme.color_scheme.accent}; margin-top: 4px; margin-right: 20px; flex-shrink: 0;"></div>
                <div style="color: {theme.color_scheme.text_primary}; font-size: 1.8rem; line-height: 1.4;">{p}</div>
            </div>
            """
            
    footer_html = ""
    if footer_note:
        footer_html = f'<div style="position: absolute; bottom: 40px; right: 40px; color: {theme.color_scheme.text_secondary}; font-size: 1.2rem; font-style: italic;">{footer_note}</div>'
        
    return f"""
    <div style="width: 100%; height: 100%; display: flex; background-color: {theme.color_scheme.background_start}; position: relative;">
        <div style="width: 32%; height: 100%; background-color: {theme.color_scheme.primary}; display: flex; flex-direction: column; justify-content: center; padding: 60px; box-sizing: border-box;">
            <div style="color: {theme.color_scheme.text_light}; font-size: 2.8rem; font-family: {theme.font_scheme.title_font}; font-weight: bold;">{title}</div>
            <div style="width: 60px; height: 4px; background-color: {theme.color_scheme.accent}; margin-top: 20px;"></div>
        </div>
        <div style="width: 68%; height: 100%; background-color: #ffffff; padding: 80px 60px; box-sizing: border-box; display: flex; flex-direction: column; justify-content: center; position: relative;">
            <div style="max-width: 900px; width: 100%;">
                {points_html}
            </div>
            {footer_html}
        </div>
    </div>
    """

def two_column_card(slots, theme: ThemeConfig):
    slide_title = slots['slide_title']
    
    def render_list(items):
        html = ""
        if isinstance(items, list):
            for item in items:
                html += f"""
                <li style="color: {theme.color_scheme.text_primary}; font-size: 1.6rem; margin-bottom: 15px; display: flex; align-items: flex-start;">
                    <span style="display: inline-block; width: 10px; height: 10px; background-color: {theme.color_scheme.secondary}; margin-top: 8px; margin-right: 15px; flex-shrink: 0;"></span>
                    <span style="line-height: 1.4;">{item}</span>
                </li>
                """
        return f'<ul style="list-style-type: none; padding: 0; margin: 0;">{html}</ul>'
        
    title_html = ""
    if slide_title:
        title_html = f'<div style="color: {theme.color_scheme.primary}; font-size: 2.5rem; font-weight: bold; font-family: {theme.font_scheme.title_font}; text-align: center; margin-bottom: 30px; width: 100%;">{slide_title}</div>'
        
    return f"""
    <div style="width: 100%; height: 100%; display: flex; flex-direction: column; justify-content: center; align-items: center; padding: 60px; box-sizing: border-box; background-color: {theme.color_scheme.background_start};">
        {title_html}
        <div style="display: flex; width: 100%; max-width: 1600px; justify-content: space-between; gap: 40px; flex: 1; max-height: 800px;">
            <div style="flex: 1; background-color: #ffffff; border-radius: 20px; box-shadow: 0 10px 30px rgba(0,0,0,0.05); display: flex; flex-direction: column; overflow: hidden;">
                <div style="width: 100%; height: 8px; background-color: {theme.color_scheme.primary};"></div>
                <div style="padding: 40px; flex: 1; overflow-y: auto;">
                    <div style="color: {theme.color_scheme.primary}; font-size: 2rem; font-weight: bold; font-family: {theme.font_scheme.title_font}; margin-bottom: 30px;">{slots['left_title']}</div>
                    {render_list(slots['left_points'])}
                </div>
            </div>
            <div style="flex: 1; background-color: #ffffff; border-radius: 20px; box-shadow: 0 10px 30px rgba(0,0,0,0.05); display: flex; flex-direction: column; overflow: hidden;">
                <div style="width: 100%; height: 8px; background-color: {theme.color_scheme.accent};"></div>
                <div style="padding: 40px; flex: 1; overflow-y: auto;">
                    <div style="color: {theme.color_scheme.accent}; font-size: 2rem; font-weight: bold; font-family: {theme.font_scheme.title_font}; margin-bottom: 30px;">{slots['right_title']}</div>
                    {render_list(slots['right_points'])}
                </div>
            </div>
        </div>
    </div>
    """

def stat_highlight(slots, theme: ThemeConfig):
    slide_title = slots['slide_title']
    stats = slots['stats']
    supporting_points = slots['supporting_points']
    
    bg = f"linear-gradient({theme.gradient_angle}deg, {theme.color_scheme.background_start}, {theme.color_scheme.background_end})"
    
    stats_html = ""
    if isinstance(stats, list):
        for stat in stats:
            val = stat.get('value', '')
            label = stat.get('label', '')
            stats_html += f"""
            <div style="background-color: #ffffff; border-radius: 20px; padding: 50px; min-width: 280px; box-shadow: 0 10px 30px rgba(0,0,0,0.08); border-bottom: 4px solid {theme.color_scheme.primary}; display: flex; flex-direction: column; align-items: center; justify-content: center; text-align: center;">
                <div style="color: {theme.color_scheme.accent}; font-size: 5rem; font-weight: bold; font-family: {theme.font_scheme.title_font}; line-height: 1.1;">{val}</div>
                <div style="color: {theme.color_scheme.text_secondary}; font-size: 1.4rem; margin-top: 15px;">{label}</div>
            </div>
            """
            
    support_html = ""
    if isinstance(supporting_points, list) and len(supporting_points) > 0:
        pts = ""
        for p in supporting_points:
            pts += f"""
            <div style="display: flex; align-items: center; margin: 0 20px 20px 20px;">
                <span style="color: {theme.color_scheme.accent}; font-size: 1.6rem; margin-right: 10px; font-weight: bold;">&#10003;</span>
                <span style="color: {theme.color_scheme.text_primary}; font-size: 1.4rem;">{p}</span>
            </div>
            """
        support_html = f'<div style="display: flex; justify-content: center; flex-wrap: wrap; margin-top: 60px; width: 100%;">{pts}</div>'

    return f"""
    <div style="width: 100%; height: 100%; display: flex; flex-direction: column; justify-content: center; align-items: center; padding: 60px; box-sizing: border-box; background: {bg};">
        <h1 style="color: {theme.color_scheme.primary}; font-size: 3rem; font-weight: bold; font-family: {theme.font_scheme.title_font}; text-align: center; margin: 0 0 60px 0;">{slide_title}</h1>
        <div style="display: flex; justify-content: center; gap: 40px; flex-wrap: wrap; width: 100%;">
            {stats_html}
        </div>
        {support_html}
    </div>
    """

def quote_feature(slots, theme: ThemeConfig):
    quote = slots['quote']
    attribution = slots['attribution']
    context = slots['context']
    
    attr_html = ""
    if attribution:
        attr_html = f'<div style="color: {theme.color_scheme.accent}; font-size: 1.6rem; text-align: center; margin-top: 40px;">&mdash; {attribution}</div>'
        
    ctx_html = ""
    if context:
        ctx_html = f'<div style="color: {theme.color_scheme.text_secondary}; font-size: 1.4rem; text-align: center; margin-top: 20px;">{context}</div>'
        
    divider = ""
    if attribution or context:
        divider = f'<div style="width: 200px; height: 2px; background-color: {theme.color_scheme.accent}; opacity: 0.5; margin: 40px auto 0 auto;"></div>'
        
    return f"""
    <div style="width: 100%; height: 100%; background-color: {theme.color_scheme.primary}; position: relative; display: flex; flex-direction: column; justify-content: center; align-items: center; padding: 80px; box-sizing: border-box;">
        <div style="position: absolute; top: 60px; left: 80px; font-size: 12rem; color: {theme.color_scheme.accent}; opacity: 0.4; font-family: serif; line-height: 1;">&ldquo;</div>
        <div style="color: {theme.color_scheme.text_light}; font-size: 3rem; text-align: center; line-height: 1.6; max-width: 1200px; z-index: 2; font-family: {theme.font_scheme.title_font};">{quote}</div>
        {divider}
        {attr_html}
        {ctx_html}
    </div>
    """

def timeline_simple(slots, theme: ThemeConfig):
    slide_title = slots['slide_title']
    steps = slots['steps']
    
    steps_html = ""
    if isinstance(steps, list) and len(steps) > 0:
        for step in steps:
            num = step.get('number', '')
            title = step.get('title', '')
            desc = step.get('description', '')
            
            steps_html += f"""
            <div style="display: flex; flex-direction: column; align-items: center; position: relative; z-index: 2; flex: 1;">
                <div style="width: 80px; height: 80px; border-radius: 50%; background-color: {theme.color_scheme.accent}; color: {theme.color_scheme.text_light}; font-size: 2rem; font-weight: bold; display: flex; justify-content: center; align-items: center; margin-bottom: 20px;">{num}</div>
                <div style="color: {theme.color_scheme.primary}; font-size: 1.6rem; font-weight: bold; text-align: center; font-family: {theme.font_scheme.title_font};">{title}</div>
                <div style="color: {theme.color_scheme.text_secondary}; font-size: 1.3rem; text-align: center; max-width: 200px; margin-top: 10px; line-height: 1.4;">{desc}</div>
            </div>
            """
            
    return f"""
    <div style="width: 100%; height: 100%; background-color: {theme.color_scheme.background_start}; padding: 80px; box-sizing: border-box; display: flex; flex-direction: column; justify-content: center;">
        <h1 style="color: {theme.color_scheme.primary}; font-size: 3rem; font-weight: bold; font-family: {theme.font_scheme.title_font}; text-align: center; margin: 0 0 100px 0;">{slide_title}</h1>
        <div style="position: relative; width: 100%; max-width: 1400px; margin: 0 auto;">
            <div style="position: absolute; top: 40px; left: 5%; right: 5%; height: 3px; background-color: {theme.color_scheme.secondary}; z-index: 1;"></div>
            <div style="display: flex; justify-content: space-between; width: 100%;">
                {steps_html}
            </div>
        </div>
    </div>
    """

def image_text_split(slots, theme: ThemeConfig):
    visual_symbol = slots['visual_symbol']
    visual_label = slots['visual_label']
    title = slots['title']
    points = slots['points']
    
    bg = f"linear-gradient({theme.gradient_angle}deg, {theme.color_scheme.primary}, {theme.color_scheme.secondary})"
    
    points_html = ""
    if isinstance(points, list):
        for p in points:
            points_html += f"""
            <div style="display: flex; align-items: flex-start; margin-bottom: 25px;">
                <div style="width: 12px; height: 12px; border-radius: 50%; background-color: {theme.color_scheme.accent}; margin-top: 8px; margin-right: 20px; flex-shrink: 0;"></div>
                <div style="color: {theme.color_scheme.text_primary}; font-size: 1.7rem; line-height: 1.6;">{p}</div>
            </div>
            """
            
    return f"""
    <div style="width: 100%; height: 100%; display: flex;">
        <div style="width: 40%; height: 100%; background: {bg}; display: flex; flex-direction: column; justify-content: center; align-items: center; padding: 40px; box-sizing: border-box;">
            <div style="font-size: 10rem; line-height: 1;">{visual_symbol}</div>
            <div style="color: {theme.color_scheme.text_light}; font-size: 1.8rem; font-weight: bold; font-family: {theme.font_scheme.title_font}; text-align: center; margin-top: 30px;">{visual_label}</div>
        </div>
        <div style="width: 60%; height: 100%; background-color: #ffffff; padding: 60px 80px; display: flex; flex-direction: column; justify-content: center; box-sizing: border-box;">
            <h1 style="color: {theme.color_scheme.primary}; font-size: 3rem; font-weight: bold; font-family: {theme.font_scheme.title_font}; margin: 0 0 30px 0;">{title}</h1>
            <div style="width: 80px; height: 4px; background-color: {theme.color_scheme.accent}; margin-bottom: 40px;"></div>
            <div style="max-width: 800px;">
                {points_html}
            </div>
        </div>
    </div>
    """

def full_text_card(slots, theme: ThemeConfig):
    title = slots['title']
    body = slots['body']
    highlight = slots['highlight']
    
    hl_html = ""
    if highlight:
        hl_html = f"""
        <div style="background-color: {theme.color_scheme.background_end}; border-left: 6px solid {theme.color_scheme.primary}; padding: 25px; margin-top: 40px;">
            <div style="color: {theme.color_scheme.primary}; font-size: 1.6rem; font-style: italic; line-height: 1.5;">{highlight}</div>
        </div>
        """
        
    return f"""
    <div style="width: 100%; height: 100%; background-color: {theme.color_scheme.background_start}; padding: 80px; display: flex; justify-content: center; align-items: center; box-sizing: border-box;">
        <div style="max-width: 1400px; width: 100%; background-color: #ffffff; padding: 60px 80px; border-radius: 20px; box-shadow: 0 15px 40px rgba(0,0,0,0.08); border-top: 8px solid {theme.color_scheme.accent};">
            <h1 style="color: {theme.color_scheme.primary}; font-size: 3.5rem; font-weight: bold; font-family: {theme.font_scheme.title_font}; margin: 0 0 30px 0;">{title}</h1>
            <div style="color: {theme.color_scheme.text_primary}; font-size: 1.8rem; line-height: 1.8; text-align: justify;">{body}</div>
            {hl_html}
        </div>
    </div>
    """

def get_component_html(component_name: str, slots: dict, theme: ThemeConfig) -> str:
    """
    Dispatcher function to map a component name and slot data into fully styled HTML.
    Never raises an exception, falls back to full_text_card with safe defaults.
    """
    if not isinstance(slots, dict):
        slots = {}
        
    if component_name not in DEFAULT_SLOTS:
        component_name = "full_text_card"
        
    defaults = DEFAULT_SLOTS[component_name]
    merged_slots = {}
    
    for k, v in defaults.items():
        if k in slots and slots[k] is not None:
            merged_slots[k] = slots[k]
        else:
            merged_slots[k] = v

    if component_name == "hero":
        return hero(merged_slots, theme)
    elif component_name == "bullets_accented":
        return bullets_accented(merged_slots, theme)
    elif component_name == "two_column_card":
        return two_column_card(merged_slots, theme)
    elif component_name == "stat_highlight":
        return stat_highlight(merged_slots, theme)
    elif component_name == "quote_feature":
        return quote_feature(merged_slots, theme)
    elif component_name == "timeline_simple":
        return timeline_simple(merged_slots, theme)
    elif component_name == "image_text_split":
        return image_text_split(merged_slots, theme)
    elif component_name == "full_text_card":
        return full_text_card(merged_slots, theme)
        
    return full_text_card(merged_slots, theme)
