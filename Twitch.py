import sys
import random
import keyboard
from openai import OpenAI
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QDesktopWidget
from PyQt5.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve
from PyQt5.QtGui import QFont, QPainter, QColor, QLinearGradient

# Point to the local server
client = OpenAI(base_url="http://localhost:1234/v1", api_key="lm-studio")

class ChatMessage(QLabel):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setStyleSheet("background-color: transparent; color: white;")
        self.setFont(QFont("Roboto", 14))
        self.setWordWrap(True)

    def colorize_username(self):
        text = self.text()
        username, message = text.split(':', 1)
        color = QColor(random.randint(100, 255), random.randint(100, 255), random.randint(100, 255))
        self.setText(f'<font color="{color.name()}">{username}</font>:{message}')

class TransparentOverlay(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.messages = []
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.add_new_comment)
        self.timer.start(random.randint(1000, 5000))
        keyboard.add_hotkey('esc', self.close)

    def initUI(self):
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        self.layout = QVBoxLayout()
        self.layout.setAlignment(Qt.AlignBottom)
        self.setLayout(self.layout)

        # Get screen resolution
        screen = QDesktopWidget().screenNumber(QDesktopWidget().cursor().pos())
        screen_size = QDesktopWidget().screenGeometry(screen)
        
        # Set window size to 25% of screen width and 50% of screen height
        width = int(screen_size.width() * 0.25)
        height = int(screen_size.height() * 0.5)
        
        # Position the window on the right side of the screen
        x = screen_size.width() - width - 20  # 20px padding from the right edge
        y = (screen_size.height() - height) // 2  # Centered vertically
        
        self.setGeometry(x, y, width, height)
        self.show()

    def update_text(self, text):
        if len(self.messages) >= 15:
            self.layout.removeWidget(self.messages[0])
            self.messages[0].deleteLater()
            self.messages.pop(0)

        new_message = ChatMessage(text)
        new_message.colorize_username()
        self.messages.append(new_message)
        self.layout.addWidget(new_message)

        # Animate new message
        self.animate_new_message(new_message)

    def animate_new_message(self, message):
        animation = QPropertyAnimation(message, b"geometry")
        animation.setDuration(300)
        animation.setStartValue(message.geometry().adjusted(self.width(), 0, self.width(), 0))
        animation.setEndValue(message.geometry())
        animation.setEasingCurve(QEasingCurve.OutCubic)
        animation.start()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Create a gradient background
        gradient = QLinearGradient(0, 0, 0, self.height())
        gradient.setColorAt(0, QColor(0, 0, 0, 180))
        gradient.setColorAt(1, QColor(0, 0, 0, 140))
        
        painter.setBrush(gradient)
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(self.rect(), 10, 10)

    def add_new_comment(self):
        new_comment = generate_comment()
        self.update_text(new_comment)
        # Set a new random interval for the next comment
        self.timer.setInterval(random.randint(1000, 5000))

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.close()

def generate_comment():
    # Simulate special events
    if random.random() < 0.05:  # 5% chance for a special event
        event_type = random.choice(['raid', 'donation', 'subscription'])
        if event_type == 'raid':
            return f"Streamlabs: {random.choice(['PogChamp', 'Kreygasm', 'Kappa'])} {random.choice(['Ninja', 'Pokimane', 'Shroud'])} is raiding with {random.randint(10, 1000)} viewers!"
        elif event_type == 'donation':
            return f"Streamlabs: {random.choice(['PogChamp', 'Kreygasm', 'Kappa'])} {random.choice(['John', 'Emma', 'Alex'])} donated ${random.randint(1, 100)}!"
        elif event_type == 'subscription':
            return f"Streamlabs: {random.choice(['PogChamp', 'Kreygasm', 'Kappa'])} {random.choice(['Sarah', 'Mike', 'Lisa'])} just subscribed for {random.randint(1, 12)} months!"

    completion = client.chat.completions.create(
        model="bartowski/Llama-3.2-1B-Instruct-GGUF",
        messages=[
            {"role": "system", "content": "This is a Twitch chat simulator! Your output will be used to generate a comment on Twitch! Respond like a Twitch gamer watching a stream. Respond in this format: <username>: <comment>"},
            {"role": "user", "content": "Go ahead and generate exactly ONE username and comment for this Twitch stream! It doesn't have to make sense, it can even be just an emoji! Be sure to come up with a fun username, and respond only with <username>: <comment>, but don't use quotation marks."}
        ],
        temperature=1.0,
    )
    
    # Get the raw content and clean it up
    raw_content = completion.choices[0].message.content
    cleaned_content = raw_content.strip('"').replace('\n', ' ').replace('\r', '')
    # Ensure the content is in the correct format
    if ':' not in cleaned_content:
        # If there's no colon, add a default username
        cleaned_content = f"Anonymous: {cleaned_content}"

    return cleaned_content

if __name__ == "__main__":
    app = QApplication(sys.argv)
    overlay = TransparentOverlay()
    
    print("Simulating Twitch chat. Press ESC to stop...")
    sys.exit(app.exec_())