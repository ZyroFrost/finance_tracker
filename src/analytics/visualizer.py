import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from utils import get_format_amount

sns.set_style("whitegrid") # Set the style of the plot, such as the background color (white) and grid lines
plt.rcParams['figure.figsize'] = (10, 6) # Set the size of the plot

class FinanceVisualizer:    
    @staticmethod
    def plot_category_spending(category_data, currency):
        """Create a bar chart to visualize spending by category."""
        if category_data.empty:
            return None
        
        # Format tiền từ utils.py
        category_data = category_data.copy()
        category_data["Total_text"] = category_data["Total"].apply(
            lambda x: get_format_amount(currency, x)
        )
        
        fig = px.bar(
            category_data,
            x='Category',
            y='Total',
            text='Total_text', # STRING ĐÃ FORMAT
            title='Spending by Category',
            #labels={'Total': 'Amount', 'Category': 'Category'},
            color='Category',
            #color_discrete_sequence=px.colors.qualitative.Set2,
            color_discrete_sequence=px.colors.qualitative.Pastel1,
            #color_discrete_sequence=px.colors.qualitative.G10,
            # color_discrete_sequence=px.colors.sequential.Plasma   
        )
        
        fig.update_traces(
            #texttemplate='%{text}',       # format tiền (ko dùng vì phải lấy format chuẩn từ utils.py)
            textposition='outside',         # hiện trên đầu cột
            hovertemplate="<b>%{x}</b><br>%{text}<extra></extra>"
        )

        fig.update_yaxes(
            tickformat=",",          # 2,800,000
            exponentformat="none"    # ❌ M, K
        )
        
        fig.update_layout(
            xaxis_title="Category",
            xaxis_tickangle=-45,
            height=500,
            # yaxis_tickformat='$,.0f',       # format trục Y
            uniformtext_minsize=10,
            uniformtext_mode='hide'
        )
        return fig
    
    @staticmethod
    def plot_pie_chart(category_data):
        """Create a pie chart to visualize spending by category."""
        if category_data.empty:
            return None
        
        fig = px.pie(
            category_data,
            values='Total',
            names='Category',
            title='Expense Distribution by Category',
            color='Category',
            #color_discrete_sequence=px.colors.qualitative.Set2,
            color_discrete_sequence=px.colors.qualitative.Pastel1,
            #color_discrete_sequence=px.colors.qualitative.G10,
            #color_discrete_sequence=px.colors.sequential.Plasma,
            hole=0.4)
        
        fig.update_traces(textposition='inside', textinfo='percent+label')
        fig.update_layout(
            showlegend=False,
            height=500
        )
        return fig
    
    @staticmethod
    def plot_monthly_trend(monthly_data, currency: str):
        if monthly_data.empty:
            return None

        fig = go.Figure()

        if "Expense" in monthly_data.columns:
            expense_text = [
                get_format_amount(currency, v)
                for v in monthly_data["Expense"]
            ]

            fig.add_trace(go.Scatter(
                x=monthly_data.index,
                y=monthly_data["Expense"],
                mode="lines+markers",
                name="Expenses",
                hovertext=expense_text,
                hovertemplate="Expenses: %{hovertext}<extra></extra>",
                line=dict(color="red", width=2)
            ))

        if "Income" in monthly_data.columns:
            income_text = [
                get_format_amount(currency, v)
                for v in monthly_data["Income"]
            ]

            fig.add_trace(go.Scatter(
                x=monthly_data.index,
                y=monthly_data["Income"],
                mode="lines+markers",
                name="Income",
                hovertext=income_text,
                hovertemplate="Income: %{hovertext}<extra></extra>",
                line=dict(color="green", width=2)
            ))

        fig.update_layout(
            title="Monthly Income vs Expenses Trend",
            xaxis_title="Month",
            yaxis_title="Amount",
            hovermode="x unified",
            height=500
        )

        return fig
