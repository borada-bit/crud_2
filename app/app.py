import mimetypes
from flask import Flask, request, Response
import json
import my_data
import my_mongo
import random
import requests

### API
api_url = "http://172.17.0.1:5000/contacts/"


def get_api_url():
    return api_url


### FLASK
app = Flask(__name__)


### REST/API METHODS BELOW
@app.route("/")
def index():
    return "Welcome!"


@app.route("/movies/", methods=["GET"])
def get_all_movies():
    movies = list(my_mongo.get_all_movies())
    if request.args.get("expand"):
        alive = False
        try:
            requests.get(get_api_url())
            alive = True
        except requests.exceptions.ConnectionError as e:
            pass

        if alive:
            for index, item in enumerate(movies):
                if item.get("renter_id"):
                    api_url = get_api_url()
                    api_url = api_url + str(item.get("renter_id"))
                    response = requests.get(api_url)
                    if response.status_code == 200:
                        item["renter_data"] = response.json()
                        item.pop("renter_id", None)
                    # if another web service does not work just return initial list of movies
                    else:
                        return Response(
                            json.dumps(movies), status=200, mimetype="application/json"
                        )

    return Response(json.dumps(movies), status=200, mimetype="application/json")


@app.route("/movies/<int:movie_id>", methods=["GET"])
def get_movie(movie_id):
    movie = my_mongo.get_movie(movie_id)
    if movie is None:
        # 404 NOT FOUND
        return Response(
            json.dumps({"Error": "No such id exists"}),
            status=404,
            mimetype="application/json",
        )

    if request.args.get("expand"):
        # if expand param is true need to return info about renter
        renter_id = movie["renter_id"]
        if renter_id is None:
            return Response(
                json.dumps({"Error": "This movie does not have a renter"}),
                status=404,
                mimetype="application/json",
            )
        alive = bool
        try:
            requests.get(get_api_url())
            alive = True
        except requests.exceptions.ConnectionError as e:
            pass
        if alive:
            api_url = get_api_url()
            api_url = api_url + str(renter_id)
            response = requests.get(api_url)
            movie["renter_data"] = response.json()
            movie.pop("renter_id", None)

        return Response(
            json.dumps(movie),
            status=response.status_code,
            mimetype="application/json",
        )
    else:
        # 200 OK
        return Response(json.dumps(movie), status=200, mimetype="application/json")


@app.route("/movies/<int:movie_id>/renter", methods=["GET"])
def get_movie_renter(movie_id):
    movie = my_mongo.get_movie(movie_id)
    if movie is None:
        # 404 NOT FOUND
        return Response(
            json.dumps({"Error": "No such id for a movie exists"}),
            status=404,
            mimetype="application/json",
        )
    # 200 OK
    renter_id = movie.get("renter_id")
    if renter_id:
        api_url = get_api_url()
        api_url = api_url + str(renter_id)
        response = requests.get(api_url)

        return Response(
            response.text,
            status=response.status_code,
            mimetype="application/json",
        )
    else:
        return Response(
            json.dumps({"Error": "This movie has no renter"}),
            status=404,
            mimetype="application/json",
        )


@app.route("/movies/", methods=["POST"])
def create_movie():
    try:
        movie_data = json.loads(request.data)
    # bad format of json
    except json.decoder.JSONDecodeError:
        # 422 UNPROCESSABLE ENTITY
        return Response(
            json.dumps({"Error": "Wrong json format"}),
            status=422,
            mimetype="application/json",
        )

    # assign random id
    while True:
        generated_id = random.randint(0, 1000)
        movie_data["id"] = generated_id

        # all_movies = list(g_db.movie_collection.find({}))
        all_movies = list(my_mongo.get_all_movies())
        for obj in all_movies:
            if movie_data["id"] == obj["id"]:
                continue
        break

    # CHECK if renter with this id exists in another web serice
    if movie_data.get("renter_id"):
        renter_id = movie_data.get("renter_id")
        api_url = get_api_url()
        api_url = api_url + str(renter_id)
        response = requests.get(api_url)

        if response.status_code != 200:
            return Response(
                json.dumps(
                    {"Error": f"No such renter with this id: {renter_id} exists"}
                ),
                # 422 UNPROCESSABLE ENTITY
                status=422,
                mimetype="application/json",
            )

    if movie_data.get("renter_data"):
        renter_data = movie_data.get("renter_data").copy()
        movie_data["renter_id"] = renter_data.get("id")
        movie_data.pop("renter_data")
        api_url = get_api_url()
        r = requests.post(api_url, json=renter_data)
        if r.status_code != 201:
            return Response(
                r.text,
                status=r.status_code,
                mimetype="application/json",
            )

    ## ALL CHECKS HAVE PASSED
    # passing copy of movie data so it does not add mongo _id field and can return response with json dumps
    added = my_mongo.add_movie(movie_data.copy())
    if added is True:
        # 201 CREATED
        resp = Response(json.dumps(movie_data), status=201, mimetype="application/json")
        # Somehow make this header below fit into Response constructor?
        resp.headers["Content-Location"] = "/movies/" + str(movie_data["id"])
        return resp
    else:
        # 422 UNPROCESSABLE ENTITY
        resp = Response(json.dumps(movie_data), status=422, mimetype="application/json")
        return resp


# TODO check if movie does not have renter already
@app.route("/movies/<int:movie_id>/renter", methods=["POST"])
def add_renter(movie_id: int):
    try:
        renter_data = json.loads(request.data)
    # bad format of json
    except json.decoder.JSONDecodeError:
        # 422 UNPROCESSABLE ENTITY
        return Response(
            json.dumps({"Error": "Wrong json format"}),
            status=422,
            mimetype="application/json",
        )

    # GETTING MOVIE DATA
    movie = my_mongo.get_movie(movie_id)
    if movie is None:
        # 404 NOT FOUND
        return Response(
            json.dumps({"Error": "No movie with such id exists"}),
            status=404,
            mimetype="application/json",
        )
    # 200 OK
    renter_id = movie.get("renter_id")
    if renter_id:
        return Response(
            json.dumps({"Error": "This movie already has a renter"}),
            status=422,
            mimetype="application/json",
        )

    api_url = get_api_url()
    r = requests.post(api_url, json=renter_data)
    if r.status_code == 201:
        renter_id = renter_data.get("id")
        if not id:
            return Response(
                json.dumps({"Error": "Failed to add renter_id to movie"}),
                status=400,
                mimetype="application/json",
            )

        if my_mongo.update_movie_renter(movie_id, renter_id):
            # 201 CREATED
            resp = Response(
                json.dumps(renter_data), status=201, mimetype="application/json"
            )
            # Somehow make this header below fit into Response constructor?
            resp.headers["Content-Location"] = "/movies/" + str(movie_id) + "/renter"
            return resp
        else:
            # 400 BAD REQUEST
            return Response(
                json.dumps({"Error": "Failed to update movie with renter_id"}),
                status=400,
                mimetype="application/json",
            )
    else:
        # 400 bad request
        return Response(
            json.dumps({"Error": "Failed to add renter to another web service"}),
            status=400,
            mimetype="application/json",
        )


# 200 status code netinka paupdatinus
# BUG veikia kaip patch, padavus tik kelis field juos updatina, reikia patikrint ar paduotas visas json objektas
# TODO check if updated renter_id exists in another webservice?
@app.route("/movies/<int:movie_id>", methods=["PUT"])
def update_movie(movie_id):
    # CHECK IF JSON IS OF GOOD FORMAT
    try:
        new_movie_data = json.loads(request.data)
    # bad format of json
    except json.decoder.JSONDecodeError:
        # 422 UNPROCESSABLE ENTITY
        return Response(
            json.dumps({"Error": "Wrong json format"}),
            status=422,
            mimetype="application/json",
        )
    # new_movie_data = json.loads(request.data)

    new_movie_data["id"] = movie_id
    # GET OLD MOVIE DATA, copy if it does new movie json is bad?
    # old_movie_data = my_mongo.get_movie(movie_id)
    old_movie_data = {}
    # NO MOVIE WITH SUCH ID EXISTS YET, SO PERFORMING MONGO_ADD INSTEAD OF MONGO UPDATE

    updated = bool
    if my_mongo.get_movie(movie_id) is None:
        # giving copy to this one so that response has no _id field
        updated = my_mongo.add_movie(new_movie_data.copy())
    else:
        # UPDATING
        old_movie_data = my_mongo.get_movie(movie_id).copy()
        my_mongo.delete_movie(movie_id)
        updated = my_mongo.add_movie(new_movie_data.copy())
        # query_filter = {"id": movie_id}
        # query_value = {"$set": new_movie_data}
        # updated = my_mongo.update_movie(movie_id, query_filter, query_value)

    if updated:
        response_data = {
            "old_movie_data": old_movie_data,
            "new_movie_data": new_movie_data,
        }
        # 200 OK
        resp = Response(
            json.dumps(response_data), status=200, mimetype="application/json"
        )
        resp.headers["Content-Location"] = "/movies/" + str(movie_id)
        return resp
    else:
        # 422 UNPROCESSABLE ENTITY
        return Response(
            json.dumps({"Error": "Wrong schema of json"}),
            status=422,
            mimetype="application/json",
        )


@app.route("/movies/<int:movie_id>/renter", methods=["PUT"])
def update_renter(movie_id):
    # CHECK IF JSON IS OF GOOD FORMAT
    try:
        new_renter_data = json.loads(request.data)
    # bad format of json
    except json.decoder.JSONDecodeError:
        # 422 UNPROCESSABLE ENTITY
        return Response(
            json.dumps({"Error": "Wrong json format"}),
            status=422,
            mimetype="application/json",
        )

    if my_mongo.get_movie(movie_id) is None:
        return Response(
            json.dumps({"Error": "No movie with such id exists."}),
            status=404,
            mimetype="application/json",
        )

    api_url = get_api_url()
    updated_in_mongo = bool
    movie_data = my_mongo.get_movie(movie_id)
    old_renter_data = {}
    old_renter_id = movie_data.get("renter_id")

    if old_renter_id:
        # UPDATING
        updated_in_mongo = my_mongo.update_movie_renter(movie_id, old_renter_id)
        api_url = api_url + str(old_renter_id)
        # BUG
        old_renter_data = json.loads(requests.get(api_url).text)
        r = requests.put(api_url, json=new_renter_data)
    else:
        r = requests.post(api_url, json=new_renter_data)
        updated_in_mongo = my_mongo.update_movie_renter(movie_id, new_renter_data["id"])

    if updated_in_mongo and (r.status_code == 201 or r.status_code == 200):
        response_data = {
            "old_renter_data": old_renter_data,
            "new_renter_data": new_renter_data,
        }
        # 200 OK
        resp = Response(
            json.dumps(response_data), status=200, mimetype="application/json"
        )
        resp.headers["Content-Location"] = "/movies/" + str(movie_id) + "/renter"
        return resp
    else:
        # 422 UNPROCESSABLE ENTITY
        return Response(
            json.dumps({"Error": "Something went wrong."}),
            status=422,
            mimetype="application/json",
        )


# paduodi objekta kuriame yra laukai kurios reikia keisti
# parodo new vs old pilnus objektus
@app.route("/movies/<int:movie_id>", methods=["PATCH"])
def patch_movie(movie_id):
    try:
        new_movie_data = json.loads(request.data)
    # bad format of json
    except json.decoder.JSONDecodeError:
        # 422 UNPROCESSABLE ENTITY
        return Response(
            json.dumps({"Error": "Wrong json format"}),
            status=422,
            mimetype="application/json",
        )

    cursor = my_mongo.get_movie(movie_id)

    if cursor is None:
        return Response(
            json.dumps({"Error": "No such id exists"}),
            status=404,
            mimetype="application/json",
        )
    else:
        new_movie_data["id"] = movie_id
        # query filters for mongo_db
        query_filter = {"id": movie_id}
        query_values = {"$set": new_movie_data}
        # saving old movie data for output
        old_movie_data = my_mongo.get_movie(movie_id)
        # updating
        updated = my_mongo.update_movie(movie_id, query_filter, query_values)
        if updated:
            response_data = {
                "old_movie_data": old_movie_data,
                "new_movie_data": new_movie_data,
            }

            # 200 OK
            resp = Response(
                json.dumps(response_data), status=200, mimetype="application/json"
            )
            resp.headers["Content-Location"] = "/movies/" + str(movie_id)
            return resp
        else:
            # 422 UNPROCESSABLE ENTITY
            return Response(
                json.dumps({"Error": "Wrong fields provided in json"}),
                status=422,
                mimetype="application/json",
            )


# IDEMPOTENT
@app.route("/movies/<int:movie_id>", methods=["DELETE"])
def delete_movie(movie_id):
    cursor = my_mongo.get_movie(movie_id)
    if cursor is None:
        # 404 NOT FOUND
        return Response(
            json.dumps({"Error": f"No such id:{movie_id} exists"}),
            status=404,
            mimetype="application/json",
        )
    else:
        movie_data = cursor.copy()
        my_mongo.delete_movie(movie_id)
        renter_id = movie_data.get("renter_id")
        renter_data = {}
        if renter_id:
            api_url = get_api_url()
            api_url = api_url + str(renter_id)
            r_get = requests.get(api_url)
            renter_data = json.loads(r_get.text)
            r_delete = requests.delete(api_url)

        # 200 OK
        return Response(
            json.dumps({"movie data": movie_data, "renter data": renter_data}),
            status=200,
            mimetype="application/json",
        )


@app.route("/movies/<int:movie_id>/renter", methods=["DELETE"])
def delete_movie_renter(movie_id):
    cursor = my_mongo.get_movie(movie_id)
    if cursor is None:
        # 404 NOT FOUND
        return Response(
            json.dumps({"Error": f"No such id:{movie_id} exists"}),
            status=404,
            mimetype="application/json",
        )
    renter_id = cursor.get("renter_id")
    if renter_id:
        api_url = get_api_url()
        api_url = api_url + str(renter_id)
        renter_data = requests.get(api_url)
        r = requests.delete(api_url)
        return Response(
            # r.text = "contact deleted successfuly"
            json.dumps({"Status": r.text, "Renter_data": json.loads(renter_data.text)}),
            status=r.status_code,
            mimetype="application/json",
        )

    else:
        # 404 NOT FOUND
        return Response(
            json.dumps({"Error": "This movie does not have renter"}),
            status=404,
            mimetype="application/json",
        )


## MAIN
def main():
    for json_obj in my_data.data:
        my_mongo.add_movie(json_obj)

    app.run(host="0.0.0.0", debug=True, port=80)


if __name__ == "__main__":
    main()
