set terminal postscript eps color solid enh font "Helvetica"
set output "ft.eps"
unset log                              # remove any log-scaling
unset label                            # remove any previous labels
set size 1.0,0.8
set format y "%.0f"
set ytics 

unset grid

set yrange [0:3000]
set xrange [0:90]
set ylabel "Throughput (txn/s)"
set xlabel "Time (seconds)"
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
set tmargin 3
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

set arrow 1 from 2.0,500 to 90,500 nohead lw 2 lc rgb "white"
set arrow 2 from 2.0,1000 to 90,1000 nohead lw 2 lc rgb "white"
set arrow 3 from 2.0,1500 to 90,1500 nohead lw 2 lc rgb "white"
set arrow 4 from 2.0,2000 to 90,2000 nohead lw 2 lc rgb "white"
set arrow 5 from 2.0,2500 to 90,2500 nohead lw 2 lc rgb "white"
set arrow 6 from 2.0,3000 to 90,3000 nohead lw 2 lc rgb "white"

set arrow 8 from 9,0 to 9,3000 nohead lw 4 dt "." lc rgb "black"
set arrow 9 from 64,0 to 64,3000 nohead lw 4 dt "." lc rgb "black"

set label at 0, 3100 "Node fails" font ",18"
set label at 60, 3100 "Node joins" font ",18"

unset key

plot 'ft.data' using 1:2 title "DynamoDB" with lines lt 15 lw 4.5
