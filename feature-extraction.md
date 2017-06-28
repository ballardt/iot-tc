Sleep time
----------
Use tcpstat to calculate how long we have between activity on average. Block size is 3 seconds.

    for d in ./*/ ; do (cd "$d" && tcpstat -r *.pcap 3 | awk '{ if ($2=="n=0") {i++} else {sum+=3*i; i=0; n++}} END { if (n>0) { print sum/n } else { print "N/A"; } }'); done


Active Volume
-------------
Use tcpstat to get average active volume size. Connection must have at least 1 packet in 3 second windows to be considered active, and subsequent windows with activity are lumped together

    for d in ./*/ ; do (cd "$d" && tcpstat -r *.pcap 3 -o '%N\n' | awk '{if ($1>0) {v+=$1} else if (v>0) {sum+=v; v=0; n++} } END { if (n>0) {print sum/n} else {print "N/A"} }') ; done


Avg. Packet Size
----------------
tcpstat with interval -1

    for d in ./*/ ; do (cd "$d" && tcpstat -r *.pcap -1 -o '%a\n') ; done


Mean Rate
---------
tcpstat with interval -1

    for d in ./*/ ; do (cd "$d" && tcpstat -r *.pcap -1 -o '%B\n') ; done


Peak / Mean Rate
----------------
Find the peak, then divide it by the mean rate

    for d in ./*/ ; do (cd "$d" && tcpstat -r *.pcap 3 -o '%B\n' | awk '{ if ($1>big) {big=$1} sum+=$1; n++} END { if (n>0&&sum>0) {mean=sum/n; print big/mean; big=0} else {print "N/A"} }') ; done


Active Time
-----------
Almost the same as sleep time, just flip the first comparator

    for d in ./*/ ; do (cd "$d" && tcpstat -r *.pcap 3 | awk '{ if ($2!="n=0") {i++} else if (i>0) {sum+=3*i; i=0; n++}} END { if (n>0) {print sum/n} else {print "N/A"} }'); done


No. of Servers
--------------
Count the unique resp IPs in conn.log

    for d in ./*/ ; do (cd "$d" && cat conn.log | awk 'NR>8 { print $5 }' | sort | uniq -c | wc -l) ; done


No. of Protocols
----------------
Get the number of unique resp port numbers (this is how they do it in the paper)

    for d in ./*/ ; do (cd "$d" && cat conn.log | awk 'NR>8 { print $6 }' | sort | uniq -c | wc -l) ; done


Unique DNS Requests
-------------------
Count the number of unique resp IPs in dns.log

    for d in ./*/ ; do (cd "$d" && 
      if [ ! -f dns.log ]; 
      then
        echo "N/A"
      else
        cat dns.log | awk 'NR>8 { print $5 }' | sort | uniq -c | wc -l
      fi) ; done


DNS Interval
------------
Sum up the differences between all timestamps

    for d in ./*/ ; do (cd "$d" && 
      if [ ! -f dns.log ];
      then
        echo "N/A"
      else
        cat dns.log | sort -n | awk 'NR>8 { if (last!=0) {sum+=$1-last; n++} last=$1 } END { if (n>0) {printf("%f\n", sum/n)} else {print "N/A"}}'
      fi) ; done


NTP Interval
------------
Same as DNS interval, but check the port number and use conn.log

    for d in ./*/ ; do (cd "$d" && cat conn.log | sort -n | awk 'NR>8 && $6==123 { if (last!=0) {sum+=$1-last; n++} last=$1 } END { if (n>0) { printf("%f\n", sum/n) } else {print "N/A"} }') ; done
