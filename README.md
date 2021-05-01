# Bulk-Mailer Using Flask & Sendgrid API ⚡️
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;

## Overview of the Topic:

Bulk Mailer is a Mail Client web application that can be used by organizations to send bulk emails for different groups of subscribers. In general, a bulk email service is a company that allows its customers to send mass email messages to multiple lists of recipients at a specified time. With this service, you can send a single message to thousands of people on a mailing list or a personalized email to each address on a list that can be of any size.
Today, marketers prefer to use bulk email services to deliver important messages with minimal effort. Unlike junk emails sent without the recipients’ permission, bulk emails are legal marketing campaigns since the recipients subscribe to receive them. However, if bulk email marketing is not properly managed, users may consider it spam, and consequently, it may hurt the sender’s reputation.

Most of the bulk email service providers price their offerings based on the number and frequency of the emails one wants to send. But, after registering with Bulk Mailer, you can send bulk emails free of charge!

Our application has a feature-rich email builder that lets you build beautiful and responsive emails in minutes. It supports adding and using different email templates as well which ensures consistency and reduced human efforts.

## Scope and Importance:

Bulk mailing is an incredibly useful tool for any business as it aims to promote a business or sell goods or even develop relationships. Sending thousands or tens of thousands of messages to even just a couple of email addresses would be draining due to the amount of time and effort required. Moreover, the cost of running such a campaign would not be sustainable for any business. Using a bulk email service is cheaper, faster, and much more convenient.

This service is a prime example of how you can utilize technology to enhance traditional marketing methods. Time-saving is, of course, one of the big advantages of bulk mailing, but there are plenty of other benefits too like the ability to spark engagement. More businesses are now seeing the benefits of combining direct mail campaigns with digital marketing methods.


[![contributions welcome](https://img.shields.io/badge/contributions-welcome-brightgreen.svg?style=flat)](https://github.com/vigneshshettyin/Bulk-Mailer/issues)
[![Forks](https://img.shields.io/github/forks/vigneshshettyin/Bulk-Mailer.svg?logo=github)](https://github.com/vigneshshettyin/Bulk-Mailer/network/members)
[![Stargazers](https://img.shields.io/github/stars/vigneshshettyin/Bulk-Mailer.svg?logo=github)](https://github.com/vigneshshettyin/Bulk-Mailer/stargazers)
[![Issues](https://img.shields.io/github/issues/vigneshshettyin/Bulk-Mailer.svg?logo=github)](https://github.com/vigneshshettyin/Bulk-Mailer/issues)
[![MIT License](https://img.shields.io/github/license/vigneshshettyin/Bulk-Mailer.svg?style=flat-square)](https://github.com/vigneshshettyin/Bulk-Mailer/blob/master/LICENSE)
![GitHub watchers](https://img.shields.io/github/watchers/vigneshshettyin/Bulk-Mailer)
![GitHub contributors](https://img.shields.io/github/contributors/vigneshshettyin/Bulk-Mailer)


Feel free to use it as-is or customize it as much as you want.

But if you want to **Contribute** and make this much better for other developer have a look at [Issues](https://github.com/vigneshshettyin/Bulk-Mailer/issues).


If you created something awesome and want to contribute then feel free to open Please don't hesitate to open an [Pull Request](https://github.com/vigneshshettyin/Bulk-Mailer/pulls).

## Tech Stack:
<img alt="CSS3" src="https://img.shields.io/badge/css3%20-%231572B6.svg?&style=for-the-badge&logo=css3&logoColor=white"/> 	<img alt="HTML5" src="https://img.shields.io/badge/html5%20-%23E34F26.svg?&style=for-the-badge&logo=html5&logoColor=white"/> <img alt="Python" src="https://img.shields.io/badge/python%20-%2314354C.svg?&style=for-the-badge&logo=python&logoColor=white"/> <img alt="JavaScript" src="https://img.shields.io/badge/javascript%20-%23323330.svg?&style=for-the-badge&logo=javascript&logoColor=%23F7DF1E"/> <img alt="Bootstrap" src="https://img.shields.io/badge/Bootstrap-563D7C?style=for-the-badge&logo=bootstrap&logoColor=white"/> <img alt="jQuery" src="https://img.shields.io/badge/jQuery-0769AD?style=for-the-badge&logo=jquery&logoColor=white"/> <img alt="Flask" src="https://img.shields.io/badge/Flask-000000?style=for-the-badge&logo=flask&logoColor=white"/> <img alt="PostgreSQL" src="https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white"/> <img alt="SQLite" src="https://img.shields.io/badge/SQLite-07405E?style=for-the-badge&logo=sqlite&logoColor=white"/> <img alt="Heroku" src="https://img.shields.io/badge/Heroku-430098?style=for-the-badge&logo=heroku&logoColor=white"/>


## Getting Started 🚀

## How To Use 🔧

**1.** Clone this repository to your local environment
 ```shell
$ git clone https://github.com/vigneshshettyin/Bulk-Mailer.git
```

**2.** Change directory into the cloned repository  
 ```shell
$ cd Bulk-Mailer
```

**3.** Setup virtual environment
 ```shell
$ py -m venv env
For Windows:-
$ .\env\Scripts\activate
For Linux:-
$ source env/Scripts/activate
```

**4.** Install requirements from requirements.txt  
 ```shell
$ pip3 install -r requirements.txt
```

**5.** Create a new file called `.env` and copy all the data from `.env.sample` to `.env` as it is.

**6.** Run the development server
 ```shell
$ python3 app.py
```
or
 ```shell
$ flask run
```

**7**.Now fire up your favorite web browser and go to http://127.0.0.1:5000/
 You will find the application running there.

**Note : If your project root directory doesn't contains `bulkmailer.db` then Run this on your terminal: 👇**

For Windows: 💾
```
$ py or python
>>>from app import db
>>>db.create_all()
>>>exit()
```

For Linux: 👨‍💻
```
$ python3
>>>from app import db
>>>db.create_all()
>>>exit()
```
## Lint and Format 📜

- We use [Flake8](https://flake8.pycqa.org/en/latest/manpage.html) and [Black](https://pypi.org/project/black/) for linting & formatting source code of this project.
<br>
- **Run QA checks on local environment ⚡** :

  - Run Shell script on Windows 💾 :

  ```
  ...\Bulk-Mailer> .\bulkmailer_QA_Checks
  ``` 

  - Run Shell script on Linux 👨‍💻 :

  ```
  .../Bulk-Mailer$ ./bulkmailer_QA_Checks
  ``` 
  
  - Alternate option ✔ :
    - Run this on terminal ⚡:
      - Windows 💾
        ```
        ...\Bulk-Mailer> black .
        ``` 
        ```
        ...\Bulk-Mailer> flake8 .
        ``` 
      - Linux 👨‍💻
        ```
        .../Bulk-Mailer$ black .
        ``` 
        ```
        .../Bulk-Mailer$ flake8 .
        ``` 
  

## Live Deployment 📦

 Click Here to view the deployment!

[![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://bulkmailercf.herokuapp.com//)<br>

[![Netlify Status](https://api.netlify.com/api/v1/badges/949ff150-ae0c-4368-b749-e9a083b8ee65/deploy-status)](https://app.netlify.com/sites/elegant-lamarr-3ec036/deploys)


When you are done with the setup, you should host your website online.
We highly recommend to read through the:<br>
- [Deploying on Heroku](https://stackabuse.com/deploying-a-flask-application-to-heroku/).<br>
- [Deploying on Netlify](https://www.netlify.com/blog/2016/10/27/a-step-by-step-guide-deploying-a-static-site-or-single-page-app/).<br>

## Demo 🛠️

<table><tr><td valign="top" width="50%">

![MAC](https://cdn.discordapp.com/attachments/701086382407549019/791974933790064660/Screenshot_2020-12-25_155448.png)

</td><td valign="top" width="50%">

![MAC](https://cdn.discordapp.com/attachments/701086382407549019/791974938377584640/Screenshot_2020-12-25_155428.png)

</td></tr></table>  


## Illustrations
- [UnDraw](https://undraw.co/illustrations)

## License 📄

This project is licensed under the GPL-3.0 License. See the [LICENSE](./LICENSE) file for details



## For the Future
If you can help us with these. Please don't hesitate to open a [Pull Request](https://github.com/vigneshshettyin/Bulk-Mailer/pulls).

## Cool Developers🚧

<a href="https://github.com/data-charya/Cn-project/graphs/contributors">
  <img src="https://contributors-img.web.app/image?repo=data-charya/Cn-project" />
</a>

<a href="https://github.com/vigneshshettyin/Bulk-Mailer/graphs/contributors">
  <img src="https://contributors-img.web.app/image?repo=vigneshshettyin/Bulk-Mailer" />
</a>

## Show some ❤️ by starring the repository

<table><tr><td valign="top" width="50%">
 
 
[![Forkers repo roster for @vigneshshettyin/Bulk-Mailer](https://reporoster.com/forks/vigneshshettyin/Bulk-Mailer)](https://github.com/vigneshshettyin/Bulk-Mailer/network/members)


</td><td valign="top" width="50%">
 
 
[![Stargazers repo roster for @vigneshshettyin/Bulk-Mailer](https://reporoster.com/stars/vigneshshettyin/Bulk-Mailer)](https://github.com/vigneshshettyin/Bulk-Mailer/stargazers)


</td></tr></table>  

