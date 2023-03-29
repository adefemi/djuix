readme_content = """
# Djuix.io - README.md

This README provides an overview of the project setup and instructions on how to run the server and create a super admin for your Djuix project.

## Overview

This project uses two shell scripts to streamline the setup process:

1. `start_server.sh`: Starts the Django development server after activating the virtual environment and installing the required dependencies from the `requirements.txt` file.
2. `create_super_admin.sh`: Creates a super admin user for your Django project, after activating the virtual environment and installing the required dependencies from the `requirements.txt` file.

## Requirements

- Python 3.x
- Django
- pip 3.x
- Virtual environment

## Setup

1. A virtual environment folder is created by default, ensure it's always activated
2. To use the shell scripts, you must be in the root directory.
3. Ensure dependecies are installed, you can double check by doing `pip3 install -r requirements.txt` in the project directory (stage 1 must be fulfilled).

## Usage

### Start the Django server

To start the Django server, run the following command in the terminal:

```bash
./start_server.sh
```

This script activates the virtual environment, changes the directory to the Django project folder, installs dependencies, and starts the server.

### Create a super admin

To create a super admin for your Django project, run the following command in the terminal:

```bash
./create_super_admin.sh
```

This script activates the virtual environment, changes the directory to the Django project folder, installs dependencies, and creates a super admin by running the `createsuperuser` management command.

## Troubleshooting

Ensure that both shell scripts (`start_server.sh` and `create_super_admin.sh`) have executable permissions. You can set the permissions by running the following command:

```bash
chmod +x start_server.sh create_super_admin.sh
```

If you encounter any issues, please consult the [Django documentation](https://docs.djangoproject.com/) for further guidance.

At this point, what you have with you is mainly a django project.
"""
