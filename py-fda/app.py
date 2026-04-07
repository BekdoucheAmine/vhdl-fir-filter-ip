import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import firwin, freqz, lfilter

# --- 1. CORE LOGIC FUNCTIONS ---

def design_fir_filter(fs, filter_type, fc, numtaps, window_type):
    """Handles the mathematical design of the FIR filter."""
    # firwin requires specific pass_zero arguments for different types
    pass_zero_map = {
        "lowpass": True,
        "highpass": False,
        "bandpass": False,
        "bandstop": True
    }
    
    taps = firwin(
        numtaps, 
        fc, 
        window=window_type, 
        pass_zero=pass_zero_map.get(filter_type, True), 
        fs=fs
    )
    return taps

def quantize_coefficients(taps, bit_width):
    """Converts floating point taps to fixed-point integers."""
    max_val = np.max(np.abs(taps))
    scale_factor = 2**(bit_width - 1) - 1
    return np.floor(taps / max_val * scale_factor).astype(int)

def calculate_responses(taps, fs, numtaps):
    """Calculates frequency and step response data."""
    # Frequency Response
    w, h = freqz(taps, 1, worN=2000)
    freq_hz = 0.5 * fs * w / np.pi
    gain_db = 20 * np.log10(np.abs(h) + 1e-12)
    
    # Step Response
    step_input = np.ones(numtaps * 3)
    step_response = lfilter(taps, 1, step_input)
    
    return freq_hz, np.abs(h), gain_db, step_response

# --- 2. UI COMPONENTS ---

def render_sidebar():
    """Renders all input controls in the sidebar."""
    with st.sidebar:
        st.title("Filter Configuration")
        fs = st.number_input("Sampling Frequency (Hz)", value=100_000_000, step=1_000_000)
        filter_type = st.radio("Filter Type:", ["lowpass", "highpass", "bandpass", "bandstop"])
        
        st.divider()
        
        # Frequency Inputs (Handling single vs multiple frequencies)
        if filter_type in ["lowpass", "highpass"]:
            fc = st.number_input("Cutoff Frequency (Hz)", value=10_000_000)
        else:
            col1, col2 = st.columns(2)
            f1 = col1.number_input("F low (Hz)", value=10_000_000)
            f2 = col2.number_input("F high (Hz)", value=20_000_000)
            fc = [f1, f2]

        st.divider()
        
        numtaps = st.slider("Number of Taps", 3, 255, 21, step=2)
        window_type = st.selectbox("Window Type", ["hamming", "hann", "blackman", "rectangular"])
        bit_width = st.select_slider("Quantization Bits", options=[8, 12, 14, 16, 18, 24], value=16)
        
        return fs, filter_type, fc, numtaps, window_type, bit_width

def render_plots(freq_hz, gain_linear, gain_db, taps_q, step_response, fc):
    """Handles the 2x2 visualization grid."""
    row1_col1, row1_col2 = st.columns(2)
    row2_col1, row2_col2 = st.columns(2)

    with row1_col1:
        fig, ax = plt.subplots()
        ax.plot(freq_hz, gain_linear, color='#2ca02c')
        ax.axvline(fc, color='red', linestyle='--', label='Cutoff')
        ax.set_ylabel('Gain')
        ax.set_xlabel('Frequency [Hz]')
        ax.grid(True, alpha=0.3)
        ax.set_title("Frequency Response (Linear)")
        st.pyplot(fig)

    with row1_col2:
        fig, ax = plt.subplots()
        ax.plot(freq_hz, gain_db, color='#1f77b4')
        ax.axvline(fc, color='red', linestyle='--', label='Cutoff')
        ax.set_ylabel('Amplitude [dB]')
        ax.set_xlabel('Frequency [Hz]')
        ax.grid(True, alpha=0.3)
        ax.set_title("Frequency Response (dB)")
        st.pyplot(fig)

    with row2_col1:
        fig, ax = plt.subplots()
        ax.stem(range(len(taps_q)), taps_q, linefmt='b-', markerfmt='bo')
        ax.axhline(0, color='black', linewidth=1)
        ax.set_ylabel('Quantized Value')
        ax.set_xlabel('Tap Index')
        ax.grid(True, alpha=0.3)
        ax.set_title("Impulse Response (Quantized Coefficients)")
        st.pyplot(fig)

    with row2_col2:
        fig, ax = plt.subplots()
        ax.plot(step_response, marker='.', linestyle='-', color='#ff7f0e')
        ax.set_ylabel('Amplitude')
        ax.set_xlabel('Samples')
        ax.grid(True, alpha=0.3)
        ax.set_title("Step Response")
        st.pyplot(fig)

# --- 3. MAIN APPLICATION ---

def main():
    st.set_page_config(page_title="FIR Filter Designer", layout="wide")
    st.title("Filter Characteristics")
    st.markdown("This is a simple FIR filter designer built with Streamlit. I used it to generate coefficients for my FPGA-based FIR filter implementation. You can check out the project on [GitHub](https://github.com/BekdoucheAmine/vhdl-fir-filter-ip)")
    # 1. Get Inputs
    fs, f_type, fc, ntaps, window, bits = render_sidebar()

    # 2. Process Data
    try:
        taps = design_fir_filter(fs, f_type, fc, ntaps, window)
        taps_q = quantize_coefficients(taps, bits)
        freq_hz, gain_lin, gain_db, step_res = calculate_responses(taps, fs, ntaps)

        # 3. Display Results
        render_plots(freq_hz, gain_lin, gain_db, taps_q, step_res, fc)
        
        st.divider()
        c1, c2 = st.columns(2)
        c1.subheader("Quantized Coefficients")
        c1.code(", ".join(map(str, taps_q)), wrap_lines=True, height=150)
        
        c2.subheader("Filter Metrics")
        c2.metric("Nyquist Frequency", f"{fs/2:,.0f} Hz")
        c2.metric("Stopband Attenuation", f"{abs(min(gain_db)):.1f} dB")
        
    except Exception as e:
        st.error(f"Design Error: {e}")
        st.info("Check if your Cutoff Frequencies are valid for the given Sampling Frequency.")

if __name__ == "__main__":
    main()