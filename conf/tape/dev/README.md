## Tape dev
- cloud2tape.py, cloud2tape_v1.py, cloud2tape_v2.py --> copy data form cloud to tape trusting the SQL DB
- cloud2tape_v2_fromlist.py copy data from cloud2tape from a file list of run names (use -f options)
- init.sh  inint function running in the container executing cloud2tape
- listTapeByTag.py check database and files consistency in clud and tape, comparing  all file size. set also the size on db if different from the file size.
- testRepofiles.py
