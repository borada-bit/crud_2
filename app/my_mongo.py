from pymongo import MongoClient, errors

###  MONGO CLIENT
g_client = MongoClient("mongodb://mongo:27017")


# DATABASE NAME movie_database
g_database_name = "movie_database"
# COLLECTION NAME movie_collection
g_collection_name = "movie_collection"


# DROPS IF ALREADY EXISTS
g_client.drop_database("movie_database")
g_db = g_client[g_database_name]


### MONGO VALIDATOR BEFORE INSERTING
g_db.create_collection(
    g_collection_name,
    validator={
        "$jsonSchema": {
            "bsonType": "object",
            "required": ["id", "title", "year", "genre", "director", "runtime"],
            "properties": {
                "_id": {"bsonType": "objectId"},
                "id": {"bsonType": "int"},
                "title": {"bsonType": "string"},
                "director": {
                    "bsonType": "string",
                    "description": "Set to default value",
                },
                "genre": {"bsonType": "string"},
                "year": {"bsonType": "int", "minimum": 1920, "maximum": 2022},
                "runtime": {
                    "bsonType": "int",
                    "minimum": 1,
                    "maximum": 500,
                    "description": "must be an integer in [ 2017, 3017 ] and is required",
                },
                "comment": {
                    "bsonType": ["string"],
                    "description": "must be a string if the field exists",
                },
                "renter_id": {
                    "bsonType": ["int"],
                    "description": "id for the renter if the movie is rented",
                },
            },
            "additionalProperties": False,
        }
    },
    validationLevel="strict",
    validationAction="error",
)

g_collection = g_db[g_collection_name]

# Returns True if adding succesffuly
# some better implemenation?
def add_movie(data):
    # seems bad
    try:
        g_collection.insert_one(data)
        return True
    except:
        print("Error inserting.")
        return False


# returns cursor object of all movies
def get_all_movies():
    return g_collection.find({}, {"_id": 0})


# returns cursor object of found(None if no movie found with such id) movie, without _id field
def get_movie(movie_id: int):
    return g_collection.find_one({"id": movie_id}, {"_id": 0})


# what does this return?
# Something with error handling because now this func does nothing more than update_one
def update_movie(movie_id: int, query_filter, query_value):
    try:
        return g_collection.update_one(query_filter, query_value)
        return True
    # nepreajo verif
    except:
        return False


# @returns True if updated
def update_movie_renter(movie_id: int, renter_id: int):
    filter = {"id": movie_id}
    value = {"$set": {"renter_id": renter_id}}
    try:
        g_collection.update_one(filter, value)
        return True
    except:
        return False


def delete_movie(movie_id: int):
    g_collection.delete_one({"id": movie_id})
