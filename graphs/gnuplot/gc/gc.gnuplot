set terminal postscript eps color solid enh font "Helvetica"
set output "gc.eps"
unset log                              # remove any log-scaling
unset label                            # remove any previous labels
set size 1.0,0.8
set format y "%.0f"
set ytics 

unset grid

set ylabel "Throughput (txn/s)"
set xlabel "Time (s)"
set xlabel font ",24" offset 0,-1.5
set ylabel font ",24" offset -4

set xtics font ",18" nomirror
set xtics auto
set ytics font ",18" offset -1 scale 2 nomirror
set ytics auto

set xrange[0:80]
set yrange[0:900]

set style rect behind fc rgb "#DBE3F0" fs solid 1.0 lc rgb "#DBE3F0"
set object 1 rect behind from graph 0,0 to graph 1,1 fs border lw 0

set lmargin 14
set rmargin 4
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
set linetype 17 lc rgb "#074050"

set arrow 1 from 0,100 to 90,100 nohead lw 2 lc rgb "white"
set arrow 2 from 2,200 to 90,200 nohead lw 2 lc rgb "white"
set arrow 3 from 0,300 to 90,300 nohead lw 2 lc rgb "white"
set arrow 4 from 2,400 to 90,400 nohead lw 2 lc rgb "white"
set arrow 5 from 0,500 to 90,500 nohead lw 2 lc rgb "white"
set arrow 6 from 2,600 to 90,600 nohead lw 2 lc rgb "white"
set arrow 7 from 0,700 to 90,700 nohead lw 2 lc rgb "white"
set arrow 8 from 2,800 to 90,800 nohead lw 2 lc rgb "white"
set arrow 9 from 0,900 to 90,900 nohead lw 2 lc rgb "white"

set boxwidth 1

set border 11 lw 1.5

set key top right font ",18"

plot 'enabled.data' using 1:2 with lines title "GC Throughput" lt 17 lw 4.5, \
     'disabled.data' using 1:2 with lines title "No GC Throughput" lt 13 lw 4.5, \
     'deleted.data' using 1:2 with lines title "Transactions Deleted" lc rgb "black" dt "." lw 4.5
