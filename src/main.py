
from qt import *
from main_window import MainWindow
from devices import DeviceManager
import qtawesome as qta


class Application(BaseApplication):
    def __init__(self) -> None:
        super().__init__()

        self.init_app_info()
        
        # self.setQuitOnLastWindowClosed(False)

        icon = QIcon(qta.icon('fa.circle','fa5s.video', options=[{'color':'gray'}, {'scale_factor':0.5, 'color':'white'}]))
        self.setWindowIcon(icon)
        
        tray = QSystemTrayIcon()
        tray_icon = QIcon(qta.icon('fa5s.video', color='white'))
        tray.setIcon(tray_icon)
        tray.setVisible(True)

        menu = QMenu()
        self.test = QAction('test', triggered=lambda: print('test'))
        menu.addAction(self.test)
        self.quit_action = QAction("Quit", triggered=self.quit)
        menu.addAction(self.quit_action)
        tray.setContextMenu(menu)
        self.tray = tray

        self.device_manager = DeviceManager(self)

        # create window
        self.window = MainWindow()
        self.window.show()

    def closeEvent(self, event):
        self.device_manager.close()
        return super().closeEvent(event)

    def init_app_info(self):
        self.setOrganizationName("DaelonCo")
        self.setOrganizationDomain("DaelonCo")
        self.setApplicationName("Stagehand")
        self.setApplicationVersion("v0.1")


def run():    
    # Create the Qt Application
    app = Application()

    # Run the main Qt loop
    app.exec_()

if __name__ == "__main__":
    run()