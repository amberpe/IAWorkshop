sudo yum install python3.11 -y
python3.11 -m ensurepip --upgrade
sam build
sam deploy --no-confirm-changeset