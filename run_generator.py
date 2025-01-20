import sys
import subprocess
import os
import itertools
import random
import string


################################################################################
# General variables

# Number of datasets per parameter set
n_datasets_per_paramset = 3

# The random seed (this can be any number. It will be used to generate random
# seeds for the generated datasets)
rand_seed = 1234

# The name of the output folder
out_folder = 'out_datasets'

# A name to prepend the generated file names. Every generated file will be named
# <out_file>_<n_subjs>_...     NEED TO ASK OPINIONS
out_file = 'fakedata'

# The default `slow_factor` to be passed to the `sigmoid` function. When this
# value is big, the divergence will happen slowly, from the divergence point on.
# When this value is small, the divergence will be fast.
# BUT NOTE: this value should probably be a bit bigger than the sum of the other
# `dspeed` biases. Take a look at the `sigmoid` function for more details.
#
# TODO: Should this be inside `params`, so that we can create datasets with
#       varying dspeed values? (if you eventually change this, add it to the
#       `out_file_name` variable)
dspeed_slow_factor = 50

# Whether we should try to force the divergence point of condition 0 to be *EXACTLY*
# at `args.dpoint`
force_divergence_point = True

params = {
    ###################
    # Variables about the datasets as a whole

    # How many participants in each file
    'n_subjs'          : [50],

    # How many conditions each participant saw
    'n_conds'          : [2],

    # How many trials for each combination 'participant x condition' ?
    'n_trials'         : [12],

    # The length of each trial in ms
    'trial_len'     : [1000],

    # The point in ms at which the probability of looks towards the target *start*
    # increasing
    'dpoint' : [300],

    # The effect of each condition. For example, if the divergence point is 300 and
    # `cond_effect` is 100, then:
    # In condition 0, the divergence point will be 300 *   0 = 300ms
    # In condition 1, the divergence point will be 300 * 100 = 400ms
    # In condition 2, the divergence point will be 300 * 200 = 500ms
    # ...
    'cond_effect' : [50, 100, 150],

    # If you want additional stats, set these to true
    'dump_per_trial_fixation_stats': [False],
    'dump_overall_fixation_stats': [False],

    ###################
    # Random variation for every trial
    # These indicate random variability for every trial.
    # Every trial, we sample from a normal distribution N(mean=0, sd=variable),
    # use the sampled number in the following ways...

    # The standard deviation of the random noise of the divergence point.
    # Every trial, we sample from the normal distribution and sum the sampled
    # value to the divergence point
    'rand_dp_noise_sd' : [20, 50],

    # The standard deviation of the random noise of the probability.
    # Every trial, we sample from the normal distribution and sum it to the
    # probability of looking to the target
    'rand_prob_noise_sd' : [0.1, 0.2],

    # The standard deviation of the random noise of the "divergence speed".
    # Every trial, we sample from the normal distribution and use this number to
    # influence the function that determines how "fast" the looks diverge at the
    # divergence point
    'rand_dspeed_noise_sd' : [5],


    ###################
    # Per trial per participant variables
    # For each participant, we sample from a normal distribution
    # N(mean=0, sd=variable) and use the sampled value as the standard deviation
    # of *another* normal distribution N(mean=0, sd=sample_value), i.e., as the
    # variability of the particular participant (some participants will have a
    # large variability, some participants will have a low variability). Then,
    # for every trial, we sample from this other normal distribution.

    # The per trial per participant variability of the divergence point.
    # The value sampled from the "other" normal distribution (every trial)
    # will be summed to the divergence point
    'subj_per_trial_dpoint_var_sd' : [10],

    # The per trial per participant variability of the participant bias.
    # The value sampled from the "other" normal distribution (every trial)
    # will be summed to the probability of looks to the target
    'subj_per_trial_bias_var_sd'   : [0.1],

    # The per trial per participant variability of the "divergence speed".
    # The value sampled from the "other" normal distribution (every trial)
    # will influence the function that determines how "fast" the looks diverge
    # at the divergence point
    'subj_per_trial_dspeed_var_sd' : [5],


    ###################
    # Per participant variables. This is set once for each participant.
    # For each participant, we sample from a normal distribution
    # N(mean=0, sd=variable) and use the sampled value directly to influence
    # something. (no per-trial random resampling as in the previous section)

    # The per participant random intercept of the divergence point.
    # The value sampled from the normal distribution will be summed to the
    # divergence point
    'subj_dpoint_rand_intercept_sd' : [50],

    # The per participant random slope of the divergence point.
    # The value sampled from the normal distribution will be summed to
    # `cond_effect` before calculating the new divergence point.
    'subj_dpoint_rand_slope_sd' : [50],

    # The per participant bias towards one of the images.
    # The value sampled from the normal distribution will be summed to the
    # probability of looking to the target.
    'subj_bias_var_sd' : [0.1],

    # The per participant bias on the "divergence speed". The idea is that
    # some participants diverge faster than others.
    # The value sampled from the normal distribution will influence the function
    # that determines how "fast" the looks diverge at the divergence point
    'subj_dspeed_bias_var_sd' : [5],


    ###################
    # Per item variables. This is set once for each combination item/condition
    # (I do it along with condition because I assume that the items are
    # different in the different conditions)
    # For each combination item/condition, we sample from a normal distribution
    # N(mean=0, sd=variable) and use the sampled value directly to influence
    # something.

    # The per item bias towards one of the images.
    # The value sampled from the normal distribution will be summed to the
    # divergence point
    'item_dpoint_bias_sd' : [50],

    # The per item bias on the "divergence speed". The idea is that some items
    # will lead participants to diverge faster than others.
    # The value sampled from the normal distribution will influence the function
    # that determines how "fast" the looks diverge at the divergence point
    'item_dspeed_bias_sd' : [5],
}


################################################################################

# Set random seed
random.seed(rand_seed)

# Where is Python / what is Python named in this computer?
PY = sys.executable

# This script assumes the `dpa_fake_data_gen.py` script is in the same folder
DPA_FAKE_DATA_GEN = os.path.join(os.path.dirname(os.path.realpath(__file__)), "dpa_fake_data_gen.py")

# Used for `random_string()`
alphabet = string.ascii_lowercase + string.digits

def random_string(length = 6):
    # This is the `random_choice` method from https://stackoverflow.com/a/56398787
    return ''.join(random.choices(alphabet, k=length))

def generate_combinations(df):
    # This is cryptic, but is directly from https://stackoverflow.com/a/61335465
    keys, values = zip(*df.items())
    permutations_dicts = [dict(zip(keys, v)) for v in itertools.product(*values)]
    return permutations_dicts

def generate_datasets(df):
    if not os.path.exists(out_folder):
        os.makedirs(out_folder)

    parameter_sets = generate_combinations(df)
    for param_set in parameter_sets:
        for dataset_idx in range(n_datasets_per_paramset):
            seed = random_string()
            run_fake_data_generator(param_set, dataset_idx, seed)

def run_fake_data_generator(params, d_idx, seed):
    out_file_name = '_'.join([out_file,
                              'sub' + str(params['n_subjs']),
                              'cond' + str(params['n_conds']),
                              'tri' + str(params['n_trials']),
                              'dp' + str(params['dpoint']),
                              'fx' + str(params['cond_effect']),
                              'rdpnoise' + str(params['rand_dp_noise_sd']),
                              'rprobnoise' + str(params['rand_prob_noise_sd']),
                              'rdsnoise' + str(params['rand_dspeed_noise_sd']),

                              'sptdpvar' + str(params['subj_per_trial_dpoint_var_sd']),
                              'sptprobvar' + str(params['subj_per_trial_bias_var_sd']),
                              'sptdsvar' + str(params['subj_per_trial_dspeed_var_sd']),

                              'sdpintrsd' + str(params['subj_dpoint_rand_intercept_sd']),
                              'sdpslopsd' + str(params['subj_dpoint_rand_slope_sd']),
                              'sprobsd' + str(params['subj_bias_var_sd']),
                              'sdssd' + str(params['subj_dspeed_bias_var_sd']),

                              'idpsd' + str(params['item_dpoint_bias_sd']),
                              'idssd' + str(params['item_dspeed_bias_sd']),
                              seed])

    run_args = [
        PY, str(DPA_FAKE_DATA_GEN),
        "--out_file", str(out_file_name),
        "--rand_seed", str(seed),
        "--n_subjs", str(params['n_subjs']),
        "--n_conds", str(params['n_conds']),
        "--n_trials", str(params['n_trials']),
        "--trial_len", str(params['trial_len']),
        "--dpoint", str(params['dpoint']),
        "--dspeed_slow_factor", str(dspeed_slow_factor),
        "--cond_effect", str(params['cond_effect']),
        "--rand_dp_noise_sd", str(params['rand_dp_noise_sd']),
        "--rand_prob_noise_sd", str(params['rand_prob_noise_sd']),
        "--rand_dspeed_noise_sd", str(params['rand_dspeed_noise_sd']),
        "--subj_per_trial_dpoint_var_sd", str(params['subj_per_trial_dpoint_var_sd']),
        "--subj_per_trial_bias_var_sd", str(params['subj_per_trial_bias_var_sd']),
        "--subj_per_trial_dspeed_var_sd", str(params['subj_per_trial_dspeed_var_sd']),
        "--subj_dpoint_rand_intercept_sd", str(params['subj_dpoint_rand_intercept_sd']),
        "--subj_dpoint_rand_slope_sd", str(params['subj_dpoint_rand_slope_sd']),
        "--subj_bias_var_sd", str(params['subj_bias_var_sd']),
        "--subj_dspeed_bias_var_sd", str(params['subj_dspeed_bias_var_sd']),
        "--item_dpoint_bias_sd", str(params['item_dpoint_bias_sd']),
        "--item_dspeed_bias_sd", str(params['item_dspeed_bias_sd']),
    ]
    if params['dump_per_trial_fixation_stats']:
        run_args.append("--dump_per_trial_fixation_stats")
    if params['dump_overall_fixation_stats']:
        run_args.append("--dump_overall_fixation_stats")
    if force_divergence_point:
        run_args.append("--force_dpoint")

    subprocess.run(run_args)

if __name__ == '__main__':
    generate_datasets(params)
