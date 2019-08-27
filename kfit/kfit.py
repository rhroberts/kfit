#!/usr/bin/env python3

import os
from matplotlib import cm
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_gtk3cairo import (
    FigureCanvasGTK3Cairo as FigureCanvas)
from custom_backend_gtk3 import (
    NavigationToolbar2GTK3 as NavigationToolbar)
import pandas as pd
import numpy as np
from lmfit.model import Parameters
import models
import tools
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

curr_dir = os.path.abspath(os.path.dirname(__file__))
idx_type_error_msg = 'Error: Cannot convert index to integer!'
idx_range_error_msg = 'Error: Column index is out of range!'
file_import_error_msg = 'Error: Failed to import file with the given settings!'
msg_length = 2000
pad = 3


class App(Gtk.Application):

    def __init__(self):
        '''
        Build GUI
        '''
        # build GUI from glade file
        self.builder = Gtk.Builder()
        self.glade_file = os.path.join(curr_dir, 'kfit.glade')
        self.builder.add_from_file(self.glade_file)
        # get the necessary ui objects
        self.window = self.builder.get_object('main_window')
        self.graph_box = self.builder.get_object('graph_box')
        self.gau_sw = self.builder.get_object('param_scroll_gau')
        self.lor_sw = self.builder.get_object('param_scroll_lor')
        self.voi_sw = self.builder.get_object('param_scroll_voi')
        self.lin_sw = self.builder.get_object('param_scroll_lin')
        self.param_viewport_gau = self.builder.get_object('param_viewport_gau')
        self.param_viewport_lor = self.builder.get_object('param_viewport_lor')
        self.param_viewport_voi = self.builder.get_object('param_viewport_voi')
        self.param_viewport_lin = self.builder.get_object('param_viewport_lin')
        self.statusbar_viewport = self.builder.get_object('statusbar_viewport')
        self.data_treeview = self.builder.get_object('data_treeview')
        self.column_entry_x = self.builder.get_object('column_entry_x')
        self.column_entry_y = self.builder.get_object('column_entry_y')
        self.graph_box = self.builder.get_object('graph_box')
        self.fname_textview = self.builder.get_object('fname_textview')
        self.fit_button = self.builder.get_object('fit_button')
        self.reset_button = self.builder.get_object('reset_button')
        self.settings_button = self.builder.get_object('settings_button')
        self.import_button = self.builder.get_object('import_button')
        self.save_button = self.builder.get_object('save_button')
        self.output_textview = self.builder.get_object('output_textview')

        # define class attributes
        self.title = 'kfit'
        self.file_name = ''
        self.xcol_idx = 0
        self.ycol_idx = 1
        self.edit_mode = False

        # for graph...
        x = np.linspace(0, 10, 500)
        y = models.gauss(x, 0.5, 4, 0.4) + \
            models.gauss(x, 0.8, 5, 0.2) + \
            models.gauss(x, 0.4, 6, 0.3) + 0.2
        self.data = pd.DataFrame([x, y]).T
        self.data.columns = ['x', 'y']
        self.x = self.data['x'].values
        self.y = self.data['y'].values
        self.xmin = self.data['x'].min()
        self.xmax = self.data['x'].max()
        plt.style.use(os.path.join(curr_dir, 'kfit.mplstyle'))
        self.figure = Figure(figsize=(10, 4), dpi=60)
        self.canvas = FigureCanvas(self.figure)
        self.canvas.set_size_request(900, 400)
        self.toolbar = NavigationToolbar(self.canvas, self.window)
        self.graph_box.pack_start(self.toolbar, True, True, 0)
        self.graph_box.pack_start(self.canvas, True, True, 0)

        # for fit...
        self.model = None
        self.result = None
        self.ngau = 0
        self.nlor = 0
        self.nvoi = 0
        self.nlin = 1
        self.curves_df = None
        self.params_df = None
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

        # for data view...
        self.fname_buffer = Gtk.TextBuffer()
        self.display_data()

        # for output...
        self.output_buffer = Gtk.TextBuffer()
        self.output_textview.set_buffer(self.output_buffer)

        # file import settings
        self.sep = ','
        self.header = 'infer'
        self.index_col = None
        self.skiprows = None
        self.dtype = None
        self.encoding = None

        # show initial plot
        self.plot()

        # add statusbar
        self.statusbar = Gtk.Statusbar()
        self.statusbar.set_margin_top(0)
        self.statusbar.set_margin_bottom(0)
        self.statusbar.set_margin_start(0)
        self.statusbar.set_margin_end(0)
        self.statusbar_viewport.add(self.statusbar)

        # connect signals
        events = {
            'on_fit_button_clicked': self.fit,
            'on_import_button_clicked': self.get_data,
            'on_reset_button_clicked': self.hard_reset,
            'on_add_gau_clicked': self.on_add_gau_clicked,
            'on_rem_gau_clicked': self.on_rem_gau_clicked,
            'on_add_lor_clicked': self.on_add_lor_clicked,
            'on_rem_lor_clicked': self.on_rem_lor_clicked,
            'on_add_voi_clicked': self.on_add_voi_clicked,
            'on_rem_voi_clicked': self.on_rem_voi_clicked,
            'on_add_lin_clicked': self.on_add_lin_clicked,
            'on_rem_lin_clicked': self.on_rem_lin_clicked,
            'on_column_entry_changed': self.column_index_set,
        }
        self.builder.connect_signals(events)

        # add accelerators / keyboard shortcuts
        self.accelerators = Gtk.AccelGroup()
        self.window.add_accel_group(self.accelerators)
        self.add_accelerator(self.fit_button, "<Control>f")
        self.add_accelerator(self.reset_button, "<Control>r")
        self.add_accelerator(self.settings_button, "<Control>p")
        self.add_accelerator(self.import_button, "<Control>o")
        self.add_accelerator(self.save_button, "<Control>s")

        # configure interface
        self.window.connect('destroy', Gtk.main_quit)

        self.init_param_widgets()
        # show the app window
        self.window.show_all()

    def plot(self):
        self.figure.clear()
        self.axis = self.figure.add_subplot(111)
        self.set_xy_range()
        self.axis.scatter(
            self.x, self.y, s=200, c='#af87ff',
            edgecolors='black', linewidth=1,
            label='data'
        )
        if self.result is not None:
            yfit = self.result.best_fit
            self.axis.plot(self.x, yfit, c='r', linewidth=2.5)
            cmap = cm.get_cmap('gnuplot')
            components = self.result.eval_components()
            for i, comp in enumerate(components):
                self.axis.plot(
                    self.x, components[comp],
                    linewidth=2.5, linestyle='--',
                    c=cmap(i/len(components)),
                    label=comp[:comp.find('_')]
                )
        self.axis.set_xlabel(self.data.columns[self.xcol_idx])
        self.axis.set_ylabel(self.data.columns[self.ycol_idx])
        self.axis.set_xlim([self.xmin, self.xmax])
        self.canvas.draw()

    def fit(self, source=None, event=None):
        # self.emode_box.setCheckState(0)
        # self.toggle_edit_mode()
        self.set_xy_range(self)
        self.set_params(self)
        self.result = self.model.fit(
            data=self.y, params=self.params, x=self.x,
            method='least_squares'
        )
        self.output_buffer.set_text(self.result.fit_report())
        self.plot()
        # overwrite widgets to clear input (not ideal method..)
        self.init_param_widgets()
        # update widgets with new placeholder text
        # NOTE: I think this is redundant?
        # self.update_param_widgets()

    def init_model(self):
        # note: increment() ensures nlin >= 1
        self.model = models.line_mod(self.nlin)
        if self.ngau != 0:
            self.model += models.gauss_mod(self.ngau)
        if self.nlor != 0:
            self.model += models.lor_mod(self.nlor)
        if self.nvoi != 0:
            self.model += models.voigt_mod(self.nvoi)
        self.statusbar.push(
                self.statusbar.get_context_id('info'),
                "Model updated: " +
                str([self.ngau, self.nlor, self.nvoi, self.nlin]),
                # msg_length
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
        self.clear_param_viewports()

        # main boxes to hold user entry widgets
        self.vbox_gau = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.vbox_lor = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.vbox_voi = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.vbox_lin = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        for param_name in self.model.param_names:
            # set param label text
            labels[param_name] = Gtk.Label()
            labels[param_name].set_text(param_name)

            # make user entry widgets
            for key in self.usr_entry_widgets:
                self.usr_entry_widgets[key][param_name] = Gtk.Entry()
                if param_name in self.usr_vals[key]:
                    self.usr_entry_widgets[key][param_name]\
                        .set_placeholder_text(
                            str(round(self.usr_vals[key][param_name], rnd))
                        )
                else:
                    self.usr_entry_widgets[key][param_name]\
                        .set_placeholder_text(key)
                # set up connections
                self.usr_entry_widgets[key][param_name].connect(
                    'changed', self.update_usr_vals, self.usr_entry_widgets
                )

            # add widgets to respective layouts
            vbox_sub = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
            for key in self.usr_entry_widgets:
                vbox_sub.pack_start(
                    self.usr_entry_widgets[key][param_name],
                    False, False, pad
                )
            if param_name.find('gau') != -1:
                self.vbox_gau.pack_start(labels[param_name], False, False, pad)
                self.vbox_gau.pack_start(vbox_sub, False, False, pad)
                self.vbox_gau.set_halign(Gtk.Align.CENTER)
            if param_name.find('lor') != -1:
                self.vbox_lor.pack_start(labels[param_name], False, False, pad)
                self.vbox_lor.pack_start(vbox_sub, False, False, pad)
                self.vbox_lor.set_halign(Gtk.Align.CENTER)
            if param_name.find('voi') != -1:
                self.vbox_voi.pack_start(labels[param_name], False, False, pad)
                self.vbox_voi.pack_start(vbox_sub, False, False, pad)
                self.vbox_voi.set_halign(Gtk.Align.CENTER)
            if param_name.find('lin') != -1:
                self.vbox_lin.pack_start(labels[param_name], False, False, pad)
                self.vbox_lin.pack_start(vbox_sub, False, False, pad)
                self.vbox_lin.set_halign(Gtk.Align.CENTER)

        # Resize all of the LineEntry widgets
        for key in self.usr_entry_widgets:
            for param, widget in self.usr_entry_widgets[key].items():
                widget.set_width_chars(7)

        # add/replace box in viewport
        self.param_viewport_gau.add(self.vbox_gau)
        self.param_viewport_lor.add(self.vbox_lor)
        self.param_viewport_voi.add(self.vbox_voi)
        self.param_viewport_lin.add(self.vbox_lin)
        for viewport in [self.param_viewport_gau, self.param_viewport_lor,
                         self.param_viewport_voi, self.param_viewport_lin]:
            viewport.show_all()

        if self.result is not None:
            self.set_params()
            self.update_param_widgets()

    def update_usr_vals(self, widget, entry_widget_dict):
        # get text input from each usr_entry_widget
        for val_type, param_dict in entry_widget_dict.items():
            for param, param_widget in param_dict.items():
                try:
                    self.usr_vals[val_type][param] = \
                        float(param_widget.get_text())
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
                self.usr_entry_widgets['value'][param].set_placeholder_text(
                    str(round(self.result.best_values[param], rnd))
                )
                self.usr_entry_widgets['min'][param].set_placeholder_text(
                    str(round(self.params[param].min, rnd))
                )
                self.usr_entry_widgets['max'][param].set_placeholder_text(
                    str(round(self.params[param].max, rnd))
                )

    def guess_params(self, source=None, event=None):
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

    def set_params(self, source=None, event=None):
        self.params = Parameters()
        self.guess_params()
        self.update_usr_vals(None, self.usr_entry_widgets)
        vals = {}

        # fill params with any user-entered values
        # fill in blanks with guesses
        for param_name in self.model.param_names:
            for val_type in ['value', 'min', 'max']:
                if param_name in self.usr_vals[val_type]:
                    vals[val_type] = self.usr_vals[val_type][param_name]
                else:
                    vals[val_type] = self.guesses[val_type][param_name]
            self.params.add(
                name=param_name, value=vals['value'], vary=True,
                min=vals['min'], max=vals['max']
            )

    def set_xy_range(self, source=None, event=None):
        self.x = self.data.iloc[:, self.xcol_idx]
        self.y = self.data.iloc[:, self.ycol_idx]
        # filter out NaN values
        if True in np.isnan(self.x) or True in np.isnan(self.y):
            nanbool = (~np.isnan(self.x)&~np.isnan(self.y))
            self.x = self.x[nanbool]
            self.y = self.y[nanbool]

        # self.xmin, self.xmax = self.axis.get_xlim()
        self.xmin = np.min(self.x) - 0.02*(np.max(self.x) - np.min(self.x))
        self.xmax = np.max(self.x) + 0.02*(np.max(self.x) - np.min(self.x))
        range_bool = (self.x >= self.xmin) & (self.x <= self.xmax)
        self.x = self.x[range_bool].values
        self.y = self.y[range_bool].values

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

    def clear_param_viewports(self):
        # clear any existing widgets from viewports
        for viewport in [self.param_viewport_gau, self.param_viewport_lin,
                         self.param_viewport_lor, self.param_viewport_voi]:
            if viewport.get_child():
                viewport.remove(viewport.get_child())

    def hard_reset(self, source=None, event=None):
        self.clear_param_viewports()
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
        self.output_buffer.set_text('')
        self.init_param_widgets()
        self.column_index_set()
        self.plot()

    def on_add_gau_clicked(self, source=None, event=None):
        self.increment('gau', True)
        self.init_param_widgets()

    def on_rem_gau_clicked(self, source=None, event=None):
        self.increment('gau', False)
        self.init_param_widgets()

    def on_add_lor_clicked(self, source=None, event=None):
        self.increment('lor', True)
        self.init_param_widgets()

    def on_rem_lor_clicked(self, source=None, event=None):
        self.increment('lor', False)
        self.init_param_widgets()

    def on_add_voi_clicked(self, source=None, event=None):
        self.increment('voi', True)
        self.init_param_widgets()

    def on_rem_voi_clicked(self, source=None, event=None):
        self.increment('voi', False)
        self.init_param_widgets()

    def on_add_lin_clicked(self, source=None, event=None):
        self.increment('lin', True)
        self.init_param_widgets()

    def on_rem_lin_clicked(self, source=None, event=None):
        self.increment('lin', False)
        self.init_param_widgets()

    def get_data(self, source=None, event=None):
        # self.emode_box.setCheckState(0)
        # self.toggle_edit_mode()
        # reset column indices
        self.xcol_idx = 0
        self.ycol_idx = 1
        # open file dialog
        self.dialog = Gtk.FileChooserDialog(
            title='Import data file...', parent=None,
            action=Gtk.FileChooserAction.OPEN,
        )
        self.dialog.add_buttons(
            Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
            Gtk.STOCK_OPEN, Gtk.ResponseType.OK
        )
        filter_csv = Gtk.FileFilter()
        filter_csv.set_name('.csv files')
        filter_csv.add_mime_type('text/csv')
        self.dialog.add_filter(filter_csv)

        filter_any = Gtk.FileFilter()
        filter_any.set_name('All files')
        filter_any.add_pattern("*")
        self.dialog.add_filter(filter_any)

        self.dialog.set_default_size(800, 400)

        response = self.dialog.run()
        if response == Gtk.ResponseType.OK:
            self.file_name = self.dialog.get_filename()
            try:
                df = tools.to_df(
                    self.file_name, sep=self.sep, header=self.header,
                    index_col=self.index_col, skiprows=self.skiprows,
                    dtype=self.dtype, encoding=self.encoding
                )
                df.iloc[:, self.xcol_idx]
                df.iloc[:, self.ycol_idx]
            except Exception:
                self.statusbar.push(
                    self.statusbar.get_context_id('import_error'),
                    file_import_error_msg
                )
                self.dialog.destroy()
                return
        else:
            self.file_name = None
            self.statusbar.push(
                self.statusbar.get_context_id('import_canceled'),
                'Import canceled.'
            )
            self.dialog.destroy()
            return

        self.dialog.destroy()

        self.data = df
        self.display_data()
        self.result = None
        # reset x, y, and xlim
        self.x = self.data.iloc[:, self.xcol_idx].values
        self.y = self.data.iloc[:, self.ycol_idx].values
        self.xmin = self.data.iloc[:, self.xcol_idx].min()
        self.xmax = self.data.iloc[:, self.xcol_idx].max()
        self.plot()
        self.statusbar.push(
            self.statusbar.get_context_id('import_finished'),
            'Imported {}'.format(self.file_name)
        )

    def display_data(self):
        # remove any pre-existing columns from treeview
        for col in self.data_treeview.get_columns():
            self.data_treeview.remove_column(col)
        # create model
        # TODO: allow for other types, and infer from data
        col_types = [float for col in self.data.columns]
        list_store = Gtk.ListStore(*col_types)

        # fill model with data
        for row in self.data.itertuples():
            list_store.append(
                [row[i+1] for i, col in enumerate(self.data.columns)]
            )
        # set it as TreeView model
        self.data_treeview.set_model(list_store)
        # Create and append columns
        for i, col in enumerate(self.data.columns):
            renderer = Gtk.CellRendererText()
            column = Gtk.TreeViewColumn(col, renderer, text=i)
            self.data_treeview.append_column(column)
        self.fname_buffer.set_text('Source:  {}'.format(self.file_name))
        self.fname_textview.set_buffer(self.fname_buffer)

    def column_index_set(self, source=None, event=None):
        # make sure user enters index that can be converted to int
        try:
            idx_x = int(self.column_entry_x.get_text())
        except ValueError:
            self.statusbar.push(
                self.statusbar.get_context_id('idx_type_error'),
                idx_type_error_msg
            )
            self.column_entry_x.set_text('')
            return
        try:
            idx_y = int(self.column_entry_y.get_text())
        except ValueError:
            self.statusbar.push(
                self.statusbar.get_context_id('idx_type_error'),
                idx_type_error_msg
                )
            self.column_entry_y.set_text('')
            return
        self.xcol_idx = idx_x
        self.ycol_idx = idx_y
        self.result = None
        # make sure user enters an index that's in the data range
        try:
            self.x = self.data.iloc[:, self.xcol_idx]
        except IndexError:
            self.statusbar.push(
                self.statusbar.get_context_id('idx_range_error'),
                idx_range_error_msg
            )
            self.xline_entry.setText(None)
            return
        try:
            self.y = self.data.iloc[:, self.ycol_idx]
        except IndexError:
            self.statusbar.push(
                self.statusbar.get_context_id('idx_range_error'),
                idx_range_error_msg
            )
            self.yline_entry.setText(None)
            return
        self.xmin = np.min(self.x)
        self.xmax = np.max(self.x)
        self.statusbar.push(
            self.statusbar.get_context_id('new_idx_success'),
            'Column Index (X) = ' + str(self.xcol_idx) + ', ' +
            'Column Index (Y) = ' + str(self.ycol_idx)
        )
        self.plot()

    def add_accelerator(self, widget, accelerator, signal="activate"):
        '''
        Adds keyboard shortcuts
        '''
        if accelerator is not None:
            key, mod = Gtk.accelerator_parse(accelerator)
            widget.add_accelerator(
                signal, self.accelerators, key, mod, Gtk.AccelFlags.VISIBLE
            )


if __name__ == '__main__':
    gui = App()
    Gtk.main()