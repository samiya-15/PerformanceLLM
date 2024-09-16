from flask import Flask, request, jsonify
import pandas as pd  # Import pandas for CSV handling
from langchain_openai import OpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

# Initialize Flask app
app = Flask(__name__)

# Configure OpenAI API Key
OPENAI_API_KEY = 'Enter_Key_Value'
llm = OpenAI(api_key=OPENAI_API_KEY)

# Define a prompt template
prompt_template = PromptTemplate(
    template="Analyze the following sales data for representative: {rep_data}. Provide detailed feedback on their performance.",
    input_variables=['rep_data']
)

# Create an LLM chain
feedback_chain = LLMChain(llm=llm, prompt=prompt_template)

# Load the sales data CSV file
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
        # Filter the dataframe for the representative's data using `rep_id`
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
    """Generate feedback from GPT based on the sales data, but summarize the data to avoid exceeding the token limit."""
    # Select a few key columns to send to the LLM, reducing the size of the input
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

    # Convert the summarized data to a string to pass to the LLM
    summarized_rep_data = str(summary_data)

    # Generate feedback with the reduced dataset
    feedback = feedback_chain.run(rep_data=summarized_rep_data)
    return feedback

@app.route('/api/rep_performance', methods=['GET'])
def rep_performance():
    # Get the representative ID from query parameters
    rep_id = request.args.get('rep_id')

    if not rep_id:
        return jsonify({"error": "Representative ID is required"}), 400

    # Load the CSV data
    sales_data_df = load_sales_data()
    if sales_data_df is None:
        return jsonify({"error": "Failed to load sales data"}), 500

    # Get the data for the requested representative
    rep_data_dict = get_rep_data(rep_id, sales_data_df)
    if not rep_data_dict:
        return jsonify({"error": f"No data found for representative ID {rep_id}"}), 404

    # Generate feedback using the summarized data
    feedback = generate_feedback(rep_data_dict)

    return jsonify({
        "rep_id": rep_id,
        "feedback": feedback
    })

if __name__ == '__main__':
    app.run(debug=True)
