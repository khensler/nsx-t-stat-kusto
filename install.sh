#!/bin/bash
while getopts ":p:c:" opt; do
  case $opt in
    p) install_path="$OPTARG"
    ;;
    c) cloud_id="$OPTARG"
    ;;
    \?) echo "Invalid option -$OPTARG" >&2
    exit 1
    ;;
  esac

  case $OPTARG in
    -*) echo "Option $opt needs a valid argument"
    exit 1
    ;;
  esac
done

wget -qO- https://repos.influxdata.com/influxdb.key | tee /etc/apt/trusted.gpg.d/influxdb.asc >/dev/null
source /etc/os-release && echo "deb https://repos.influxdata.com/${ID} ${VERSION_CODENAME} stable" | tee /etc/apt/sources.list.d/influxdb.list
apt-get update && apt-get install telegraf
service telegraf stop
mkdir $install_path
echo "AVS_CLOUD_ID=$c" > $install_path/.env
cp main.py $install_path
cp requirements.txt $install_path
cp telegraf.conf $install_path
cp nsx-stat.service $install_path
cp start.sh $install_path
chmod +x $install_path/start.sh
cd $install_path
python3 -m venv venv
source ./venv/bin/activate
python3 -m pip install -r requirements.txt
sed -i "s~/##WORKINGDIR##~$install_path~" nsx-stat.service
cp nsx-stat.service /etc/systemd/system/
systemctl daemon-reload
sed -i "s~/##WORKINGDIR##~$install_path~" $install_path/telegraf.conf
cp $install_path/telegraf.conf /etc/telegraf/
systemctl start telegraf
systemctl start nsx-stats