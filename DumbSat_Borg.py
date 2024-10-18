import csv
import itertools
import time

#DumbSat Solver

class DumbSAT:
    def __init__(self, formulas):
        if isinstance(formulas, str):
            self.formulas = self.__read_cnf_csv(formulas)
        else:
            self.formulas = formulas
        self.satisfiableArray = []
        self.timeArray = []

    def __read_cnf_csv(self, file_name):
        formulas = []
        current_formula = []

        with open(file_name, mode='r', encoding='utf-8-sig') as file:
            csv_reader = csv.reader(file)

            for line in csv_reader:
                # Skip any empty lines
                if not line or all(col == '' for col in line):
                    continue

                # Process comment lines
                if line[0].startswith('c'):
                    # Start a new formula if there's an existing one
                    if current_formula:
                        formulas.append(current_formula)
                        current_formula = []
                    continue

                # Process the problem line
                if line[0].startswith('p'):
                    continue  # We can ignore the problem line in this context

                # Process clause lines
                clause = [int(literal) for literal in line if literal and literal != '0']
                if clause:  # Only add non-empty clauses
                    current_formula.append(tuple(clause))

            # Append the last formula if any
            if current_formula:
                formulas.append(current_formula)

        return formulas

    def __brute_force(self, formula):
        # Extract all unique literals from the given formula
        literals = set()
        for clause in formula:
            for literal in clause:
                literals.add(abs(literal))

        literals = list(literals)
        n = len(literals)

        # Generate all combinations of truth assignments
        for seq in itertools.product([True, False], repeat=n):
            assignment = dict(zip(literals, seq))

            # Check if the current assignment satisfies the CNF
            if self.__is_satisfiable(formula, assignment):
                return True, assignment

        return False, None

    def __is_satisfiable(self, formula, assignment):
        for clause in formula:
            satisfied = False
            for literal in clause:
                if (literal > 0 and assignment[literal]) or (literal < 0 and not assignment[abs(literal)]):
                    satisfied = True
                    break
            if not satisfied:
                return False
        return True

    def solve(self):
        results = []
        for formula in self.formulas:
            start_time = time.time()
            result, _ = self.__brute_force(formula)
            end_time = time.time()
            exec_time = (end_time - start_time) * 1e6  # Convert to microseconds
            results.append(exec_time)
        return results

    def getSatisfiableArray(self):
        return self.satisfiableArray

    def getTimeArray(self):
        return self.timeArray
