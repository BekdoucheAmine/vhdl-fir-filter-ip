--Copyright 1986-2018 Xilinx, Inc. All Rights Reserved.
----------------------------------------------------------------------------------
--Tool Version: Vivado v.2018.3 (win64) Build 2405991 Thu Dec  6 23:38:27 MST 2018
--Date        : Sat Apr  4 00:01:07 2026
--Host        : Amine_s-Laptop running 64-bit major release  (build 9200)
--Command     : generate_target sim_impulse_response_wrapper.bd
--Design      : sim_impulse_response_wrapper
--Purpose     : IP block netlist
----------------------------------------------------------------------------------
library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
library UNISIM;
use UNISIM.VCOMPONENTS.ALL;
entity sim_impulse_response_wrapper is
  port (
    Clock_250MHz : out STD_LOGIC;
    Fir_Output : out STD_LOGIC_VECTOR ( 31 downto 0 );
    Impulse : out STD_LOGIC_VECTOR ( 15 downto 0 )
  );
end sim_impulse_response_wrapper;

architecture STRUCTURE of sim_impulse_response_wrapper is
  component sim_impulse_response is
  port (
    Clock_250MHz : out STD_LOGIC;
    Fir_Output : out STD_LOGIC_VECTOR ( 31 downto 0 );
    Impulse : out STD_LOGIC_VECTOR ( 15 downto 0 )
  );
  end component sim_impulse_response;
begin
sim_impulse_response_i: component sim_impulse_response
     port map (
      Clock_250MHz => Clock_250MHz,
      Fir_Output(31 downto 0) => Fir_Output(31 downto 0),
      Impulse(15 downto 0) => Impulse(15 downto 0)
    );
end STRUCTURE;
