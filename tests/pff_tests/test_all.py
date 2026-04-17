import os
import sys
from pathlib import Path
from cocotb_tools.runner import get_runner

def test_pff(num_taps=21, in_width=16, coeff_width=16, out_width=35):
    """Helper to initialize the runner and build the project"""
    sim = os.getenv("SIM", "ghdl")
    proj_path = Path(__file__).resolve().parent.parent.parent

    sources = [proj_path / "hardware-src" / "hdl" / "parallel_fir_filter.vhd"]

    runner = get_runner(sim)
    runner.build(
        sources=sources,
        hdl_toplevel="parallel_fir_filter",
        parameters={
            "G_NUM_TAPS": num_taps, 
            "G_IN_WIDTH": in_width, 
            "G_COEFF_WIDTH": coeff_width, 
            "G_OUT_WIDTH": out_width
        },
        build_dir=str(proj_path / "sim_build") # Keeps build files organized
    )

    if not os.path.exists(proj_path / "xml-reports"):
        os.makedirs(proj_path / "xml-reports")
    
    if not os.path.exists(proj_path / "png-results"):
        os.makedirs(proj_path / "png-results")

    runner.test(hdl_toplevel="parallel_fir_filter", 
                test_module="test_impulse", results_xml=proj_path / "xml-reports" / "impulse_results.xml")
    
    runner.test(hdl_toplevel="parallel_fir_filter", 
                test_module="test_square", results_xml=proj_path / "xml-reports" / "square_results.xml")
    
    runner.test(hdl_toplevel="parallel_fir_filter", 
                test_module="test_step", results_xml=proj_path / "xml-reports" / "step_results.xml")
    
    runner.test(hdl_toplevel="parallel_fir_filter", 
                test_module="test_sweep", results_xml=proj_path / "xml-reports" / "sweep_results.xml")

def test_conf_0():
    """Test configuration 0: 21 taps, 16-bit input, 16-bit coefficients, 35-bit output."""
    test_pff(num_taps=21, in_width=16, coeff_width=16, out_width=35)

def test_conf_1():
    """Test configuration 1: 21 taps, 16-bit input, 16-bit coefficients, 32-bit output."""
    test_pff(num_taps=21, in_width=16, coeff_width=16, out_width=32)

if __name__ == "__main__":
    test_conf_0()
    test_conf_1()