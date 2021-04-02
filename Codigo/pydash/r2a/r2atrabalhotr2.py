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
        
        # lista de vazões
        self.throughputs = []

        # lista de estimativa das vazões
        self.estimados_throughputs = []

        self.request_time = 0
        self.qi = []
        self.passagem = 0

        self.ts_menos1 = 0

    def handle_xml_request(self, msg):

        # inicia a contagem
        self.request_time = time.perf_counter()

        # passa a mensagem
        self.send_down(msg)

    def handle_xml_response(self, msg):

        parsed_mpd = parse_mpd(msg.get_payload())
        self.qi = parsed_mpd.get_qi()

        t = time.perf_counter() - self.request_time
        self.throughputs.append(msg.get_bit_length() / t)

        self.send_up(msg)

    def handle_segment_size_request(self, msg):

        self.request_time = time.perf_counter()

        # calcular o delta e o desvio!

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

        #selected_qi = self.qi[0]
        #for i in self.qi:
        #    if te > i:
        #        selected_qi = i
        #


        # placeholder
        selected_qi = 46980

        self.passagem += 1
        msg.add_quality_id(selected_qi)
        self.send_down(msg)

    def handle_segment_size_response(self, msg):
        
        t = time.perf_counter() - self.request_time
        self.throughputs.append(msg.get_bit_length() / t)
        self.send_up(msg)

    def initialize(self):
        pass

    def finalization(self):
        pass
