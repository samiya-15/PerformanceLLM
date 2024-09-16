# @app.route('/api/team_performance', methods=['GET'])
def team_performance():
    df = get_sales_data()
    
    # Example: Calculate total team performance 
    total_sales = df['sales'].sum()
    performance_summary = f"The sales team has total sales of ${total_sales:.2f}."

    prompt = f"Analyze the following sales data for the team: {df.to_dict()}.\nProvide feedback on the team's performance."
    feedback = generate_feedback(prompt)

    return jsonify({
        'total_sales': total_sales,
        'performance_summary': performance_summary,
        'feedback': feedback
    }) 

================================================
@app.route('/api/team_performance', methods=['GET'])
def team_performance():
    # Get the sales data
    df = get_sales_data()

    # Ensure the data types are correct
    df['employee_id'] = df['employee_id'].astype(int)

    # Limit the data sent to the model (e.g., use only the first 5 rows)
    df_limited = df.head(5)

    # Example metrics: Total leads and conversion rates
    total_leads = df['lead_taken'].sum()
    tours_per_lead_rate = df['tours_per_lead'].mean()
    apps_per_tour_rate = df['apps_per_tour'].mean()

    # Convert to native Python types (to avoid int64 issues)
    total_leads = int(total_leads)  # Convert int64 to native int
    tours_per_lead_rate = float(tours_per_lead_rate)  # Convert float64 to native float
    apps_per_tour_rate = float(apps_per_tour_rate)

    # Summarize performance using only the specific columns
    performance_summary = (
        f"The sales team has generated a total of {total_leads} leads.\n"
        f"Average tours per lead: {tours_per_lead_rate:.2f}.\n"
        f"Average applications per tour: {apps_per_tour_rate:.2f}."
    )

    # Reduce the amount of data being sent by summarizing and limiting rows
    data_summary = df_limited.to_dict(2)

    # Generate feedback using GPT-4 based on summarized data
    prompt = f"Analyze the following limited sales data for the team: {data_summary}.\nProvide feedback on the team's performance."
    
    try:
        feedback = generate_feedback(prompt)
    except openai.error.RateLimitError as e:
        return jsonify({
            'error': 'Rate limit exceeded, the data is too large to process at once. Please reduce the dataset.'
        }), 429

    return jsonify({
        'total_leads': total_leads,
        #'tours_per_lead_rate': tours_per_lead_rate,
        #'apps_per_tour_rate': apps_per_tour_rate,
        #'performance_summary': performance_summary,
        'feedback': feedback
    })
