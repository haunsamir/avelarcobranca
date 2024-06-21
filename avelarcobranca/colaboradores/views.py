from datetime import date
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .models import Evento, ListaDistribuida
from django.db.models import Count

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            if user.is_superuser:
                return redirect('index_adm')
            else:
                return redirect('index')
        else:
            messages.error(request, 'Usuário ou senha incorretos')
            return render(request, 'colaboradores/login.html')
    return render(request, 'colaboradores/login.html')


def logout_view(request):
    logout(request)
    return redirect('login')

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Evento, ListaDistribuida, PagamentoRemovido
from datetime import date

@login_required
def index_view(request):
    user = request.user
    eventos_hoje = Evento.objects.filter(colaborador=user, data=date.today())
    listas_hoje = ListaDistribuida.objects.filter(colaborador=user, data_distribuicao__date=date.today()).values('nome_lista', 'id_lista').distinct()
    picotes_excluidos = PagamentoRemovido.objects.filter(colaborador_original=user, visible=True)

    context = {
        'user': user,
        'eventos_hoje': eventos_hoje,
        'listas_hoje': listas_hoje,
        'picotes_excluidos': picotes_excluidos,
    }
    return render(request, 'colaboradores/index.html', context)


from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from .forms import ListaDistribuidaForm
from .models import ListaDistribuida, CustomUser
import uuid

@login_required
@user_passes_test(lambda u: u.is_superuser)
def distribuir_lista_view(request):
    tipo_lista = request.GET.get('tipo_lista', 'regular')

    if request.method == 'POST':
        form = ListaDistribuidaForm(request.POST, tipo_lista=tipo_lista)
        if form.is_valid():
            lista = form.cleaned_data['lista']
            nome_lista = form.cleaned_data['nome_lista']
            colaboradores = form.cleaned_data['colaboradores']
            tipo_lista = form.cleaned_data['tipo_lista']

            linhas = lista.split('\n')
            num_colaboradores = colaboradores.count()
            id_lista = uuid.uuid4()  # Gerar um UUID para a lista

            distribuicoes = []
            for i, linha in enumerate(linhas):
                if linha.strip():  # Ignorar linhas vazias
                    codigo, nome = linha.split('\t')
                    colaborador = colaboradores[i % num_colaboradores]
                    distribuicao = ListaDistribuida.objects.create(
                        id_lista=id_lista,
                        codigo=codigo,
                        nome=nome,
                        nome_lista=nome_lista,
                        colaborador=colaborador,
                        tipo_lista=tipo_lista
                    )
                    distribuicoes.append(distribuicao)

            context = {
                'form': form,
                'distribuicoes': distribuicoes,
            }
            return render(request, 'colaboradores/distribuir_lista.html', context)
    else:
        form = ListaDistribuidaForm(initial={'tipo_lista': tipo_lista}, tipo_lista=tipo_lista)

    colaboradores = CustomUser.objects.filter(user_type='colaborador', colaborador_type=tipo_lista)
    form.fields['colaboradores'].queryset = colaboradores

    return render(request, 'colaboradores/distribuir_lista.html', {'form': form})


from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import CustomUserCreationForm

@login_required
def create_user_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Usuário criado com sucesso!')
            return redirect('create_user')
        else:
            messages.error(request, 'Erro ao criar usuário. Verifique os dados e tente novamente.')
    else:
        form = CustomUserCreationForm()
    return render(request, 'colaboradores/create_user.html', {'form': form})

from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import ListaDistribuida, Interacao
from django.db.models import Count
from django.db.models import Max

@login_required
def listas_colaborador_view(request):
    colaborador = request.user
    listas = ListaDistribuida.objects.filter(colaborador=colaborador) \
        .values('id_lista', 'nome_lista') \
        .annotate(data_distribuicao_max=Max('data_distribuicao')) \
        .order_by('-data_distribuicao_max')

    context = {
        'listas': listas
    }
    print(f"Colaborador ID: {colaborador.id}")
    print(f"Total de listas encontradas: {listas.count()}")
    return render(request, 'colaboradores/minhas_listas.html', context)

from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import ListaDistribuida, Interacao
from django.http import HttpResponseNotFound

@login_required
def detalhes_lista_view(request, id_lista):
    colaborador = request.user
    listas = ListaDistribuida.objects.filter(id_lista=id_lista, colaborador=colaborador)

    if not listas.exists():
        return HttpResponseNotFound("Lista não encontrada ou você não tem permissão para visualizá-la.")

    nome_lista = listas.first().nome_lista  # Supondo que há um campo 'nome_lista' na model ListaDistribuida
    quantidade_clientes = listas.count()  # Adiciona a quantidade de clientes na lista

    linhas = []
    interacoes = {}
    for lista in listas:
        if lista.codigo and lista.nome:  # Assegurar que código e nome não estão vazios
            linhas.append({
                'codigo_cliente': lista.codigo,
                'nome_cliente': lista.nome,
                'outras_informacoes': ''  # Ajustar conforme necessário
            })
            # Adiciona as interações já existentes
            interacao = Interacao.objects.filter(
                codigo_cliente=lista.codigo,
                colaborador=colaborador,
                lista_distribuida_id=lista.id_lista  # Verificar também lista_distribuida_id
            ).first()
            if interacao:
                interacoes[lista.codigo] = {
                    'legenda': interacao.legenda,
                    'motivo': interacao.motivo,
                    'observacao': interacao.observacao
                }
            else:
                interacoes[lista.codigo] = {
                    'legenda': '',
                    'motivo': '',
                    'observacao': ''
                }

    context = {
        'id_lista': id_lista,
        'nome_lista': nome_lista,  # Passar o nome da lista para o contexto
        'linhas': linhas,
        'interacoes': interacoes,  # Passar as interações para o contexto
        'user': request.user,  # Passar o usuário logado para o contexto
        'quantidade_clientes': quantidade_clientes,  # Adiciona a quantidade de clientes ao contexto
    }
    return render(request, 'colaboradores/detalhes_lista.html', context)


from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import ListaDistribuida

@login_required
def minhas_listas_view(request):
    colaborador = request.user
    listas = ListaDistribuida.objects.filter(colaborador=colaborador).order_by('-data_distribuicao')

    context = {
        'listas': listas
    }
    return render(request, 'colaboradores/minhas_listas.html', context)



from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from .models import Interacao

@csrf_exempt
@login_required
def update_interaction(request, cliente_id):
    if request.method == 'POST':
        try:
            # Parse data from request
            data = json.loads(request.body)
            legenda = data.get('legenda')
            motivo = data.get('motivo')
            observacao = data.get('observacao')
            lista_distribuida_id = data.get('lista_distribuida_id')

            # Find existing interaction or create a new one
            interacao, created = Interacao.objects.get_or_create(
                codigo_cliente=cliente_id,
                lista_distribuida_id=lista_distribuida_id,
                defaults={'colaborador': request.user}
            )

            # Update the fields if they are provided
            if legenda is not None:
                interacao.legenda = legenda
            if motivo is not None:
                interacao.motivo = motivo
            if observacao is not None:
                interacao.observacao = observacao
            
            interacao.save()

            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

@login_required
def agenda_view(request):
    eventos = Evento.objects.filter(colaborador=request.user).order_by('data')
    return render(request, 'colaboradores/agenda.html', {'eventos': eventos})

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from .models import Evento

@csrf_exempt
@login_required
def adicionar_evento(request):
    if request.method == 'POST':
        try:
            colaborador = request.user
            data = request.POST.get('data')
            codigo = request.POST.get('codigo')
            observacao = request.POST.get('observacao')

            # Crie o evento e salve-o no banco de dados
            evento = Evento.objects.create(
                colaborador=colaborador,
                data=data,
                codigo=codigo,
                observacao=observacao
            )

            # Retorne uma resposta JSON indicando o sucesso e os detalhes do evento criado
            return JsonResponse({'status': 'success', 'evento': {
                'id': evento.id,
                'data': evento.data,
                'codigo': evento.codigo,
                'observacao': evento.observacao
            }})
        except Exception as e:
            # Em caso de erro, retorne uma resposta JSON indicando o erro ocorrido
            return JsonResponse({'status': 'error', 'message': str(e)})
    # Se a solicitação não for POST, retorne uma resposta JSON indicando um método de solicitação inválido
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

from datetime import datetime
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Caderno, PagamentoTransferido
from django.db import connection
import logging
import json

logger = logging.getLogger(__name__)

@login_required
def caderno_view(request):
    colaborador = request.user
    tabela_picotes = 'picotes_filial' if colaborador.colaborador_type == 'filial' else 'picotes_moc'

    if request.method == 'POST':
        if 'remover_pagamento' in request.POST:
            codigo_cliente = request.POST['codigo_cliente']
            logger.debug(f"Removendo pagamento para o código cliente: {codigo_cliente}")
            Caderno.objects.filter(colaborador=request.user, codigo_cliente=codigo_cliente).delete()
            return redirect('caderno')

        if 'transferir_pagamentos' in request.POST:
            pagamentos_encontrados_json = request.POST.get('pagamentos_encontrados_json')
            if pagamentos_encontrados_json:
                try:
                    pagamentos_encontrados = json.loads(pagamentos_encontrados_json)
                    logger.debug(f"Transferindo pagamentos: {pagamentos_encontrados}")
                    for pagamento in pagamentos_encontrados:
                        for parcela in pagamento['parcelas']:
                            logger.debug(f"Transferindo pagamento: {pagamento['codigo_cliente']}, {pagamento['titular']}, {pagamento['data_pgto']}, {parcela}")
                            PagamentoTransferido.objects.create(
                                codigo_cliente=pagamento['codigo_cliente'],
                                nome_titular=pagamento['titular'],
                                data_pgto=datetime.strptime(pagamento['data_pgto'], '%d de %B de %Y').date(),
                                parcela=parcela,
                                colaborador=request.user
                            )
                            Caderno.objects.filter(colaborador=request.user, codigo_cliente=pagamento['codigo_cliente']).delete()
                except json.JSONDecodeError:
                    logger.error("Erro ao decodificar JSON")
            return redirect('caderno')

        codigo_cliente = request.POST['codigo_cliente']
        data_baixa = request.POST['data_baixa']
        data_baixa = datetime.strptime(data_baixa, "%Y-%m-%d").date()
        Caderno.objects.create(colaborador=request.user, codigo_cliente=codigo_cliente, data_baixa=data_baixa)
        return redirect('caderno')

    caderno = Caderno.objects.filter(colaborador=colaborador)

    pagamentos_encontrados = {}
    pagamentos_nao_encontrados = []

    for item in caderno:
        codigo_cliente = item.codigo_cliente
        data_baixa = item.data_baixa.strftime('%Y-%m-%d')  # Formato correto para a query

        with connection.cursor() as cursor:
            query = f"""
                SELECT `Número`, `Titular`, `Data Venc.`, `Data Pgto.`
                FROM {tabela_picotes}
                WHERE `Número` = %s AND `Data Pgto.` = %s
            """
            logger.debug(f"Executando query: {query} com parâmetros: {codigo_cliente}, {data_baixa}")
            cursor.execute(query, [codigo_cliente, data_baixa])

            pagamentos = cursor.fetchall()
            logger.debug(f"Pagamentos no banco de dados para código {codigo_cliente} e data {data_baixa}: {pagamentos}")

            if pagamentos:
                for pagamento in pagamentos:
                    data_vencimento = datetime.strptime(pagamento[2], "%Y-%m-%d").date()
                    parcela_formatada = data_vencimento.strftime('%m/%y')

                    if codigo_cliente not in pagamentos_encontrados:
                        pagamentos_encontrados[codigo_cliente] = {
                            'codigo_cliente': codigo_cliente,
                            'titular': pagamento[1],
                            'data_pgto': datetime.strptime(pagamento[3], "%Y-%m-%d").date(),
                            'parcelas': [parcela_formatada]
                        }
                    else:
                        pagamentos_encontrados[codigo_cliente]['parcelas'].append(parcela_formatada)
            else:
                pagamento_dict = {
                    'codigo_cliente': codigo_cliente,
                    'data_baixa': item.data_baixa.strftime('%d %B %Y')  # Formata a data de baixa para exibição
                }
                pagamentos_nao_encontrados.append(pagamento_dict)

    for pagamento in pagamentos_encontrados.values():
        pagamento['data_pgto'] = pagamento['data_pgto'].strftime('%d de %B de %Y')

    logger.debug(f"Pagamentos encontrados: {pagamentos_encontrados}")

    context = {
        'caderno': caderno,
        'pagamentos_encontrados': list(pagamentos_encontrados.values()),
        'pagamentos_nao_encontrados': pagamentos_nao_encontrados,
    }
    return render(request, 'colaboradores/caderno.html', context)
    

def buscar_pagamentos(codigo_cliente, data_baixa):
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT `Número`, `Titular`, `Data Venc.`, `Data Pgto.`
            FROM picotes_moc
            WHERE `Número` = %s AND `Data Pgto.` = %s
        """, [codigo_cliente, data_baixa])
        pagamentos = cursor.fetchall()
        logger.debug(f"Pagamentos no banco de dados: {pagamentos}")
        return pagamentos

@login_required
def adicionar_codigo_view(request):
    if request.method == 'POST':
        codigo_cliente = request.POST['codigo_cliente']
        data_baixa = request.POST['data_baixa']
        Caderno.objects.create(colaborador=request.user, codigo_cliente=codigo_cliente, data_baixa=data_baixa)
        return redirect('caderno')
    return redirect('caderno')

import logging
from babel.dates import parse_date
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import PagamentoTransferido
from datetime import datetime

logger = logging.getLogger(__name__)

def processar_parcela(codigo_cliente, parcela, nome_titular, data_pgto_str, colaborador_id):
    try:
        # Verificar se a data está no formato esperado
        if data_pgto_str:
            logger.debug(f'Formatando data de pagamento: {data_pgto_str}')
            try:
                # Converter a data manualmente para o formato datetime
                data_pgto = datetime.strptime(data_pgto_str, '%d de %B de %Y')
                logger.debug(f'Data pagamento convertida: {data_pgto}')
            except Exception as e:
                logger.error(f'Erro ao converter data de pagamento: {e}')
                return False, f'Erro ao converter data de pagamento: {e}'
        else:
            logger.error('Data de pagamento não fornecida')
            return False, 'Data de pagamento não fornecida'

        # Verificar se o registro já existe para o mesmo código_cliente, parcela e colaborador_id
        if PagamentoTransferido.objects.filter(codigo_cliente=codigo_cliente, parcela=parcela, colaborador_id=colaborador_id).exists():
            logger.error(f'Pagamento já registrado para o código {codigo_cliente}, parcela {parcela} e colaborador {colaborador_id}')
            return False, 'Pagamento já registrado para este cliente e parcela.'

        # Inserir no banco de dados
        PagamentoTransferido.objects.create(
            codigo_cliente=codigo_cliente,
            nome_titular=nome_titular,
            data_pgto=data_pgto,
            parcela=parcela,
            colaborador_id=colaborador_id  # Incluindo o colaborador_id
        )
        logger.debug(f'Parcela {parcela} do código {codigo_cliente} inserida na tabela PagamentoTransferido')
        return True, 'Pagamento registrado com sucesso.'
    except Exception as e:
        logger.error(f'Erro ao inserir no banco de dados: {e}')
        return False, f'Erro ao inserir no banco de dados: {e}'

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required

@csrf_exempt
@login_required
def processar_pagamentos_view(request):
    if request.method == 'POST':
        try:
            parcelas_selecionadas = request.POST.getlist('parcelas')
            sucesso = True
            error_messages = []

            for parcela_full in parcelas_selecionadas:
                try:
                    codigo_cliente, parcela = parcela_full.split('_', 1)
                except ValueError:
                    sucesso = False
                    error_messages.append(f'Formato de parcela inválido: {parcela_full}')
                    continue

                nome_titular = request.POST.get(f'nome_titular_{codigo_cliente}')
                data_pgto_str = request.POST.get(f'data_pgto_{codigo_cliente}')
                colaborador_id = request.user.id

                if not (codigo_cliente and parcela and nome_titular and data_pgto_str):
                    sucesso = False
                    error_messages.append('Dados insuficientes fornecidos.')
                    continue

                parcela_sucesso, mensagem = processar_parcela(codigo_cliente, parcela, nome_titular, data_pgto_str, colaborador_id)
                if not parcela_sucesso:
                    sucesso = False
                    error_messages.append(mensagem)
                else:
                    # Remover o registro do Caderno após a inserção
                    Caderno.objects.filter(codigo_cliente=codigo_cliente, colaborador_id=colaborador_id).delete()

            if sucesso:
                return JsonResponse({'status': 'success', 'message': 'Pagamentos processados com sucesso!'})
            else:
                return JsonResponse({'status': 'error', 'message': 'Erro: ' + '; '.join(error_messages)})

        except Exception as e:
            return JsonResponse({'status': 'error', 'message': f'Erro inesperado ao processar pagamentos: {e}'}, status=500)
    else:
        return JsonResponse({'status': 'error', 'message': 'Método inválido'}, status=400)

@login_required
@csrf_exempt
def remover_pagamento_view(request):
    if request.method == 'POST':
        try:
            codigo_cliente = request.POST.get('codigo_cliente')
            colaborador_id = request.user.id

            # Exclui todos os registros do cliente para o colaborador atual
            Caderno.objects.filter(codigo_cliente=codigo_cliente, colaborador_id=colaborador_id).delete()

            return JsonResponse({'status': 'success', 'message': 'Pagamento removido com sucesso!'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': f'Erro ao remover pagamento: {e}'}, status=500)
    else:
        return JsonResponse({'status': 'error', 'message': 'Método inválido'}, status=400)

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import PagamentoTransferido, CustomUser
from datetime import datetime
import json
from collections import defaultdict

@login_required
def resultados_adm_view(request):
    month = request.GET.get('month')
    colaborador_id = request.GET.get('colaborador')
    colaboradores = CustomUser.objects.filter(user_type='colaborador')

    if month:
        selected_month = datetime.strptime(month, "%Y-%m").date()
    else:
        selected_month = datetime.now().date()

    pagamentos = PagamentoTransferido.objects.filter(
        criado_em__year=selected_month.year,
        criado_em__month=selected_month.month
    ).order_by('-criado_em')

    if colaborador_id:
        pagamentos = pagamentos.filter(colaborador_id=colaborador_id)

    pagamentos_agrupados = defaultdict(lambda: {'titular': '', 'data_pgto': None, 'parcelas': [], 'criado_em': None})
    parcelas_atrasadas = 0
    parcelas_regulares = 0
    parcelas_adiantadas = 0
    parcelas_por_dia = defaultdict(int)

    for pagamento in pagamentos:
        codigo_cliente = pagamento.codigo_cliente
        pagamentos_agrupados[codigo_cliente]['titular'] = pagamento.nome_titular
        pagamentos_agrupados[codigo_cliente]['data_pgto'] = pagamento.data_pgto
        pagamentos_agrupados[codigo_cliente]['parcelas'].append(pagamento.parcela)
        pagamentos_agrupados[codigo_cliente]['criado_em'] = pagamento.criado_em

        dia = pagamento.criado_em.day
        parcelas_por_dia[dia] += 1

        data_pgto = pagamento.data_pgto
        if data_pgto < selected_month.replace(day=1):
            parcelas_atrasadas += 1
        elif data_pgto.year == selected_month.year and data_pgto.month == selected_month.month:
            parcelas_regulares += 1
        else:
            parcelas_adiantadas += 1

    for codigo_cliente in pagamentos_agrupados:
        pagamentos_agrupados[codigo_cliente]['parcelas'] = json.dumps(pagamentos_agrupados[codigo_cliente]['parcelas'])

    total_parcelas = pagamentos.count()
    total_clientes = len(pagamentos_agrupados)

    context = {
        'pagamentos_agrupados': dict(pagamentos_agrupados),
        'selected_month': selected_month,
        'total_parcelas': total_parcelas,
        'total_clientes': total_clientes,
        'parcelas_atrasadas': parcelas_atrasadas,
        'parcelas_regulares': parcelas_regulares,
        'parcelas_adiantadas': parcelas_adiantadas,
        'parcelas_por_dia': dict(parcelas_por_dia),
        'colaboradores': colaboradores,
        'pagamentos': pagamentos,
    }

    return render(request, 'colaboradores/resultados_adm.html', context)


from collections import defaultdict
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import PagamentoTransferido
from datetime import datetime, timedelta
import json
import mysql.connector

def get_month_range(selected_month):
    start_date = selected_month.replace(day=1)
    if selected_month.month == 12:
        end_date = selected_month.replace(year=selected_month.year + 1, month=1, day=1) - timedelta(days=1)
    else:
        end_date = selected_month.replace(month=selected_month.month + 1, day=1) - timedelta(days=1)
    return start_date, end_date

@login_required
def resultados(request):
    month = request.GET.get('month')
    if month:
        selected_month = datetime.strptime(month, "%Y-%m").date()
    else:
        selected_month = datetime.now().date()

    start_date, end_date = get_month_range(selected_month)

    # Obter dados de PagamentoTransferido
    pagamentos = PagamentoTransferido.objects.filter(
        colaborador=request.user,
        criado_em__range=(start_date, end_date)
    ).order_by('-criado_em')  # Ordenar por criado_em de forma decrescente

    pagamentos_agrupados = defaultdict(lambda: {'titular': '', 'data_pgto': None, 'parcelas': [], 'criado_em': None})
    parcelas_atrasadas = 0
    parcelas_regulares = 0
    parcelas_adiantadas = 0
    parcelas_por_dia = defaultdict(int)
    
    for pagamento in pagamentos:
        codigo_cliente = pagamento.codigo_cliente
        pagamentos_agrupados[codigo_cliente]['titular'] = pagamento.nome_titular
        pagamentos_agrupados[codigo_cliente]['data_pgto'] = pagamento.data_pgto
        pagamentos_agrupados[codigo_cliente]['parcelas'].append(pagamento.parcela)
        pagamentos_agrupados[codigo_cliente]['criado_em'] = pagamento.criado_em

        # Contar parcelas por dia
        dia = pagamento.criado_em.day
        parcelas_por_dia[dia] += 1

        # Convertendo a parcela para datetime.date
        parcela_mes_ano = datetime.strptime(pagamento.parcela, '%m/%y').date()
        if parcela_mes_ano < start_date:
            parcelas_atrasadas += 1
        elif parcela_mes_ano.year == selected_month.year and parcela_mes_ano.month == selected_month.month:
            parcelas_regulares += 1
        else:
            parcelas_adiantadas += 1

    for codigo_cliente in pagamentos_agrupados:
        pagamentos_agrupados[codigo_cliente]['parcelas'] = json.dumps(pagamentos_agrupados[codigo_cliente]['parcelas'])

    total_parcelas = pagamentos.count()
    total_clientes = len(pagamentos_agrupados)

    # Obter dados de picotes_moc e pagamentos_transferidos
    cnx = mysql.connector.connect(
        host="35.199.121.189",
        user="root",
        password="912341",
        database="avelarcobranca"
    )

    query_picotes_moc = f"""
        SELECT COUNT(*) FROM picotes_moc
        WHERE `Data Pgto.` BETWEEN '{start_date}' AND '{end_date}'
        AND `Data Venc.` <= '{end_date}'
    """
    query_pagamentos_transferidos = f"""
        SELECT COUNT(*) FROM colaboradores_pagamentotransferido
        WHERE `criado_em` BETWEEN '{start_date}' AND '{end_date}'
        AND `colaborador_id` = %s
    """

    cursor = cnx.cursor()
    
    # Print da query com as datas substituídas
    print(f"Executing query: {query_picotes_moc}")

    cursor.execute(query_picotes_moc)
    picotes_moc_count = cursor.fetchone()[0]

    meta_picotes = 8959
    percentual_meta_picotes = round((picotes_moc_count / meta_picotes) * 100, 2)

    colaborador_id = request.user.id

    print(f"Executing query: {query_pagamentos_transferidos % colaborador_id}")
    cursor.execute(query_pagamentos_transferidos, (colaborador_id,))
    pagamentos_transferidos_count = cursor.fetchone()[0]

    meta_pagamentos = 624
    percentual_meta_pagamentos = round((pagamentos_transferidos_count / meta_pagamentos) * 100, 2)

    cursor.close()
    cnx.close()

    context = {
        'pagamentos_agrupados': dict(pagamentos_agrupados),
        'selected_month': selected_month,
        'total_parcelas': total_parcelas,
        'total_clientes': total_clientes,
        'parcelas_atrasadas': parcelas_atrasadas,
        'parcelas_regulares': parcelas_regulares,
        'parcelas_adiantadas': parcelas_adiantadas,
        'parcelas_por_dia': dict(parcelas_por_dia),  # Adicionar parcelas por dia ao contexto
        'picotes_moc_count': picotes_moc_count,
        'meta_picotes': meta_picotes,
        'percentual_meta_picotes': percentual_meta_picotes,
        'pagamentos_transferidos_count': pagamentos_transferidos_count,
        'meta_pagamentos': meta_pagamentos,
        'percentual_meta_pagamentos': percentual_meta_pagamentos
    }

    return render(request, 'colaboradores/resultados.html', context)


@login_required
def index_adm_view(request):
    user = request.user
    eventos_hoje = Evento.objects.filter(colaborador=user, data=date.today())
    listas_hoje = ListaDistribuida.objects.filter(colaborador=user, data_distribuicao__date=date.today()) \
                                           .values('nome_lista', 'id_lista').distinct()

    context = {
        'user': user,
        'eventos_hoje': eventos_hoje,
        'listas_hoje': listas_hoje,
    }
    return render(request, 'colaboradores/index_adm.html', context)


from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from .forms import CustomUserEditForm, CustomUserCreationForm
from .models import CustomUser

@login_required
@user_passes_test(lambda u: u.is_superuser)
def edit_user_view(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)
    
    if request.method == 'POST':
        form = CustomUserEditForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect('user_list')  # Redirecionar para a página de lista de usuários
    else:
        form = CustomUserEditForm(instance=user)
    
    context = {
        'form': form,
        'user': user
    }
    return render(request, 'colaboradores/edit_user.html', context)

@login_required
@user_passes_test(lambda u: u.is_superuser)
def user_list_view(request):
    users = CustomUser.objects.all()
    return render(request, 'colaboradores/user_list.html', {'users': users})

@login_required
@user_passes_test(lambda u: u.is_superuser)
def delete_user_view(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)
    user.delete()
    return redirect('user_list')


from django.http import JsonResponse

@login_required
@user_passes_test(lambda u: u.is_superuser)
def get_user_data(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)
    data = {
        'username': user.username,
        'email': user.email,
        'user_type': user.user_type,
        'colaborador_type': user.colaborador_type,
    }
    return JsonResponse(data)

from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import CustomUser
from .forms import ChangePasswordForm
from django.utils import timezone

@login_required
@user_passes_test(lambda u: u.is_superuser)
def change_password_view(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)

    if request.method == 'POST':
        form = ChangePasswordForm(request.POST, instance=user)
        if form.is_valid():
            new_password = form.cleaned_data.get('new_password')
            user.set_password(new_password)
            user.save()
            messages.success(request, 'Senha alterada com sucesso!')
            return redirect('user_list')
    else:
        form = ChangePasswordForm(instance=user)

    return render(request, 'colaboradores/change_password.html', {'form': form, 'user': user})

from datetime import timedelta
from django.utils import timezone
from django.db.models import Count, Subquery, OuterRef, IntegerField, F
from .models import Interacao, ListaDistribuida, PagamentoTransferido

def get_last_business_day():
    today = timezone.now().date()
    last_business_day = today
    while last_business_day.weekday() > 4:  # 0 = Monday, 1 = Tuesday, ..., 4 = Friday, 5 = Saturday, 6 = Sunday
        last_business_day -= timedelta(days=1)
    return last_business_day

def get_conflicting_payments():
    conflicting_payments_data = PagamentoTransferido.objects.raw("""
        SELECT pt.id, pt.codigo_cliente, pt.parcela, cu.username
        FROM avelarcobranca.colaboradores_pagamentotransferido pt
        JOIN avelarcobranca.colaboradores_customuser cu ON pt.colaborador_id = cu.id
        WHERE (pt.codigo_cliente, pt.parcela) IN (
            SELECT codigo_cliente, parcela
            FROM avelarcobranca.colaboradores_pagamentotransferido
            GROUP BY codigo_cliente, parcela
            HAVING COUNT(DISTINCT colaborador_id) > 1
        )
    """)
    
    conflicting_payments = {}
    for row in conflicting_payments_data:
        key = (row.codigo_cliente, row.parcela)
        if key not in conflicting_payments:
            conflicting_payments[key] = []
        conflicting_payments[key].append(row.username)
    
    return conflicting_payments

from django.http import JsonResponse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from datetime import timedelta
from .models import Evento, ListaDistribuida, PagamentoTransferido, Interacao
from django.db.models import Count, Subquery, OuterRef, IntegerField, F

@login_required
def index_adm_view(request):
    hoje = timezone.now().date()
    sete_dias_atras = hoje - timedelta(days=7)
    
    # Obter listas distribuídas únicas nos últimos 7 dias
    listas_distribuidas_raw = ListaDistribuida.objects.filter(
        data_distribuicao__date__gte=sete_dias_atras
    ).order_by('-data_distribuicao').values('id_lista', 'nome_lista', 'data_distribuicao')
    
    # Criar um dicionário para garantir unicidade das listas
    listas_distribuidas = {}
    for lista in listas_distribuidas_raw:
        listas_distribuidas[lista['id_lista']] = lista
    
    # Garantir que a lista de hoje esteja incluída
    lista_hoje_raw = ListaDistribuida.objects.filter(data_distribuicao__date=hoje).values('id_lista', 'nome_lista', 'data_distribuicao')
    for lista in lista_hoje_raw:
        listas_distribuidas[lista['id_lista']] = lista

    listas_distribuidas = list(listas_distribuidas.values())

    # Definir a lista mais recente como padrão
    lista_mais_recente = max(listas_distribuidas, key=lambda x: x['data_distribuicao'], default=None)
    lista_selecionada = request.GET.get('lista_selecionada', lista_mais_recente['id_lista'] if lista_mais_recente else None)
    
    if lista_selecionada:
        listas_distribuidas_selecionada = [lista for lista in listas_distribuidas if lista['id_lista'] == lista_selecionada]

    andamento_colaboradores = ListaDistribuida.objects.filter(id_lista=lista_selecionada).values('colaborador__username', 'nome_lista', 'id_lista', 'colaborador_id').annotate(
        total_clientes=Count('id'),
        total_interacoes=Subquery(
            Interacao.objects.filter(
                lista_distribuida_id=OuterRef('id_lista'),
                colaborador_id=OuterRef('colaborador_id')
            ).values('colaborador_id').annotate(
                count_interactions=Count('id')
            ).values('count_interactions')[:1],
            output_field=IntegerField()
        )
    ).annotate(
        percentual_conclusao=F('total_interacoes') * 100.0 / F('total_clientes')
    ).order_by('colaborador__username').values(
        'colaborador__username', 'nome_lista', 'total_clientes', 'total_interacoes', 'percentual_conclusao'
    )

    atividades_recentes = PagamentoTransferido.objects.filter(criado_em__date=hoje).order_by('-criado_em')

    conflicting_payments = get_conflicting_payments()

    for colaborador in andamento_colaboradores:
        if colaborador['total_interacoes'] is None:
            colaborador['total_interacoes'] = 0
        if colaborador['percentual_conclusao'] is None:
            colaborador['percentual_conclusao'] = 0

    context = {
        'user': request.user,
        'andamento_colaboradores': andamento_colaboradores,
        'atividades_recentes': atividades_recentes,
        'conflicting_payments': conflicting_payments,
        'listas_distribuidas': listas_distribuidas,
        'lista_selecionada': lista_selecionada,
    }

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'andamento_colaboradores': list(andamento_colaboradores),
            'atividades_recentes': list(atividades_recentes.values(
                'codigo_cliente', 'parcela', 'colaborador__username', 'criado_em'
            )),
        })

    return render(request, 'colaboradores/index_adm.html', context)

from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import Evento

@login_required
@user_passes_test(lambda u: u.is_superuser)
def agenda_adm_view(request):
    eventos = Evento.objects.all().order_by('data')
    eventos_data = [
        {
            'codigo': evento.codigo,
            'data': evento.data,
            'observacao': evento.observacao,
            'criador': evento.colaborador.username
        }
        for evento in eventos
    ]

    context = {
        'eventos': eventos_data
    }
    return render(request, 'colaboradores/agenda_adm.html', context)


from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import PagamentoTransferido, PagamentoRemovido
from datetime import datetime

@login_required
def remover_pagamento_adm_view(request):
    if request.method == 'POST':
        try:
            pagamento_id = request.POST.get('pagamento_id')
            motivo = request.POST.get('motivo')

            if not pagamento_id:
                return JsonResponse({'status': 'error', 'message': 'Nenhum ID de pagamento fornecido.'}, status=400)

            pagamento = PagamentoTransferido.objects.get(id=pagamento_id)

            # Salvar a remoção na nova tabela
            PagamentoRemovido.objects.create(
                codigo_cliente=pagamento.codigo_cliente,
                nome_cliente=pagamento.nome_titular,
                motivo=motivo,
                parcela=pagamento.parcela,  # Salvando a parcela
                colaborador=request.user,
                colaborador_original=pagamento.colaborador,  # Salvar o colaborador original
                visible=True
            )

            pagamento.delete()

            return JsonResponse({'status': 'success', 'message': 'Pagamento removido com sucesso!'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': f'Erro ao remover pagamento: {e}'}, status=500)
    else:
        return JsonResponse({'status': 'error', 'message': 'Método inválido'}, status=400)


def dashboard_view(request):
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        colaborador = request.GET.get('colaborador')
        lista = request.GET.get('lista')

        legendas_data = Interacao.objects.all()
        motivos_data = Interacao.objects.all()

        if colaborador != 'all':
            legendas_data = legendas_data.filter(colaborador_id=colaborador)
            motivos_data = motivos_data.filter(colaborador_id=colaborador)

        if lista != 'all':
            legendas_data = legendas_data.filter(lista_distribuida_id=lista)
            motivos_data = motivos_data.filter(lista_distribuida_id=lista)

        legendas_counts = legendas_data.values('legenda').annotate(count=Count('id'))
        motivos_counts = motivos_data.values('motivo').annotate(count=Count('id'))

        legendas_data = [
            {
                'label': item['legenda'],
                'count': item['count'],
                'percentage': item['count'] / sum([i['count'] for i in legendas_counts]) * 100
            } for item in legendas_counts
        ]

        motivos_data = [
            {
                'label': item['motivo'],
                'count': item['count'],
                'percentage': item['count'] / sum([i['count'] for i in motivos_counts]) * 100
            } for item in motivos_counts
        ]

        return JsonResponse({
            'legendas_data': legendas_data,
            'motivos_data': motivos_data,
        })

    colaboradores = CustomUser.objects.filter(is_superuser=False)
    listas = ListaDistribuida.objects.values('id_lista', 'nome_lista').distinct()
    meses = PagamentoTransferido.objects.dates('criado_em', 'month')

    # Adicionando prints para depuração
    print(f"Colaboradores: {colaboradores}")
    print(f"Listas: {listas}")
    print(f"Meses: {meses}")

    return render(request, 'colaboradores/dashboard.html', {
        'colaboradores': colaboradores,
        'listas': listas,
        'meses': [mes.strftime('%Y-%m') for mes in meses]
    })

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from .models import PagamentoTransferido
from django.db.models import Count
from datetime import datetime

@csrf_exempt
@login_required
def dashboard_pagamentos_view(request):
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        colaborador = request.GET.get('colaborador')
        meses = request.GET.get('meses').split(',')

        pagamentos_data = PagamentoTransferido.objects.all()

        if colaborador != 'all':
            pagamentos_data = pagamentos_data.filter(colaborador_id=colaborador)

        if 'all' not in meses:
            # Convertendo os meses de string para objetos datetime
            meses = [datetime.strptime(m, '%Y-%m') for m in meses]
            # Filtrando os pagamentos apenas para os meses especificados
            pagamentos_data = pagamentos_data.filter(criado_em__year__in=[m.year for m in meses], criado_em__month__in=[m.month for m in meses])

        # Agrupando os pagamentos por mês e contando o número total de registros em cada mês
        pagamentos_counts = pagamentos_data.values('criado_em__year', 'criado_em__month').annotate(count=Count('id'))

        # Organizando os dados para retornar ao frontend, ordenando por ano e mês
        pagamentos_counts = sorted(pagamentos_counts, key=lambda x: (x['criado_em__year'], x['criado_em__month']))

        pagamentos_data = {
            'labels': [f"{item['criado_em__year']}-{item['criado_em__month']}" for item in pagamentos_counts],
            'counts': [item['count'] for item in pagamentos_counts]
        }

        return JsonResponse({
            'pagamentos_data': pagamentos_data,
        })

    return JsonResponse({
        'status': 'error',
        'message': 'Invalid request'
    })

from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from datetime import datetime
from .models import PagamentoTransferido

@login_required
def api_get_data(request):
    month = request.GET.get('month')
    colaborador_id = request.GET.get('colaborador')
    
    if month:
        selected_month = datetime.strptime(month, "%Y-%m").date()
    else:
        selected_month = datetime.now().date()

    pagamentos = PagamentoTransferido.objects.filter(
        criado_em__year=selected_month.year,
        criado_em__month=selected_month.month
    )

    if colaborador_id:
        pagamentos = pagamentos.filter(colaborador_id=colaborador_id)

    parcelas_atrasadas = 0
    parcelas_regulares = 0
    parcelas_adiantadas = 0

    for pagamento in pagamentos:
        parcela_date = datetime.strptime(pagamento.parcela, "%m/%y").date()
        if parcela_date < selected_month.replace(day=1):
            parcelas_atrasadas += 1
        elif parcela_date.year == selected_month.year and parcela_date.month == selected_month.month:
            parcelas_regulares += 1
        else:
            parcelas_adiantadas += 1

    total_parcelas = pagamentos.count()
    total_clientes = pagamentos.values('codigo_cliente').distinct().count()
    
    parcelas_por_dia = pagamentos.values('criado_em__day').annotate(count=Count('id')).order_by('criado_em__day')

    return JsonResponse({
        'parcelas_atrasadas': parcelas_atrasadas,
        'parcelas_regulares': parcelas_regulares,
        'parcelas_adiantadas': parcelas_adiantadas,
        'total_parcelas': total_parcelas,
        'total_clientes': total_clientes,
        'parcelas_por_dia': list(parcelas_por_dia),
    })

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from .models import PagamentoRemovido

@csrf_exempt
@login_required
def marcar_como_lido(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            picote_id = data.get('id')
            picote = PagamentoRemovido.objects.get(id=picote_id)

            # Marcar como lido (visible = False)
            picote.visible = False
            picote.save()

            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'})


from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from .models import MaterialConvalescente
from .forms import MaterialConvalescenteForm
from django.db.models import Sum

def get_icone_for_material(material_name):
    icones = {
        "Andador": "fa-solid fa-hospital-user",
        "Cadeira de Banho": "fa-solid fa-wheelchair",
        "Cadeira de Banho Grande": "fa-solid fa-wheelchair",
        "Muletas Alumínio - Par": "fas fa-crutch",
        "Cadeira de Rodas": "fas fa-wheelchair",
        "Cadeira de Rodas Grande": "fas fa-wheelchair",
        "Bengala": "fa-solid fa-person-walking-with-cane",
        "Muleta Canadense - Par": "fas fa-crutch",
        "Bota Ortopédica": "fas fa-shoe-prints"
    }
    return icones.get(material_name, "fas fa-box")

from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from .models import MaterialConvalescente
from .forms import MaterialConvalescenteForm
from django.db.models import Sum
import logging

logger = logging.getLogger(__name__)

def material_convalescente_view(request):
    try:
        if request.method == 'POST':
            form = MaterialConvalescenteForm(request.POST)
            if form.is_valid():
                material_convalescente = form.save(commit=False)
                # Defina o colaborador_id aqui
                material_convalescente.colaborador_id = request.user.id  # Supondo que o colaborador seja o usuário logado
                material_convalescente.save()
                return JsonResponse({'success': True})
            else:
                return JsonResponse({'success': False, 'errors': form.errors}, status=400)
        else:
            form = MaterialConvalescenteForm()
            mes = request.GET.get('mes')
            ano = request.GET.get('ano')

            if mes and ano:
                resultados = MaterialConvalescente.objects.filter(data_pagamento__month=mes, data_pagamento__year=ano, colaborador_id=request.user.id)
            else:
                resultados = MaterialConvalescente.objects.filter(colaborador_id=request.user.id)

            materiais = [
                {'material': 'Andador', 'icone': get_icone_for_material('Andador'), 'total_parcelas': resultados.filter(material='Andador').aggregate(Sum('parcelas'))['parcelas__sum'] or 0},
                {'material': 'Cadeira de Banho', 'icone': get_icone_for_material('Cadeira de Banho'), 'total_parcelas': resultados.filter(material='Cadeira de Banho').aggregate(Sum('parcelas'))['parcelas__sum'] or 0},
                {'material': 'Muletas Alumínio - Par', 'icone': get_icone_for_material('Muletas Alumínio - Par'), 'total_parcelas': resultados.filter(material='Muletas Alumínio - Par').aggregate(Sum('parcelas'))['parcelas__sum'] or 0},
                {'material': 'Cadeira de Rodas', 'icone': get_icone_for_material('Cadeira de Rodas'), 'total_parcelas': resultados.filter(material='Cadeira de Rodas').aggregate(Sum('parcelas'))['parcelas__sum'] or 0},
                {'material': 'Cadeira de Rodas Grande', 'icone': get_icone_for_material('Cadeira de Rodas Grande'), 'total_parcelas': resultados.filter(material='Cadeira de Rodas Grande').aggregate(Sum('parcelas'))['parcelas__sum'] or 0},
                {'material': 'Bengala', 'icone': get_icone_for_material('Bengala'), 'total_parcelas': resultados.filter(material='Bengala').aggregate(Sum('parcelas'))['parcelas__sum'] or 0},
                {'material': 'Muleta Canadense - Par', 'icone': get_icone_for_material('Muleta Canadense - Par'), 'total_parcelas': resultados.filter(material='Muleta Canadense - Par').aggregate(Sum('parcelas'))['parcelas__sum'] or 0},
                {'material': 'Bota Ortopédica', 'icone': get_icone_for_material('Bota Ortopédica'), 'total_parcelas': resultados.filter(material='Bota Ortopédica').aggregate(Sum('parcelas'))['parcelas__sum'] or 0},
                {'material': 'Cadeira de Banho Grande', 'icone': get_icone_for_material('Cadeira de Banho Grande'), 'total_parcelas': resultados.filter(material='Cadeira de Banho Grande').aggregate(Sum('parcelas'))['parcelas__sum'] or 0},
            ]

            # Filtrar materiais com parcelas > 0
            materiais = [material for material in materiais if material['total_parcelas'] > 0]

            context = {
                'form': form,
                'resultados': resultados,
                'materiais': materiais,
                'mes': mes,
                'ano': ano,
            }
            return render(request, 'colaboradores/material_convalescente.html', context)
    except Exception as e:
        logger.error(f"Error processing request: {e}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from .models import MaterialConvalescente

def remover_material_convalescente(request, id):
    if request.method == 'POST':
        material = get_object_or_404(MaterialConvalescente, id=id)
        material.delete()
        return JsonResponse({'success': True})
    return JsonResponse({'success': False, 'error': 'Método não permitido'})

    
    
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import ListaDistribuida, CustomUser
import logging

logger = logging.getLogger(__name__)

@login_required
def search_code_view(request, id_lista, codigo_cliente):
    try:
        # Limpar os hífens do id_lista
        id_lista_clean = id_lista.replace('-', '')
        logger.debug(f"Pesquisando código cliente: {codigo_cliente} na lista: {id_lista_clean}")

        # Limpar o código do cliente
        codigo_cliente_clean = codigo_cliente.strip()
        logger.debug(f"codigo_cliente_clean: {codigo_cliente_clean}")

        # Buscar a lista distribuída correspondente
        lista_distribuida = ListaDistribuida.objects.filter(codigo=codigo_cliente_clean, id_lista=id_lista_clean).first()

        if lista_distribuida:
            # Obter o username do colaborador
            colaborador = lista_distribuida.colaborador.username
            logger.debug(f"Colaborador encontrado: {colaborador}")
            return JsonResponse({'status': 'success', 'colaborador': colaborador})
        else:
            logger.debug(f"Código cliente {codigo_cliente} não encontrado na lista {id_lista_clean}")
            return JsonResponse({'status': 'error', 'message': 'Código não encontrado'})
    except Exception as e:
        logger.error(f"Erro ao pesquisar o código: {str(e)}")
        return JsonResponse({'status': 'error', 'message': 'Erro ao pesquisar o código'})



from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
import mysql.connector
from datetime import datetime, timedelta

def get_month_range_loop():
    now = datetime.now()
    start_date = now.replace(day=1)
    if now.month == 12:
        end_date = now.replace(year=now.year + 1, month=1, day=1) - timedelta(days=1)
    else:
        end_date = now.replace(month=now.month + 1, day=1) - timedelta(days=1)
    return start_date.date(), end_date.date()

@login_required
def loop_view(request):
    # Conexão com o banco de dados MySQL
    cnx = mysql.connector.connect(
        host="35.199.121.189",
        user="root",
        password="912341",
        database="avelarcobranca"
    )

    start_date, end_date = get_month_range_loop()

    query_picotes_moc = f"""
        SELECT COUNT(*) FROM picotes_moc
        WHERE `Data Pgto.` BETWEEN '{start_date}' AND '{end_date}'
        AND `Data Venc.` <= '{end_date}'
    """
    query_pagamentos_transferidos = f"""
        SELECT COUNT(*) FROM colaboradores_pagamentotransferido
        WHERE `criado_em` BETWEEN '{start_date}' AND '{end_date}'
        AND `colaborador_id` = %s
    """

    cursor = cnx.cursor()
    
    # Print da query com as datas substituídas
    print(f"Executing query: {query_picotes_moc}")

    cursor.execute(query_picotes_moc)
    picotes_moc_count = cursor.fetchone()[0]

    meta_picotes = 8959
    percentual_meta_picotes = round((picotes_moc_count / meta_picotes) * 100, 2)

    colaborador_id = request.user.id

    print(f"Executing query: {query_pagamentos_transferidos % colaborador_id}")
    cursor.execute(query_pagamentos_transferidos, (colaborador_id,))
    pagamentos_transferidos_count = cursor.fetchone()[0]

    meta_pagamentos = 624
    percentual_meta_pagamentos = round((pagamentos_transferidos_count / meta_pagamentos) * 100, 2)

    cursor.close()
    cnx.close()

    context = {
        'picotes_moc_count': picotes_moc_count,
        'meta_picotes': meta_picotes,
        'percentual_meta_picotes': percentual_meta_picotes,
        'pagamentos_transferidos_count': pagamentos_transferidos_count,
        'meta_pagamentos': meta_pagamentos,
        'percentual_meta_pagamentos': percentual_meta_pagamentos,
    }

    return render(request, 'colaboradores/loop.html', context)

from datetime import datetime, timedelta
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
import mysql.connector

@login_required
def ticker_data(request):
    # Conexão com o banco de dados MySQL
    cnx = mysql.connector.connect(
        host="35.199.121.189",
        user="root",
        password="912341",
        database="avelarcobranca"
    )

    now = datetime.now()
    start_date = now.replace(day=1).strftime('%Y-%m-%d')
    if now.month == 12:
        end_date = now.replace(year=now.year + 1, month=1, day=1) - timedelta(days=1)
    else:
        end_date = now.replace(month=now.month + 1, day=1) - timedelta(days=1)
    end_date = end_date.strftime('%Y-%m-%d')

    query_picotes_moc = f"""
        SELECT COUNT(*) FROM picotes_moc
        WHERE `Data Pgto.` BETWEEN '{start_date}' AND '{end_date}'
        AND `Data Venc.` <= '{end_date}'
    """
    query_pagamentos_transferidos = f"""
        SELECT COUNT(*) FROM colaboradores_pagamentotransferido
        WHERE `criado_em` BETWEEN '{start_date}' AND '{end_date}'
        AND `colaborador_id` = %s
    """

    cursor = cnx.cursor()
    
    # Print da query com as datas substituídas
    print(f"Executing query: {query_picotes_moc}")

    cursor.execute(query_picotes_moc)
    picotes_moc_count = cursor.fetchone()[0]

    meta_picotes = 8959
    percentual_meta_picotes = round((picotes_moc_count / meta_picotes) * 100, 2)

    colaborador_id = request.user.id

    print(f"Executing query: {query_pagamentos_transferidos % colaborador_id}")
    cursor.execute(query_pagamentos_transferidos, (colaborador_id,))
    pagamentos_transferidos_count = cursor.fetchone()[0]

    meta_pagamentos = 624
    percentual_meta_pagamentos = round((pagamentos_transferidos_count / meta_pagamentos) * 100, 2)

    cursor.close()
    cnx.close()

    data = {
        'picotes_moc_count': picotes_moc_count,
        'meta_picotes': meta_picotes,
        'percentual_meta_picotes': percentual_meta_picotes,
        'pagamentos_transferidos_count': pagamentos_transferidos_count,
        'meta_pagamentos': meta_pagamentos,
        'percentual_meta_pagamentos': percentual_meta_pagamentos,
    }

    return JsonResponse(data)
