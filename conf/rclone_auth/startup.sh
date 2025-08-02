#!/bin/bash
i=0
# env

if [ -z "$TOKEN_FILE" ]; then 
	TOKEN_FILE='/tmp/token'  
else 
	echo "using ${TOKEN_FILE}"
fi

DURATION=3600

echo "STARTNG TOKENER-->"
while :
do
	d=`date +%Y-%M-%d\ %H:%M:%S`
	minio=$(curl -s "https://minio.cloud.infn.it/" \
		-X POST \
  		-H "Content-Type: application/x-www-form-urlencoded" \
  		-d "Action=AssumeRoleWithWebIdentity" \
  		-d "RoleArn=arn:aws:iam::cygno:role/IAMaccess" \
  		-d "RoleSessionName=Bob" \
  		-d "WebIdentityToken=${TOKEN}" \
  		-d "DurationSeconds=${DURATION}" \
  		-d "Version=2011-06-15")

	cnaf=$(curl -s "https://s3.cr.cnaf.infn.it:7480/" \
  		-X POST \
  		-H "Content-Type: application/x-www-form-urlencoded" \
  		-d "Action=AssumeRoleWithWebIdentity" \
  		-d "RoleArn=arn:aws:iam::cygno:role/IAMaccess" \
  		-d "RoleSessionName=Bob" \
  		-d "WebIdentityToken=${TOKEN}" \
  		-d "DurationSeconds=${DURATION}" \
  		-d "Version=2011-06-15")

	minio_access_key=$(echo "$minio" | grep -oPm1 "(?<=<AccessKeyId>)[^<]+")
	minio_secret_key=$(echo "$minio" | grep -oPm1 "(?<=<SecretAccessKey>)[^<]+")
	minio_session_token=$(echo "$minio" | grep -oPm1 "(?<=<SessionToken>)[^<]+")
#	minio_session_expiration=$(echo "$minio" | grep -oPm1 "(?<=<Expiration>)[^<]+")

	cnaf_access_key=$(echo "$cnaf" | grep -oPm1 "(?<=<AccessKeyId>)[^<]+")
	cnaf_secret_key=$(echo "$cnaf" | grep -oPm1 "(?<=<SecretAccessKey>)[^<]+")
	cnaf_session_token=$(echo "$cnaf" | grep -oPm1 "(?<=<SessionToken>)[^<]+")
#	cnaf_session_expiration=$(echo "$cnaf" | grep -oPm1 "(?<=<Expiration>)[^<]+")
#	token_time=`date -d"${cnaf_session_expiration}" +%s`
#	now=`date +%s`
#	DT=$[token_time-now]


	cd /config/rclone/
##################################################
cat > ./rclone.conf <<EOF
[0_BARI]
type = s3
provider = Other
env_auth = false
access_key_id = ${BA_ACCESS_KEY_ID}
secret_access_key = ${BA_SECRET_ACCESS_KEY}
endpoint = https://swift.recas.ba.infn.it/

[1_MINIO]
type = s3
provider = Other
env_auth = false
access_key_id = ${minio_access_key}
secret_access_key = ${minio_secret_key}
session_token = ${minio_session_token}
endpoint = https://minio.cloud.infn.it/
region = ${S3_REGION}

[2_CNAF]
type = s3
provider = Other
env_auth = false
access_key_id = ${cnaf_access_key}
secret_access_key = ${cnaf_secret_key}
session_token = ${cnaf_session_token}
endpoint = https://s3.cr.cnaf.infn.it:7480/
region = ${S3_REGION}

EOF
##################################################
	pwd
	ls -lsrt
	cat  ./rclone.conf


	if [ $? -ne 0 ]; then 
		WAIT=10  #retry in 5 seconds
	else
		WAIT=$(($DURATION-300)) # refresh token after
	fi
	echo "$d next refreshing token in $WAIT sec, loop $i"
	i=$((i+1))
	sleep $WAIT
done
