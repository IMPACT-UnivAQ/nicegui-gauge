"""
Test application for Heading Gauge (semicircular)
Minigui for testing and refining heading gauge visualization
"""

import sys
import os

# Add parent directory to path to import gauge module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from nicegui import ui
from gauge import GaugeSVGFull


class HeadingGaugeTest:
    """Test application for heading gauge"""
    
    def __init__(self):
        self.gauge = None
        self.rotate_timer = None
        self.rotate_active = False
        self.current_value = 0.0
        
    def create_ui(self):
        """Create test UI"""
        ui.page_title('Heading Gauge Test')
        
        with ui.column().classes('w-full items-center gap-4 p-8'):
            # Title
            ui.label('Test Heading Gauge').classes('text-2xl font-bold')
            
            # Gauge display area
            with ui.card().classes('p-4'):
                # Try to load background image if available
                bg_path = os.path.join(
                    os.path.dirname(os.path.dirname(__file__)),
                    'assets',
                    'gauge_background_heading.png'
                )
                
                if not os.path.exists(bg_path):
                    bg_path = None
                
                self.gauge = GaugeSVGFull(
                    value=0,
                    min_value=0,
                    max_value=360,
                    label='EGO Heading',
                    gauge_type='semicircular',
                    background_image=bg_path,
                    size=220,
                    needle_color='#000000',
                    needle_length=0.75,
                    show_value=True,
                    show_ticks=True,
                    tick_count=12
                )
            
            # Controls
            with ui.card().classes('w-full max-w-md p-4'):
                ui.label('Controls').classes('text-lg font-bold mb-4')
                
                # Value display
                self.value_label = ui.label('Value: 0.0 gradi').classes('text-lg mb-4')
                
                # Slider
                self.slider = ui.slider(
                    min=0,
                    max=360,
                    value=0,
                    step=1
                ).classes('w-full mb-4')
                self.slider.on_value_change(self._on_slider_change)
                
                # Manual value input
                with ui.row().classes('w-full items-center gap-2'):
                    ui.label('Manual Value:').classes('w-32')
                    self.value_input = ui.number(
                        value=0,
                        min=0,
                        max=360,
                        step=1
                    ).classes('flex-1')
                    self.value_input.on_value_change(self._on_input_change)
                    ui.label('gradi').classes('w-12')
                
                # Buttons
                with ui.row().classes('w-full gap-2'):
                    self.rotate_btn = ui.button(
                        'Start Continuous Rotation',
                        on_click=self._toggle_rotation
                    ).classes('flex-1')
                    
                    ui.button(
                        'Reset',
                        on_click=self._reset
                    ).classes('flex-1')
                    
                    ui.button(
                        'Set to 90',
                        on_click=lambda: self._set_value(90)
                    ).classes('flex-1')
                    
                    ui.button(
                        'Set to 180',
                        on_click=lambda: self._set_value(180)
                    ).classes('flex-1')
                    
                    ui.button(
                        'Set to 270',
                        on_click=lambda: self._set_value(270)
                    ).classes('flex-1')
            
            # Info
            with ui.card().classes('w-full max-w-md p-4'):
                ui.label('Info').classes('text-lg font-bold mb-2')
                ui.label('- Use slider or input to change gauge value manually')
                ui.label('- Continuous Rotation simulates heading changes')
                ui.label('- Gauge type: Semicircular (0-360 gradi)')
                ui.label('- Background: PNG image (if available)')
    
    def _on_slider_change(self, e):
        """Handle slider change"""
        # Extract value from event object
        if hasattr(e, 'value') and e.value is not None:
            value = e.value
        elif hasattr(e, 'args') and e.args and len(e.args) > 0:
            value = e.args[0]
        else:
            # Fallback: try to get value from slider directly
            value = self.slider.value
        self._set_value(float(value))
    
    def _on_input_change(self, e):
        """Handle input change"""
        # Extract value from event object
        if hasattr(e, 'value') and e.value is not None:
            value = e.value
        elif hasattr(e, 'args') and e.args and len(e.args) > 0:
            value = e.args[0]
        else:
            # Fallback: try to get value from input directly
            value = self.value_input.value
        if value is not None:
            self._set_value(float(value))
            # Sync slider
            self.slider.value = float(value)
    
    def _set_value(self, value: float):
        """Set gauge value"""
        self.current_value = max(0, min(360, value))
        if self.gauge:
            self.gauge.set_value(self.current_value)
        self.value_label.text = f'Value: {self.current_value:.1f} gradi'
        self.value_input.value = self.current_value
        self.slider.value = self.current_value
    
    def _toggle_rotation(self):
        """Toggle continuous rotation"""
        if self.rotate_active:
            # Stop rotation
            if self.rotate_timer:
                self.rotate_timer.deactivate()
            self.rotate_active = False
            self.rotate_btn.text = 'Start Continuous Rotation'
        else:
            # Start rotation
            self.rotate_active = True
            self.rotate_btn.text = 'Stop Rotation'
            
            def rotate_value():
                if self.rotate_active:
                    # Continuous rotation 0-360 degrees
                    self.current_value = (self.current_value + 1) % 360
                    self._set_value(self.current_value)
            
            self.rotate_timer = ui.timer(0.05, rotate_value, active=True)  # 20 updates/sec
    
    def _reset(self):
        """Reset gauge to 0"""
        self._set_value(0)


def main():
    """Main entry point"""
    app = HeadingGaugeTest()
    app.create_ui()
    
    # Run on port 8080, no HTTPS
    ui.run(port=8080, host='0.0.0.0', show=False, title='Heading Gauge Test')


if __name__ in {'__main__', '__mp_main__'}:
    main()

