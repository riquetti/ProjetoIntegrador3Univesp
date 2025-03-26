import requests
from django.shortcuts import render
from livro.models import Livros  # Importa o modelo Livros

# URL base da API do Deezer para gêneros
DEEZER_GENRE_URL = "https://api.deezer.com/genre"

# URL para buscar faixas mais populares (mais tocadas) no Deezer
DEEZER_POPULAR_TRACKS_URL = "https://api.deezer.com/chart/{}/tracks"  # Alteração no endpoint para pegar faixas por gênero

def artistas_por_genero(request):
    # Realiza a requisição para a API Deezer para pegar todos os gêneros
    response = requests.get(DEEZER_GENRE_URL)
    generos_dict = {}

    if response.status_code == 200:
        generos = response.json()["data"]
        generos_dict = {str(g['id']): g['name'].lower() for g in generos}  # Mapeia ID para nome minúsculo
    else:
        generos = []

    # Define faixas e livros como vazios inicialmente
    faixas = []  # Para armazenar as faixas mais tocadas
    livros = Livros.objects.all()  # Carrega todos os livros por padrão

    # Verifica se o formulário foi enviado
    if request.method == 'POST':
        genre_id = request.POST['genero']  # ID do gênero selecionado
        genre_name = generos_dict.get(genre_id, "").lower()  # Obtém o nome do gênero correspondente

        # Busca faixas mais populares do Deezer para o gênero selecionado
        response = requests.get(DEEZER_POPULAR_TRACKS_URL.format(genre_id))  # Faz a requisição para o gênero específico

        # Depuração: Verifique a resposta da API
        print(f"URL da requisição: {DEEZER_POPULAR_TRACKS_URL.format(genre_id)}")  # URL sendo chamada
        print(f"Status da resposta: {response.status_code}")  # Status HTTP da resposta
        if response.status_code == 200:
            try:
                faixas = response.json().get("data", [])
                if not faixas:
                    print("Nenhuma faixa popular encontrada para esse gênero.")
                print("Faixas recebidas:", faixas)  # Adicione a depuração aqui
            except ValueError:  # Em caso de erro ao tentar decodificar JSON
                faixas = []
                print("Erro ao decodificar JSON.")
        else:
            print(f"Erro na requisição: {response.status_code}")
            print(response.json())  # Adicione a depuração para ver o erro completo da API

        # Filtra livros pelo nome do gênero no banco
        if genre_name:
            livros = Livros.objects.filter(genero__iexact=genre_name)  # Busca pelo nome (case insensitive)

    # Passando as informações para o template
    context = {
        'generos': generos,
        'faixas': faixas,  # Faixas para a parte esquerda
        'livros': livros   # Livros para a parte direita
    }
    return render(request, 'deezer_integration/genre_deezer.html', context)
