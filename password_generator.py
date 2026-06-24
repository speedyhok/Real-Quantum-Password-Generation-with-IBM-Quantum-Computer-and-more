import math
import random
import secrets
import zxcvbn

# Define default character sets
CHARSETS = {
    "lowercase": "abcdefghijklmnopqrstuvwxyz",
    "uppercase": "ABCDEFGHIJKLMNOPQRSTUVWXYZ",
    "digits": "0123456789",
    "symbols": "!@#$%^&*()_+-=[]{}|;:,.<>?"
}

def bits_to_password(bitstring, length, selected_sets):
    """
    Converts a bitstring into a password of the specified length using rejection sampling
    to eliminate modulo bias.
    
    selected_sets: list of keys from CHARSETS (e.g., ["lowercase", "uppercase", "digits", "symbols"])
    """
    # Build combined alphabet
    alphabet = "".join([CHARSETS[s] for s in selected_sets if s in CHARSETS])
    if not alphabet:
        raise ValueError("At least one character set must be selected.")
        
    alphabet_size = len(alphabet)
    
    # Calculate the number of bits k needed per character: 2^k >= alphabet_size
    k = math.ceil(math.log2(alphabet_size))
    
    # Calculate the upper limit for rejection sampling to avoid modulo bias
    # limit is the largest multiple of alphabet_size that is <= 2^k
    limit = (1 << k) - ((1 << k) % alphabet_size)
    
    bit_iter = iter(bitstring)
    password = []
    
    try:
        while len(password) < length:
            # Consume k bits
            bits = []
            for _ in range(k):
                bits.append(next(bit_iter))
            
            val = int("".join(bits), 2)
            
            # Rejection sampling check
            if val < limit:
                char_idx = val % alphabet_size
                password.append(alphabet[char_idx])
            # If val >= limit, it is discarded, and we try the next k bits
    except StopIteration:
        raise ValueError(
            f"Ran out of random bits during rejection sampling. "
            f"Need more than {len(bitstring)} bits. Please increase the bit generation size."
        )
        
    return "".join(password)

def generate_classical_random_bits(num_bits):
    """
    Generates a random bitstring of length `num_bits` using Python's standard `random` module
    (Mersenne Twister PRNG).
    """
    bits = [str(random.choice([0, 1])) for _ in range(num_bits)]
    return "".join(bits)

def generate_classical_secrets_bits(num_bits):
    """
    Generates a random bitstring of length `num_bits` using Python's `secrets` module
    (Cryptographically secure PRNG).
    """
    # secrets.randbits(1) returns 0 or 1 cryptographically securely
    bits = [str(secrets.randbits(1)) for _ in range(num_bits)]
    return "".join(bits)

def evaluate_password_strength(password, selected_sets):
    """
    Evaluates password strength using the zxcvbn library and calculates theoretical entropy.
    """
    # Run zxcvbn analysis
    analysis = zxcvbn.zxcvbn(password)
    
    score = analysis["score"]  # 0 to 4
    crack_times = analysis["crack_times_display"]
    feedback = analysis["feedback"]
    
    # Calculate theoretical entropy: L * log2(A)
    # where L is password length, A is alphabet size
    alphabet = "".join([CHARSETS[s] for s in selected_sets if s in CHARSETS])
    alphabet_size = len(alphabet)
    
    length = len(password)
    if alphabet_size > 0:
        theoretical_entropy = length * math.log2(alphabet_size)
    else:
        theoretical_entropy = 0.0
        
    return {
        "score": score,
        "crack_times": {
            "online_throttled": crack_times["online_throttling_100_per_hour"],
            "online_unthrottled": crack_times["online_no_throttling_10_per_second"],
            "offline_slow_hash": crack_times["offline_slow_hashing_1e4_per_second"],
            "offline_fast_hash": crack_times["offline_fast_hashing_1e10_per_second"]
        },
        "warning": feedback.get("warning", ""),
        "suggestions": feedback.get("suggestions", []),
        "theoretical_entropy_bits": theoretical_entropy
    }
