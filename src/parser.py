import re

def parse_gym_log(log_text):
    # Regex to find: [Weight]kg, [Sets] sets, [Reps] reps
    weight_match = re.search(r'(\d+)\s*kg', log_text)
    sets_match = re.search(r'(\d+)\s*sets', log_text)
    reps_match = re.search(r'(\d+)\s*reps', log_text)

    data = {
        "weight": int(weight_match.group(1)) if weight_match else 0,
        "sets": int(sets_match.group(1)) if sets_match else 0,
        "reps": int(reps_match.group(1)) if reps_match else 0,
    }
    
    # Calculate Volume: weight * sets * reps
    data["total_volume"] = data["weight"] * data["sets"] * data["reps"]
    return data

if __name__ == "__main__":
    test_log = "I did 80kg bench press for 3 sets of 10 reps"
    print(f"Parsed Data: {parse_gym_log(test_log)}")