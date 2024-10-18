import time
import matplotlib.pyplot as plt
import numpy as np
from collections import defaultdict
from TwoSAT_Borg import TwoSATSolver
from DumbSat_Borg import DumbSAT

#extract data from csv
def process_2sat_csv(file_path):
    with open(file_path, 'r', encoding='utf-8-sig') as f:
        lines = f.readlines()

    problems = []
    current_problem = []
    num_vars = 0

    for line in lines:
        line = line.strip()
        #line start 
        if line.startswith('p,cnf'):
            if current_problem:
                problems.append((num_vars, current_problem))
                current_problem = []
            parts = line.split(',')
            num_vars = int(parts[2])
        #breaker between problems
        elif line == '?':
            if current_problem:
                problems.append((num_vars, current_problem))
                current_problem = []

        elif not line or line.startswith('c'):
            continue

        else:
            try:
                literals = list(map(int, line.split(',')[:2]))
                current_problem.append(tuple(literals))
            except ValueError:
                continue

    if current_problem:
        problems.append((num_vars, current_problem))

    return problems

#2 SAT solver
def solve_with_two_sat(file_path):
    problems = process_2sat_csv(file_path)[:60] # jsut do first 60 to save run time
    grouped_timings = defaultdict(list)

    for idx, (num_vars, clauses) in enumerate(problems):
        solver = TwoSATSolver(num_vars)
        for clause in clauses:
            solver.add_clause(clause[0], clause[1])

        start_time = time.time()
        solver.solve()
        end_time = time.time()

        time_taken = (end_time - start_time) * 1e6  # microseconds
        grouped_timings[(num_vars, len(clauses))].append(time_taken)

    #calculate average timings for each group and sort by problem size
    average_timings = sorted([(params, np.mean(times)) for params, times in grouped_timings.items()],
                             key=lambda x: x[0][0] + x[0][1])
    return average_timings

# Dumb Sat Solver
def solve_with_dumb_sat(file_path):
    problems = process_2sat_csv(file_path)[:60]  #first 60 to save runtime 
    dumb_solver = DumbSAT([clauses for _, clauses in problems])
    timings = []

    for formula in dumb_solver.formulas:
        start_time = time.time()
        result, _ = dumb_solver._DumbSAT__brute_force(formula)
        end_time = time.time()

        time_taken = (end_time - start_time) * 1e6  # Convert to microseconds
        timings.append(time_taken)

    # Number of variables and clauses groupings for apporximate size
    grouped_timings = defaultdict(list)
    for (num_vars, clauses), time_taken in zip(problems[:len(timings)], timings):
        grouped_timings[(num_vars, len(clauses))].append(time_taken)

    # average timings for each group and sort by problem size
    average_timings = sorted([(params, np.mean(times)) for params, times in grouped_timings.items()],
                             key=lambda x: x[0][0] + x[0][1])
    return average_timings

# comparison of both solvers plot
def plot_comparison(two_sat_timings, dumb_sat_timings):
    # problem sizes and times for both solvers
    two_sat_problem_sizes = [params[0] + params[1] for params, _ in two_sat_timings]
    two_sat_times = [time for _, time in two_sat_timings]

    dumb_sat_problem_sizes = [params[0] + params[1] for params, _ in dumb_sat_timings]
    dumb_sat_times = [time for _, time in dumb_sat_timings]

    #line graph for TwoSAT
    plt.figure(figsize=(12, 8))
    plt.plot(two_sat_problem_sizes, two_sat_times, 'bo-', label='TwoSAT Solver (µs)')

    # line graph for DumbSAT
    plt.plot(dumb_sat_problem_sizes, dumb_sat_times, 'ro-', label='DumbSAT Solver (µs)')

    # titles and labels
    plt.title('Comparison of 2-SAT and Dumb SAT Solver Time Complexity (Microseconds)')
    plt.xlabel('Problem Size (Num Vars + Num Clauses)')
    plt.ylabel('Average Time (µs)')
    plt.legend()
    plt.grid(True)
    plt.show()

#comparison on the provided CSV file
file_path = 'data_2SAT.cnf.csv'
two_sat_timings = solve_with_two_sat(file_path)
dumb_sat_timings = solve_with_dumb_sat(file_path)
plot_comparison(two_sat_timings, dumb_sat_timings)
