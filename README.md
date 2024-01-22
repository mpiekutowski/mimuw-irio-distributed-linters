# Runing the project

## Pull linter images:

```
docker pull ghcr.io/mpiekutowski/linter:1.0 
docker pull ghcr.io/mpiekutowski/linter:1.1 
docker pull ghcr.io/mpiekutowski/linter:1.2 
docker pull ghcr.io/mpiekutowski/linter:2.0
```

## Start the containers:

`docker compose up`

# Distributed Linters API:

## Machine Manager:

#### Creating new linter:

<details>
 <summary><code>POST</code> <code><b>/</b></code> <code>create</code></summary>

##### Body

| key      | type     | description                       |
|----------|----------|-----------------------------------|
| `lang`   | `String` | Language for which to create a linter |


##### Response 200, JSON:

| key       | type      | description              |
 |-----------|-----------|--------------------------|
| `status`  | `String` | Result of operation, `ok` for successful creation |
| `ip` | `String`  | IP address of the created linter        |

##### Response 400, JSON:

| key       | type      | description              |
 |-----------|-----------|--------------------------|
| `status`  | `String` | Result of operation, `error` for invalid request parameter |
| `message` | `String`  | Detailed explanation of error         |

##### Response 500, JSON:

| key       | type      | description              |
|-----------|-----------|--------------------------|
| `status`  | `String` | Result of operation, `error` for internal server error |
| `message` | `String`  | Detailed explanation of error         |

</details>

---

#### Deleting linter:

<details>
 <summary><code>POST</code> <code><b>/</b></code> <code>delete</code></summary>

##### Body

| key    | type     | description                   |
|--------|----------|-------------------------------|
| `ip`   | `String` | IP address of the linter to delete |

##### Response 200, JSON:

| key       | type      | description                              |
|:----------|:----------|:-----------------------------------------|
| `status`  | `String`  | Result of operation, `ok` for successful deletion |

##### Response 400, JSON:

| key       | type      | description                              |
|:----------|:----------|:-----------------------------------------|
| `status`  | `String`  | Result of operation, `error` for invalid request parameter |
| `message` | `String`  | Detailed explanation of the error       |

##### Response 500, JSON:

| key       | type      | description                              |
|:----------|:----------|:-----------------------------------------|
| `status`  | `String`  | Result of operation, `error` for internal server error |
| `message` | `String`  | Detailed explanation of the error       |

</details>

---

#### Initializing update to new version:

<details>
 <summary><code>POST</code> <code><b>/</b></code> <code>init-update</code></summary>

##### Body

| key       | type     | description                                    |
|-----------|----------|------------------------------------------------|
| `lang`    | `String` | Language for which to initiate the update       |
| `version` | `String` | Target version to update to                     |

##### Response 200, JSON:

| key       | type      | description                              |
|:----------|:----------|:-----------------------------------------|
| `status`  | `String`  | Result of operation, `ok` for successful initiation of update |

##### Response 400, JSON:

| key       | type      | description                              |
|:----------|:----------|:-----------------------------------------|
| `status`  | `String`  | Result of operation, `error` for invalid request parameters |
| `message` | `String`  | Detailed explanation of the error       |

##### Response 500, JSON:

| key       | type      | description                              |
|:----------|:----------|:-----------------------------------------|
| `status`  | `String`  | Result of operation, `error` for internal server error |
| `message` | `String`  | Detailed explanation of the error       |

</details>

---

#### Progressing to next update step:

<details>
 <summary><code>POST</code> <code><b>/</b></code> <code>update</code></summary>

##### Body

| key       | type     | description                                    |
|-----------|----------|------------------------------------------------|
| `lang`    | `String` | Language for which to perform the update       |

##### Response 200, JSON:

| key       | type      | description                              |
|:----------|:----------|:-----------------------------------------|
| `status`  | `String`  | Result of operation, `ok` for successful update |

##### Response 400, JSON:

| key       | type      | description                              |
|:----------|:----------|:-----------------------------------------|
| `status`  | `String`  | Result of operation, `error` for invalid request parameters |
| `message` | `String`  | Detailed explanation of the error       |

##### Response 500, JSON:

| key       | type      | description                              |
|:----------|:----------|:-----------------------------------------|
| `status`  | `String`  | Result of operation, `error` for internal server error |
| `message` | `String`  | Detailed explanation of the error       |

</details>

---

#### Rolling back to previous update step:

<details>
 <summary><code>POST</code> <code><b>/</b></code> <code>rollback</code></summary>

##### Body

| key       | type     | description                                    |
|-----------|----------|------------------------------------------------|
| `lang`    | `String` | Language for which to perform the rollback     |

##### Response 200, JSON:

| key       | type      | description                              |
|:----------|:----------|:-----------------------------------------|
| `status`  | `String`  | Result of operation, `ok` for successful rollback |

##### Response 400, JSON:

| key       | type      | description                              |
|:----------|:----------|:-----------------------------------------|
| `status`  | `String`  | Result of operation, `error` for invalid request parameters |
| `message` | `String`  | Detailed explanation of the error       |

##### Response 500, JSON:

| key       | type      | description                              |
|:----------|:----------|:-----------------------------------------|
| `status`  | `String`  | Result of operation, `error` for internal server error |
| `message` | `String`  | Detailed explanation of the error       |

</details>

---

#### Getting status of currently running linters

<details>
 <summary><code>GET</code> <code><b>/</b></code> <code>status</code></summary>

###### Body
Request body is empty for that request.

##### Response 200, JSON
| key       | type      | description                              |
|:----------|:----------|:-----------------------------------------|
| `linters`  | `JSON[]`  | Array of JSON objects describing currently running linters |

Each JSON object has one key of type `String` - the IP of the linter. Value for that key is another JSON object with the following fields:

| key       | type      | description                              |
|:----------|:----------|:-----------------------------------------|
| `is_healthy`  | `Boolean`  | Health status of the linter |
| `version` | `String` | Version of the linter |
| `lang` | `String` | Language that can be linted |
| `request_count` | `Integer` | Number of requests that were served by the linter |

##### Example response
```json
{
    "linters": [
        {
            "127.0.0.1": {
                "is_healthy": true,
                "version": "2.0",
                "lang": "java",
                "request_count": 5
            },
            "127.0.0.2": {
                "is_healthy": false,
                "version": "1.0",
                "lang": "python",
                "request_count": 1
            }
        }
    ]
}
```


</details>

---



## Load Balancer:

---

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

---

#### Adding linter to load balancing queue:

<details>
 <summary><code>POST</code> <code><b>/</b></code> <code>add</code></summary>

##### Body

| key         | type     | description               |
 |-------------|----------|---------------------------|
| `lang`      | `String` | Language of linter to add |
| `version`   | `String` | Version of linter to add  |
| `uri`       | `String` | URI of linter to add      |
| `secretKey` | `String` | Key for authorization     |

##### Responses

| http code | description                           |
 |-----------|---------------------------------------|
| `200`     | Addition comleted                         |
| `400`     | Language not supported or invalid URI |
| `403`     | Auth failed                           |

</details>


---

#### Removing linter from load balancing queue:

<details>
 <summary><code>POST</code> <code><b>/</b></code> <code>remove</code></summary>

##### Body

| key         | type     | description             |
 |-------------|----------|-------------------------|
| `uri`       | `String` | URI of linter to remove |
| `secretKey` | `String` | Key for authorization   |

##### Responses

| http code | description    |
 |-----------|----------------|
| `200`     | Removal copmpleted |
| `400`     | Invalid URI    |
| `403`     | Auth failed    |

</details>

---

#### Updating load balancing ratio between version:

<details>
 <summary><code>POST</code> <code><b>/</b></code> <code>ratio</code></summary>

##### Body

| key            | type     | description                                                                                           |
 |----------------|----------|-------------------------------------------------------------------------------------------------------|
| `lang`         | `String` | Lang of linters                                                                                       |
| `versionRatio` | `Dict`   | {"v1": Int, "v2":Int, ...} Any number of keys as long as their values sum up to arbitrary total ratio |
| `secretKey`    | `String` | Key for authorization                                                                                 |

##### Responses

| http code | description                                 |
 |-----------|---------------------------------------------|
| `200`     | Ratio updated                               |
| `400`     | Wrong total ratio or language not supported |
| `403`     | Auth failed                                 |

</details>



--- 

#### Checking load balancer status:

<details>
 <summary><code>GET</code> <code><b>/</b></code> <code>health</code></summary>

##### Response 200

</details>

## Linters:

---

#### Linting code:

<details>
 <summary><code>POST</code> <code><b>/</b></code> <code>lint</code></summary>

##### Request body:

| key    | type     | description             |
 |--------|----------|-------------------------|
| `code` | `String` | URI of linter to remove |

##### Response 200, JSON:

| key       | type      | description              |
 |-----------|-----------|--------------------------|
| `result`  | `Boolean` | Linting passed or failed |
| `details` | `String`  | Message for user         |

</details>

---

#### Checking linter status:

<details>
 <summary><code>GET</code> <code><b>/</b></code> <code>health</code></summary>

##### Response 200, JSON:

| key            | type     | description                         |
 |----------------|----------|-------------------------------------|
| `version`      | `String` | Version of linter                   |
| `language`     | `String` | Language of linter                  |
| `requestCount` | `Int`    | Number of requests served by linter |

</details>

