set terminal postscript eps color solid enh font "Helvetica"
set output "multi.eps"
unset log                              # remove any log-scaling
unset label                            # remove any previous labels
set size 1.0,0.8
set format y "%.0f"
set ytics 

unset grid

set yrange [0:14000]
set xrange [0:650]
set ylabel "Throughput (txn/s)"
set xlabel "Number of Clients"
set xlabel font ",24" offset 0,-1.5
set ylabel font ",24" offset -4

set xtics font ",18" nomirror
set xtics auto
set ytics font ",18" offset -1 scale 2 nomirror
set ytics auto

set style rect behind fc rgb "#DBE3F0" fs solid 1.0 lc rgb "#DBE3F0"
set object 1 rect behind from graph 0,0 to graph 1,1 fs border lw 0

set lmargin 14
set rmargin 5
set tmargin 1
set bmargin 5

set style fill solid border rgb "black"
set style arrow 1 nohead lw 3 lc rgb "black"

set linetype 11 lc rgb "#D3F2A3"
set linetype 12 lc rgb "#97E196"
set linetype 13 lc rgb "#6CC08B"
set linetype 14 lc rgb "#4B9B82"
set linetype 15 lc rgb "#217A79"
set linetype 16 lc rgb "#105965"

set boxwidth 1

set border 3 lw 1.5

set arrow 1 from 20,2000 to 800,2000 nohead lw 2 lc rgb "white"
set arrow 2 from 20,4000 to 800,4000 nohead lw 2 lc rgb "white"
set arrow 3 from 20,6000 to 800,6000 nohead lw 2 lc rgb "white"
set arrow 4 from 20,8000 to 800,8000 nohead lw 2 lc rgb "white"
set arrow 5 from 20,10000 to 800,10000 nohead lw 2 lc rgb "white"
set arrow 6 from 20,12000 to 800,12000 nohead lw 2 lc rgb "white"

set key top left font ",18"

plot 'multi.data' using 1:2 title "Aft (DynamoDB)" with linespoints lt 16 lw 4.5 pt 2 ps 1.5, \
     14 * x title "Aft (Dynamo) Ideal" with lines dt "-" lt 16 lw 3.5, \
     '' using 1:3 title "Aft (Redis)" with linespoints lt 13 lw 4.5 pt 4 ps 1.5, \
     21.8 * x title "Aft (Redis) Ideal" with lines dt "-" lt 13 lw 3.5
