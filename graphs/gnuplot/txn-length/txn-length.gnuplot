set terminal postscript eps color solid enh font "Helvetica"
set output "txn-length.eps"
unset log                              # remove any log-scaling
unset label                            # remove any previous labels
set size 1.0,0.8
set format y "%.0f"
set ytics 

unset grid

set style data boxes
set style histogram gap 0

set yrange [0:450]
set ylabel "Latency (ms)"
unset xlabel

set xtics offset 0,-0.5 font ",16" scale 0
set xlabel offset 0,-3.5 font ",28" 
set ylabel font ",28" offset -4
set ytics font ",20" offset -1 scale 2 nomirror
set ytics auto

set style rect behind fc rgb "#DBE3F0" fs solid 1.0 lc rgb "#DBE3F0"
set object 1 rect behind from graph 0,0 to graph 1,1 fs border lw 0

set lmargin 14
set rmargin 5
set tmargin 1
set bmargin 5

unset key

set style fill solid border rgb "black"
set style arrow 1 nohead lw 3 lc rgb "black"

set linetype 11 lc rgb "#D3F2A3"
set linetype 12 lc rgb "#97E196"
set linetype 13 lc rgb "#6CC08B"
set linetype 14 lc rgb "#4B9B82"
set linetype 15 lc rgb "#217A79"
set linetype 16 lc rgb "#105965"
set linetype 17 lc rgb "#074050"

set boxwidth 1

set palette defined (1 "white", 2 "black")
unset colorbox

set border 3 lw 1.5

set arrow 1 from -0.8,50 to 20,50 nohead lw 2 lc rgb "white"
set arrow 2 from -0.6,100 to 20,100 nohead lw 2 lc rgb "white"
set arrow 3 from -0.8,150 to 20,150 nohead lw 2 lc rgb "white"
set arrow 4 from -0.6,200 to 20,200 nohead lw 2 lc rgb "white"
set arrow 5 from -0.8,250 to 20,250 nohead lw 2 lc rgb "white"
set arrow 6 from -0.6,300 to 20,300 nohead lw 2 lc rgb "white"
set arrow 7 from -0.6,350 to 20,350 nohead lw 2 lc rgb "white"
set arrow 8 from -0.6,400 to 20,400 nohead lw 2 lc rgb "white"

set label "Dynamo" at screen 0.28,0.03 font ",22"
set label "Redis" at screen 0.72,0.03 font ",22"

plot newhistogram "dynamo", 'txn-length.data' using ($0):2:6:xtic(1) with boxes lc variable notitle, \
                        '' using ($0):2:(0):($3 - $2) with vectors arrowstyle 1 notitle, \
                        '' using ($0 - .25):3:(.5):(0) with vectors arrowstyle 1 notitle, \
                        '' using 0:($2 - 15):2:7 with labels tc palette notitle, \
                        '' using 0:($3 + 15):3 with labels notitle, \
     newhistogram "redis", 'txn-length.data' using ($0 + 8):4:6:xtic(1) with boxes lc variable notitle, \
                       '' using ($0 + 8):4:(0):($5 - $4) with vectors arrowstyle 1 notitle, \
                       '' using ($0 + 7.75):5:(.5):(0) with vectors arrowstyle 1 notitle, \
                       '' using ($0 + 8):($4 - 15):4:7 with labels tc palette notitle, \
                       '' using ($0 + 8):($5 + 15):5 with labels notitle
