import requests

__userId = "AKfycbzttkMrIptIbHM2g05uv97eL1yKmr7nUybSDPhX-OyvgcRoAfoo"


def send_message(msg):
    url = ("https://script.google.com/macros/s/{0}/exec?msg={1}".format(__userId, msg))
    requests.get(url)
