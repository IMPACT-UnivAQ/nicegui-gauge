"""
Test application for Speed Gauge (circular)
Minigui for testing and refining speed gauge visualization
"""

import sys
import os
import random
# Add parent directory to path to import gauge module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from nicegui import ui
from gauge import GaugeSVGFull


class SpeedGaugeTest:
    """Test application for speed gauge"""
    
    def __init__(self):
        self.gauge = None
        self.auto_update_timer = None
        self.auto_update_active = False
        self.current_value = 0.0
        self.manual_mode = False
        self.sensor_enabled=False
        self.sensor_timer=None
        self.timer_enable=False  
    def create_ui(self):
        """Create test UI"""
        ui.page_title('Speed Gauge Test')
        
        with ui.column().classes('w-full items-center gap-4 p-8'):
            # Title
            ui.label('Test Speed Gauge').classes('text-2xl font-bold')
            
            # Gauge display area
            with ui.card().classes('p-4'):
                # Try to load background image if available
                bg_path = os.path.join(
                    os.path.dirname(os.path.dirname(__file__)),
                    'assets',
                    'gauge_background_speed.png'
                )
                
                if not os.path.exists(bg_path):
                    bg_path = None
                
                self.gauge = GaugeSVGFull(
                    value=0,
                    min_value=0,
                    max_value=100,
                    label='EGO Speed',
                    gauge_type='circular',
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
                self.value_label = ui.label('Value: 0.0 km/h').classes('text-lg mb-4')
                
                # Slider
                self.slider = ui.slider(
                    min=0,
                    max=100,
                    value=0,
                    step=0.1
                ).classes('w-full mb-4')
                #self.slider.disabled=True
                self.slider.on_value_change(self._on_slider_change)
                self.slider.disable()
                #checkbox
                
                ui.checkbox('Enable slider',value=False,on_change=self._toggle_slider)
                self.sensor_cb=ui.checkbox('Enable Sensor', value=False,on_change=self.update_gauge_state)
                self.sensor_cb.disable()  
                self.timer_cb=ui.checkbox('Enable Timer',value=False,on_change=self.update_gauge_state)
                
                # Manual value input
                with ui.row().classes('w-full items-center gap-2'):
                    ui.label('Manual Value:').classes('w-32')
                    self.value_input = ui.number(
                        value=0,
                        min=0,
                        max=100,
                        step=0.1
                    ).classes('flex-1')
                    self.value_input.on_value_change(self._on_input_change)
                    ui.label('km/h').classes('w-12')
                
                # Buttons
                with ui.row().classes('w-full gap-2'):
                    self.auto_update_btn = ui.button(
                        'Start Auto Update',
                        on_click=self._toggle_auto_update
                    ).classes('flex-1')
                    
                    ui.button(
                        'Reset',
                        on_click=self._reset
                    ).classes('flex-1')
                    
                    ui.button(
                        'Set to 50',
                        on_click=lambda: self._set_value(50)
                    ).classes('flex-1')
                    
                    ui.button(
                        'Set to 100',
                        on_click=lambda: self._set_value(100)
                    ).classes('flex-1')
            
            # Info
            with ui.card().classes('w-full max-w-md p-4'):
                ui.label('Info').classes('text-lg font-bold mb-2')
                ui.label('- Use slider or input to change gauge value manually')
                ui.label('- Auto Update simulates real-time data updates')
                ui.label('- Gauge type: Circular (0-100 km/h)')
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
        if not self.manual_mode:
            return  # Ignore slider changes if manual mode is disabled
    
        value = e.value

    def _toggle_slider(self,e):
        self.manual_mode =e.value
        if self.manual_mode:
        # Enable manual control
            self.slider.enable()
            print("✅ Manual control ENABLED - Slider is active")
        else:
        # Disable manual control  
            self.slider.disable()
            print("🔵 Manual control DISABLED - Slider is locked")

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
    def update_gauge_state(self, e=None):
        self.sensor_enabled = self.sensor_cb.value
        if not self.timer_cb.value:
            print("✅ Sensor is not available")
            self.sensor_cb.disable()
            self.sensor_cb.value = False
            self.sensor_enabled = False

            if self.sensor_timer:

                self.sensor_timer.deactivate()
            self._set_value(0)  # reset gauge
            return
        #self.sensor_cb.enable()
        if self.timer_cb :
            self.sensor_cb.enable()
            print("✅ Sensor Checkbox is active")
            if self.sensor_timer:
                self.sensor_timer.activate()
        if self.timer_cb.value and self.sensor_cb.value:
        # create timer if it doesn't exist
            if not hasattr(self, 'sensor_timer') or self.sensor_timer is None:
                
                def update_sensor():
                    if self.sensor_cb.value:
                        value = random.uniform(0, 100)
                        self._set_value(value)
                self.sensor_timer = ui.timer(0.1, update_sensor, active=True)
            else:
                self.sensor_timer.activate()
        else:
            print("🔵 Sensor Checkbox is not active")
            if self.sensor_timer:
                self.sensor_timer.deactivate()
 
    def _set_value(self, value: float):
        """Set gauge value"""
        self.current_value = max(0, min(100, value))
        if self.gauge:
            self.gauge.set_value(self.current_value)
        self.value_label.text = f'Value: {self.current_value:.1f} km/h'
        self.value_input.value = self.current_value
        self.slider.value = self.current_value
    
    def _toggle_auto_update(self):
        """Toggle auto update simulation"""
        if self.auto_update_active:
            # Stop auto update
            if self.auto_update_timer:
                self.auto_update_timer.deactivate()
            self.auto_update_active = False
            self.auto_update_btn.text = 'Start Auto Update'

        

        else:
            # Start auto update
            self.auto_update_active = True
            self.auto_update_btn.text = 'Stop Auto Update'
        
            def update_value():
                if self.auto_update_active:
                    # Simulate speed changes (0-100 km/h)
                    import math
                    import time
                    t = time.time()
                                           
                    # Sinusoidal variation
                    value = 50 + 40 * math.sin(t * 0.5)

                    
                elif self.sensor_enabled: 
                     value=self.update_sensor()
                self._set_value(value)    
            self.auto_update_timer = ui.timer(0.1, update_value, active=True)
            
    
    def _reset(self):
        """Reset gauge to 0"""
        self._set_value(0)


def main():
    """Main entry point"""
    app = SpeedGaugeTest()
    app.create_ui()
    
    # Run on port 8080, no HTTPS
    ui.run(port=8080, host='0.0.0.0', show=False, title='Speed Gauge Test')


if __name__ in {'__main__', '__mp_main__'}:
    main()

