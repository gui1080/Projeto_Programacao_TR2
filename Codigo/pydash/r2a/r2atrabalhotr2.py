# Projeto de Programação para TR2
# UnB - 2020/02

# Ayllah Ahmad 17/0056465
# Guilherme Braga 17/0162290

from r2a.ir2a import IR2A
from player.parser import *
import time
from statistics import mean


# (apenas fazendo alguns testes)

class R2ATrabalhoTR2(IR2A):

    def __init__(self, id):
        # init
        IR2A.__init__(self, id)


        self.throughputs = []               # lista de vazões
        self.estimados_throughputs = []     # lista de estimativa das vazões
        self.qi = []                        # lista de qualidades


        self.request_time = 0               # tempo de solicitação
        self.passagem = 0                   # quantidade de vezes que passou pelo código
        self.ts_menos1 = 0                  # Ts[i-1]

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

        # calcular o delta e o desvio!

        # k =  21       #parâmetro k da função logística delta
        # P0 = 0.2      #parâmetro P0 da função logística delta

        #p = |throughputs[0] - estimados_throughputs[i]| / estimados_throughputs[i]             # desvio normalizado de vazão

        # a relação geral entre p e delta pode ser modelada pela função logísitca da seguinte forma:
        #delta = 1/(1+exp(-k*(p-P0)))

        # para obter a taxa de transferência estimada para o segmento i, usa-se uma forma de média em execução como segue:
        #estimados_throughputs[i] = (1-delta)*estimados_throughputs[i-2]+delta*throughputs[i-1]    # para i > 0
        #estimados_throughputs[i] = throughputs[i]                                                 # para i = 1,2

        # para obter a restrição de taxa de bits Rc(i) a partir da taxa de transferência estimada,uma média de segurança mi é usada
        #Rc[i] = (1-mi)*estimados_throughputs[i]        # restrição de taxa de bits com mi[0, 0.5]

        # nas primeiras duas passagens não tem vazão para estimar
        # então enche com as vazões medidas no começo
        if (self.passagem == 0):
            self.estimados_throughputs.append(self.throughputs[0])
        if (self.passagem == 1):
            self.estimados_throughputs.append(self.throughputs[1])
        # quando for tirar o mais antigo dessa lista, vai sair Te(i-2)

        if (self.passagem > 0):
            # pegando Ts(i-1)
            self.ts_menos1 = self.throughputs[0]
            # mantendo uma lista só com throughput atual, próxima iteração vira Ts(i-1)
            del self.throughputs[0]

        # calcula Te(i), bota ele na lista de vazões estimadas, deleta o mais antigo, passa para frente

        print("-----VAZÃO-------")
        print(self.throughputs)
        print("------------")
        print("------VAZÃO REAL MENOS 1------")
        print(self.ts_menos1)
        print("------------")
        print("------ LISTA DE VAZÃO ESTIMADA ------")
        print(self.estimados_throughputs)
        print("------------")

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
        selected_qi = 46980

        self.passagem += 1
        msg.add_quality_id(selected_qi)     # informa a qualidade escolhida
        self.send_down(msg)                 # passa a mensagem

    def handle_segment_size_response(self, msg):

        t = time.perf_counter() - self.request_time             # coleta quanto tempo se passou

        self.throughputs.append(msg.get_bit_length() / t)       # calcula a vazão para fazer a requisição do xml e coloca na lista de vazões
        self.send_up(msg)                                       # passa a mensagem

    def initialize(self):
        pass

    def finalization(self):
        pass
