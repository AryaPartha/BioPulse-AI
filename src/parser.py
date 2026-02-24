import re
from utils import logger  # Ensure src/utils.py exists with the logger config

def parse_gym_log(log_text):
    """
    Parses natural language gym logs into structured data.
    Handles formats like: '80kg 3x10', '60 kilos for 5 sets of 5', etc.
    """
    try:
        # 1. Flexible Regex for Weight (handles kg, kilos, kgs, kilograms)
        weight_match = re.search(r'(\d+)\s*(?:kg|kilos|kgs|kilograms)', log_text, re.IGNORECASE)
        
        # 2. Flexible Regex for Sets and Reps keywords
        sets_match = re.search(r'(\d+)\s*(?:sets|set)', log_text, re.IGNORECASE)
        reps_match = re.search(r'(\d+)\s*(?:reps|rep|repetitions)', log_text, re.IGNORECASE)

        # 3. Fallback for Multiplier Format (e.g., '3x10' or '3 x 10')
        multiplier_match = re.search(r'(\d+)\s*[xX*]\s*(\d+)', log_text)

        weight = int(weight_match.group(1)) if weight_match else 0
        sets = 0
        reps = 0

        # Logic to determine sets/reps based on available matches
        if sets_match and reps_match:
            sets = int(sets_match.group(1))
            reps = int(reps_match.group(1))
        elif multiplier_match:
            sets = int(multiplier_match.group(1))
            reps = int(multiplier_match.group(2))

        # 4. Validation Check
        # If we couldn't find weight OR sets/reps, it's a failed parse
        if weight == 0 or sets == 0 or reps == 0:
            logger.warning(f"⚠️ Failed to parse meaningful data from: '{log_text}'")
            return None

        data = {
            "weight": weight,
            "sets": sets,
            "reps": reps,
            "total_volume": weight * sets * reps
        }
        
        logger.info(f"✅ Successfully parsed: '{log_text}' -> {data}")
        return data

    except Exception as e:
        logger.error(f"❌ Critical Error parsing log '{log_text}': {e}")
        return None

if __name__ == "__main__":
    # Test cases to verify the logic
    test_cases = [
        "80kg 3x10",
        "Squats 60kilos 3x12",
        "Bench 100 kgs for 5 sets of 5 repetitions",
        "I feel tired today" # Should return None and log a warning
    ]
    
    print("--- Running Parser Tests ---")
    for tc in test_cases:
        result = parse_gym_log(tc)
        print(f"Input: {tc} \nOutput: {result}\n")