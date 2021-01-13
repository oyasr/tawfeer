# Tawfeer
### Description
Tawfeer is an Expenses Tracking web application. Users are able to track their monthly spendings, 
set a monthly budget or even draw some insights thanks to Tawfeer's visualization page. 
With Tawfeer's user friendly interface and its robust architecture, managing budgets and tracking expenses have never been so easy!

### Motivation
Tawfeer (توفير) is the Arabic word for 'Economizing', which is the motivation of this project's idea.
The main reason you should track your expenses is to identify and eliminate wasteful spending habits in your financial life. 
Moreover, consistently tracking your expenses will help you maintain control of your finances, and promote better financial habits like saving and investing.
But it seems like most people don't know what their monthly average spendings is. In fact, for many people, the idea of logging every transaction 
into a personal budget note sounds like the world’s most boring, insignificant task. And it really is! Just think of the ammount
of the manual work it would take someone to keep this organized and consistent. Think about how would you know which category spends the most?
How the spendings of the current month compare to other months? All of this and more is now achievable with just a few clicks!

### Code style
All backend code follows [**PEP8 style guidelines**](https://www.python.org/dev/peps/pep-0008/)

## Getting Started
### Pre-requisites and Local Development
Developers using this project should already have Python3, pip and sqlite installed on their local machines.\
From inside the 'tawfeer' folder run `pip install -r requirements.txt`. All required packages are included in the requirements file.
To run the application locally run the following command:

    flask run

The application is run on `http://127.0.0.1:5000/` by default.

### Project Structure
    ├── tawfeer/
        ├── static/
        |    ├── styles.css
        |    ├── faveicon.ico
        ├── env/
        ├── templates/
        |    ├── add.html
        |    ├── apology.html
        |    ├── index.html
        |    ├── insights.html
        |    ├── layout.html
        |    ├── login.html
        |    ├── register.html
        ├── helpers.py
        ├── app.py
        ├── requirements.txt
        ├── tawfeer.db

This structure has three top-level folders:
* The *static* which contains static files such as styles, faveicon & images
* The *env* folder contains the Python virtual environment.
* The *templates* folder where views (html files) exist.

There are also a few new files:
* *app.py* where the flask application lives.
* *helpers.py* contains helper functions.
* *requirements.txt* lists the package dependencies to regenerate identical virtual environments.
* *tawfeer.db* which is the sqlite database file

## Acknowledgements & Final words
This is the first version of Tawfeer. Of course there will be imperfections, flaws that might need some more work. We plan on continuing the development proccess
of this project, adding more new features and making it ready for production. So if you are interested in contributing to this project don't hesitate to send a 
pull request or even open up a new issue and we will respond ASAP.

## Authors
Ahmed Yasser Fathi<br>
Moaz Mohammed Samy<br>
Osama Mohammed Ragab<br> 
Osama Yasser Saber
