
host="127.0.0.1"

timestamp=$(date --utc +%FT%T.%3NZ)

iperf3 -c $host -P 40 > iperf3.log
iperf3 -c $host -P 40 -R > iperf3-R.log

qperf $host tcp_lat > qperf-tcp-lat.log
qperf $host udp_lat > qperf-udp-lat.log

senderresult=`grep SUM iperf3.log | grep sender | perl -n -e'/([0-9]{1,3}\.?[0-9]{1,3}?) (.bits)\/sec\s*?([0-9]{1}?)/ && print $1'`
senderunit=`grep SUM iperf3.log | grep sender | perl -n -e'/([0-9]{1,3}\.?[0-9]{1,3}?) (.bits)\/sec\s*?([0-9]{1}?)/ && print $2'`
senderretry=`grep SUM iperf3.log | grep sender | perl -n -e'/([0-9]{1,3}\.?[0-9]{1,3}?) (.bits)\/sec\s*?([0-9]{1}?)/ && print $3'`
receiverresult=`grep SUM iperf3.log | grep receiver | perl -n -e'/([0-9]{1,3}\.?[0-9]{1,3}?) (.bits)\/sec/ && print $1'`
receiverunit=`grep SUM iperf3.log | grep receiver | perl -n -e'/([0-9]{1,3}\.?[0-9]{1,3}?) (.bits)\/sec/ && print $2'`


senderresultR=`grep SUM iperf3-R.log | grep sender | perl -n -e'/([0-9]{1,3}\.?[0-9]{1,3}?) (.bits)\/sec\s*?([0-9]{1}?)/ && print $1'`
senderunitR=`grep SUM iperf3-R.log | grep sender | perl -n -e'/([0-9]{1,3}\.?[0-9]{1,3}?) (.bits)\/sec\s*?([0-9]{1}?)/ && print $2'`
senderretryR=`grep SUM iperf3.log | grep sender | perl -n -e'/([0-9]{1,3}\.?[0-9]{1,3}?) (.bits)\/sec\s*?([0-9]{1,}?)/ && print $3'`
receiverresultR=`grep SUM iperf3-R.log | grep receiver | perl -n -e'/([0-9]{1,3}\.?[0-9]{1,3}?) (.bits)\/sec/ && print $1'`
receiverunitR=`grep SUM iperf3-R.log | grep receiver | perl -n -e'/([0-9]{1,3}\.?[0-9]{1,3}?) (.bits)\/sec/ && print $2'`


qperftcplat=`perl -ne 'while(/[0-9]{1,9}\.[0-9]{1,9}? (.s)/g){print "$&\n";}' qperf-tcp-lat.log | awk '{print $1}'`
qperftcplatunit=`perl -ne 'while(/[0-9]{1,9}\.[0-9]{1,9}? (.s)/g){print "$&\n";}' qperf-tcp-lat.log | awk '{print $2}'`
qperfudplat=`perl -ne 'while(/[0-9]{1,9}\.[0-9]{1,9}? (.s)/g){print "$&\n";}' qperf-udp-lat.log | awk '{print $1}'`
qperfudplatunit=`perl -ne 'while(/[0-9]{1,9}\.[0-9]{1,9}? (.s)/g){print "$&\n";}' qperf-udp-lat.log | awk '{print $2}'`


echo timestamp, testtype, senderresult, senderunit, receiverresult, receiverunit, senderretry > iperf.csv
echo $timestamp, iperf, $senderresult, $senderunit, $receiverresult, $receiverunit, $senderretry >>iperf.csv
echo $timestamp, iperf-R, $senderresultR, $senderunitR, $receiverresultR, $receiverunitR, $senderretryR >>iperf.csv

echo timestamp, testtype, latency, unit > qperf.csv
echo $timestamp, tcp_lat, $qperftcplat, $qperftcplatunit >> qperf.csv
echo $timestamp, udp_lat, $qperfudplat, $qperfudplatunit >> qperf.csv

