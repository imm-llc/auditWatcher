#!/usr/bin/env python3
import adal
import json
import binascii
import requests
import logging
from time import sleep
from pygelf import GelfTcpHandler, GelfUdpHandler, GelfTlsHandler, GelfHttpHandler
from sys import argv, exit
from datetime import datetime, timedelta

class Main:

    def __init__(self):

        self.config_file = argv[1]


    def read_config(self):

        with open(self.config_file, "r") as cf:
            self.config_json = json.load(cf)

            cf.close()

    def init_logger(self):
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger()
        handler = GelfUdpHandler(host=self.config_json['graylog_ip'], port=self.config_json['graylog_port'], _app="auditwatch")
        self.logger.addHandler(handler)

    def init_auth(self):

        c = adal.AuthenticationContext('https://login.microsoftonline.com/{}'.format(self.config_json['tenant_id']))

        try:
            token = c.acquire_token_with_client_certificate(
                "https://manage.office.com",
                self.config_json['client_id'],
                open(self.config_json['private_key']).read(),
                self.config_json['public_key_fingerprint']
            )

            #j = json.dumps(token)
            
            self.access_token = token['accessToken']


        except adal.AdalError as e:
            print("\n\nError getting token\n\n")
            print("Full error: \n")
            print(str(e))
            exit(1)
        except Exception as e:
            print("Unknown error occurred\n\n")
            print("Full error:\n")
            print(str(e))
            exit(0)

    def list_current_subcriptions(self):

        h= {
            "Authorization": "Bearer {}".format(str(self.access_token))
        }

        r = requests.get(f"https://manage.office.com/api/v1.0/{self.config_json['tenant_id']}/activity/feed/subscriptions/list", headers=h)

        print(f"Response from listing subscriptions: {r.status_code}")
        print("")
        print(f"Subscriptions: {r.text}")

        for s in self.config_json['subscriptions']:
            if s not in r.text:
                print(f"{s} not found in current subscriptions")
                self.subscribe_audit_log(s) 

    def subscribe_audit_log(self, content_type):

        h= {
            "Authorization": "Bearer {}".format(str(self.access_token))
        }

        r = requests.post(f"https://manage.office.com/api/v1.0/{self.config_json['tenant_id']}/activity/feed/subscriptions/start?contentType={content_type}", headers=h)

        print(r.status_code)
        print(json.dumps(r.text))

    def get_available_content(self):

        h= {
            "Authorization": "Bearer {}".format(str(self.access_token))
        }

        delta = timedelta(minutes=15)
        now = datetime.utcnow()
        start = now - delta

        start_time = start.strftime("%Y-%m-%dT%H:%M") #"2018-07-16T19:00"
        end_time = now.strftime("%Y-%m-%dT%H:%M") #"2018-07-16T23:00"

        print(f"Checking between {start_time} and {end_time} UTC")


        for s in self.config_json['subscriptions']:

            try:
                r = requests.get(f"https://manage.office.com/api/v1.0/{self.config_json['tenant_id']}/activity/feed/subscriptions/content?contentType={s}&startTime={start_time}&endTime={end_time}", headers=h)
                print(f"\n\nStatus code retrieving available {s} events: {r.status_code}")
                if r.status_code != 200:
                    print(r.text)
                    exit(1)
                j = json.loads(r.text)
                if len(j) < 1:
                    self.logger.warning("No events to retrieve")
                    exit(0)
                print(f"{len(j)} events to process")
                for i in j:
                    self.poll_audit(i['contentUri'])

            except Exception as e:
                print(str(e))


    def poll_audit(self, uri):

        h= {
            "Authorization": "Bearer {}".format(str(self.access_token))
        }

        r = requests.get(uri, headers=h)
        j = json.loads(r.text)

        for i in j:
            self.logger.info(json.dumps(i))


if __name__ == "__main__": 
    m = Main()
    m.read_config()
    m.init_logger()
    m.init_auth()
    m.list_current_subcriptions()
    m.get_available_content()
