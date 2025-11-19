"""
Test application for Both Gauges
Minigui for testing speed and heading gauges together
"""

import sys
import os
import math
import time

# Add parent directory to path to import gauge module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from nicegui import ui
from gauge import GaugeSVGFull


class BothGaugesTest:
    """Test application for both gauges"""
    
    def __init__(self):
        self.speed_gauge = None
        self.heading_gauge = None
        self.simulate_timer = None
        self.simulate_active = False
        self.speed_value = 0.0
        self.heading_value = 0.0
        self.start_time = time.time()
        
    def create_ui(self):
        """Create test UI"""
        ui.page_title('Both Gauges Test')
        
        with ui.column().classes('w-full items-center gap-4 p-8'):
            # Title
            ui.label('Test Both Gauges').classes('text-2xl font-bold')
            
            # Gauges display area - side by side
            with ui.row().classes('w-full justify-center gap-8'):
                # Speed gauge
                with ui.card().classes('p-4'):
                    bg_path_speed = os.path.join(
                        os.path.dirname(os.path.dirname(__file__)),
                        'assets',
                        'gauge_background_speed.png'
                    )
                    
                    if not os.path.exists(bg_path_speed):
                        bg_path_speed = None
                    
                    self.speed_gauge = GaugeSVGFull(
                        value=0,
                        min_value=0,
                        max_value=100,
                        label='EGO Speed',
                        gauge_type='circular',
                        background_image=bg_path_speed,
                        size=220,
                        needle_color='#000000',
                        needle_length=0.75,
                        show_value=True,
                        show_ticks=True,
                        tick_count=12
                    )
                
                # Heading gauge
                with ui.card().classes('p-4'):
                    bg_path_heading = os.path.join(
                        os.path.dirname(os.path.dirname(__file__)),
                        'assets',
                        'gauge_background_heading.png'
                    )
                    
                    if not os.path.exists(bg_path_heading):
                        bg_path_heading = None
                    
                    self.heading_gauge = GaugeSVGFull(
                        value=0,
                        min_value=0,
                        max_value=360,
                        label='EGO Heading',
                        gauge_type='semicircular',
                        background_image=bg_path_heading,
                        size=220,
                        needle_color='#000000',
                        needle_length=0.75,
                        show_value=True,
                        show_ticks=True,
                        tick_count=9
                    )
            
            # Controls
            with ui.card().classes('w-full max-w-2xl p-4'):
                ui.label('Controls').classes('text-lg font-bold mb-4')
                
                # Value displays
                with ui.row().classes('w-full gap-4 mb-4'):
                    self.speed_label = ui.label('Speed: 0.0 km/h').classes('text-lg flex-1')
                    self.heading_label = ui.label('Heading: 0.0 gradi').classes('text-lg flex-1')
                
                # Manual controls
                with ui.row().classes('w-full gap-4 mb-4'):
                    # Speed control
                    with ui.column().classes('flex-1'):
                        ui.label('Speed:').classes('text-sm font-bold')
                        self.speed_slider = ui.slider(
                            min=0,
                            max=100,
                            value=0,
                            step=0.1
                        ).classes('w-full')
                        self.speed_slider.on_value_change(self._on_speed_slider_change)
                    
                    # Heading control
                    with ui.column().classes('flex-1'):
                        ui.label('Heading:').classes('text-sm font-bold')
                        self.heading_slider = ui.slider(
                            min=0,
                            max=360,
                            value=0,
                            step=1
                        ).classes('w-full')
                        self.heading_slider.on_value_change(self._on_heading_slider_change)
                
                # Buttons
                with ui.row().classes('w-full gap-2'):
                    self.simulate_btn = ui.button(
                        'Start EGO Simulation',
                        on_click=self._toggle_simulation
                    ).classes('flex-1')
                    
                    ui.button(
                        'Reset',
                        on_click=self._reset
                    ).classes('flex-1')
                    
                    ui.button(
                        'Set Test Values',
                        on_click=self._set_test_values
                    ).classes('flex-1')
            
            # Info
            with ui.card().classes('w-full max-w-2xl p-4'):
                ui.label('Info').classes('text-lg font-bold mb-2')
                ui.label('- EGO Simulation simulates realistic vehicle data')
                ui.label('- Speed varies sinusoidally (0-100 km/h)')
                ui.label('- Heading rotates continuously (0-360 gradi)')
                ui.label('- Both gauges update simultaneously')
    
    def _on_speed_slider_change(self, e):
        """Handle speed slider change"""
        # Extract value from event object
        if hasattr(e, 'value') and e.value is not None:
            value = e.value
        elif hasattr(e, 'args') and e.args and len(e.args) > 0:
            value = e.args[0]
        else:
            # Fallback: try to get value from slider directly
            value = self.speed_slider.value
        self._set_speed(float(value))
    
    def _on_heading_slider_change(self, e):
        """Handle heading slider change"""
        # Extract value from event object
        if hasattr(e, 'value') and e.value is not None:
            value = e.value
        elif hasattr(e, 'args') and e.args and len(e.args) > 0:
            value = e.args[0]
        else:
            # Fallback: try to get value from slider directly
            value = self.heading_slider.value
        self._set_heading(float(value))
    
    def _set_speed(self, value: float):
        """Set speed gauge value"""
        self.speed_value = max(0, min(100, value))
        if self.speed_gauge:
            self.speed_gauge.set_value(self.speed_value)
        self.speed_label.text = f'Speed: {self.speed_value:.1f} km/h'
        self.speed_slider.value = self.speed_value
    
    def _set_heading(self, value: float):
        """Set heading gauge value"""
        self.heading_value = max(0, min(360, value))
        if self.heading_gauge:
            self.heading_gauge.set_value(self.heading_value)
        self.heading_label.text = f'Heading: {self.heading_value:.1f} gradi'
        self.heading_slider.value = self.heading_value
    
    def _toggle_simulation(self):
        """Toggle EGO data simulation"""
        if self.simulate_active:
            # Stop simulation
            if self.simulate_timer:
                self.simulate_timer.deactivate()
            self.simulate_active = False
            self.simulate_btn.text = 'Start EGO Simulation'
        else:
            # Start simulation
            self.simulate_active = True
            self.simulate_btn.text = 'Stop Simulation'
            self.start_time = time.time()
            
            def simulate_ego_data():
                if self.simulate_active:
                    t = time.time() - self.start_time
                    
                    # Simulate speed: sinusoidal variation 0-100 km/h
                    speed = 50 + 40 * math.sin(t * 0.3)
                    self._set_speed(speed)
                    
                    # Simulate heading: continuous rotation
                    heading = (t * 30) % 360  # 30 degrees per second
                    self._set_heading(heading)
            
            self.simulate_timer = ui.timer(0.1, simulate_ego_data, active=True)  # 10 Hz
    
    def _reset(self):
        """Reset both gauges to 0"""
        self._set_speed(0)
        self._set_heading(0)
    
    def _set_test_values(self):
        """Set test values"""
        self._set_speed(75)
        self._set_heading(135)


def main():
    """Main entry point"""
    app = BothGaugesTest()
    app.create_ui()
    
    # Run on port 8080, no HTTPS
    ui.run(port=8080, host='0.0.0.0', show=False, title='Both Gauges Test')


if __name__ in {'__main__', '__mp_main__'}:
    main()

