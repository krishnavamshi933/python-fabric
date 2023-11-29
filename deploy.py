import os
from fabric import Connection
from invoke.exceptions import UnexpectedExit

# Server configuration
server = '3.144.18.239'
pem_file_path = '/home/kali/krish-test.pem'

# Repository configuration
repo_url = 'https://github.com/krishnavamshi933/myprojectdir.git'
repo_destination = '/home/ubuntu/myprojectdir'

# Function to activate the virtual environment and change directory
def activate_virtualenv_and_cd(connection, project_path, virtualenv_path):
    with connection.cd(project_path):
        connection.run(f'source {virtualenv_path}/bin/activate')

# Function to install project dependencies
def install_dependencies(connection, project_path):
    with connection.cd(project_path):
        connection.sudo('apt-get update')
        connection.sudo('apt-get install -y python3-venv python3-dev libpq-dev postgresql postgresql-contrib nginx curl')
        connection.run('python3 -m venv myprojectenv')
        connection.run('source myprojectenv/bin/activate && pip install -r requirements.txt')

# Function to clone the repository
def clone_repository(connection, repo_url, repo_destination):
    connection.run(f'git clone {repo_url} {repo_destination}')

# Function to configure Gunicorn
def configure_gunicorn(connection, project_path):
    gunicorn_service = '''
    [Unit]
    Description=Gunicorn service for myproject
    After=network.target

    [Service]
    User=ubuntu
    Group=www-data
    WorkingDirectory={project_path}
    ExecStart={virtualenv_path}/bin/gunicorn --access-logfile - --workers 3 --bind unix:{project_path}/myproject.sock myproject.wsgi:application

    [Install]
    WantedBy=multi-user.target
    '''.format(project_path=project_path, virtualenv_path=os.path.join(project_path, 'myprojectenv'))

    connection.sudo('echo "{}" | sudo tee /etc/systemd/system/gunicorn.service'.format(gunicorn_service))
    connection.sudo('sudo systemctl daemon-reload')
    connection.sudo('sudo systemctl enable gunicorn')
    connection.sudo('sudo systemctl start gunicorn')

# Function to configure Nginx
def configure_nginx(connection, project_path):
    nginx_config = '''
    server {{
        listen 80;
        server_name your_domain.com;
    
        location / {{
            include proxy_params;
            proxy_pass http://unix:{project_path}/myproject.sock;
        }}
    }}
    '''.format(project_path=project_path)

    connection.sudo('echo "{}" | sudo tee /etc/nginx/sites-available/myproject'.format(nginx_config))
    connection.sudo('sudo ln -s /etc/nginx/sites-available/myproject /etc/nginx/sites-enabled/')
    connection.sudo('sudo systemctl restart nginx')

def main():
    # Connect to the server using SSH
    key = os.path.expanduser(pem_file_path)
    with Connection(server, user='ubuntu', connect_kwargs={'key_filename': key}) as conn:
        print(f'Deploying to {server}')

        try:
            # Clone the repository
            clone_repository(conn, repo_url, repo_destination)

            # Activate the virtual environment and change directory
            activate_virtualenv_and_cd(conn, repo_destination, 'myprojectenv')

            # Install project dependencies
            install_dependencies(conn, repo_destination)

            # Configure Gunicorn
            configure_gunicorn(conn, repo_destination)

            # Configure Nginx
            configure_nginx(conn, repo_destination)

        except UnexpectedExit as e:
            print(f'Error: {e}')

if __name__ == '__main__':
    main()
