from flask import Flask, request, jsonify
import pandas as pd
import openai
import json
import os

app = Flask(__name__)

# Configure OpenAI API Key
openai.api_key = 'Enter_Key'


def generate_feedback(prompt):
    """Generate feedback from GPT based on the prompt."""
    response = openai.ChatCompletion.create(
        model="gpt-4",  # Or your preferred GPT model
        messages=[
        {"role": "system", "content": "You are an assistant who extrgenerate feedback."},
        {"role": "user", "content": f"{prompt}"}
    ],
        max_tokens=1500
    )
    return response

def load_data(file_path):
    """Load sales data from CSV or JSON."""
    if file_path.endswith('.csv'):
        return pd.read_csv(file_path)
    elif file_path.endswith('.json'):
        return pd.read_json(file_path)
    else:
        raise ValueError("Unsupported file format")

def get_sales_data():
    """Load and return sales data."""
    
    return load_data('data/sales_performance_data.csv')

@app.route('/api/rep_performance', methods=['GET'])
def rep_performance():
    rep_id = request.args.get('rep_id')
    if not rep_id:
        return jsonify({'error': 'rep_id parameter is required'}), 400
    
    df = get_sales_data()
    if not df.empty:
        df['employee_id'] = df['employee_id'].astype(int)
    
    rep_id = int(rep_id)
    rep_data = df[df['employee_id'] == rep_id]
    rep_data = rep_data.tail(10)
    
    if rep_data.empty:
        return jsonify({'error': 'Sales representative not found'}), 404

    # Example: Summarize rep performance (adjust as necessary)
    # total_sales = rep_data['sales'].sum()
    # performance_summary = f"Sales Representative {rep_id} has total sales of ${total_sales:.2f}."

    prompt = f"Analyze the following sales data for representative {rep_id}: {rep_data.to_dict()}.\nProvide feedback on their performance."
    feedback = generate_feedback(prompt)

    return jsonify({
        'rep_id': rep_id,
        # 'total_sales': total_sales,
        # 'performance_summary': performance_summary,
        'feedback': feedback
    })


if __name__ == '__main__':
    app.run(debug=True)
