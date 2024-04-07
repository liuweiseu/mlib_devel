// NB: This core requires a WB timeout allowance
// of ~2^NCLKDIVBITS * (NBITS + 2)


module axi4lite_spi_master#(
    parameter NBITS = 24,
    parameter NCLKDIVBITS = 5,
    parameter NCSBITS = 3
    )(
    // axi4lite registers
    input         aclk,                 // axi4lite clk
    input         [31 : 0] spi_din,
    output        [31 : 0] spi_dout,
    input         [7 : 0]  spi_cs,
    input         [7 : 0]  spi_cs_idle,
    input         spi_trigger,
    output        [31 : 0] spi_event_count,
    // SPI
    output [NCSBITS - 1 : 0] cs,
    output sclk,
    output mosi,
    input miso
  );

  reg wb_ack;

  /*** Registers ****/
  //reg [31:0] spi_din = 32'b0;
  reg [31:0] spi_dout = 32'b0;
  //reg [7:0] spi_cs;
  //reg [7:0] spi_cs_idle;
  wire [NBITS-1:0] spi_dout_tmp;
  wire spi_dvld;
  
  //reg spi_trigger;
  reg spi_ack;
  reg wait_for_spi = 1'b0;
   
  reg [31:0] wb_data_out_reg = 32'b0;
  reg [31:0] spi_event_count = 32'b0;

  wire spi_trigger_rising_edge;
  reg spi_trigger_d;
  always @(posedge aclk)begin
    spi_trigger_d <= spi_trigger;
  end
  assign spi_trigger_rising_edge = spi_trigger & (~spi_trigger_d);

  always @(posedge aclk) begin
      // Ack SPI transactions outside of WB transaction
      // clause. This means that if the WB bus times out,
      // the SPI command could still succeed and update
      // the SPI read data.
      // Reading back address 0 will verify if the
      // SPI transaction is still pending and/or has
      // completed but hasn't been acknowledged
      if (wait_for_spi && spi_dvld) begin
        wait_for_spi <= 1'b0;
        spi_event_count <= spi_event_count + 1'b1;
        spi_dout[NBITS-1:0] <= spi_dout_tmp;
        spi_ack <= 1'b1;
      end
      else if(spi_trigger_rising_edge) begin
        wait_for_spi <= 1'b1;
        spi_event_count <= spi_event_count;
        spi_dout <= spi_dout;
        spi_ack <= 0;
      end
      else begin
        wait_for_spi <= wait_for_spi;
        spi_event_count <= spi_event_count;
        spi_dout <= spi_dout;
        spi_ack <= 0;
      end
  end

  spi_master #(
    .NCLKDIVBITS(NCLKDIVBITS),
    .NBITS(NBITS),
    .NCSBITS(NCSBITS)
    ) spi_master_inst (
    .clk(aclk),
    .cs_in(spi_cs[NCSBITS-1:0]),
    .cs_in_idle(spi_cs_idle[NCSBITS-1:0]),
    .din(spi_din[NBITS-1:0]),
    .trigger(spi_trigger),
    .ack(spi_ack),
    .dout(spi_dout_tmp),
    .dvld(spi_dvld),

    .cs(cs),
    .sclk(sclk),
    .mosi(mosi),
    .miso(miso)
  );

endmodule
