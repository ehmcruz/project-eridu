import csv
import sys
import xlsxwriter
import itertools

PRECO_INFINITO = 999999.0

class orcamento_t:
	def __init__ (self):
		print("orcamento init")
		self.lojas = list()
		self.itens = list()
		self.qtds = list()
		self.precos = list()
		self.fretes = list()

	def carregar_csv (self, arquivo_entrada_nome):
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
				self.qtds[i] = 0.0
			else:
				self.qtds[i] = float(self.qtds[i])
			for j in range(0, len(self.precos[i])):
				if not self.precos[i][j].strip():
					self.precos[i][j] = PRECO_INFINITO
				else:
					self.precos[i][j] = float(self.precos[i][j])

		for i in range(0, len(self.fretes)):
			if not self.fretes[i].strip():
				self.fretes[i] = 0.0
			else:
				self.fretes[i] = float(self.fretes[i])

		# imprime a tabela processada
		for i in range(0, len(self.itens)):
			print(f"{self.itens[i]}   {self.qtds[i]}   {'   '.join(str(p) for p in self.precos[i])}")
		print(f"Frete   {'   '.join(str(p) for p in self.fretes)}")
		
		print(f'Processadas {linha_i} linhas.')

	def calcular (self, arquivo_saida_nome):
		book = xlsxwriter.Workbook(arquivo_saida_nome)
		sh = book.add_worksheet("orcamento")

		formato_celula_prod_faltando = book.add_format()
		formato_celula_prod_faltando.set_font_color('red')

		# escrever cabecalho base

		sh.write(0, 0, "Ítem")
		sh.write(0, 1, "Qtd.")

		for i in range(0, len(self.lojas)):
			sh.write(0, i+2, self.lojas[i])

		# escrever itens

		for i in range(0, len(self.itens)):
			sh.write(i+1, 0, self.itens[i])
			sh.write(i+1, 1, self.qtds[i])

		linha_frete_xls = len(self.itens) + 1
		linha_total_xls = linha_frete_xls + 1

		sh.write(linha_frete_xls, 0, "Frete")
		sh.write(linha_total_xls, 0, "Total")

		print(f"calculando melhor com 1 loja")

		for j in range(0, len(self.lojas)):
			total = 0
			for i in range(0, len(self.itens)):
				if self.precos[i][j] != PRECO_INFINITO:
					sh.write(i+1, j+2, self.precos[i][j])
					total += self.precos[i][j]
				else:
					sh.write(i+1, j+2, "Faltando", formato_celula_prod_faltando)
			total += self.fretes[j]
			sh.write(linha_frete_xls, j+2, self.fretes[j])
			sh.write(linha_total_xls, j+2, total)

		xlsx_col_ini = len(self.lojas) + 2

		xlsx_col = xlsx_col_ini

		vmax = list()

		for n in range(0, xlsx_col_ini):
			vmax.append(PRECO_INFINITO)

		ids_todas_lojas = list(range(0, len(self.lojas)))

		for n in range(2, len(self.lojas)+1):
			print(f"calculando melhor com {n} lojas")

			for ids_lojas in itertools.combinations(ids_todas_lojas, n):
				lojas = list()

				valor_frete = 0
				valor_total = 0

				for loja in ids_lojas:
					lojas.append(self.lojas[loja])
					valor_frete += self.fretes[loja]

				valor_total += valor_frete
				
				#print(total_por_loja)

				sh.write(0, xlsx_col, ', '.join(lojas))
				falta_prod = False

				for i in range(0, len(self.itens)):
					menor_preco_loja = ids_lojas[0]

					for loja in ids_lojas:
						if self.precos[i][loja] < self.precos[i][menor_preco_loja]:
							menor_preco_loja = loja
					
					if self.precos[i][menor_preco_loja] != PRECO_INFINITO:
						sh.write(i+1, xlsx_col, self.precos[i][menor_preco_loja])
						valor_total += self.precos[i][menor_preco_loja] * self.qtds[i]
					else:
						sh.write(i+1, xlsx_col, "Faltando", formato_celula_prod_faltando)
						falta_prod = True
				
				sh.write(linha_frete_xls, xlsx_col, valor_frete)
				sh.write(linha_total_xls, xlsx_col, valor_total)

				if falta_prod:
					vmax.append(PRECO_INFINITO)
				else:
					vmax.append(valor_total)

				print(lojas)

				xlsx_col += 1

		menor_preco_pos = xlsx_col_ini

		for c in range(xlsx_col_ini, xlsx_col):
			if vmax[c] < vmax[menor_preco_pos]:
				menor_preco_pos = c

		formato_celula_menor_preco = book.add_format()
		formato_celula_menor_preco.set_font_color('green')

		sh.write(linha_total_xls+1, menor_preco_pos, vmax[menor_preco_pos], formato_celula_menor_preco)

		book.close()

# ---------------------------------------------

if len(sys.argv) != 3:
	print("erro!\nUso: python3 eridu.py <csv-entrada> <xlsx-saida>")
	exit()

arquivo_entrada = sys.argv[1]
arquivo_saida = sys.argv[2]

print(f"{arquivo_entrada} -> {arquivo_saida}")

orcamento = orcamento_t()
orcamento.carregar_csv(arquivo_entrada)
orcamento.calcular(arquivo_saida)

print("\nEu nao me responsabilizo pelos resultados!")