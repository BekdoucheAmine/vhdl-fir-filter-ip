import cocotb
from cocotb.triggers import Timer
from model import FIRFilter
from parrallel_fir_filter import ParallelFIRFilter
import numpy as np

@cocotb.test()
async def impulse_response_test(dut):
    """Test the impulse response of the FIR filter."""
    # Initialize the model and DUT interfaces
    clk_period_ns = 4 # 250 MHz clock
    pd_ns = 1 # 1 ns propagation delay

    taps = np.array([-1, -350, -1041, -1911, -2033, 0, 5227, 13397, 22620, 29963, 32767, 29963, 22620, 13397, 5227, 0, -2033, -1911, -1041, -350, -1], dtype=np.int16)

    model = FIRFilter(taps=taps)
    dut_interface = ParallelFIRFilter(dut, clk_period_ns, pd_ns, simulation_time_ns=10000)

    cocotb.start_soon(dut_interface.generate_clock())  # Start the clock in the background
    await dut_interface.reset_dut(active_high=False, duration_ns=80)  # Reset the DUT

    cocotb.log.info("Calculating expected impulse response from the model...")

    # Apply impulse input
    impulse_input = np.zeros(100, dtype=np.int64)  # Longer input to capture full impulse response
    impulse_input[0] = 1  # Impulse at the first sample

    expected_output = model.filter(impulse_input)  # Get expected impulse response from the model
    
    cocotb.log.info("Applying impulse input to the DUT...")

    cocotb.start_soon(dut_interface.filter(impulse_input))  # Apply impulse input to the DUT

    await dut_interface.check_output(expected_output, plot=True, title="Impulse Response Test")  # Check DUT output against expected impulse response







    