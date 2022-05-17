# API for Movie Database
Simple Web Service CRUD application movie database 

## Requirements:
* docker
* git
* docker-compose

## To launch:
```bash
git clone --recurse https://github.com/borada-bit/crud_2.git
cd crud_2
docker-compose build
docker-compose up
```

## Usage
Test the API with [Postman](https://www.postman.com/).

### Example JSON

```JSON
[ 
    "id": 3,
    "title": "Forrest Gump",
    "year": 1994,
    "genre": "drama",
    "director": "Robert Zemeckis",
    "runtime": 144,
    "renter_id": 12345
]
```

### Example JSON expanded

```JSON
[ 
    "id": 3,
    "title": "Forrest Gump",
    "year": 1994,
    "genre": "drama",
    "director": "Robert Zemeckis",
    "runtime": 144,
    "renter_data": {
        "id": 12345,
        "surname": "Vangogh",
        "name": "Jake",
        "number": "+37065841738",
        "email": "jakevan@mail.com"
    }
]
```

## RESTFUL API:
### POST 

#### Create a movie

`http://localhost:80/movies/`

#### Create a movie's renter

`http://localhost:80/movies/<movie_id>/renter`

### GET
#### Get a movie by id:

`http://localhost:80/movies/<movie_id>`

#### Get all movies:

`http://localhost:80/movies/`

#### Get movie renter

`http://localhost:80/movies/<movie_id>/renter`

### PUT
#### Update movie by id:

`http://localhost:80/movies/<movie_id>`

#### Update movie's renter by id:

`http://localhost:80/movies/<movie_id>/renter`

### PATCH
#### Modify movie fields by id:

`http://localhost:80/movies/<movie_id>`

### DELETE 
#### Delete movie by id:

`http://localhost:80/movies/<movie_id>`

#### Delete movie's renter:

`http://localhost:80/movies/<movie_id>/renter`
