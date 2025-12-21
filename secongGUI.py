from PySide6.QtWidgets import QApplication, QLabel, QWidget, QPushButton, QVBoxLayout
import sys
import os

class Myapp(QWidget):
    def __init__(self):
        super().__init__()


        self.yesbutton = QPushButton("yes")
        self.nobutton = QPushButton("no")

        self.yesbutton.clicked.connect(self.yesbutton_clicked)
        self.nobutton.clicked.connect(self.nobutton_clicked)

        layout = QVBoxLayout()
        layout.addWidget(self.yesbutton)
        layout.addWidget(self.nobutton)
        self.setLayout(layout)

    def yesbutton_clicked(self):
        print("Yes Button was clicked")
        os.system("start whatsapp:")

    def yesbutton_clicked(self):
        print("No Button was clicked")
        os.system("start whatsapp:")


app = QApplication(sys.argv)
window = Myapp()
window.show()
sys.exit(app.exec())

