from enum import Enum
from typing import List, Dict, Any, Union
import plotly.graph_objects as go
import plotly.express as px
import networkx as nx
from core.logger import LOGGER
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

class ChartType(Enum):
    LINE = "line"
    BAR = "bar"
    PIE = "pie"
    SCATTER = "scatter"
    HEATMAP = "heatmap"
    NETWORK = "network"
    SANKEY = "sankey"
    TIMELINE = "timeline"

class VisualizationHelper:
    @staticmethod
    def create_line_chart(
        data: pd.DataFrame,
        x_column: str,
        y_column: str,
        title: str = "Line Chart",
        color: str = None
    ) -> go.Figure:
        """Creates an interactive line chart using Plotly."""
        try:
            fig = px.line(data, x=x_column, y=y_column, title=title, color=color)
            return fig
        except Exception as e:
            LOGGER.error(f"Error creating line chart: {str(e)}")
            raise

    @staticmethod
    def create_network_graph(
        nodes: List[str],
        edges: List[tuple],
        node_colors: List[str] = None,
        title: str = "Network Graph"
    ) -> go.Figure:
        """Creates an interactive network graph using Plotly and NetworkX."""
        try:
            G = nx.Graph()
            G.add_nodes_from(nodes)
            G.add_edges_from(edges)
            
            pos = nx.spring_layout(G)
            
            edge_trace = go.Scatter(
                x=[], y=[], line=dict(width=0.5, color='#888'), 
                hoverinfo='none', mode='lines')

            for edge in G.edges():
                x0, y0 = pos[edge[0]]
                x1, y1 = pos[edge[1]]
                edge_trace['x'] += (x0, x1, None)
                edge_trace['y'] += (y0, y1, None)

            node_trace = go.Scatter(
                x=[], y=[], mode='markers+text',
                hoverinfo='text', marker=dict(size=10))

            for node in G.nodes():
                x, y = pos[node]
                node_trace['x'] += (x,)
                node_trace['y'] += (y,)

            fig = go.Figure(data=[edge_trace, node_trace],
                          layout=go.Layout(title=title, showlegend=False))
            return fig
        except Exception as e:
            LOGGER.error(f"Error creating network graph: {str(e)}")
            raise

    @staticmethod
    def create_sankey_diagram(
        source: List[int],
        target: List[int],
        values: List[float],
        labels: List[str],
        title: str = "Sankey Diagram"
    ) -> go.Figure:
        """Creates a Sankey diagram for flow visualization."""
        try:
            fig = go.Figure(data=[go.Sankey(
                node=dict(
                    pad=15,
                    thickness=20,
                    line=dict(color="black", width=0.5),
                    label=labels,
                    color="blue"
                ),
                link=dict(
                    source=source,
                    target=target,
                    value=values
                )
            )])
            fig.update_layout(title_text=title)
            return fig
        except Exception as e:
            LOGGER.error(f"Error creating Sankey diagram: {str(e)}")
            raise

    @staticmethod
    def create_timeline(
        events: List[Dict[str, Any]],
        title: str = "Timeline"
    ) -> go.Figure:
        """Creates an interactive timeline visualization."""
        try:
            df = pd.DataFrame(events)
            fig = px.timeline(
                df, 
                x_start="start_date",
                x_end="end_date",
                y="task",
                color="status",
                title=title
            )
            return fig
        except Exception as e:
            LOGGER.error(f"Error creating timeline: {str(e)}")
            raise

    @staticmethod
    def create_heatmap(
        data_matrix: Union[List[List[float]], pd.DataFrame],
        x_labels: List[str] = None,
        y_labels: List[str] = None,
        title: str = "Heatmap"
    ) -> go.Figure:
        """Creates a heatmap visualization."""
        try:
            if isinstance(data_matrix, list):
                data_matrix = pd.DataFrame(data_matrix)
            
            fig = px.imshow(
                data_matrix,
                labels=dict(x="X", y="Y", color="Value"),
                x=x_labels,
                y=y_labels,
                title=title
            )
            return fig
        except Exception as e:
            LOGGER.error(f"Error creating heatmap: {str(e)}")
            raise

    @staticmethod
    def save_figure(
        fig: go.Figure,
        filename: str,
        format: str = "html"
    ) -> None:
        """Saves the figure to a file."""
        try:
            if format == "html":
                fig.write_html(filename)
            elif format == "png":
                fig.write_image(filename)
            elif format == "json":
                fig.write_json(filename)
            LOGGER.info(f"Successfully saved figure to {filename}")
        except Exception as e:
            LOGGER.error(f"Error saving figure: {str(e)}")
            raise

    @staticmethod
    def create_custom_theme() -> None:
        """Sets up a custom theme for consistent visualization styling."""
        try:
            # Define custom color palette
            colors = ['#2E86AB', '#A23B72', '#F18F01', '#C73E1D', '#3B1F2B']
            sns.set_palette(colors)
            
            # Set style parameters
            plt.style.use('seaborn')
            sns.set_style("whitegrid")
            
            LOGGER.info("Successfully set custom theme")
        except Exception as e:
            LOGGER.error(f"Error setting custom theme: {str(e)}")
            raise
