import random
import pygame
import supabase
import os
from supabase import create_client, Client

# --- CONSTANTES GLOBAIS ---
METEOR_TYPE = "METEORO"
STAR_TYPE = "ESTRELA"
ENEMY_TYPE = "INIMIGO"
BULLET_TYPE = "PROJETIL_INIMIGO"
BOSS_TYPE = "BOSS"
PLAYER_BULLET_TYPE = "TIRO_PLAYER"

# Cores
AZUL_ESCURO = (10, 10, 40)
BRANCO = (255, 255, 255)
VERMELHO = (200, 50, 50)
AMARELO = (255, 255, 0)
VERDE = (0, 200, 0)
ROXO = (150, 0, 150)
AZUL_CLARO = (0, 150, 255)

# Configurações do Supabase (MANTIDAS)
SUPABASE_URL = "https://bswwwlirnufexdhnsdkt.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImJzd3d3bGlybnVmZXhkaG5zZGt0Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTczNDE3NjEsImV4cCI6MjA3MjkxNzc2MX0.gHO2CHcHMgzJkHHnN8Ai0PwJrP-MbY5qcoRgGLcehv4"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

pygame.init()

largura, altura = 400, 600
tela = pygame.display.set_mode((largura, altura))
pygame.display.set_caption("Space Collector - Dificuldade Escalonada!")
clock = pygame.time.Clock()

# --- CARREGAMENTO DE IMAGENS ---
SKIN_TAMANHO = (30, 40)  # Tamanho padrão da nave do jogador

try:
    IMAGEM_FUNDO = pygame.transform.scale(pygame.image.load(os.path.join('fundo.png')).convert(), (largura, altura))
    IMAGEM_ESTRELA = pygame.transform.scale(pygame.image.load(os.path.join('estrela.png')).convert_alpha(), (40, 40))
    IMAGEM_METEORO = pygame.transform.scale(pygame.image.load(os.path.join('asteroide.png')).convert_alpha(), (40, 40))
    IMAGEM_NAVE_INIMIGA = pygame.transform.scale(pygame.image.load(os.path.join('inimigo.png')).convert_alpha(),
                                                 (40, 40))
    IMAGEM_BOSS = pygame.transform.scale(pygame.image.load(os.path.join('boss.png')).convert_alpha(), (120, 80))
    IMAGEM_PROJETIL = pygame.transform.scale(pygame.image.load(os.path.join('projetil.png')).convert_alpha(), (10, 20))

    # --- SKINS DO JOGADOR ---
    SKIN1 = pygame.transform.scale(pygame.image.load(os.path.join('player1.png')).convert_alpha(), SKIN_TAMANHO)
    SKIN2 = pygame.transform.scale(pygame.image.load(os.path.join('player2.png')).convert_alpha(), SKIN_TAMANHO)
    SKIN3 = pygame.transform.scale(pygame.image.load(os.path.join('player3.png')).convert_alpha(), SKIN_TAMANHO)

    PLAYER_SKINS = [
        {"nome": "Nave Principal", "img": SKIN1},
        {"nome": "Nave Ágil", "img": SKIN2},
        {"nome": "Nave Tanque", "img": SKIN3}
    ]

except pygame.error as e:
    print(f"ERRO AO CARREGAR IMAGEM: {e}. Certifique-se de que os arquivos de imagem estão na pasta correta.")
    # Define superfícies padrão caso as imagens falhem
    IMAGEM_FUNDO = pygame.Surface((largura, altura));
    IMAGEM_FUNDO.fill(AZUL_ESCURO)
    IMAGEM_ESTRELA = pygame.Surface((40, 40));
    IMAGEM_ESTRELA.fill(AMARELO)
    IMAGEM_METEORO = pygame.Surface((40, 40));
    IMAGEM_METEORO.fill(VERMELHO)
    IMAGEM_PROJETIL = pygame.Surface((10, 20));
    IMAGEM_PROJETIL.fill(BRANCO)

    # Placeholders para as skins
    SKIN_FALLBACK = pygame.Surface(SKIN_TAMANHO);
    SKIN_FALLBACK.fill(BRANCO)
    IMAGEM_NAVE_INIMIGA = pygame.Surface((40, 40));
    IMAGEM_NAVE_INIMIGA.fill(VERDE)
    IMAGEM_BOSS = pygame.Surface((120, 80));
    IMAGEM_BOSS.fill(ROXO)

    PLAYER_SKINS = [
        {"nome": "Placeholder 1", "img": SKIN_FALLBACK},
        {"nome": "Placeholder 2", "img": SKIN_FALLBACK},
        {"nome": "Placeholder 3", "img": SKIN_FALLBACK}
    ]

IMAGEM_PLAYER = PLAYER_SKINS[0]["img"]
jogador = IMAGEM_PLAYER.get_rect(x=180, y=500)

# === VARIÁVEIS DE JOGO E LEVEL UP (MANTIDAS) ===
fonte = pygame.font.Font(None, 36)
fonte_pequena = pygame.font.Font(None, 24)

tempo_inicio = pygame.time.get_ticks()
tempo_atual = 0

nivel = 1
xp_atual = 0
xp_proximo_nivel = 100
VELOCIDADE_INIMIGOS_BASE = 3
COOLDOWN_INIMIGO_BASE = 120
SPAWN_CHANCE_BASE = 30
XP_POR_ESTRELA = 25
PLAYER_DANO = 10
VELOCIDADE_DIAGONAL_METEORO = 2

boss_ativo = False
tempo_proximo_boss = 30
boss_hp_base = 50
boss_cooldown_base = 30
boss_padrao_atual = 0
VELOCIDADE_PROJETIL_BASE = 8

player_projeteis = []
player_cooldown_max = 15
player_cooldown = 0
player_velocidade_tiro = 10

velocidade = 5
obstaculos = []
projeteis_inimigos = []

objetos_assets = [
    {'img': IMAGEM_METEORO, 'type': METEOR_TYPE, 'xp': 0, 'cor': VERMELHO, 'hp': 1, 'dano_boss': False},
    {'img': IMAGEM_ESTRELA, 'type': STAR_TYPE, 'xp': XP_POR_ESTRELA, 'cor': AMARELO, 'hp': 0, 'dano_boss': False},
    {'img': IMAGEM_NAVE_INIMIGA, 'type': ENEMY_TYPE, 'xp': 0, 'cor': VERDE, 'hp': 1, 'dano_boss': True},
    {'img': IMAGEM_BOSS, 'type': BOSS_TYPE, 'xp': 100, 'cor': ROXO, 'hp': boss_hp_base, 'dano_boss': True},
]

largura_proj = IMAGEM_PROJETIL.get_width()
altura_proj = IMAGEM_PROJETIL.get_height()

nome_jogador = ""


# --- FUNÇÕES SUPABASE (MANTIDAS) ---
def salvar_pontuacao(nome, nivel, tempo):
    try:
        data = supabase.table("ranking").insert({
            "nome": nome,
            "pontuacao": nivel,
            "tempo": tempo
        }).execute()
        return True
    except Exception as e:
        print(f"Erro ao salvar pontuação: {e}")
        return False


def obter_top_pontuacoes():
    try:
        response = supabase.table("ranking") \
            .select("*") \
            .order("pontuacao", desc=True) \
            .limit(3) \
            .execute()
        return response.data
    except Exception as e:
        print(f"Erro ao obter pontuações: {e}")
        return []


# --- FUNÇÕES DE LÓGICA DE JOGO (MANTIDAS) ---

def atirar_padrao_boss(boss_obj, padrao):
    novos_projeteis = []
    cooldown_ajustado = 60
    if boss_obj is None:
        boss_x = largura // 2 - 60; boss_y = 50
    else:
        boss_x = boss_obj["rect"].x; boss_y = boss_obj["rect"].y
    cooldown_base_reduzido = max(10, boss_cooldown_base - (nivel * 3))

    if padrao == 1:
        if boss_obj is not None:
            novos_projeteis.append(criar_projetil_inimigo(boss_x + 10, boss_y))
            novos_projeteis.append(criar_projetil_inimigo(boss_x + 70, boss_y))
        cooldown_ajustado = 30
    elif padrao == 2:
        if boss_obj is not None:
            novos_projeteis.append(criar_projetil_inimigo(boss_x + 5, boss_y))
            novos_projeteis.append(criar_projetil_inimigo(boss_x + 45, boss_y))
            novos_projeteis.append(criar_projetil_inimigo(boss_x + 85, boss_y))
        cooldown_ajustado = 60
    elif padrao == 3:
        if boss_obj is not None:
            proj_boss_img = pygame.transform.scale(IMAGEM_PROJETIL, (largura_proj * 2, altura_proj * 2))
            rect_tiro = proj_boss_img.get_rect(x=boss_x + 40, y=boss_y + 40)
            novos_projeteis.append({"rect": rect_tiro, "velocidade": max(4, VELOCIDADE_PROJETIL_BASE + (nivel // 3)),
                                    "img": proj_boss_img})
        cooldown_ajustado = 90
    elif padrao == 4:
        cooldown_ajustado = 60
    else:
        cooldown_ajustado = 60

    cooldown_final = max(10, cooldown_ajustado - (nivel * 2))
    return novos_projeteis, cooldown_final


def criar_objeto():
    x = random.randint(0, largura - 40)
    chance = random.random()
    if chance < 0.6:
        asset_info = objetos_assets[1]
    elif chance < 0.8:
        asset_info = objetos_assets[0]
    else:
        asset_info = objetos_assets[2]
    rect = pygame.Rect(x, -40, asset_info['img'].get_width(), asset_info['img'].get_height())
    hp_ajustado = asset_info['hp'] + (nivel // 5) if asset_info['type'] != STAR_TYPE else 0
    objeto = {"rect": rect, "asset_info": asset_info, "hp": hp_ajustado}
    if asset_info['type'] == ENEMY_TYPE:
        cooldown_ajustado = max(30, COOLDOWN_INIMIGO_BASE - (nivel * 5))
        objeto['cooldown'] = random.randint(cooldown_ajustado - 30, cooldown_ajustado)
    if asset_info['type'] == METEOR_TYPE:
        objeto['direcao_horizontal'] = random.choice([-1, 1])
        objeto['velocidade_horizontal'] = VELOCIDADE_DIAGONAL_METEORO + (nivel // 5)
    return objeto


def criar_objeto_boss():
    asset_info = objetos_assets[3]
    rect = IMAGEM_BOSS.get_rect(x=largura // 2 - 60, y=50)
    boss_hp_atual = asset_info['hp'] + (nivel * 100)
    padrao_inicial = random.randint(1, 3)
    _, cooldown_inicial = atirar_padrao_boss(None, padrao_inicial)
    objeto = {
        "rect": rect,
        "asset_info": asset_info,
        "hp": boss_hp_atual,
        "max_hp": boss_hp_atual,
        "cooldown": cooldown_inicial,
        "padrao": padrao_inicial
    }
    return objeto


def criar_projetil_inimigo(x, y):
    rect = IMAGEM_PROJETIL.get_rect(centerx=x + (IMAGEM_NAVE_INIMIGA.get_width() // 2),
                                    top=y + IMAGEM_NAVE_INIMIGA.get_height())
    velocidade_tiro = VELOCIDADE_PROJETIL_BASE + (nivel // 5)
    return {"rect": rect, "velocidade": velocidade_tiro, "img": IMAGEM_PROJETIL}


def criar_player_projetil():
    rect = IMAGEM_PROJETIL.get_rect(centerx=jogador.centerx, bottom=jogador.top)
    img_invertida = pygame.transform.flip(IMAGEM_PROJETIL, False, True)
    return {"rect": rect, "img": img_invertida}


# --- FUNÇÕES DE INTERFACE E CONTROLE (CORRIGIDAS) ---

POWER_UPS = [
    {"nome": "Hyper-Speed", "descricao": "Aumenta a velocidade de movimento da sua nave (V + 1)."},
    {"nome": "Dano Aprimorado", "descricao": "Aumenta o dano da sua arma (+5 Dano)."},
    {"nome": "Sorte do Saqueador", "descricao": "Aumenta o XP ganho por estrela coletada."},
    {"nome": "Fogo Rápido", "descricao": "Diminui o Cooldown do seu tiro (Atira mais rápido)."},
]


def aplicar_power_up(nome_power_up):
    global velocidade, XP_POR_ESTRELA, objetos_assets, player_cooldown_max, PLAYER_DANO
    if nome_power_up == "Hyper-Speed":
        velocidade += 1
    elif nome_power_up == "Dano Aprimorado":
        PLAYER_DANO += 5
    elif nome_power_up == "Sorte do Saqueador":
        XP_POR_ESTRELA += 10
        objetos_assets[1]['xp'] = XP_POR_ESTRELA
    elif nome_power_up == "Fogo Rápido":
        player_cooldown_max = max(5, player_cooldown_max - 3)
    print(f"Power-up '{nome_power_up}' aplicado! Nível: {nivel}")


def desenhar_botao(texto, x, y, largura, altura, cor_normal, cor_hover, mouse_pos):
    cor = cor_hover if (x <= mouse_pos[0] <= x + largura and y <= mouse_pos[1] <= y + altura) else cor_normal
    pygame.draw.rect(tela, cor, (x, y, largura, altura))
    pygame.draw.rect(tela, BRANCO, (x, y, largura, altura), 2)
    texto_botao = fonte.render(texto, True, BRANCO)
    texto_x = x + (largura - texto_botao.get_width()) // 2
    texto_y = y + (altura - texto_botao.get_height()) // 2
    tela.blit(texto_botao, (texto_x, texto_y))


def tela_escolha_power_up():
    power_ups_escolhidos = random.sample(POWER_UPS, 3)
    escolhendo = True
    while escolhendo:
        mouse_pos = pygame.mouse.get_pos()

        tela.fill(AZUL_ESCURO)
        texto_titulo = fonte.render(f"NÍVEL {nivel} ALCANÇADO!", True, AMARELO)
        texto_instrucao = fonte.render("Escolha um Power-up:", True, BRANCO)
        tela.blit(texto_titulo, (largura // 2 - texto_titulo.get_width() // 2, 50))
        tela.blit(texto_instrucao, (largura // 2 - texto_instrucao.get_width() // 2, 100))

        botoes = []
        y_start = 180
        for i, pu in enumerate(power_ups_escolhidos):
            x, y, w, h = 50, y_start + i * 130, 300, 100
            botoes.append((x, y, w, h, pu))
            cor_normal = (50, 50, 100)
            cor_hover = (80, 80, 150)
            desenhar_botao(pu['nome'], x, y, w, h, cor_normal, cor_hover, mouse_pos)
            texto_desc = fonte_pequena.render(pu['descricao'], True, BRANCO)
            tela.blit(texto_desc, (x + 10, y + h // 2 + 10))

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                return False
            elif evento.type == pygame.MOUSEBUTTONDOWN:
                if evento.button == 1:
                    for x, y, w, h, pu in botoes:
                        if x <= mouse_pos[0] <= x + w and y <= mouse_pos[1] <= y + h:
                            aplicar_power_up(pu['nome'])
                            escolhendo = False;
                            return True
        pygame.display.flip()
        clock.tick(60)
    return True


def checar_level_up(ganho_xp):
    global nivel, xp_atual, xp_proximo_nivel
    xp_atual += ganho_xp

    if xp_atual >= xp_proximo_nivel:
        xp_excedente = xp_atual - xp_proximo_nivel
        nivel += 1
        xp_atual = xp_excedente
        xp_base = 100
        fator_crescimento = 60
        expoente = 1.5
        xp_proximo_nivel = xp_base + int((nivel ** expoente) * fator_crescimento)
        if not tela_escolha_power_up(): return False

    return True


def reiniciar_jogo(player_skin_img):
    global jogador, obstaculos, tempo_inicio, tempo_atual, nome_jogador, projeteis_inimigos
    global nivel, xp_atual, xp_proximo_nivel, boss_ativo, tempo_proximo_boss, player_projeteis
    global player_cooldown_max, PLAYER_DANO, XP_POR_ESTRELA, velocidade, IMAGEM_PLAYER

    IMAGEM_PLAYER = player_skin_img
    # Redefine o retangulo do jogador com o tamanho da nova skin
    jogador = IMAGEM_PLAYER.get_rect(x=180, y=500)

    obstaculos = [];
    projeteis_inimigos = [];
    player_projeteis = []
    # Reseta o tempo de início do jogo
    tempo_inicio = pygame.time.get_ticks()
    tempo_atual = 0

    # Reseta o progresso do jogo
    nivel = 1;
    xp_atual = 0;
    xp_proximo_nivel = 100
    boss_ativo = False;
    tempo_proximo_boss = 30

    # Reseta as estatísticas base
    velocidade = 5;
    PLAYER_DANO = 10
    XP_POR_ESTRELA = 25
    player_cooldown_max = 15
    objetos_assets[1]['xp'] = XP_POR_ESTRELA


def desenhar_campo_texto(texto, x, y, largura, altura, ativo):
    cor = (100, 100, 100) if ativo else (70, 70, 70)
    pygame.draw.rect(tela, cor, (x, y, largura, altura))
    pygame.draw.rect(tela, BRANCO, (x, y, largura, altura), 2)
    texto_surface = fonte.render(texto, True, BRANCO)
    tela.blit(texto_surface, (x + 5, y + (altura - texto_surface.get_height()) // 2))
    if ativo:
        if pygame.time.get_ticks() % 1000 < 500:
            cursor_x = x + 5 + texto_surface.get_width()
            pygame.draw.line(tela, BRANCO, (cursor_x, y + 5), (cursor_x, y + altura - 5), 2)


def tela_selecao_skin():
    global IMAGEM_PLAYER, jogador

    while True:
        mouse_pos = pygame.mouse.get_pos()
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT: return None
            if evento.type == pygame.MOUSEBUTTONDOWN:
                if evento.button == 1:
                    # Lógica de seleção de skin
                    for i, skin in enumerate(PLAYER_SKINS):
                        x_skin = 50 + i * 120 + 10 * i
                        w_btn, h_btn = 100, 30
                        y_skin_btn = 350

                        if (x_skin <= mouse_pos[0] <= x_skin + w_btn and
                                y_skin_btn <= mouse_pos[1] <= y_skin_btn + h_btn):
                            IMAGEM_PLAYER = skin["img"]
                            jogador.size = IMAGEM_PLAYER.get_size()

                            # Botão Confirmar
                    x_conf, y_conf, w_conf, h_conf = largura // 2 - 100, altura - 70, 200, 50
                    if (x_conf <= mouse_pos[0] <= x_conf + w_conf and
                            y_conf <= mouse_pos[1] <= y_conf + h_conf):
                        return IMAGEM_PLAYER

        tela.fill(AZUL_ESCURO)
        texto_titulo = fonte.render("ESCOLHA SUA NAVE", True, AMARELO)
        tela.blit(texto_titulo, (largura // 2 - texto_titulo.get_width() // 2, 50))

        # Desenhar as 3 opções de skin
        for i, skin in enumerate(PLAYER_SKINS):
            x_area = 50 + i * 120 + 10 * i
            w_btn, h_btn = 100, 30

            texto_nome = fonte_pequena.render(skin["nome"], True, BRANCO)
            tela.blit(texto_nome, (x_area + (100 - texto_nome.get_width()) // 2, 120))

            x_img = x_area + (100 - skin["img"].get_width()) // 2
            y_img = 150 + (100 - skin["img"].get_height()) // 2
            tela.blit(skin["img"], (x_img, y_img))
            pygame.draw.rect(tela, BRANCO, (x_area, 150, 100, 100), 1)  # Moldura

            # Botão de Selecionar
            cor_normal = (50, 50, 100)
            cor_selecionada = (0, 150, 0)
            cor = cor_selecionada if IMAGEM_PLAYER == skin["img"] else cor_normal
            x_btn = x_area
            y_btn = 350

            desenhar_botao("Selecionar", x_btn, y_btn, w_btn, h_btn, cor, (80, 80, 150), mouse_pos)

        # Botão Confirmar
        x_conf, y_conf, w_conf, h_conf = largura // 2 - 100, altura - 70, 200, 50
        desenhar_botao("CONFIRMAR", x_conf, y_conf, w_conf, h_conf, (0, 100, 0), (0, 150, 0), mouse_pos)

        pygame.display.flip()
        clock.tick(60)


# FUNÇÕES DE INTERFACE PARA CORRIGIR O NAMERROR
def atualizar_pontuacao():
    global tempo_atual
    tempo_atual = (pygame.time.get_ticks() - tempo_inicio) // 1000


def desenhar_barra_boss(boss_obj):
    hp_percent = boss_obj['hp'] / boss_obj['max_hp']
    barra_largura_total = 300
    barra_preenchida = int(barra_largura_total * hp_percent)

    x, y = largura // 2 - barra_largura_total // 2, 90

    pygame.draw.rect(tela, (50, 50, 50), (x, y, barra_largura_total, 15))
    pygame.draw.rect(tela, ROXO, (x, y, barra_preenchida, 15))
    pygame.draw.rect(tela, BRANCO, (x, y, barra_largura_total, 15), 2)

    texto_hp = fonte_pequena.render(f"BOSS HP: {int(boss_obj['hp'])}", True, BRANCO)
    tela.blit(texto_hp, (x + 10, y + 2))


def desenhar_interface():
    # Desenha o Tempo, Nível e Barra de XP
    atualizar_pontuacao()

    minutos = tempo_atual // 60
    segundos = tempo_atual % 60
    texto_tempo = fonte.render(f"Tempo: {minutos:02d}:{segundos:02d}", True, BRANCO)
    tela.blit(texto_tempo, (10, 10))

    texto_nivel = fonte.render(f"Nível: {nivel}", True, AZUL_CLARO)
    tela.blit(texto_nivel, (largura - texto_nivel.get_width() - 10, 10))

    barra_largura = 150
    barra_altura = 10
    xp_percent = (xp_atual / xp_proximo_nivel) if xp_proximo_nivel > 0 else 0
    xp_preenchido = int(barra_largura * xp_percent)

    pygame.draw.rect(tela, (50, 50, 50), (largura - barra_largura - 10, 50, barra_largura, barra_altura))
    pygame.draw.rect(tela, AZUL_CLARO, (largura - barra_largura - 10, 50, xp_preenchido, barra_altura))
    pygame.draw.rect(tela, BRANCO, (largura - barra_largura - 10, 50, barra_largura, barra_altura), 1)


# FIM DA CORREÇÃO

def tela_digitar_nome():
    global nome_jogador
    nome_jogador = ""
    digitando = True
    campo_ativo = True
    campo_rect = pygame.Rect(largura // 2 - 150, altura // 2, 300, 40)

    while digitando:
        mouse_pos = pygame.mouse.get_pos()
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                return False
            elif evento.type == pygame.KEYDOWN:
                if campo_ativo:
                    if evento.key == pygame.K_RETURN and nome_jogador.strip():
                        digitando = False
                    elif evento.key == pygame.K_BACKSPACE:
                        nome_jogador = nome_jogador[:-1]
                    elif evento.key == pygame.K_ESCAPE:
                        return False
                    elif evento.unicode.isalnum() or evento.unicode in " _-":
                        if len(nome_jogador) < 15: nome_jogador += evento.unicode
            elif evento.type == pygame.MOUSEBUTTONDOWN:
                campo_ativo = campo_rect.collidepoint(mouse_pos)

        tela.fill(AZUL_ESCURO)
        texto_titulo = fonte.render("DIGITE SEU NOME", True, BRANCO)
        texto_instrucao = fonte_pequena.render("Pressione ENTER para continuar", True, (200, 200, 200))
        tela.blit(texto_titulo, (largura // 2 - texto_titulo.get_width() // 2, altura // 2 - 60))
        tela.blit(texto_instrucao, (largura // 2 - texto_instrucao.get_width() // 2, altura // 2 + 50))
        desenhar_campo_texto(nome_jogador, campo_rect.x, campo_rect.y, campo_rect.width, campo_rect.height, campo_ativo)
        pygame.display.flip()
        clock.tick(60)
    return True


def tela_game_over():
    global rodando, nome_jogador, IMAGEM_PLAYER

    if not nome_jogador and not tela_digitar_nome(): return False
    if nome_jogador: salvar_pontuacao(nome_jogador, nivel, tempo_atual)

    top_pontuacoes = obter_top_pontuacoes()
    botao_reiniciar_rect = (largura // 2 - 100, altura // 2 + 160, 200, 50)
    botao_sair_rect = (largura // 2 - 100, altura // 2 + 220, 200, 50)
    aguardando = True

    while aguardando:
        mouse_pos = pygame.mouse.get_pos()
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                aguardando = False;
                rodando = False;
                return False
            elif evento.type == pygame.MOUSEBUTTONDOWN:
                if evento.button == 1:
                    # CLIQUE EM REINICIAR
                    if (botao_reiniciar_rect[0] <= mouse_pos[0] <= botao_reiniciar_rect[0] + botao_reiniciar_rect[2] and
                            botao_reiniciar_rect[1] <= mouse_pos[1] <= botao_reiniciar_rect[1] + botao_reiniciar_rect[
                                3]):

                        selecionada_skin = tela_selecao_skin()
                        if selecionada_skin is not None:
                            reiniciar_jogo(selecionada_skin);
                            aguardando = False;
                            return True  # Retorna True para continuar o loop principal
                        else:
                            aguardando = False;
                            rodando = False;
                            return False

                    # CLIQUE EM SAIR
                    elif (botao_sair_rect[0] <= mouse_pos[0] <= botao_sair_rect[0] + botao_sair_rect[2] and
                          botao_sair_rect[1] <= mouse_pos[1] <= botao_sair_rect[1] + botao_sair_rect[3]):
                        aguardando = False;
                        rodando = False;
                        return False  # Retorna False para parar o loop principal

        tela.fill(AZUL_ESCURO)
        texto_game_over = fonte.render("NAVE DESTRUIDA!", True, VERMELHO)
        texto_nivel_final = fonte.render(f"Nível Máximo Alcançado: {nivel}", True, BRANCO)
        texto_tempo_final = fonte.render(f"Tempo de Sobrevivência: {tempo_atual // 60:02d}:{tempo_atual % 60:02d}",
                                         True, BRANCO)
        tela.blit(texto_game_over, (largura // 2 - texto_game_over.get_width() // 2, altura // 2 - 150))
        tela.blit(texto_nivel_final, (largura // 2 - texto_nivel_final.get_width() // 2, altura // 2 - 110))
        tela.blit(texto_tempo_final, (largura // 2 - texto_tempo_final.get_width() // 2, altura // 2 - 70))
        texto_ranking = fonte.render("TOP 3 NÍVEIS", True, AMARELO)
        tela.blit(texto_ranking, (largura // 2 - texto_ranking.get_width() // 2, altura // 2 - 30))
        for i, record in enumerate(top_pontuacoes):
            texto_record = fonte_pequena.render(
                f"{i + 1}. {record['nome']}: NÍVEL {record['pontuacao']} - {record['tempo'] // 60:02d}:{record['tempo'] % 60:02d}",
                True, BRANCO
            )
            tela.blit(texto_record, (largura // 2 - texto_record.get_width() // 2, altura // 2 + i * 25))
        desenhar_botao("REINICIAR MISSAO", botao_reiniciar_rect[0], botao_reiniciar_rect[1], botao_reiniciar_rect[2],
                       botao_reiniciar_rect[3], (0, 100, 0), (0, 150, 0), mouse_pos)
        desenhar_botao("SAIR", botao_sair_rect[0], botao_sair_rect[1], botao_sair_rect[2], botao_sair_rect[3],
                       (100, 0, 0), (150, 0, 0), mouse_pos)
        pygame.display.flip()
        clock.tick(60)
    return False


def tela_de_inicio():
    botao_iniciar_rect = (largura // 2 - 100, altura // 2, 200, 50)
    botao_sair_rect = (largura // 2 - 100, altura // 2 + 70, 200, 50)
    while True:
        mouse_pos = pygame.mouse.get_pos()
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT: return False
            if evento.type == pygame.MOUSEBUTTONDOWN:
                if evento.button == 1:
                    if (botao_iniciar_rect[0] <= mouse_pos[0] <= botao_iniciar_rect[0] + botao_iniciar_rect[2] and
                            botao_iniciar_rect[1] <= mouse_pos[1] <= botao_iniciar_rect[1] + botao_iniciar_rect[3]):
                        return True
                    if (botao_sair_rect[0] <= mouse_pos[0] <= botao_sair_rect[0] + botao_sair_rect[2] and
                            botao_sair_rect[1] <= mouse_pos[1] <= botao_sair_rect[1] + botao_sair_rect[3]):
                        return False

        tela.fill(AZUL_ESCURO)
        tela.blit(IMAGEM_FUNDO, (0, 0))
        texto_titulo = fonte.render("SPACE COLLECTOR", True, AMARELO)
        tela.blit(texto_titulo, (largura // 2 - texto_titulo.get_width() // 2, 150))
        texto_instrucao1 = fonte_pequena.render("Use as SETAS para mover", True, BRANCO)
        texto_instrucao2 = fonte_pequena.render("Use a tecla ESPAÇO para atirar", True, BRANCO)
        tela.blit(texto_instrucao1, (largura // 2 - texto_instrucao1.get_width() // 2, 220))
        tela.blit(texto_instrucao2, (largura // 2 - texto_instrucao2.get_width() // 2, 250))
        desenhar_botao("INICIAR JOGO", botao_iniciar_rect[0], botao_iniciar_rect[1], botao_iniciar_rect[2],
                       botao_iniciar_rect[3], (0, 100, 0), (0, 150, 0), mouse_pos)
        desenhar_botao("SAIR", botao_sair_rect[0], botao_sair_rect[1], botao_sair_rect[2], botao_sair_rect[3],
                       (100, 0, 0), (150, 0, 0), mouse_pos)
        pygame.display.flip()
        clock.tick(60)


# --- FLUXO DE INÍCIO DO JOGO ---
rodando = tela_de_inicio()

if rodando:
    skin_escolhida = tela_selecao_skin()

    if skin_escolhida is not None:
        reiniciar_jogo(skin_escolhida)

        if not tela_digitar_nome():
            rodando = False
    else:
        rodando = False

# --- LOOP PRINCIPAL DO JOGO (CORREÇÃO DO FIM DE JOGO) ---
while rodando:
    tela.blit(IMAGEM_FUNDO, (0, 0))

    # 1. TRATAMENTO DE INPUT E TIRO DO JOGADOR
    teclas = pygame.key.get_pressed()
    if teclas[pygame.K_LEFT] and jogador.left > 0: jogador.x -= velocidade
    if teclas[pygame.K_RIGHT] and jogador.right < largura: jogador.x += velocidade
    if teclas[pygame.K_UP] and jogador.top > 0: jogador.y -= velocidade
    if teclas[pygame.K_DOWN] and jogador.bottom < altura: jogador.y += velocidade
    player_cooldown = max(0, player_cooldown - 1)
    if teclas[pygame.K_SPACE] and player_cooldown == 0:
        player_projeteis.append(criar_player_projetil())
        player_cooldown = player_cooldown_max
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            rodando = False

    if not rodando: break  # Checa se a janela foi fechada

    # 2. GERAÇÃO DE OBJETOS E BOSS
    if not boss_ativo and tempo_atual >= tempo_proximo_boss:
        obstaculos.append(criar_objeto_boss())
        boss_ativo = True
        tempo_proximo_boss += 60
    chance_spawn = max(5, SPAWN_CHANCE_BASE - (nivel // 2))
    if not boss_ativo and random.randint(1, chance_spawn) == 1:
        obstaculos.append(criar_objeto())

    # 3. LÓGICA DO PROJÉTIL DO JOGADOR
    novos_projeteis_player = []
    for p_proj in player_projeteis:
        p_proj["rect"].y -= player_velocidade_tiro
        acertou_alvo = False
        novos_obstaculos_temp = []
        for obstaculo in obstaculos:
            if obstaculo["rect"].colliderect(p_proj["rect"]):
                obj_type = obstaculo["asset_info"]["type"]
                if obj_type != STAR_TYPE:
                    obstaculo["hp"] -= PLAYER_DANO
                    acertou_alvo = True
                    if obstaculo["hp"] <= 0:
                        if obj_type == BOSS_TYPE:
                            xp_ganho = obstaculo["asset_info"]["xp"] * nivel
                            if not checar_level_up(xp_ganho): rodando = False; break
                            boss_ativo = False
                        elif obj_type == ENEMY_TYPE or obj_type == METEOR_TYPE:
                            pass
                        continue
            novos_obstaculos_temp.append(obstaculo)
        obstaculos = novos_obstaculos_temp
        if not acertou_alvo and p_proj["rect"].y > 0:
            novos_projeteis_player.append(p_proj)
            tela.blit(p_proj["img"], p_proj["rect"])
    player_projeteis = novos_projeteis_player
    if not rodando: break

    # 4. LÓGICA DE OBSTÁCULOS E PROJÉTEIS INIMIGOS
    novos_obstaculos = []
    velocidade_queda_atual = VELOCIDADE_INIMIGOS_BASE + (nivel // 4)
    for obstaculo in obstaculos:
        obj_type = obstaculo["asset_info"]["type"]

        if obj_type != BOSS_TYPE:
            obstaculo["rect"].y += velocidade_queda_atual

        if obj_type == METEOR_TYPE:
            vel_h = obstaculo['velocidade_horizontal']
            direcao = obstaculo['direcao_horizontal']
            obstaculo["rect"].x += vel_h * direcao

        if obj_type == ENEMY_TYPE or obj_type == BOSS_TYPE:
            obstaculo['cooldown'] -= 1
            if obstaculo['cooldown'] <= 0:
                if obj_type == BOSS_TYPE:
                    novos_tiros = []
                    if obstaculo['padrao'] != 4:
                        novos_tiros, _ = atirar_padrao_boss(obstaculo, obstaculo['padrao'])
                        projeteis_inimigos.extend(novos_tiros)
                    if obstaculo['padrao'] == 4:
                        obstaculo['padrao'] = random.randint(1, 3)
                    else:
                        if random.random() < 0.5:
                            obstaculo['padrao'] = 4
                        else:
                            obstaculo['padrao'] = random.randint(1, 3)
                    _, cooldown_proximo = atirar_padrao_boss(obstaculo, obstaculo['padrao'])
                    obstaculo['cooldown'] = random.randint(cooldown_proximo - 10, cooldown_proximo)
                else:
                    projeteis_inimigos.append(criar_projetil_inimigo(obstaculo["rect"].x, obstaculo["rect"].y))
                    cooldown_atual = max(30, COOLDOWN_INIMIGO_BASE - (nivel * 5))
                    obstaculo['cooldown'] = random.randint(cooldown_atual - 10, cooldown_atual)

        # Colisão do Jogador com Objeto/Obstáculo
        if obstaculo["rect"].colliderect(jogador):
            if obj_type == STAR_TYPE:
                if not checar_level_up(obstaculo["asset_info"]["xp"]): rodando = False; break
                continue  # Estrelas desaparecem após coleta
            elif obj_type != STAR_TYPE:
                if not tela_game_over():
                    rodando = False;
                    break  # Sai do loop se o jogador perder e escolher não reiniciar

        if (obstaculo["rect"].bottom > 0 and obstaculo["rect"].top < altura and
                obstaculo["rect"].left < largura and obstaculo["rect"].right > 0):
            novos_obstaculos.append(obstaculo)
            tela.blit(obstaculo["asset_info"]["img"], obstaculo["rect"])
            if obj_type == BOSS_TYPE:
                desenhar_barra_boss(obstaculo)

    obstaculos = novos_obstaculos
    if not rodando: break

    # 5. MOVIMENTO E COLISÃO DOS PROJÉTEIS INIMIGOS
    novos_projeteis_inimigos = []
    for p_inimigo in projeteis_inimigos:
        velocidade_tiro = p_inimigo.get("velocidade", VELOCIDADE_PROJETIL_BASE)
        p_inimigo["rect"].y += velocidade_tiro

        # Colisão do Jogador com Projétil Inimigo
        if p_inimigo["rect"].colliderect(jogador):
            if not tela_game_over():
                rodando = False;
                break  # Sai do loop se o jogador perder e escolher não reiniciar

        if p_inimigo["rect"].y < altura:
            novos_projeteis_inimigos.append(p_inimigo)
            tela.blit(p_inimigo["img"], p_inimigo["rect"])

    projeteis_inimigos = novos_projeteis_inimigos
    if not rodando: break

    # 6. ATUALIZAÇÃO DA TELA
    # Desenhar jogador
    tela.blit(IMAGEM_PLAYER, jogador)
    desenhar_interface()  # Chama a função corrigida

    pygame.display.flip()
    clock.tick(60)

pygame.quit()