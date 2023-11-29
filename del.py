from fabric import Connection
import os

# Server configuration
server = '3.86.104.25'
pem_file_path = 'ncsubuntu230522.pem'

# Connect to the server using SSH
key = os.path.expanduser(pem_file_path)
conn = Connection(host=server, user='ubuntu', connect_kwargs={'key_filename': key})

def delete_deployment_files():
    # Repository configuration
    repo_destination = '/home/ubuntu/ncsjobsbe'

    # Nginx and Gunicorn configuration files
    nginx_config_file = '/etc/nginx/sites-available/myproject'
    gunicorn_service_file = '/etc/systemd/system/gunicorn.service'
    gunicorn_socket_file = '/etc/systemd/system/gunicorn.socket'

    # Delete deployment files
    try:
        # Remove repository directory
        conn.run(f'sudo rm -rf {repo_destination}')

        # Delete Nginx and Gunicorn configuration files
        conn.sudo(f'sudo rm -f {nginx_config_file}')
        conn.sudo(f'sudo rm -f {gunicorn_service_file}')
        conn.sudo(f'sudo rm -f {gunicorn_socket_file}')

        print('Deployment files and configuration files deleted successfully.')
    except Exception as e:
        print(f'Error occurred while deleting deployment files: {str(e)}')

    # Remove the ncsjobsbe directory
    try:
        conn.run('sudo rm -rf /home/ubuntu/ncsjobsbe')
        print('ncsjobsbe directory removed successfully.')
    except Exception as e:
        print(f'Error occurred while removing ncsjobsbe directory: {str(e)}')

def uninstall_packages():
    try:
        packages = [
            'fabric',
            'django-restframework',
            'sib-api-v3-sdk'
        ]

        for package in packages:
            conn.run(f'pip uninstall -y {package}')

        print('Packages uninstalled successfully.')
    except Exception as e:
        print(f'Error occurred while uninstalling packages: {str(e)}')

def remove_system_packages():
    try:
        system_packages = [
            'python3-venv',
            'python3-dev',
            'libpq-dev',
            'postgresql',
            'postgresql-contrib',
            'nginx',
            'curl'
        ]

        for package in system_packages:
            conn.sudo(f'apt-get remove -y {package}')

        print('System packages uninstalled successfully.')
    except Exception as e:
        print(f'Error occurred while uninstalling system packages: {str(e)}')

def main():
    print(f'Connecting to {server}...')
    conn.open()

    try:
        delete_deployment_files()
        uninstall_packages()
        remove_system_packages()
    except Exception as e:
        print(f'An error occurred: {str(e)}')
    finally:
        conn.close()

if __name__ == '__main__':
    main()
