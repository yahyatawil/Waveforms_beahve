Feature: Check Baiscs

  Scenario Outline: Static I/O
     Given Analog Discovery 2 is connected
      When Output #<output_number> set to <output_state>
      Then Input #<input_number> is <input_state>
      Then Close connection with Analog Discovery 2
    Examples:
        |  output_number  |  input_number | output_state | input_state | 
        |  0              |  1            |  1           | 1           |
        |  0              |  1            |  0           | 0           |
        
  Scenario Outline: UART
     Given Analog Discovery 2 UART is configured
      Then Wait to send 0x<rx_char> via UART
      Then Close connection with Analog Discovery 2
    Examples:
        |  rx_char  |  
        |  AA       | 
        |  55       |  