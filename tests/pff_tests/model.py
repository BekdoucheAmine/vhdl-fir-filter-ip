from scipy.signal import freqz, lfilter, firwin
import numpy as np

class FIRFilter:
    def __init__(self, taps=None, fs=None, filter_type=None, fc=None, numtaps=None, window_type=None, latency=4):
        if taps is not None:
            self.taps = taps.astype(np.float64)
        elif fs is not None and filter_type is not None and fc is not None and numtaps is not None and window_type is not None:
            # store parameters
            self.fs = fs
            self.filter_type = filter_type
            self.fc = fc
            self.numtaps = numtaps
            self.window_type = window_type
            # calculate the filter coefficients
            self.taps = firwin(numtaps, cutoff=fc, window=window_type, pass_zero=filter_type, fs=fs)
        else:
            raise ValueError("Either taps or all of fs, filter_type, fc, numtaps, and window_type must be provided.")
        
        self.latency = latency  # Number of clock cycles of latency for the filter output
    
    
    def filter(self, x):
        """Applies the FIR filter to an input signal x."""
        y = lfilter(self.taps, 1, x)
        y_with_latency = np.concatenate((np.zeros(self.latency-1), y))  # Add latency to the output
        return np.floor(y_with_latency).astype(np.int64)

    def update_parameters(self, fs=None, filter_type=None, fc=None, numtaps=None, window_type=None, worN=None):
        """Updates filter parameters and recalculates responses."""
        if fs is not None:
            self.fs = fs
        if filter_type is not None:
            self.filter_type = filter_type
        if fc is not None:
            self.fc = fc
        if numtaps is not None:
            self.numtaps = numtaps
        if window_type is not None:
            self.window_type = window_type
        if worN is not None:
            self.worN = worN
        
        # Recalculate coefficients and responses
        self.taps = firwin(self.numtaps, self.fc, window=self.window_type, pass_zero=self.filter_type, fs=self.fs)

    def set_sampling_frequency(self, fs):
        """Updates the sampling frequency and recalculates responses."""
        self.fs = fs
        self.taps = firwin(self.numtaps, self.fc, window=self.window_type, pass_zero=self.filter_type, fs=self.fs)
        

    def get_sampling_frequency(self):
        """Returns the current sampling frequency."""
        return self.fs
    
    def set_filter_type(self, filter_type):
        """Updates the filter type and recalculates responses."""
        self.filter_type = filter_type
        self.taps = firwin(self.numtaps, self.fc, window=self.window_type, pass_zero=self.filter_type, fs=self.fs)
        

    def get_filter_type(self):
        """Returns the current filter type."""
        return self.filter_type
    
    def set_fc(self, fc):
        """Updates the cutoff frequency and recalculates responses."""
        self.fc = fc
        self.taps = firwin(self.numtaps, self.fc, window=self.window_type, pass_zero=self.filter_type, fs=self.fs)
        

    def get_fc(self):
        """Returns the current cutoff frequency."""
        return self.fc  
    
    def set_numtaps(self, numtaps):
        """Updates the number of taps and recalculates responses."""
        self.numtaps = numtaps
        self.taps = firwin(self.numtaps, self.fc, window=self.window_type, pass_zero=self.filter_type, fs=self.fs)
        
    
    def get_numtaps(self):
        """Returns the current number of taps."""
        return self.numtaps
    
    def set_window_type(self, window_type):
        """Updates the window type and recalculates responses."""
        self.window_type = window_type
        self.taps = firwin(self.numtaps, self.fc, window=self.window_type, pass_zero=self.filter_type, fs=self.fs)
        
    
    def get_window_type(self):
        """Returns the current window type."""
        return self.window_type

    def set_worN(self, worN):
        """Updates the number of frequency points for response calculation."""
        self.worN = worN
        self._calculate_frequency_response()

    def get_worN(self):
        """Returns the current number of frequency points for response calculation."""
        return self.worN