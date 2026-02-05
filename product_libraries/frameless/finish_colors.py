"""
Finish Color Library System

Manages stain and paint colors for cabinet materials.
Colors are stored in two tiers:
  1. Built-in defaults (shipped with the addon, not editable)
  2. User custom colors (saved to %APPDATA%/home_builder_5/custom_colors.json)

Each color defines the two wood colors plus optional shader overrides
that get applied to the procedural wood material node group.
"""

import os
import json

# ============================================
# USER DATA FOLDER
# ============================================

def get_user_data_folder():
    """Get the user data folder for Home Builder 5.
    Creates it if it doesn't exist.
    Returns: path string (e.g. C:/Users/.../AppData/Roaming/home_builder_5/)
    """
    appdata = os.environ.get('APPDATA', os.path.expanduser('~'))
    folder = os.path.join(appdata, 'home_builder_5')
    if not os.path.exists(folder):
        os.makedirs(folder, exist_ok=True)
    return folder


def get_custom_colors_path():
    """Get the path to the user's custom colors JSON file."""
    return os.path.join(get_user_data_folder(), 'custom_colors.json')


# ============================================
# DEFAULT STAIN COLORS
# ============================================

DEFAULT_STAIN_COLORS = {
    'White': {
        'color_1': [0.806947, 0.752943, 0.679543, 1.0],
        'color_2': [0.806947, 0.752943, 0.679543, 1.0],
    },
    'Honey Wheat': {
        'color_1': [0.545725, 0.319560, 0.141263, 1.0],
        'color_2': [0.440175, 0.238398, 0.098899, 1.0],
    },
    'Golden Oak': {
        'color_1': [0.558337, 0.238398, 0.090842, 1.0],
        'color_2': [0.423265, 0.158961, 0.051270, 1.0],
    },
    'Provincial': {
        'color_1': [0.318547, 0.155926, 0.072271, 1.0],
        'color_2': [0.215861, 0.104616, 0.051270, 1.0],
    },
    'Special Walnut': {
        'color_1': [0.155926, 0.082085, 0.044522, 1.0],
        'color_2': [0.107023, 0.057805, 0.034340, 1.0],
    },
    'Classic Grey': {
        'color_1': [0.202503, 0.193292, 0.182563, 1.0],
        'color_2': [0.119111, 0.113844, 0.107702, 1.0],
    },
    'Espresso': {
        'color_1': [0.086500, 0.044522, 0.025187, 1.0],
        'color_2': [0.051270, 0.028426, 0.017642, 1.0],
    },
    'Chestnut': {
        'color_1': [0.155926, 0.068478, 0.034340, 1.0],
        'color_2': [0.086500, 0.051270, 0.038204, 1.0],
    },
    'Ebony': {
        'color_1': [0.025187, 0.017642, 0.015209, 1.0],
        'color_2': [0.038204, 0.028426, 0.023153, 1.0],
    },
    'Merlot': {
        'color_1': [0.119111, 0.031896, 0.031896, 1.0],
        'color_2': [0.082085, 0.023153, 0.028426, 1.0],
    },
    'Cabernet': {
        'color_1': [0.082085, 0.020289, 0.025187, 1.0],
        'color_2': [0.057805, 0.015209, 0.020289, 1.0],
    },
    'Navy': {
        'color_1': [0.023153, 0.034340, 0.068478, 1.0],
        'color_2': [0.017642, 0.025187, 0.051270, 1.0],
    },
    'Denim': {
        'color_1': [0.044522, 0.064803, 0.107023, 1.0],
        'color_2': [0.031896, 0.047366, 0.082085, 1.0],
    },
    'Evergreen': {
        'color_1': [0.025187, 0.044522, 0.028426, 1.0],
        'color_2': [0.017642, 0.034340, 0.020289, 1.0],
    },
    'Hunter Green': {
        'color_1': [0.034340, 0.057805, 0.034340, 1.0],
        'color_2': [0.023153, 0.041241, 0.025187, 1.0],
    },
}


# ============================================
# DEFAULT PAINT COLORS
# ============================================

DEFAULT_PAINT_COLORS = {
    'Arctic White': {
        'color_1': [0.871367, 0.871367, 0.871367, 1.0],
        'color_2': [0.871367, 0.871367, 0.871367, 1.0],
        'roughness': 0.3,
    },
    'Alabaster': {
        'color_1': [0.791298, 0.768151, 0.714618, 1.0],
        'color_2': [0.791298, 0.768151, 0.714618, 1.0],
        'roughness': 0.3,
    },
    'Agreeable Grey': {
        'color_1': [0.565097, 0.533277, 0.488166, 1.0],
        'color_2': [0.565097, 0.533277, 0.488166, 1.0],
        'roughness': 0.35,
    },
    'Iron Ore': {
        'color_1': [0.068478, 0.064803, 0.061246, 1.0],
        'color_2': [0.068478, 0.064803, 0.061246, 1.0],
        'roughness': 0.35,
    },
    'Naval': {
        'color_1': [0.031896, 0.047366, 0.072271, 1.0],
        'color_2': [0.031896, 0.047366, 0.072271, 1.0],
        'roughness': 0.3,
    },
    'Tricorn Black': {
        'color_1': [0.017642, 0.015209, 0.015209, 1.0],
        'color_2': [0.017642, 0.015209, 0.015209, 1.0],
        'roughness': 0.3,
    },
    'Sage Green': {
        'color_1': [0.291771, 0.318547, 0.278894, 1.0],
        'color_2': [0.291771, 0.318547, 0.278894, 1.0],
        'roughness': 0.35,
    },
    'Slate Blue': {
        'color_1': [0.215861, 0.250158, 0.304987, 1.0],
        'color_2': [0.215861, 0.250158, 0.304987, 1.0],
        'roughness': 0.35,
    },
    'Midnight Blue': {
        'color_1': [0.057805, 0.107023, 0.138432, 1.0],
        'color_2': [0.057805, 0.107023, 0.138432, 1.0],
        'roughness': 0.3,
    },
    'Forest': {
        'color_1': [0.035601, 0.043735, 0.028426, 1.0],
        'color_2': [0.035601, 0.043735, 0.028426, 1.0],
        'roughness': 0.35,
    },
    'Cranberry': {
        'color_1': [0.104616, 0.049707, 0.051269, 1.0],
        'color_2': [0.072271, 0.043735, 0.045186, 1.0],
        'roughness': 0.3,
    },
}


# ============================================
# COLOR DATA ACCESS
# ============================================

# Shader parameter defaults — used when a color doesn't override them
SHADER_DEFAULTS = {
    'roughness': 1.0,
    'noise_bump_strength': 0.1,
    'knots_bump_strength': 0.15,
    'wood_bump_strength': 0.2,
}


def _load_custom_colors():
    """Load user custom colors from JSON file.
    Returns dict with 'stain' and 'paint' keys, each containing color dicts.
    """
    path = get_custom_colors_path()
    if not os.path.exists(path):
        return {'stain': {}, 'paint': {}}
    try:
        with open(path, 'r') as f:
            data = json.load(f)
        # Validate structure
        if not isinstance(data, dict):
            return {'stain': {}, 'paint': {}}
        return {
            'stain': data.get('stain', {}),
            'paint': data.get('paint', {}),
        }
    except (json.JSONDecodeError, IOError):
        return {'stain': {}, 'paint': {}}


def _save_custom_colors(custom_data):
    """Save user custom colors to JSON file."""
    path = get_custom_colors_path()
    try:
        with open(path, 'w') as f:
            json.dump(custom_data, f, indent=2)
        return True
    except IOError:
        return False


def get_all_stain_colors():
    """Get all stain colors: defaults + user custom.
    Returns dict of {name: color_data}.
    User colors with same name override defaults.
    """
    colors = dict(DEFAULT_STAIN_COLORS)
    custom = _load_custom_colors()
    colors.update(custom.get('stain', {}))
    return colors


def get_all_paint_colors():
    """Get all paint colors: defaults + user custom.
    Returns dict of {name: color_data}.
    User colors with same name override defaults.
    """
    colors = dict(DEFAULT_PAINT_COLORS)
    custom = _load_custom_colors()
    colors.update(custom.get('paint', {}))
    return colors


def get_color_data(color_name, color_type='stain'):
    """Get full color data dict for a given color name.
    
    Args:
        color_name: Name of the color
        color_type: 'stain' or 'paint'
    
    Returns:
        dict with at minimum 'color_1' and 'color_2' keys,
        plus any shader overrides. Returns Natural/Arctic White fallback.
    """
    if color_type == 'paint':
        colors = get_all_paint_colors()
        fallback = DEFAULT_PAINT_COLORS.get('Arctic White', {
            'color_1': [0.871367, 0.871367, 0.871367, 1.0],
            'color_2': [0.871367, 0.871367, 0.871367, 1.0],
        })
    else:
        colors = get_all_stain_colors()
        fallback = DEFAULT_STAIN_COLORS.get('Natural', {
            'color_1': [0.806947, 0.752943, 0.679543, 1.0],
            'color_2': [0.806947, 0.752943, 0.679543, 1.0],
        })
    
    return colors.get(color_name, fallback)


def save_custom_color(name, color_data, color_type='stain'):
    """Save a custom color to the user library.
    
    Args:
        name: Color name
        color_data: dict with color_1, color_2, and optional shader overrides
        color_type: 'stain' or 'paint'
    """
    custom = _load_custom_colors()
    custom[color_type][name] = color_data
    return _save_custom_colors(custom)


def delete_custom_color(name, color_type='stain'):
    """Delete a custom color from the user library.
    Cannot delete built-in defaults.
    
    Returns True if deleted, False if not found or is a default.
    """
    defaults = DEFAULT_STAIN_COLORS if color_type == 'stain' else DEFAULT_PAINT_COLORS
    if name in defaults:
        return False  # Can't delete defaults
    
    custom = _load_custom_colors()
    if name in custom.get(color_type, {}):
        del custom[color_type][name]
        _save_custom_colors(custom)
        return True
    return False


def is_custom_color(name, color_type='stain'):
    """Check if a color is user-custom (not a built-in default)."""
    defaults = DEFAULT_STAIN_COLORS if color_type == 'stain' else DEFAULT_PAINT_COLORS
    if name in defaults:
        return False
    custom = _load_custom_colors()
    return name in custom.get(color_type, {})

