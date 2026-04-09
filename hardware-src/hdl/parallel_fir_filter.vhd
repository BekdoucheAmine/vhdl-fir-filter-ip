----------------------------------------------------------------------------------
-- Engineer: Amine BEKDOUCHE
-- 
-- Create Date: 04.04.2026 23:53:51
-- Design Name: parallel_fir_filter_wrapper.vhd
-- Simulation Name: parallel_fir_filter_sim_wrapper.vhd
-- Module Name: parallel_fir_filter - behavioral
-- Project Name: vhdl_fir_filter_ip
-- Target Devices: zynq-7000
-- Tool Versions: vivado 2018.3
-- Description: Parallel FIR filter implementation with parameterizable number
--              of taps, input width, coefficient width, and output width. The
--              filter is designed to be implemented using DSP48E1 slices in 
--              Xilinx FPGAs for efficient performance.
-- Revision:
-- Revision 0.01 - File Created
----------------------------------------------------------------------------------

library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
use IEEE.NUMERIC_STD.ALL;

entity parallel_fir_filter is
    Generic (
        G_NUM_TAPS          : positive              := 60;      -- number of filter coefficients (taps)
        -- 7 Series DSP48E1 Slice User Guide (https://docs.amd.com/v/u/en-US/ug479_7Series_DSP48E1)
        G_IN_WIDTH          : integer range 8 to 25 := 24;      -- 25 to fit in DSP48E1 input
        G_COEFF_WIDTH       : integer range 8 to 18 := 16;      -- 18 to fit in DSP48E1 input
        G_OUT_WIDTH         : integer range 8 to 48 := 40       -- 48 to fit in DSP48E1 output 
                                                                -- and > G_IN_WIDTH + G_COEFF_WIDTH - 1 to avoid overflow
    );
    Port (
        clk                 : in  std_logic;
        rst_n               : in  std_logic;
        -- slave axis interface
        s_axis_tvalid       : in  std_logic;
        s_axis_tdata        : in  std_logic_vector(G_IN_WIDTH-1 downto 0);
        s_axis_tready       : out std_logic; -- ready to accept after reset, then follows AXIS handshaking protocol
        -- master axis interface
        m_axis_tvalid       : out std_logic;
        m_axis_tdata        : out std_logic_vector(G_OUT_WIDTH-1 downto 0);
        m_axis_tready       : in  std_logic
    );
end parallel_fir_filter;

architecture behavioral of parallel_fir_filter is
    
    -- type definitions and constants
    constant C_MULT_WIDTH           : integer := G_IN_WIDTH + G_COEFF_WIDTH; -- width of multiplication result

    type integer_array_t            is array (natural range <>) of integer;
    type signed_input_array         is array (natural range <>) of signed(G_IN_WIDTH-1 downto 0);
    type signed_mult_array          is array (natural range <>) of signed(C_MULT_WIDTH - 1 downto 0);
    type signed_acc_array           is array (natural range <>) of signed(G_OUT_WIDTH-1 downto 0);
    type signed_coeff_array         is array (natural range <>) of signed(G_COEFF_WIDTH-1 downto 0);

        
    -- force the use of DSP48E1 slices for multiplication and accumulation
    attribute use_dsp               : string;
    attribute use_dsp of Behavioral : architecture is "yes";
    
    -- Internal signals
    signal in_regs                  : signed_input_array(0 to G_NUM_TAPS-1); -- input data registers for each tap
    signal mult_regs                : signed_mult_array(0 to G_NUM_TAPS-1); -- multiplication results for each tap
    signal acc_regs                 : signed_acc_array(0 to G_NUM_TAPS-1); -- accumulation registers for each tap, final output is in acc_regs(0)
        
    -- ========== Coefficients as Integers ==========
    constant coeff_values : integer_array_t(0 to G_NUM_TAPS-1) := (
        -1, -350, -1041, -1911, -2033, 0, 5227, 13397, 22620, 29963, 32767, 29963, 22620, 13397, 5227, 0, -2033, -1911, -1041, -350, -1
    );

    -- ========== Coefficients Converted to Signed ==========
    constant coeff_regs : signed_coeff_array(0 to G_NUM_TAPS-1) := (
        to_signed(coeff_values(0), G_COEFF_WIDTH),  to_signed(coeff_values(1), G_COEFF_WIDTH),
        to_signed(coeff_values(2), G_COEFF_WIDTH),  to_signed(coeff_values(3), G_COEFF_WIDTH),
        to_signed(coeff_values(4), G_COEFF_WIDTH),  to_signed(coeff_values(5), G_COEFF_WIDTH),
        to_signed(coeff_values(6), G_COEFF_WIDTH),  to_signed(coeff_values(7), G_COEFF_WIDTH),
        to_signed(coeff_values(8), G_COEFF_WIDTH),  to_signed(coeff_values(9), G_COEFF_WIDTH),
        to_signed(coeff_values(10), G_COEFF_WIDTH), to_signed(coeff_values(11), G_COEFF_WIDTH),
        to_signed(coeff_values(12), G_COEFF_WIDTH), to_signed(coeff_values(13), G_COEFF_WIDTH),
        to_signed(coeff_values(14), G_COEFF_WIDTH), to_signed(coeff_values(15), G_COEFF_WIDTH),
        to_signed(coeff_values(16), G_COEFF_WIDTH), to_signed(coeff_values(17), G_COEFF_WIDTH),
        to_signed(coeff_values(18), G_COEFF_WIDTH), to_signed(coeff_values(19), G_COEFF_WIDTH),
        to_signed(coeff_values(20), G_COEFF_WIDTH), -- to_signed(coeff_values(21), G_COEFF_WIDTH),
        -- to_signed(coeff_values(22), G_COEFF_WIDTH), to_signed(coeff_values(23), G_COEFF_WIDTH),
        -- to_signed(coeff_values(24), G_COEFF_WIDTH), to_signed(coeff_values(25), G_COEFF_WIDTH),
        -- to_signed(coeff_values(26), G_COEFF_WIDTH), to_signed(coeff_values(27), G_COEFF_WIDTH),
        -- to_signed(coeff_values(28), G_COEFF_WIDTH), to_signed(coeff_values(29), G_COEFF_WIDTH),
        -- to_signed(coeff_values(30), G_COEFF_WIDTH), to_signed(coeff_values(31), G_COEFF_WIDTH),
        others => (others => '0') -- zero out remaining coefficients if G_NUM_TAPS < 32
    );
    -- Output registers
    signal s_axis_tready_r          : std_logic;
    signal m_axis_tvalid_r          : std_logic;

    -- Pipeline valid signals to manage the flow of data through the filter stages
    constant C_LATENCY              : integer := 4; -- latency of the filter pipeline (input to output)
    signal valid_pipeline           : std_logic_vector(C_LATENCY-1 downto 0) := (others => '0');
begin
    assert G_OUT_WIDTH > G_IN_WIDTH + G_COEFF_WIDTH - 1
        report "G_OUT_WIDTH must be greater than G_IN_WIDTH + G_COEFF_WIDTH - 1 to avoid overflow"
        severity ERROR;

    s_axis_tready <= s_axis_tready_r; -- output ready signal for AXIS Slave interface
    m_axis_tvalid <= m_axis_tvalid_r; -- output valid signal for AXIS Master interface
    m_axis_tdata <= std_logic_vector(acc_regs(0)); -- output the final accumulated result

    -- FIR filter process
    -- Transposed implementation: input data is pipelined through registers,
    -- multiplication and accumulation are performed in parallel for each tap
    -- This structure allows higher clock frequencies by breaking the critical
    -- path into smaller stages
    fir_filter_p : process(clk)
    begin
        if rising_edge(clk) then
            if rst_n = '0' then
                -- Reset all registers and outputs
                in_regs     <= (others => (others => '0'));
                mult_regs   <= (others => (others => '0'));
                acc_regs    <= (others => (others => '0'));
            elsif s_axis_tvalid = '1' and s_axis_tready_r = '1' then
                -- pipeline input data into the filter stages
                for i in 0 to G_NUM_TAPS-1 loop
                    in_regs(i) <= signed(s_axis_tdata);
                end loop;
                -- perform multiplication for each tap
                for i in 0 to G_NUM_TAPS-1 loop
                    mult_regs(i) <= in_regs(i) * coeff_regs(i);
                end loop;
                -- accumulate the results
                acc_regs(G_NUM_TAPS-1) <= resize(mult_regs(G_NUM_TAPS-1), G_OUT_WIDTH);
                for i in G_NUM_TAPS-2 downto 0 loop
                    acc_regs(i) <= acc_regs(i+1) + resize(mult_regs(i), G_OUT_WIDTH);
                end loop;
            end if;
        end if;
    end process fir_filter_p;

    -- Control logic for AXIS handshaking
    control_p : process(clk)
    begin
        if rising_edge(clk) then
            if rst_n = '0' then
                s_axis_tready_r <= '1'; -- ready to accept data after reset
                m_axis_tvalid_r <= '0';
            else
                -- 1. Ready Logic: We are ready if the output is accepted 
                -- OR if we aren't currently holding a valid output.
                s_axis_tready_r <= m_axis_tready or (not m_axis_tvalid_r);
                
                -- 2. Data Movement: Only shift if we have data AND space
                if (s_axis_tvalid = '1' and s_axis_tready_r = '1') then
                    -- Shift the 'valid' token through the pipe
                    valid_pipeline(0) <= '1';
                    for i in 1 to C_LATENCY-1 loop
                        valid_pipeline(i) <= valid_pipeline(i-1);
                    end loop;
                elsif (m_axis_tready = '1') then
                    -- If we aren't taking new data but the output was accepted,
                    -- we need to eventually clear the pipeline valid bits.
                    valid_pipeline <= valid_pipeline(C_LATENCY-2 downto 0) & '0';
                end if;

                -- 3. Final Output Valid
                m_axis_tvalid_r <= valid_pipeline(C_LATENCY-1);
            end if;
        end if;
    end process control_p;
end behavioral;
