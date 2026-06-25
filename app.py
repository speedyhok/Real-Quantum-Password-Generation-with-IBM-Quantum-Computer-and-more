import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import qrng
import password_generator as pg
import randomness_tests as rt
import time

# Set page config
st.set_page_config(
    page_title="Quantum Random Password Generator",
    page_icon="🔑",
    layout="wide",
    initial_sidebar_state="collapsed" # Hide sidebar by default for a clean look
)

# Apply premium dark mode & glassmorphism CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700&family=Space+Grotesk:wght@400;500;600;700;800&family=Fira+Code:wght@400;500&display=swap');
    
    [data-testid="stAppViewContainer"] {
        background: radial-gradient(circle at 80% 10%, rgba(30, 10, 60, 0.8) 0%, rgba(10, 11, 16, 0.99) 70%) !important;
        color: #e2e8f0 !important;
    }
    
    [data-testid="stHeader"] {
        background-color: rgba(0,0,0,0) !important;
    }
    
    h1, h2, h3, .main-title, .section-header {
        font-family: 'Space Grotesk', sans-serif;
        color: #ffffff;
    }
    
    p, span, div, li, label, .stMarkdown {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }
    
    .main-title-container {
        padding: 1.5rem 0 1rem 0;
        margin-bottom: 1.5rem;
        border-bottom: 1px solid rgba(255, 255, 255, 0.05);
    }
    
    .main-title {
        font-size: 2.5rem;
        background: linear-gradient(135deg, #00E5FF 0%, #8A2BE2 50%, #FF2E93 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
        letter-spacing: -1px;
    }
    
    .glass-card {
        background: rgba(255, 255, 255, 0.02) !important;
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border: 1px solid rgba(255, 255, 255, 0.06) !important;
        border-radius: 16px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 10px 40px 0 rgba(0, 0, 0, 0.4);
    }
    
    .metric-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        background: rgba(255, 255, 255, 0.01);
        border: 1px solid rgba(255, 255, 255, 0.04);
        border-radius: 12px;
        padding: 14px;
        text-align: center;
    }
    
    .metric-label {
        font-size: 0.75rem;
        color: #94a3b8;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 6px;
    }
    
    .metric-val {
        font-size: 1.5rem;
        font-weight: 700;
        color: #00E5FF;
        font-family: 'Space Grotesk', sans-serif;
    }
    
    /* Table styling */
    table {
        background-color: rgba(255, 255, 255, 0.01) !important;
        border-collapse: collapse !important;
        border-radius: 12px !important;
        overflow: hidden !important;
        border: 1px solid rgba(255, 255, 255, 0.05) !important;
        width: 100% !important;
        margin-top: 10px;
    }
    
    th {
        background-color: rgba(138, 43, 226, 0.08) !important;
        color: #ffffff !important;
        font-weight: 600 !important;
        padding: 10px 12px !important;
        text-align: left !important;
        border-bottom: 1px solid rgba(255, 255, 255, 0.08) !important;
        font-family: 'Space Grotesk', sans-serif;
        font-size: 0.9rem;
    }
    
    td {
        padding: 10px 12px !important;
        border-bottom: 1px solid rgba(255, 255, 255, 0.04) !important;
        color: #cbd5e1 !important;
        font-size: 0.85rem;
    }
    
    /* Badges */
    .badge-pass {
        color: #10b981 !important;
        font-weight: 600 !important;
    }
    
    .badge-fail {
        color: #ef4444 !important;
        font-weight: 600 !important;
    }
    
    /* Buttons styling */
    div.stButton > button {
        background: linear-gradient(135deg, #8A2BE2 0%, #4A00E0 50%, #00E5FF 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 10px 24px !important;
        font-weight: 600 !important;
        font-family: 'Space Grotesk', sans-serif !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 15px rgba(138, 43, 226, 0.2) !important;
        width: 100%;
    }
    
    div.stButton > button:hover {
        transform: translateY(-1px) !important;
        box-shadow: 0 6px 20px rgba(138, 43, 226, 0.35) !important;
    }
    
    /* Inputs */
    .stTextInput input, .stSelectbox [data-baseweb="select"] {
        background-color: rgba(255, 255, 255, 0.03) !important;
        color: #ffffff !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 8px !important;
        padding: 8px 12px !important;
    }
    
    .stTabs [data-baseweb="tab-list"] {
        border-bottom: 1px solid rgba(255, 255, 255, 0.05) !important;
        margin-bottom: 20px !important;
    }
    
    .stTabs [data-baseweb="tab"] {
        padding: 10px 20px !important;
        color: #94a3b8 !important;
        font-family: 'Space Grotesk', sans-serif !important;
        font-size: 1rem !important;
    }
    
    .stTabs [aria-selected="true"] {
        color: #00E5FF !important;
    }
</style>
""", unsafe_allow_html=True)

# Minimal Header
st.markdown("""
<div class="main-title-container">
    <div class="main-title">🔑 Quantum Random Password Generator</div>
    <p style="color: #94a3b8; font-size: 1.05rem; margin-top: 8px; margin-bottom: 0; line-height: 1.6; font-family: 'Plus Jakarta Sans', sans-serif; max-width: 800px;">
        Harness the fundamental laws of quantum mechanics to generate secure passwords. This application executes Hadamard superposition circuits on superconducting IBM Quantum hardware and local simulators, evaluating their physical randomness quality in real-time.
    </p>
</div>
""", unsafe_allow_html=True)

# Matplotlib configuration for transparent dark-mode
plt.rcParams['figure.facecolor'] = 'none'
plt.rcParams['axes.facecolor'] = 'none'
plt.rcParams['text.color'] = '#e2e8f0'
plt.rcParams['axes.labelcolor'] = '#cbd5e1'
plt.rcParams['xtick.color'] = '#94a3b8'
plt.rcParams['ytick.color'] = '#94a3b8'
plt.rcParams['grid.color'] = '#2a2b36'

def plot_randomness_metrics(results_dict):
    labels = list(results_dict.keys())
    entropy_vals = [results_dict[lbl]["entropy"] for lbl in labels]
    
    fig, ax = plt.subplots(1, 2, figsize=(12, 4.5))
    colors = ['#FF2E93', '#00E5FF', '#8A2BE2', '#FACC15']
    
    # Entropy Bar Chart
    bars = ax[0].bar(labels, entropy_vals, color=colors[:len(labels)], width=0.4, edgecolor='none')
    ax[0].set_title("Shannon Entropy (Ideal: 1.0)", fontsize=11, fontweight='bold', color='#ffffff')
    ax[0].set_ylim(0.96, 1.0005)
    ax[0].grid(axis='y', linestyle='--', alpha=0.3)
    
    for bar in bars:
        height = bar.get_height()
        ax[0].annotate(f'{height:.5f}', xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 3), textcoords="offset points", ha='center', va='bottom', fontsize=8, color='#ffffff')
    
    # P-values Plot
    x = np.arange(len(labels))
    width = 0.25
    monobit_p = [results_dict[lbl]["nist_monobit"]["p_value"] for lbl in labels]
    runs_p = [results_dict[lbl]["nist_runs"]["p_value"] for lbl in labels]
    
    rects1 = ax[1].bar(x - width/2, monobit_p, width, label='NIST Monobit P-val', color='#8A2BE2')
    rects2 = ax[1].bar(x + width/2, runs_p, width, label='NIST Runs P-val', color='#00E5FF')
    
    ax[1].set_title("NIST P-values (Threshold: >= 0.01)", fontsize=11, fontweight='bold', color='#ffffff')
    ax[1].set_xticks(x)
    ax[1].set_xticklabels(labels)
    ax[1].set_ylim(0, 1.1)
    ax[1].axhline(y=0.01, color='#FF2E93', linestyle='--', linewidth=1.2, label='Limit (0.01)')
    ax[1].legend(loc='upper right', framealpha=0.05, fontsize=8)
    ax[1].grid(axis='y', linestyle='--', alpha=0.3)

    plt.tight_layout()
    return fig

def display_stats_comparison_table(results_dict):
    markdown_table = """
| Generator | Shannon Entropy | NIST Monobit P-val | NIST Runs P-val | Chi-Sq Pair P-val | Serial Corr |
| :--- | :--- | :--- | :--- | :--- | :--- |
"""
    for gen_name, metrics in results_dict.items():
        mono_status = "**🟢 PASS**" if metrics['nist_monobit']['passed'] else "**🔴 FAIL**"
        runs_status = "**🟢 PASS**" if metrics['nist_runs']['passed'] else "**🔴 FAIL**"
        pair_status = "**🟢 PASS**" if metrics['chi_square_pair']['passed'] else "**🔴 FAIL**"
        
        markdown_table += f"| **{gen_name}** | `{metrics['entropy']:.5f}` | `{metrics['nist_monobit']['p_value']:.4f}` {mono_status} | `{metrics['nist_runs']['p_value']:.4f}` {runs_status} | `{metrics['chi_square_pair']['p_value']:.4f}` {pair_status} | `{metrics['serial_correlation']:.4f}` |\n"
        
    st.markdown(markdown_table)

def display_password_card(password, strength_metrics):
    # Monospaced password card
    password_html = f"""
    <div class="glass-card" style="text-align: center; border-left: 4px solid #00E5FF; margin-top: 10px;">
        <div style="font-family: 'Fira Code', monospace; font-size: 2rem; font-weight: 700; color: #ffffff; letter-spacing: 1px; word-break: break-all; margin: 10px 0;">
            {password}
        </div>
    </div>
    """
    st.markdown(password_html, unsafe_allow_html=True)
    st.code(password, language="text")
    
    score = strength_metrics["score"]
    score_colors = ["#EF4444", "#F97316", "#FACC15", "#4ADE80", "#00E5FF"]
    score_labels = ["Very Weak", "Weak", "Fair", "Strong", "Excellent"]
    color = score_colors[score]
    label = score_labels[score]
    pct = (score + 1) * 20
    
    # Custom compact strength bar
    strength_bar_html = f"""
    <div style="margin-top: 5px; margin-bottom: 15px;">
        <div style="display: flex; justify-content: space-between; font-size: 0.8rem; color: #94a3b8; margin-bottom: 6px;">
            <span>Password Strength</span>
            <span style="color: {color}; font-weight: bold;">{label}</span>
        </div>
        <div style="height: 6px; width: 100%; background-color: rgba(255, 255, 255, 0.05); border-radius: 3px; overflow: hidden;">
            <div style="height: 100%; width: {pct}%; background: linear-gradient(90deg, {color} 0%, #7E22CE 100%); border-radius: 3px;"></div>
        </div>
    </div>
    """
    st.markdown(strength_bar_html, unsafe_allow_html=True)
    
    # Grid of basic metrics
    metrics_html = f"""
    <div style="display: flex; gap: 10px; margin-top: 10px; margin-bottom: 20px; flex-wrap: wrap;">
        <div class="metric-container" style="flex: 1; min-width: 100px;">
            <div class="metric-label">Score</div>
            <div class="metric-val" style="color: {color};">{score}/4</div>
        </div>
        <div class="metric-container" style="flex: 1; min-width: 100px;">
            <div class="metric-label">Theoretical Entropy</div>
            <div class="metric-val" style="color: #c084fc;">{strength_metrics['theoretical_entropy_bits']:.1f} bits</div>
        </div>
        <div class="metric-container" style="flex: 1; min-width: 120px;">
            <div class="metric-label">Crack Time (Fast Hashing)</div>
            <div class="metric-val" style="color: #60a5fa; font-size: 1.25rem;">{strength_metrics['crack_times']['offline_fast_hash']}</div>
        </div>
    </div>
    """
    st.markdown(metrics_html, unsafe_allow_html=True)

# Tabs definitions
tab1, tab2 = st.tabs(["🌐 IBM Quantum Cloud", "💻 Local Qiskit Simulator"])

# ----------------- TAB 1: IBM QUANTUM -----------------
with tab1:
    col_x, col_y = st.columns([1, 2])
    
    with col_x:
        st.markdown("#### Configuration")
        ibm_token = st.text_input("IBM API Token", type="password")
        
        if ibm_token:
            if 'backends_list' not in st.session_state:
                with st.spinner("Loading backends..."):
                    try:
                        st.session_state['backends_list'] = qrng.get_ibm_backends(ibm_token)
                    except Exception as e:
                        st.error(f"Error: {e}")
            
            if 'backends_list' in st.session_state and st.session_state['backends_list']:
                backends = st.session_state['backends_list']
                backend_options = [f"{b['name']} ({b['qubits']}Q)" for b in backends if b['operational'] and not b['simulator']]
                selected_backend = st.selectbox("Quantum Device", backend_options)
                selected_backend_name = selected_backend.split(" ")[0] if selected_backend else None
            else:
                selected_backend_name = None
        else:
            selected_backend_name = None
            st.info("Enter your IBM token to fetch available quantum devices.")
            
        ibm_length = st.slider("Password Length", 8, 64, 16, key="ibm_len")
        ibm_charsets = st.multiselect("Character Sets", ["lowercase", "uppercase", "digits", "symbols"], 
                                      default=["lowercase", "uppercase", "digits", "symbols"], key="ibm_char")
        ibm_bits_to_gen = st.slider("Bits to Generate", 512, 4096, 1024, step=512, key="ibm_bits")
        
        generate_btn = st.button("Generate Password", disabled=not ibm_token, key="ibm_gen_btn")

    with col_y:
        st.markdown("#### Generation Results")
        if generate_btn and ibm_token:
            job_status = st.empty()
            
            def update_job_status(status, job_id):
                job_status.info(f"Job ID: `{job_id}` | Status: **{status}**")
                
            with st.spinner("Running on IBM Quantum hardware..."):
                try:
                    q_bitstring = qrng.generate_quantum_bits_ibm(
                        num_bits=ibm_bits_to_gen,
                        api_token=ibm_token,
                        backend_name=selected_backend_name,
                        job_callback=update_job_status
                    )
                    job_status.empty()
                    
                    # Generate comparisons
                    prng_bitstring = pg.generate_classical_random_bits(ibm_bits_to_gen)
                    csprng_bitstring = pg.generate_classical_secrets_bits(ibm_bits_to_gen)
                    
                    q_pass = pg.bits_to_password(q_bitstring, ibm_length, ibm_charsets)
                    q_strength = pg.evaluate_password_strength(q_pass, ibm_charsets)
                    
                    # Display password & strength
                    display_password_card(q_pass, q_strength)
                    
                    # Display Stats
                    st.markdown("##### 📊 Randomness Analysis")
                    analysis_results = {
                        "Quantum (IBM)": rt.run_all_tests(q_bitstring),
                        "CSPRNG (Secrets)": rt.run_all_tests(csprng_bitstring),
                        "PRNG (Random)": rt.run_all_tests(prng_bitstring)
                    }
                    display_stats_comparison_table(analysis_results)
                    st.pyplot(plot_randomness_metrics(analysis_results))
                    
                except Exception as e:
                    st.error(f"Error: {e}")
        else:
            st.write("Configure settings on the left and click Generate.")

# ----------------- TAB 2: LOCAL SIMULATOR -----------------
with tab2:
    col_z, col_w = st.columns([1, 2])
    
    with col_z:
        st.markdown("#### Configuration")
        sim_length = st.slider("Password Length", 8, 64, 16, key="sim_len")
        sim_charsets = st.multiselect("Character Sets", ["lowercase", "uppercase", "digits", "symbols"], 
                                      default=["lowercase", "uppercase", "digits", "symbols"], key="sim_char")
        sim_bits_to_gen = st.slider("Bits to Generate", 512, 4096, 2048, step=512, key="sim_bits")
        
        sim_btn = st.button("Generate Password", key="sim_gen_btn")

    with col_w:
        st.markdown("#### Generation Results")
        if sim_btn:
            with st.spinner("Simulating..."):
                try:
                    q_bitstring = qrng.generate_quantum_bits_local(num_bits=sim_bits_to_gen)
                    prng_bitstring = pg.generate_classical_random_bits(sim_bits_to_gen)
                    csprng_bitstring = pg.generate_classical_secrets_bits(sim_bits_to_gen)
                    
                    q_pass = pg.bits_to_password(q_bitstring, sim_length, sim_charsets)
                    q_strength = pg.evaluate_password_strength(q_pass, sim_charsets)
                    
                    # Display results
                    display_password_card(q_pass, q_strength)
                    
                    # Display Stats
                    st.markdown("##### 📊 Randomness Analysis")
                    analysis_results = {
                        "Quantum (Sim)": rt.run_all_tests(q_bitstring),
                        "CSPRNG (Secrets)": rt.run_all_tests(csprng_bitstring),
                        "PRNG (Random)": rt.run_all_tests(prng_bitstring)
                    }
                    display_stats_comparison_table(analysis_results)
                    st.pyplot(plot_randomness_metrics(analysis_results))
                    
                except Exception as e:
                    st.error(f"Error: {e}")
        else:
            st.write("Configure settings on the left and click Generate.")

# ----------------- NOISE & PHYSICS DISCUSSION (EXPANDER) -----------------
st.markdown("---")
with st.expander("🔍 Quantum Noise vs. Ideal Simulation (Click to Expand)"):
    col_n1, col_n2 = st.columns(2)
    with col_n1:
        st.markdown("### The Spinning Coin Analogy")
        st.write(
            "Think of a quantum bit (qubit) like a coin on a table. When lying flat, it is either "
            "Heads (1) or Tails (0). But when you flick it and it spins, it is in **superposition**—effectively "
            "both 1 and 0 at the same time.\n\n"
            "Stopping the spin with your hand collapses the state, giving you a measurement of 1 or 0.\n\n"
            "* **The Local Simulator** is like spinning a coin in a perfect, windless vacuum with zero gravity. It produces "
            "mathematically flawless 50/50 randomness every single time.\n"
            "* **Real IBM Quantum Hardware** is like spinning that coin on a bumpy, vibrating table in a drafty room. Physical "
            "glitches interfere with the results, causing minor bias."
        )
    with col_n2:
        st.markdown("### The 3 Real-World Quantum Glitches")
        st.write(
            "1. **Decoherence (The Tired Qubit)**: A spinning coin eventually loses speed and falls over. Real qubits "
            "get 'tired' quickly due to temperature fluctuations, dropping out of their spin and collapsing back to the ground state (0). "
            "This creates an excess of zeros in the raw bitstream.\n"
            "2. **Gate Errors (The Lazy Flick)**: To spin a coin, you must flick it. If your finger slips, the spin is wobbly. "
            "In hardware, we use microwave pulses to rotate qubits. Slight inaccuracies in these pulses cause wobbly superposition.\n"
            "3. **Readout Errors (The Dark Room)**: If you read the coin in a dark room with a blurry camera, you might misread a "
            "Heads as Tails. Reading subatomic quantum states is highly sensitive, and measurement readings sometimes misinterpret 1s as 0s."
        )
        st.markdown(
            "**Takeaway**: Because real hardware is noisy, physical quantum random numbers are run through a classical program "
            "called a **Randomness Extractor** to 'clean' the stream and guarantee perfect cryptographic security."
        )

# ----------------- FOOTER -----------------
st.markdown("""
<div style="text-align: center; margin-top: 50px; padding: 20px 0; border-top: 1px solid rgba(255, 255, 255, 0.05); font-family: 'Plus Jakarta Sans', sans-serif;">
    <p style="margin: 0; color: #94a3b8; font-size: 0.85rem;">
        © 2026 <b>Mohibul Hoque</b>. All rights reserved. Licensed under the MIT License.
    </p>
    <p style="margin: 8px 0 0 0; font-size: 0.85rem;">
        <a href="mailto:Hokworks@gmail.com" style="color: #00E5FF; text-decoration: none; margin-right: 15px; font-weight: 500; transition: color 0.3s;" onmouseover="this.style.color='#fff'" onmouseout="this.style.color='#00E5FF'">📧 Hokworks@gmail.com</a>
        <a href="https://www.linkedin.com/in/speedymohibul" target="_blank" style="color: #8A2BE2; text-decoration: none; font-weight: 500; transition: color 0.3s;" onmouseover="this.style.color='#fff'" onmouseout="this.style.color='#8A2BE2'">🔗 linkedin.com/in/speedymohibul</a>
    </p>
</div>
""", unsafe_allow_html=True)

