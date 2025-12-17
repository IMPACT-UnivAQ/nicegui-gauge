"""
GaugeSVGFull - SVG Complete Programmed Gauge for NiceGUI
Python-only implementation without JavaScript dependencies
"""

import base64
import os
import math
from typing import Optional, List, Tuple
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
        tick_count: Optional[int] = None,  # Number of tick marks (None -> sensible default)
        angle_map: Optional[List[Tuple[float, float]]] = None,
        angle_center: Optional[float] = None,
        angle_span: Optional[float] = None,
        counter_clockwise: bool = False
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
        # Optional advanced angle mapping
       #self._counter_clockwise = bool(counter_clockwise)
       #self._angle_center = angle_center
       #self._angle_span = angle_span

        if angle_map:
            self._angle_map = sorted(angle_map, key=lambda t: t[0])
        else:
            self._angle_map = None

        # If angle_span provided and no explicit map, build symmetric mapping
        if self._angle_map is None and (self._angle_span is not None):
            half = float(self._angle_span) / 2.0
            if self._angle_center is not None:
                self._angle_map = [
                    (self._min, -half),
                    (self._angle_center, 0.0),
                    (self._max, half),
                ]
            else:
                self._angle_map = [
                    (self._min, -half),
                    (self._max, half),
                ]
            self._angle_map = sorted(self._angle_map, key=lambda t: t[0])
        
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
        
        # Automatically enable colored zones for common speed gauges (0-100)
        # If the caller wants to control this explicitly, they can set
        # `self._colored_zones` after construction.
        self._colored_zones = (self._min == 0 and self._max == 100)

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
        # If an explicit piecewise angle_map is provided, use linear interpolation
        if getattr(self, '_angle_map', None):
            m = self._angle_map
            # If only one point provided, return its angle
            if len(m) == 1:
                return float(m[0][1])

            # below first point -> extrapolate using first segment
            if value <= m[0][0]:
                x0, y0 = m[0]
                x1, y1 = m[1]
                if x1 == x0:
                    return float(y0)
                t = (value - x0) / (x1 - x0)
                return float(y0 + t * (y1 - y0))

            # above last point -> extrapolate using last segment
            if value >= m[-1][0]:
                x0, y0 = m[-2]
                x1, y1 = m[-1]
                if x1 == x0:
                    return float(y1)
                t = (value - x0) / (x1 - x0)
                return float(y0 + t * (y1 - y0))

            # find segment containing value
            for i in range(len(m) - 1):
                x0, y0 = m[i]
                x1, y1 = m[i + 1]
                if x0 <= value <= x1:
                    if x1 == x0:
                        return float(y0)
                    t = (value - x0) / (x1 - x0)
                    return float(y0 + t * (y1 - y0))

        # Default behavior: Normalize value to 0-1 range and map to start+range
        normalized = (value - self._min) / (self._max - self._min)
        angle_range = self._angle_range * (-1 if self._counter_clockwise else 1)
        angle = self._start_angle + (normalized * angle_range)
        return float(angle)
    
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
        
        # If an explicit angle_map is provided, draw ticks only at those map points
        # that fall within the numeric range [min, max]. Also add minor ticks
        # between consecutive mapped major ticks (9 minor ticks between majors).
        if getattr(self, '_angle_map', None):
            # Keep only mapped values inside the numeric range
            majors = [pt[0] for pt in self._angle_map if (self._min <= pt[0] <= self._max)]
            majors = sorted(set(majors))

            # If after filtering there are no mapped points inside range, don't draw any ticks
            if not majors:
                return ''

            # Parameters for minor ticks
            minor_between = 9  # number of minor ticks between each pair of major ticks

            seen_angles = set()

            for idx, value in enumerate(majors):
                angle = self._calculate_angle(value)

                # Deduplicate by angle
                ang_key = round(float(angle), 6)
                if ang_key in seen_angles:
                    continue
                seen_angles.add(ang_key)

                # Major tick positions
                inner_radius = self._radius - 10
                outer_radius = self._radius

                if self._gauge_type == 'semicircular' and (self._max - self._min) == 360:
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

                # Label for major tick
                label_radius = self._radius - 25
                label_font = 10
                label_x = self._center_x + label_radius * math.cos(angle_rad)
                if self._gauge_type == 'semicircular' and (self._max - self._min) == 360:
                    label_y = self._center_y - label_radius * math.sin(angle_rad)
                else:
                    label_y = self._center_y + label_radius * math.sin(angle_rad)

                ticks_svg.append(
                    f'<text x="{label_x}" y="{label_y}" '
                    f'text-anchor="middle" dominant-baseline="middle" '
                    f'font-size="{label_font}" font-weight="300" fill="#333" font-family="Arial, sans-serif">'
                    f'{value:.0f}</text>'
                )

                # Generate minor ticks between this major and the next major
                if idx < len(majors) - 1:
                    v0 = value
                    v1 = majors[idx + 1]
                    for j in range(1, minor_between + 1):
                        t = j / (minor_between + 1)
                        v_minor = v0 + t * (v1 - v0)
                        a_minor = self._calculate_angle(v_minor)
                        ang_key_m = round(float(a_minor), 6)
                        if ang_key_m in seen_angles:
                            continue
                        seen_angles.add(ang_key_m)

                        inner_minor = self._radius - 6
                        outer_minor = self._radius

                        if self._gauge_type == 'semicircular' and (self._max - self._min) == 360:
                            rad_m = math.radians(a_minor)
                            mx1 = self._center_x + inner_minor * math.cos(rad_m)
                            my1 = self._center_y - inner_minor * math.sin(rad_m)
                            mx2 = self._center_x + outer_minor * math.cos(rad_m)
                            my2 = self._center_y - outer_minor * math.sin(rad_m)
                        else:
                            rad_m = math.radians(a_minor - 90)
                            mx1 = self._center_x + inner_minor * math.cos(rad_m)
                            my1 = self._center_y + inner_minor * math.sin(rad_m)
                            mx2 = self._center_x + outer_minor * math.cos(rad_m)
                            my2 = self._center_y + outer_minor * math.sin(rad_m)

                        ticks_svg.append(
                            f'<line x1="{mx1}" y1="{my1}" x2="{mx2}" y2="{my2}" '
                            f'stroke="#666" stroke-width="0.8"/>'
                        )

            return '\n'.join(ticks_svg)

        # Special-case: for semicircular heading gauges spanning 0..360,
        # generate ticks every 30° (0,30,...,360) to ensure correct placement
        elif self._gauge_type == 'semicircular' and (self._max - self._min) == 360:
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

            # Determine angle using mapping if present
            angle = self._calculate_angle(value)

            # Skip ticks for values outside numeric range (guard against
            # mapped points that accidentally lie outside [min,max]).
            if value < self._min or value > self._max:
                continue

            # Deduplicate ticks that land on the same angle (avoid mapped
            # tick drawing on top of default tick). Use rounded angle key.
            if 'seen_angles' not in locals():
                seen_angles = set()
            ang_key = round(float(angle), 6)
            if ang_key in seen_angles:
                continue
            seen_angles.add(ang_key)

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
            # (aim for ~13 labels across the gauge). Use `total_divs` so that
            # custom angle_map sizes are respected.
            label_step = max(1, round(total_divs / 12))

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
                    f'font-size="{label_font}" font-weight="300" fill="#333" font-family="Arial, sans-serif">'
                    f'{value:.0f}</text>'
                )
        
        return '\n'.join(ticks_svg)

    def _generate_colored_zones(self) -> str:
        """
        Generate colored arc segments (zones) for speed-style gauges.

        Returns:
            SVG string for colored arc segments
        """
        if not self._colored_zones:
            return ''

        # Define zones as (start_value, end_value, color)
        zones = [
            (0.9, 30,'#2ecc71'),
            (31, 50, '#f1c40f'),
            (51, 90, "#f96a0b"),
            (91, 99, "#d51d08"),
        ]

        parts = []

        # Stroke thickness for zone band
        stroke_w = 12

        for start_v, end_v, color in zones:
            # Use _calculate_angle so colored zones follow any provided angle_map
            a0 = self._calculate_angle(start_v)
            a1 = self._calculate_angle(end_v)

            # Convert to radians for path coords. Use same convention as tick marks
            # which uses angle_rad = radians(angle - 90)
            r = self._radius
            angle0 = math.radians(a0 - 90)
            angle1 = math.radians(a1 - 90)

            x0 = self._center_x + r * math.cos(angle0)
            y0 = self._center_y + r * math.sin(angle0)
            x1 = self._center_x + r * math.cos(angle1)
            y1 = self._center_y + r * math.sin(angle1)

            # Determine large-arc-flag based on angular span
            span_deg = (a1 - a0)
            large_arc = '1' if abs(span_deg) > 180 else '0'

            # Sweep flag: SVG arc uses 0 = CCW, 1 = CW when using standard coords.
            sweep = '1' if span_deg > 0 else '0'

            parts.append(
                f'<path d="M {x0} {y0} A {r} {r} 0 {large_arc} {sweep} {x1} {y1}" '
                f'stroke="{color}" stroke-width="{stroke_w}" fill="none" stroke-linecap="round"/>'
            )

        return '\n'.join(parts)
    
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
        
        # Add colored zones (if enabled) and tick marks
        zones_svg = ''
        if self._colored_zones:
            zones_svg = self._generate_colored_zones()
        if zones_svg:
            svg_parts.append(f'<g id="{self._id}_zones">{zones_svg}</g>')

        # If the caller provided an angle_map, draw a solid arc connecting the
        # major mapped tick positions to form a frame for the displayed range.
        if getattr(self, '_angle_map', None):
            majors = [pt[0] for pt in self._angle_map if (self._min <= pt[0] <= self._max)]
            majors = sorted(set(majors))
            if majors:
                arc_radius = self._radius + 6
                arc_w = 2
                # Draw a smooth circular arc between the first and last major
                # tick using the same convention as colored zones.
                a0 = self._calculate_angle(majors[0])
                a1 = self._calculate_angle(majors[-1])

                if self._gauge_type == 'semicircular' and (self._max - self._min) == 360:
                    angle0 = math.radians(a0)
                    angle1 = math.radians(a1)
                    x0 = self._center_x + arc_radius * math.cos(angle0)
                    y0 = self._center_y - arc_radius * math.sin(angle0)
                    x1 = self._center_x + arc_radius * math.cos(angle1)
                    y1 = self._center_y - arc_radius * math.sin(angle1)
                else:
                    angle0 = math.radians(a0 - 90)
                    angle1 = math.radians(a1 - 90)
                    x0 = self._center_x + arc_radius * math.cos(angle0)
                    y0 = self._center_y + arc_radius * math.sin(angle0)
                    x1 = self._center_x + arc_radius * math.cos(angle1)
                    y1 = self._center_y + arc_radius * math.sin(angle1)

                span_deg = (a1 - a0)
                large_arc = '1' if abs(span_deg) > 180 else '0'
                sweep = '1' if span_deg > 0 else '0'

                path_d = f'M {x0} {y0} A {arc_radius} {arc_radius} 0 {large_arc} {sweep} {x1} {y1}'

                svg_parts.append(
                    f'<path d="{path_d}" stroke="#333" stroke-width="{arc_w}" '
                    f'fill="none" stroke-linecap="round" stroke-linejoin="round"/>'
                )

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
                <div style="margin-top: 5px; font-size: 14px; font-weight: 400; color: #333;">
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

