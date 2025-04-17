import sys
import subprocess
import os
import itertools
import random
import string


# Where is Python / what is Python named in this computer?
PY = sys.executable

# This script assumes the `dpa_fake_data_gen.py` script is in the same folder
DPA_FAKE_DATA_GEN = os.path.join(os.path.dirname(os.path.realpath(__file__)), "dpa_fake_data_gen.py")

# Used for `random_string()`
alphabet = string.ascii_lowercase + string.digits

def random_string(length = 6):
    # This is the `random_choice` method from https://stackoverflow.com/a/56398787
    return ''.join(random.choices(alphabet, k=length))

def generate_combinations(dictionary):
    # This is cryptic, but is directly from https://stackoverflow.com/a/61335465
    keys, values = zip(*dictionary.items())
    permutations_dicts = [dict(zip(keys, v)) for v in itertools.product(*values)]
    return permutations_dicts


def run_fake_data_generator(general_params, params, d_idx, seed):
    out_file_name = '_'.join([general_params['out_file'],
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
                              'ipsd' + str(params['item_prob_bias_sd']),
                              'idssd' + str(params['item_dspeed_bias_sd']),

                              "olp" + str(params['outmonitor_look_prob']),
                              "solpsd" + str(params['subj_outmonitor_look_bias_sd']),
                              seed])

    run_args = [
        PY, str(DPA_FAKE_DATA_GEN),
        "--out_file", os.path.join(general_params['out_folder'], str(out_file_name)),
        "--rand_seed", str(seed),
        "--n_subjs", str(params['n_subjs']),
        "--n_conds", str(params['n_conds']),
        "--n_trials", str(params['n_trials']),
        "--trial_len", str(params['trial_len']),
        "--dpoint", str(params['dpoint']),
        "--dspeed_slow_factor", str(general_params['dspeed_slow_factor']),
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
        "--item_prob_bias_sd", str(params['item_prob_bias_sd']),
        "--item_dspeed_bias_sd", str(params['item_dspeed_bias_sd']),
        "--outmonitor_look_prob", str(params['outmonitor_look_prob']),
        "--subj_outmonitor_look_bias_sd", str(params['subj_outmonitor_look_bias_sd']),
        "--pop_multiplier", str(general_params['population_multiplier']),
    ]
    #if general_params['dump_per_trial_fixation_stats']:
    #    run_args.append("--dump_per_trial_fixation_stats")
    #if general_params['dump_overall_fixation_stats']:
    #    run_args.append("--dump_overall_fixation_stats")
    if general_params['force_divergence_point']:
        run_args.append("--force_dpoint")
    if general_params['force_dp_memory_efficient']:
        run_args.append("--force_dpoint_me")

    return subprocess.Popen(run_args)

def generate_datasets(general_params, params, additional_callback):
    if not os.path.exists(general_params['out_folder']):
        os.makedirs(general_params['out_folder'])

    parameter_sets = generate_combinations(params)
    total_parameters_sets = len(parameter_sets)

    for idx,param_set in enumerate(parameter_sets):
        for dataset_idx in range(general_params['n_datasets_per_paramset']):
            seed = random_string()
            process = run_fake_data_generator(general_params, param_set, dataset_idx, seed)
            while process.poll() is None:
                additional_callback(idx+1, dataset_idx+1, total_parameters_sets, general_params['n_datasets_per_paramset'])

