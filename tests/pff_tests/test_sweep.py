import cocotb
from cocotb.triggers import Timer
from model import FIRFilter
from parrallel_fir_filter import ParallelFIRFilter
from scipy.signal import chirp
import numpy as np
from pathlib import Path

@cocotb.test()
async def sweep_test(dut):
    """Test the frequency sweep response of the FIR filter."""
    # Initialize the model and DUT interfaces
    clk_period_ns = 4 # 250 MHz clock
    pd_ns = 1 # 1 ns propagation delay

    taps = np.array([-1, -350, -1041, -1911, -2033, 0, 5227, 13397, 22620, 29963, 32767, 29963, 22620, 13397, 5227, 0, -2033, -1911, -1041, -350, -1], dtype=np.int16)

    model = FIRFilter(taps=taps)
    dut_interface = ParallelFIRFilter(dut, clk_period_ns, pd_ns, simulation_time_ns=2000000)

    cocotb.start_soon(dut_interface.generate_clock())  # Start the clock in the background
    await dut_interface.reset_dut(active_high=False, duration_ns=80)  # Reset the DUT

    cocotb.log.info("Calculating expected square response from the model...")

    # Apply square input
    # Parameters
    fs = 250000000      # Sampling frequency (250MHz)
    duration = 0.000100 # 10 microsecond
    t = np.linspace(0, duration, int(fs * duration))

    # Generate a frequency sweep from 500KHz to 50MHz
    # 'linear', 'quadratic', or 'logarithmic' methods are available
    sweep_sine = chirp(t, f0=500000, f1=50000000, t1=duration, method='linear')

    amplitude = 2**(int(dut.G_IN_WIDTH.value)-1)-1
    
    sweep_sine = (sweep_sine * amplitude).astype(np.int16)

    # Add zeros at the end to allow the filter to fully respond to the square wave input
    input_signal = np.concatenate([sweep_sine, np.zeros(len(model.taps) + 5)])

    expected_output = model.filter(input_signal)  # Get expected square response from the model

    cocotb.log.info("Applying sweep input to the DUT...")

    cocotb.start_soon(dut_interface.filter(input_signal))  # Apply sweep input to the DUT

    await dut_interface.check_output(expected_output, plot=True, title="Sweep Response Test", path= Path(__file__).resolve().parent.parent.parent / "png-results" / "sweep_response.png")  # Check DUT output against expected square response