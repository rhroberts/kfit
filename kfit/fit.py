import sys
from kfit import models, tools
from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow, \
                            QPushButton, QTableView, QVBoxLayout, \
                            QTabWidget, QFileDialog
from PyQt5.QtCore import pyqtSlot, QCoreApplication
from PyQt5.QtGui import QIcon
import pandas as pd
from pandas_qtmodel import PandasModel
from matplotlib.backends.backend_qt5agg import FigureCanvas, \
    NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
import matplotlib.pyplot as plt


class App(QMainWindow):
    def __init__(self):
        super().__init__()
        self.title = 'kfit'
        self.left = 500
        self.top = 200
        self.width = 2000
        self.height = 1200
        self.file_name = ''

        # temporary data 
        self.data = pd.read_csv('../scripts/example_data.csv')

        self.initUI()

    def initUI(self):
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.setWindowTitle(self.title)
        self.setWindowIcon(QIcon('../images/K.png'))
        
        # Create the Main Tab Widget
        self.tabs = QTabWidget(self)
        self.setCentralWidget(self.tabs)
        self.tab1 = QWidget(self)
        self.tab2 = QTableView(self)
        self.tabs.addTab(self.tab1,"Graph")
        self.tabs.addTab(self.tab2,"Data")

        # Tab 1 - Graph
        plt.style.use('fivethirtyeight')
        self.tab1.figure = Figure(figsize=(9,6))
        self.tab1.canvas = FigureCanvas(self.tab1.figure)
        self.tab1.toolbar =  NavigationToolbar(self.tab1.canvas, self)
        layout = QVBoxLayout()
        layout.addWidget(self.tab1.canvas)
        layout.addWidget(self.tab1.toolbar)
        self.tab1.setLayout(layout)
        self.plot()

        # Tab 2 - Data Table
        self.model = PandasModel(self.data)
        self.tab2.setModel(self.model)
        self.tab2.resizeColumnsToContents()

        # quit button
        quit_btn = QPushButton("Quit", self)
        quit_btn.clicked.connect(self.close_app)
        quit_btn.resize(100,55)
        quit_btn.move(1900, 0)

        # import button
        import_btn = QPushButton("Import", self)
        import_btn.clicked.connect(self.get_data)
        import_btn.resize(100, 55)
        import_btn.move(1800, 0)

        self.show()

    @pyqtSlot()
    def close_app(self):
        print('Quitting application...')
        sys.exit()

    @pyqtSlot()
    def get_data(self):
        print('\nImporting .csv file...\n')
        self.file_name,_ = QFileDialog.getOpenFileName(
            self, 'Open File', '', 'CSV files (*.csv)'
        )
        if self.file_name != '':
            print(self.file_name)
            df = tools.to_df(self.file_name)
            self.data = df
            print('Done.\n')
        else:
            print('Import cancelled.')

        self.model = PandasModel(self.data)
        self.tab2.setModel(self.model)
        self.tab2.resizeColumnsToContents()
        self.plot()

    def plot(self):
        self.tab1.figure.clear()
        ax = self.tab1.figure.add_subplot(111, label=self.file_name)
        ax.scatter(
            self.data.iloc[:,0], self.data.iloc[:,1],
            s=250, c='None', edgecolors='purple', linewidth=3
        )
        ax.set_xlabel(self.data.columns[0])
        ax.set_ylabel(self.data.columns[1])
        self.tab1.canvas.draw()

def run():
    app = QApplication(sys.argv)
    GUI = App()
    sys.exit(app.exec_())

    
if __name__ == '__main__':
    run()
