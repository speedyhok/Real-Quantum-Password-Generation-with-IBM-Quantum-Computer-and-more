import os
import sys
import math
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# Add current directory to path
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

import qrng
import password_generator as pg
import randomness_tests as rt

def clear_screen():
    # Only clear screen if not running in a piped/non-interactive test environment
    if sys.stdin.isatty():
        os.system('cls' if os.name == 'nt' else 'clear')

def get_input(prompt, default, val_type=int):
    # If stdin has been closed or is not a tty, use default
    if not sys.stdin.isatty():
        return default
    user_input = input(f"{prompt} [default: {default}]: ").strip()
    if not user_input:
        return default
    try:
        return val_type(user_input)
    except ValueError:
        print(f"Invalid input. Using default: {default}")
        return default

def plot_and_save_metrics(results_dict, filename="randomness_comparison.png"):
    """
    Generates comparison plots and saves them locally as an image.
    """
    labels = list(results_dict.keys())
    entropy_vals = [results_dict[lbl]["entropy"] for lbl in labels]
    
    # Configure plotting parameters
    plt.rcParams['text.color'] = '#333333'
    plt.rcParams['axes.labelcolor'] = '#333333'
    plt.rcParams['xtick.color'] = '#333333'
    plt.rcParams['ytick.color'] = '#333333'
    plt.rcParams['grid.color'] = '#e2e8f0'
    plt.rcParams['font.family'] = 'sans-serif'
    
    fig, ax = plt.subplots(1, 2, figsize=(12, 5))
    colors = ['#FF2E93', '#00E5FF', '#8A2BE2', '#FACC15']
    
    # 1. Entropy Bar Chart
    bars = ax[0].bar(labels, entropy_vals, color=colors[:len(labels)], width=0.4, edgecolor='gray', alpha=0.85)
    ax[0].set_title("Shannon Entropy Comparison\n(Ideal: 1.0)", fontsize=11, fontweight='bold')
    ax[0].set_ylabel("Entropy (bits per bit)")
    ax[0].set_ylim(0.96, 1.0005)
    ax[0].grid(axis='y', linestyle='--')
    
    for bar in bars:
        height = bar.get_height()
        ax[0].annotate(f'{height:.5f}', xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 3), textcoords="offset points", ha='center', va='bottom', fontsize=8)
    
    # 2. P-values Bar Chart (NIST Tests)
    x = np.arange(len(labels))
    width = 0.25
    monobit_p = [results_dict[lbl]["nist_monobit"]["p_value"] for lbl in labels]
    runs_p = [results_dict[lbl]["nist_runs"]["p_value"] for lbl in labels]
    
    rects1 = ax[1].bar(x - width/2, monobit_p, width, label='NIST Monobit P-val', color='#8A2BE2', alpha=0.85)
    rects2 = ax[1].bar(x + width/2, runs_p, width, label='NIST Runs P-val', color='#00E5FF', alpha=0.85)
    
    ax[1].set_title("NIST P-values\n(Threshold: >= 0.01 is random)", fontsize=11, fontweight='bold')
    ax[1].set_xticks(x)
    ax[1].set_xticklabels(labels)
    ax[1].set_ylim(0, 1.1)
    ax[1].axhline(y=0.01, color='#FF2E93', linestyle='--', linewidth=1.2, label='Limit (0.01)')
    ax[1].legend(loc='upper right', framealpha=0.8, fontsize=8)
    ax[1].grid(axis='y', linestyle='--')
    
    plt.tight_layout()
    plt.savefig(filename, dpi=300)
    plt.close()
    print(f"\nVisual comparison chart saved successfully to: {os.path.abspath(filename)}")

def main():
    clear_screen()
    print("=====================================================================")
    print(" QUANTUM RANDOM PASSWORD GENERATOR & ANALYZER (CLI MODE) ")
    print("=====================================================================")
    print("This tool generates secure passwords using true quantum randomness and")
    print("evaluates the randomness quality against classical generators.")
    print("=====================================================================\n")
    
    print("Select Generator Backend:")
    print("1. Local Qiskit Aer Simulator (Local, fast, no internet/token needed)")
    print("2. IBM Quantum Real Hardware (Cloud, requires API token)")
    
    choice = get_input("Enter choice (1-2)", 1)
    
    # 1. Parameter configuration
    print("\n--- Configuration Settings ---")
    length = get_input("Password Length (8-64)", 16)
    bits_to_gen = get_input("Bits to Generate for Randomness Tests (512-4096)", 1024)
    
    # Check if we are running interactively to prompt for characters
    char_options = []
    if sys.stdin.isatty():
        print("\nCharacter sets to include (enter 'y' or 'n'):")
        if input("Include Lowercase letters? (y/n) [default: y]: ").strip().lower() != 'n':
            char_options.append("lowercase")
        if input("Include Uppercase letters? (y/n) [default: y]: ").strip().lower() != 'n':
            char_options.append("uppercase")
        if input("Include Digits? (y/n) [default: y]: ").strip().lower() != 'n':
            char_options.append("digits")
        if input("Include Symbols/Special? (y/n) [default: y]: ").strip().lower() != 'n':
            char_options.append("symbols")
    else:
        # Non-interactive mode (default to all)
        char_options = ["lowercase", "uppercase", "digits", "symbols"]
        
    if not char_options:
        char_options = ["lowercase", "uppercase", "digits", "symbols"]

    # 2. QRNG Execution
    q_bitstring = ""
    gen_label = "Quantum (Sim)"
    
    if choice == 2:
        ibm_token = input("\nEnter your IBM Quantum API Token: ").strip()
        if not ibm_token:
            print("Token empty. Falling back to Local Simulator.")
            choice = 1
        else:
            try:
                print("\nFetching available operational quantum devices...")
                backends = qrng.get_ibm_backends(ibm_token)
                active_backends = [b for b in backends if b['operational'] and not b['simulator']]
                
                print("\nAvailable Quantum Devices:")
                for idx, b in enumerate(active_backends):
                    print(f"{idx + 1}. {b['name']} ({b['qubits']} Qubits, Queue: {b['pending_jobs']} jobs)")
                
                backend_choice = get_input("\nSelect device index", 1)
                selected_backend = active_backends[backend_choice - 1]['name']
                gen_label = "Quantum (IBM)"
                
                print(f"\nSubmitting QRNG job to {selected_backend}...")
                
                def cli_status_callback(status, job_id):
                    print(f"  [Qiskit Job Status] ID: {job_id} | State: {status}")
                    
                q_bitstring = qrng.generate_quantum_bits_ibm(
                    num_bits=bits_to_gen,
                    api_token=ibm_token,
                    backend_name=selected_backend,
                    job_callback=cli_status_callback
                )
                print("Job finished and random bits retrieved successfully!")
            except Exception as e:
                print(f"\nIBM Quantum Error: {e}")
                print("Falling back to local Qiskit Aer simulator...")
                choice = 1

    if choice == 1:
        print("\nSimulating quantum superposition circuit locally...")
        q_bitstring = qrng.generate_quantum_bits_local(num_bits=bits_to_gen)
        print("Simulation complete. Quantum bits generated successfully!")
        
    # 3. Generate baseline classical random bits
    prng_bitstring = pg.generate_classical_random_bits(bits_to_gen)
    csprng_bitstring = pg.generate_classical_secrets_bits(bits_to_gen)
    
    # 4. Map bits to passwords (mitigating modulo bias)
    q_password = pg.bits_to_password(q_bitstring, length, char_options)
    
    # 5. Evaluate Password Strength
    strength = pg.evaluate_password_strength(q_password, char_options)
    
    # 6. Display Password & Strength
    print("\n" + "="*50)
    print(" GENERATED QUANTUM PASSWORD:")
    print("="*50)
    print(f"\n   >>>  {q_password}  <<<\n")
    print("="*50)
    print(" PASSWORD STRENGTH ANALYSIS (zxcvbn):")
    print("="*50)
    score_desc = ["Very Weak", "Weak", "Fair", "Strong", "Excellent"]
    print(f"Strength Score:      {score_desc[strength['score']]}")
    print(f"Theoretical Entropy: {strength['theoretical_entropy_bits']:.2f} bits")
    print(f"Crack Time (Offline Fast Hashing): {strength['crack_times']['offline_fast_hash']}")
    print(f"Crack Time (Online Throttled):     {strength['crack_times']['online_throttled']}")
    if strength['warning']:
        print(f"Security Warning:    {strength['warning']}")
    if strength['suggestions']:
        print("Suggestions:")
        for sug in strength['suggestions']:
            print(f"  - {sug}")
    print("="*50)
    
    # 7. Evaluate and Compare Randomness Quality
    print("\n RUNNING STATISTICAL RANDOMNESS ANALYSIS...")
    print("This evaluates the bitstreams against NIST standards and Chi-Square uniformity tests.\n")
    
    analysis_results = {
        gen_label: rt.run_all_tests(q_bitstring),
        "CSPRNG (Secrets)": rt.run_all_tests(csprng_bitstring),
        "PRNG (Random)": rt.run_all_tests(prng_bitstring)
    }
    
    # Construct comparative table
    data = []
    for gen_name, metrics in analysis_results.items():
        data.append({
            "Generator": gen_name,
            "Entropy": f"{metrics['entropy']:.5f}",
            "NIST Monobit P-val": f"{metrics['nist_monobit']['p_value']:.4f}",
            "Monobit Pass": "YES" if metrics['nist_monobit']['passed'] else "NO",
            "NIST Runs P-val": f"{metrics['nist_runs']['p_value']:.4f}",
            "Runs Pass": "YES" if metrics['nist_runs']['passed'] else "NO",
            "Chi-Sq Pair P-val": f"{metrics['chi_square_pair']['p_value']:.4f}",
            "Pair Pass": "YES" if metrics['chi_square_pair']['passed'] else "NO",
            "Serial Corr": f"{metrics['serial_correlation']:.4f}"
        })
        
    df = pd.DataFrame(data)
    print(df.to_string(index=False))
    print("\n*Note: P-values >= 0.01 indicate that the sequence passes that randomness test.")
    
    # Generate and save plot
    plot_and_save_metrics(analysis_results)
    
    # 8. Brief Noise Discussion
    print("\n" + "="*50)
    print(" PHYSICS CORNER: QUANTUM NOISE IN NISQ COMPUTERS")
    print("="*50)
    print("If you compared the Simulator against Real IBM Hardware, you might notice")
    print("slight variations in the statistical tests. Here is why:")
    print("1. Qiskit Aer Simulator runs on an idealized, noise-free closed system.")
    print("2. Real superconducting hardware is subject to environmental interactions:")
    print("   - Thermal Decoherence (qubits decay to |0> ground state over time).")
    print("   - Gate pulse calibration inaccuracies.")
    print("   - Readout errors during measurement collapse.")
    print("This creates physical bias (more 0s) and correlations in the raw bitstream.")
    print("In real-world cryptography, raw quantum bits must undergo Von Neumann debiasing")
    print("or hash-based randomness extraction to strip out hardware noise before use.")
    print("="*50 + "\n")

if __name__ == "__main__":
    main()
