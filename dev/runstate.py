import midas.client

"""
A simple example program that connects to a midas experiment,
reads an ODB value, then sets an ODB value.

Expected output is:

```
The experiment is currently stopped
The new value of /pyexample/eg_float is 5.670000
```
"""

if __name__ == "__main__":
    client = midas.client.MidasClient("pytest")

    # Read a value from the ODB. The return value is a normal python
    # type (an int in this case, but could also be a float, string, bool,
    # list or dict).
    state = client.odb_get("/Runinfo/State")

    if state == midas.STATE_RUNNING:
        print("The experiment is currently running")
    elif state == midas.STATE_PAUSED:
        print("The experiment is currently paused")
    elif state == midas.STATE_STOPPED:
        print("The experiment is currently stopped")
    else:
        print("The experiment is in an unexpected run state")

