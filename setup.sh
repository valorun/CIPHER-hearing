#!/bin/bash

add_to_startup(){
    filename="$(basename $1)"
    echo "Adding $filename to startup ..."

    if [ -e "/etc/systemd/system/$filename" ]
    then
        echo "Program already added on startup."
    else
        while true; do
            read -p "Do you want to add this program on startup ? " yn
            case $yn in
                [Yy]* ) cp $1 /etc/systemd/system/
                        systemctl daemon-reload
                        systemctl enable $filename
                        systemctl start $filename
                        break;;
                [Nn]* ) exit;;
                * ) echo "Please answer yes or no.";;
            esac
        done
    fi
}

### requirements ###
apt-get -y install "python3"
apt-get -y install "python3-pip"


APP_PATH=$(cd $(dirname "$0") && pwd)
echo "Application path: $APP_PATH"
python3 -m venv venv --system-site-packages
source $APP_PATH/venv/bin/activate

if [ -e $APP_PATH/requirements.txt ]
then
    echo "Installing python dependencies ..."
    $APP_PATH/venv/bin/pip3 install -r $APP_PATH/requirements.txt
else
    echo "No requirements file found."
fi

### Rustpotter wakeword detector ###
curl -L https://github.com/GiviMAD/rustpotter-cli/releases/download/v3.0.2/rustpotter-cli_debian_armv7l -o rustpotter-cli

### Vosk STT ###
cd $APP_PATH
source $APP_PATH/venv/bin/activate
curl -LO https://alphacephei.com/vosk/models/vosk-model-small-fr-0.22.zip
unzip vosk-model-small-fr-0.22.zip

### configure client ###
CONFIG_FILE=$APP_PATH/cipher_hearing/config.ini

read -p "MQTT client id [UNKNOWN]: " id
read -p "MQTT server address [localhost]: " addr
read -p "MQTT server port [1883]: " port
id=${id:-UNKNOWN}
addr=${addr:-localhost}
port=${port:-1883}

echo -e "[GENERAL]" > $CONFIG_FILE
echo -e "MQTT_CLIENT_ID=$id" >> $CONFIG_FILE
echo -e "\n[MQTT_BROKER]" >> $CONFIG_FILE
echo -e "URL=$addr" >> $CONFIG_FILE
echo -e "PORT=$port" >> $CONFIG_FILE

### add to startup ###
cat > $APP_PATH/cipher-hearing.service <<EOF
[Unit]
Description=CIPHER robotic client STT
After=network.target

[Service]
WorkingDirectory=$APP_PATH
ExecStart=$APP_PATH/venv/bin/python3 $APP_PATH/app.py
Restart=always

[Install]
WantedBy=multi-user.target
EOF

add_to_startup "$APP_PATH/cipher-hearing.service"
