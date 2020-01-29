from ota_update.main.ota_updater import OTAUpdater

def download_and_install_update_if_available():
     o = OTAUpdater('https://github.com/ntjoar/ESP8266')
     o.download_and_install_update_if_available('TP-Link_33C4', 'nasturtium')

def start():
    from main import germinator.py
    proj = germinator()
    proj.run()

def boot():
    download_and_install_update_if_available()
    start()

boot()