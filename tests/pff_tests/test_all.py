import os
import sys
from pathlib import Path
from cocotb_tools.runner import get_runner

def test_conf_0():
    """Helper to initialize the runner and build the project"""
    sim = os.getenv("SIM", "ghdl")
    proj_path = Path(__file__).resolve().parent.parent.parent

    sources = [proj_path / "hardware-src" / "hdl" / "parallel_fir_filter.vhd"]

    runner = get_runner(sim)
    runner.build(
        sources=sources,
        hdl_toplevel="parallel_fir_filter",
        parameters={
            "G_NUM_TAPS": 21, 
            "G_IN_WIDTH": 16, 
            "G_COEFF_WIDTH": 16, 
            "G_OUT_WIDTH": 35
        },
        build_dir=str(proj_path / "sim_build") # Keeps build files organized
    )
    runner.test(hdl_toplevel="parallel_fir_filter", 
                test_module="test_impulse", results_xml=proj_path / "xml-reports" / "impulse_results.xml")
    
    runner.test(hdl_toplevel="parallel_fir_filter", 
                test_module="test_square", results_xml=proj_path / "xml-reports" / "square_results.xml")
    
    runner.test(hdl_toplevel="parallel_fir_filter", 
                test_module="test_step", results_xml=proj_path / "xml-reports" / "step_results.xml")
    
    runner.test(hdl_toplevel="parallel_fir_filter", 
                test_module="test_sweep", results_xml=proj_path / "xml-reports" / "sweep_results.xml")

if __name__ == "__main__":
    test_conf_0()
