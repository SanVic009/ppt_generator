"""
Professional PowerPoint themes with comprehensive styling options.
Each theme includes color schemes, fonts, backgrounds, and layout preferences.
"""

from pptx.dml.color import RGBColor
from pptx.util import Pt
from dataclasses import dataclass
from typing import Dict, List, Tuple, Optional

@dataclass
class ColorScheme:
    """Color scheme for a theme"""
    primary: RGBColor
    secondary: RGBColor
    accent: RGBColor
    background_start: RGBColor
    background_end: RGBColor
    text_primary: RGBColor
    text_secondary: RGBColor
    text_light: RGBColor

@dataclass
class FontScheme:
    """Font scheme for a theme"""
    title_font: str
    content_font: str
    title_size: int
    subtitle_size: int
    content_size: int
    bullet_size: int

@dataclass
class ThemeConfig:
    """Complete theme configuration"""
    name: str
    display_name: str
    description: str
    color_scheme: ColorScheme
    font_scheme: FontScheme
    gradient_angle: int
    icon_style: str  # 'modern', 'classic', 'minimal', 'creative'
    layout_preference: str  # 'balanced', 'text_heavy', 'visual_focused'

class PPTThemes:
    """Professional PowerPoint themes collection"""
    
    @staticmethod
    def get_all_themes() -> Dict[str, ThemeConfig]:
        """Get all available themes"""
        return {
            'corporate_blue': PPTThemes._corporate_blue(),
            'modern_gradient': PPTThemes._modern_gradient(),
            'elegant_dark': PPTThemes._elegant_dark(),
            'nature_green': PPTThemes._nature_green(),
            'sunset_warm': PPTThemes._sunset_warm(),
            'ocean_depths': PPTThemes._ocean_depths(),
            'royal_purple': PPTThemes._royal_purple(),
            'minimalist_gray': PPTThemes._minimalist_gray(),
            'vibrant_orange': PPTThemes._vibrant_orange(),
            'tech_cyber': PPTThemes._tech_cyber(),
            'classic_academic': PPTThemes._classic_academic(),
            'creative_rainbow': PPTThemes._creative_rainbow(),
            'financial_gold': PPTThemes._financial_gold(),
            'healthcare_mint': PPTThemes._healthcare_mint(),
            'startup_energy': PPTThemes._startup_energy()
        }
    
    @staticmethod
    def get_theme(theme_name: str) -> Optional[ThemeConfig]:
        """Get a specific theme by name"""
        themes = PPTThemes.get_all_themes()
        return themes.get(theme_name)
    
    @staticmethod
    def get_theme_names() -> List[str]:
        """Get list of available theme names"""
        return list(PPTThemes.get_all_themes().keys())
    
    @staticmethod
    def get_theme_display_info() -> List[Dict]:
        """Get theme information for UI display"""
        themes = PPTThemes.get_all_themes()
        return [
            {
                'id': theme_id,
                'name': theme.display_name,
                'description': theme.description,
                'preview_colors': {
                    'primary': f"rgb({theme.color_scheme.primary[0]}, {theme.color_scheme.primary[1]}, {theme.color_scheme.primary[2]})",
                    'secondary': f"rgb({theme.color_scheme.secondary[0]}, {theme.color_scheme.secondary[1]}, {theme.color_scheme.secondary[2]})",
                    'accent': f"rgb({theme.color_scheme.accent[0]}, {theme.color_scheme.accent[1]}, {theme.color_scheme.accent[2]})"
                }
            }
            for theme_id, theme in themes.items()
        ]
    
    @staticmethod
    def _corporate_blue() -> ThemeConfig:
        """Professional corporate blue theme"""
        return ThemeConfig(
            name='corporate_blue',
            display_name='Corporate Blue',
            description='Professional and trustworthy with classic blue tones',
            color_scheme=ColorScheme(
                primary=RGBColor(13, 71, 161),      # Deep blue
                secondary=RGBColor(66, 165, 245),   # Light blue
                accent=RGBColor(255, 193, 7),       # Amber accent
                background_start=RGBColor(240, 248, 255),
                background_end=RGBColor(227, 242, 253),
                text_primary=RGBColor(33, 37, 41),
                text_secondary=RGBColor(108, 117, 125),
                text_light=RGBColor(255, 255, 255)
            ),
            font_scheme=FontScheme(
                title_font='Segoe UI Semibold',
                content_font='Segoe UI',
                title_size=36,
                subtitle_size=28,
                content_size=20,
                bullet_size=18
            ),
            gradient_angle=135,
            icon_style='classic',
            layout_preference='balanced'
        )
    
    @staticmethod
    def _modern_gradient() -> ThemeConfig:
        """Modern gradient theme with contemporary colors"""
        return ThemeConfig(
            name='modern_gradient',
            display_name='Modern Gradient',
            description='Contemporary design with smooth gradients and modern typography',
            color_scheme=ColorScheme(
                primary=RGBColor(102, 51, 153),     # Purple
                secondary=RGBColor(156, 39, 176),   # Deep purple
                accent=RGBColor(255, 87, 34),       # Orange accent
                background_start=RGBColor(248, 245, 255),
                background_end=RGBColor(240, 230, 255),
                text_primary=RGBColor(33, 33, 33),
                text_secondary=RGBColor(97, 97, 97),
                text_light=RGBColor(255, 255, 255)
            ),
            font_scheme=FontScheme(
                title_font='Segoe UI Light',
                content_font='Segoe UI',
                title_size=40,
                subtitle_size=26,
                content_size=19,
                bullet_size=17
            ),
            gradient_angle=45,
            icon_style='modern',
            layout_preference='visual_focused'
        )
    
    @staticmethod
    def _elegant_dark() -> ThemeConfig:
        """Elegant dark theme for sophisticated presentations"""
        return ThemeConfig(
            name='elegant_dark',
            display_name='Elegant Dark',
            description='Sophisticated dark theme with gold accents for premium feel',
            color_scheme=ColorScheme(
                primary=RGBColor(33, 37, 41),       # Dark gray
                secondary=RGBColor(52, 58, 64),     # Medium gray
                accent=RGBColor(255, 193, 7),       # Gold accent
                background_start=RGBColor(52, 58, 64),
                background_end=RGBColor(33, 37, 41),
                text_primary=RGBColor(248, 249, 250),
                text_secondary=RGBColor(206, 212, 218),
                text_light=RGBColor(255, 255, 255)
            ),
            font_scheme=FontScheme(
                title_font='Segoe UI',
                content_font='Segoe UI',
                title_size=38,
                subtitle_size=26,
                content_size=20,
                bullet_size=18
            ),
            gradient_angle=90,
            icon_style='minimal',
            layout_preference='text_heavy'
        )
    
    @staticmethod
    def _nature_green() -> ThemeConfig:
        """Nature-inspired green theme"""
        return ThemeConfig(
            name='nature_green',
            display_name='Nature Green',
            description='Fresh and natural with green tones, perfect for environmental topics',
            color_scheme=ColorScheme(
                primary=RGBColor(46, 125, 50),      # Forest green
                secondary=RGBColor(102, 187, 106),  # Light green
                accent=RGBColor(255, 167, 38),      # Orange accent
                background_start=RGBColor(248, 255, 248),
                background_end=RGBColor(232, 245, 233),
                text_primary=RGBColor(27, 94, 32),
                text_secondary=RGBColor(76, 175, 80),
                text_light=RGBColor(255, 255, 255)
            ),
            font_scheme=FontScheme(
                title_font='Segoe UI Semibold',
                content_font='Segoe UI',
                title_size=36,
                subtitle_size=28,
                content_size=20,
                bullet_size=18
            ),
            gradient_angle=120,
            icon_style='creative',
            layout_preference='balanced'
        )
    
    @staticmethod
    def _sunset_warm() -> ThemeConfig:
        """Warm sunset theme with orange and red tones"""
        return ThemeConfig(
            name='sunset_warm',
            display_name='Sunset Warm',
            description='Energetic warm tones inspired by sunset colors',
            color_scheme=ColorScheme(
                primary=RGBColor(230, 81, 0),       # Deep orange
                secondary=RGBColor(255, 138, 101),  # Light orange
                accent=RGBColor(244, 67, 54),       # Red accent
                background_start=RGBColor(255, 248, 225),
                background_end=RGBColor(255, 236, 179),
                text_primary=RGBColor(191, 54, 12),
                text_secondary=RGBColor(239, 108, 0),
                text_light=RGBColor(255, 255, 255)
            ),
            font_scheme=FontScheme(
                title_font='Segoe UI',
                content_font='Segoe UI',
                title_size=38,
                subtitle_size=28,
                content_size=20,
                bullet_size=18
            ),
            gradient_angle=60,
            icon_style='modern',
            layout_preference='visual_focused'
        )
    
    @staticmethod
    def _ocean_depths() -> ThemeConfig:
        """Deep ocean theme with blue-teal gradients"""
        return ThemeConfig(
            name='ocean_depths',
            display_name='Ocean Depths',
            description='Deep and calming ocean-inspired blues and teals',
            color_scheme=ColorScheme(
                primary=RGBColor(0, 77, 64),        # Deep teal
                secondary=RGBColor(0, 150, 136),    # Teal
                accent=RGBColor(255, 235, 59),      # Yellow accent
                background_start=RGBColor(224, 247, 250),
                background_end=RGBColor(178, 235, 242),
                text_primary=RGBColor(0, 77, 64),
                text_secondary=RGBColor(0, 121, 107),
                text_light=RGBColor(255, 255, 255)
            ),
            font_scheme=FontScheme(
                title_font='Segoe UI Light',
                content_font='Segoe UI',
                title_size=36,
                subtitle_size=26,
                content_size=19,
                bullet_size=17
            ),
            gradient_angle=180,
            icon_style='modern',
            layout_preference='balanced'
        )
    
    @staticmethod
    def _royal_purple() -> ThemeConfig:
        """Luxurious royal purple theme"""
        return ThemeConfig(
            name='royal_purple',
            display_name='Royal Purple',
            description='Luxurious and regal with deep purple and gold combinations',
            color_scheme=ColorScheme(
                primary=RGBColor(74, 20, 140),      # Deep purple
                secondary=RGBColor(142, 36, 170),   # Purple
                accent=RGBColor(255, 193, 7),       # Gold accent
                background_start=RGBColor(250, 245, 255),
                background_end=RGBColor(243, 229, 245),
                text_primary=RGBColor(74, 20, 140),
                text_secondary=RGBColor(123, 31, 162),
                text_light=RGBColor(255, 255, 255)
            ),
            font_scheme=FontScheme(
                title_font='Segoe UI Semibold',
                content_font='Segoe UI',
                title_size=38,
                subtitle_size=28,
                content_size=20,
                bullet_size=18
            ),
            gradient_angle=45,
            icon_style='classic',
            layout_preference='text_heavy'
        )
    
    @staticmethod
    def _minimalist_gray() -> ThemeConfig:
        """Clean minimalist gray theme"""
        return ThemeConfig(
            name='minimalist_gray',
            display_name='Minimalist Gray',
            description='Clean and simple design with subtle gray tones',
            color_scheme=ColorScheme(
                primary=RGBColor(97, 97, 97),       # Medium gray
                secondary=RGBColor(158, 158, 158),  # Light gray
                accent=RGBColor(33, 150, 243),      # Blue accent
                background_start=RGBColor(255, 255, 255),
                background_end=RGBColor(250, 250, 250),
                text_primary=RGBColor(33, 33, 33),
                text_secondary=RGBColor(97, 97, 97),
                text_light=RGBColor(255, 255, 255)
            ),
            font_scheme=FontScheme(
                title_font='Segoe UI Light',
                content_font='Segoe UI',
                title_size=36,
                subtitle_size=24,
                content_size=18,
                bullet_size=16
            ),
            gradient_angle=0,
            icon_style='minimal',
            layout_preference='text_heavy'
        )
    
    @staticmethod
    def _vibrant_orange() -> ThemeConfig:
        """Energetic vibrant orange theme"""
        return ThemeConfig(
            name='vibrant_orange',
            display_name='Vibrant Orange',
            description='Bold and energetic with vibrant orange and complementary colors',
            color_scheme=ColorScheme(
                primary=RGBColor(230, 81, 0),       # Vibrant orange
                secondary=RGBColor(255, 138, 101),  # Light orange
                accent=RGBColor(96, 125, 139),      # Blue gray accent
                background_start=RGBColor(255, 243, 224),
                background_end=RGBColor(255, 224, 178),
                text_primary=RGBColor(191, 54, 12),
                text_secondary=RGBColor(239, 108, 0),
                text_light=RGBColor(255, 255, 255)
            ),
            font_scheme=FontScheme(
                title_font='Segoe UI',
                content_font='Segoe UI',
                title_size=40,
                subtitle_size=30,
                content_size=22,
                bullet_size=20
            ),
            gradient_angle=45,
            icon_style='modern',
            layout_preference='visual_focused'
        )
    
    @staticmethod
    def _tech_cyber() -> ThemeConfig:
        """Modern tech/cyber theme"""
        return ThemeConfig(
            name='tech_cyber',
            display_name='Tech Cyber',
            description='Futuristic tech theme with neon accents and dark backgrounds',
            color_scheme=ColorScheme(
                primary=RGBColor(0, 188, 212),      # Cyan
                secondary=RGBColor(0, 150, 136),    # Teal
                accent=RGBColor(76, 175, 80),       # Green accent
                background_start=RGBColor(23, 28, 36),
                background_end=RGBColor(38, 50, 64),
                text_primary=RGBColor(224, 247, 250),
                text_secondary=RGBColor(178, 235, 242),
                text_light=RGBColor(255, 255, 255)
            ),
            font_scheme=FontScheme(
                title_font='Segoe UI',
                content_font='Segoe UI',
                title_size=38,
                subtitle_size=26,
                content_size=20,
                bullet_size=18
            ),
            gradient_angle=135,
            icon_style='modern',
            layout_preference='visual_focused'
        )
    
    @staticmethod
    def _classic_academic() -> ThemeConfig:
        """Traditional academic theme"""
        return ThemeConfig(
            name='classic_academic',
            display_name='Classic Academic',
            description='Traditional academic style with serif fonts and conservative colors',
            color_scheme=ColorScheme(
                primary=RGBColor(139, 69, 19),      # Saddle brown
                secondary=RGBColor(205, 133, 63),   # Peru
                accent=RGBColor(178, 34, 34),       # Fire brick
                background_start=RGBColor(255, 248, 220),
                background_end=RGBColor(250, 240, 210),
                text_primary=RGBColor(101, 67, 33),
                text_secondary=RGBColor(139, 69, 19),
                text_light=RGBColor(255, 255, 255)
            ),
            font_scheme=FontScheme(
                title_font='Times New Roman',
                content_font='Times New Roman',
                title_size=36,
                subtitle_size=26,
                content_size=20,
                bullet_size=18
            ),
            gradient_angle=90,
            icon_style='classic',
            layout_preference='text_heavy'
        )
    
    @staticmethod
    def _creative_rainbow() -> ThemeConfig:
        """Creative rainbow theme for artistic presentations"""
        return ThemeConfig(
            name='creative_rainbow',
            display_name='Creative Rainbow',
            description='Colorful and creative with rainbow gradients for artistic presentations',
            color_scheme=ColorScheme(
                primary=RGBColor(156, 39, 176),     # Purple
                secondary=RGBColor(103, 58, 183),   # Deep purple
                accent=RGBColor(255, 193, 7),       # Amber
                background_start=RGBColor(255, 240, 245),
                background_end=RGBColor(240, 230, 255),
                text_primary=RGBColor(74, 20, 140),
                text_secondary=RGBColor(123, 31, 162),
                text_light=RGBColor(255, 255, 255)
            ),
            font_scheme=FontScheme(
                title_font='Segoe UI',
                content_font='Segoe UI',
                title_size=38,
                subtitle_size=28,
                content_size=20,
                bullet_size=18
            ),
            gradient_angle=60,
            icon_style='creative',
            layout_preference='visual_focused'
        )
    
    @staticmethod
    def _financial_gold() -> ThemeConfig:
        """Professional financial theme with gold accents"""
        return ThemeConfig(
            name='financial_gold',
            display_name='Financial Gold',
            description='Professional financial theme with gold and dark blue for business presentations',
            color_scheme=ColorScheme(
                primary=RGBColor(13, 71, 161),      # Deep blue
                secondary=RGBColor(25, 118, 210),   # Blue
                accent=RGBColor(255, 193, 7),       # Gold
                background_start=RGBColor(250, 250, 250),
                background_end=RGBColor(245, 245, 245),
                text_primary=RGBColor(13, 71, 161),
                text_secondary=RGBColor(25, 118, 210),
                text_light=RGBColor(255, 255, 255)
            ),
            font_scheme=FontScheme(
                title_font='Segoe UI Semibold',
                content_font='Segoe UI',
                title_size=36,
                subtitle_size=26,
                content_size=20,
                bullet_size=18
            ),
            gradient_angle=135,
            icon_style='classic',
            layout_preference='balanced'
        )
    
    @staticmethod
    def _healthcare_mint() -> ThemeConfig:
        """Clean healthcare theme with mint and blue"""
        return ThemeConfig(
            name='healthcare_mint',
            display_name='Healthcare Mint',
            description='Clean and trustworthy healthcare theme with mint green and blue tones',
            color_scheme=ColorScheme(
                primary=RGBColor(0, 121, 107),      # Teal
                secondary=RGBColor(77, 182, 172),   # Light teal
                accent=RGBColor(33, 150, 243),      # Blue accent
                background_start=RGBColor(240, 253, 250),
                background_end=RGBColor(224, 247, 250),
                text_primary=RGBColor(0, 77, 64),
                text_secondary=RGBColor(0, 121, 107),
                text_light=RGBColor(255, 255, 255)
            ),
            font_scheme=FontScheme(
                title_font='Segoe UI',
                content_font='Segoe UI',
                title_size=36,
                subtitle_size=26,
                content_size=20,
                bullet_size=18
            ),
            gradient_angle=120,
            icon_style='modern',
            layout_preference='balanced'
        )
    
    @staticmethod
    def _startup_energy() -> ThemeConfig:
        """High-energy startup theme"""
        return ThemeConfig(
            name='startup_energy',
            display_name='Startup Energy',
            description='Dynamic and energetic theme perfect for startup pitches and innovation',
            color_scheme=ColorScheme(
                primary=RGBColor(244, 67, 54),      # Red
                secondary=RGBColor(255, 87, 34),    # Deep orange
                accent=RGBColor(255, 193, 7),       # Amber
                background_start=RGBColor(255, 245, 238),
                background_end=RGBColor(255, 224, 178),
                text_primary=RGBColor(183, 28, 28),
                text_secondary=RGBColor(244, 67, 54),
                text_light=RGBColor(255, 255, 255)
            ),
            font_scheme=FontScheme(
                title_font='Segoe UI',
                content_font='Segoe UI',
                title_size=40,
                subtitle_size=30,
                content_size=22,
                bullet_size=20
            ),
            gradient_angle=45,
            icon_style='modern',
            layout_preference='visual_focused'
        )
