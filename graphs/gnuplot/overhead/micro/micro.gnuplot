set terminal postscript eps color solid enh font "Helvetica"
set output "micro.eps"
unset log                              # remove any log-scaling
unset label                            # remove any previous labels
set size 1.0,0.8
set format y "%.0f"
set ytics 

unset grid

set style data boxes
set style histogram gap 0

set yrange [1:1300]
set ylabel "Latency (ms)"
unset xlabel

unset xtics
set xlabel offset 0,-3.5 font ",28" 
set ylabel font ",28" offset -4
set ytics font ",20" offset -1 scale 2 nomirror
set ytics auto

set style rect behind fc rgb "#DBE3F0" fs solid 1.0 lc rgb "#DBE3F0"
set object 1 rect behind from graph 0,0 to graph 1,1 fs border lw 0

set lmargin 14
set rmargin 5
set tmargin 1
set bmargin 3.5

set log y

set style fill solid border rgb "black"
set style arrow 1 nohead lw 3 lc rgb "black"

set linetype 11 lc rgb "#D3F2A3"
set linetype 12 lc rgb "#97E196"
set linetype 13 lc rgb "#6CC08B"
set linetype 14 lc rgb "#4B9B82"
set linetype 15 lc rgb "#217A79"
set linetype 16 lc rgb "#105965"

set boxwidth 1

set palette defined (1 "white", 2 "black")
unset colorbox

set border 3 lw 1.5

set key top left font ",18"

set label "1 write" at screen 0.25,0.05 font ",18"
set label "5 writes" at screen 0.505,0.05 font ",18"
set label "10 writes" at screen 0.76,0.05 font ",18"

set arrow 1 from -0.8,3 to 15,3 nohead lw 2 lc rgb "white"
set arrow 2 from -0.6,10 to 15,10 nohead lw 2 lc rgb "white"
set arrow 3 from -0.8,30 to 15,30 nohead lw 2 lc rgb "white"
set arrow 4 from -0.6,100 to 15,100 nohead lw 2 lc rgb "white"
set arrow 5 from -0.8,300 to 15,300 nohead lw 2 lc rgb "white"
set arrow 6 from -0.6,1000 to 15,1000 nohead lw 2 lc rgb "white"

plot newhistogram "1w", 'micro.data' using ($0):2:8:xtic(1) with boxes lc variable notitle, \
                        '' using ($0):2:(0):($3 - $2) with vectors arrowstyle 1 notitle, \
                        '' using ($0 - .25):3:(.5):(0) with vectors arrowstyle 1 notitle, \
                        '' using 0:($2 * .75):2:9 with labels tc palette notitle, \
                        '' using 0:($3 * 1.25):3 with labels notitle, \
     newhistogram "5w", 'micro.data' using ($0 + 5):4:8:xtic(1) with boxes lc variable notitle, \
                        '' using ($0 + 5):4:(0):($5 - $4) with vectors arrowstyle 1 notitle, \
                        '' using ($0 + 4.75):5:(.5):(0) with vectors arrowstyle 1 notitle, \
                        '' using ($0 + 5):($4 * .75):4:9 with labels tc palette notitle, \
                        '' using ($0 + 5):($5 * 1.25):5 with labels notitle, \
     newhistogram "10w", 'micro.data' using ($0 + 10):6:8:xtic(1) with boxes lc variable notitle, \
                         '' using ($0 + 10):6:(0):($7 - $6) with vectors arrowstyle 1 notitle, \
                         '' using ($0 + 9.75):7:(.5):(0) with vectors arrowstyle 1 notitle, \
                         '' using ($0 + 10):($6 * .75):6:9 with labels tc palette notitle, \
                         '' using ($0 + 10):($7 * 1.25):7 with labels notitle, \
     newhistogram "key2", '' using 0:(0) with boxes lt 11 title "Aft Sequential", \
     newhistogram "key3", '' using 0:(0) with boxes lt 13 title "Aft Batch", \
     newhistogram "key4", '' using 0:(0) with boxes lt 14 title "DynamoDB Sequential", \
     newhistogram "key1", '' using 0:(0) with boxes lt 16 title "DynamoDB Batch", \
