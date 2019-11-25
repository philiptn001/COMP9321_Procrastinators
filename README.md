# COMP9321_Procrastinators
Assignment 2 for COMP9321 Group Procrastinator
Providing a Flask Restplus Analytical Service design to assist a user in analysing relationship between cars /brands and their value new and resale.

## Setup
### Backend setup
To set up the development environment, you are required Python 3 and pip\
    1. Install `python3.7.X.` (pip comes by default after python3.4)\
    2. install virtual environment `python3 -m venv venv` if windows `py -3 -m venv venv`\
    3. Activate virtual environment `. venv/bin/activate` if windows `> venv\Scripts\activate`\
    4. Install using `pip install -r requirements.txt` \
    6. Run `python app.py`\
    Back end api can be accessed by default using `localhost:9000` (port is defaulted to 9000)

# client setup

## Project setup
```
npm install
```

### Compiles and hot-reloads for development
```
npm run serve
```

### Compiles and minifies for production
```
npm run build
```

### Run your tests
```
npm run test
```

### Lints and fixes files
```
npm run lint
```

### Customize configuration
See [Configuration Reference](https://cli.vuejs.org/config/).


# User Logins for authentications
##### sample user login
username: user\
password: password

##### sample admin
username: admin\
password: abc123

##### Flask monitoring dashboard
access via /dashboard endpoint
username: admin\
password: admin
