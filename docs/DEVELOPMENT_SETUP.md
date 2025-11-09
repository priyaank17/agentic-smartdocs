# Development Environment Setup

## Prerequisites

- Python3
  - Install dependencies in a python virtual environment
    - For Linux Based machines

      ```bash
        chmod 777 ./scripts/start.sh
        ./scripts/start.sh
      ```

    - For windows

      ```bat
      call python -m venv .venv
      call .venv/Scripts/activate
      call python -m pip install --upgrade pip pipenv
      call python -m pipenv install --dev --pre
      ```

  - Enable python virtual environment
    - For Linux Based machines

      ```bash
        source .venv/bin/activate
      ```

    - For Windows

      ```bat
        .venv/Scripts/activate
      ```

- NodeJS
  - Install NodeJS dependencies

  ```bash
    npm i
  ```

- VSCode Extensions
  - [Code Spell Checker](https://marketplace.visualstudio.com/items?itemName=streetsidesoftware.code-spell-checker)
  - [Cypher Query Language](https://marketplace.visualstudio.com/items?itemName=jakeboone02.cypher-query-language)
  - [DotEnv](https://marketplace.visualstudio.com/items?itemName=mikestead.dotenv)
  - [EditorConfig for VS Code](https://marketplace.visualstudio.com/items?itemName=EditorConfig.EditorConfig)
  - [Flake8](https://marketplace.visualstudio.com/items?itemName=ms-python.flake8)
  - [Even Better TOML](https://marketplace.visualstudio.com/items?itemName=tamasfe.even-better-toml)
  - [Edit CSV](https://marketplace.visualstudio.com/items?itemName=janisdd.vscode-edit-csv)
  - [ESLint](https://marketplace.visualstudio.com/items?itemName=dbaeumer.vscode-eslint)
  - [GitLens](https://marketplace.visualstudio.com/items?itemName=eamodio.gitlens)
  - [HTTP Client](https://marketplace.visualstudio.com/items?itemName=mkloubert.vscode-http-client)
  - [Liver Server](https://marketplace.visualstudio.com/items?itemName=ritwickdey.LiveServer)
  - [Markdownlint](https://marketplace.visualstudio.com/items?itemName=DavidAnson.vscode-markdownlint)
  - [Pipenv Scripts](https://marketplace.visualstudio.com/items?itemName=FedericoVarela.pipenv-scripts)
  - [Word Count](https://marketplace.visualstudio.com/items?itemName=ms-vscode.wordcount)
  - [Pylint](https://marketplace.visualstudio.com/items?itemName=ms-python.pylint)

## Set permission to scripts

```bash
  chmod 777 ./scripts/*
```

## Install VSCode extensions

```bash
  ./scripts/install_vscode_extensions.sh
```

## Install AWS Lambda RIE (Runtime Interface Emulator)

[Reference: https://github.com/aws/aws-lambda-runtime-interface-emulator](https://github.com/aws/aws-lambda-runtime-interface-emulator)

```bash
mkdir -p ~/.aws-lambda-rie && curl -Lo ~/.aws-lambda-rie/aws-lambda-rie \
https://github.com/aws/aws-lambda-runtime-interface-emulator/releases/latest/download/aws-lambda-rie \
&& chmod +x ~/.aws-lambda-rie/aws-lambda-rie
```

## Create .env file

```env
SYMBOL_DETECTOR_CORE_URL = "..."
PYTHONPATH=.
SANDBOX_ENV=true
DO_NOT_USE_ASM=true
AWS_DEFAULT_REGION=us-west-2
LAMBDA_TASK_ROOT=.
DOCKER_DEFAULT_PLATFORM=linux/x86_64
EXTRACT_TABLE_LAMBDA_ARN=arn:aws:lambda:us-west-2:461906100116:function:artisan-table-detection-core
```

## Running application on your machine

### Build the docker image

```bash
  ./scripts/build.sh
```

or

```bash
  docker build --platform linux/x86_64 -t artisan-symbol-detector-core .
```

### Run the Docker image

The below command runs the image as a container and starts up an endpoint locally at [http://localhost:9000/2015-03-31/functions/function/invocations](http://localhost:9000/2015-03-31/functions/function/invocations).

run with AWS Lambda RIE (Runtime Interface Emulator)

```bash
  ./scripts/run.sh
```

or with out RIE

```bash
  docker run -p 9000:8080 artisan-symbol-detector-core:latest
```

### Watch the logs

```bash
  ./scripts/log.sh
```

### Run All the above commands together

Use this command when you make a change in the code and want to rebuild the image, run the container and watch the logs

```bash
 ./scripts/dev.sh
```

### Important Note. If using API gateway, response from lambda must be of this format

```{
    "cookies" : ["cookie1", "cookie2"],
    "isBase64Encoded": true|false,
    "statusCode": httpStatusCode,
    "headers": { "headername": "headervalue", ... },
    "body": "Hello from Lambda!"
}```
