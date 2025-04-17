config = {
    # Datasets per parameter set
    'n_datasets_per_paramset': 1,

    # Random seed
    'rand_seed': 1234,

    # Output folder name
    'out_folder': 'out_datasets',

    # Output file name prefix
    'out_file': 'fakedata',

    # Divergence Speed "slow factor"'
    'dspeed_slow_factor': 50,

    # Force Divergence Point
    'force_divergence_point': False,

    # Force Divergence Point (Memory efficient)
    'force_dp_memory_efficient': True,

    # Population Multiplier'
    'population_multiplier': 1,

    # Number of participants
    'n_subjs': 40,

    # Number of condition
    'n_conds': 2,

    # Number of trials per condition'
    'n_trials': 80,

    # Trial length (in ms)
    'trial_len': 1000,

    # Divergence Point
    'dpoint': 300,

    # Effect of Condition
    'cond_effect': '100, 200',

    # Variation on Divergence Point
    'rand_dp_noise_sd': 10,

    # Variation in Prob. of looks to Target
    'rand_prob_noise_sd': 0.01,

    # Variation in "Div. Speed"
    'rand_dspeed_noise_sd': 2,

    # Variation on Divergence Point
    'subj_per_trial_dpoint_var_sd': 7,

    # Variation in Prob. of looks to Target
    'subj_per_trial_bias_var_sd': 0.005,

    # Variation in "Div. Speed"
    'subj_per_trial_dspeed_var_sd': 2,

    # Variation in Random Intercepts
    # (i.e., in the Divergence Point for Condition 0)
    'subj_dpoint_rand_intercept_sd': 15,

    # Variation in Random Slopes
    # (i.e., in the difference between conditions)
    'subj_dpoint_rand_slope_sd': 5,

    # Variation in Prob. of looks to Target
    # (i.e., of Biases to Target Obj.)
    'subj_bias_var_sd': 0.05,

    # Variation in "Div. Speed"
    'subj_dspeed_bias_var_sd': 4,

    # Variation on Divergence Point
    'item_dpoint_bias_sd': 15,

    # Variation in Prob. of looks to Target
    'item_prob_bias_sd': 0.05,

    # Variation in "Div. Speed"
    'item_dspeed_bias_sd': 5,

    # Overall Prob. of looking away
    'outmonitor_look_prob': 0.01,

    # Variation per Participant
    'subj_outmonitor_look_bias_sd': 0.001
}