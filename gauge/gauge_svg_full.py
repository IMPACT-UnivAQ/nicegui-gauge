"""
GaugeSVGFull - SVG Complete Programmed Gauge for NiceGUI
Python-only implementation without JavaScript dependencies
"""

import base64
import os
import math
from typing import Optional
from nicegui import ui


class GaugeSVGFull:
    """
    Gauge widget using complete SVG generation in Python
    
    Generates full SVG markup with background PNG and rotating needle.
    No JavaScript required - pure Python/NiceGUI implementation.
    """
    
    def __init__(
        self,
        value: float = 0,
        min_value: float = 0,
        max_value: float = 100,
        label: str = 'Gauge',
        gauge_type: str = 'semicircular',  # 'circular' or 'semicircular'
        background_image: Optional[str] = None,  # Path to PNG background
        size: int = 220,  # Gauge size in pixels
        needle_color: str = '#000000',  # Needle color
        needle_length: float = 0.75,  # Needle length (0.0-1.0 of radius)
        show_value: bool = True,  # Show numeric value
        show_ticks: bool = True,  # Show tick marks
        tick_count: Optional[int] = None  # Number of tick marks (None -> sensible default)
    ):
        """
        Initialize gauge
        
        Args:
            value: Initial gauge value
            min_value: Minimum gauge value
            max_value: Maximum gauge value
            label: Label text below gauge
            gauge_type: 'circular' (360 gradi) or 'semicircular' (180 gradi)
            background_image: Path to PNG background image
            size: Gauge size in pixels
            needle_color: Needle color (hex)
            needle_length: Needle length as fraction of radius
            show_value: Show numeric value display
            show_ticks: Show tick marks
            tick_count: Number of tick marks
        """
        self._id = f'gauge_svg_{id(self)}'
        self._value = max(min_value, min(max_value, value))  # Clamp value
        self._min = min_value
        self._max = max_value
        self._label = label
        self._gauge_type = gauge_type
        self._size = size
        self._needle_color = needle_color
        self._needle_length = needle_length
        self._show_value = show_value
        self._show_ticks = show_ticks
        # Choose a sensible default number of divisions when not provided:
        # - semicircular: 12 segments -> 13 tick marks (0..360 every 30°)
        # - circular: 10 segments by default
        if tick_count is None:
            if gauge_type == 'semicircular':
                self._tick_count = 12
            else:
                self._tick_count = 10
        else:
            self._tick_count = tick_count
        self._background_image = background_image
        
        # Calculate gauge parameters
        self._center_x = size // 2
        self._center_y = size // 2
        self._radius = size // 2 - 20  # Leave margin
        
        # Determine angle range based on gauge type
        if gauge_type == 'circular':
            self._start_angle = 270  # Start from top
            self._angle_range = 360
            self._container_height = size + 30  # Extra space for label
        else:  # semicircular
            # Map numeric range across the semicircle so values go left->top->right.
            # Use a negative angle range so that:
            #   0   -> 180 (left),
            #   180 -> 90  (top),
            #   360 -> 0   (right)
            self._start_angle = 180  # Start from left
            self._angle_range = -180
            self._container_height = size // 2 + 30
        
        # Load background image as base64 if provided
        self._background_base64 = None
        if background_image and os.path.exists(background_image):
            with open(background_image, 'rb') as f:
                img_data = f.read()
                self._background_base64 = base64.b64encode(img_data).decode('utf-8')
        
        # Create UI container
        self.container = self._create_gauge_container()
    
    def _calculate_angle(self, value: float) -> float:
        """
        Calculate needle angle from value
        
        Args:
            value: Gauge value
            
        Returns:
            Angle in degrees
        """
        # Normalize value to 0-1 range
        normalized = (value - self._min) / (self._max - self._min)
        
        # Calculate angle
        angle = self._start_angle + (normalized * self._angle_range)
        
        return angle
    
    def _generate_needle_svg(self, angle: float) -> str:
        """
        Generate SVG for needle rotated at given angle
        
        Args:
            angle: Rotation angle in degrees
            
        Returns:
            SVG string for needle
        """
        # Calculate needle end point
        needle_radius = self._radius * self._needle_length

        # For semicircular heading gauges spanning 0..360, use standard
        # polar coordinates with 0°=right, positive CCW, and invert Y
        if self._gauge_type == 'semicircular' and (self._max - self._min) == 360:
            # angle is already computed so that 0->180, 180->90, 360->0
            rad = math.radians(angle)
            end_x = self._center_x + needle_radius * math.cos(rad)
            end_y = self._center_y - needle_radius * math.sin(rad)

            needle_svg = f'''
                <g id="{self._id}_needle">
                    <line x1="{self._center_x}" y1="{self._center_y}" 
                          x2="{end_x}" y2="{end_y}"
                          stroke="{self._needle_color}" 
                          stroke-width="4" 
                          stroke-linecap="round"/>
                    <circle cx="{self._center_x}" cy="{self._center_y}" 
                            r="6" 
                            fill="{self._needle_color}"/>
                </g>
            '''
        else:
            # Default behavior (keeps previous rotation-based drawing)
            angle_rad = math.radians(angle - 90)  # SVG uses 0 degrees at top
            end_x = self._center_x + needle_radius * math.cos(angle_rad)
            end_y = self._center_y + needle_radius * math.sin(angle_rad)

            needle_svg = f'''
                <g id="{self._id}_needle" transform="rotate({angle}, {self._center_x}, {self._center_y})">
                    <line x1="{self._center_x}" y1="{self._center_y}" 
                          x2="{self._center_x}" y2="{self._center_y - needle_radius}"
                          stroke="{self._needle_color}" 
                          stroke-width="4" 
                          stroke-linecap="round"/>
                    <circle cx="{self._center_x}" cy="{self._center_y}" 
                            r="6" 
                            fill="{self._needle_color}"/>
                </g>
            '''
        
        return needle_svg
    
    def _generate_tick_marks(self) -> str:
        """
        Generate SVG for tick marks
        
        Returns:
            SVG string for tick marks
        """
        if not self._show_ticks:
            return ''
        
        ticks_svg = []
        
        # Special-case: for semicircular heading gauges spanning 0..360,
        # generate ticks every 30° (0,30,...,360) to ensure correct placement
        if self._gauge_type == 'semicircular' and (self._max - self._min) == 360:
            tick_values = [self._min + i * 30 for i in range(0, 13)]
            iter_ticks = [(i, v) for i, v in enumerate(tick_values)]
            total_divs = 12
        else:
            iter_ticks = [(i, None) for i in range(self._tick_count + 1)]
            total_divs = self._tick_count

        for i, tick_val in iter_ticks:
            # Calculate angle for this tick
            if tick_val is None:
                normalized = i / total_divs
                value = self._min + (normalized * (self._max - self._min))
            else:
                value = tick_val
                normalized = (value - self._min) / (self._max - self._min)

            angle = self._start_angle + (normalized * self._angle_range)

            # Calculate tick positions. For semicircular 0..360 gauges use
            # conventional polar coordinates (0° = right, CCW positive).
            inner_radius = self._radius - 10
            outer_radius = self._radius

            if self._gauge_type == 'semicircular' and (self._max - self._min) == 360:
                # angle is already mapped (180..0), interpret as standard angle
                rad = math.radians(angle)
                x1 = self._center_x + inner_radius * math.cos(rad)
                y1 = self._center_y - inner_radius * math.sin(rad)
                x2 = self._center_x + outer_radius * math.cos(rad)
                y2 = self._center_y - outer_radius * math.sin(rad)
                angle_rad = rad
            else:
                angle_rad = math.radians(angle - 90)
                x1 = self._center_x + inner_radius * math.cos(angle_rad)
                y1 = self._center_y + inner_radius * math.sin(angle_rad)
                x2 = self._center_x + outer_radius * math.cos(angle_rad)
                y2 = self._center_y + outer_radius * math.sin(angle_rad)
            
            ticks_svg.append(
                f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" '
                f'stroke="#333" stroke-width="1"/>'
            )
            
            # Decide label interval so we show a reasonable number of labels
            # (aim for ~13 labels across the gauge). Compute label_step such
            # that for large tick_count we don't crowd labels.
            label_step = max(1, round(self._tick_count / 12))

            # Decide whether to show label for this tick
            if i % label_step == 0 or i == 0 or i == total_divs:
                # Place labels outside the outer arc for semicircular 0..360 gauges
                if self._gauge_type == 'semicircular' and (self._max - self._min) == 360:
                    label_radius = self._radius + 12
                    label_font = 11
                else:
                    label_radius = self._radius - 25
                    label_font = 10

                # For semicircular heading gauge we already computed angle_rad
                label_x = self._center_x + label_radius * math.cos(angle_rad)
                # Use inverted Y for semicircular polar math when applicable
                if self._gauge_type == 'semicircular' and (self._max - self._min) == 360:
                    label_y = self._center_y - label_radius * math.sin(angle_rad)
                else:
                    label_y = self._center_y + label_radius * math.sin(angle_rad)

                ticks_svg.append(
                    f'<text x="{label_x}" y="{label_y}" '
                    f'text-anchor="middle" dominant-baseline="middle" '
                    f'font-size="{label_font}" fill="#333" font-family="Arial, sans-serif">'
                    f'{value:.0f}</text>'
                )
        
        return '\n'.join(ticks_svg)
    
    def _generate_svg(self, angle: float) -> str:
        """
        Generate complete SVG markup
        
        Args:
            angle: Needle rotation angle in degrees
            
        Returns:
            Complete SVG string
        """
        # Determine SVG viewBox and height based on gauge type
        if self._gauge_type == 'circular':
            view_height = self._size
            svg_height = self._size
        else:  # semicircular
            view_height = self._size // 2
            svg_height = self._size // 2
        
        # Start SVG
        svg_parts = [
            f'<svg id="{self._id}_svg" '
            f'width="{self._size}" height="{svg_height}" '
            f'viewBox="0 0 {self._size} {view_height}" '
            f'xmlns="http://www.w3.org/2000/svg" '
            f'style="display: block;">'
        ]
        
        # Add background image if available
        if self._background_base64:
            svg_parts.append(
                f'<image x="0" y="0" width="{self._size}" height="{svg_height}" '
                f'href="data:image/png;base64,{self._background_base64}" '
                f'preserveAspectRatio="xMidYMid meet"/>'
            )
        else:
            # Draw simple background circle/arc if no image
            if self._gauge_type == 'circular':
                svg_parts.append(
                    f'<circle cx="{self._center_x}" cy="{self._center_y}" '
                    f'r="{self._radius}" '
                    f'fill="#f0f0f0" stroke="#ccc" stroke-width="2"/>'
                )
            else:  # semicircular
                svg_parts.append(
                    f'<path d="M {self._center_x - self._radius} {self._center_y} '
                    f'A {self._radius} {self._radius} 0 0 1 {self._center_x + self._radius} {self._center_y}" '
                    f'fill="#f0f0f0" stroke="#ccc" stroke-width="2"/>'
                )
        
        # Add tick marks
        if self._show_ticks:
            svg_parts.append(f'<g id="{self._id}_ticks">{self._generate_tick_marks()}</g>')
        
        # Add needle
        svg_parts.append(self._generate_needle_svg(angle))
        
        # Add value display
        if self._show_value:
            value_y = svg_height - 15 if self._gauge_type == 'semicircular' else self._center_y
            svg_parts.append(
                f'<text id="{self._id}_value" '
                f'x="{self._center_x}" y="{value_y}" '
                f'text-anchor="middle" dominant-baseline="middle" '
                f'font-size="16" font-weight="bold" fill="#333" '
                f'font-family="Arial, sans-serif">'
                f'{self._value:.1f}</text>'
            )
        
        # Close SVG
        svg_parts.append('</svg>')
        
        return '\n'.join(svg_parts)
    
    def _create_gauge_container(self):
        """
        Create NiceGUI container for gauge
        
        Returns:
            ui.html element containing gauge
        """
        initial_angle = self._calculate_angle(self._value)
        svg_content = self._generate_svg(initial_angle)
        
        html_content = f'''
            <div id="{self._id}_container" 
                 style="width: {self._size}px; height: {self._container_height}px; 
                        text-align: center; display: inline-block;">
                {svg_content}
                <div style="margin-top: 5px; font-size: 14px; font-weight: bold; color: #333;">
                    {self._label}
                </div>
            </div>
        '''
        
        return ui.html(html_content, sanitize=False)
    
    def set_value(self, value: float):
        """
        Update gauge value and rotate needle
        
        Args:
            value: New gauge value
        """
        # Clamp value to valid range
        self._value = max(self._min, min(self._max, value))
        
        # Calculate new angle
        angle = self._calculate_angle(self._value)
        
        # Update SVG needle rotation using JavaScript
        # This is minimal JS - only for updating transform attribute
        ui.run_javascript(f'''
            (function() {{
                const needle = document.getElementById('{self._id}_needle');
                const valueText = document.getElementById('{self._id}_value');
                
                if (needle) {{
                    needle.setAttribute('transform', 'rotate({angle}, {self._center_x}, {self._center_y})');
                }}
                
                if (valueText) {{
                    valueText.textContent = '{self._value:.1f}';
                }}
            }})();
        ''')
    
    @property
    def value(self) -> float:
        """Get current gauge value"""
        return self._value

