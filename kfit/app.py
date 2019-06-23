import sys
from kfit import models, tools
# from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QMainWindow, QApplication, QPushButton, \
    QWidget, QAction, QTabWidget, QVBoxLayout, QFileDialog, \
    QSizePolicy
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt
from matplotlib.backends.backend_qt5agg import FigureCanvas, \
    NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import numpy as np
from pandas_qtmodel import PandasModel


class App(QMainWindow):
    
    def __init__(self):
        super().__init__()
        self.title = 'kfit'
        self.left = 500
        self.top = 200
        self.width = 2000
        self.height = 1200
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.setWindowTitle(self.title)
        # self.setWindowTitle('kfit')
        self.setWindowIcon(QIcon('../images/K.png'))
        
        self.table_widget = MyTableWidget(self)
        self.setCentralWidget(self.table_widget)
        
        # add import button
        import_btn = QPushButton('Import', self)
        import_btn.clicked.connect(self.import_data)
        import_btn.resize(import_btn.sizeHint())
        import_btn.move(600,12.5)
        
        # add clear canvas button
        clear_btn = QPushButton('Clear Data', self)
        clear_btn.clicked.connect(self.update_canvas)
        clear_btn.resize(clear_btn.sizeHint())
        clear_btn.move(720, 12.5)

        # add quit button
        quit_btn = QPushButton('Quit', self)
        quit_btn.clicked.connect(self.close_app)
        quit_btn.resize(quit_btn.sizeHint())
        quit_btn.move(887.5, 12.5)

        self.show()
        
    def close_app(self):
        print('\nExiting kfit...\n')
        sys.exit()
        
    def import_data(self):
        print('\nImporting .csv file...\n')
        file_name,_ = QFileDialog.getOpenFileName(
            self, 'Open File', '', 'CSV files (*.csv)'
        )
        if file_name != '':
            print(file_name)
            df = tools.to_df(file_name)
            print(df)
            print('Done.\n')
        else:
            print('Import cancelled.')
        
        # # clear canvas
        # self.update_canvas()
        # 
        # # plot new data
        # model = PandasModel(df)
        # self.tableView.setModel(model)
        
    def update_canvas(self):
        # self._static_ax.clear()
        # self._static_ax.figure.canvas.draw()
        # !!!! STUCK HERE !!!!
        self.table_widget.tab1.layout.clear()
        # figure.canvas.draw()


class MyTableWidget(QWidget):
    
    def __init__(self, parent):
        # super(QWidget, self).__init__(parent)
        super(MyTableWidget, self).__init__()
        self.layout = QVBoxLayout(self)
        
        # Initialize tab screen
        self.tabs = QTabWidget()
        self.tab1 = QWidget()
        self.tab2 = QWidget()
        self.tabs.resize(300,200)
        
        # Add tabs
        self.tabs.addTab(self.tab1,"Graph View")
        self.tabs.addTab(self.tab2,"Data View")
        
        # Graph View tab
        self.tab1.layout = QVBoxLayout(self)
        self.tab1.layout.addWidget(WidgetPlot(self))
        self.tab1.setLayout(self.tab1.layout)

        # Add tabs to widget
        self.layout.addWidget(self.tabs)
        self.setLayout(self.layout)
        self.show()
        

class WidgetPlot(QWidget):
    def __init__(self, *args, **kwargs):
        QWidget.__init__(self, *args, **kwargs)
        self.setLayout(QVBoxLayout())
        self.canvas = PlotCanvas(self, width=9, height=6)
        self.toolbar = NavigationToolbar(self.canvas, self)
        self.layout().addWidget(self.canvas)
        self.layout().addWidget(self.toolbar)

class PlotCanvas(FigureCanvas):
    def __init__(self, parent=None, width=9, height=6, dpi=150):
        fig = Figure(figsize=(width, height), dpi=dpi)
        FigureCanvas.__init__(self, fig)
        self.setParent(parent)
        FigureCanvas.setSizePolicy(self, QSizePolicy.Expanding, QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)
        self.plot()

    def plot(self):
        plt.style.use('fivethirtyeight')
        x = np.linspace(0, 10, 100)
        y = models.gauss(x, 1, 3, 2) + \
            models.gauss(x, 0.4, 5, 1) + \
            models.gauss(x, 15, 8, 1)
        ax = self.figure.add_subplot(111)
        ax.scatter(
            x, y, s=150, c='None', edgecolors='black',
            linewidth=2
        )
        self.draw()

def run():
    app = QApplication(sys.argv)
    GUI = App()
    sys.exit(app.exec_())

    
if __name__ == '__main__':
    run()
