import math
import logging
from qiskit import QuantumCircuit, transpile

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def generate_quantum_bits_local(num_bits, num_qubits=8):
    """
    Generates a random bitstring of length `num_bits` using the local Qiskit Aer simulator.
    Uses H gates on all qubits to create superposition and measurements to produce randomness.
    """
    if num_bits <= 0:
        return ""
    
    from qiskit_aer import AerSimulator
    
    # Calculate number of shots needed
    shots = math.ceil(num_bits / num_qubits)
    logger.info(f"Generating {num_bits} bits locally using {num_qubits} qubits and {shots} shots.")
    
    # Create the QRNG circuit
    qc = QuantumCircuit(num_qubits)
    qc.h(range(num_qubits))
    qc.measure_all()
    
    # Run the circuit on the local Aer Simulator
    simulator = AerSimulator()
    qc_transpiled = transpile(qc, simulator)
    
    # Run with memory=True to retrieve the chronological sequence of measurements
    job = simulator.run(qc_transpiled, shots=shots, memory=True)
    result = job.result()
    memory = result.get_memory() # List of bitstrings, e.g. ['10110011', '01011010', ...]
    
    # Concatenate the shots and truncate to the requested bit length
    full_bitstring = "".join(memory)
    return full_bitstring[:num_bits]

def get_ibm_backends(api_token):
    """
    Connects to IBM Quantum and returns a list of available active backends.
    """
    from qiskit_ibm_runtime import QiskitRuntimeService
    
    try:
        try:
            service = QiskitRuntimeService(channel="ibm_quantum_platform", token=api_token)
        except Exception as e:
            logger.info(f"Failed to connect to ibm_quantum_platform, trying ibm_cloud: {e}")
            service = QiskitRuntimeService(channel="ibm_cloud", token=api_token)
        backends = service.backends()
        backend_info = []
        for b in backends:
            status = b.status()
            backend_info.append({
                "name": b.name,
                "qubits": b.num_qubits,
                "operational": status.operational,
                "pending_jobs": status.pending_jobs,
                "simulator": b.simulator
            })
        return backend_info
    except Exception as e:
        logger.error(f"Error fetching IBM backends: {str(e)}")
        raise e

def generate_quantum_bits_ibm(num_bits, api_token, backend_name=None, num_qubits=8, job_callback=None):
    """
    Generates a random bitstring of length `num_bits` using real IBM Quantum hardware.
    Uses Hadamard gates to create superposition and SamplerV2 to run the circuit.
    
    job_callback: optional callable to report the job status or ID.
    """
    if num_bits <= 0:
        return ""
    
    from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2
    
    logger.info("Initializing connection to IBM Quantum Service...")
    try:
        service = QiskitRuntimeService(channel="ibm_quantum_platform", token=api_token)
    except Exception as e:
        logger.info(f"Failed to connect to ibm_quantum_platform, trying ibm_cloud: {e}")
        service = QiskitRuntimeService(channel="ibm_cloud", token=api_token)
    
    if backend_name:
        logger.info(f"Using specified backend: {backend_name}")
        backend = service.backend(backend_name)
    else:
        logger.info("Selecting the least busy operational real backend...")
        backend = service.least_busy(simulator=False, operational=True)
        logger.info(f"Selected least busy backend: {backend.name}")
    
    # Adapt number of qubits to backend capacity if necessary
    actual_qubits = min(num_qubits, backend.num_qubits)
    shots = math.ceil(num_bits / actual_qubits)
    
    logger.info(f"Creating QRNG circuit on {actual_qubits} qubits, requiring {shots} shots.")
    
    # Create the QRNG circuit
    qc = QuantumCircuit(actual_qubits)
    qc.h(range(actual_qubits))
    qc.measure_all()
    
    # Transpile the circuit for the IBM backend
    qc_transpiled = transpile(qc, backend)
    
    # Run using the SamplerV2 primitive
    sampler = SamplerV2(backend)
    
    logger.info("Submitting job to IBM Quantum cloud...")
    job = sampler.run([qc_transpiled], shots=shots)
    job_id = job.job_id()
    logger.info(f"Job submitted successfully. Job ID: {job_id}")
    
    # Poll job status to update the UI
    import time
    while not job.in_final_state():
        status = job.status()
        logger.info(f"Job {job_id} status: {status}")
        if job_callback:
            job_callback(status, job_id)
        time.sleep(4)  # check status every 4 seconds
        
    final_status = job.status()
    logger.info(f"Job finished with status: {final_status}")
    if job_callback:
        job_callback(final_status, job_id)
        
    if final_status == "ERROR":
        raise RuntimeError(f"IBM Quantum Job failed. Error: {job.error_message()}")
    elif final_status == "CANCELLED":
        raise RuntimeError("IBM Quantum Job was cancelled.")
    
    # Retrieve final results
    result = job.result()
    logger.info("Retrieving results from completed job...")
    
    # Extract bitstrings from PubResult
    pub_result = result[0]
    data_keys = list(pub_result.data.keys())
    if not data_keys:
        raise ValueError("No measurement register found in the IBM job results.")
    
    # Get the raw list of shot outcomes
    bit_array = pub_result.data[data_keys[0]]
    memory = bit_array.get_bitstrings()
    
    # Concatenate and truncate
    full_bitstring = "".join(memory)
    return full_bitstring[:num_bits]
