from flask import Flask, jsonify, request
import random
import copy

app = Flask(__name__)

# Define your data
subjects = [
    "Deep Learning", 
    "Big Data Analytics", 
    "Neural Network and Fuzzy System", 
    "Blockchain", 
    "CyberSecurity"
]
labs = [
    "Neural Network and Fuzzy System Lab", 
    "Deep Learning Lab", 
    "Big Data Analytics Lab", 
    "Blockchain Lab"
]
project_slot = "Major Project"
days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]

# Updated time slots to start at 9:15 and end at 5:15
time_slots = [
    "9:15-10:15", 
    "10:15-11:15", 
    "11:15-11:30 (Break)",
    "11:30-12:30", 
    "12:30-1:30", 
    "1:30-2:15 (Break)",
    "2:15-3:15", 
    "3:15-4:15", 
    "4:15-5:15"
]

# Define a timetable structure (empty initially)
def create_empty_timetable():
    return {day: [""] * len(time_slots) for day in days}

# Fitness function to evaluate a timetable
def fitness(timetable):
    score = 0
    # Check that breaks are respected
    for day in days:
        if timetable[day][2] != "Break" or timetable[day][5] != "Break":
            return 0  # Timetable doesn't respect break times
        
    # Check that there are no duplicate subjects in a day
    for day in days:
        subjects_scheduled = set()
        for slot in timetable[day]:
            if slot != "Break" and slot != "":
                if slot in subjects_scheduled:
                    return 0
                subjects_scheduled.add(slot)
        
    # Check that "Major Project" appears exactly 3 times per week
    major_project_count = sum([timetable[day].count(project_slot) for day in days])
    if major_project_count != 3:
        return 0
    
    # Check that every subject and lab appears at least once
    all_subjects = subjects + labs
    for item in all_subjects:
        if not any(item in timetable[day] for day in days):
            return 0
    
    # Each valid timetable gains a positive score
    score += 1
    return score

# Generate a random timetable
def generate_random_timetable():
    timetable = create_empty_timetable()

    # Copy of classes to assign
    all_classes = copy.deepcopy(subjects)
    
    # Define the labs that take 2 hours (spanning two consecutive slots)
    lab_sessions = {
        "Neural Network and Fuzzy System Lab": False,
        "Deep Learning Lab": False,
        "Big Data Analytics Lab": False,
        "Blockchain Lab": False
    }

    # Assign "Major Project" 3 times per week
    project_assigned = 0
    while project_assigned < 3:
        day = random.choice(days)
        slot = random.choice([i for i in range(len(time_slots)) if time_slots[i] not in ["11:15-11:30 (Break)", "1:30-2:15 (Break)"] and timetable[day][i] == ""])
        timetable[day][slot] = project_slot
        project_assigned += 1

    # Assign labs (each lab is 2 hours, spans 2 consecutive slots, once per week)
    for lab in lab_sessions:
        lab_assigned = False
        while not lab_assigned:
            day = random.choice(days)
            slot = random.choice([i for i in range(len(time_slots) - 1) if time_slots[i] not in ["11:15-11:30 (Break)", "1:30-2:15 (Break)"] and timetable[day][i] == "" and timetable[day][i + 1] == ""])
            
            # Assign the lab to two consecutive slots
            timetable[day][slot] = lab
            timetable[day][slot + 1] = lab
            lab_assigned = True
    
    # Assign other subjects
    for day in days:
        for i in range(len(time_slots)):
            if time_slots[i] in ["11:15-11:30 (Break)", "1:30-2:15 (Break)"]:
                timetable[day][i] = "Break"
            elif timetable[day][i] == "":
                if all_classes:
                    chosen_class = random.choice(all_classes)
                    timetable[day][i] = chosen_class
                    all_classes.remove(chosen_class)
                else:
                    timetable[day][i] = ""  # Leave empty if no classes left
    
    return timetable

# Crossover between two timetables
def crossover(timetable1, timetable2):
    new_timetable = copy.deepcopy(timetable1)
    crossover_day = random.choice(days)
    new_timetable[crossover_day] = copy.deepcopy(timetable2[crossover_day])
    return new_timetable

# Mutation to introduce variability
def mutate(timetable):
    day_to_mutate = random.choice(days)
    time_slot_to_mutate = random.choice(range(len(time_slots)))
    
    if time_slots[time_slot_to_mutate] not in ["11:15-11:30 (Break)", "1:30-2:15 (Break)"]:
        possible_classes = subjects + labs + [project_slot]
        timetable[day_to_mutate][time_slot_to_mutate] = random.choice(possible_classes)
    
    return timetable

# Main genetic algorithm function
def run_genetic_algorithm(data, population_size=20, generations=500):
    # Create initial population
    population = [generate_random_timetable() for _ in range(population_size)]
    
    for generation in range(generations):
        # Sort population based on fitness
        population = sorted(population, key=lambda x: fitness(x), reverse=True)
        
        # Check if the best timetable is valid
        if fitness(population[0]) == 1:
            print(f"Optimal timetable found at generation {generation}")
            return population[0]  # Found an optimal solution
        
        # Selection (top 50% will survive)
        survivors = population[:population_size // 2]
        
        # Crossover and mutation to create new offspring
        new_population = []
        while len(new_population) < population_size:
            parent1 = random.choice(survivors)
            parent2 = random.choice(survivors)
            
            child = crossover(parent1, parent2)
            if random.random() < 0.1:  # 10% mutation rate
                child = mutate(child)
            
            new_population.append(child)
        
        population = new_population
    
    # After all generations, return the best timetable found
    best_timetable = sorted(population, key=lambda x: fitness(x), reverse=True)[0]
    print("No optimal timetable found. Returning the best timetable found.")
    return best_timetable

# Flask route to generate the timetable
@app.route('/generate_timetable', methods=['GET', 'POST'])
def generate_timetable():
    if request.method == 'GET':
        return jsonify({"message": "This is a POST-only endpoint. Please send a POST request with data."}), 405

    # For POST requests
    data = request.get_json()
    
    if data is None:
        return jsonify({"error": "No data provided"}), 400
    
    # Pass the data to your genetic algorithm function
    timetable = run_genetic_algorithm(data)
    
    # Format the timetable to include time slots
    formatted_timetable = {}
    
    for day in days:
        formatted_day = []
        for i in range(len(time_slots)):
            formatted_day.append({
                "time_slot": time_slots[i],
                "subject": timetable[day][i]
            })
        formatted_timetable[day] = formatted_day
    
    # Return the generated timetable in a structured format
    return jsonify(formatted_timetable), 200

# Run the Flask app
if __name__ == "__main__":
    app.run(debug=True)
