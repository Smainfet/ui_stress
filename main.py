from PyQt5.QtWidgets import QApplication
from mainWindow import WelcomeScreen
from PyQt5 import QtWidgets
import sys
# main
app = QApplication(sys.argv)
app.setStyle("fusion")
welcome = WelcomeScreen()
widget = QtWidgets.QStackedWidget()
widget.addWidget(welcome)
widget.setFixedHeight(752)
widget.setFixedWidth(1430)
widget.show()
try:
    sys.exit(app.exec_())
except:
    print("Exiting")