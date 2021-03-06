'''
This script explores the KS Test, especially its large-sample properties.
'''


import numpy as np
from scipy import stats
import matplotlib.pyplot as plt

rng = np.random.default_rng()

# from https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.ks_2samp.html


n1 = 200
n2 = 300

# different location and scale, easily reject null
rvs1 = stats.norm.rvs(size=n1, loc=0., scale=1, random_state=rng)
rvs2 = stats.norm.rvs(size=n2, loc=0.5, scale=1.5, random_state=rng)
stats.ks_2samp(rvs1, rvs2)

# essentially same distribution, cannot reject null
rvs1 = stats.norm.rvs(size=n1, loc=0., scale=1, random_state=rng)
rvs2 = stats.norm.rvs(size=n2, loc=0.01, scale=1, random_state=rng)
stats.ks_2samp(rvs1, rvs2)

# From the docs, the defualt hull hypothesis is "equal distributions" with
# a default alternative hypothesis of "not equal" -- in either direction.


# Is the KS test appropriately sensitive in larger-sample settings?

n1 = 2000
n2 = 6000

p_vals = []

# note: this loop takes about a minute
for i in range(1000):
    rvs1 = stats.norm.rvs(size=n1, loc=0.0, scale=1, random_state=rng)
    rvs2 = stats.norm.rvs(size=n2, loc=0.0, scale=1, random_state=rng)
    stat = stats.ks_2samp(rvs1, rvs2)
    p_vals.append(stat[1])


# We should expect a p-value of < 0.05 5% of the time (be definition)
small_pvals = [x for x in p_vals if x < 0.05]
len(small_pvals) / len(p_vals) # seems about right

'''
Note that this test asks the question: are these distributions the same?
Kent's specific question *might* be different. He specifically asked: Is
a pair of distributions generated by a particular segmentation of a parent
distribution statistically more different than a random cut of the parent
distribution? For that, we'll build a bootstrap distribution of the KS test
statistic.

Note: That's *really* similar to asking if a particular sub-component of 
a parent distribution is the same as the parent distribution, which you can 
ask and answer directly with the KS test.
'''


# a function to test whether a particular partition of a distribution is
# statistically different from a random partition of the distribution of the same size
# parent_distribution: all the samples
# sub_distr1: a subset of the parent_distribution
# sub_distr2: the remainder of the parent_distribution
# note set(sub_distr1) + set(sub_distr2) should = parent_distribution
# plot: boolean, whether to emit a histogram of the test statistics with a red line for
# the value of the stat for your cut
def bootstrap_ks(parent_distribution, sub_distr1, sub_distr2, plot=False):
    # draw a bunch of random cuts of parent distribution of right size
    # this is our bootstrap distribution
    ks_stats = []
    set_total = set(list(range(len(parent_distribution))))
    for i in range(1000):
        rand_sub_1 = np.random.choice(list(range(len(parent))), len(sub_distr1), replace=False)
        rand_sub_2 = np.array(list(set_total - set(rand_sub_1)))
        x_a = parent_distribution[rand_sub_1]
        x_b = parent_distribution[rand_sub_2]
        stat = stats.ks_2samp(x_a, x_b)
        ks_stats.append(stat[0])
    # find the value of the KS statistic for our actual sub-distributions
    test_stat = stats.ks_2samp(sub_distr1, sub_distr2)[0]
    # find the quantile in the distribution of ks_stats for our test statistic
    numerator = len([x for x in ks_stats if x < test_stat])
    ptile = float(numerator)/len(ks_stats)
    if plot:
        plt.hist(ks_stats)
        plt.axvline(x=test_stat, c="red")
    return ptile


# test on random subset, should be unremarkable
p = np.random.normal(0,1,1000)
set_total = set(list(range(len(p))))
rand_sub_1 = np.random.choice(list(range(len(p))), 300, replace=False)
rand_sub_2 = np.array(list(set_total - set(rand_sub_1)))
x_a = p[rand_sub_1]
x_b = p[rand_sub_2]

bootstrap_ks(p, x_a, x_b)

# test on non-random subset, should be high (close to 1.0)
x_a = np.random.normal(0, 1, 300)
x_b = np.random.normal(0.3, 1, 700)
p = np.concatenate((x_a, x_b))
bootstrap_ks(p, x_a, x_b, plot=True)

