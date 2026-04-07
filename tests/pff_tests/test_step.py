import cocotb
from cocotb.triggers import Timer
from model import FIRFilter
from parrallel_fir_filter import ParallelFIRFilter
from scipy.signal import chirp
import numpy as np
from pathlib import Path

@cocotb.test()
async def step_test(dut):
    """Test the step response of the FIR filter."""
    # Initialize the model and DUT interfaces
    clk_period_ns = 4 # 250 MHz clock
    pd_ns = 1 # 1 ns propagation delay

    taps = np.array([-1, -350, -1041, -1911, -2033, 0, 5227, 13397, 22620, 29963, 32767, 29963, 22620, 13397, 5227, 0, -2033, -1911, -1041, -350, -1], dtype=np.int16)

    model = FIRFilter(taps=taps)
    dut_interface = ParallelFIRFilter(dut, clk_period_ns, pd_ns, simulation_time_ns=2000000)

    cocotb.start_soon(dut_interface.generate_clock())  # Start the clock in the background
    await dut_interface.reset_dut(active_high=False, duration_ns=80)  # Reset the DUT

    cocotb.log.info("Calculating expected step response from the model...")

    # Apply step input
    # Parameters
    input_signal = np.ones(100)      # Sampling frequency (250MHz)
    input_signal[0] = 0  # Step at the first sample
    
    expected_output = model.filter(input_signal)  # Get expected step response from the model

    cocotb.log.info("Applying step input to the DUT...")

    cocotb.start_soon(dut_interface.filter(input_signal))  # Apply step input to the DUT

    await dut_interface.check_output(expected_output, plot=True, title="Step Response Test", path= Path(__file__).resolve().parent.parent.parent / "png-results" / "step_response.png")  # Check DUT output against expected step response