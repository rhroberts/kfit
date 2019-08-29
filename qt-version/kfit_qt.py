#!/usr/bin/env python3

import sys
import pyperclip
import pandas as pd
import numpy as np
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import matplotlib.cm as cm
# from kfit import models, tools
import models
import tools
from lmfit.model import Parameters
from PyQt5.QtGui import QIcon, QKeySequence
from PyQt5.QtCore import (Qt, QAbstractTableModel, QModelIndex,
                          QSize, QVariant, QEvent)
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout,
                             QStatusBar, QHBoxLayout, QApplication,
                             QPushButton, QProgressBar, QLabel,
                             QLineEdit, QTabWidget, QGridLayout,
                             QTableView, QSizePolicy, QScrollArea,
                             QLayout, QPlainTextEdit, QFileDialog,
                             QSplitter, QDialog, QCheckBox,
                             QShortcut)
from matplotlib.backends.backend_qt5agg import FigureCanvas, \
    NavigationToolbar2QT as NavigationToolbar
from matplotlib.widgets import Cursor

idx_type_error_msg = 'Error: Cannot convert index to integer!'
idx_range_error_msg = 'Error: Column index is out of range!'
file_import_error_msg = 'Error: Failed to import file with the given settings!'
msg_length = 2000


class App(QMainWindow):
    def __init__(self):
        super().__init__()
        self.title = 'kfit'
        self.left = 400
        self.top = 150
        self.width = 1200
        self.height = 800
        self.file_name = ''
        self.xcol_idx = 0
        self.ycol_idx = 1
        self.ngau = 0
        self.nlor = 0
        self.nvoi = 0
        self.nlin = 1
        self.model = None
        self.result = None
        self.curves_df = None
        self.params_df = None
        self.edit_mode = False
        # empty Parameters to hold parameter guesses/constraints
        self.params = Parameters()
        self.guesses = {
            'value': {},
            'min': {},
            'max': {}
        }
        self.usr_vals = {
            'value': {},
            'min': {},
            'max': {}
        }
        self.usr_entry_widgets = {}
        self.cid = None

        # file import settings
        self.sep = ','
        self.header = 'infer'
        self.index_col = None
        self.skiprows = None
        self.dtype = None
        self.encoding = None

        # keyboard shortcuts
        self.fit_shortcut = QShortcut(QKeySequence('Ctrl+F'), self)
        self.fit_shortcut.activated.connect(self.fit)
        self.reset_shortcut = QShortcut(QKeySequence('Ctrl+R'), self)
        self.reset_shortcut.activated.connect(self.hard_reset)
        self.save_fit = QShortcut(QKeySequence('Ctrl+S'), self)
        self.save_fit.activated.connect(self.export_results)
        self.add_gau = QShortcut(QKeySequence('G'), self)
        self.add_gau.activated.connect(lambda: self.increment('gau', True))
        self.add_gau.activated.connect(self.init_param_widgets)
        self.sub_gau = QShortcut(QKeySequence('Shift+G'), self)
        self.sub_gau.activated.connect(lambda: self.increment('gau', False))
        self.sub_gau.activated.connect(self.init_param_widgets)
        self.add_lor = QShortcut(QKeySequence('L'), self)
        self.add_lor.activated.connect(lambda: self.increment('lor', True))
        self.add_lor.activated.connect(self.init_param_widgets)
        self.sub_lor = QShortcut(QKeySequence('Shift+L'), self)
        self.sub_lor.activated.connect(lambda: self.increment('lor', False))
        self.sub_lor.activated.connect(self.init_param_widgets)
        self.add_voi = QShortcut(QKeySequence('V'), self)
        self.add_voi.activated.connect(lambda: self.increment('voi', True))
        self.add_voi.activated.connect(self.init_param_widgets)
        self.sub_voi = QShortcut(QKeySequence('Shift+V'), self)
        self.sub_voi.activated.connect(lambda: self.increment('voi', False))
        self.sub_voi.activated.connect(self.init_param_widgets)
        self.add_lin = QShortcut(QKeySequence('N'), self)
        self.add_lin.activated.connect(lambda: self.increment('lin', True))
        self.add_lin.activated.connect(self.init_param_widgets)
        self.sub_lin = QShortcut(QKeySequence('Shift+N'), self)
        self.sub_lin.activated.connect(lambda: self.increment('lin', False))
        self.sub_lin.activated.connect(self.init_param_widgets)

        # temporary data
        x = np.linspace(0, 10, 500)
        y = models.gauss(x, 0.5, 4, 0.4) + \
            models.gauss(x, 0.8, 5, 0.2) + \
            models.gauss(x, 0.4, 6, 0.3) + 0.2

        # set data
        self.data = pd.DataFrame([x, y]).T
        self.data.columns = ['x', 'y']
        self.x = self.data['x']
        self.y = self.data['y']
        self.xmin = self.data['x'].min()
        self.xmax = self.data['x'].max()

        self.initUI()

    def initUI(self):
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.setWindowTitle(self.title)
        self.setWindowIcon(QIcon('../images/K.png'))

        # set up the status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage('Welcome to kfit!', msg_length)
        self.status_bar.setStyleSheet('background-color: white')

        # Create the Main Widget and Layout
        self.main_layout = QVBoxLayout()
        self.main_widget = QSplitter()
        self.main_widget.setOrientation(Qt.Vertical)
        self.setCentralWidget(self.main_widget)

        # create "top bar" widget
        self.topbar_layout = QHBoxLayout()
        self.topbar_widget = QWidget()
        # fit button
        self.fit_button = QPushButton('Fit', self)
        self.fit_button.setMaximumWidth(100)
        self.fit_button.clicked.connect(self.fit)
        self.fit_button.installEventFilter(self)
        # import button
        self.import_button = QPushButton('Import', self)
        self.import_button.setMaximumWidth(100)
        self.import_button.clicked.connect(self.get_data)
        self.import_button.installEventFilter(self)
        # import settings button
        self.import_settings_button = QPushButton('', self)
        self.import_settings_button.setIcon(
            QIcon.fromTheme('stock_properties')
        )
        self.import_settings_button.setMaximumWidth(40)
        self.import_settings_button.clicked.connect(
            self.import_settings_dialog
        )
        self.import_settings_button.installEventFilter(self)
        # reset fit button
        self.reset_button = QPushButton('', self)
        self.reset_button.setIcon(QIcon.fromTheme('view-refresh'))
        self.reset_button.setMaximumWidth(40)
        self.reset_button.clicked.connect(self.hard_reset)
        self.reset_button.installEventFilter(self)
        # save results button
        self.save_button = QPushButton('', self)
        self.save_button.setIcon(QIcon.fromTheme('filesave'))
        self.save_button.setMaximumWidth(40)
        self.save_button.clicked.connect(self.export_results)
        self.save_button.installEventFilter(self)
        # progress bar
        self.progress_bar = QProgressBar()
        # self.progressBar.setMaximumWidth(150)
        self.progress_bar.hide()
        # get column header for x
        self.xlabel = QLabel(self)
        self.xlabel.setText('ColumnIndex(X):')
        self.xlabel.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        # self.xlabel.setMaximumWidth(250)
        self.xline_entry = QLineEdit(self)
        self.xline_entry.setText('0')
        self.xline_entry.setAlignment(Qt.AlignCenter)
        # self.xline_entry.setMaximumWidth(50)
        self.xline_entry.returnPressed.connect(self.column_index_set)
        # get column header for y
        self.ylabel = QLabel(self)
        self.ylabel.setText('ColumnIndex(Y):')
        self.ylabel.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        # self.ylabel.setMaximumWidth(100)
        self.yline_entry = QLineEdit(self)
        self.yline_entry.setText('1')
        self.yline_entry.setAlignment(Qt.AlignCenter)
        # self.yline_entry.setMaximumWidth(50)
        self.yline_entry.returnPressed.connect(self.column_index_set)
        # add topbar widgets to layout
        self.topbar_layout.addSpacing(600)
        self.topbar_layout.addWidget(self.xlabel)
        self.topbar_layout.addWidget(self.xline_entry)
        self.topbar_layout.addWidget(self.ylabel)
        self.topbar_layout.addWidget(self.yline_entry)
        self.topbar_layout.addWidget(self.fit_button)
        self.topbar_layout.addWidget(self.import_button)
        self.topbar_layout.addWidget(self.import_settings_button)
        self.topbar_layout.addWidget(self.reset_button)
        self.topbar_layout.addWidget(self.save_button)
        self.topbar_layout.addWidget(self.progress_bar)
        self.topbar_layout.setAlignment(Qt.AlignRight)
        self.topbar_widget.setLayout(self.topbar_layout)
        self.topbar_widget.setMaximumHeight(75)

        # create tabs widget
        self.tabs = QTabWidget(self)
        self.tab1 = QWidget(self)
        self.tab2 = QTableView(self)
        self.tab3 = QWidget(self)
        self.tabs.addTab(self.tab1, 'Graph')
        self.tabs.addTab(self.tab2, 'Data')
        self.tabs.addTab(self.tab3, 'Output')
        self.tabs.setMinimumHeight(300)

        # create params widget
        self.params_widget = QSplitter()
        self.gau_layout = QVBoxLayout()
        self.gau_layout.setAlignment(Qt.AlignTop)
        self.gau_widget = QWidget()
        self.gau_widget.setLayout(self.gau_layout)
        self.gau_widget.setSizePolicy(
            QSizePolicy.Expanding, QSizePolicy.Expanding
        )
        self.gau_scroll = QScrollArea()
        self.gau_scroll.setWidget(self.gau_widget)
        self.gau_scroll.setWidgetResizable(True)
        self.lor_widget = QWidget()
        self.lor_layout = QVBoxLayout()
        self.lor_layout.setAlignment(Qt.AlignTop)
        self.lor_widget.setLayout(self.lor_layout)
        self.lor_widget.setSizePolicy(
            QSizePolicy.Expanding, QSizePolicy.Expanding
        )
        self.lor_scroll = QScrollArea()
        self.lor_scroll.setWidget(self.lor_widget)
        self.lor_scroll.setWidgetResizable(True)
        self.voi_widget = QWidget()
        self.voi_layout = QVBoxLayout()
        self.voi_layout.setAlignment(Qt.AlignTop)
        self.voi_widget.setLayout(self.voi_layout)
        self.voi_widget.setSizePolicy(
            QSizePolicy.Expanding, QSizePolicy.Expanding
        )
        self.voi_scroll = QScrollArea()
        self.voi_scroll.setWidget(self.voi_widget)
        self.voi_scroll.setWidgetResizable(True)
        self.lin_widget = QWidget()
        self.lin_layout = QVBoxLayout()
        self.lin_layout.setAlignment(Qt.AlignTop)
        self.lin_widget.setLayout(self.lin_layout)
        self.lin_widget.setSizePolicy(
            QSizePolicy.Expanding, QSizePolicy.Expanding
        )
        self.lin_scroll = QScrollArea()
        self.lin_scroll.setWidget(self.lin_widget)
        self.lin_scroll.setWidgetResizable(True)
        self.params_widget.addWidget(self.gau_scroll)
        self.params_widget.addWidget(self.lor_scroll)
        self.params_widget.addWidget(self.voi_scroll)
        self.params_widget.addWidget(self.lin_scroll)
        self.params_widget.setMinimumHeight(180)

        # add everything to main widget
        self.main_widget.addWidget(self.topbar_widget)
        self.main_widget.addWidget(self.tabs)
        self.main_widget.addWidget(self.params_widget)

        # Tab 1 - Graph / Model
        # Graph
        plt.style.use('fivethirtyeight')
        self.tab1.figure = Figure(figsize=(8, 6),  dpi=60)
        self.tab1.canvas = FigureCanvas(self.tab1.figure)
        self.tab1.toolbar = NavigationToolbar(self.tab1.canvas, self)
        # tristate checkbox for edit mode
        self.emode_box = QCheckBox()
        self.emode_box.setTristate(True)
        self.emode_box.setIcon(QIcon.fromTheme('stock_edit'))
        self.emode_box.stateChanged.connect(self.toggle_edit_mode)
        self.emode_box.installEventFilter(self)
        # tweaking the toolbar layout
        self.tab1.toolbar.setIconSize(QSize(18, 18))
        spacer = QWidget()
        spacer.setFixedWidth(20)
        self.tab1.toolbar.addWidget(spacer)
        self.tab1.toolbar.addWidget(self.emode_box)
        self.tab1.toolbar.locLabel.setAlignment(Qt.AlignRight | Qt.AlignCenter)
        graph_layout = QVBoxLayout()
        graph_layout.addWidget(self.tab1.toolbar)
        graph_layout.addWidget(self.tab1.canvas)

        # The "Set Model" layout
        model_layout = QGridLayout()
        widget_setgau = QWidget()
        layout_setgau = QHBoxLayout()
        layout_setgau.setSizeConstraint(QLayout.SetFixedSize)
        widget_setgau.setLayout(layout_setgau)
        widget_setlor = QWidget()
        layout_setlor = QHBoxLayout()
        layout_setlor.setSizeConstraint(QLayout.SetFixedSize)
        widget_setlor.setLayout(layout_setlor)
        widget_setvoi = QWidget()
        layout_setvoi = QHBoxLayout()
        layout_setvoi.setSizeConstraint(QLayout.SetFixedSize)
        widget_setvoi.setLayout(layout_setvoi)
        widget_setlin = QWidget()
        layout_setlin = QHBoxLayout()
        layout_setlin.setSizeConstraint(QLayout.SetFixedSize)
        widget_setlin.setLayout(layout_setlin)
        model_layout.addWidget(widget_setgau, 0, 0)
        model_layout.addWidget(widget_setlor, 0, 1)
        model_layout.addWidget(widget_setvoi, 0, 2)
        model_layout.addWidget(widget_setlin, 0, 3)

        # specify number of gaussian curves
        gauss_label = QLabel(self)
        gauss_label.setText('Gaussians')
        gauss_label.setAlignment(Qt.AlignVCenter)
        gauss_button_add = QPushButton('', self)
        gauss_button_add.setIcon(QIcon.fromTheme('list-add'))
        gauss_button_add.clicked.connect(
            lambda: self.increment('gau', True)
        )
        gauss_button_add.clicked.connect(self.init_param_widgets)
        gauss_button_sub = QPushButton('', self)
        gauss_button_sub.setIcon(QIcon.fromTheme('list-remove'))
        gauss_button_sub.clicked.connect(
            lambda: self.increment('gau', False)
        )
        gauss_button_sub.clicked.connect(self.init_param_widgets)
        layout_setgau.addWidget(gauss_label)
        layout_setgau.addWidget(gauss_button_add)
        layout_setgau.addWidget(gauss_button_sub)
        # specify number of lorentzian curves
        lorentz_label = QLabel(self)
        lorentz_label.setText('Lorentzians')
        lorentz_label.setAlignment(Qt.AlignVCenter)
        lorentz_button_add = QPushButton('', self)
        lorentz_button_add.setIcon(QIcon.fromTheme('list-add'))
        lorentz_button_add.clicked.connect(
            lambda: self.increment('lor', True)
        )
        lorentz_button_add.clicked.connect(self.init_param_widgets)
        lorentz_button_sub = QPushButton('', self)
        lorentz_button_sub.setIcon(QIcon.fromTheme('list-remove'))
        lorentz_button_sub.clicked.connect(
            lambda: self.increment('lor', False)
        )
        lorentz_button_sub.clicked.connect(self.init_param_widgets)
        layout_setlor.addWidget(lorentz_label)
        layout_setlor.addWidget(lorentz_button_add)
        layout_setlor.addWidget(lorentz_button_sub)
        # specify number of voigt curves
        voigt_label = QLabel(self)
        voigt_label.setText('Pseudo-Voigts')
        voigt_label.setAlignment(Qt.AlignVCenter)
        voigt_button_add = QPushButton('', self)
        voigt_button_add.setIcon(QIcon.fromTheme('list-add'))
        voigt_button_add.clicked.connect(
            lambda: self.increment('voi', True)
        )
        voigt_button_add.clicked.connect(self.init_param_widgets)
        voigt_button_sub = QPushButton('', self)
        voigt_button_sub.setIcon(QIcon.fromTheme('list-remove'))
        voigt_button_sub.clicked.connect(
            lambda: self.increment('voi', False)
        )
        voigt_button_sub.clicked.connect(self.init_param_widgets)
        layout_setvoi.addWidget(voigt_label)
        layout_setvoi.addWidget(voigt_button_add)
        layout_setvoi.addWidget(voigt_button_sub)
        # specify number of lines
        line_label = QLabel(self)
        line_label.setText('Lines:')
        line_label.setAlignment(Qt.AlignVCenter)
        line_button_add = QPushButton('', self)
        line_button_add.setIcon(QIcon.fromTheme('list-add'))
        line_button_add.clicked.connect(
            lambda: self.increment('lin', True)
        )
        line_button_add.clicked.connect(self.init_param_widgets)
        line_button_sub = QPushButton('', self)
        line_button_sub.setIcon(QIcon.fromTheme('list-remove'))
        line_button_sub.clicked.connect(
            lambda: self.increment('lin', False)
        )
        line_button_sub.clicked.connect(self.init_param_widgets)
        layout_setlin.addWidget(line_label)
        layout_setlin.addWidget(line_button_add)
        layout_setlin.addWidget(line_button_sub)

        graph_layout.addLayout(model_layout)
        self.tab1.setLayout(graph_layout)
        self.plot()

        # Tab 2 - Data Table
        self.table_model = PandasModel(self.data)
        self.tab2.setModel(self.table_model)
        self.tab2.resizeColumnsToContents()

        # Tab 3 - Output
        self.tab3_widget = QPlainTextEdit()
        tab3_layout = QVBoxLayout()
        tab3_layout.addWidget(self.tab3_widget)
        self.tab3.setLayout(tab3_layout)

        self.init_param_widgets()
        self.show()

    def export_results(self):
        self.process_results()
        # open file dialog
        exp_file_name, _ = QFileDialog.getSaveFileName(
            self, 'QFileDialog.getSaveFileName()', 'fit_results.csv',
            'CSV files (*.csv)',
        )
        if exp_file_name:
            self.process_results()
            self.curves_df.to_csv(exp_file_name)
            # NOTE: if user chooses a file extension other than .csv, or does
            # not use a file extension, this should still work, but I haven't
            # tested too rigorously yet
            self.params_df.to_csv(
                '{}.params.csv'.format(
                    exp_file_name[:exp_file_name.find('.csv')]
                )
            )
            self.status_bar.showMessage(
                'Exported fit results to: ' +
                exp_file_name, 2*msg_length
            )
        else:
            self.status_bar.showMessage(
                'Export canceled.', 2*msg_length
            )
            return

    def process_results(self):
        if self.result is not None:
            self.params_df = pd.DataFrame.from_dict(
                self.result.best_values, orient='index'
            )
            self.params_df.index.name = 'parameter'
            self.params_df.columns = ['value']
            curves_dict = {
                'data': self.y,
                'total_fit': self.result.best_fit,
            }
            components = self.result.eval_components()
            for i, comp in enumerate(components):
                curves_dict[comp[:comp.find('_')]] = components[comp]
            self.curves_df = pd.DataFrame.from_dict(curves_dict)
            self.curves_df.index = self.x
            self.curves_df.index.name = self.data.columns[self.xcol_idx]
        else:
            self.status_bar.showMessage(
                'No fit results to export!', msg_length
            )

    def eventFilter(self, object, event):
        if event.type() == QEvent.Enter:
            if object is self.reset_button:
                self.status_bar.showMessage("Reset fit")
            if object is self.import_settings_button:
                self.status_bar.showMessage("File import settings")
            if object is self.import_button:
                self.status_bar.showMessage("Import .csv file")
            if object is self.fit_button:
                self.status_bar.showMessage("Fit data")
            if object is self.emode_box:
                self.status_bar.showMessage("Toggle edit mode")
            if object is self.save_button:
                self.status_bar.showMessage("Export fit results")
            return True
        elif event.type() == QEvent.Leave:
            self.status_bar.showMessage(None)
        return False

    def init_model(self):
        # increment() ensures nlin >= 1
        self.model = models.line_mod(self.nlin)
        if self.ngau != 0:
            self.model += models.gauss_mod(self.ngau)
        if self.nlor != 0:
            self.model += models.lor_mod(self.nlor)
        if self.nvoi != 0:
            self.model += models.voigt_mod(self.nvoi)
        self.status_bar.showMessage(
                "Model updated: " +
                str([self.ngau, self.nlor, self.nvoi, self.nlin]),
                msg_length
        )

    def init_param_widgets(self):
        self.init_model()
        self.usr_entry_widgets = {
            'value': {},
            'min': {},
            'max': {}
        }
        labels = {}
        rnd = 3  # decimals to round to in placeholder text
        self.clear_fit_layouts()

        for param_name in self.model.param_names:
            # set param label text
            labels[param_name] = QLabel()
            labels[param_name].setText(param_name)

            # make qlineedit widgets
            for key in self.usr_entry_widgets:
                self.usr_entry_widgets[key][param_name] = QLineEdit()
                if param_name in self.usr_vals[key]:
                    self.usr_entry_widgets[key][param_name]\
                        .setPlaceholderText(
                            str(round(self.usr_vals[key][param_name], rnd))
                        )
                else:
                    self.usr_entry_widgets[key][param_name]\
                        .setPlaceholderText(key)
                # set up connections
                # connect() expects a callable func, hence the lambda
                self.usr_entry_widgets[key][param_name].returnPressed.connect(
                    lambda: self.update_usr_vals(self.usr_entry_widgets)
                )

            # add widgets to respective layouts
            sublayout1 = QVBoxLayout()
            sublayout2 = QHBoxLayout()
            sublayout1.addWidget(labels[param_name])
            for key in self.usr_entry_widgets:
                sublayout2.addWidget(
                    self.usr_entry_widgets[key][param_name]
                )
            if param_name.find('gau') != -1:
                self.gau_layout.addLayout(sublayout1)
                self.gau_layout.addLayout(sublayout2)
            if param_name.find('lor') != -1:
                self.lor_layout.addLayout(sublayout1)
                self.lor_layout.addLayout(sublayout2)
            if param_name.find('voi') != -1:
                self.voi_layout.addLayout(sublayout1)
                self.voi_layout.addLayout(sublayout2)
            if param_name.find('lin') != -1:
                self.lin_layout.addLayout(sublayout1)
                self.lin_layout.addLayout(sublayout2)

        # Resize all of the LineEntry widgets
        for key in self.usr_entry_widgets:
            for param, widget in self.usr_entry_widgets[key].items():
                widget.setMaximumWidth(150)

        if self.result is not None:
            self.set_params()
            self.update_param_widgets()

    def update_usr_vals(self, entry):
        # get text input from each usr_entry_widget
        for val_type, param_dict in self.usr_entry_widgets.items():
            for param, param_widget in param_dict.items():
                try:
                    self.usr_vals[val_type][param] = \
                        float(param_widget.text())
                except Exception:
                    pass

    def update_param_widgets(self):
        rnd = 3
        # the 'value' placeholder text is the result for that param
        # taken from self.result
        # the 'min' and 'max' text is from either the self.guesses
        # or from self.usr_vals
        for param in self.params:
            if param in self.result.best_values:
                self.usr_entry_widgets['value'][param].setPlaceholderText(
                    str(round(self.result.best_values[param], rnd))
                )
                self.usr_entry_widgets['min'][param].setPlaceholderText(
                    str(round(self.params[param].min, rnd))
                )
                self.usr_entry_widgets['max'][param].setPlaceholderText(
                    str(round(self.params[param].max, rnd))
                )

    def guess_params(self):
        for comp in self.model.components:
            if comp.prefix.find('gau') != -1 or \
                    comp.prefix.find('lor') != -1 or \
                    comp.prefix.find('voi') != -1:

                # need to define explicitly to make proper guesses
                c = comp.prefix + 'center'
                a = comp.prefix + 'amplitude'
                s = comp.prefix + 'sigma'
                f = comp.prefix + 'fraction'

                self.guesses['value'][c] = \
                    self.data.iloc[:, self.xcol_idx].mean()
                self.guesses['value'][a] = \
                    self.data.iloc[:, self.ycol_idx].mean()
                self.guesses['value'][s] = \
                    self.data.iloc[:, self.xcol_idx].std()
                self.guesses['min'][c] = None
                self.guesses['min'][a] = 0
                self.guesses['min'][s] = 0
                self.guesses['max'][c] = None
                self.guesses['max'][a] = None
                self.guesses['max'][s] = None

                if comp.prefix.find('voi') != -1:
                    self.guesses['value'][f] = 0.5
                    self.guesses['min'][f] = 0
                    self.guesses['max'][f] = 1
            else:
                slope = comp.prefix + 'slope'
                intc = comp.prefix + 'intercept'
                for p in [slope, intc]:
                    self.guesses['value'][p] = \
                        self.data.iloc[:, self.ycol_idx].mean()
                    self.guesses['min'][p] = None
                    self.guesses['max'][p] = None

    def set_params(self):
        self.params = Parameters()
        self.guess_params()
        self.update_usr_vals(self.usr_entry_widgets)
        vals = {}

        # fill params with any user-entered values
        # fill in blanks with guesses
        for param_name in self.model.param_names:
            for val_type in ['value', 'min', 'max']:
                if param_name in self.usr_vals[val_type]:
                    vals[val_type] = self.usr_vals[val_type][param_name]
                    # print('param: ' + param_name + ', type: ' +\
                    #         val_type + ', set_by: user')
                else:
                    vals[val_type] = self.guesses[val_type][param_name]
                    # print('param: ' + param_name + ', type: ' +\
                    #         val_type + ', set_by: guess')
            self.params.add(
                name=param_name, value=vals['value'], vary=True,
                min=vals['min'], max=vals['max']
            )

    def set_xy_range(self):
        self.x = self.data.iloc[:, self.xcol_idx]
        self.y = self.data.iloc[:, self.ycol_idx]
        self.xmin, self.xmax = self.ax.get_xlim()
        range_bool = (self.x >= self.xmin) & (self.x <= self.xmax)
        self.x = self.x[range_bool].values
        self.y = self.y[range_bool].values

    def reset_xy_range(self):
        self.xmin = np.min(self.x)
        self.xmax = np.max(self.x)

    def fit(self):
        self.emode_box.setCheckState(0)
        self.toggle_edit_mode()
        self.set_xy_range()
        self.set_params()
        self.result = self.model.fit(
            data=self.y, params=self.params, x=self.x,
            method='least_squares'
        )
        self.tab3_widget.clear()
        self.tab3_widget.insertPlainText(self.result.fit_report())
        self.plot()
        # overwrite widgets to clear input (not ideal method..)
        self.init_param_widgets()
        # update widgets with new placeholder text
        self.update_param_widgets()

    def column_index_set(self):
        # make sure user enters index that can be converted to int
        try:
            idx_x = int(self.xline_entry.text())
        except ValueError:
            self.status_bar.showMessage(idx_type_error_msg, msg_length)
            self.xline_entry.setText(None)
            return
        try:
            idx_y = int(self.yline_entry.text())
        except ValueError:
            self.status_bar.showMessage(idx_type_error_msg, msg_length)
            self.yline_entry.setText(None)
            return
        self.xcol_idx = idx_x
        self.ycol_idx = idx_y
        self.result = None
        # make sure user enters an index that's in the data range
        try:
            self.x = self.data.iloc[:, self.xcol_idx]
        except IndexError:
            self.status_bar.showMessage(idx_range_error_msg, msg_length)
            self.xline_entry.setText(None)
            return
        try:
            self.y = self.data.iloc[:, self.ycol_idx]
        except IndexError:
            self.status_bar.showMessage(idx_range_error_msg, msg_length)
            self.yline_entry.setText(None)
            return
        self.xmin = np.min(self.x)
        self.xmax = np.max(self.x)
        self.plot()
        self.status_bar.showMessage(
            'ColumnIndex(X) = ' + str(idx_x) + ', ' +
            'ColumnIndex(Y) = ' + str(idx_y),
            msg_length
        )

    def toggle_edit_mode(self):
        # first toggle off the zoom or pan button
        # so they don't interfere with edit_mode cursor style
        if self.tab1.toolbar._active == 'ZOOM':
            self.tab1.toolbar.zoom()
        if self.tab1.toolbar._active == 'PAN':
            self.tab1.toolbar.pan()
        states = {
            0: 'Edit mode off',
            1: 'Edit mode on | copy x-value',
            2: 'Edit mode on | copy y-value',
        }
        self.status_bar.showMessage(
            states[self.emode_box.checkState()], msg_length
        )
        if self.emode_box.checkState() == 0:
            self.mpl_cursor = None
            self.tab1.canvas.mpl_disconnect(self.cid)
        if self.emode_box.checkState() == 1:
            self.mpl_cursor = Cursor(
                self.ax, lw=1, c='red', linestyle='--'
            )
            self.cid = self.tab1.canvas.mpl_connect(
                'button_press_event', self.get_coord_click
            )
        if self.emode_box.checkState() == 2:
            self.cid = self.tab1.canvas.mpl_connect(
                'button_press_event', self.get_coord_click
            )

    def get_coord_click(self, event):
        self.x_edit, self.y_edit = round(event.xdata, 3), round(event.ydata, 3)
        if self.emode_box.checkState() == 1:
            pyperclip.copy(self.x_edit)
            self.status_bar.showMessage(
                    'Copied X=' + str(self.x_edit) + ' to clipboard!',
                    msg_length
            )
        if self.emode_box.checkState() == 2:
            pyperclip.copy(self.y_edit)
            self.status_bar.showMessage(
                    'Copied Y=' + str(self.y_edit) + ' to clipboard!',
                    msg_length
            )

    def close_app(self):
        sys.exit()

    def get_data(self):
        self.emode_box.setCheckState(0)
        self.toggle_edit_mode()
        # reset column indices
        self.xcol_idx = 0
        self.ycol_idx = 1
        # open file dialog
        self.file_name, _ = QFileDialog.getOpenFileName(
            self, 'Open File', '', 'CSV files (*.csv);; All Files (*)'
        )
        if self.file_name:
            # this message isn't showing up...
            # TODO: needs to be threaded
            self.status_bar.showMessage(
                'Importing: ' + self.file_name, msg_length
            )
            try:
                df = tools.to_df(
                    self.file_name, sep=self.sep, header=self.header,
                    index_col=self.index_col, skiprows=self.skiprows,
                    dtype=self.dtype, encoding=self.encoding
                )
                df.iloc[:, self.xcol_idx]
                df.iloc[:, self.ycol_idx]
            except Exception:
                self.status_bar.showMessage(
                    file_import_error_msg, 2*msg_length
                )
                return
        else:
            self.status_bar.showMessage(
                'Import canceled.', msg_length
            )
            return

        self.data = df
        self.table_model = PandasModel(self.data)
        self.tab2.setModel(self.table_model)
        self.tab2.resizeColumnsToContents()
        # clear any previous fit result
        self.result = None
        # reset x, y, and xlim
        self.x = self.data.iloc[:, self.xcol_idx].values
        self.y = self.data.iloc[:, self.ycol_idx].values
        self.xmin = self.data.iloc[:, self.xcol_idx].min()
        self.xmax = self.data.iloc[:, self.xcol_idx].max()
        self.plot()
        self.status_bar.showMessage(
            'Import finished.', msg_length
        )

    def import_settings_dialog(self):
        self.dialog_window = QDialog()
        self.dialog_window.setWindowTitle('File Import Settings')
        toplevel = QVBoxLayout()
        dialog_layout = QHBoxLayout()
        label_layout = QVBoxLayout()
        entry_layout = QVBoxLayout()
        button_layout = QVBoxLayout()
        label1 = QLabel(self.dialog_window)
        label1.setText('sep')
        label2 = QLabel(self.dialog_window)
        label2.setText('header')
        label3 = QLabel(self.dialog_window)
        label3.setText('skiprows')
        label4 = QLabel(self.dialog_window)
        label4.setText('dtype')
        label5 = QLabel(self.dialog_window)
        label5.setText('encoding')
        for lbl in [label1, label2, label3, label4, label5]:
            label_layout.addWidget(lbl)
        self.sep_edit = QLineEdit(self.dialog_window)
        self.head_edit = QLineEdit(self.dialog_window)
        self.skipr_edit = QLineEdit(self.dialog_window)
        self.dtype_edit = QLineEdit(self.dialog_window)
        self.enc_edit = QLineEdit(self.dialog_window)
        self.sep_edit.setText(self.sep)
        self.head_edit.setText(self.header)
        # if value is None, show text as 'None'
        if self.skiprows is not None:
            self.skipr_edit.setText(self.skiprows)
        else:
            self.skipr_edit.setText('None')
        if self.dtype is not None:
            self.dtype_edit.setText(self.dtype)
        else:
            self.dtype_edit.setText('None')
        if self.encoding is not None:
            self.enc_edit.setText(self.encoding)
        else:
            self.enc_edit.setText('None')

        # add widgets to layout
        for ewidget in [self.sep_edit, self.head_edit, self.skipr_edit,
                        self.dtype_edit, self.enc_edit]:
            ewidget.setAlignment(Qt.AlignCenter)
            entry_layout.addWidget(ewidget)

        button1 = QPushButton('Set', self.dialog_window)
        button2 = QPushButton('Set', self.dialog_window)
        button3 = QPushButton('Set', self.dialog_window)
        button4 = QPushButton('Set', self.dialog_window)
        button5 = QPushButton('Set', self.dialog_window)
        for btn in [button1, button2, button3, button4, button5]:
            btn.clicked.connect(self.set_import_settings)
            button_layout.addWidget(btn)

        reflabel = QLabel(self.dialog_window)
        reflabel.setText(
            "for help, refer to <a href='https://pandas.pydata.org/" +
            "pandas-docs/stable/reference/api/" +
            "pandas.read_csv.html'>pandas.read_csv()</a>"
        )
        reflabel.setOpenExternalLinks(True)
        reflabel.setAlignment(Qt.AlignCenter)
        for lo in [label_layout, entry_layout, button_layout]:
            dialog_layout.addLayout(lo)
        toplevel.addLayout(dialog_layout)
        toplevel.addSpacing(25)
        toplevel.addWidget(reflabel)
        self.dialog_window.setLayout(toplevel)
        self.dialog_window.setWindowModality(Qt.ApplicationModal)
        self.dialog_window.exec_()

    def set_import_settings(self):
        self.sep = self.sep_edit.text()
        self.header = self.head_edit.text()
        # convert 'None' entries to None
        if self.skipr_edit.text() == 'None':
            self.skiprows = None
        else:
            self.skiprows = self.skipr_edit.text()
        if self.dtype_edit.text() == 'None':
            self.dtype = None
        else:
            self.dtype = self.dtype_edit.text()
        if self.enc_edit.text() == 'None':
            self.encoding = None
        else:
            self.encoding = self.enc_edit.text()

    def plot(self):
        self.tab1.figure.clear()
        self.ax = self.tab1.figure.add_subplot(111, label=self.file_name)
        self.ax.scatter(
            self.x, self.y, s=100, c='None',
            edgecolors='black', linewidth=1,
            label='data'
        )
        if self.result is not None:
            yfit = self.result.best_fit
            self.ax.plot(self.x, yfit, c='r', linewidth=2.5)
            cmap = cm.get_cmap('gnuplot')
            components = self.result.eval_components()
            for i, comp in enumerate(components):
                self.ax.plot(
                    self.x, components[comp],
                    linewidth=2.5, linestyle='--',
                    c=cmap(i/len(components)),
                    label=comp[:comp.find('_')]
                )
        self.ax.set_xlabel(self.data.columns[self.xcol_idx], labelpad=15)
        self.ax.set_ylabel(self.data.columns[self.ycol_idx], labelpad=15)
        self.ax.set_xlim([self.xmin, self.xmax])
        self.ax.legend(loc='upper right')
        self.tab1.figure.subplots_adjust(bottom=0.15, left=0.06, right=0.94)
        self.tab1.canvas.draw()

    def clear_layout(self, layout):
        if layout:
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget:
                    widget.deleteLater()
                else:
                    self.clear_layout(item.layout())
                layout.removeItem(item)

    def clear_fit_layouts(self):
        for layout in [
            self.gau_layout, self.lor_layout,
            self.voi_layout, self.lin_layout
        ]:
            self.clear_layout(layout)

    def hard_reset(self):
        self.clear_fit_layouts()
        self.ngau = 0
        self.nlor = 0
        self.nvoi = 0
        self.nlin = 1
        self.init_model()
        self.params = Parameters()
        self.result = None
        self.params_df = None
        self.curves_df = None
        self.guesses = {
            'value': {},
            'min': {},
            'max': {}
        }
        self.usr_vals = {
            'value': {},
            'min': {},
            'max': {}
        }
        self.init_param_widgets()
        self.plot()

    def increment(self, val, add):
        if add:
            if val == 'gau':
                self.ngau += 1
            if val == 'lor':
                self.nlor += 1
            if val == 'voi':
                self.nvoi += 1
            if val == 'lin':
                self.nlin += 1
        if not add:
            if val == 'gau':
                self.ngau -= 1
            if val == 'lor':
                self.nlor -= 1
            if val == 'voi':
                self.nvoi -= 1
            if val == 'lin':
                self.nlin -= 1

        # make sure value doesn't go below zero
        if self.ngau < 0:
            self.ngau = 0
        if self.nlor < 0:
            self.nlor = 0
        if self.nvoi < 0:
            self.nvoi = 0
        if self.nlin < 1:
            self.nlin = 1


class PandasModel(QAbstractTableModel):
    def __init__(self, df=pd.DataFrame(), parent=None):
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
        self._df.sort_values(
            colname, ascending=order == Qt.AscendingOrder, inplace=True
        )
        self._df.reset_index(inplace=True, drop=True)
        self.layoutChanged.emit()


def run():
    qapp = QApplication(sys.argv)
    App().show()
    sys.exit(qapp.exec_())


if __name__ == '__main__':
    run()
