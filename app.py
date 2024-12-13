# Import the dependencies.
import os
import pandas as pd
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from flask import Flask, jsonify, render_template
from dotenv import load_dotenv

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Database Setup
#################################################

# Load environment variables from .env
load_dotenv()

# Call the database URL from the .env file
DATABASE_URL = os.getenv('DATABASE_URL')

# Create SQLAlchemy engine
engine = create_engine(DATABASE_URL)

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Additional Engine Configs
conn = engine.connect()
session = Session(engine)

#################################################
# Flask Routes
#################################################

# Defining the homepage
@app.route("/")
def index():
    """Return the homepage."""
    return render_template("index.html")

# Defining the route to the state pages
@app.route("/state_list")
def states():
    #Running a query to find all unique states and return a list of them
    states = pd.read_sql("SELECT state FROM medicare_data", engine)
    state_list = states['state'].unique()
    state_list = state_list.tolist()
    state_list = sorted(state_list)
    return jsonify(state_list)

# Route to National Stats
@app.route("/national_stats")
def national_stats():
    # Query to fetch only relevant columns for the given state
    query = """
        SELECT * 
        FROM stats_table 
    """
    # Execute query and store result in a DataFrame
    national_stats_data = pd.read_sql(query, engine)
    
    # Convert DataFrame to a list of dictionaries
    result = national_stats_data.to_dict(orient="records")
    
    # Return the result as a JSON response
    return jsonify(result)

# Route to the StateDB
@app.route("/db_info/<state>")
def db_info(state):
    
    query = """
        SELECT zip, mdc_code,mdc_desc, discharges, avg_covered_charge, avg_total_payment, avg_medicare_payment, avg_oop
        FROM medicare_data 
        WHERE state = %s
    """
    # Execute query and store result in a DataFrame
    state_data = pd.read_sql(query, engine, params=(state,))
    
    # Convert DataFrame to a list of dictionaries
    result = state_data.to_dict(orient="records")
    
    # Return the result as a JSON response
    return jsonify(result)

# Run the Application
if __name__ == '__main__':
    app.run(debug=True)