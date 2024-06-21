# urls.py
from django.urls import path
from .views import (
    login_view, logout_view, index_view, distribuir_lista_view, create_user_view,
    listas_colaborador_view, detalhes_lista_view, update_interaction, caderno_view,
    agenda_view, adicionar_evento, adicionar_codigo_view, processar_pagamentos_view, 
    remover_pagamento_view, resultados, index_adm_view, user_list_view, edit_user_view,
    delete_user_view, change_password_view, agenda_adm_view, resultados_adm_view, remover_pagamento_adm_view, dashboard_view,
    api_get_data, marcar_como_lido, dashboard_pagamentos_view, material_convalescente_view  # Adicionar a nova view
)
from .views import search_code_view
from . import views
from django.contrib.staticfiles.views import serve

urlpatterns = [
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('index/', index_view, name='index'),
    path('index_adm/', index_adm_view, name='index_adm'),
    path('distribuir_lista/', distribuir_lista_view, name='distribuir_lista'),
    path('create_user/', create_user_view, name='create_user'),
    path('user_list/', user_list_view, name='user_list'),
    path('edit_user/<int:user_id>/', edit_user_view, name='edit_user'),
    path('delete_user/<int:user_id>/', delete_user_view, name='delete_user'),
    path('minhas_listas/', listas_colaborador_view, name='minhas_listas'),
    path('minhas_listas/<uuid:id_lista>/', detalhes_lista_view, name='detalhes_lista'),
    path('update_interaction/<int:cliente_id>/', update_interaction, name='update_interaction'),
    path('caderno/', caderno_view, name='caderno'),
    path('agenda/', agenda_view, name='agenda'),
    path('adicionar_evento/', adicionar_evento, name='adicionar_evento'),
    path('caderno/adicionar/', adicionar_codigo_view, name='adicionar_codigo'),
    path('caderno/processar/', processar_pagamentos_view, name='processar_pagamentos'),
    path('remover_pagamento/', remover_pagamento_view, name='remover_pagamento'),
    path('remover_pagamento_adm/', remover_pagamento_adm_view, name='remover_pagamento_adm'),
    path('resultados/', resultados, name='resultados'),
    path('change_password/<int:user_id>/', change_password_view, name='change_password'),
    path('agenda_adm/', agenda_adm_view, name='agenda_adm'),
    path('resultados_adm/', resultados_adm_view, name='resultados_adm'),
    path('dashboard/', dashboard_view, name='dashboard'),
    path('dashboard_pagamentos/', dashboard_pagamentos_view, name='dashboard_pagamentos'),
    path('api/get-data/', api_get_data, name='api_get_data'),
    path('marcar_como_lido/', marcar_como_lido, name='marcar_como_lido'),
    path('material_convalescente/', material_convalescente_view, name='material_convalescente'),  # Nova URL
    path('remover_material_convalescente/<int:id>/', views.remover_material_convalescente, name='remover_material_convalescente'),
    path('search_code/<str:id_lista>/<str:codigo_cliente>/', search_code_view, name='search_code'),
    path('loop/', views.loop_view, name='loop'),
    path('ticker-data/', views.ticker_data, name='ticker_data'),

]
