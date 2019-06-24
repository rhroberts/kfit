import sys
import pandas as pd
import numpy as np
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
from kfit import models, tools
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from matplotlib.backends.backend_qt5agg import FigureCanvas, \
    NavigationToolbar2QT as NavigationToolbar

class App(QMainWindow):
    def __init__(self):
        super().__init__()
        self.title = 'kfit'
        self.left = 500
        self.top = 200
        self.width = 2000
        self.height = 1200
        self.file_name = ''
        self.xcol_idx = 0
        self.ycol_idx = 1

        # temporary data 
        # self.data = pd.read_csv('../scripts/example_data.csv')
        x = np.linspace(0,10,500)
        y = models.gauss(x, 0.5, 4, 0.4) + \
                models.gauss(x, 0.8, 5, 0.2) + \
                models.gauss(x, 0.4, 6, 0.3)
        self.data = pd.DataFrame([x,y]).T
        self.data.columns = ['x', 'y']

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
        self.tab3 = QWidget(self)
        self.tabs.addTab(self.tab1,'Graph')
        self.tabs.addTab(self.tab2,'Data')
        self.tabs.addTab(self.tab3,'Model')

        # Tab 1 - Graph
        plt.style.use('fivethirtyeight')
        self.tab1.figure = Figure(figsize=(9,6), dpi=110)
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
        self.quitButton = QPushButton('Quit', self)
        self.quitButton.clicked.connect(self.close_app)
        self.quitButton.resize(100,55)
        self.quitButton.move(1900, 0)

        # import button
        self.importButton = QPushButton('Import', self)
        self.importButton.clicked.connect(self.get_data)
        self.importButton.resize(100, 55)
        self.importButton.move(1800, 0)

        # fit button
        self.fitButton = QPushButton('Fit', self)
        self.fitButton.clicked.connect(self.fit)
        self.fitButton.resize(100, 55)
        self.fitButton.move(1700, 0)
        self.fitButton.setStyleSheet('background-color: lightgreen')
        
        # get column header for x
        self.xLabel = QLabel(self)
        self.xLabel.setText('ColumnIndex(X):')
        self.xLabel.resize(300, 45)
        self.xLabel.move(500, 5)
        self.xLineEntry = QLineEdit(self)
        self.xLineEntry.resize(75, 45)
        self.xLineEntry.move(725, 5)
        self.xLineEntry.setPlaceholderText('0')
        self.xLineEntry.setAlignment(Qt.AlignCenter)
        self.xSet = QPushButton('Set', self)
        self.xSet.resize(50, 45)
        self.xSet.move(800, 5)
        self.xSet.clicked.connect(self.xset_click)

        # get column header for y
        self.yLabel = QLabel(self)
        self.yLabel.setText('ColumnIndex(Y):')
        self.yLabel.resize(300, 45)
        self.yLabel.move(900, 5)
        self.yLineEntry = QLineEdit(self)
        self.yLineEntry.resize(75, 45)
        self.yLineEntry.move(1125, 5)
        self.yLineEntry.setPlaceholderText('1')
        self.yLineEntry.setAlignment(Qt.AlignCenter)
        self.ySet = QPushButton('Set', self)
        self.ySet.resize(50, 45)
        self.ySet.move(1200, 5)
        self.ySet.clicked.connect(self.yset_click)

        self.show()

    @pyqtSlot()
    def fit(self):
        pass

    @pyqtSlot()
    def xset_click(self):
        try:
            idx = int(self.xLineEntry.text())
        except:
            print("Can't convert index to integer!")
            return
        self.xcol_idx = idx
        self.plot()
        print('ColumnIndex(X) = ' + str(idx))

    @pyqtSlot()
    def yset_click(self):
        try:
            idx = int(self.yLineEntry.text())
        except:
            print("Can't convert index to integer!")
            return
        self.ycol_idx = idx
        self.plot()
        print('ColumnIndex(Y) = ' + str(idx))

    @pyqtSlot()
    def close_app(self):
        print('\nQuitting application...')
        sys.exit()

    @pyqtSlot()
    def get_data(self):
        self.file_name,_ = QFileDialog.getOpenFileName(
            self, 'Open File', '', 'CSV files (*.csv)'
        )
        if self.file_name != '':
            print('\nImporting .csv file:')
            print(self.file_name)
            print('...')
            df = tools.to_df(self.file_name)
            self.data = df
        else:
            print('Import cancelled.')
            return

        self.model = PandasModel(self.data)
        self.tab2.setModel(self.model)
        self.tab2.resizeColumnsToContents()
        self.plot()
        print('\nDone.\n')

    def plot(self):
        self.tab1.figure.clear()
        ax = self.tab1.figure.add_subplot(111, label=self.file_name)
        ax.scatter(
            self.data.iloc[:,self.xcol_idx],
            self.data.iloc[:,self.ycol_idx],
            s=200, c='None', edgecolors='purple', linewidth=3
        )
        ax.set_xlabel(self.data.columns[self.xcol_idx], labelpad=10)
        ax.set_ylabel(self.data.columns[self.ycol_idx], labelpad=15)
        self.tab1.canvas.draw()

class PandasModel(QAbstractTableModel): 
    def __init__(self, df = pd.DataFrame(), parent=None): 
        QAbstractTableModel.__init__(self, parent=parent)
        self._df = df

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role != Qt.DisplayRole:
            return QVariant()

        if orientation == Qt.Horizontal:
            try:
                return self._df.columns.tolist()[section]
            except (IndexError, ):
                return QVariant()
        elif orientation == Qt.Vertical:
            try:
                # return self.df.index.tolist()
                return self._df.index.tolist()[section]
            except (IndexError, ):
                return QVariant()

    def data(self, index, role=Qt.DisplayRole):
        if role != Qt.DisplayRole:
            return QVariant()

        if not index.isValid():
            return QVariant()

        return QVariant(str(self._df.ix[index.row(), index.column()]))

    def setData(self, index, value, role):
        row = self._df.index[index.row()]
        col = self._df.columns[index.column()]
        if hasattr(value, 'toPyObject'):
            # PyQt4 gets a QVariant
            value = value.toPyObject()
        else:
            # PySide gets an unicode
            dtype = self._df[col].dtype
            if dtype != object:
                value = None if value == '' else dtype.type(value)
        self._df.set_value(row, col, value)
        return True

    def rowCount(self, parent=QModelIndex()): 
        return len(self._df.index)

    def columnCount(self, parent=QModelIndex()): 
        return len(self._df.columns)

    def sort(self, column, order):
        colname = self._df.columns.tolist()[column]
        self.layoutAboutToBeChanged.emit()
        self._df.sort_values(colname, ascending= order == Qt.AscendingOrder, inplace=True)
        self._df.reset_index(inplace=True, drop=True)
        self.layoutChanged.emit()
def run():
    app = QApplication(sys.argv)
    GUI = App()
    sys.exit(app.exec_())

    
if __name__ == '__main__':
    run()
