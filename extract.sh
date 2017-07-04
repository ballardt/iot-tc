#!/bin/bash
########################################
# Split all pcaps in a folder into the #
# workshop paper device flows          #
########################################

# Ensure we have enough arguments
if [ "$#" -ne 2 ]
then
  echo "Usage: ./extract.sh <path/to/split-dates/dir> <path/to/output/CSV/dir>"
  exit 1
fi

# Preliminary
curDir=`dirname "$(readlink -f "$0")"`
splitDir="${1%/}"
outfile="$curDir/${2%/}/split-dates-features.csv"
new="new.csv"
prev="prev.csv"
cd $splitDir

# Output CSV header
echo "device,date,sleep_time,active_volume,avg_packet_size,mean_rate,peak_to_mean_rate,active_time,num_servers,num_protocols,unique_dns_reqs,dns_interval,ntp_interval" > $outfile

# Output "device" and "date" columns
for d in ./*/ ; do (trim=${d:2:-1}; echo "${trim//_/,}") ; done >> $outfile
echo "Beginning extraction..."

# Sleep time
echo "Began extracting sleep time"
for d in ./*/ ; do (cd "$d" && tcpstat -r *.pcap 3 | awk '{ if ($2=="n=0") {i++} else {sum+=3*i; i=0; n++}} END { if (n>0) { print sum/n } else { print "N/A"; } }'); done > $new
cat $outfile > $prev
paste $prev $new -d , > $outfile

# Active volume
echo "Began extracting active volume"
for d in ./*/ ; do (cd "$d" && tcpstat -r *.pcap 3 -o '%N\n' | awk '{if ($1>0) {v+=$1} else if (v>0) {sum+=v; v=0; n++} } END { if (n>0) {print sum/n} else {print "N/A"} }') ; done > $new
cat $outfile > $prev
paste $prev $new -d , > $outfile

# Avg. packet size
echo "Began extracting avg pckt size"
for d in ./*/ ; do (cd "$d" && tcpstat -r *.pcap -1 -o '%a\n') ; done > $new
cat $outfile > $prev
paste $prev $new -d , > $outfile

# Mean rate
echo "Began extracting mean rate"
for d in ./*/ ; do (cd "$d" && tcpstat -r *.pcap -1 -o '%B\n') ; done > $new
cat $outfile > $prev
paste $prev $new -d , > $outfile

# Peak / mean rate
echo "Began extracting peak / mean rate"
for d in ./*/ ; do (cd "$d" && tcpstat -r *.pcap 3 -o '%B\n' | awk '{ if ($1>big) {big=$1} sum+=$1; n++} END { if (n>0&&sum>0) {mean=sum/n; print big/mean; big=0} else {print "N/A"} }') ; done > $new
cat $outfile > $prev
paste $prev $new -d , > $outfile

# Active time
echo "Began extracting active time"
for d in ./*/ ; do (cd "$d" && tcpstat -r *.pcap 3 | awk '{ if ($2!="n=0") {i++} else if (i>0) {sum+=3*i; i=0; n++}} END { if (n>0) {print sum/n} else {print "N/A"} }'); done > $new
cat $outfile > $prev
paste $prev $new -d , > $outfile

# No. of servers
echo "Began extracting no. of servers"
for d in ./*/ ; do (cd "$d" && cat conn.log | awk 'NR>8 { print $5 }' | sort | uniq -c | wc -l) ; done > $new
cat $outfile > $prev
paste $prev $new -d , > $outfile

# No. of protocols
echo "Began extracting no. of protocols"
for d in ./*/ ; do (cd "$d" && cat conn.log | awk 'NR>8 { print $6 }' | sort | uniq -c | wc -l) ; done > $new
cat $outfile > $prev
paste $prev $new -d , > $outfile

# Unique DNS requests
echo "Began extracting unique DNS requests"
for d in ./*/ ; do (cd "$d" && 
  if [ ! -f dns.log ]; 
  then
    echo "N/A"
  else
    cat dns.log | awk 'NR>8 { print $5 }' | sort | uniq -c | wc -l
  fi) ; done > $new
cat $outfile > $prev
paste $prev $new -d , > $outfile

# DNS interval
echo "Began extracting DNS interval"
for d in ./*/ ; do (cd "$d" && 
  if [ ! -f dns.log ];
  then
    echo "N/A"
  else
    cat dns.log | sort -n | awk 'NR>8 { if (last!=0) {sum+=$1-last; n++} last=$1 } END { if (n>0) {printf("%f\n", sum/n)} else {print "N/A"}}'
  fi) ; done > $new
cat $outfile > $prev
paste $prev $new -d , > $outfile

# NTP interval
echo "Began extracting NTP interval"
for d in ./*/ ; do (cd "$d" && cat conn.log | sort -n | awk 'NR>8 && $6==123 { if (last!=0) {sum+=$1-last; n++} last=$1 } END { if (n>0) { printf("%f\n", sum/n) } else {print "N/A"} }') ; done > $new
cat $outfile > $prev
paste $prev $new -d , > $outfile
