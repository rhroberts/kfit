import sys
import time
import pandas as pd
import numpy as np
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from kfit import models, tools
from lmfit.model import Parameters
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from matplotlib.backends.backend_qt5agg import FigureCanvas, \
    NavigationToolbar2QT as NavigationToolbar

idx_error_msg = "Error: Can't convert index to integer!"
msg_length = 2000

class App(QMainWindow):
    def __init__(self):
        super().__init__()
        self.title = 'kfit'
        self.left = 1000
        self.top = 200
        self.width = 2000
        self.height = 1400
        self.file_name = ''
        self.xcol_idx = 0
        self.ycol_idx = 1
        self.ngau = 0
        self.nlor = 0
        self.nvoi = 0
        self.nlin = 1
        self.model = None
        self.result = None
        # empty Parameters to hold parameter guesses/constraints
        self.params = Parameters()

        # temporary data 
        x = np.linspace(0,10,500)
        y = models.gauss(x, 0.5, 4, 0.4) + \
                models.gauss(x, 0.8, 5, 0.2) + \
                models.gauss(x, 0.4, 6, 0.3) + 0.2
        self.data = pd.DataFrame([x,y]).T
        self.data.columns = ['x', 'y']

        self.initUI()

    def initUI(self):
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.setWindowTitle(self.title)
        self.setWindowIcon(QIcon('../images/K.png'))

        # set up the status bar
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        self.statusBar.showMessage('Welcome to kfit!', msg_length)
        self.statusBar.setStyleSheet('background-color: white')
        
        # Create the Main Widget and Layout
        self.main_layout = QVBoxLayout()
        self.main_widget = QWidget()
        self.setCentralWidget(self.main_widget)

        # create "top bar" widget
        self.topbar_layout = QHBoxLayout()
        self.topbar_widget = QWidget()
        # import button
        self.importButton = QPushButton('', self)
        self.importButton.setIcon(QIcon.fromTheme('up'))
        self.importButton.setIconSize(QSize(50,50))
        self.importButton.clicked.connect(self.get_data)
        # fit button
        self.fitButton = QPushButton('', self)
        self.fitButton.setIcon(QIcon.fromTheme('dialog-apply'))
        self.fitButton.setIconSize(QSize(50,50))
        self.fitButton.clicked.connect(self.fit)
        self.fitButton.setStyleSheet('font-style: bold')
        # quit button
        self.quitButton = QPushButton('', self)
        self.quitButton.setIcon(QIcon.fromTheme('gtk-cancel'))
        self.quitButton.setIconSize(QSize(50,50))
        self.quitButton.clicked.connect(self.close_app)
        # get column header for x
        self.xLabel = QLabel(self)
        self.xLabel.setText('ColumnIndex(X):')
        self.xLineEntry = QLineEdit(self)
        self.xLineEntry.setPlaceholderText('0')
        self.xLineEntry.setAlignment(Qt.AlignCenter)
        self.xLineEntry.returnPressed.connect(self.xset_click)
        # get column header for y
        self.yLabel = QLabel(self)
        self.yLabel.setText('ColumnIndex(Y):')
        self.yLineEntry = QLineEdit(self)
        self.yLineEntry.setPlaceholderText('1')
        self.yLineEntry.setAlignment(Qt.AlignCenter)
        self.yLineEntry.returnPressed.connect(self.yset_click)
        # add topbar widgets to layout
        self.topbar_layout.addSpacing(500)
        self.topbar_layout.addWidget(self.xLabel)
        self.topbar_layout.addWidget(self.xLineEntry)
        self.topbar_layout.addSpacing(50)
        self.topbar_layout.addWidget(self.yLabel)
        self.topbar_layout.addWidget(self.yLineEntry)
        self.topbar_layout.addSpacing(250)
        self.topbar_layout.addWidget(self.fitButton)
        self.topbar_layout.addWidget(self.importButton)
        self.topbar_layout.addWidget(self.quitButton)
        self.topbar_widget.setLayout(self.topbar_layout)

        # create tabs widget
        self.tabs = QTabWidget(self)
        self.tab1 = QWidget(self)
        self.tab2 = QTableView(self)
        self.tab3 = QWidget(self)
        self.tabs.addTab(self.tab1,'Graph')
        self.tabs.addTab(self.tab2,'Data')
        self.tabs.addTab(self.tab3,'Output')

        # create params widget
        self.params_widget = QWidget() 
        self.params_layout = QFormLayout()
        self.params_widget.setLayout(self.params_layout)

        # add everything to layout
        self.main_layout.setSpacing(0)
        self.main_layout.setContentsMargins(0,0,0,0)
        self.main_layout.addWidget(self.topbar_widget)
        self.main_layout.addWidget(self.tabs)
        self.main_layout.addWidget(self.params_widget)
        self.main_widget.setLayout(self.main_layout)

        # Tab 1 - Graph / Model
        plt.style.use('fivethirtyeight')
        self.tab1.figure = Figure(figsize=(9,6), dpi=110)
        self.tab1.canvas = FigureCanvas(self.tab1.figure)
        self.tab1.toolbar =  NavigationToolbar(self.tab1.canvas, self)
        graph_layout = QGridLayout()
        graph_layout.addWidget(self.tab1.canvas, 0, 0)
        graph_layout.addWidget(self.tab1.toolbar, 1, 0)
        model_layout = QHBoxLayout()
        ## specify number of gaussian curves
        gauss_label = QLabel(self)
        gauss_label.setText('Gaussians:')
        gauss_label.setAlignment(Qt.AlignVCenter)
        self.gauss_entry = QLineEdit(self)
        self.gauss_entry.setAlignment(Qt.AlignCenter)
        self.gauss_entry.setPlaceholderText('0')
        self.gauss_entry.returnPressed.connect(self.fit)
        model_layout.addSpacing(200)
        model_layout.addWidget(gauss_label)
        model_layout.addWidget(self.gauss_entry)
        model_layout.addSpacing(50)
        ## specify number of lorentzian curves
        lorentz_label = QLabel(self)
        lorentz_label.setText('Lorentzians:')
        lorentz_label.setAlignment(Qt.AlignVCenter)
        self.lorentz_entry = QLineEdit(self)
        self.lorentz_entry.setAlignment(Qt.AlignCenter)
        self.lorentz_entry.setPlaceholderText('0')
        self.lorentz_entry.returnPressed.connect(self.fit)
        model_layout.addWidget(lorentz_label)
        model_layout.addWidget(self.lorentz_entry)
        model_layout.addSpacing(50)
        ## specify number of pseudo-voigt curves
        voigt_label = QLabel(self)
        voigt_label.setText('Pseudo-Voigts:')
        voigt_label.setAlignment(Qt.AlignVCenter)
        self.voigt_entry = QLineEdit(self)
        self.voigt_entry.setAlignment(Qt.AlignCenter)
        self.voigt_entry.setPlaceholderText('0')
        self.voigt_entry.returnPressed.connect(self.fit)
        model_layout.addWidget(voigt_label)
        model_layout.addWidget(self.voigt_entry)
        model_layout.addSpacing(50)
        ## specify number of linear curves
        line_label = QLabel(self)
        line_label.setText('Lines:')
        line_label.setAlignment(Qt.AlignVCenter)
        self.line_entry = QLineEdit(self)
        self.line_entry.setAlignment(Qt.AlignCenter)
        self.line_entry.setPlaceholderText('1')
        self.line_entry.returnPressed.connect(self.fit)
        model_layout.addWidget(line_label)
        model_layout.addWidget(self.line_entry)
        model_layout.addSpacing(200)

        graph_layout.addLayout(model_layout, 2, 0)
        self.tab1.setLayout(graph_layout)
        self.plot()

        # Tab 2 - Data Table
        self.table_model = PandasModel(self.data)
        self.tab2.setModel(self.table_model)
        self.tab2.resizeColumnsToContents()

        # Tab 3 - Output
        tab3_layout = QGridLayout()
        self.tab3.setLayout(tab3_layout)

        self.show()

    def init_model(self):
        try:
            if self.gauss_entry.text() != '':
                self.ngau = int(self.gauss_entry.text())
            if self.lorentz_entry.text() != '':
                self.nlor = int(self.lorentz_entry.text())
            if self.voigt_entry.text() != '':
                self.nvoi = int(self.voigt_entry.text())
            if self.line_entry.text() != '':
                self.nlin = int(self.line_entry.text())
        except:
            self.statusBar.showMessage(idx_error_msg, msg_length)
            return

        if self.nlin > 1:
            self.model = models.line_mod(self.nlin)
        else:
            self.model = models.line_mod(1)

        self.statusBar.showMessage(
                "Model updated: " + \
                str([self.ngau, self.nlor, self.nvoi, self.nlin]),
            msg_length
        )

    def guess_params(self):
        self.params = Parameters()
        self.clear_layout(self.params_layout)
        for comp in self.model.components:
            if comp.prefix.find('gau') != -1 or \
                    comp.prefix.find('lor') != -1 or \
                    comp.prefix.find('voi') != -1:

                c = comp.prefix + 'center'
                cval = self.data.iloc[:,self.xcol_idx].mean()
                cmin = self.data.iloc[:,self.xcol_idx].min()
                cmax = self.data.iloc[:,self.xcol_idx].max()
                self.params.add(c, cval, True, cmin, cmax)

                # add widgets (gau/lor/voi center)
                label = QLabel()
                entry = QLineEdit()
                label.setText(c)
                entry.setPlaceholderText(str(round(cval,5)))
                self.params_layout.addRow(label, entry)
                entry.returnPressed.connect(self.test_function)

                a = comp.prefix + 'amplitude'
                aval = self.data.iloc[:,self.ycol_idx].mean()
                amin = self.data.iloc[:,self.ycol_idx].min()
                amax = self.data.iloc[:,self.ycol_idx].max()
                self.params.add(a, aval, True, amin, amax)            
                # add widgets (gau/lor/voi amplitude)
                label = QLabel()
                entry = QLineEdit()
                label.setText(a)
                entry.setPlaceholderText(str(round(aval,5)))
                self.params_layout.addRow(label, entry)
                entry.returnPressed.connect(self.test_function)

                s = comp.prefix + 'sigma'
                sval = self.data.iloc[:,self.xcol_idx].std()
                self.params.add(s, sval, True)            
                # add widgets (gau/lor/voi sigma)
                label = QLabel()
                entry = QLineEdit()
                label.setText(s)
                entry.setPlaceholderText(str(round(sval,5)))
                self.params_layout.addRow(label, entry)
                entry.returnPressed.connect(self.test_function)

                f = comp.prefix + 'fraction'
                fval = 0.5
                if comp.prefix.find('voi') != -1:
                    self.params.add(f, fval, True)
                    # add widgets (voi fraction)
                    label = QLabel()
                    entry = QLineEdit()
                    label.setText(f)
                    entry.setPlaceholderText(str(round(fval,5)))
                    self.params_layout.addRow(label, entry)
                    entry.returnPressed.connect(self.test_function)
            else:
                slope = comp.prefix + 'slope'
                slopeval = self.data.iloc[:,self.ycol_idx].mean()
                self.params.add(slope, slopeval, True)
                intc = comp.prefix + 'intercept'
                intcval = self.data.iloc[:,self.ycol_idx].mean()
                self.params.add(intc, intcval, True)
                # add widgets (line slope)
                label = QLabel()
                entry = QLineEdit()
                label.setText(slope)
                entry.setPlaceholderText(str(round(slopeval,5)))
                self.params_layout.addRow(label, entry)
                entry.returnPressed.connect(self.test_function)
                # add widgets (line intercept)
                label = QLabel()
                entry = QLineEdit()
                label.setText(intc)
                entry.setPlaceholderText(str(round(intcval,5)))
                self.params_layout.addRow(label, entry)
                entry.returnPressed.connect(
                    self.test_function,
                )

    def test_function(self):
        print()


    def fit(self):
        self.init_model()
        if self.ngau != 0:
            self.model += models.gauss_mod(self.ngau) 
        if self.nlor != 0:
            self.model += models.lor_mod(self.nlor)
        if self.nvoi != 0:
            self.model += models.voigt_mod(self.nvoi)
        
        # adding this guessing function doesn't seem to help...
        self.guess_params()

        self.result = self.model.fit(
            data=self.data.iloc[:,self.ycol_idx],
            params=self.params,
            x=self.data.iloc[:,self.xcol_idx]
        )
        print(self.result.fit_report())
        self.plot()

    def xset_click(self):
        try:
            idx = int(self.xLineEntry.text())
        except:
            self.statusBar.showMessage(idx_error_msg, msg_length)
            return
        self.xcol_idx = idx
        self.plot()
        self.fit()
        self.statusBar.showMessage(
            'ColumnIndex(X) = ' + str(idx), msg_length
        )

    def yset_click(self):
        try:
            idx = int(self.yLineEntry.text())
        except:
            self.statusBar.showMessage(idx_error_msg, msg_length)
            return
        self.ycol_idx = idx
        self.plot()
        self.fit()
        self.statusBar.showMessage(
            'ColumnIndex(Y) = ' + str(idx), msg_length
        )

    def close_app(self):
        sys.exit()

    def get_data(self):
        # reset column indices
        # !!! need to clear the boxes as well...
        self.xcol_idx = 0
        self.ycol_idx = 1
        # open file dialog
        self.file_name,_ = QFileDialog.getOpenFileName(
            self, 'Open File', '', 'CSV files (*.csv)'
        )
        if self.file_name != '':
            # this message isn't showing up...
            self.statusBar.showMessage(
                'Importing .csv file: ' + self.file_name, msg_length
            )
            df = tools.to_df(self.file_name)
            self.data = df
        else:
            self.statusBar.showMessage(
                'Import cancelled.', msg_length
            )
            return

        self.table_model = PandasModel(self.data)
        self.tab2.setModel(self.table_model)
        self.tab2.resizeColumnsToContents()
        self.plot()
        self.statusBar.showMessage(
            'Import finished.', msg_length
        )


    def plot(self):
        x = self.data.iloc[:,self.xcol_idx].values
        y = self.data.iloc[:,self.ycol_idx].values
        self.tab1.figure.clear()
        ax = self.tab1.figure.add_subplot(111, label=self.file_name)
        ax.scatter(
            x, y, s=200, c='None',
            edgecolors='purple', linewidth=3
        )
        if self.result != None:
            yfit = self.result.best_fit.values
            ax.plot(x, yfit, c='r')
            cmap = cm.get_cmap('Dark2')
            components = self.result.eval_components()
            for i, comp in enumerate(components):
                ax.plot(
                    x, components[comp],
                    linewidth=2, linestyle='--',
                    c=cmap(i/len(components))
                )
        ax.set_xlabel(self.data.columns[self.xcol_idx], labelpad=10)
        ax.set_ylabel(self.data.columns[self.ycol_idx], labelpad=15)
        self.tab1.canvas.draw()

    def clear_layout(self, layout):
        if layout:
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget:
                    widget.deleteLater()
                else :
                    self.clear_layout(item.layout())
                layout.removeItem(item)


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

        return QVariant(str(self._df.iloc[index.row(), index.column()]))

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
