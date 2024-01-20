# Machine manager

### Setup

#### Build
`docker build -t machine-manager .`

#### Run
`docker run -p 5000:5000 --network linter_network -v /var/run/docker.sock:/var/run/docker.sock machine-manager`

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

### Init update

Initialize update for given language to given version.
This will already push the update into the first step (so some containers may be altered).

`curl -X POST -H "Content-Type: application/json" -d '{"lang": "java", "version": "1.1"}' http://localhost:5000/init-update`

### Update

Push the update for given language into the next update step.

`curl -X POST -H "Content-Type: application/json" -d '{"lang": "java"}' http://localhost:5000/update`

### Rollback

Rollback the update for given language into the previous step.

`curl -X POST -H "Content-Type: application/json" -d '{"lang": "java"}' http://localhost:5000/rollback`

### Status

Get status of all running linters.

`curl http://localhost:5000/status`