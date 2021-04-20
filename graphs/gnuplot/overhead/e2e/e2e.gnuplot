set terminal postscript eps color solid enh font "Helvetica"
set output "e2e.eps"
unset log                              # remove any log-scaling
unset label                            # remove any previous labels
set size 1.0,0.8
set format y "%.0f"
set ytics 

unset grid

set style data boxes
set style histogram gap 0

set yrange [0:825]
# set xrange [-1.0:12]
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
set linetype 14 lc rgb "#4B9B82"
set linetype 15 lc rgb "#217A79"
set linetype 16 lc rgb "#105965"

set boxwidth 1

set palette defined (1 "white", 2 "black")
unset colorbox

set label "S3" at screen 0.26,.05 font ",22"
set label "DynamoDB" at screen .48,.05 font ",22" 
set label "Redis" at screen .79,.05 font ",22" 

set border 3 lw 1.5

set arrow 1 from -0.7,100 to 13.5,100 nohead lw 2 lc rgb "white"
set arrow 2 from -0.7,200 to 13.5,200 nohead lw 2 lc rgb "white"
set arrow 3 from -0.7,300 to 13.5,300 nohead lw 2 lc rgb "white"
set arrow 4 from -0.7,400 to 13.5,400 nohead lw 2 lc rgb "white"
set arrow 5 from -0.7,500 to 13.5,500 nohead lw 2 lc rgb "white"
set arrow 6 from -0.7,600 to 13.5,600 nohead lw 2 lc rgb "white"
set arrow 7 from -0.7,700 to 13.5,700 nohead lw 2 lc rgb "white"
set arrow 8 from -0.7,800 to 13.5,800 nohead lw 2 lc rgb "white"
set arrow 9 from -0.7,900 to 13.5,900 nohead lw 2 lc rgb "white"

set key top right font ",18"

plot newhistogram "S3", 'e2e.data' every ::1:::2 using ($0):2:8 with boxes lc variable notitle, \
                        '' every ::1:::2 using 0:2:(0):($3 - $2) with vectors arrowstyle 1 notitle, \
                        '' every ::1:::2 using ($0 - .25):3:(.5):(0) with vectors arrowstyle 1 notitle, \
                        '' every ::1:::2 using 0:($2 - 20):2:9 with labels font ",16" tc palette notitle, \
                        '' every ::1:::2 using 0:($3 + 20):3 with labels font ",16" notitle, \
     newhistogram "DynamoDB", 'e2e.data' using ($0 + 3):4:8:xtic(1) with boxes lc variable notitle, \
                              '' using ($0 + 3):4:(0):($5 - $4) with vectors arrowstyle 1 notitle, \
                              '' using ($0 + 2.75):5:(.5):(0) with vectors arrowstyle 1 notitle, \
                              '' using ($0 + 3):($4 - 20):4:9 with labels font ",16" tc palette notitle, \
                              '' using ($0 + 3):($5 + 20):5 with labels font ",16" notitle, \
     newhistogram "Redis", 'e2e.data' every ::1:::2 using ($0 + 7):6:8:xtic(1) with boxes lc variable notitle, \
                           '' every ::1:::2 using ($0 + 7):6:(0):($7 - $6) with vectors arrowstyle 1 notitle, \
                           '' every ::1:::2 using ($0 + 6.75):7:(.5):(0) with vectors arrowstyle 1 notitle, \
                           '' every ::1:::2 using ($0 + 7):($6 - 20):6:9 with labels font ",16" tc palette notitle, \
                           '' every ::1:::2 using ($0 + 7):($7 + 20):7 with labels font ",16" notitle, \
     newhistogram "key1", '' using 0:(0) with boxes lt 11 title "Transactional", \
     newhistogram "key2", '' using 0:(0) with boxes lt 13 title "Plain", \
     newhistogram "key3", '' using 0:(0) with boxes lt 16 title "Aft", \
