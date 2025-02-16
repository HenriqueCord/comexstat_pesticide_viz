# seasonal_decompose_plot.py

import plotly.graph_objects as go
import plotly.express as px


def plot_trend_with_bar(
    data,
    x_key,
    y_key,
    trend_arr,
    color_key,
    color_map,
    x_title="Date",
    y_title="Net Weight (kg)",
):
    """
    Generate a bar plot with a trendline overlay using Plotly.
    """
    # Bar plot
    fig = px.bar(
        data,
        x=x_key,
        y=y_key,
        color=color_key,
        color_discrete_map=color_map,
    )

    # Trendline overlay
    fig.add_trace(
        go.Scatter(
            x=trend_arr.index,
            y=trend_arr.values,
            mode="lines",
            name="Trend",
            line=dict(color="cornsilk", width=2.5),
        )
    )

    # Layout updates
    fig.update_layout(
        xaxis_title=x_title,
        yaxis_title=y_title,
        colorway=px.colors.qualitative.Dark24,
    )

    return fig


def plot_bar_by_class(data, x_key, y_key, color_key, color_map, title):
    """
    Generate a bar chart showing the share by product class.
    """
    fig = px.bar(
        data,
        x=x_key,
        y=y_key,
        color=color_key,
        color_discrete_map=color_map,
        title=title,
    )

    # Adjust layout
    fig.update_layout(
        xaxis_title=x_key,
        yaxis_title=y_key,
        template="plotly_white",
    )

    return fig


def plot_seasonal_decompose(seasonal_arr, residual_arr):
    """
    Generate a Plotly figure showing the seasonal decomposition components.
    """
    fig_decompose = go.Figure()

    # Add seasonal component (solid line)
    fig_decompose.add_trace(
        go.Scatter(
            x=seasonal_arr.index,
            y=seasonal_arr.values,
            mode="lines",
            name="Seasonal",
            line=dict(color="lightgreen", width=1.5),
        )
    )

    # Add residual component (scatter points)
    fig_decompose.add_trace(
        go.Scatter(
            x=residual_arr.index,
            y=residual_arr.values,
            mode="markers",
            name="Residuals",
            marker=dict(color="tomato", size=8, symbol="circle-open-dot"),
        )
    )

    # Update layout
    fig_decompose.update_layout(
        xaxis_title="Time",
        yaxis_title="Weight (kg)",
        legend=dict(title="Components"),
        template="plotly_white",
    )

    return fig_decompose


def plot_choropleth(
    data,
    country_code_key,
    value_key,
    color_scale="Plasma",
):
    """
    Generate a choropleth map using Plotly Graph Objects.
    """
    # Create the choropleth map
    fig = go.Figure(
        go.Choropleth(
            locations=data[country_code_key],
            z=data[value_key],
            locationmode="ISO-3",
            colorscale=color_scale,
            colorbar=dict(title=value_key),
            text=data[country_code_key],  # Hover information
        )
    )

    # Update layout
    fig.update_layout(
        geo=dict(
            showframe=False,
            showcoastlines=True,
            projection_type="equirectangular",
        ),
    )

    return fig
