--Copyright 1986-2018 Xilinx, Inc. All Rights Reserved.
----------------------------------------------------------------------------------
--Tool Version: Vivado v.2018.3 (win64) Build 2405991 Thu Dec  6 23:38:27 MST 2018
--Date        : Fri Apr 10 00:46:10 2026
--Host        : Amine_s-Laptop running 64-bit major release  (build 9200)
--Command     : generate_target fir_compiler_sim_imp_resp_wrapper.bd
--Design      : fir_compiler_sim_imp_resp_wrapper
--Purpose     : IP block netlist
----------------------------------------------------------------------------------
library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
library UNISIM;
use UNISIM.VCOMPONENTS.ALL;
entity fir_compiler_sim_imp_resp_wrapper is
  port (
    Clock_250MHz : out STD_LOGIC;
    Fir_Output : out STD_LOGIC_VECTOR ( 31 downto 0 );
    Impulse : out STD_LOGIC_VECTOR ( 15 downto 0 )
  );
end fir_compiler_sim_imp_resp_wrapper;

architecture STRUCTURE of fir_compiler_sim_imp_resp_wrapper is
  component fir_compiler_sim_imp_resp is
  port (
    Clock_250MHz : out STD_LOGIC;
    Fir_Output : out STD_LOGIC_VECTOR ( 31 downto 0 );
    Impulse : out STD_LOGIC_VECTOR ( 15 downto 0 )
  );
  end component fir_compiler_sim_imp_resp;
begin
fir_compiler_sim_imp_resp_i: component fir_compiler_sim_imp_resp
     port map (
      Clock_250MHz => Clock_250MHz,
      Fir_Output(31 downto 0) => Fir_Output(31 downto 0),
      Impulse(15 downto 0) => Impulse(15 downto 0)
    );
end STRUCTURE;
