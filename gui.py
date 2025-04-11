# I am expecting this to be available in all computers
import tkinter as tk

class CreateToolTip(object):
    """
    From: https://stackoverflow.com/a/36221216
    create a tooltip for a given widget
    """
    def __init__(self, widget, text='widget info'):
        self.waittime = 500     #miliseconds
        self.wraplength = 180   #pixels
        self.widget = widget
        self.text = text
        self.widget.bind("<Enter>", self.enter)
        self.widget.bind("<Leave>", self.leave)
        self.widget.bind("<ButtonPress>", self.leave)
        self.id = None
        self.tw = None

    def enter(self, event=None):
        self.schedule()

    def leave(self, event=None):
        self.unschedule()
        self.hidetip()

    def schedule(self):
        self.unschedule()
        self.id = self.widget.after(self.waittime, self.showtip)

    def unschedule(self):
        id = self.id
        self.id = None
        if id:
            self.widget.after_cancel(id)

    def showtip(self, event=None):
        x = y = 0
        x, y, cx, cy = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 20
        # creates a toplevel window
        self.tw = tk.Toplevel(self.widget)
        # Leaves only the label and removes the app window
        self.tw.wm_overrideredirect(True)
        self.tw.wm_geometry("+%d+%d" % (x, y))
        label = tk.Label(self.tw, text=self.text, justify='left',
                       background="#ffffff", relief='solid', borderwidth=1,
                       wraplength = self.wraplength)
        label.pack(ipadx=1)

    def hidetip(self):
        tw = self.tw
        self.tw= None
        if tw:
            tw.destroy()

class Field:
    def __init__(self, frame, text, tooltip):
        self.text = text
        self.tooltip = tooltip

        self.own_frame = tk.Frame(master=frame,
                               relief=tk.GROOVE,
                               borderwidth=5)
        self.own_frame.columnconfigure(0, weight=2)
        self.own_frame.columnconfigure(1, weight=1)
        self.own_frame.pack(fill=tk.BOTH, expand=True)

        self.label = tk.Label(master=self.own_frame, text=text)
        self.label.grid(row=0, column=0, sticky=tk.W)
        self.label_tooltip = CreateToolTip(self.label, tooltip)


class TextField(Field):
    def __init__(self, frame, text, tooltip, varname, default_value):
        super().__init__(frame, text, tooltip)
        self.varname = varname
        self.text_obj = tk.Entry(master=self.own_frame, bg='white')
        self.text_obj.insert(0, default_value)
        self.text_obj.grid(row=0, column=1, sticky=tk.E)

    def get_value(self):
        return self.text_obj.get()

class ListField(TextField):
    def __init__(self, frame, text, tooltip, varname, default_value):
        super().__init__(frame, text, tooltip, varname, default_value)

    def get_value(self):
        return awefawe # TODO: parse the input comma separated


class CheckboxField(Field):
    def __init__(self, frame, text, tooltip, varname, default_value):
        super().__init__(frame, text, tooltip)
        self.varname = varname
        self.value = default_value
        self.checkbox_obj = tk.Checkbutton(master=self.own_frame,
                                   text='',
                                   variable=self.value,
                                   onvalue=True,
                                   offvalue=False)
        if default_value:
            self.checkbox_obj.select()
        self.checkbox_obj.grid(row=0, column=1, sticky=tk.E)

    def get_value(self):
        return self.value

section_content = [
    [(Field, 'General variables', "These variables are valid for ALL datasets."),
     (TextField, 'Datasets per parameter set',
        'Number of datasets per parameter set',
        'n_datasets_per_paramset', 1),
     (TextField, 'Random seed',
        'The random seed (this can be any number. It will be used to generate random '
        'seeds for the generated datasets)',
        'rand_seed', 1234),
     (TextField, 'Output folder name',
        'The name of the output folder',
        'out_folder', 'out_datasets'),
     (TextField, 'Output file name prefix',
        'A name to prepend the generated file names. Every generated file will be named '
        '<out_file>_<n_subjs>_...',
        'out_file', 'fakedata'),
     (TextField, 'Div. Speed "slow factor"',
        'The default `slow_factor` to be passed to the `sigmoid` function. When this '
        'value is big, the divergence will happen slowly, from the divergence point on. '
        'When this value is small, the divergence will be fast. '
        'BUT NOTE: this value should probably be a bit bigger than the sum of the other '
        '`dspeed` biases. Take a look at the `sigmoid` function for more details.',
        'out_file', 50),
     (CheckboxField, 'Force Divergence Point',
        'Whether we should try to force the divergence point of condition 0 to be *EXACTLY* '
        'at the specified divergence point.\n'
        'If this is set, the generator will produce a larger population, '
        'perform a DPA on this larger population, and then shift the trials so that '
        'the divergence point for condition 0 is *exactly* at the time `dpoint`, '
        'the divergence point for condition 1 is *exactly* at the time `dpoint + cond_effect`, '
        'and so on. Then, it will sample `n_subjs` from this population. '
        '(this is mutually exclusive with `force_dp_memory_efficient`) ',
        'force_divergence_point', True),

    (ListField, 'Number of participants', 'blah', 'n_subjs', '1,2')],
    [(Field, 'Per dataset general variables', 'blah')]
 ]


def create_field(frame, text, field_type, varname):
    global params
    global how_to_access
    whole_frame = tk.Frame(master=frame,
                           relief=tk.GROOVE,
                           borderwidth=5)
    whole_frame.pack(fill=tk.BOTH, expand=True)

    label = tk.Label(master=whole_frame, text=text)
    label.grid(row=0, column=0)

    if field_type == 'text':
        field_obj = tk.Entry(master=whole_frame,
                             width=50)
        how_to_access[varname] = 'call_get'
        params[varname] = field_obj
    elif field_type == 'checkbox':
        #field_obj = tk.Checkbutton(window, text='Python',variable=var1, onvalue=1, offvalue=0, command=print_selection)
        params[varname] = None
        field_obj = tk.Checkbutton(master=whole_frame,
                                   text='Python',
                                   variable=params[varname],
                                   onvalue=1,
                                   offvalue=0)
        how_to_access[varname] = 'use_var'
    field_obj.grid(row=0, column=1)

def create_label(frame, text):
    label = tk.Label(master=frame, text=text)
    label.pack()

def make_widget(frame, i):
    widget_type = i[0]
    widget_type(frame, *i[1:])


def make_section_frame(window, frame_content):
    frame = tk.Frame(master=window,
                     relief=tk.GROOVE,
                     borderwidth=5)
    frame.pack(fill=tk.BOTH, side=tk.LEFT, expand=False)
    for i in frame_content:
        make_widget(frame, i)

def make_top(window):
    top_text = "DPA fake data generator"
    label = tk.Label(master=window, text=top_text)
    label.pack()

def create_window():
    window = tk.Tk()
    make_top(window)

    for i in section_content:
        make_section_frame(window, i)

    return window


window = create_window()
window.mainloop()

