# Linters

## Basic
Checks if assignments are surrounded by spaces
#### Build
`docker build --build-arg LINTER_PATH=basic -t linter:1.0 -f Dockerfile .`
#### Run Java
`docker run -d -p 8080:80 -e LANGUAGE=java linter:1.0`
#### Run Python
`docker run -d -p 8080:80 -e LANGUAGE=python linter:1.0`


## Slow
Basic + sleeps for specified amount of time before returning the result
#### Build
`docker build --build-arg LINTER_PATH=slow -t linter:1.1 -f Dockerfile .`
#### Run Java
`docker run -d -p 8080:80 -e LANGUAGE=java -e PROCESSING_TIME=5 linter:1.1`
#### Run Python
`docker run -d -p 8080:80 -e LANGUAGE=python -e PROCESSING_TIME=5 linter:1.1`

## Broken
Basic + enters endless loop after receiving empty code
#### Build
`docker build --build-arg LINTER_PATH=broken -t linter:1.2 -f Dockerfile .`
#### Run Java
`docker run -d -p 8080:80 -e LANGUAGE=java linter:1.2`
#### Run Python
`docker run -d -p 8080:80 -e LANGUAGE=python linter:1.2`

## Extended
Basic + checks if code ends with empty line
#### Build
`docker build --build-arg LINTER_PATH=extended -t linter:2.0 -f Dockerfile .`
#### Run Java
`docker run -d -p 8080:80 -e LANGUAGE=java linter:2.0`
#### Run Python
`docker run -d -p 8080:80 -e LANGUAGE=python linter:2.0`