# plumnet

  [![License](https://img.shields.io/static/v1?label=License&message=MIT&color=blue&?style=plastic&logo=appveyor)](https://opensource.org/license/MIT)



## Table Of Content

- [Description](#description)

- [Installation](#installation)
- [Usage](#usage)
- [Contributing](#contribution)
- [Tests](#tests)
- [GitHub](#github)
- [Contact](#contact)
- [License](#license)




![GitHub repo size](https://img.shields.io/github/repo-size/ManikTzyyy/plumnet?style=plastic)

  ![GitHub top language](https://img.shields.io/github/languages/top/ManikTzyyy/plumnet?style=plastic)



## Description

  Motivation
The motivation behind this project came from the challenges often faced in managing FTTH networks, specifically the difficulty of monitoring ONT devices and the repetitive configuration tasks that frequently lead to human errors.

Why did you build this project?
I built this project to provide a more efficient and centralized way to manage FTTH networks by creating a single dashboard that integrates network automation and monitoring.

What problem does it solve?
This project addresses two major issues:

The lack of visibility in monitoring ONT devices in FTTH networks.

The repetitive and error-prone manual configuration process.
By implementing a Django-based dashboard integrated with GenieACS, along with automation for device configuration via SSH (e.g., Mikrotik), the system minimizes human error and streamlines network operations.

What did you learn?
Through this project, I gained a deeper understanding of how FTTH networks and OLT devices operate. I also learned how to develop web applications using the Django framework, integrate third-party systems such as GenieACS, and establish communication between clients and devices using SSH.





## Package
Django==4.2.7
django_extensions==4.1
paramiko==3.3.1
RouterOS-api==0.21.0
librouteros==3.4.1
netmiko==4.6.0
python-decouple==3.8
waitress==3.0.2
requests==2.32.5
django-apscheduler==0.7.0
gunicorn==23.0.0
whitenoise==6.9.0
waitress==3.0.2





## Installation

git clone https://github.com/ManikTzyyy/plumnet
cd plumnet
pip install -r requirements.txt
python manage.py collectstatic
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser #fill the data
python manage.py runserver

Open http://127.0.0.1:8000/





plumnet is built with the following tools and libraries: <ul><li>Django</li><li>Netmiko</li><li>Chart.js</li><li>sweetaler2</li><li>leaflet.js</li></ul>





## Usage
 
hehe





## Contribution
 
fork and make pull request😁





## Tests
 
test






## GitHub

<a href="https://github.com/ManikTzyyy"><strong>ManikTzyyy</a></strong>



<p>Visit my website: <strong><a href="https://manik-porto.vercel.app/">My Portofolio Website</a></strong></p>





## Contact

Feel free to reach out to me on my email:
ktmanikyogantara@gmail.com





## License

[![License](https://img.shields.io/static/v1?label=Licence&message=MIT&color=blue)](https://opensource.org/license/MIT)


