"""
Feather Icons Integration Module for Streamlit UI.
Provides lightweight vector SVG definitions, contextual coloring,
standard 24x24px dimensions, and 8px right margin alignment.
Complies with Feather Icons design language (stroke-width 2, round linecaps/joins).
"""

from typing import Optional, Dict

# Standard Contextual Color Palette
COLOR_PRIMARY = "#6B8E7D"   # Emerald green / Main brand actions / Primary
COLOR_CRITICAL = "#EF4444"  # Red / Urgent Leaks / Critical alerts
COLOR_WARNING = "#FF6B6B"   # Red / Urgent Leaks / Critical alerts
COLOR_SUCCESS = "#2ECC71"   # Green / Eco actions / CO2 reduction / Cost savings
COLOR_NEUTRAL = "#34495E"   # Dark slate / Headings / Default icons
COLOR_SECONDARY = "#95A5A6"  # Light slate / Inactive / Muted / Configuration
COLOR_INFO = "#3498DB"    # Blue / Help / Documentation / Information
COLOR_AMBER = "#F59E0B"    # Amber / Electricity / Quick fixes
COLOR_ORANGE = "#F97316"   # Orange / Transport / High priority

# Complete Vector SVG Inner Elements for Feather Icons
FEATHER_SVGS: Dict[str, str] = {
  # Core Requested Mappings
  "home": '<path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"></path><polyline points="9 22 9 12 15 12 15 22"></polyline>',
  "upload": '<path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path><polyline points="17 8 12 3 7 8"></polyline><line x1="12" y1="3" x2="12" y2="15"></line>',
  "pie-chart": '<path d="M21.21 15.89A10 10 0 1 1 8 2.83"></path><path d="M22 12A10 10 0 0 0 12 2v10z"></path>',
  "alert-triangle": '<path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path><line x1="12" y1="9" x2="12" y2="13"></line><line x1="12" y1="17" x2="12.01" y2="17"></line>',
  "lightbulb": '<line x1="9" y1="18" x2="15" y2="18"></line><line x1="10" y1="22" x2="14" y2="22"></line><path d="M15.09 14c.18-.98.65-1.74 1.41-2.5A4.65 4.65 0 0 0 18 8 6 6 0 0 0 6 8c0 1 .5 2.5 1.5 3.5.76.76 1.23 1.52 1.41 2.5h6.18z"></path>',
  "dollar-sign": '<line x1="12" y1="1" x2="12" y2="23"></line><path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"></path>',
  "leaf": '<path d="M11 20A7 7 0 0 1 9.8 6.1C15.5 5 17 4.48 19 2c1 2 2 4.18 2 8 0 5.5-4.78 10-10 10Z"></path><path d="M2 21c0-3 1.85-5.36 5.08-6C9.5 14.52 12 13 13 12"></path>',
  "sliders": '<line x1="4" y1="21" x2="4" y2="14"></line><line x1="4" y1="10" x2="4" y2="3"></line><line x1="12" y1="21" x2="12" y2="12"></line><line x1="12" y1="8" x2="12" y2="3"></line><line x1="20" y1="21" x2="20" y2="16"></line><line x1="20" y1="12" x2="20" y2="3"></line><line x1="1" y1="14" x2="7" y2="14"></line><line x1="9" y1="8" x2="15" y2="8"></line><line x1="17" y1="16" x2="23" y2="16"></line>',
  "check-list": '<path d="M9 11l3 3L22 4"></path><path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11"></path>',
  "calendar": '<rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect><line x1="16" y1="2" x2="16" y2="6"></line><line x1="8" y1="2" x2="8" y2="6"></line><line x1="3" y1="10" x2="21" y2="10"></line>',
  "truck": '<rect x="1" y="3" width="15" height="13"></rect><polygon points="16 8 20 8 23 11 23 16 16 16 16 8"></polygon><circle cx="5.5" cy="18.5" r="2.5"></circle><circle cx="18.5" cy="18.5" r="2.5"></circle>',
  "zap": '<polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"></polygon>',
  "trash-2": '<polyline points="3 6 5 6 21 6"></polyline><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path><line x1="10" y1="11" x2="10" y2="17"></line><line x1="14" y1="11" x2="14" y2="17"></line>',
  "settings": '<circle cx="12" cy="12" r="3"></circle><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"></path>',
  "download": '<path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path><polyline points="7 10 12 15 17 10"></polyline><line x1="12" y1="15" x2="12" y2="3"></line>',
  "help-circle": '<circle cx="12" cy="12" r="10"></circle><path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3"></path><line x1="12" y1="17" x2="12.01" y2="17"></line>',
  "columns": '<path d="M12 3h7a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2h-7m0-18H5a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h7m0-18v18"></path>',

  # Additional Feather Icons used in SaaS UI
  "droplet": '<path d="M12 2.69l5.66 5.66a8 8 0 1 1-11.31 0z"></path>',
  "check-square": '<polyline points="9 11 12 14 22 4"></polyline><path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11"></path>',
  "check-circle": '<path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path><polyline points="22 4 12 14.01 9 11.01"></polyline>',
  "check": '<polyline points="20 6 9 17 4 12"></polyline>',
  "clipboard": '<path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2"></path><rect x="8" y="2" width="8" height="4" rx="1" ry="1"></rect>',
  "list": '<line x1="8" y1="6" x2="21" y2="6"></line><line x1="8" y1="12" x2="21" y2="12"></line><line x1="8" y1="18" x2="21" y2="18"></line><line x1="3" y1="6" x2="3.01" y2="6"></line><line x1="3" y1="12" x2="3.01" y2="12"></line><line x1="3" y1="18" x2="3.01" y2="18"></line>',
  "user": '<path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path><circle cx="12" cy="7" r="4"></circle>',
  "users": '<path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path><circle cx="9" cy="7" r="4"></circle><path d="M23 21v-2a4 4 0 0 0-3-3.87"></path><path d="M16 3.13a4 4 0 0 1 0 7.75"></path>',
  "log-out": '<path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"></path><polyline points="16 17 21 12 16 7"></polyline><line x1="21" y1="12" x2="9" y2="12"></line>',
  "file-text": '<path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline><line x1="16" y1="13" x2="8" y2="13"></line><line x1="16" y1="17" x2="8" y2="17"></line><polyline points="10 9 9 9 8 9"></polyline>',
  "activity": '<polyline points="22 12 18 12 15 21 9 3 6 12 2 12"></polyline>',
  "sun": '<circle cx="12" cy="12" r="5"></circle><line x1="12" y1="1" x2="12" y2="3"></line><line x1="12" y1="21" x2="12" y2="23"></line><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"></line><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"></line><line x1="1" y1="12" x2="3" y2="12"></line><line x1="21" y1="12" x2="23" y2="12"></line><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"></line><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"></line>',
  "moon": '<path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"></path>',
  "lock": '<rect x="3" y="11" width="18" height="11" rx="2" ry="2"></rect><path d="M7 11V7a5 5 0 0 1 10 0v4"></path>',
  "globe": '<circle cx="12" cy="12" r="10"></circle><line x1="2" y1="12" x2="22" y2="12"></line><path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"></path>',
  "refresh-cw": '<polyline points="23 4 23 10 17 10"></polyline><polyline points="1 20 1 14 7 14"></polyline><path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"></path>',
  "trending-down": '<polyline points="23 18 13.5 8.5 8.5 13.5 1 6"></polyline><polyline points="17 18 23 18 23 12"></polyline>',
  "trending-up": '<polyline points="23 6 13.5 15.5 8.5 10.5 1 18"></polyline><polyline points="17 6 23 6 23 12"></polyline>',
  "search": '<circle cx="11" cy="11" r="8"></circle><line x1="21" y1="21" x2="16.65" y2="16.65"></line>',
  "filter": '<polygon points="22 3 2 3 10 12.46 10 19 14 21 14 12.46 22 3"></polygon>',
  "target": '<circle cx="12" cy="12" r="10"></circle><circle cx="12" cy="12" r="6"></circle><circle cx="12" cy="12" r="2"></circle>',
  "award": '<circle cx="12" cy="8" r="7"></circle><polyline points="8.21 13.89 7 23 12 20 17 23 15.79 13.88"></polyline>',
  "shield": '<path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path>',
  "box": '<path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"></path><polyline points="3.27 6.96 12 12.01 20.73 6.96"></polyline><line x1="12" y1="22.08" x2="12" y2="12"></line>',
  "arrow-right": '<line x1="5" y1="12" x2="19" y2="12"></line><polyline points="12 5 19 12 12 19"></polyline>',
  "arrow-left": '<line x1="19" y1="12" x2="5" y2="12"></line><polyline points="12 19 5 12 12 5"></polyline>',
  "thumbs-up": '<path d="M14 9V5a3 3 0 0 0-3-3l-4 9v11h11.28a2 2 0 0 0 2-1.7l1.38-9a2 2 0 0 0-2-2.3zM7 22H4a2 2 0 0 1-2-2v-7a2 2 0 0 1 2-2h3"></path>',
  "info": '<circle cx="12" cy="12" r="10"></circle><line x1="12" y1="16" x2="12" y2="12"></line><line x1="12" y1="8" x2="12.01" y2="8"></line>',
  "bar-chart-2": '<line x1="18" y1="20" x2="18" y2="10"></line><line x1="12" y1="20" x2="12" y2="4"></line><line x1="6" y1="20" x2="6" y2="14"></line>',
  "tool": '<path d="M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 7.94l-6.91 6.91a2.12 2.12 0 0 1-3-3l6.91-6.91a6 6 0 0 1 7.94-7.94l-3.76 3.76z"></path>',
  "repeat": '<polyline points="17 1 21 5 17 9"></polyline><path d="M3 11V9a4 4 0 0 1 4-4h14"></path><polyline points="7 23 3 19 7 15"></polyline><path d="M21 13v2a4 4 0 0 1-4 4H3"></path>',
  "user-check": '<path d="M16 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path><circle cx="8.5" cy="7" r="4"></circle><polyline points="17 11 19 13 23 9"></polyline>',
  "trending-up": '<polyline points="23 6 13.5 15.5 8.5 10.5 1 18"></polyline><polyline points="17 6 23 6 23 12"></polyline>',
  "trending-down": '<polyline points="23 18 13.5 8.5 8.5 13.5 1 6"></polyline><polyline points="17 18 23 18 23 12"></polyline>',
}

# Synonyms & Fallback Aliases
ALIASES = {
  "checklist": "check-list",
  "check_list": "check-list",
  "tasks": "check-list",
  "bulb": "lightbulb",
  "idea": "lightbulb",
  "eco": "leaf",
  "green": "leaf",
  "carbon": "leaf",
  "power": "zap",
  "energy": "zap",
  "fuel": "droplet",
  "diesel": "droplet",
  "gas": "droplet",
  "water": "droplet",
  "shipping": "truck",
  "transport": "truck",
  "waste": "trash-2",
  "garbage": "trash-2",
  "money": "dollar-sign",
  "cost": "dollar-sign",
  "savings": "dollar-sign",
  "chart": "pie-chart",
  "analytics": "bar-chart-2",
  "warning": "alert-triangle",
  "leak": "alert-triangle",
  "config": "settings",
  "export": "download",
  "help": "help-circle",
  "compare": "columns",
}


def feather_icon(
  icon_name: str,
  color: str = COLOR_NEUTRAL,
  size: int = 24,
  stroke_width: int = 2,
  margin_right: int = 8,
  class_name: str = "",
  extra_style: str = ""
) -> str:
  """
  Renders an authentic Feather Icon as an inline SVG HTML string.

  Args:
    icon_name: Name of the Feather icon (e.g. 'home', 'upload', 'zap', 'leaf')
    color: Hex color code (e.g. '#FF6B6B', '#2ECC71', '#34495E')
    size: Icon dimensions in pixels (default 24)
    stroke_width: Vector line stroke width (default 2)
    margin_right: Right margin spacing in pixels (default 8)
    class_name: Optional CSS class
    extra_style: Optional custom CSS rules

  Returns:
    HTML string containing embedded SVG ready for st.markdown(..., unsafe_allow_html=True)
  """
  clean_name = icon_name.strip().lower()
  resolved_name = ALIASES.get(clean_name, clean_name)
  svg_inner = FEATHER_SVGS.get(resolved_name)

  if not svg_inner:
    # Fallback to circle indicator if icon not found
    svg_inner = '<circle cx="12" cy="12" r="10"></circle>'

  margin_css = f"margin-right: {margin_right}px;" if margin_right > 0 else ""
  style_attr = f"display: inline-flex; align-items: center; justify-content: center; vertical-align: middle; line-height: 1; {margin_css} {extra_style}".strip()

  return (
    f'<span class="feather-icon-wrap {class_name}" style="{style_attr}">'
    f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" '
    f'viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="{stroke_width}" '
    f'stroke-linecap="round" stroke-linejoin="round" class="feather feather-{resolved_name}">'
    f'{svg_inner}'
    f'</svg>'
    f'</span>'
  )


def render_icon_heading(
  icon_name: str,
  title_text: str,
  level: str = "h2",
  color: Optional[str] = None,
  icon_size: int = 26,
  subtitle: Optional[str] = None,
  badge: Optional[str] = None,
  badge_class: str = "step-badge"
) -> str:
  """
  Renders a unified section header with an authentic Feather Icon aligned on the left (8px margin).

  Args:
    icon_name: Feather icon name
    title_text: Text title
    level: Header tag (h1, h2, h3, h4)
    color: Icon color (defaults contextually based on icon)
    icon_size: Icon size in pixels (default 26)
    subtitle: Optional subtitle description paragraph
    badge: Optional badge text to render alongside the title
    badge_class: CSS class for badge
  """
  if color is None:
    # Contextual default coloring based on intent
    if icon_name in ["alert-triangle"]:
      color = COLOR_WARNING
    elif icon_name in ["leaf", "check-list", "dollar-sign"]:
      color = COLOR_SUCCESS
    elif icon_name in ["zap"]:
      color = COLOR_AMBER
    elif icon_name in ["truck"]:
      color = COLOR_ORANGE
    elif icon_name in ["help-circle", "info"]:
      color = COLOR_INFO
    elif icon_name in ["settings", "calendar"]:
      color = COLOR_SECONDARY
    else:
      color = COLOR_NEUTRAL

  icon_svg = feather_icon(icon_name, color=color, size=icon_size, margin_right=8)
  badge_html = f'<span class="{badge_class}" style="margin-left: 12px; vertical-align: middle;">{badge}</span>' if badge else ""
  subtitle_html = f'<p style="font-size: 0.95rem; color: var(--text-muted); margin-top: 6px; margin-bottom: 0;">{subtitle}</p>' if subtitle else ""

  font_sizes = {
    "h1": "2.1rem",
    "h2": "1.85rem",
    "h3": "1.45rem",
    "h4": "1.15rem",
  }
  f_size = font_sizes.get(level, "1.85rem")

  return f"""
  <div style="margin-bottom: 20px;">
    <div style="display: flex; align-items: center; flex-wrap: wrap;">
      <{level} style="font-size: {f_size}; font-weight: 800; margin: 0; display: inline-flex; align-items: center; letter-spacing: -0.01em;">
        {icon_svg}
        <span>{title_text}</span>
      </{level}>
      {badge_html}
    </div>
    {subtitle_html}
  </div>
  """
