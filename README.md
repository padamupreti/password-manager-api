# password-manager-api

Password manager API built with [FastAPI](https://fastapi.tiangolo.com/ 'FastAPI Website')

## Requirements

-   [Python](https://python.org/downloads/ 'Download Python') (with pip)

## Setup

To install dependencies, navigate to project root in the terminal and run:

```
pip install -r requirements.txt
```

This project uses a [PostgreSQL](https://www.postgresql.org/) database. Json Web Tokens are used for
authentication and user info is encrypted. Here is a sample `.env` file to be created at project root for the
application to work:

```
DB_USERNAME=username
DB_PASSWORD=password
DB_HOST=127.0.0.1
DB_PORT=5432
DB_NAME=test
JWT_SECRET_KEY=cbf8443be260a54431f3bb23152f15a4666ab07931a85cf857f24786ce518423
JWT_ALGORITHM=HS256
JWT_TOKEN_EXPIRE_MINUTES=15
PW_ENCRYPTION_KEY='6w0TxKyjm494NwqLW0bXXbllvv3V89SrpfT_Y6ieVc8='
```

`JWT_SECRET_KEY` can be generated with the command `openssl rand -hex 32` in the terminal.

`PW_ENCRYPTION_KEY` can be generated using `generate_key()` method of Fernet class from the `cryptography`
module which should have installed during the installation of requirements.

```python
>>> from cryptography.fernet import Fernet
>>> Fernet.generate_key().decode()
'EFdMO1zHYDVWphIFTM-YpEYkF26Bb19sV2QQnvFGjbk='
```

After setting the environment variables, run the following from project root to start the API server:

```
uvicorn app.main:app
```

## Test Usage

The `/docs` endpoint provides a simple breakdown of all routes based on project code itself.
The API can be understood and interacted with using this interface. After creating a user, the `Authorize`
button can be used for logging in and accessing all protected routes from this interface.

![Screenshot](https://i.imgur.com/uexmNAS.png)
