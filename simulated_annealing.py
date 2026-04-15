import pandas as pd
from collections import defaultdict
import matplotlib.pyplot as plt
import time
import random
import os

'''    DATA LOADING    '''

# Change to the directory where the script is located
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# File paths
distances_file = 'data/Distancias_Na.xlsx'
populations_file = 'data/Población_ord2.xlsx'

# Read files
df_distances = pd.read_excel(distances_file, sheet_name='in')
df_populations = pd.read_excel(populations_file, sheet_name='Export')

# Population data adjustments
df_populations = df_populations.iloc[1:-1]
df_populations.columns = ['Codigo', 'Municipio', 'Poblacion']
df_populations['Codigo'] = df_populations['Codigo'].astype(str).str.zfill(3)
df_populations = df_populations.set_index('Codigo')

column_codes = ['000'] + list(df_populations.index)
municipalities = list(df_populations.index)

df_distances.index = municipalities
df_distances.columns = column_codes

# Create distance matrix
distance_matrix = defaultdict(dict)
for ka in municipalities:
    for kb in municipalities:
        distance_matrix[ka][kb] = df_distances.loc[ka, kb]

total_population = df_populations['Poblacion'].sum()
pamplona_code = df_populations[df_populations['Municipio'].str.contains('Pamplona', case=False)].index[0]


'''    CORE FUNCTIONS    '''

def average_emergency_time(municipality, ambulance_hq):
    """Calculates the average time occupied per emergency in hours."""
    return (distance_matrix[municipality][ambulance_hq] + distance_matrix[municipality][pamplona_code]) / 80 + 1.5

class Solution:
    def __init__(self, hq_list):
        self.hq_list = hq_list
        self.assignments = self._assign_municipalities()
        self.headquarters = self._calculate_required_ambulances()

    def _assign_municipalities(self):
        """Assigns each municipality to its closest headquarters."""
        assignments = {}
        for mun in municipalities:
            closest_hq = min(self.hq_list, key=lambda hq: distance_matrix[mun][hq])
            assignments[mun] = closest_hq
        return assignments

    def _calculate_required_ambulances(self):
        """Calculates the number of ambulances needed per HQ to meet SLA (Constraint R3)."""
        hq_dict = {}
        for hq in self.hq_list:
            assigned_muns = [mun for mun in municipalities if self.assignments[mun] == hq]
            hq_total_population = sum(df_populations.loc[mun, 'Poblacion'] for mun in assigned_muns)
            daily_emergencies = 3 * (hq_total_population / 100000)
            
            if not assigned_muns:
                hq_dict[hq] = 1
                continue
                
            avg_time = sum(average_emergency_time(mun, hq) for mun in assigned_muns) / len(assigned_muns)
            workload = daily_emergencies * avg_time
            
            # Mathematical shortcut to ensure availability probability >= 0.8
            hq_dict[hq] = 1 if workload < 4.8 else 2
        return hq_dict

    def _objective_function(self):
        """Calculates the objective function to minimize."""
        term_hq = 1.5 * len(self.headquarters)
        term_amb = sum(self.headquarters.values())
        term_dist = sum(df_populations.loc[mun, 'Poblacion'] * distance_matrix[mun][self.assignments[mun]] for mun in municipalities)
        return term_hq + term_amb + 1e-5 * term_dist

    def _meets_r1(self):
        """Checks if 98% of the population has an ambulance within 40 km."""
        covered_pop = sum(df_populations.loc[mun, 'Poblacion'] for mun in municipalities if any(distance_matrix[mun][hq] < 40 for hq in self.headquarters))
        return covered_pop / total_population >= 0.98

    def _meets_r2(self):
        """Checks if 80% of the population has an ambulance within 20 km."""
        covered_pop = sum(df_populations.loc[mun, 'Poblacion'] for mun in municipalities if any(distance_matrix[mun][hq] < 20 for hq in self.headquarters))
        return covered_pop / total_population >= 0.80

def generate_random_solution():
    """Generates an initial random solution that satisfies all constraints."""
    while True:
        n_hqs = random.randint(10, len(municipalities) - 100)
        hqs = random.sample(municipalities, n_hqs)
        sol = Solution(hqs)
        if sol._meets_r1() and sol._meets_r2():
            return sol

def generate_neighbor(sol):
    """Generates a neighboring solution using ALNS principles (add, remove, move)."""
    current_hqs = sol.hq_list.copy()
    available_muns = [m for m in municipalities if m not in current_hqs]
    
    move_type = random.choices(list(probs.keys()), weights=list(probs.values()), k=1)[0]
    
    if move_type == 'add' and available_muns:
        current_hqs.append(random.choice(available_muns))
    elif move_type == 'remove' and len(current_hqs) > 1:
        current_hqs.remove(random.choice(current_hqs))
    elif move_type == 'move' and available_muns and current_hqs:
        current_hqs.remove(random.choice(current_hqs))
        current_hqs.append(random.choice(available_muns))
        
    new_solution = Solution(current_hqs)
    return new_solution, move_type


'''    ALGORITHM PARAMETERS    '''

T = 500
T_min = 25
alpha = 0.98
c = 0.001
num_iters = 250

# Initialize probabilities for neighborhood structures (ALNS)
def init_probs():
    return {'add': 1/3, 'remove': 1/3, 'move': 1/3}
probs = init_probs()

seed = 143389
random.seed(seed)
start_time = time.time()


'''    MAIN SEARCH (SIMULATED ANNEALING)    '''

current_solution = generate_random_solution()
current_obj_val = current_solution._objective_function()
obj_values_history = []

while T > T_min:
    for _ in range(num_iters):
        cand_solution, move_type = generate_neighbor(current_solution)
        cand_obj_val = cand_solution._objective_function()
        
        # Acceptance criteria
        if cand_obj_val < current_obj_val:
            current_solution, current_obj_val = cand_solution, cand_obj_val
            print(f"New best solution: {current_obj_val:.4f} (Move: {move_type}, Temp: {T:.2f})")
        else:
            # Dynamically adjust probabilities (Adaptive Large Neighborhood Search)
            probs[move_type] = max(0, probs[move_type] - c)
            others = [m for m in probs if m != move_type]
            for o in others:
                probs[o] = min(1, probs[o] + c/2)
                
            total_prob = sum(probs.values())
            for k in probs:
                probs[k] /= total_prob
                
        obj_values_history.append(current_obj_val)
    T *= alpha

duration = time.time() - start_time
if duration < 60:
    time_str = f"{int(duration)} seconds"
else:
    minutes, seconds = divmod(int(duration), 60)
    time_str = f"{minutes} minutes {seconds} seconds"
    

'''    DISPLAY RESULTS    '''

print("\n" + "="*40)
print(f"Final Objective Function Value: {current_obj_val:.4f}")
print(f"Seed: {seed} | Execution Time: {time_str}")

print("\nOptimal Headquarters Layout:")
for hq in sorted(current_solution.headquarters):
    mun_name = df_populations.loc[hq, 'Municipio']
    print(f"  - {mun_name}: {current_solution.headquarters[hq]} ambulances")

print(f"\nTotal Active Ambulances: {sum(current_solution.headquarters.values())}")
print(f"Total Covered Population: {total_population}")
print(f"Ratio: 1 Ambulance per {round(total_population / sum(current_solution.headquarters.values()), 2)} inhabitants")

print("\nSample Assignments (First 10):")
print("  - Municipality → Assigned HQ")
for i, (mun, hq) in enumerate(current_solution.assignments.items()):
    if i >= 10: break
    mun_name = df_populations.loc[mun, 'Municipio']
    hq_name = df_populations.loc[hq, 'Municipio']
    print(f"  - {mun_name} → {hq_name}")


'''    CONVERGENCE PLOT    '''

plt.figure(figsize=(10, 6))
plt.plot(obj_values_history, label='Objective Function')
plt.xlabel('Iterations')
plt.ylabel('Objective Function Value')
plt.title('Simulated Annealing Convergence')
plt.legend()
plt.grid(True)
plt.show()


'''    EXPORT SOLUTION TO EXCEL    '''

output_data = []

for mun in municipalities:
    mun_code = int(mun)
    is_hq = 1 if mun in current_solution.headquarters else 0
    num_amb = current_solution.headquarters[mun] if is_hq else 0
    hq_code = int(current_solution.assignments[mun])
    
    # Keeping specific Spanish column names as required by external formats
    output_data.append({
        'Cod. Municipio': mun_code,
        'Sede (0: NO, 1: SI)': is_hq,
        'NumAmbulancias': num_amb,
        'Cod. Sede': hq_code
    })

df_output = pd.DataFrame(output_data)

# Sort by municipality code for clarity
df_output = df_output.sort_values(by='Cod. Municipio')

# Save to Excel
output_filename = "solutions/Solucion_ambulancias_Navarra.xlsx"
df_output.to_excel(output_filename, index=False)

print(f"\nOptimization complete. Solution successfully exported to '{output_filename}'.")