import numpy as np
import random

#Generate environements
# 10 bits = 1024 env
n = 10
env_list = [bin(x)[2:].rjust(n, "0") for x in range(2**n)]


#From string to binary
for i in range(len(env_list)):
    env_list[i] = [int(numeric_string) for numeric_string in env_list[i]]

#Every environment sum is == 5
env_list = [i for i in env_list if sum(i) == 5]


#10 is also the number of traits that the individual can "invest" in
# T = (T1, T2, T3...T10)
# Sum of T_i is always 1 (trade-off)
# Mutation is for example T2 =- 0.1 and respectively T6 =+ 0.1

#Initialize one individual
ind1 = [np.random.dirichlet(np.ones(10),size=1)] #sum = 1
#ind2 = np.array([0, 0, 0, 0, 0, 0, 0, 0, 0, 1],  dtype=float)
print(np.sum(ind1)) #sum close to one but not exactly 1 #TODO

def mutate(ind):
    # select a random trait
    T_x = random.randint(0, 9)
    # select a random trait different from previous one
    T_y = random.choice([i for i in range(0, 10) if i != T_x])

    #Avoid ind[T_x] to go lower then 0 and ind[T_y] to go higher then 1
    step = np.random.uniform(0, min(ind[T_x], (-ind[T_y] + 1)))

    ind[T_x] -= step
    ind[T_y] += step
    return ind



fit = 0
#fitness(ind1, env_list[834])
def fitness(ind, env):
    #np.linalg.norm(ind - env) is the mismatch
    # The 10 is arbitrary, worst fitness possible is 6.83772..
    fit = 10 - np.linalg.norm(ind - env)
    return fit


#Print fitness of ind in every environment
#Computational costly but if we store fitness in every environement then we can see if they are "specializing"
#Fitness in a set of enviornment much greater then in a different subset
for i in range(len(env_list)):
    print(env_list[i], fitness(ind1, env_list[i]))











