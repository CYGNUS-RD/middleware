### IAM migration ###

register on the new identity authentication manager (IAM) https://iam-cygno.cloud.cnaf.infn.it/ on which we are going to move all the 
cygno services soon. This will help us to have an independent authorisation of the users from the INFN infrastructure avoiding the frustrating loss of time we had up 
to now… and easily manage the personal access to different services (queue, grafana, etc, etc), moreover this allows us to have valid tokens up to 12 days ensuring 
data transfer form the queue and other technical futures to boring to be explain. 

to do:

- go to https://iam-cygno.cloud.cnaf.infn.it/
- authenticate in the standard way with your AAI account.
- ask for a new account (you probably are asked to fill only the comment, and put whatever you like)
- wait for a confirmation email and confirm it following the attached link to the mail
- then when you receive a feedback mail please check if you can autenticate on https://iam-cygno.cloud.cnaf.infn.it/
- for expert, if desired configure certificate and so on for alternative login

(Igor, Giorgio and Giulia are already authenticated and do not need to do nothing)

### access to old HOME foleder troght the s3 rados gateway ###
https://s3webui.cloud.infn.it/
