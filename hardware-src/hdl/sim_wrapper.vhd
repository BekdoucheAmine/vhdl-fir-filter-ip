--Copyright 1986-2018 Xilinx, Inc. All Rights Reserved.
----------------------------------------------------------------------------------
--Tool Version: Vivado v.2018.3 (win64) Build 2405991 Thu Dec  6 23:38:27 MST 2018
--Date        : Mon Apr  6 11:29:12 2026
--Host        : Amine_s-Laptop running 64-bit major release  (build 9200)
--Command     : generate_target sim_wrapper.bd
--Design      : sim_wrapper
--Purpose     : IP block netlist
----------------------------------------------------------------------------------
library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
library UNISIM;
use UNISIM.VCOMPONENTS.ALL;
entity sim_wrapper is
  port (
    Clock_250MHz : out STD_LOGIC;
    Fir_Output : out STD_LOGIC_VECTOR ( 31 downto 0 );
    Mixed_Signals : out STD_LOGIC_VECTOR ( 8 downto 0 );
    PFF_OUT : out STD_LOGIC_VECTOR ( 29 downto 0 );
    Sine_500KHz : out STD_LOGIC_VECTOR ( 7 downto 0 );
    Sine_50MHz : out STD_LOGIC_VECTOR ( 7 downto 0 )
  );
end sim_wrapper;

architecture STRUCTURE of sim_wrapper is
  component sim is
  port (
    Mixed_Signals : out STD_LOGIC_VECTOR ( 8 downto 0 );
    Clock_250MHz : out STD_LOGIC;
    Sine_500KHz : out STD_LOGIC_VECTOR ( 7 downto 0 );
    Sine_50MHz : out STD_LOGIC_VECTOR ( 7 downto 0 );
    Fir_Output : out STD_LOGIC_VECTOR ( 31 downto 0 );
    PFF_OUT : out STD_LOGIC_VECTOR ( 29 downto 0 )
  );
  end component sim;
begin
sim_i: component sim
     port map (
      Clock_250MHz => Clock_250MHz,
      Fir_Output(31 downto 0) => Fir_Output(31 downto 0),
      Mixed_Signals(8 downto 0) => Mixed_Signals(8 downto 0),
      PFF_OUT(29 downto 0) => PFF_OUT(29 downto 0),
      Sine_500KHz(7 downto 0) => Sine_500KHz(7 downto 0),
      Sine_50MHz(7 downto 0) => Sine_50MHz(7 downto 0)
    );
end STRUCTURE;
