# import necessary libraries
from flask import Flask, render_template, request, redirect
from flask_pymongo import PyMongo
import math

# create instance of Flask app
app = Flask(__name__)

# Use PyMongo to establish Mongo connection
mongo = PyMongo(app, uri="mongodb://localhost:27017/perfi_app")

# List of dictionaries
prompts = ["Should I use my Chime card or my cashback credit card?",
        "Use this app to find out!"]

# create route that renders index.html template
@app.route("/")
def index():

    # Find one record of data from the mongo database
    data = mongo.db.collection.find_one()

    # Return template and data
    return render_template("index.html", prompts=prompts, data=data)

# Route that will trigger the scrape function
@app.route("/", methods=['POST'])
def my_form_post():
    try:
        cc_rate = float(request.form['text-input'])
    except:
        cc_rate = 0
    try:
        spend_amt = float(request.form['text-input-2'])
    except:
        spend_amt = 0
    if spend_amt % 1 != 0:
        #chime_gain = math.floor(.1*(1-(spend_amt % 1))*100)/100
        chime_gain = round(.1*(1-(spend_amt % 1)), 2)
    elif spend_amt % 1 ==0:
        chime_gain = 0 
    #cc_gain = math.floor(cc_rate*spend_amt)/100
    cc_gain = round(cc_rate*spend_amt/100, 2)
    if chime_gain > cc_gain:
        card = "your Chime card"
        g_cb = chime_gain
        l_cb = cc_gain
    elif chime_gain == cc_gain:
        card = "either card"
        g_cb = chime_gain
        l_cb = cc_gain
    elif chime_gain < cc_gain:
        card = "your credit card"
        g_cb = cc_gain
        l_cb = chime_gain
    # Return results
    data = {
        "spend_amt": spend_amt,
        "card": card,
        "g_cb": g_cb,
        "l_cb": l_cb
    }
    # Update the Mongo database using update and upsert=True
    mongo.db.collection.update_one({}, {"$set": data}, upsert=True)
    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True)
