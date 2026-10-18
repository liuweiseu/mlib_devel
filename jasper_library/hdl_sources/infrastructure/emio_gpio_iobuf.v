`timescale 1ns/1ps
`default_nettype none

// Tri-state IO buffers between PS GPIO EMIO (tri_o/tri_t/tri_i) and FPGA pins,
// equivalent to the IOBUFs Vivado inserts in a block design wrapper for a
// gpio_rtl interface port. A pin is high impedance while its GPIO is an input
// (gpio_t = 1), which is the PS GPIO reset state.
module emio_gpio_iobuf #(
  parameter WIDTH = 1
) (
  input  wire [WIDTH-1:0] gpio_o,
  input  wire [WIDTH-1:0] gpio_t,
  output wire [WIDTH-1:0] gpio_i,
  inout  wire [WIDTH-1:0] gpio_io
);

  genvar i;
  generate
    for (i = 0; i < WIDTH; i = i + 1) begin : gen_iobuf
      IOBUF iobuf_inst (
        .I  (gpio_o[i]),
        .T  (gpio_t[i]),
        .O  (gpio_i[i]),
        .IO (gpio_io[i])
      );
    end
  endgenerate

endmodule

`default_nettype wire
