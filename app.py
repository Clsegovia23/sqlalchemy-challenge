import numpy as np
import pandas as pd
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify


# create engine to hawaii.sqlite
engine = create_engine("sqlite:///./Instructions/Resources/hawaii.sqlite")
conn = engine.connect()

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables

Base.prepare(conn, reflect=True)

# View all of the classes that automap found
Base.classes.keys()

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)



app = Flask(__name__)

@app.route("/")
def home():
    return(
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start><end>"
    )

# /api/v1.0/precipitation
# Convert the query results to a dictionary using date as the key and prcp as the value.
# Return the JSON representation of your dictionary.

@app.route("/api/v1.0/precipitation")
def precipitation():
    recent_date = dt.date(2017, 8, 23)
    year_ago = recent_date - dt.timedelta(days=365)
    
    historical_temps = (session.query(Measurement.date, Measurement.prcp).\
                       filter(Measurement.date <= recent_date).\
                       filter(Measurement.date >= year_ago).\
                       order_by(Measurement.date).all())
    
    precipitation = {date: prcp for date, prcp in historical_temps}
    return jsonify(precipitation)

# /api/v1.0/stations
# Return a JSON list of stations from the dataset.
@app.route("/api/v1.0/stations")
def stations():
    stations_list = (session.query(Station.station).all())
    return jsonify(stations_list)

# /api/v1.0/tobs
# Query the dates and temperature observations of the most active station for the last year of data.
# Return a JSON list of temperature observations (TOBS) for the previous year.
@app.route("/api/v1.0/tobs")
def tobs():
   
    recent_date = dt.date(2017, 8, 23)
    year_ago = recent_date - dt.timedelta(days=365)
    
    hist_tobs = (session.query(Measurement.tobs).\
                filter(Measurement.station == "USC00519281").\
                filter(Measurement.date <= recent_date).\
                filter(Measurement.date >= year_ago).\
                order_by(Measurement.tobs).all())
    return jsonify(hist_tobs)


# Return a JSON list of the minimum temperature, the average temperature, and the max temperature 
# for a given start or start-end range.
# When given the start only, calculate TMIN, TAVG, and TMAX for all dates greater than and equal to the start date.

#     start = (session.query(Measurement.date).order_by(Measurement.date).first())
#     end = (session.query(Measurement.date).order_by(Measurement.date.desc()).first())

@app.route("/api/v1.0/<start>")
def start(start=None):
    #start = Measurement.date <= "2010-01-01"
    #end = Measurement.date >= "2017-08-23"
        
    tobs_stats = (session.query(Measurement.tobs).\
                 filter(Measurement.date.between(start, "2017-08-23")).all())
    
    tobs_df = pd.DataFrame(tobs_stats, columns=["tobs"])
 
    tmin = tobs_df["tobs"].min()
    tavg = tobs_df["tobs"].mean()
    tmax = tobs_df["tobs"].max()
    print(tmin, tavg, tmax)
    print(tobs_df)    
    return jsonify(tmin, tavg, tmax)


# Return a JSON list of the minimum temperature, the average temperature, and the max temperature 
# for a given start or start-end range.
# When given the start and the end date, calculate the TMIN, TAVG, and TMAX for dates between the start and end date inclusive.

@app.route("/api/v1.0/<start>/<end>")
def startend(start=None, end=None):
    start = Measurement.date <= "2010-01-01"
    end = Measurement.date >= "2017-08-23"

    tobs_stats = (session.query(Measurement.tobs).\
                 filter(Measurement.date.between(start, end)).all())
    
    tobs_all_df = pd.DataFrame(tobs_stats, columns=["tobs"])
    
    tmin = tobs_all_df["tobs"].min()
    tavg = tobs_all_df["tobs"].mean()
    tmax = tobs_all_df["tobs"].max()
    print(tmin, tavg, tmax)
    print(tobs_all_df)
    return jsonify(tmin, tavg, tmax)

if __name__ == "__main__":
    app.run(debug=True)