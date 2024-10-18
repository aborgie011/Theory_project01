import time
import csv
import matplotlib.pyplot as plt
import numpy as np
from collections import defaultdict

# Two SAT Solver class using DPLL algorithm
class TwoSATSolver:
    def __init__(self, num_vars):
        self.num_vars = num_vars
        self.clauses = []

    def add_clause(self, x, y):
        self.clauses.append((x, y))

    def __select_literal(self, cnf):
        for clause in cnf:
            for literal in clause:
                return abs(literal)

    def __dpll(self, cnf, assignments={}):
        # Base case: if CNF is empty, all clauses are satisfied
        if len(cnf) == 0:
            return True, assignments

        #any clause is empty, the CNF is unsatisfiable
        if any(len(clause) == 0 for clause in cnf):
            return False, None

        #literal to branch on
        l = self.__select_literal(cnf)

        #l is True and simplify the CNF
        new_cnf = [clause for clause in cnf if l not in clause]
        new_cnf = [tuple(lit for lit in clause if lit != -l) for clause in new_cnf]
        sat, vals = self.__dpll(new_cnf, {**assignments, **{l: True}})
        if sat:
            return sat, vals

        #l is False and simplify the CNF
        new_cnf = [clause for clause in cnf if -l not in clause]
        new_cnf = [tuple(lit for lit in clause if lit != l) for clause in new_cnf]
        sat, vals = self.__dpll(new_cnf, {**assignments, **{l: False}})
        if sat:
            return sat, vals

        return False, None

    def solve(self):
        result, assignments = self.__dpll(self.clauses)
        return result, assignments


#process the file and extract multiple problems
def process_2sat_csv(file_path):
    with open(file_path, 'r', encoding='utf-8-sig') as f:
        lines = f.readlines()

    problems = []
    current_problem = []
    num_vars = 0

    for line in lines:
        line = line.strip()

        if line.startswith('p,cnf'):
            if current_problem:
                problems.append((num_vars, current_problem))
                current_problem = []
            parts = line.split(',')
            num_vars = int(parts[2])

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


# run each 2-SAT problem,
def solve_multiple_problems(file_path):
    problems = process_2sat_csv(file_path)
    grouped_timings = defaultdict(list)
    
    for idx, (num_vars, clauses) in enumerate(problems):
        solver = TwoSATSolver(num_vars)
        for clause in clauses:
            solver.add_clause(clause[0], clause[1])

        start_time = time.time()
        satisfiable, _ = solver.solve()
        end_time = time.time()

        #convert time to microseconds
        time_taken = (end_time - start_time) * 1e6
        print(f"Problem {idx+1}: Satisfiable = {satisfiable}, Time taken = {time_taken:.2f}µs")
        
        #timings by number of variables and clauses
        grouped_timings[(num_vars, len(clauses))].append(time_taken)

    #average timings for each group and sort by problem size
    average_timings = sorted([(params, np.mean(times)) for params, times in grouped_timings.items()],
                             key=lambda x: x[0][0] + x[0][1])
    return average_timings


#plot average time complexity as a line graph with a line of best fit
def plot_time_complexity(average_timings):
    #extract problem parameters and average times
    problem_sizes = [params[0] + params[1] for params, _ in average_timings]
    avg_times = [time for _, time in average_timings]

    # numpy arrays for fitting
    problem_sizes_np = np.array(problem_sizes)
    avg_times_np = np.array(avg_times)

    # line to the data
    coefficients = np.polyfit(problem_sizes_np, avg_times_np, 1)
    polynomial = np.poly1d(coefficients)
    line_of_best_fit = polynomial(problem_sizes_np)

    #line graph
    plt.figure(figsize=(10, 6))
    plt.plot(problem_sizes_np, avg_times_np, 'bo-', label='Average Execution Time (µs)')
    plt.plot(problem_sizes_np, line_of_best_fit, 'r--', label='Line of Best Fit')

    #titles and labels
    plt.title('2-SAT Solver Average Time Complexity (Microseconds)')
    plt.xlabel('Problem Size (Num Vars + Num Clauses)')
    plt.ylabel('Average Time (µs)')
    plt.legend()
    plt.grid(True)
    plt.show()

#Usage to Generaete Graph 

#run the test on the provided CSV file and plot the timings
#file_path = 'data_2SAT.cnf.csv'
#average_timings = solve_multiple_problems(file_path)
#plot_time_complexity(average_timings)
