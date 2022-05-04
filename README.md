# API for Movie Database
Simple Web Service CRUD application movie database 

## Requirements:
* docker
* git

## To launch:
```bash
git clone --recurse git@github.com:borada-bit/crud_2.git
cd crud_2
docker-compose build
docker-compose up
```

## Usage
Test the API with [Postman](https://www.postman.com/).

### Example JSON

```JSON
[ 
	{
	"title": "Avengers",
	"year": 2012,
	"genre": "Action",
	"director": "Josh Whedon",
	"runtime": 143,
	"comment": "Amazing action movie!"
	"renter_id": 12345
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
