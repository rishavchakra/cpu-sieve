CC=arm-linux-gnu-gcc

default: zipf seq

zipf: zipf.o
	$(CC) zipf.c -lm -o mem_zipf
	$(CC) zipf.c -DCONTROL -lm -o mem_zipf_control

seq: seq.o
	$(CC) seq.c -o mem_seq
	$(CC) seq.c -DCONTROL -o mem_seq_control
