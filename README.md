# Homework 4: 🐳 Starting with the project back-end

Author: Dmytro Hrebeniuk

## 📝 What does this MR do?

Homework task was to create realisation of back-end of the system of ticket realisation. This system creates API requests and connects with database MySQL.

In this MR I created modules:

- database.py - creates database engine and connection session to connect mysql databse to at the localhost:3306. I also define "Base" for the database models.

- bm_classes.py - creates bases for entities used in the project (Event, Event_w_id, Ticket (Enums TicketStatus and TicketType inside) Performer, User, User_w_id, Contract). Bases Event_w_id and User_w_id are used to return entities with id's when answering GET Api request.

- Dockerfile - contains all biuld information, installs all dependencies and sparts application's Docker conatiner on localhost:8000.

- main.py - contains all Rest Api's design and main system logic. 

- models.py - contains models that will be used in the database

- requirements.txt - list all libraries needed in the project

- docker-compose.yaml - build dtabase and app containers. Describes relations between them.


## 🏃‍♂️ How to run and Results

You need to open Docker on your PC and the [https://github.com/Dimitro2021/APZ_4](url) to copy the project. Then navigate yourself to APZ_4 directory and execute in terminal
- `docker compose up --build`
![image](https://github.com/Dimitro2021/APZ_4/assets/91617001/f92b3a6c-f168-4d56-bfd3-b1b0f58f1899)



Describe the specific results or outcomes of the application's execution.
Provide any relevant screenshots, logs, or data to illustrate the results.

### How to run the application

🦾 [ Example – modify for your case ] 🦾

❗️ It is **mandatory** to illustrate results, otherwise it will lead to _points deduction_.❗️

1. Clone the repository

   `git clone {your_repo_name}`

2. Go to directory `{your_hw_directory}`
   `cd {your_hw_directory}`

3. Run this command to ...
   `{command_to_run}`
   ![image_command_result.png]({your_image_path})

## 🎀 Additional Notes

Add any additional information here, which you consider important to note, especially if it is related to homework structure, what can be improved, and what you has struggles with.
