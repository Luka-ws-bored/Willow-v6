"""
Color Mood Mapper Plugin

A simple plugin for mapping colors to moods and emotions.
This plugin demonstrates the dynamic loading system in Willow v6.
"""

import logging

logger = logging.getLogger(__name__)

def map_color(mood: str) -> str:
    """
    Generate a HEX color code based on a mood description.
    (Placeholder logic — replace with color psychology algorithm.)
    """
    logger.info(f"Mapping mood to color for input: {mood}")
    # simple placeholder mapping
    mapping = {
        "sadness": "#4A4A4A",
        "happiness": "#FFD700",
        "calm": "#A3D5D3",
        "anger": "#FF4500",
    }
    for key, hexcode in mapping.items():
        if key in mood.lower():
            return hexcode
    return "#CCCCCC"  # default neutral gray

def map_color_to_mood(color: str) -> str:
    """
    Map a color to a corresponding mood or emotion.
    
    Args:
        color: The color to map (case-insensitive)
        
    Returns:
        The corresponding mood or 'neutral' if not found
    """
    color_mood_map = {
        'red': 'passionate',
        'blue': 'calm',
        'green': 'peaceful',
        'yellow': 'happy',
        'purple': 'mysterious',
        'orange': 'energetic',
        'pink': 'romantic',
        'black': 'serious',
        'white': 'pure',
        'gray': 'neutral'
    }
    return color_mood_map.get(color.lower(), 'neutral')

def get_mood_intensity(mood: str) -> str:
    """
    Get the intensity level of a mood.
    
    Args:
        mood: The mood to check
        
    Returns:
        The intensity level ('high', 'medium', 'low', or 'unknown')
    """
    intensity_map = {
        'passionate': 'high',
        'energetic': 'high',
        'happy': 'medium',
        'romantic': 'medium',
        'calm': 'low',
        'peaceful': 'low',
        'neutral': 'low',
        'serious': 'medium',
        'mysterious': 'medium',
        'pure': 'low'
    }
    return intensity_map.get(mood, 'unknown')

def analyze_color_palette(colors: list) -> dict:
    """
    Analyze a palette of colors and return mood insights.
    
    Args:
        colors: List of colors to analyze
        
    Returns:
        Dictionary with mood analysis results
    """
    if not colors:
        return {'error': 'No colors provided'}
    
    moods = [map_color_to_mood(color) for color in colors]
    intensities = [get_mood_intensity(mood) for mood in moods]
    
    # Count mood frequencies
    mood_counts = {}
    for mood in moods:
        mood_counts[mood] = mood_counts.get(mood, 0) + 1
    
    # Find dominant mood
    dominant_mood = max(mood_counts.items(), key=lambda x: x[1])[0] if mood_counts else 'neutral'
    
    return {
        'colors': colors,
        'moods': moods,
        'intensities': intensities,
        'mood_distribution': mood_counts,
        'dominant_mood': dominant_mood,
        'overall_intensity': 'high' if 'high' in intensities else 'medium' if 'medium' in intensities else 'low'
    }

# This is the entry point the plugin loader & CLI expect
def run(input_text: str) -> str:
    hexcode = map_color(input_text)
    return f"{hexcode}" 