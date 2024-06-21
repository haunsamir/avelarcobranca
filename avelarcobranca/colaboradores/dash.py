# colaboradores/dash_app.py
import dash
from dash import dcc, html
import plotly.express as px
import pandas as pd
from django_plotly_dash import DjangoDash
from django.db.models import Count
from colaboradores.models import Interacao

# Extraindo os dados do Django
motivos_data = Interacao.objects.values('motivo').annotate(count=Count('motivo')).order_by('-count')
motivos_df = pd.DataFrame(list(motivos_data))

legendas_data = Interacao.objects.values('legenda').annotate(count=Count('legenda')).order_by('-count')
legendas_df = pd.DataFrame(list(legendas_data))

# Criando a aplicação Dash
app = DjangoDash('SimpleExample')

# Layout do Dash
app.layout = html.Div(children=[
    html.H1(children='Dashboard'),

    dcc.Graph(
        id='motivos-graph',
        figure=px.pie(motivos_df, names='motivo', values='count', title='Motivos')
    ),

    dcc.Graph(
        id='legendas-graph',
        figure=px.pie(legendas_df, names='legenda', values='count', title='Legendas')
    ),
])
