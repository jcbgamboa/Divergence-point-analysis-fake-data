import sys
import subprocess
import os


# General variables
OUTPUT_FILENAME  = 'fake_data.csv'
RANDOM_SEED      = 'abcd'

N_PARTICIPANTS   = 50
N_TRIALS         = 12
N_CONDITIONS     = 2

TRIAL_LENGTH     = 1000

DIVERGENCE_POINT = 300
CONDITION_EFFECT = 150

# Random variation for every trial
RANDOM_DIVERGENCE_POINT_NOISE_SD   = 10
RANDOM_PROBABILITY_NOISE_SD        = 0.5
RANDOM_DIVERGENCE_SPEED_NOISE_SD   = 5


# Per trial per participant variables
# This is used to produce a per-participant random variability (so that some
# participants are more variable, and some are less), that is set every trial
PARTICIPANT_PER_TRIAL_DIVERGENCE_POINT_VARIATION_SD = 10
PARTICIPANT_PER_TRIAL_BIAS_VARIATION_SD             = 0.5
PARTICIPANT_PER_TRIAL_DIVERGENCE_SPEED_VARIATION_SD = 5


# Per participant variables. This is set once for each participant
PARTICIPANT_DIVERGENCE_POINT_RANDOM_INTERCEPT_SD    = 50
PARTICIPANT_DIVERGENCE_POINT_RANDOM_SLOPE_SD        = 50
PARTICIPANT_BIAS_VARIATION_SD                       = 50
PARTICIPANT_DIVERGENCE_SPEED_BIAS_VARIATION_SD      = 5


# If you want additional stats, set these to true
DUMP_OVERALL_FIXATION_STATS    = True
DUMP_PER_TRIAL_FIXATION_STATS  = True



DPA_FAKE_DATA_GEN = os.path.join(os.path.dirname(os.path.realpath(__file__)), "dpa_fake_data_gen.py")

run_args = [
    sys.executable,                      str(DPA_FAKE_DATA_GEN),
    "--out_file",                        str(OUTPUT_FILENAME),
    "--rand_seed",                       str(RANDOM_SEED),
    "--n_subjs",                         str(N_PARTICIPANTS),
    "--n_trials",                        str(N_TRIALS),
    "--n_conds",                         str(N_CONDITIONS),
    "--trial_len",                       str(TRIAL_LENGTH),
    "--dpoint",                          str(DIVERGENCE_POINT),
    "--cond_effect",                     str(CONDITION_EFFECT),
    "--rand_dp_noise_sd",                str(RANDOM_DIVERGENCE_POINT_NOISE_SD),
    "--rand_prob_noise_sd",              str(RANDOM_PROBABILITY_NOISE_SD),
    "--rand_dspeed_noise_sd",            str(RANDOM_DIVERGENCE_SPEED_NOISE_SD),
    "--subj_per_trial_dpoint_var_sd",    str(PARTICIPANT_PER_TRIAL_DIVERGENCE_POINT_VARIATION_SD),
    "--subj_per_trial_bias_var_sd",      str(PARTICIPANT_PER_TRIAL_BIAS_VARIATION_SD),
    "--subj_per_trial_dspeed_var_sd",    str(PARTICIPANT_PER_TRIAL_DIVERGENCE_SPEED_VARIATION_SD),
    "--subj_dpoint_rand_intercept_sd",   str(PARTICIPANT_DIVERGENCE_POINT_RANDOM_INTERCEPT_SD),
    "--subj_dpoint_rand_slope_sd",       str(PARTICIPANT_DIVERGENCE_POINT_RANDOM_SLOPE_SD),
    "--subj_bias_var_sd",                str(PARTICIPANT_BIAS_VARIATION_SD),
    "--subj_dspeed_bias_var_sd",         str(PARTICIPANT_DIVERGENCE_SPEED_BIAS_VARIATION_SD),
]

if DUMP_OVERALL_FIXATION_STATS:
    run_args.append("--dump_per_trial_fixation_stats")
if DUMP_PER_TRIAL_FIXATION_STATS:
    run_args.append("--dump_overall_fixation_stats")

subprocess.run(run_args)

