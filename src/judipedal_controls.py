from qt import *
from devices import DeviceManager
import json


class PedalActions(QWidget):
    def __init__(self, name, obs, parent=None):
        super().__init__(parent=parent)
        self.obs = obs

        self.name = QLabel(name)
        self.status = QLabel('up')
        self.pressed_action = PersistentLineEdit(f'{name}_pressed')
        self.released_action = PersistentLineEdit(f'{name}_released')

        with CVBoxLayout(self) as layout:
            with layout.hbox(align='left'):
                layout.add(QLabel('Pedal:'))
                layout.add(self.name)
                layout.add(QLabel(), 1)
                layout.add(QLabel('Status:'))
                layout.add(self.status)
                
            with layout.hbox():
                with layout.vbox():
                    layout.add(QLabel('Pressed:'))
                    layout.add(QLabel('Released:'))
                with layout.vbox():
                    layout.add(self.pressed_action)
                    layout.add(self.released_action)

    def pressed(self):
        self.status.setText('down')
        if self.pressed_action.text():
            try:
                payload = json.loads(self.pressed_action.text())
                self.obs.send(payload)
            except:
                pass

    def released(self):
        self.status.setText('up')
        if self.released_action.text():
            try:
                payload = json.loads(self.released_action.text())
                self.obs.send(payload)
            except:
                pass


@DeviceManager.subscribe_to("judipedals")
class JudiPedalsControls(QWidget):
    def __init__(self, parent=None, obs=None):
        super().__init__(parent=parent)

        self.obs = obs

        self.one = PedalActions('one', obs)
        self.two = PedalActions('two', obs)
        self.three = PedalActions('three', obs)
        self.four = PedalActions('four', obs)

        self.status = QLabel("No Pedals Connected")
        
        with CVBoxLayout(self, align='top') as layout:
            with layout.hbox(align='left'):
                layout.add(QLabel('Status:'))
                layout.add(self.status)
            layout.add(HLine())
            layout.add(self.one)
            layout.add(HLine())
            layout.add(self.two)
            layout.add(HLine())
            layout.add(self.three)
            layout.add(HLine())
            layout.add(self.four)

    def connected(self, device):
        self.status.setText('Pedals Connected')
        device.signals.button_pressed.connect(self.button_pressed)
        device.signals.button_released.connect(self.button_released)

    def button_pressed(self, button):
        if button == '1':
            self.one.pressed()
        if button == '2':
            self.two.pressed()
        if button == '3':
            self.three.pressed()
        if button == '4':
            self.four.pressed()

    def button_released(self, button):
        if button == '1':
            self.one.released()
        if button == '2':
            self.two.released()
        if button == '3':
            self.three.released()
        if button == '4':
            self.four.released()