# Import the dependencies.
from flask import Flask, jsonify
from sqlalchemy import create_engine
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy.sql import func
import datetime as dt
import json
from pprint import pprint


#################################################
# Database Setup
#################################################


# reflect an existing database into a new model
engine = create_engine("sqlite:///Starter_Code/Resources/hawaii.sqlite")
Base = automap_base()

# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
Station = Base.classes.station
Measurement = Base.classes.measurement

# Create our session (link) from Python to the DB
session = Session(engine)

#Dictionary of the query results of precipitation analysis by date
year_ago = dt.date(2017,8,23) - dt.timedelta(days=365)
prcp_query = session.query(Measurement.date,Measurement.prcp).\
    filter(Measurement.date >= year_ago).all()

prcp_results = []
for row in prcp_query:
    prcp_results.append([{"Date":row[0],"Prcp":row[1]}])


#List of the stations
station_query = session.query(Station.name).all()

station_names = []
for row in station_query:
    station_names.append([row[0]])

#Dictionary of temperatures for the most active station by date
temp_query = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.station == 'USC00519281',Measurement.date >=year_ago).all()

temp_results = []
for row in temp_query:
    temp_results.append([{"Date":row[0],"Tobs":row[1]}])


#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################
@app.route("/")
def welcome():
    return(
    f"Welcome to the my Climate App!<br/>"
    f"Available Routes:<br/>"
    f"/api/v1.0/precipitation<br/>"
    f"/api/v1.0/stations<br/>"
    f"/api/v1.0/tobs<br/>"
    f"/api/v1.0/2016510<br/>"
    f"/api/v1.0/2016823/2017823<br/>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation_query_results ():
    """Return precipitation data as json"""

    return jsonify(f"Percipitation Query Results by Date",prcp_results)

@app.route("/api/v1.0/stations")
def station_name_list ():
    """Return station name data as json"""

    return jsonify(f"List of Station Names",station_names)

@app.route("/api/v1.0/tobs")
def temperature_list ():
    """Return temperature data as json"""

    return jsonify(f"Temperature Query Results by Date",temp_results)

@app.route("/api/v1.0/<start>")
def temp_start(start):
    '''Fetch the minimum temperature, the average temperature, and the maximum temperature for a specified start or start-end range'''
    date = dt.datetime.strptime(start, '%Y%m%d').date()
    range = session.query(func.avg(Measurement.tobs).label("Average Temp"), func.min(Measurement.tobs).label("Minimum Temp"), func.max(Measurement.tobs).label("Max Temp")) .\
        filter(Measurement.date >=date).all()
    
    for row in range:
        average = row[0]
        minimum = row[1]
        maximum = row[2]

    return jsonify(f"Average temperature in from start date {date} is {average}, minimum temperature is {minimum}, and max temperature is {maximum}")

@app.route("/api/v1.0/<start>/<end>")
def temp_range(start, end):
    start_date = dt.datetime.strptime(start, '%Y%m%d').date()
    end_date = dt.datetime.strptime(end, '%Y%m%d').date()

    range = session.query(func.avg(Measurement.tobs).label("Average Temp"), func.min(Measurement.tobs).label("Minimum Temp"), func.max(Measurement.tobs).label("Max Temp")) .\
        filter(Measurement.date >=start_date, Measurement.date<=end_date).all()
    
    for row in range:
        average = row[0]
        minimum = row[1]
        maximum = row[2]

    return jsonify(f"Average temperature in range between {start_date} and {end_date} is {average}, minimum temperature is {minimum}, and max temperature is {maximum}")

if __name__ == "__main__":
    app.run(debug=True)