# Fygo Transactions API 


## What could have been improved ?
* We should not store any kind of credentials to settings.py but since we are not using any creds this is not applicable.
* According to The Twelve Factor App methodology we should Store config in the environment.
* We can use Sphinx Documentation. Sphinx is a tool to easily create intelligent and beautiful documentation. 
  It lets you generate Python documentation from existing reStructuredText and export documentation in formats like HTML.  
* Authentication can be added using oauth_toolkit provided by django.
* Better routing of urls can be done using Default Routers in DRF.
* I have used SQLite DB for now but PostgresSQL can be used since SQLite can't handle more concurrent requests.
* I have added a few extra functionalities to django admin but more customization could have done.
* I would have added documentation for deploying our DB as well.

## How to set up project.
* First clone the repository from https://github.com/ygsh0816/fygo
* Considering you have created a virtual environment you need to install all requirements using below command.  
```bash
cd fygo/source
pip install -r requirements.txt
```
* Once all requirements are installed we need to make migrations and migrate them to our database. Please run the below commands in the same order.
Since we are using a custom user model, so the app having the user model will be migrated first.
```bash
python manage.py makemigrations transactions
python manage.py migrate transactions
python manage.py migrate
```
* Once all the migrations are migrated we need to create a superuser to access our admin using following command.
```commandline
python manage.py createsuperuser
```
* Above command will prompt you to give admin username and password. 
* Now you can run your project by the following command and APIs will be accessible on the below shared URLs.
```commandline
python manage.py runserver
```
# API Documentation
Name: Create Transaction  
API Method - POST  
URL:http://localhost:8000/create-transaction/  
Body Type: (json)  
data = {  
  "user": 2,  
  "transaction_type": 1,  
  "transaction_amount": -100,  
  "transaction_id": 101010091  
}  

Name: Get All Users   
URL: http://localhost:8000/get-all-users/  

Name: Get Transactions  
URL: http://localhost:8000/get-transactions/  

Name: Get User Operations  
URL: http://localhost:8000/get-operations/1/  

NAME: Create a Withdrawal  
API Method :POST  
http://localhost:8000/withdraw/1/  
Body Type: (json)  
data = {  
  "transaction_amount": 0  
}  

NAME: Get Available balance  
URL: http://localhost:8000/get-my-balance/1/  


NAME: Register User  
API Method :POST    
URL: http://localhost:8000/register/  
Body Type: (json)  
Data = {  
  "firstname": "test1",  
  "lastname": "data",  
  "email": "test1@data.com",  
  "password": "12345678"  
}


## How to deploy it to AWS EC2 using AWS ElasticBeanStalk.
### What is Elastic Beanstalk?
Amazon Web Services (AWS) comprises over one hundred services, 
each of which exposes an area of functionality.
With Elastic Beanstalk, you can quickly deploy and manage applications in the
AWS Cloud without having to learn about the infrastructure that runs
those applications. Elastic Beanstalk reduces management 
complexity without restricting choice or control. 
You simply upload your application, and Elastic Beanstalk automatically
handles the details of capacity provisioning, load balancing, scaling,
and application health monitoring.
### Deploying a Django application to Elastic Beanstalk
* First We need to have an AWS account.
* We should have below prerequisites installed.
  1. Python 3.6 or later
  2. pip
  3. virtualenv
  4. awsebcli
  
* Create a directory named .ebextensions inside your project using below command.
```commandline
(eb-virtualenv) ~/fygo$ mkdir .ebextensions
```
* (eb-virtualenv) indicates that you have activated your environment.
* In the .ebextensions directory, add a configuration file named django.config with the following text.
```editorconfig
option_settings:
  aws:elasticbeanstalk:container:python:
    WSGIPath: fygo.wsgi:application
```
### Deploy your site with the EB CLI
* By now You should've added everything you need to deploy your application on Elastic Beanstalk.
* Initialize your EB CLI repository with the eb init command.
```commandline
eb init -p python-3.8 fygo-app
```
* The above command creates an application named fygo-app. It also configures your local repository to create environments with the latest Python 3.6 platform version.
*  Run eb init again to configure a default key pair so that you can use SSH to connect to the EC2 instance running your application.
```commandline
$ eb init
Do you want to set up SSH for your instances?
(y/n): y
Select a keypair.
1) my-keypair
2) [ Create new KeyPair ]
```
* Create an environment and deploy your application to it with eb create.
```commandline
eb create django-env
```
* When the environment creation process completes, find the domain name of your new environment by running eb status
```commandline
$ eb status
Environment details for: django-env
  Application name: django-tutorial
  ...
  CNAME: eb-django-app-dev.elasticbeanstalk.com
  ...
```
* Your environment's domain name is the value of the CNAME property.
* Open the settings.py file in the fygo directory. Locate the ALLOWED_HOSTS setting, and then add your application's domain name that you found in the previous step to the setting's value. If you can't find this setting in the file, add it to a new line.
* Save the file, and then deploy your application by running eb deploy. When you run eb deploy, the EB CLI bundles up the contents of your project directory and deploys it to your environment.
```commandline
$ eb deploy
```
* When the environment update process completes, open your website with eb open.
```commandline
$ eb open
```
* This opens a browser window using the domain name created for your application. You should see the same Django website that you created and tested locally.

