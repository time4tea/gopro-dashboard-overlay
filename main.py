import plotly.graph_objects as go

fig = go.Figure(go.Indicator(
    mode="gauge+number+delta",
    value=23,
    domain={'x': [0, 1], 'y': [0, 1]},
    title={'text': "Speed",
           'font': {'size': 24}},
    delta={'reference': 23, 'increasing': {'color': "RebeccaPurple"}},
    gauge={
        'axis': {
            'range': [None, 40],
            'tickwidth': 1, 'tickcolor': "darkblue"},
        'bar': {'color': "green"},
        'bgcolor': "white",
        'borderwidth': 2,
        'bordercolor': "gray",
        # 'steps': [
        #     {'range': [0, 10], 'color': 'cyan'},
        #     {'range': [10, 20], 'color': 'royalblue'}],
        'threshold': {
            'line': {'color': "red", 'width': 4},
            'thickness': 0.75,
            'value': 35}}))

fig.update_layout(paper_bgcolor="white", font={'color': "darkblue", 'family': "Arial"})

fig.show()
