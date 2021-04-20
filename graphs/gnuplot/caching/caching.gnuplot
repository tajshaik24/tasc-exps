set terminal postscript eps color solid enh font "Helvetica"
set output "caching.eps"
unset log                              # remove any log-scaling
unset label                            # remove any previous labels
set size 1.0,0.8
set format y "%.0f"
set ytics 

unset grid

set log y

set style data boxes
set style histogram gap 0

set yrange [1:7000]
set ylabel "Latency (ms)"
unset xlabel

# set xtics offset 0,-1 font ",18" nomirror
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

unset key

set style fill solid border rgb "black"
set style arrow 1 nohead lw 3 lc rgb "black"

set linetype 11 lc rgb "#D3F2A3"
set linetype 12 lc rgb "#97E196"
set linetype 13 lc rgb "#6CC08B"
set linetype 14 lc rgb "#428A73"
set linetype 16 lc rgb "#105965"

set boxwidth 1

set palette defined (1 "white", 2 "black")
unset colorbox

set label "z=1.0" at screen 0.27,.05 font ",22"
set label "z=1.5" at screen .50,.05 font ",22" 
set label "z=2.0" at screen .775,.05 font ",22" 

set border 3 lw 1.5

set arrow 1 from -0.8,3 to 20,3 nohead lw 2 lc rgb "white"
set arrow 2 from -0.6,10 to 20,10 nohead lw 2 lc rgb "white"
set arrow 3 from -0.8,30 to 20,30 nohead lw 2 lc rgb "white"
set arrow 4 from -0.6,100 to 20,100 nohead lw 2 lc rgb "white"
set arrow 5 from -0.8,300 to 20,300 nohead lw 2 lc rgb "white"
set arrow 6 from -0.6,1000 to 20,1000 nohead lw 2 lc rgb "white"
set arrow 7 from -0.6,3000 to 20,3000 nohead lw 2 lc rgb "white"

set key horizontal top left font ",17"

plot newhistogram "z1", 'caching.data' using ($0):2:8:xtic(1) with boxes lc variable notitle, \
                        '' using ($0):2:(0):($3 - $2) with vectors arrowstyle 1 notitle, \
                        '' using ($0 - .25):3:(.5):(0) with vectors arrowstyle 1 notitle, \
                        '' using 0:($2 * .75):2:9 with labels tc palette notitle, \
                        '' using 0:($3 * 1.25):3 with labels notitle, \
     newhistogram "z1.5", 'caching.data' using ($0 + 6):4:8:xtic(1) with boxes lc variable notitle, \
                          '' using ($0 + 6):4:(0):($5 - $4) with vectors arrowstyle 1 notitle, \
                          '' using ($0 + 5.75):5:(.5):(0) with vectors arrowstyle 1 notitle, \
                          '' using ($0 + 6):($4 * .75):4:9 with labels tc palette notitle, \
                          '' using ($0 + 6):($5 * 1.25):5 with labels notitle, \
     newhistogram "z2", 'caching.data' using ($0 + 12):6:8:xtic(1) with boxes lc variable notitle, \
                        '' using ($0 + 12):6:(0):($7 - $6) with vectors arrowstyle 1 notitle, \
                        '' using ($0 + 11.75):7:(.5):(0) with vectors arrowstyle 1 notitle, \
                        '' using ($0 + 12):($6 * .75):6:9 with labels tc palette notitle, \
                        '' using ($0 + 12):($7 * 1.25):7 with labels notitle, \
     newhistogram "key1", '' using 0:(0) with boxes lt 11 title "DynamoDB Txns", \
     newhistogram "key2", '' using 0:(0) with boxes lt 12 title "Aft-D No Caching", \
     newhistogram "key3", '' using 0:(0) with boxes lt 13 title "Aft-D Caching", \
     newhistogram "key4", '' using 0:(0) with boxes lt 14 title "Aft-R No Caching", \
     newhistogram "key5", '' using 0:(0) with boxes lt 16 title "Aft-R Caching", \
