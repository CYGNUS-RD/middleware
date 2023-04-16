#!/usr/bin/env python3
def main(verbose):
    import time
    from json import dumps
    from kafka import KafkaProducer
    
    import requests
    import boto3
    from boto3sts import credentials as creds
    import urllib.parse
    import sys
    session = creds.assumed_session("infncloud-wlcg", endpoint="https://minio.cloud.infn.it/", verify=True)
    s3 = session.client('s3', endpoint_url="https://minio.cloud.infn.it/", config=boto3.session.Config(signature_version='s3v4'),
                                                verify=True)

    id = 0
    t2 = time.time()
    while True:
        try:
            with open("/tmp/payload.dat", "rb") as f:
                payload = f.read()
            payload_name =  "payload_{:05d}.dat".format(id)
            url_out = s3.generate_presigned_post('cygno-data','EVENTS/'+payload_name, ExpiresIn=3600)

            t1 = time.time()
            files = {'file': (payload_name, payload)}
            http_response = requests.post(url_out['url'], data=url_out['fields'], files=files)
            print("{:05d} {} {:.2f} {:.2f}".format(id, http_response.status_code, time.time()-t1, time.time()-t2))
            id+=1
            time.sleep(0.1)
            t2 = time.time()
        except KeyboardInterrupt:
            sys.exit(0)
    
if __name__ == "__main__":
    from optparse import OptionParser
    parser = OptionParser(usage='usage: %prog\t ')
    parser.add_option('-v','--verbose', dest='verbose', action="store_true", default=False, help='verbose output;');
    (options, args) = parser.parse_args()
    main(verbose=options.verbose)