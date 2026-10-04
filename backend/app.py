# Import necessary libraries
import numpy as np
import joblib  # For loading the serialized model
import pandas as pd  # For data manipulation
from flask import Flask, request, jsonify  # For creating the Flask API

# Initialize the Flask application
sale_price_predictor_api = Flask("SuperKart Sales Price Predictor")

# Load the trained machine learning model
model = joblib.load("SuperKart_Model_v1_0.joblib")

# Define a route for the home page (GET request)
@sale_price_predictor_api.get('/')
def home():
    return "Welcome to the Super Kart Product Sales Price Prediction API!"

# Define an endpoint for single property prediction (POST request)
@sale_price_predictor_api.post('/v1/price')
def predict_price():
    # Get the JSON data from the request body
    property_data = request.get_json()

    # Extract relevant features from the JSON data
    sample = {
        'Product_Weight': property_data['Product_Weight'],
        'Product_Sugar_Content': property_data['Product_Sugar_Content'],
        'Product_Allocated_Area': property_data['Product_Allocated_Area'],
        'Product_MRP': property_data['Product_MRP'],
        'Store_Size': property_data['Store_Size'],
        'Store_Location_City_Type': property_data['Store_Location_City_Type'],
        'Store_Type': property_data['Store_Type'],
        'Product_Id_char': property_data['Product_Id_char'],
        'Store_Age_Years': property_data['Store_Age_Years'],
        'Product_Type_Category': property_data['Product_Type_Category']
    }

    # Convert the extracted data into a Pandas DataFrame
    input_data = pd.DataFrame([sample])

    # Make prediction (the model was trained on actual scale, do not use np.exp)
    predicted_sales_price = model.predict(input_data)[0]

    # Convert predicted_price to Python float
    predicted_price = round(float(predicted_sales_price), 2)

    # Return the actual predicted price
    return jsonify({'Predicted Price (in dollars)': predicted_price})


# Define an endpoint for batch prediction (POST request)
@sale_price_predictor_api.post('/v1/salespricebatch')
def predict_rental_price_batch():
    # Get the uploaded CSV file from the request
    file = request.files['file']

    # Read the CSV file into a Pandas DataFrame
    input_data = pd.read_csv(file)

    # Make predictions for all records in the DataFrame
    predicted_sale_prices = model.predict(input_data).tolist()

    # Round predictions
    predicted_prices = [round(float(price), 2) for price in predicted_sale_prices]

    # Create a dictionary of predictions with property IDs as keys
    property_ids = input_data['id'].tolist() if 'id' in input_data.columns else list(range(len(predicted_prices)))
    output_dict = dict(zip(property_ids, predicted_prices))

    # Return the predictions dictionary as a JSON response
    return jsonify(output_dict)

# Run the Flask application if this script is executed directly
if __name__ == '__main__':
    sale_price_predictor_api.run(host='0.0.0.0', port=7860, debug=True)
