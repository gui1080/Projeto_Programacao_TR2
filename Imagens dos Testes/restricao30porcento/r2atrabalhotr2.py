# Projeto de Programação para TR2
# UnB - 2020/02

# Ayllah Ahmad 17/0056465
# Guilherme Braga 17/0162290

from r2a.ir2a import IR2A
from player.parser import *
import time
import math
from statistics import mean

# (apenas fazendo alguns testes)

class R2ATrabalhoTR2(IR2A):

    def __init__(self, id):
        # init
        IR2A.__init__(self, id)


        self.throughputs = []               # lista de vazões
        self.estimados_throughputs = []     # lista de estimativa das vazões
        self.qi = []                        # lista de qualidades

        self.Rc = []                        # restrição de taxa de bits


        self.request_time = 0               # tempo de solicitação
        self.passagem = 0                   # quantidade de vezes que passou pelo código
        self.ts_menos1 = 0                  # Ts[i-1]
        self.delta = 0                      # delta, para a fórmula de Te
        self.te_menos2 = 0                  # Te[i-2]

        self.P0 = 0.05                      # parametros arbitrarios para calculo de delta
        # P0 = 0.2                          #parâmetro P0 da função logística delta
        self.k = 21                         # relacionados com a qualidade da conexão

        self.p = 0                          # desvio padrão normalizado de vazão sendo calculado

        self.mi = 0.5                       # mi[0, 0.5]


    def handle_xml_request(self, msg):

        self.request_time = time.perf_counter()     # inicia a contagem
        self.send_down(msg)                         # passa a mensagem

    def handle_xml_response(self, msg):

        parsed_mpd = parse_mpd(msg.get_payload())           # objeto parse_mpd
        t = time.perf_counter() - self.request_time         # coleta quanto tempo se passou


        self.qi = parsed_mpd.get_qi()                       # insere as qualidades do vídeo na lista de qualidades
        self.throughputs.append(msg.get_bit_length() / t)   # calcula a vazão para fazer a requisição do xml e coloca na lista de vazões
        self.send_up(msg)                                   # passa a mensagem

    def handle_segment_size_request(self, msg):

        self.request_time = time.perf_counter()      # inicia a contagem

        # ----------------------------------------
        # CALCULO DO DELTA

        # math.exp(x) retorna e^x
        # k e P0 dependem da conexão
        self.delta = (1 / (1 + (math.exp(-self.k * (self.p - self.P0)))))  # função logísitca da relação geral entre p e delta

        # ----------------------------------------
        # PARÂMETROS PARA ESTIMAR A VAZÃO
        # para obter a taxa de transferência estimada para o segmento i, usa-se uma forma de média em execução

        # Nas primeiras duas passagens não tem vazão para estimar
        # Então enche com as vazões medidas no começo
        if (self.passagem == 0):
            self.estimados_throughputs.append(self.throughputs[0])
            vazao_atual = self.throughputs[0]       # salvamos esse valor para calcular o desvio
            self.delta = 0                          # primeira vez que algoritmo roda, não tem Te(0) para calcular delta, nenhuma variação ocorreu

        if (self.passagem == 1):
            self.estimados_throughputs.append(self.throughputs[1])  # quando for tirar o mais antigo dessa lista, vai sair Te(i-2)

        if (self.passagem > 0):
            self.ts_menos1 = self.throughputs[0]    # pegando Ts(i-1)
            del self.throughputs[0]                 # mantendo uma lista só com throughput atual, próxima iteração vira Ts(i-1)

        # ----------------------------------------

        # calcula Te(i), bota ele na lista de vazões estimadas, deleta o mais antigo, passa para frente

        if (self.passagem > 1):

            # no final, temos que colocar o novo Te(i) na fila, para o ciclo repetir

            self.te_menos2 = self.estimados_throughputs[0]  # podemos retirar o elemento mais antigo dessa fila, sendo o Te(i-2)

            estimativa_atual = ((1 - self.delta) * self.te_menos2) + (self.delta * self.ts_menos1)

            self.estimados_throughputs.append(estimativa_atual)  # damos append na nova estimativa e deletamos
            del self.estimados_throughputs[0]

            self.p = abs(self.throughputs[0] - estimativa_atual) / estimativa_atual  # desvio normalizado de vazão

            # para obter a restrição de taxa de bits Rc(i) a partir da taxa de transferência estimada,uma média de segurança mi é usada
            restricao = ((1 - self.mi) * estimativa_atual)

            restrição_recuperação = (estimativa_atual * 0.3)

            self.Rc.append(restricao)

        else:
            estimativa_atual = 0
            restricao = 0
            self.Rc.append(0)


        # Prints :)
        print("********************************************************************************")
        print("VAZÃO                    :", self.throughputs)
        print("VAZÃO REAL MENOS 1       :", self.ts_menos1)
        print("LISTA DE VAZÃO ESTIMADA  :", self.estimados_throughputs)
        print("DELTA                    :", self.delta)
        print("ESTIMATIVA ATUAL         :", estimativa_atual)
        print("P                        :", self.p)
        print("RESTRIÇÃO                :", restricao)
        print("RESTRIÇÃO DE TAXA DE BITS:", self.Rc)
        print("QUANTIDADE QUE FALTA NO BUFFER:", self.whiteboard.get_amount_video_to_play())
        print("TAMANHO MÁXIMO DE BUFFER:", self.whiteboard.get_max_buffer_size())
        print("LISTA DE TRAVAMENTOS:", self.whiteboard.get_playback_pauses())                   # tupla - lista de pausas que ocorreu, junto dos momentos
        print("MOMENTO E TAMANHO DO BUFFER: ", self.whiteboard.get_playback_buffer_size())
        print("MOMENTO E STATUS:", self.whiteboard.get_playback_history())
        print("*********************************************************************************")

        # Com esse comando aqui vc muda o maximo do buffer de 60 pra 10
        # self.whiteboard.add_max_buffer_size(10)



        # CALCULO DO DESVIO
        # calculamos o desvio pra próxima iteração saber o valor necessário de p

        #self.p = 0.40  # placeholder pra equação do delta rodar

        # ----------------------------------------

        # seleciona qualidades para envio
        # qi[0] = 46980bps
        # qi[1] = 91917bps
        # ...
        # qi[18] = 4242923bps
        # qi[19] = 4726737bps

        # te é o throughput estimado
        # faz um for, compara com as opções, escolhe uma qualidade

        # selected_qi = self.qi[0]
        # for i in self.qi:
        #    if te > i:
        #        selected_qi = i
        #

        # placeholder
        # selected_qi = 46980


        selected_qi = self.qi[0]

    #-------------------------------------------------------------------------------------------------------------------------------------
        #for i in self.qi:
        #    if estimativa_atual > i:
        #        if self.whiteboard.get_amount_video_to_play() > 5:          #Verifica se o buffer tem espaço de armazenamento
        #            selected_qi = i
        #        else:
        #            selected_qi = self.qi[0]
    # -------------------------------------------------------------------------------------------------------------------------------------


        #Se o buffer tiver espaço realiza a operação com o valor da estimativa, caso contrário faz com que seja usada uma restrição para a taxa de bits

        if self.p < 0.4:      #Verifica se o desvio é menor que 0,4
            if self.whiteboard.get_amount_video_to_play() > 0:  #Verifica se há espaço no buffer
                for i in self.qi:
                    if estimativa_atual > i:
                        selected_qi = i
            else:
                for i in self.qi:
                    if restricao > i:
                        selected_qi = i
        else:
            for i in self.qi:
                    if restrição_recuperação > i:
                        selected_qi = i


        self.passagem += 1                  # contabiliza a passagem pelo código
        msg.add_quality_id(selected_qi)     # informa a qualidade escolhida
        self.send_down(msg)                 # passa a mensagem
        del self.Rc[0]                      # Deleta primeiro valor da lista para que esta possua sempre só 1 componente

    def handle_segment_size_response(self, msg):

        t = time.perf_counter() - self.request_time             # coleta quanto tempo se passou

        self.throughputs.append(msg.get_bit_length() / t)       # calcula a vazão para fazer a requisição do xml e coloca na lista de vazões
        self.send_up(msg)                                       # passa a mensagem

    def initialize(self):
        pass

    def finalization(self):
        pass
