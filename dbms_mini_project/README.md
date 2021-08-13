# flask-app-dbms-project

A minimal web app to store secret notes and photos developed using Flask framework. 

The main purpose is to introduce how to implement the database in web application with Flask.

## How to Run

- Step 1: Make sure you have Python

- Step 2: Install the requirements: `pip install -r requirements.txt`

- Step 3: Go to this app's directory and run `python app.py`


## Details about This App

There are two tabs in this toy app

- **Private**: Only logged-in user can access this page. Otherwise the user will get a 401 error page.

- **Admin Page**: This part is only open to the user who logged in as "Admin". In this tab, the administrator can manage accounts (list, delete, or add).


A few accounts were set for testing, like ***admin*** (password: admin), ***krunal*** (password: krunal), ***test*** (password: 123456), etc. 
You can also delete or add accounts after you log in as ***admin***.

# LOG IN TO THE APP & STORE YOUR SECRET NOTES AND IMAGES. LETS GO...