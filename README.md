dust
---
####Environment
```
pipenv install
pipenv shell
# db related
flask db init # only at first time
flask db migrate
flask db upgrade

# using shell
# pipenv shell
flask shell
```



####API
| URL                             | Method | POST Json or Description                                     |
| ------------------------------- | ------ | ------------------------------------------------------------ |
| /login                          | POST   | {'username':'...', 'password': '...'}                        |
| /logout                         | POST   |                                                              |
| /register                       | POST   | {'username':'...', 'password': '...'}                        |
| /planets/show                   | GET    | Get random 16 planets' info, in which timestamp is 'created_at' |
| /planets/\<string:planet_name>  | GET    | Return the planet's info                                     |
| /user/planet                    | POST   | Set up a planet                                              |
| /user/get-dust                  | GET    | How many times left in a day to get dust                     |
| /user/get-dust                  | POST   | Get 88 dust                                                  |
| /user/build                     | POST   | {'planet_name':'…', 'dust_num':'...'}                        |
| /user/spy/\<string:planet_name> | GET    | Return email                                                 |
| /rank/builders                  | GET    | Return top 10 builders'name with <br />the reward dust sum from building planets |
| /rank/planets                   | GET    | Return top 10 planets'name with their dust num               |
| /rank/owners                    | GET    | Return top 10 owners                                         |





