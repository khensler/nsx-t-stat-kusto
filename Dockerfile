FROM python
SHELL ["/bin/bash", "-c"]
COPY requirements.txt ./
RUN apt-get update && apt-get install build-essential -y
RUN pip install --no-cache-dir -r requirements.txt
RUN wget -qO- https://repos.influxdata.com/influxdb.key | tee /etc/apt/trusted.gpg.d/influxdb.asc >/dev/null
RUN source /etc/os-release && echo "deb https://repos.influxdata.com/${ID} ${VERSION_CODENAME} stable" | tee /etc/apt/sources.list.d/influxdb.list
RUN apt-get update && apt-get install telegraf
RUN systemctl stop telegraf
COPY . .
COPY telegraf.conf /etc/telegraf/telegraf.conf
CMD [ "python", "./main.py" ]