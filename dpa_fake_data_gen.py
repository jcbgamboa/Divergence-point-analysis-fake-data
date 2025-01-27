# Generate fake data for Divergence Point Analysis

# Imports that produce dependencies
import pandas as pd    # requires `pip install pandas`

# Python native imports
import os
import math
import argparse
import random

WARNINGS_ON = True           # If false, deactivate all warnings

PRETRIAL_BUFFER = 1000
POSTTRIAL_BUFFER = 500

DPA_DISTANCE = 200           # How many consecutive ttests need to be significant
                             # for us to decide we found a divergence
TTEST_SIGNIFICANCE = 1.96

FIXATION_LEN_MU = 215        # Fixations should be between 180 and 250. 215 is the
FIXATION_LEN_SD = 35         # midpoint, and 215-35=180, and 215+35=250


all_fixation_lengths = []                               # for stats
item_dpoint_biases = {}
item_dspeed_biases = {}
item_prob_biases = {}

def parse_command_line():
    description = ''
    argparser = argparse.ArgumentParser(description=description)
    argparser.add_argument('--n_subjs', metavar='n_subjs',
                           type=int,
                           default=50,
                           help='Number of participants to be generated')

    argparser.add_argument('--n_trials', metavar='n_trials',
                           type=int,
                           default=12,
                           help='Number of trials to be generated by participant '
                                'by condition (e.g., if it is 2, then a given '
                                'participant will have 2 trials per condition).')

    argparser.add_argument('--trial_len', metavar='trial_len',
                           type=int,
                           default=1000,
                           help='Length of the trial in miliseconds.')

    argparser.add_argument('--dpoint', metavar='dpoint',
                           type=int,
                           default=300,
                           help='The divergence point for condition 0 (in ms).')

    argparser.add_argument('--dspeed_slow_factor',
                           metavar='dspeed_slow_factor',
                           type=float,
                           default=50,
                           help='The `slow_factor` of the sigmoid() function. '
                                'Ideally, this value should be bigger than the sum '
                                'of all the other `dspeed`-related values.')

    argparser.add_argument('--n_conds', metavar='n_conds',
                           type=int,
                           default=2,
                           help='How many conditions we have.')

    argparser.add_argument('--cond_effect', metavar='cond_effect',
                           type=int,
                           default=150,
                           help='The main effect of condition. For simplicity, each '
                                'new condition has its divergence point delayed by '
                                '`cond_effect`. (e.g., if it is 100, then the second '
                                'condition will diverge 100ms after the first, '
                                'the third condition will diverge 100ms after the '
                                'second, and so on.)')

    # Probability of looking away from the screen
    argparser.add_argument('--outmonitor_look_prob',
                           metavar='outmonitor_look_prob',
                           type=float,
                           default=0.01,
                           help='Every fixation, there is a chance a participant '
                                'looks away from the screen, i.e., does not look '
                                'towards any of the objects. This models it. '
                                '(see also `subj_outmonitor_look_bias_sd`)')


    # Random noise per trial. This is uncontrollable! Every participant varies
    # every trial just a little bit, simply because they're human
    argparser.add_argument('--rand_dp_noise_sd',
                           metavar='rand_dp_noise_sd',
                           type=float,
                           default=10,
                           help='Every trial has a divergence point that is just '
                                'a bit randomly different. This defines the SD '
                                '(in ms) of this variability.')

    argparser.add_argument('--rand_prob_noise_sd',
                           metavar='rand_prob_noise_sd',
                           type=float,
                           default=0.1,
                           help='Every trial is just slightly (and randomly) biased '
                                'towards one or the other image. This defines the SD '
                                '(in probability) of this variability.')

    argparser.add_argument('--rand_dspeed_noise_sd',
                           metavar='rand_dspeed_noise_sd',
                           type=float,
                           default=5,
                           help='Every trial is just slightly (and randomly) varied '
                                'on the "speed" with which the divergence happens. '
                                'That is, how quickly the probability of fixating on '
                                'the target increases, after the divergence point '
                                'has passed. (This is not in a clear "unit", like '
                                '"prob/ms", or anything. The value you choose here '
                                'will just influence the sigmoid '
                                'function.)')

    # Per trial per participant variables.
    # Over the random noise, some participants may have more variability, and some
    # may have less. This depends on the participant.

    argparser.add_argument('--subj_per_trial_dpoint_var_sd',
                           metavar='subj_per_trial_dpoint_var_sd',
                           type=float,
                           default=10,
                           help='The divergence point variability SD, per trial, of '
                                'participants. (some participants vary more, some vary '
                                'less.)')

    argparser.add_argument('--subj_per_trial_bias_var_sd',
                           metavar='subj_per_trial_bias_var_sd',
                           type=float,
                           default=0.1,
                           help='The variability SD, per trial, of the participant '
                                'bias towards one or the other image. (some participants '
                                'vary more, some vary less.)')

    argparser.add_argument('--subj_per_trial_dspeed_var_sd',
                           metavar='subj_per_trial_dspeed_var_sd',
                           type=float,
                           default=5,
                           help='The variability SD, per trial, of the participant '
                                'divergence "speed" towards one or the other image. '
                                '(This is not in a clear "unit", like '
                                '"prob/ms", or anything. The value you choose here '
                                'will just influence the sigmoid '
                                'function.)')


    # Per participant variables. This is set once for each participant

    # Random effects
    argparser.add_argument('--subj_dpoint_rand_intercept_sd',
                           metavar='subj_dpoint_rand_intercept_sd',
                           type=float,
                           default=50,
                           help="The variability (in ms) of the random intercept of "
                                "participants' divergence point.")

    argparser.add_argument('--subj_dpoint_rand_slope_sd',
                           metavar='subj_dpoint_rand_slope_sd',
                           default=50,
                           type=float,
                           help="The variability (in ms) of the random slope of "
                                "participants' divergence point. The random "
                                "slope will be a slight change (per participant) "
                                "of the effect of the condition.")

    argparser.add_argument('--subj_bias_var_sd',
                           metavar='subj_bias_var_sd',
                           type=float,
                           default=0.1,
                           help='The variability of a per-participant bias '
                                '(in probability) of looking towards one or the '
                                'other image.')

    argparser.add_argument('--subj_dspeed_bias_var_sd',
                           metavar='subj_dspeed_bias_var_sd',
                           type=float,
                           default=5,
                           help='The variability of a per-participant bias '
                                'of diverging either faster or slower once past '
                                'the divergence point. '
                                '(This is not in a clear "unit", like '
                                '"prob/ms", or anything. The value you choose here '
                                'will just influence the sigmoid '
                                'function.)')

    argparser.add_argument('--subj_outmonitor_look_bias_sd',
                           metavar='subj_outmonitor_look_bias_sd',
                           type=float,
                           default=0.004,
                           help='Every fixation, there is a chance a participant '
                                'looks away from the screen, i.e., does not look '
                                'towards any of the objects. While the variable '
                                '`outmonitor_look_prob` models that probability, this '
                                'variable models a per-participant random variation '
                                'that is added to it. (ideally, this should be much'
                                'smaller than `outmonitor_look_prob`)')


    # I will assume participants don't diverge different (don't have different
    # `dspeed`) in the different conditions.

    # Per item variables. This is set once for each item
    argparser.add_argument('--item_dpoint_bias_sd',
                           metavar='item_dpoint_bias_sd',
                           type=float,
                           default=50,
                           help="The variability (in ms) of the random intercept of "
                                "items' divergence point.")

    argparser.add_argument('--item_prob_bias_sd',
                           metavar='item_prob_bias_sd',
                           type=float,
                           default=0.1,
                           help="The variability (in prob) of the random intercept of "
                                "items' target probability. (i.e., for each item, one "
                                "of the two images may be more salient and call more "
                                "attention than the other, and this may vary randomly)")


    argparser.add_argument('--item_dspeed_bias_sd',
                           metavar='item_dspeed_bias_sd',
                           type=float,
                           default=5,
                           help='The variability of a per-item bias '
                                'of diverging either faster or slower once past '
                                'the divergence point. '
                                '(This is not in a clear "unit", like '
                                '"prob/ms", or anything. The value you choose here '
                                'will just influence the sigmoid '
                                'function.)')



    argparser.add_argument('--out_file', metavar='out_file',
                           type=str, default='fake_data.csv',
                           help='File to be produced with the data')

    argparser.add_argument('--rand_seed', metavar='rand_seed',
                           type=str, default=None,
                           help='File to be produced with the data')

    argparser.add_argument('--force_dpoint',
                           default=False,
                           action='store_true',
                           help='(Requires library scipy) If set, the generated '
                                'datasets will go through a simple DPA, and the '
                                'trials will be "shifted" so that the overall '
                                'DPA of the dataset is exactly at `dpoint`. '
                                '(this is much slower.)')



    argparser.add_argument('--dump_per_trial_fixation_stats',
                           default=False,
                           action='store_true',
                           help='If set, produces a file with statistics of the '
                                'fixations of each trial. Each row will contain stats '
                                'of a given trial. The last row will contain an '
                                'average of all previous rows. The file will be '
                                'called `per_trial_fixation_stats.csv`.')

    argparser.add_argument('--dump_overall_fixation_stats',
                           default=False,
                           action='store_true',
                           help='(Requires library plotnine) If set, produces a folder '
                                'with statistics about the length of the fixations, '
                                'regardless of which trial they come from. The folder '
                                'is called `fixation_stats`')

    # argparser.add_argument('--parser', metavar='parser', type=str,
    #                     default='spacy',
    #                     help='Which parser to use ("nltk" or "spacy")')

    return argparser.parse_args()


#####################################

def sigmoid(x, slow_factor, rand_effect):
    # This is:
    #              (version A)    (version B)
    #                   x
    #                  e              1
    # sigmoid(x) =   -------   =   ---------
    #                     x              -x
    #                1 + e          1 + e
    #
    # `slow_factor` is just supposed to make it approach 1 slower.
    #
    # According to https://stackoverflow.com/a/64717799 , the version A is
    # numerically stable when x<0, and the version B is numerically stable when
    # x>0. Since my x is always positive, I will use only version B
    divisor = slow_factor + sum(rand_effect)
    if divisor <= 0:
        if (x == 0 and      # We say this only once per trial (this is a hack)...
           WARNINGS_ON):   # ... and only if warnings are on (by default, they are)
            print("*-*-*-*-*")
            print("WARNING: SIGMOID'S `DIVISOR` IS NEGATIVE.")
            print("You probably want to either increase `args.dspeed_slow_factor` or "
                  "decrease the other `dspeed` parameters.")
            print("  args.dspeed_slow_factor: ", slow_factor)
            print("  random_dspeed_noise: ", rand_effect[0])
            print("  subj_per_trial_dspeed_var: ", rand_effect[1])
            print("  subj_dspeed_bias: ", rand_effect[2])
            print("  item_dspeed_bias: ", rand_effect[3])
            print("For now, we'll a different sigmoid that *is* numerically stable.")
            print("*-*-*-*-*")
        # This is probably not what we want. Not only for numerical stability,
        # but also because we probably don't want a super fast divergence (as we'd
        # get when the divisor is negative). Still, to prevent crashing, let's use
        # the sigmoid "Version A", which is numerically stable in this case.
        return (math.e ** (x/divisor)) / (1 + math.e ** (x/divisor))
    return 1 / (1 + math.e ** (-x/divisor))

def get_look_probs(trial_len,
                   pretrial_buffer,
                   cond,
                   subj_per_trial_dp_var_sd,
                   subj_per_trial_bias_var_sd,
                   subj_per_trial_dspeed_var_sd,
                   subj_bias_toward_obj,
                   subj_dspeed_bias,
                   subj_dpoint_random_intercept,
                   subj_dpoint_random_slope,
                   item_dpoint_bias,
                   item_prob_bias,
                   item_dspeed_bias,
                   args):
    condition_fixed_effect = cond * (args.cond_effect + subj_dpoint_random_slope)

    random_dp_noise = int(random.gauss(mu=0, sigma=args.rand_dp_noise_sd))
    random_prob_noise = random.gauss(mu=0, sigma=args.rand_prob_noise_sd)
    random_dspeed_noise = random.gauss(mu=0, sigma=args.rand_dspeed_noise_sd)

    subj_per_trial_dp_var = int(random.gauss(mu=0, sigma=subj_per_trial_dp_var_sd))
    subj_per_trial_bias_var = int(random.gauss(mu=0, sigma=subj_per_trial_bias_var_sd))
    subj_per_trial_dspeed_var = random.gauss(mu=0, sigma=subj_per_trial_dspeed_var_sd)

    divergence_moment = (
            pretrial_buffer +
            args.dpoint +
            random_dp_noise +
            condition_fixed_effect +
            subj_dpoint_random_intercept +
            subj_per_trial_dp_var +
            item_dpoint_bias
    )
    #print(condition_fixed_effect, random_dp_noise, random_prob_noise , subj_dpoint_random_intercept,
    #      subj_per_trial_dp_var_sd,
    #      subj_per_trial_dp_var, divergence_moment)

    return ([0.5 + random_prob_noise + subj_per_trial_bias_var + subj_bias_toward_obj + item_prob_bias
            for i in range(divergence_moment)]
            +
            [sigmoid(i, slow_factor=args.dspeed_slow_factor,
                     rand_effect=[random_dspeed_noise, subj_per_trial_dspeed_var,
                                     subj_dspeed_bias, item_dspeed_bias]) +
                 random_prob_noise + subj_per_trial_bias_var + subj_bias_toward_obj + item_prob_bias
             for i in range(trial_len-divergence_moment)])



def get_events(trial_len):
    # I am using the word "event" here to denote (basically) the fixations.
    # The plan is to have an event happen every ~200ms (a typical fixation has
    # between 180ms and 250ms), and for it to be super rare for fixations to
    # happen immediately one after another.
    events = [False]*trial_len
    fixation_lengths = []

    idx = 0
    while idx < trial_len:
        events[idx] = True
        curr_fixation_len = int(random.gauss(mu=FIXATION_LEN_MU, sigma=FIXATION_LEN_SD))
        fixation_lengths.append(curr_fixation_len)
        idx += curr_fixation_len

    all_fixation_lengths.append(fixation_lengths)
    return events

def create_dataframe(looks, subj_id, trial_id, cond):
    data = []
    for idx,i in enumerate(looks):
        looking_target = True if i == 'Target' else False
        looking_distractor = True if i == 'Distractor' else False

        data.append((idx, 'Target', int(looking_target)))
        data.append((idx, 'Distractor', int(looking_distractor)))

    milliseconds, objs, is_looking = zip(*data)

    trial_data = pd.DataFrame(data={
        'participant': subj_id,
        'condition': cond,
        'trial': trial_id,
        'time': milliseconds,
        'object': objs,
        'is_looking': is_looking
    })
    return trial_data


def generate_trial_data(subj_id,
                        trial_id,
                        cond,
                        subj_per_trial_dp_var_sd,
                        subj_per_trial_bias_var_sd,
                        subj_per_trial_dspeed_var_sd,
                        subj_bias_toward_obj,
                        subj_dspeed_bias,
                        subj_outmonitor_look_bias,
                        subj_dpoint_random_intercept,
                        subj_dpoint_random_slope,
                        item_dpoint_bias,
                        item_prob_bias,
                        item_dspeed_bias,
                        args):
    # We only care use `POSTTRIAL_BUFFER` if `force_dpoint` is set
    posttrial_buffer = POSTTRIAL_BUFFER if args.force_dpoint else 0

    prob = get_look_probs(
        args.trial_len + PRETRIAL_BUFFER + posttrial_buffer,
        PRETRIAL_BUFFER,
        cond,
        subj_per_trial_dp_var_sd,
        subj_per_trial_bias_var_sd,
        subj_per_trial_dspeed_var_sd,
        subj_bias_toward_obj,
        subj_dspeed_bias,
        subj_dpoint_random_intercept,
        subj_dpoint_random_slope,
        item_dpoint_bias,
        item_prob_bias,
        item_dspeed_bias,
        args
    )

    # The additional time (PRETRIAL_BUFFER) is so that we can treat better
    # the trial beginning
    looks = []
    events = get_events(args.trial_len + PRETRIAL_BUFFER + posttrial_buffer)
    curr_looking_at = random.random() < prob[0]
    for ms, e in enumerate(events):
        if e:
            # Let's see if the participant will look away from the monitor
            will_look_outmonitor = random.random() < args.outmonitor_look_prob + subj_outmonitor_look_bias
            if will_look_outmonitor:
                curr_looking_at = 'Away'
            else:
                curr_looking_at = 'Target' if random.random() < prob[ms] else 'Distractor'
        looks.append(curr_looking_at)

    trial_data = create_dataframe(looks[PRETRIAL_BUFFER:], subj_id, trial_id, cond)

    return trial_data

def get_item_dpoint_bias(cond, trial):
    if (cond, trial) not in item_dpoint_biases:
        item_dpoint_biases[(cond, trial)] = int(random.gauss(mu=0, sigma=args.item_dpoint_bias_sd))
    return item_dpoint_biases[(cond, trial)]

def get_item_dspeed_bias(cond, trial):
    if (cond, trial) not in item_dspeed_biases:
        item_dspeed_biases[(cond, trial)] = int(random.gauss(mu=0, sigma=args.item_dspeed_bias_sd))
    return item_dspeed_biases[(cond, trial)]

def get_item_prob_bias(cond, trial):
    if (cond, trial) not in item_prob_biases:
        item_prob_biases[(cond, trial)] = int(random.gauss(mu=0, sigma=args.item_prob_bias_sd))
    return item_prob_biases[(cond, trial)]



def generate_subj_data(subj_id, args):
    n_conditions = args.n_conds

    # These influence variations that occur every trial
    subj_per_trial_dp_var_sd = random.gauss(mu=0, sigma=args.subj_per_trial_dpoint_var_sd)
    subj_per_trial_bias_var_sd = random.gauss(mu=0, sigma=args.subj_per_trial_bias_var_sd)
    subj_per_trial_dspeed_var_sd = random.gauss(mu=0, sigma=args.subj_per_trial_dspeed_var_sd)

    # These are fixed for each subject
    subj_bias_toward_obj = random.gauss(mu=0, sigma=args.subj_bias_var_sd)
    subj_dspeed_bias = random.gauss(mu=0, sigma=args.subj_dspeed_bias_var_sd)
    subj_outmonitor_look_bias = random.gauss(mu=0, sigma=args.subj_outmonitor_look_bias_sd)

    # This is the effect of condition on each participant
    # TODO: Maybe this should inside the for loop, recalculated every condition.
    #       It won't matter now because there're only 2 conditions.
    subj_dpoint_random_intercept = int(random.gauss(mu=0, sigma=args.subj_dpoint_rand_intercept_sd))
    subj_dpoint_random_slope = int(random.gauss(mu=0, sigma=args.subj_dpoint_rand_slope_sd))

    # `subj_trials` is a list of data frames
    subj_trials = []
    for cond in range(n_conditions):
        for trial in range(args.n_trials):
            trial_id = "T" + str(trial)

            item_dpoint_bias = get_item_dpoint_bias(cond, trial)
            item_prob_bias = get_item_prob_bias(cond, trial)
            item_dspeed_bias = get_item_dspeed_bias(cond, trial)

            subj_trials.append(
                generate_trial_data(
                    subj_id,
                    trial_id,
                    cond,
                    subj_per_trial_dp_var_sd,
                    subj_per_trial_bias_var_sd,
                    subj_per_trial_dspeed_var_sd,
                    subj_bias_toward_obj,
                    subj_dspeed_bias,
                    subj_outmonitor_look_bias,
                    subj_dpoint_random_intercept,
                    subj_dpoint_random_slope,
                    item_dpoint_bias,
                    item_prob_bias,
                    item_dspeed_bias,
                    args)
            )
    return subj_trials


def generate_data(args):
    # `all_data` is a list of data frames
    all_data = []
    for subj in range(args.n_subjs):
        subj_id = "P" + str(subj)
        # Define other variables
        subj_trials = generate_subj_data(subj_id, args)
        all_data.extend(subj_trials)

    return pd.concat(all_data, axis=0)

#####################################

def per_trial_fixation_stats():
    maxes = []
    mins = []
    means = []
    medians = []
    means_without_last = []
    medians_without_last = []

    for i in all_fixation_lengths:
        maxes.append(max(i))
        mins.append(min(i))
        means.append(s.mean(i))
        medians.append(s.median(i))
        means_without_last.append(s.mean(i[:-1]))
        medians_without_last.append(s.median(i[:-1]))

    # Now, let's get the average of them all into the last line
    maxes.append(s.mean(maxes))
    mins.append(s.mean(mins))
    means.append(s.mean(means))
    medians.append(s.mean(medians))
    means_without_last.append(s.mean(means_without_last))
    medians_without_last.append(s.mean(medians_without_last))

    df = pd.DataFrame(data={
        "Max": maxes,
        "Min": mins,
        "Mean": means,
        "Median": medians,
        "Mean_nolast": means_without_last,
        "Median_nolast": medians_without_last
    })
    return df


def overall_fixation_stats(out_folder):
    # I know this is unreadable. Look here: https://stackoverflow.com/a/952952
    all_fixations = [i for j in all_fixation_lengths for i in j]

    # First, let's assume this is a normal distribution. What can we calculate?
    max_f = max(all_fixations)
    min_f = min(all_fixations)
    mean_f = s.mean(all_fixations)
    median_f = s.median(all_fixations)
    sd_f = s.stdev(all_fixations)

    # Now I want to plot these. I want to see the distribution.
    df = pd.DataFrame({
        'x': all_fixations
    })
    p = ggplot(df, aes(x='x')) + geom_histogram(fill='lightblue', color='black')

    # Dump stuff
    if not os.path.exists(out_folder):
        os.makedirs(out_folder)

    with open(os.path.join(out_folder, 'overall_fixation_stats.txt'), 'w') as f:
        f.write("max, min, mean, median, sd\n")
        f.write("{}, {}, {}, {}, {}".format(max_f, min_f, mean_f, median_f, sd_f))
    p.save(os.path.join(out_folder, 'histogram_fixation.svg'))

#####################################

def run_ttests(df):
    # For the calculations below, we will only consider the looks to the Target
    no_distractor = df.loc[df['object'] != 'Distractor']
    no_distractor_nor_aways = no_distractor.loc[no_distractor['object'] != 'Away']

    # This will give us the mean `looks` for each combination of
    # (participant, time, condition)
    per_ms_looks = no_distractor_nor_aways.groupby(['participant', 'time', 'condition']).apply(
        lambda x: x['is_looking'].mean())

    # `per_ms_looks` is a Series, which I dislike. Let's make it a Data Frame
    per_ms_looks_df = pd.DataFrame({'participant': per_ms_looks.index.get_level_values(0),
                                    'time': per_ms_looks.index.get_level_values(1),
                                    'condition': per_ms_looks.index.get_level_values(2),
                                    'mean_looks': per_ms_looks.values})

    # Now we calculate, for each pair (time, condition), the t-test over all participant means
    ttests = per_ms_looks_df.groupby(['time', 'condition']).apply(
        lambda x: stats.ttest_1samp(x['mean_looks'],
                                    popmean=0.5).statistic)

    # `ttests` is a Series, which I dislike. Let's make it a Data Frame
    ttests_df = pd.DataFrame({'time': ttests.index.get_level_values(0),
                              'condition': ttests.index.get_level_values(1),
                              'tvalue': ttests.values})

    return ttests_df

def find_divergence_point(ttests_df):
    # Ok... I did calculate the ttests for all conditions; and it may be useful
    # in the future; BUT...
    # I only need the condition 0 for my purposes here.
    ttests_only_cond0 = ttests_df.loc[ttests_df['condition'] == 0]

    condition_count = 0
    divergence_point = None
    for index, row in ttests_df.iterrows():
        cond = row['condition']
        if cond != 0:
            continue

        if row['tvalue'] > TTEST_SIGNIFICANCE:
            condition_count += 1
        else:
            condition_count = 0

        if condition_count >= DPA_DISTANCE:
            divergence_point = row['time'] - DPA_DISTANCE
            break

    return divergence_point

def run_ttests_and_trim(df, args):
    ttests_df = run_ttests(df)
    actual_divergence_point = find_divergence_point(ttests_df)

    # This is how much we want to trim the beginning of every trial in the dataset
    # (note the order of the calculation. Typically, the `actual_divergence_point`
    # will be *after* `args.point`)
    time_is_off_by = actual_divergence_point - args.dpoint

    # Shift the trial by the calculated offset
    df['time'] -= time_is_off_by

    # Trim any `ms` that is below 0 or above the user-defined trial length
    df = df.loc[df['time'] >= 0]
    df = df.loc[df['time'] < args.trial_len]
    return df


#####################################


if __name__ == '__main__':
    # Tests the functionalities of this file
    print("Parsing command line...")
    args = parse_command_line()

    if args.rand_seed is not None:
        print('Received random seed. Setting it...')
        random.seed(args.rand_seed)

    print("Generating data...")
    out_df = generate_data(args)

    if args.force_dpoint:
        from scipy import stats
        print("Calculating t-tests and forcing divergence point...")
        out_df = run_ttests_and_trim(out_df, args)

    print("Dumping into output file...")
    out_df.to_csv(args.out_file)

    if args.dump_per_trial_fixation_stats:
        import statistics as s
        print("Calculating per trial fixation stats...")
        stats = per_trial_fixation_stats()
        print("Dumping per trial fixation stats...")
        stats.to_csv('per_trial_fixation_stats.csv')
        #print(stats)

    if args.dump_overall_fixation_stats:
        import statistics as s
        from plotnine import *
        print("Calculating overall fixation stats...")
        stats = overall_fixation_stats('fixation_stats')
        print("Dumping per trial fixation stats...")

    print("Done")

