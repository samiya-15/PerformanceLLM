@app.route('/api/performance_trends', methods=['GET'])
def performance_trends():
    # Get time period from query parameters (default to 'monthly')
    time_period = request.args.get('time_period', 'monthly')

    # Fetch and process sales data
    df = get_sales_data()

    # Ensure the 'dated' column is in datetime format
    df['dated'] = pd.to_datetime(df['dated'], errors='coerce')

    # Check for invalid or missing dates
    if df['dated'].isnull().any():
        # Log the rows with invalid dates for debugging
        invalid_dates = df[df['dated'].isnull()]
        print("Rows with invalid date format:\n", invalid_dates)

        # Optionally, remove rows with invalid dates
        df = df.dropna(subset=['dated'])
        if df.empty:
            return jsonify({'error': 'No valid date entries in the data'}), 400

    # Set the index to the 'dated' column
    df.set_index('dated', inplace=True)

    # Choose the correct time period for resampling
    if time_period == 'monthly':
        trends = df.resample('M').sum()['revenue_confirmed']  # Replace 'revenue_confirmed' with your actual column
    elif time_period == 'quarterly':
        trends = df.resample('Q').sum()['revenue_confirmed']
    else:
        return jsonify({'error': 'Invalid time_period parameter. Use "monthly" or "quarterly".'}), 400

    # Prepare prompt for GPT-4 analysis
    prompt = f"Analyze the sales trends over the {time_period} period: {trends.to_dict()}.\nProvide a forecast for future performance."

    try:
        forecast = generate_feedback(prompt)  # Assuming this function generates the GPT-4 forecast
    except openai.error.RateLimitError:
        return jsonify({'error': 'Rate limit exceeded. Please try again later.'}), 429

    # Format the trends to return as YYYY-MM or YYYY-Q
    trends_dict = trends.to_dict()
    
    if time_period == 'monthly':
        trends_dict = {key.strftime('%Y-%m'): value for key, value in trends_dict.items()}
    elif time_period == 'quarterly':
        trends_dict = {f"{key.year}-Q{(key.month - 1) // 3 + 1}": value for key, value in trends_dict.items()}

    # Return the trend and forecast
    return jsonify({
        'time_period': time_period,
        'trends': trends_dict,
        'forecast': forecast
    })
