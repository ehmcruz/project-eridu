import csv
import sys

class orcamento_t:
	def __init__ (self):
		print("orcamento init")
		self.lojas = list()
		self.itens = list()
		self.qtds = list()
		self.precos = list()
		self.fretes = list()

	def load_csv (self, arquivo_entrada_nome):
		linha_i = 0
		tem_frete = False

		# estagio 1
		# carregar csv na memoria

		with open(arquivo_entrada_nome) as arq_csv:
			arq_csv_leitor = csv.reader(arq_csv, delimiter=',')
			
			for linha in arq_csv_leitor:
				if linha_i == 0:
					if linha[0] != "Item":
						print(f"A primeira coluna deve se chamar \"Item\", nao {linha[0]}")
						exit()
					if linha[1] != "Qtd":
						print(f"A segunda coluna deve se chamar \"Qtd\", nao {linha[1]}")
						exit()

					for i in range(2, len(linha)):
						self.lojas.append(linha[i])

					print(f"{len(self.lojas)} lojas detectadas: {', '.join(self.lojas)}")

					linha_i += 1
				else:
					if len(linha) != len(self.lojas)+2:
						print(f"Todas as linhas devem ter {len(self.lojas)+2} colunas, mas a linha {linha_i+1} tem {len(linha)}")
						exit()
					if tem_frete == True:
						print("O Frete deve ser a ultima linha")
						exit()
					if linha[0] == "Frete":
						tem_frete = True
						for i in range(2, len(linha)):
							self.fretes.append(str(linha[i]))
					else: # eh um produto
						self.itens.append(str(linha[0]))
						self.qtds.append(str(linha[1]))
						p = list()

						for i in range(2, len(linha)):
							p.append(str(linha[i]))

						self.precos.append(p)

					linha_i += 1

		if tem_frete == False:
			print("Eh obrigatorio incluir o Frete como ultimo item")
			exit()

		# estagio 2
		# processar dados

		usa_virgula = False
		usa_ponto = False

		for i in range(0, len(self.itens)):
			if "," in self.qtds[i]:
				usa_virgula = True
			if "." in self.qtds[i]:
				usa_ponto = True
			for j in range(0, len(self.precos[i])):
				if "," in self.precos[i][j]:
					usa_virgula = True
				if "." in self.precos[i][j]:
					usa_ponto = True

		for i in range(0, len(self.fretes)):
			if "," in self.fretes[i]:
				usa_virgula = True
			if "." in self.fretes[i]:
				usa_ponto = True

		print(f"usa virgula nos numeros: {usa_virgula}")
		print(f"usa ponto nos numeros: {usa_ponto}")

		if usa_virgula and usa_ponto:
			print("erro! decida-se entre virgula ou ponto")
			exit()

		if usa_virgula:
			print("convertendo de virgula para ponto...")

			for i in range(0, len(self.itens)):
				self.qtds[i] = self.qtds[i].replace(",", ".")
				for j in range(0, len(self.precos[i])):
					self.precos[i][j] = self.precos[i][j].replace(",", ".")

			for i in range(0, len(self.fretes)):
				self.fretes[i] = self.fretes[i].replace(",", ".")

		# trocar vazio por infinito, para forçar nao escolher da loja
		# caso contrario, converte para numero

		print("processando vazios...")

		for i in range(0, len(self.itens)):
			if not self.qtds[i].strip():
				self.qtds[i] = 0
			else:
				self.qtds[i] = float(self.qtds[i])
			for j in range(0, len(self.precos[i])):
				if not self.precos[i][j].strip():
					self.precos[i][j] = 9999999
				else:
					self.precos[i][j] = float(self.precos[i][j])

		for i in range(0, len(self.itens)):
			print(f"{self.itens[i]}   {self.qtds[i]}   {'   '.join(str(p) for p in self.precos[i])}")
		
		print(f'Processadas {linha_i} linhas.')

# ---------------------------------------------

if len(sys.argv) != 3:
	print("erro!\nUso: python3 eridu.py <csv-entrada> <csv-saida>")
	exit()

arquivo_entrada = sys.argv[1]
arquivo_saida = sys.argv[2]

print(f"{arquivo_entrada} -> {arquivo_saida}")

orcamento = orcamento_t()
orcamento.load_csv(arquivo_entrada)
