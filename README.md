# Distributed Linters API:

## Machine Manager:

    TODO

## Load Balancer:

#### Forwarding request to linter chosen by load balancing algorithm:

<details>
 <summary><code>POST</code> <code><b>/</b></code> <code>lint</code></summary>

##### Body

| key    | type     | description       |
 |--------|----------|-------------------|
| `code` | `String` | Code to be linted |

##### Responses

| http code | description                           |
 |-----------|---------------------------------------|
| `200`     | There is linter to handle the request |
| `503`     | No available linters                  |

</details>

#### Removing linter from load balancing queue:

<details>
 <summary><code>POST</code> <code><b>/</b></code> <code>remove</code></summary>

##### Body

| key         | type     | description             |
 |-------------|----------|-------------------------|
| `uri`       | `String` | URI of linter to delete |
| `secretKey` | `String` | Key for authorizatoin   |

##### Responses

| http code | description       |
 |-----------|-------------------|
| `200`     | Removal completed |

</details>

    TODO

## Linters:

    TODO