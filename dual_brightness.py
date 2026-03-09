import sys
import subprocess
from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QSlider, 
                             QLabel, QHBoxLayout, QPushButton, QSystemTrayIcon)
from PyQt6.QtGui import QIcon, QCursor
from PyQt6.QtCore import Qt
from PyQt6.QtNetwork import QLocalServer, QLocalSocket

# --- GLOBAL CONFIGURATION ---
DISPLAY_NAME = "eDP"
SOCKET_NAME = "DualBrightnessDaemon"
STEP_SIZE = 5  # How much the brightness changes per key press
# ----------------------------

class BrightnessPopup(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.WindowType.Popup | Qt.WindowType.FramelessWindowHint)
        self.setFixedSize(280, 100)
        
        self.current_hw = -1
        self.current_sw = -1.0
        
        layout = QVBoxLayout()
        
        slider_layout = QHBoxLayout()
        slider_label = QLabel("Brightness:")
        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.setRange(0, 100) 
        slider_layout.addWidget(slider_label)
        slider_layout.addWidget(self.slider)
        
        quit_btn = QPushButton("Quit")
        quit_btn.clicked.connect(self.quit_app)
        
        layout.addLayout(slider_layout)
        layout.addWidget(quit_btn)
        self.setLayout(layout)

        self.slider.valueChanged.connect(self.process_slider_change)
        self.reset_values()

    def process_slider_change(self, value):
        if value >= 50:
            sw_target = 1.0
            hw_target = int(5 + (value - 50) * 1.9)
        else:
            hw_target = 5
            sw_target = round(0.2 + (value * 0.018), 2)

        if hw_target != self.current_hw:
            subprocess.run(["brightnessctl", "set", f"{hw_target}%"], check=False)
            self.current_hw = hw_target
            
        if sw_target != self.current_sw:
            subprocess.run(["xrandr", "--output", DISPLAY_NAME, "--brightness", str(sw_target)], check=False)
            self.current_sw = sw_target

    def step_brightness(self, direction):
        current_val = self.slider.value()
        if direction == "UP":
            self.slider.setValue(min(100, current_val + STEP_SIZE))
        elif direction == "DOWN":
            self.slider.setValue(max(0, current_val - STEP_SIZE))

    def reset_values(self):
        self.slider.setValue(100)

    def quit_app(self):
        self.reset_values()
        QApplication.quit()

class TrayApp:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.app.setQuitOnLastWindowClosed(False) 
        
        self.tray = QSystemTrayIcon()
        icon = QIcon.fromTheme("video-display") 
        self.tray.setIcon(icon)
        self.tray.setVisible(True)
        
        self.popup = BrightnessPopup()
        self.tray.activated.connect(self.on_tray_click)
        
        # --- IPC SERVER SETUP ---
        self.server = QLocalServer()
        QLocalServer.removeServer(SOCKET_NAME) # Clean up dead sockets
        self.server.listen(SOCKET_NAME)
        self.server.newConnection.connect(self.handle_connection)
        
    def handle_connection(self):
        socket = self.server.nextPendingConnection()
        if socket.waitForReadyRead(1000):
            message = socket.readAll().data().decode('utf-8')
            if message == "UP" or message == "DOWN":
                self.popup.step_brightness(message)
        socket.disconnectFromServer()

    def on_tray_click(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            self.popup.move(QCursor.pos())
            self.popup.show()

    def run(self):
        sys.exit(self.app.exec())

# --- CLI SENDER LOGIC ---
def send_ipc_message(message):
    socket = QLocalSocket()
    socket.connectToServer(SOCKET_NAME)
    if socket.waitForConnected(500):
        socket.write(message.encode('utf-8'))
        socket.waitForBytesWritten(500)
        socket.disconnectFromServer()
    else:
        print("Daemon is not running. Please start the app first.")

if __name__ == "__main__":
    if "--up" in sys.argv:
        send_ipc_message("UP")
        sys.exit(0)
    elif "--down" in sys.argv:
        send_ipc_message("DOWN")
        sys.exit(0)
    else:
        # Start the background daemon if no arguments are passed
        app = TrayApp()
        app.run()