#!/usr/bin/env python3
#
# G. Mazzitelli 2022
# versione DAQ LNGS/LNF per midas file2cloud 
# cheker and sql update Nov 22 
#


def get_s3_sts(client_id, client_secret, endpoint_url, session_token):
    # Specify the session token, access key, and secret key received from the STS
    import boto3
    sts_client = boto3.client('sts',
            endpoint_url = endpoint_url,
            region_name  = ''
            )

    response_sts = sts_client.assume_role_with_web_identity(
            RoleArn          = "arn:aws:iam:::role/S3AccessIAM200",
            RoleSessionName  = 'cygno',
            DurationSeconds  = 3600,
            WebIdentityToken = session_token # qua ci va il token IAM
            )

    s3 = boto3.client('s3',
            aws_access_key_id     = response_sts['Credentials']['AccessKeyId'],
            aws_secret_access_key = response_sts['Credentials']['SecretAccessKey'],
            aws_session_token     = response_sts['Credentials']['SessionToken'],
            endpoint_url          = endpoint_url,
            region_name           = '')
    return s3

def daq_read_runlog_file_size(connection, run_number, verbose=False):
    import cygno as cy
    return cy.cmd.read_sql_value(connection, table_name="Runlog", row_element="run_number", 
                     row_element_condition=str(run_number), 
                     colum_element="file_size", 
                     verbose=verbose)

def main(tag, start_run, verbose):
    #

    import os,sys

    import numpy as np
    import subprocess
    import cygno as cy
    connection = cy.daq_sql_cennection(verbose)
    if not connection:
        print ("ERROR: Sql connetion")
        exit(1)
    script_path = os.path.dirname(os.path.realpath(__file__))
    tape_path = 'davs://xfer-archive.cr.cnaf.infn.it:8443/cygno/'
    client_id     = os.environ['IAM_CLIENT_ID']
    client_secret = os.environ['IAM_CLIENT_SECRET']
    endpoint_url  = os.environ['ENDPOINT_URL']
    tape_token_file  = os.environ['TAPE_TOKEN_FILE']
    s3_token_file  = os.environ['S3_TOKEN_FILE']
    
    
    with open(tape_token_file) as file:
        token = file.readline().strip('\n')
    os.environ["BEARER_TOKEN"] = token
    if (verbose): print("tape token: "+token)
    try:
        tape_data_file = subprocess.check_output("gfal-ls -l "+tape_path+tag+"/ | awk '{print $9\" \"$5}'", shell=True)
        datas = np.sort(np.array(tape_data_file.decode("utf-8").split('\n')))
        #print (type(datas), len(datas))
        k = 0
        j = 0
        for i, data in enumerate(datas):
            if data:
                run, size = np.array(data.split(' '))
                run_number = int(run.split('run')[1].split('.')[0])
                if run_number>=start_run:
                    j +=1
                    rsize = daq_read_runlog_file_size(connection, run_number, verbose=verbose)
                    if verbose: print (i, run, size, rsize)
                    if (int(rsize)-int(size)):
                        print (i, run, size, rsize, j)
                        k+=1
        print(">>> Total file:", i, "mismatch:", k)
    except Exception as e: 
        print("EROOR in getting tape size:", e)
        exit(1)
    exit(0)
    
    
if __name__ == "__main__":
    from optparse import OptionParser
    #
    # deault parser value
    #

    parser = OptionParser(usage='usage: %prog <tag> -v')
    parser.add_option('-r','--run', dest='run', type="string", default='-1', help='start run for rechek')
    parser.add_option('-v','--verbose', dest='verbose', action="store_true", default=False, help='verbose output')
    (options, args) = parser.parse_args()
    if options.verbose: 
        print ("options", options)
        print ("args", args)
    if len(args)<1:
        parser.print_help()
        exit(1)
    main(args[0], int(options.run), options.verbose)
