import cocotb
import matplotlib.pyplot as plt
from cocotb.triggers import RisingEdge, FallingEdge, Timer

class ParallelFIRFilter:
    """A simple FIR filter model for testing purposes."""
    def __init__(self, dut, clk_period_ns, pd_ns, simulation_time_ns=1000000):
        self.clk_period_ns = clk_period_ns
        self.pd_ns = pd_ns
        self.dut = dut
        self.simulation_time_ns = simulation_time_ns
    
    async def generate_clock(self):
        """"Generate clock signal."""

        while self.simulation_time_ns > 0:
            self.dut.clk.value = 0
            await Timer(self.clk_period_ns // 2, unit="ns")
            self.dut.clk.value = 1
            await Timer(self.clk_period_ns // 2, unit="ns")
            self.simulation_time_ns -= self.clk_period_ns

    async def reset_dut(self, active_high=True, duration_ns=100):
        """Reset the DUT."""
        self.dut.rst_n.value = 1 if active_high else 0
        await Timer(duration_ns, unit="ns")
        self.dut.rst_n.value = 0 if active_high else 1

    async def filter(self, input_signal):
        """Apply the input signal to the DUT and capture the output."""
        for sample in input_signal:
            while self.dut.s_axis_tready.value == 0:  # wait until DUT is ready to accept input
                await Timer(self.clk_period_ns, unit="ns")
            await RisingEdge(self.dut.clk)
            self.dut.s_axis_tvalid.value = 1
            self.dut.s_axis_tdata.value = int(sample)
            await Timer(self.pd_ns, unit="ns")  # Wait for the signal to propagate
        
        # reset valid to 0
        await RisingEdge(self.dut.clk)
        self.dut.s_axis_tvalid.value = 0
    

    async def check_output(self, expected_output, tolerance=0, plot=False, title=None):
        """Check the DUT output against expected values."""

        await RisingEdge(self.dut.clk)
        self.dut.m_axis_tready.value = 1

        actual_output = []

        for expected in expected_output:
            while self.dut.m_axis_tvalid == 0:
                await Timer(self.clk_period_ns, unit="ns")
            
            await RisingEdge(self.dut.clk)
            actual = int(self.dut.m_axis_tdata.value.to_signed())
            actual_output.append(actual)
            cocotb.log.debug(f"Expected {expected}, got {actual}")

            await Timer(self.pd_ns, unit="ns")  # Wait before checking the next value
        
        await RisingEdge(self.dut.clk)
        self.dut.m_axis_tready.value = 0

        if plot:
            plt.figure(figsize=(14, 7), dpi=300)
            plt.plot(range(0,len(expected_output)), expected_output, color="#ff7300", linestyle='-', linewidth=2.5, alpha=0.6, label='Ideal SciPy Model')
            markerline, stemlines, _ = plt.stem(range(0,len(actual_output)), actual_output, 
                                        linefmt='C0-', 
                                        markerfmt='C0o', 
                                        basefmt='k-', 
                                        label='RTL Output')
            plt.setp(markerline, markersize=3)
            plt.setp(stemlines, linewidth=0.5)

            if title:
                plt.title(title)
            else:
                plt.title('FIR Filter Output Comparison')
            plt.xlabel('Sample Index')
            plt.ylabel('Output Value')
            plt.legend()
            plt.grid()

            plt.savefig("filter_comparison.png")
            plt.close()
        i = 0
        for expected, actual in zip(expected_output, actual_output):
            assert expected == actual, f"Expected {expected}, got {actual}, index {i}, Simulation Time: {self.simulation_time_ns} ns"
            i += 1
