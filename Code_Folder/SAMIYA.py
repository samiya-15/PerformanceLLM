from flask import Flask, request, jsonify
import pandas as pd
from langchain_openai import OpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

# Initialize Flask app
app = Flask(__name__)

# Configure OpenAI API Key
OPENAI_API_KEY = 'Enter_Key'
llm = OpenAI(api_key=OPENAI_API_KEY)

# Define prompt templates
rep_performance_prompt = PromptTemplate(
    template="Analyze the following sales data for representative: {rep_data}. Provide detailed feedback on their performance.",
    input_variables=['rep_data']
)

team_performance_prompt = PromptTemplate(
    template="Analyze the overall sales performance of the team using the following data: {team_data}. Provide insights and recommendations.",
    input_variables=['team_data']
)

# Create LLM chains
feedback_chain = LLMChain(
    llm=llm,
    prompt=rep_performance_prompt
)

team_performance_chain = LLMChain(
    llm=llm,
    prompt=team_performance_prompt
)

# Load sales data CSV file
def load_sales_data():
    try:
        df = pd.read_csv('data/sales_performance_data.csv')  # Replace with your actual CSV path
        return df
    except Exception as e:
        print(f"Error loading CSV: {e}")
        return None

# Filter representative data from the CSV
def get_rep_data(rep_id, df):
    try:
        rep_data = df[df['employee_id'] == int(rep_id)].to_dict(orient='records')
        if rep_data:
            return rep_data[0]  # Return the first matching record as a dictionary
        else:
            return None
    except Exception as e:
        print(f"Error getting representative data: {e}")
        return None

# Generate feedback based on the summarized representative data
def generate_feedback(rep_data):
    summary_data = {
        "employee_id": rep_data.get('employee_id'),
        "employee_name": rep_data.get('employee_name'),
        "lead_taken": rep_data.get('lead_taken'),
        "applications": rep_data.get('applications'),
        "revenue_confirmed": rep_data.get('revenue_confirmed'),
        "revenue_pending": rep_data.get('revenue_pending'),
        "avg_deal_value_30_days": rep_data.get('avg_deal_value_30_days'),
        "estimated_revenue": rep_data.get('estimated_revenue'),
        "tours": rep_data.get('tours')
    }
    summarized_rep_data = str(summary_data)
    feedback = feedback_chain.run(rep_data=summarized_rep_data)
    return feedback

# Endpoint for representative performance
@app.route('/api/rep_performance', methods=['GET'])
def rep_performance():
    rep_id = request.args.get('rep_id')
    if not rep_id:
        return jsonify({"error": "Representative ID is required"}), 400

    sales_data_df = load_sales_data()
    if sales_data_df is None:
        return jsonify({"error": "Failed to load sales data"}), 500

    rep_data_dict = get_rep_data(rep_id, sales_data_df)
    if not rep_data_dict:
        return jsonify({"error": f"No data found for representative ID {rep_id}"}), 404

    feedback = generate_feedback(rep_data_dict)
    return jsonify({
        "rep_id": rep_id,
        "feedback": feedback
    })

import logging
logging.basicConfig(level=logging.DEBUG)

@app.route('/api/team_performance', methods=['POST'])
def post_team_performance():
    logging.debug("Headers: %s", request.headers)
    logging.debug("Body: %s", request.data)
    data = request.json
    if not data or 'summary' not in data:
        return jsonify({"error": "Summary field is required in the JSON payload"}), 400

    summary = data['summary']
    sales_data_df = load_sales_data()
    if sales_data_df is None:
        return jsonify({"error": "Failed to load sales data"}), 500

    team_data = sales_data_df.to_dict(orient='records')
    team_data_summary = str(team_data) + " " + summary
    insights = team_performance_chain.run(team_data=team_data_summary)
    return jsonify({
        "insights": insights
    })

@app.route('/api/performance_trends', methods=['POST'])
def post_performance_trends():
    try:
        logging.debug("Headers: %s", request.headers)
        logging.debug("Body: %s", request.data)

        data = request.json
        if not data or 'time_period' not in data:
            return jsonify({"error": "Time period is required in the JSON payload"}), 400

        time_period = data['time_period']
        sales_data_df = load_sales_data()
        if sales_data_df is None:
            return jsonify({"error": "Failed to load sales data"}), 500

        trend_summary = f"Trends for the period: {time_period}."
        return jsonify({
            "time_period": time_period,
            "trend_summary": trend_summary
        })
    except Exception as e:
        logging.error("Unexpected error: %s", str(e))
        return jsonify({"error": "An unexpected error occurred"}), 500


if __name__ == '__main__':
    app.run(debug=True)
