import pygame
import random
import sys

# -------------------------------------------------------
# CONFIGURAÇÕES GERAIS
# -------------------------------------------------------
LARGURA = 800
ALTURA = 600
FPS = 60

# Cores (R, G, B)
PRETO  = (0, 0, 0)
BRANCO = (255, 255, 255)
VERDE  = (0, 255, 0)
VERMELHO = (255, 50, 50)
AMARELO  = (255, 220, 0)
CIANO    = (0, 200, 255)
CINZA    = (100, 100, 100)

# -------------------------------------------------------
# CLASSE: JOGADOR
# -------------------------------------------------------
class Jogador:
    def __init__(self):
        self.largura = 50
        self.altura  = 30
        self.x = LARGURA // 2 - self.largura // 2
        self.y = ALTURA - 60
        self.velocidade = 5
        self.cor = CIANO
        self.vidas = 3
        self.invencivel = 0          # frames de invencibilidade após tomar dano

    def mover(self, teclas):
        if teclas[pygame.K_LEFT] and self.x > 0:
            self.x -= self.velocidade
        if teclas[pygame.K_RIGHT] and self.x < LARGURA - self.largura:
            self.x += self.velocidade

    def desenhar(self, tela):
        # Pisca quando invencível
        if self.invencivel > 0 and self.invencivel % 10 < 5:
            self.invencivel -= 1
            return
        if self.invencivel > 0:
            self.invencivel -= 1

        # Corpo da nave
        pygame.draw.rect(tela, self.cor, (self.x, self.y + 10, self.largura, self.altura - 10))
        # Cabine (triângulo feito com polígono)
        pygame.draw.polygon(tela, self.cor, [
            (self.x + self.largura // 2, self.y),
            (self.x + 10, self.y + 12),
            (self.x + self.largura - 10, self.y + 12),
        ])

    def rect(self):
        return pygame.Rect(self.x, self.y, self.largura, self.altura)


# -------------------------------------------------------
# CLASSE: TIRO DO JOGADOR
# -------------------------------------------------------
class Tiro:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.velocidade = 8
        self.largura = 4
        self.altura  = 14
        self.cor = AMARELO

    def mover(self):
        self.y -= self.velocidade

    def fora_da_tela(self):
        return self.y < 0

    def desenhar(self, tela):
        pygame.draw.rect(tela, self.cor, (self.x, self.y, self.largura, self.altura))
        pygame.draw.rect(tela, BRANCO,   (self.x + 1, self.y, 2, 4))

    def rect(self):
        return pygame.Rect(self.x, self.y, self.largura, self.altura)


# -------------------------------------------------------
# CLASSE: TIRO DO INIMIGO
# -------------------------------------------------------
class TiroInimigo:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.velocidade = 4
        self.largura = 4
        self.altura  = 12
        self.cor = VERMELHO

    def mover(self):
        self.y += self.velocidade

    def fora_da_tela(self):
        return self.y > ALTURA

    def desenhar(self, tela):
        pygame.draw.rect(tela, self.cor, (self.x, self.y, self.largura, self.altura))

    def rect(self):
        return pygame.Rect(self.x, self.y, self.largura, self.altura)


# -------------------------------------------------------
# CLASSE: INIMIGO
# -------------------------------------------------------
class Inimigo:
    def __init__(self, x, y, tipo=0):
        self.x = x
        self.y = y
        self.tipo = tipo          # 0 = básico, 1 = médio, 2 = chefe
        self.largura = 36
        self.altura  = 26
        self.animacao = 0         # alterna entre dois frames de desenho

        # Pontos e cor variam por tipo
        if tipo == 0:
            self.cor    = VERDE
            self.pontos = 10
        elif tipo == 1:
            self.cor    = AMARELO
            self.pontos = 20
        else:
            self.cor    = VERMELHO
            self.pontos = 40

    def desenhar(self, tela):
        x, y = self.x, self.y
        w, h = self.largura, self.altura
        a = self.animacao  # 0 ou 1

        # Corpo principal
        pygame.draw.rect(tela, self.cor, (x + 4, y + 4, w - 8, h - 8))

        # Antenas (alternam entre aberto e fechado)
        offset = 4 if a == 0 else 0
        pygame.draw.line(tela, self.cor, (x + 6,  y + 4), (x + 2 + offset, y - 4), 2)
        pygame.draw.line(tela, self.cor, (x + w - 6, y + 4), (x + w - 2 - offset, y - 4), 2)

        # Pernas (alternam)
        leg_y = y + h - 4 + (4 if a == 0 else 0)
        pygame.draw.line(tela, self.cor, (x + 8,     y + h - 4), (x + 4,     leg_y), 2)
        pygame.draw.line(tela, self.cor, (x + w - 8, y + h - 4), (x + w - 4, leg_y), 2)

        # Olhos
        pygame.draw.circle(tela, PRETO, (x + 10, y + 12), 4)
        pygame.draw.circle(tela, PRETO, (x + w - 10, y + 12), 4)
        pygame.draw.circle(tela, BRANCO, (x + 10, y + 12), 2)
        pygame.draw.circle(tela, BRANCO, (x + w - 10, y + 12), 2)

    def rect(self):
        return pygame.Rect(self.x, self.y, self.largura, self.altura)


# -------------------------------------------------------
# CLASSE: BARREIRA (proteção do jogador)
# -------------------------------------------------------
class Barreira:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.largura = 70
        self.altura  = 40
        self.vida    = 4   # quantos tiros aguenta

    def desenhar(self, tela):
        if self.vida <= 0:
            return
        # Cor vai escurecendo conforme perde vida
        intensidade = int(255 * self.vida / 4)
        cor = (0, intensidade, 0)
        pygame.draw.rect(tela, cor, (self.x, self.y, self.largura, self.altura), border_radius=6)
        # Rachaduras visuais
        if self.vida <= 2:
            pygame.draw.line(tela, PRETO, (self.x + 10, self.y + 5), (self.x + 30, self.y + 35), 2)
        if self.vida == 1:
            pygame.draw.line(tela, PRETO, (self.x + 40, self.y + 8), (self.x + 60, self.y + 30), 2)

    def rect(self):
        return pygame.Rect(self.x, self.y, self.largura, self.altura)


# -------------------------------------------------------
# FUNÇÕES AUXILIARES
# -------------------------------------------------------
def criar_inimigos():
    """Cria a grade de inimigos em 5 colunas x 4 linhas."""
    inimigos = []
    for linha in range(4):
        for col in range(10):
            x = 60 + col * 65
            y = 80 + linha * 55
            tipo = 2 if linha == 0 else (1 if linha == 1 else 0)
            inimigos.append(Inimigo(x, y, tipo))
    return inimigos

def criar_barreiras():
    """Cria 4 barreiras distribuídas na tela."""
    barreiras = []
    for i in range(4):
        x = 80 + i * 175
        y = ALTURA - 130
        barreiras.append(Barreira(x, y))
    return barreiras

def desenhar_hud(tela, fonte, pontuacao, vidas, nivel):
    """Desenha pontuação, vidas e nível na tela."""
    tela.blit(fonte.render(f"PONTOS: {pontuacao}", True, BRANCO), (10, 10))
    tela.blit(fonte.render(f"NÍVEL: {nivel}", True, BRANCO), (LARGURA // 2 - 40, 10))
    # Desenha corações pelas vidas
    for i in range(vidas):
        pygame.draw.polygon(tela, VERMELHO, [
            (LARGURA - 90 + i * 28 + 7, 16),
            (LARGURA - 90 + i * 28,     22),
            (LARGURA - 90 + i * 28 + 7, 32),
            (LARGURA - 90 + i * 28 + 14, 22),
        ])

def desenhar_tela_titulo(tela, fonte_grande, fonte):
    tela.fill(PRETO)
    titulo = fonte_grande.render("SPACE INVADERS", True, VERDE)
    tela.blit(titulo, (LARGURA // 2 - titulo.get_width() // 2, 180))
    sub = fonte.render("Pressione ENTER para jogar", True, BRANCO)
    tela.blit(sub, (LARGURA // 2 - sub.get_width() // 2, 300))
    dica = fonte.render("← → para mover   ESPAÇO para atirar", True, CINZA)
    tela.blit(dica, (LARGURA // 2 - dica.get_width() // 2, 360))

def desenhar_game_over(tela, fonte_grande, fonte, pontuacao, vitoria=False):
    tela.fill(PRETO)
    msg  = "VOCÊ VENCEU!" if vitoria else "GAME OVER"
    cor  = VERDE if vitoria else VERMELHO
    txt  = fonte_grande.render(msg, True, cor)
    tela.blit(txt, (LARGURA // 2 - txt.get_width() // 2, 200))
    pts  = fonte.render(f"Pontuação final: {pontuacao}", True, BRANCO)
    tela.blit(pts, (LARGURA // 2 - pts.get_width() // 2, 300))
    redo = fonte.render("Pressione ENTER para jogar novamente", True, CINZA)
    tela.blit(redo, (LARGURA // 2 - redo.get_width() // 2, 360))


# -------------------------------------------------------
# LOOP PRINCIPAL DO JOGO
# -------------------------------------------------------
def jogar():
    pygame.init()
    tela  = pygame.display.set_mode((LARGURA, ALTURA))
    pygame.display.set_caption("Space Invaders — Python")
    relogio = pygame.time.Clock()

    fonte_grande = pygame.font.SysFont("monospace", 48, bold=True)
    fonte        = pygame.font.SysFont("monospace", 22)

    # --- Estados do jogo ---
    TITULO    = "titulo"
    JOGANDO   = "jogando"
    GAME_OVER = "game_over"
    estado    = TITULO
    vitoria   = False

    # --- Variáveis de jogo ---
    jogador   = None
    inimigos  = []
    barreiras = []
    tiros     = []          # tiros do jogador
    tiros_inimigos = []
    pontuacao = 0
    nivel     = 1

    # Controle de movimento dos inimigos
    direcao      = 1        # 1 = direita, -1 = esquerda
    vel_inimigos = 1.2
    timer_inimigo_tiro  = 0
    intervalo_tiro      = 90  # frames entre tiros inimigos
    timer_animacao      = 0
    frame_animacao      = 0
    timer_descer        = 0

    def iniciar_jogo():
        nonlocal jogador, inimigos, barreiras, tiros, tiros_inimigos
        nonlocal pontuacao, nivel, direcao, vel_inimigos
        nonlocal timer_inimigo_tiro, timer_animacao, frame_animacao, timer_descer
        jogador   = Jogador()
        inimigos  = criar_inimigos()
        barreiras = criar_barreiras()
        tiros     = []
        tiros_inimigos = []
        pontuacao = 0
        nivel     = 1
        direcao   = 1
        vel_inimigos = 1.2
        timer_inimigo_tiro  = 0
        timer_animacao      = 0
        frame_animacao      = 0
        timer_descer        = 0

    delay_tiro = 0   # cooldown entre tiros do jogador

    # ---- LOOP ----
    while True:
        relogio.tick(FPS)

        # Eventos
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if evento.type == pygame.KEYDOWN:
                if estado == TITULO and evento.key == pygame.K_RETURN:
                    iniciar_jogo()
                    estado = JOGANDO
                elif estado == GAME_OVER and evento.key == pygame.K_RETURN:
                    estado = TITULO

        # ============ TELA DE TÍTULO ============
        if estado == TITULO:
            desenhar_tela_titulo(tela, fonte_grande, fonte)
            pygame.display.flip()
            continue

        # ============ GAME OVER ============
        if estado == GAME_OVER:
            desenhar_game_over(tela, fonte_grande, fonte, pontuacao, vitoria)
            pygame.display.flip()
            continue

        # ============ JOGANDO ============
        teclas = pygame.key.get_pressed()

        # Mover jogador
        jogador.mover(teclas)

        # Atirar (com cooldown)
        if delay_tiro > 0:
            delay_tiro -= 1
        if teclas[pygame.K_SPACE] and delay_tiro == 0:
            cx = jogador.x + jogador.largura // 2 - 2
            tiros.append(Tiro(cx, jogador.y))
            delay_tiro = 20

        # Mover tiros do jogador
        for t in tiros[:]:
            t.mover()
            if t.fora_da_tela():
                tiros.remove(t)

        # --- Movimento dos inimigos ---
        timer_animacao += 1
        if timer_animacao >= 30:
            timer_animacao = 0
            frame_animacao = 1 - frame_animacao
            for inv in inimigos:
                inv.animacao = frame_animacao

        # Verifica se algum inimigo bate nas bordas
        mover_x = vel_inimigos * direcao
        precisa_descer = False
        for inv in inimigos:
            nx = inv.x + mover_x
            if nx <= 0 or nx + inv.largura >= LARGURA:
                precisa_descer = True
                break

        if precisa_descer:
            direcao *= -1
            for inv in inimigos:
                inv.y += 18
        else:
            for inv in inimigos:
                inv.x += mover_x

        # Inimigos atiram
        timer_inimigo_tiro += 1
        if timer_inimigo_tiro >= intervalo_tiro and inimigos:
            timer_inimigo_tiro = 0
            atirador = random.choice(inimigos)
            cx = atirador.x + atirador.largura // 2 - 2
            tiros_inimigos.append(TiroInimigo(cx, atirador.y + atirador.altura))

        # Mover tiros inimigos
        for ti in tiros_inimigos[:]:
            ti.mover()
            if ti.fora_da_tela():
                tiros_inimigos.remove(ti)

        # --- COLISÕES ---

        # Tiro do jogador x inimigos
        for t in tiros[:]:
            for inv in inimigos[:]:
                if t.rect().colliderect(inv.rect()):
                    pontuacao += inv.pontos
                    inimigos.remove(inv)
                    if t in tiros:
                        tiros.remove(t)
                    break

        # Tiro do jogador x barreiras
        for t in tiros[:]:
            for b in barreiras:
                if b.vida > 0 and t.rect().colliderect(b.rect()):
                    b.vida -= 1
                    if t in tiros:
                        tiros.remove(t)

        # Tiro inimigo x jogador
        for ti in tiros_inimigos[:]:
            if ti.rect().colliderect(jogador.rect()) and jogador.invencivel == 0:
                jogador.vidas -= 1
                jogador.invencivel = 90
                tiros_inimigos.remove(ti)
                if jogador.vidas <= 0:
                    estado = GAME_OVER
                    vitoria = False

        # Tiro inimigo x barreiras
        for ti in tiros_inimigos[:]:
            for b in barreiras:
                if b.vida > 0 and ti.rect().colliderect(b.rect()):
                    b.vida -= 1
                    if ti in tiros_inimigos:
                        tiros_inimigos.remove(ti)

        # Inimigo chega até o jogador
        for inv in inimigos:
            if inv.y + inv.altura >= jogador.y:
                estado = GAME_OVER
                vitoria = False

        # Todos os inimigos destruídos → próximo nível
        if not inimigos:
            nivel += 1
            vel_inimigos += 0.4
            intervalo_tiro = max(30, intervalo_tiro - 10)
            inimigos  = criar_inimigos()
            barreiras = criar_barreiras()
            tiros.clear()
            tiros_inimigos.clear()

        # --- DESENHO ---
        tela.fill(PRETO)

        # Estrelas de fundo (simples)
        random.seed(42)
        for _ in range(60):
            sx = random.randint(0, LARGURA)
            sy = random.randint(0, ALTURA)
            pygame.draw.circle(tela, CINZA, (sx, sy), 1)
        random.seed()

        for b in barreiras:
            b.desenhar(tela)

        jogador.desenhar(tela)

        for t in tiros:
            t.desenhar(tela)
        for ti in tiros_inimigos:
            ti.desenhar(tela)
        for inv in inimigos:
            inv.desenhar(tela)

        desenhar_hud(tela, fonte, pontuacao, jogador.vidas, nivel)

        # Linha do chão
        pygame.draw.line(tela, CINZA, (0, ALTURA - 30), (LARGURA, ALTURA - 30), 1)

        pygame.display.flip()

# -------------------------------------------------------
# ENTRADA
# -------------------------------------------------------
if __name__ == "__main__":
    jogar()