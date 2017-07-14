#!/bin/sh -x
########################################
# Split all pcaps in a folder into the #
# workshop paper device flows          #
########################################

# Define the list of device MAC addresses
# IoT
Devices[0]='d0:52:a8:00:67:5e'
Devices[1]='44:65:0d:56:cc:d3'
Devices[2]='70:ee:50:18:34:43'
Devices[3]='f4:f2:6d:93:51:f1'
Devices[4]='00:16:6c:ab:6b:88'
Devices[5]='30:8c:fb:2f:e4:b2'
Devices[6]='00:62:6e:51:27:2e'
Devices[7]='e8:ab:fa:19:de:4f'
Devices[8]='00:24:e4:11:18:a8'
Devices[9]='ec:1a:59:79:f4:89'
Devices[10]='50:c7:bf:00:56:39'
Devices[11]='74:c6:3b:29:d7:1d'
Devices[12]='ec:1a:59:83:28:11'
Devices[13]='18:b4:30:25:be:e4'
Devices[14]='70:ee:50:03:b8:ac'
Devices[15]='00:24:e4:1b:6f:96'
Devices[16]='74:6a:89:00:2e:25'
Devices[17]='00:24:e4:20:28:c6'
Devices[18]='d0:73:d5:01:83:08'
Devices[19]='18:b7:9e:02:20:44'
Devices[20]='e0:76:d0:33:bb:85'
Devices[21]='70:5a:0f:e4:9b:c0'
# non-IoT
# TODO 020c & fce3?
Devices[22]='00:24:e4:10:ee:4c'
Devices[23]='08:21:ef:3b:fc:e3'
Devices[24]='14:cc:20:51:33:ea'
Devices[25]='30:8c:fb:b6:ea:45'
Devices[26]='40:f3:08:ff:1e:da'
Devices[27]='74:2f:68:81:69:42'
Devices[28]='8a:05:81:fa:cc:14'
Devices[29]='ac:bc:32:d4:6f:2f'
Devices[30]='b4:ce:f6:a7:a3:c2'
Devices[31]='d0:a6:37:df:a1:e1'
Devices[32]='d2:13:91:23:2a:58'
Devices[33]='f4:5c:89:93:cc:85'

# Ensure we have enough arguments
if [ "$#" -ne 2 ]
then
  echo "Usage: ./split-dates.sh <path/to/raw/pcap/dir> <path/to/output/dir>"
  exit 1
fi

# Preliminary
curDir=`dirname "$(readlink -f "$0")"`
rawDir="${1%/}"
outDir="${2%/}"/split-dates
rm -rf $outDir
mkdir -p $outDir

# Split pcap per device per date and build the command for non-IoT packets
for datePcap in $rawDir/*.pcap; do
  nonCmd=""
  datePcap=${datePcap##*/}
  for d in "${Devices[@]}"; do
    # Filter the pcap for only this device
    devDate="${d//:/-}_${datePcap%.*}"
    mkdir -p $outDir/$devDate
    tcpdump -nnr "$rawDir/$datePcap" -w "$outDir/$devDate/data.pcap" "(ether host $d)"
    echo tcpdump -nnr $rawDir/$datePcap -w "$outDir/$devDate/data.pcap" "(ether host $d)"
 
    # Analyze with Bro (have to `cd`)
    cd $outDir/$devDate
    bro -r 'data.pcap'

    # Get rid of empty directories, which indicates that there's no traffic for
    # this device on this date. Empty directories complicate things down the line,
    # so it's easiest to remove them here.
    if [ ! -f conn.log ]; 
    then
      cd ../
      rm -rf $devDate
    fi
    cd $curDir

    # Filter out this device for the non-IoT pcap by building up $nonCmd over
    # all devices for this date.
    nonCmd="$nonCmd(ether host $d) or "
  done

  # Generate pcap for non-IoT packets on this date
  nonDir="noniot_${datePcap%.*}"
  mkdir -p $outDir/$nonDir
  nonCmd="${nonCmd% or })'"
  nonCmd="tcpdump -nnr $rawDir/$datePcap -w $outDir/$nonDir/data.pcap 'not ($nonCmd"
  eval $nonCmd

  # Analyze with Bro (have to `cd`), remove if empty
  cd $outDir/$nonDir
  bro -r data.pcap
  if [ ! -f conn.log ]; 
  then
    cd ../
    rm -rf $nonDir
  fi
  cd $curDir
done
