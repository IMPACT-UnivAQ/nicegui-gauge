"""
Gauge module for NiceGUI - SVG Full implementation
Python-only gauge widgets without JavaScript dependencies
"""

from .gauge_svg_full import GaugeSVGFull

# Alias for backward compatibility
Gauge = GaugeSVGFull

__all__ = ['GaugeSVGFull', 'Gauge']

