module adder(
    input clk,
    input [31:0] a,
    input [31:0] b,
    output reg [31:0] sum
);

always @(posedge clk) begin
    sum <= a + b;
end

endmodule;