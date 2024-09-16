@app.route('/api/team_performance', methods=['GET'])
def team_performance():
    # Get the sales data
    df = get_sales_data()
    
    if df is None or df.empty:
        return jsonify({'error': 'No data available'}), 404

    # Ensure the data types are correct
    df['employee_id'] = df['employee_id'].astype(int)

    # Limit the data sent to the model (e.g., use only the first 5 rows)
    df_limited = df.head(5)

    # Calculate both total leads and total confirmed revenue
    total_leads = df['lead_taken'].sum()
    total_revenue_confirmed = df['revenue_confirmed'].sum()

    # Conversion rates
    tours_per_lead_rate = df['tours_per_lead'].mean()
    apps_per_tour_rate = df['apps_per_tour'].mean()

    # Convert to native Python types (to avoid int64 issues)
    total_leads = int(total_leads)  # Convert int64 to native int
    total_revenue_confirmed = float(total_revenue_confirmed)  # Convert to native float
    tours_per_lead_rate = float(tours_per_lead_rate)  # Convert to native float
    apps_per_tour_rate = float(apps_per_tour_rate)

    # Summarize performance using only the specific columns
    performance_summary = (
        f"The sales team has generated a total of {total_leads} leads and a total confirmed revenue of ${total_revenue_confirmed:.2f}.\n"
        f"Average tours per lead: {tours_per_lead_rate:.2f}.\n"
        f"Average applications per tour: {apps_per_tour_rate:.2f}."
    )

    # Reduce the amount of data being sent by summarizing and limiting rows
    data_summary = df_limited.to_dict('records')

    # Generate feedback using GPT-4 based on summarized data
    prompt = f"Analyze the following limited sales data for the team: {data_summary}.\nProvide feedback on the team's performance."

    try:
        # FOR TESTING: Manually raise RateLimitError to simulate condition
        raise openai.error.RateLimitError("Simulated rate limit exceeded.")
        
        # feedback = generate_feedback(prompt)  # Uncomment in actual use
    except openai.error.RateLimitError as e:
        return jsonify({
            'error': 'Rate limit exceeded, the data is too large to process at once. Please reduce the dataset.'
        }), 429

    return jsonify({
        'total_leads': total_leads,
        'total_revenue_confirmed': total_revenue_confirmed,
        'feedback': feedback  # In real scenario, feedback would be generated
    })

