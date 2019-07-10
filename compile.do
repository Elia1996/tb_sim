vlib work

vcom fa.vhd
vcom rca.vhd
vcom rca_test.vhd

vsim -t ns -novopt work.rca_test

#add list -decimal clk -notrigger a b c cout sum

run 0ns
run 10ms

#write list counter.lst
quit -f
