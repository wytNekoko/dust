dust
---
#### Environment

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



#### API

 URL                             | Method | POST Json or Return Json                                     
 ------------------------------- | ------ | ------------------------------------------------------------ 
 /login                          | POST   | {'username':'...', 'password': '...'}                        
 /logout                         | POST   |                                                              
 /register                       | POST   | {'username':'...', 'password': '...'}                        
 /planets/show                   | GET    | Get random 16 planets' info, in which timestamp is 'created_at'
 /planets/one/\<string:planet_name>  | GET    | Return the planet's info                                     
 /user/planet                    | POST   | Set up a planet                                              
 /user/get-dust                  | GET    | How many times left in a day to get dust                     
 /user/get-dust                  | POST   | Get 88 dust                                                  
 /user/build                     | POST   | {'planet_name':'…', 'dust_num':'...'}                        
 /user/spy/\<string:planet_name> | GET    | xxx@yyy.com                                                 
 /rank/dashboard                 | GET    | {'planets':\[{'name':..,'dust':..}], 'owners':\[{'name':..,'dust':..}], 'builders':\[{'name':..,'dust':..}]}
 /rank/winners                   | GET    | {'planets':\[{'name':..,'dust':..}], 'owners':\[{'name':..,'dust':..}], 'builders':\[{'name':..,'dust':..}]}
 /profile/owned-planets          | GET    | \[{'name': planet_name, 'dust_num': num}]
 /profile/builded-planets        | GET    | \[{'name': planet_name, 'reward_dust': num}]
 /profile/main                   | GET    | {'total_dust':num, \[{'created_at': timestamp, 'name'; planet_name, 'reward': dust num}]





