# Distributed Linters API:

## Machine Manager:

    TODO

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

| key         | type     | description              |
 |-------------|----------|--------------------------|
| `lang`      | `String` | lang of linter to add    |
| `version`   | `String` | version of linter to add |
| `uri`       | `String` | URI of linter to add     |
| `secretKey` | `String` | Key for authorization    |

##### Response 200

</details>


---

#### Removing linter from load balancing queue:

<details>
 <summary><code>POST</code> <code><b>/</b></code> <code>remove</code></summary>

##### Body

| key         | type     | description             |
 |-------------|----------|-------------------------|
| `uri`       | `String` | URI of linter to delete |
| `secretKey` | `String` | Key for authorization   |

##### Response 200

</details>

---

#### Updating load balancing ratio between version:

<details>
 <summary><code>POST</code> <code><b>/</b></code> <code>ratio</code></summary>

##### Body

| key            | type     | description                                                                                           |
 |----------------|----------|-------------------------------------------------------------------------------------------------------|
| `lang`         | `String` | lang of linters                                                                                       |
| `versionRatio` | `Dict`   | {"v1": Int, "v2":Int, ...} Any number of keys as long as their values sum up to arbitrary total ratio |
| `secretKey`    | `String` | Key for authorization                                                                                 |

##### Response 200

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
| `code` | `String` | URI of linter to delete |

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

