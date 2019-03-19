#/bin/bash

if [-p fifo]
then
	rm fifo
fi

mkfifo fifo
	nc -l -v -p 9000 > fifo
