# I am expecting this to be available in all computers
import os
import tkinter as tk

import run_generator as rg

cwd = os.path.dirname(os.path.realpath(__file__))
os.chdir(cwd)


def extract_parameters(data_widgets, general_widgets, whole_dataset_widgets):
    # TODO: maybe remove the code repetition here?
    general_params = {}
    for i in general_widgets:
        if hasattr(i, 'varname'):
            general_params[i.varname] = i.get_value()

    params = {}
    for i in data_widgets + whole_dataset_widgets:
        if hasattr(i, 'varname'):
            params[i.varname] = i.get_value()

    return general_params, params


def run_fake_data_gen(label, data_widgets, general_widgets, whole_dataset_widgets):
    def update_label(curr_paramset, curr_iter, total_paramsets, total_per_paramset):
        # Just a fancy way to avoid showing `label` to `run_generator.py`
        label['text'] = "Generating dataset " + str(curr_iter) + "/" + str(total_per_paramset) + \
                        " for parameter set " + str(curr_paramset) + "/" + str(total_paramsets)
        label.update_idletasks()

    label['text'] = 'Extracting parameters'
    general_params, params = extract_parameters(data_widgets, general_widgets, whole_dataset_widgets)

    rg.random.seed(general_params['rand_seed'])
    rg.generate_datasets(general_params, params, update_label)


class CreateToolTip(object):
    """
    From: https://stackoverflow.com/a/36221216
    create a tooltip for a given widget
    """
    def __init__(self, widget, text='widget info'):
        self.waittime = 500     #miliseconds
        self.wraplength = 550   #pixels
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

        self.own_frame = tk.Frame(master=frame)
                               #relief=tk.GROOVE,
                               #borderwidth=5)
        self.own_frame.columnconfigure(0, weight=2)
        self.own_frame.columnconfigure(1, weight=1)
        self.own_frame.pack(fill=tk.BOTH, expand=True)

        self.label = tk.Label(master=self.own_frame, text=text)
        self.label.grid(row=0, column=0, sticky=tk.W, padx=5)
        if tooltip is not None:
            self.label_tooltip = CreateToolTip(self.label, tooltip)


class TextField(Field):
    def __init__(self, frame, text, varname, default_value, tooltip):
        super().__init__(frame, text, tooltip)
        self.varname = varname
        self.text_obj = tk.Entry(master=self.own_frame, bg='white')
        self.text_obj.insert(0, default_value)
        self.text_obj.grid(row=0, column=1, sticky=tk.E)

    def get_value(self):
        return self.text_obj.get()

class NumberField(TextField):
    def __init__(self, frame, text, varname, default_value, tooltip):
        super().__init__(frame, text, varname, default_value, tooltip)
        self.own_frame.columnconfigure(2, weight=1)

        self.buttons_frame = tk.Frame(master=self.own_frame)
        self.buttons_frame.grid(row=0, column=2, sticky=tk.E)
        self.button_up   = tk.Button(master=self.buttons_frame, text="+", command=self.increase)
        self.button_down = tk.Button(master=self.buttons_frame, text="-", command=self.decrease)
        self.button_up.grid(row=0, column=0, sticky=tk.E)
        self.button_down.grid(row=0, column=1, sticky=tk.E)

    def change_value(self, how_much):
        curr_value = int(self.get_value())
        new_value = curr_value + how_much
        new_value = 0 if new_value < 0 else new_value

        self.text_obj.delete(0, tk.END)
        self.text_obj.insert(0, new_value)
    def increase(self):
        self.change_value(1)

    def decrease(self):
        self.change_value(-1)

    def get_value(self):
        return int(self.text_obj.get())

class ListField(TextField):
    def __init__(self, frame, text, varname, default_value, tooltip):
        super().__init__(frame, text, varname, default_value, tooltip)

    def get_value(self):
        # This is a hack so that Python doesn't complain if there is only a
        # single number. We add another element, here... and then remove it
        # with [:-1] upon returning
        content = self.text_obj.get() + ', 100'
        # From https://stackoverflow.com/a/19334424
        # This `eval()` option is good because it allows me not to have to
        # explicitly say whether the type is `int` or `float`
        return list(eval(content))[:-1]


class CheckboxField(Field):
    def __init__(self, frame, text, varname, default_value, tooltip):
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

general_vars = [
    (Field, 'General variables',
     'These are variables that are valid for this program in general, and not '
     'necessarily to each individual dataset that will be generated.'),
    (Field, '(Input only a single value for each variable)', None),
    (Field, '', None),
    (NumberField, 'Datasets per parameter set', 'n_datasets_per_paramset', 1,
     'Number of datasets per parameter set'),
    (TextField, 'Random seed', 'rand_seed', 1234,
     'The random seed (this can be any number. It will be used to generate random '
     'seeds for the generated datasets)'),
    (TextField, 'Output folder name', 'out_folder', 'out_datasets',
     'The name of the output folder'),
    (TextField, 'Output file name prefix', 'out_file', 'fakedata',
     'A name to prepend the generated file names. Every generated file will be named '
     '<out_file>_<n_subjs>_...'),
    (TextField, 'Divergence Speed "slow factor"', 'dspeed_slow_factor', 50,
     'The default `slow_factor` to be passed to the `sigmoid` function. When this '
     'value is big, the divergence will happen slowly, from the divergence point on. '
     'When this value is small, the divergence will be fast. '
     'BUT NOTE: this value should probably be a bit bigger than the sum of the other '
     '`dspeed` biases. Take a look at the `sigmoid` function for more details.'),
    (CheckboxField, 'Force Divergence Point', 'force_divergence_point', False,
     'Whether we should try to force the divergence point of condition 0 to be *EXACTLY* '
     'at the specified divergence point.\n'
     'If this is set, the generator will produce a larger population, '
     'perform a DPA on this larger population, and then shift the trials so that '
     'the divergence point for condition 0 is *exactly* at the time `dpoint`, '
     'the divergence point for condition 1 is *exactly* at the time `dpoint + cond_effect`, '
     'and so on. Then, it will sample `n_subjs` from this population. '
     '(this is mutually exclusive with `force_dp_memory_efficient`) '),
    (CheckboxField, 'Force Divergence Point (Memory efficient)', 'force_dp_memory_efficient', True,
     'A "memory efficient" version of the `force_divergence_point` algorithm. '
     '(this is mutually exclusive with `force_divergence_point`)'),
    (TextField, 'Population multiplier', 'population_multiplier', 50,
     '(Only useful if `force_dpoint` is set). '
     'This will be used to define the size of the "larger population" in the '
     'description of `force_divergence_point` above. It will have size: '
     '`n_subjs * pop_multiplier`. '),
    (CheckboxField, 'Dump per trial fixation stats', 'dump_per_trial_fixation_stats', False,
     'Additional stats on the length of each trial fixation.'),
    (CheckboxField, 'Dump overall fixation stats', 'dump_overall_fixation_stats', False,
     'Additional stats on the length of fixations for the whole dataset.')
]

whole_dataset_vars = [
    (Field, 'Per dataset general variables',
     'These variables do not have to do probabilities or variabilities, but rather '
     'with general information that will be relevant for the dataset as a whole.'),
    (Field, '(Use commas to input multiple values)', None),
    (Field, '', None),
    (ListField, 'Number of participants', 'n_subjs', 40,
     'How many participants in each dataset.'),
    (ListField, 'Number of condition', 'n_conds', 2,
     'How many conditions each participant saw.'),
    (ListField, 'Number of trials per condition', 'n_trials', 80,
     'How many trials for each combination `participant x condition`'),
    (ListField, 'Trial length (in ms)', 'trial_len', 1000,
     'The length of each trial in ms'),
    (ListField, 'Divergence Point (see tooltip)', 'dpoint', 300,
     'If you do not set "Force Divergence Point" (or its memory efficient version), '
     'then this is the point (in ms) at which the probability of looks towards the '
     'target *starts* to increase.\n\n'
     'If you set the option to "Force Divergence Point", then we will try to '
     'use a simpler non-bootstrapped version of DPA to kind-of force the '
     'divergence point to be the specified value.'),
    (ListField, 'Effect of condition', 'cond_effect', '100, 200',
     'The length of each trial in ms'
     'The effect of each condition. For example, if the divergence point is 300 and '
     '`cond_effect` is 100, then:\n'
     'In condition 0, the divergence point will be 300 + (0 * 100) = 300ms\n'
     'In condition 1, the divergence point will be 300 + (1 * 100) = 400ms\n'
     'In condition 2, the divergence point will be 300 + (2 * 100) = 500ms\n'
     '...')
]

random_var_per_trial = [
    (Field, 'Random variation for every trial',
     'These indicate random variability for every trial.\n'
     'Every trial, we sample from a normal distribution N(mean=0, sd=variable) '
     'use the sampled number in the following ways...'),
    (Field, '(Use commas to input multiple values)', None),
    (Field, '', None),
    (ListField, 'Variation on Divergence Point', 'rand_dp_noise_sd', 10,
     'The standard deviation of the random noise of the divergence point.\n'
     'Every trial, we sample from the normal distribution and sum the sampled '
     'value to the divergence point.'),
    (ListField, 'Variation in Prob. of looks to Target', 'rand_prob_noise_sd', 0.01,
     'The standard deviation of the random noise of the probability.\n'
     'Every trial, we sample from the normal distribution and sum it to the '
     'probability of looking to the target'),
    (ListField, 'Variation in "Div. Speed"', 'rand_dspeed_noise_sd', 2,
     'The standard deviation of the random noise of the "divergence speed".\n'
     'Every trial, we sample from the normal distribution and use this number to '
     'influence the function that determines how "fast" the looks diverge at the '
     'divergence point')
]

per_trial_per_subj_var = [
    (Field, 'Variation per participant per trial',
     'For each participant, we sample from a normal distribution '
     'N(mean=0, sd=variable) and use the sampled value as the standard deviation '
     'of *another* normal distribution N(mean=0, sd=sample_value), i.e., as the '
     'variability of the particular participant (some participants will have a ' 
     'large variability, some participants will have a low variability). Then, '
     'for every trial, we sample from this other normal distribution.'),
    (Field, '(Use commas to input multiple values)', None),
    (Field, '', None),
    (ListField, 'Variation on Divergence Point', 'subj_per_trial_dpoint_var_sd', 7,
     'The per trial per participant variability of the divergence point.\n'
     'The value sampled from the "other" normal distribution (every trial) '
     'will be summed to the divergence point'),
    (ListField, 'Variation in Prob. of looks to Target', 'subj_per_trial_bias_var_sd', 0.005,
     'The per trial per participant variability of the participant bias.\n'
     'The value sampled from the "other" normal distribution (every trial) '
     'will be summed to the probability of looks to the target'),
    (ListField, 'Variation in "Div. Speed"', 'subj_per_trial_dspeed_var_sd', 2,
     'The per trial per participant variability of the "divergence speed".\n'
     'The value sampled from the "other" normal distribution (every trial) '
     'will influence the function that determines how "fast" the looks diverge '
     'at the divergence point'),
]

per_subj_var = [
    (Field, 'Per participant variation. This is set once for each participant.',
     'For each participant, we sample from a normal distribution '
     'N(mean=0, sd=variable) and use the sampled value directly to influence '
     'something. (no per-trial random resampling as in the previous section) '),
    (Field, '(Use commas to input multiple values)', None),
    (Field, '', None),
    (ListField, 'Variation on Random Intercepts', 'subj_dpoint_rand_intercept_sd', 15,
     'The per participant random intercept of the divergence point.\n'
     'The value sampled from the normal distribution will be summed to the '
     'divergence point'),
    (ListField, 'Variation on Random Slopes', 'subj_dpoint_rand_slope_sd', 5,
     'The per participant random slope of the divergence point.\n'
     'The value sampled from the normal distribution will be summed to '
     '`cond_effect` before calculating the new divergence point.'),
    (ListField, 'Variation of Biases to Target Obj.', 'subj_bias_var_sd', 0.05,
     'The per participant bias towards one of the images.\n'
     'The value sampled from the normal distribution will be summed to the '
     'probability of looking to the target.'),
    (ListField, 'Variation on "Divergence Speeds"', 'subj_dspeed_bias_var_sd', 4,
     'The per participant bias on the "divergence speed". The idea is that '
     'some participants diverge faster than others.\n'
     'The value sampled from the normal distribution will influence the function '
     'that determines how "fast" the looks diverge at the divergence point'
     ),
]

per_item_var = [
    (Field, 'Per item variation. This is set once for each combination item/condition',
     '(I do it along with condition because I assume that the items are '
     'different in the different conditions)\n'
     'For each combination item/condition, we sample from a normal distribution '
     'N(mean=0, sd=variable) and use the sampled value directly to influence '
     'something.'),
    (Field, '(Use commas to input multiple values)', None),
    (Field, '', None),
    (ListField, 'Variation on Divergence Point', 'item_dpoint_bias_sd', 15,
     'The per item variability on the divergence point.\n'
     'The value sampled from the normal distribution will be summed to the '
     'divergence point'),
    (ListField, 'Variation in Prob. of looks to Target', 'item_prob_bias_sd', 0.05,
     'The per item bias towards one of the other images.\n'
     'This bias models the situation where one of the images of a given item '
     'is more "salient" than the other. '
     'The value sampled from the normal distribution will be summed to the '
     'probability of looks to the target'),
    (ListField, 'Variation in "Div. Speed"', 'item_dspeed_bias_sd', 5,
     'The per item bias on the "divergence speed". The idea is that some items '
     'will lead participants to diverge faster than others.\n'
     'The value sampled from the normal distribution will influence the function '
     'that determines how "fast" the looks diverge at the divergence point'),
]

outmonitor_var = [
    (Field, 'Probabilities of looking away from the monitor',
     'Every fixation, before deciding whether the participant looked at the '
     'target or not, we randomly decide whether they instead "looked away". '
     'The probability of looking away is a sum of two values. One fixed, and '
     'one that is sampled per subject.'),
    (Field, '(Use commas to input multiple values)', None),
    (Field, '', None),
    (ListField, 'Overall Prob. of looking away', 'outmonitor_look_prob', 0.01,
     None),
    (ListField, 'Variation per Participant', 'subj_outmonitor_look_bias_sd', 0.001,
     'The per participant bias for looking away.\n'
     'For each participant, we sample from a normal distribution '
     'N(mean=0, sd=subj_outmonitor_look_bias_sd) and sum the sampled value to '
     'the probability of looking away.')
]


section_content = [
    #general_vars,
    #whole_dataset_vars,
    random_var_per_trial,
    per_trial_per_subj_var,
    per_subj_var,
    per_item_var,
    outmonitor_var
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
    widget = widget_type(frame, *i[1:])
    return widget


def make_section_frame(window, frame_content, row, column, rowspan):
    frame = tk.Frame(master=window,
                     relief=tk.GROOVE,
                     borderwidth=5)
    frame.grid(sticky='nswe',
               row=row, column=column,
               rowspan=rowspan)
    ret = []
    for i in frame_content:
        ret.append(make_widget(frame, i))
    return ret

def make_run_button(window, data_widgets, general_widgets, whole_dataset_widgets):
    frame = tk.Frame(master=window,
                     relief=tk.GROOVE,
                     borderwidth=5)
    frame.grid(sticky='nswe',
               row=4, column=1)

    label = tk.Label(master=frame, text="We'll display the status here")
    button = tk.Button(master=frame, text='Run Generator',
                       command=lambda: run_fake_data_gen(label,
                                                         data_widgets,
                                                         general_widgets,
                                                         whole_dataset_widgets))
    label.pack()
    button.pack()


def run_application():
    # Create the Window, set up the frames, etc...
    window = tk.Tk()
    data_widgets = []
    for idx,i in enumerate(section_content):
        data_widgets.extend(make_section_frame(window, i, row=idx, column=0, rowspan=1))

    general_widgets = make_section_frame(window, general_vars, row=0, column=1, rowspan=2)
    whole_dataset_widgets = make_section_frame(window, whole_dataset_vars, row=2, column=1, rowspan=2)
    make_run_button(window, data_widgets, general_widgets, whole_dataset_widgets)

    window.mainloop()


run_application()

