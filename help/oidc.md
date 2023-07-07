### how to install oidc on linux
* go to the repo http://repo.data.kit.edu/
* check your ubuntu relese `lsb_release -a`
* example of ubuntu 20.04:
<code>
curl repo.data.kit.edu/repo-data-kit-edu-key.gpg | gpg --dearmor > /etc/apt/trusted.gpg.d/kitrepo-archive.gpg
</code>
<code>
vi /etc/apt/sources.list
</code>
* paste:
<code>
deb [signed-by=/etc/apt/trusted.gpg.d/kitrepo-archive.gpg] https://repo.data.kit.edu//ubuntu/20.04 ./
deb [signed-by=/etc/apt/trusted.gpg.d/kitrepo-archive.gpg] https://repo.data.kit.edu//ubuntu/focal ./
</code>
* save and exit, and do the followinfg command:
<code>
apt-get update
apt-get install oidc-agent
</code>
  
