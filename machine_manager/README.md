# Machine manager

#### Build
`docker build -t machine-manager .`

#### Run
`docker run -p 5000:5000 -v /var/run/docker.sock:/var/run/docker.sock machine-manager`

The `/var/run/...` part is needed to be able to spawn containers on the host system from inside MM container.
Works on Ubuntu 22.04, may need reworking if it breaks on other setups.