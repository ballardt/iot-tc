#!/bin/bash
########################################
# Split all pcaps in a folder into the #
# workshop paper device flows          #
########################################

# TODO: Devfile and nonfile should be changed since the actual
#       files aren't used any more

# Define the list of device MAC addresses
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

# Be sure we're in the right place
cd /home/trevor/Projects/iot-diff/data/raw/
rm -rf ../filtered
mkdir ../filtered

# Split pcap per device per date and build the command for noniot packets
for date in *.pcap; do
  nonFile="noniot_${date%.*}.pcap"
  noniotCmd="tcpdump -nnr ../../raw/$date -w data.pcap 'not ("
  for d in "${Devices[@]}"; do
    devFile="${d//:/-}.pcap"
    devDate="${devFile%.*}_${date%.*}"

    mkdir ../filtered/$devDate
    cd ../filtered/$devDate

    tcpdump -nnr ../../raw/$date -w 'data.pcap' '(ether host '$d')'

    # Analyze with Bro
    bro -r 'data.pcap'

    # Get rid of empty directories
    if [ ! -f conn.log ]; 
    then
      cd ../
      rm -rf $devDate
      cd ../raw
    else
      cd ../../raw
    fi

    # Filter out this device for the non-IoT pcap
    noniotCmd="$noniotCmd(ether host $d) or "
  done

  # Generate pcap for noniot packets
  cd ../filtered/
  nonFolder="${nonFile%.*}"
  mkdir $nonFolder
  cd $nonFolder
  noniotCmd="${noniotCmd% or })'"
  eval $noniotCmd

  # Analyze with Bro
  bro -r data.pcap

  cd ../../raw
done

