# create an example to illustrate why you need 2 proxies to know the ATE 

# variables
# A treatment
# Y outcome
# U confounder
# W proxy
#     U ---> W
#    / \  
#   /   \ 
#  A --->Y

import numpy as np 

# Number of samples
n_samples = 10000

# U is a binomial with probability 0.5
U = np.random.binomial(1, 0.5, n_samples)

# A is a binomial with probability 0.5 if U is 0, and 0.7 if U is 1
A = np.random.binomial(1, np.where(U == 0, 0.5, 0.7), n_samples)

# Y is a binomial with probability 0.5 + A*0.2 + U*0.2
Y_prob = 0.5 + A * 0.2 + U * 0.2
Y = np.random.binomial(1, Y_prob, n_samples)

# W is a binomial with probability 0.5 if U is 0, and 0.8 if U is 1
W = np.random.binomial(1, np.where(U == 0, 0.5, 0.8), n_samples)


# Ha the matrix is supossed to be 
# array([[ 1.03333333,  0.36666667],
#        [-0.03333333,  0.63333333]])


# which other matrix would hold here? 


# arthur gretton example
# \begin{aligned}
# U & \sim \operatorname{Unif}(-1,1), & A & =\Phi(U)+\varepsilon_1 \\
# Y & =\sin (2 \pi U)+A^2-0.3, & W & =\exp (U)+\varepsilon_2
# \end{aligned}
# Here, Φ is the Gaussian error function, and ε1 ∼ N (0, 0.01), ε2 ∼ N (0, 0.0025). The true structural function
# is fstruct(a) = a2 − 0.3



# two setups to consider: Noisy outcome and High dimensional proxy

Noisy_outcome = False

# sample U form uniform distribution
U = np.random.uniform(-1, 1, n_samples)

# A is the treatment, and is a function of U plus some noise
A =  + np.random.normal(0, 0.01, n_samples)

# Y is the outcome, and is a function of U and A plus some noise
Y = np.sin(2 * np.pi * U) + A**2 - 0.3 + np.random.normal(0, 0.01, n_samples)

if Noisy_outcome:
    Y = Y + np.random.normal(0, 1, n_samples)
