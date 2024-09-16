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

    # Calculating multiple metrics for team performance
    total_leads = df['lead_taken'].sum()
    total_revenue_confirmed = df['revenue_confirmed'].sum()
    total_tours_booked = df['tours_booked'].sum()
    total_applications = df['applications'].sum()

    # Additional conversion rates
    avg_apps_per_lead = df['apps_per_lead'].mean()
    avg_apps_per_tour = df['apps_per_tour'].mean()
    avg_tours_per_lead = df['tours_per_lead'].mean()

    # Pipeline and revenue metrics
    total_revenue_pending = df['revenue_pending'].sum()
    revenue_runrate = df['revenue_runrate'].mean()
    avg_deal_value = df['avg_deal_value_30_days'].mean()

    # Convert to native Python types
    total_leads = int(total_leads)
    total_revenue_confirmed = float(total_revenue_confirmed)
    total_tours_booked = int(total_tours_booked)
    total_applications = int(total_applications)
    avg_apps_per_lead = float(avg_apps_per_lead)
    avg_apps_per_tour = float(avg_apps_per_tour)
    avg_tours_per_lead = float(avg_tours_per_lead)
    total_revenue_pending = float(total_revenue_pending)
    revenue_runrate = float(revenue_runrate)
    avg_deal_value = float(avg_deal_value)

    # Summarize performance
    performance_summary = (
        f"Team has generated {total_leads} leads, booked {total_tours_booked} tours, "
        f"and processed {total_applications} applications.\n"
        f"Confirmed revenue: ${total_revenue_confirmed:.2f}, Pending revenue: ${total_revenue_pending:.2f}.\n"
        f"Average deal value: ${avg_deal_value:.2f}, Revenue runrate: ${revenue_runrate:.2f}.\n"
        f"Conversion rates: {avg_tours_per_lead:.2f} tours per lead, {avg_apps_per_tour:.2f} apps per tour."
    )

    # Reduce the amount of data being sent by summarizing and limiting rows
    data_summary = df_limited.to_dict('records')

    # Generate feedback using GPT-4 based on summarized data
    prompt = f"Analyze the following sales data for the team: {data_summary}. Provide feedback on the team's performance."

    try:
        feedback = generate_feedback(prompt)
    except openai.error.RateLimitError as e:
        return jsonify({
            'error': 'Rate limit exceeded, the data is too large to process at once. Please reduce the dataset.'
        }), 429

    return jsonify({
        'total_leads': total_leads,
        'total_revenue_confirmed': total_revenue_confirmed,
        'total_tours_booked': total_tours_booked,
        'total_applications': total_applications,
        'avg_apps_per_lead': avg_apps_per_lead,
        'avg_apps_per_tour': avg_apps_per_tour,
        'avg_tours_per_lead': avg_tours_per_lead,
        'total_revenue_pending': total_revenue_pending,
        'revenue_runrate': revenue_runrate,
        'avg_deal_value': avg_deal_value,
        'feedback': feedback
    })
