# Machine manager

### Setup

#### Build
`docker build -t machine-manager .`

#### Run
`docker run -p 5000:5000 -v /var/run/docker.sock:/var/run/docker.sock machine-manager`

The `/var/run/...` part is needed to be able to spawn containers on the host system from inside MM container.
Works on Ubuntu 22.04, may need reworking if it breaks on other setups.

### Usage

#### Create

Create a new container with linter for specified language.

Example:
`curl -X POST -H "Content-Type: application/json" -d '{"lang": "java"}' http://localhost:5000/create`

#### Delete

Remove an existing container based on it's IP and port.

Example:
`curl -X POST -H "Content-Type: application/json" -d '{"ip_port": "127.0.0.1:32768"}' http://localhost:5000/delete`