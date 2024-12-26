import mysql.connector
from barcode import EAN13
from barcode.writer import ImageWriter
import os

# Configuração do banco de dados
db_config = {
    "host": "localhost",
    "user": "root",
    "password": "",  # Insira sua senha do MySQL, se houver
    "database": "produtosceamo",
}

# Conexão com o banco de dados
try:
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    print("Conexão com o banco de dados estabelecida com sucesso!")
except mysql.connector.Error as err:
    print(f"Erro ao conectar ao banco de dados: {err}")
    exit()


# Contador para gerar números únicos (começando de um número arbitrário)
barcode_counter = 100000000000  # 12 dígitos para o número base

# Diretório para salvar as imagens
output_dir = "imagens_codigos_barras"
os.makedirs(output_dir, exist_ok=True)

print("Bem-vindo ao Gerador de Códigos de Barras Únicos (EAN-13)")
print("Adicione seus produtos. Digite 'sair' para finalizar.")

while True:
    # Nome do produto
    product_name = input("Digite o nome do produto (ou 'sair' para finalizar): ")
    if product_name.lower() == "sair":
        break

    # Preço do produto
    try:
        product_price = float(input(f"Digite o preço do produto '{product_name}': "))
    except ValueError:
        print("Preço inválido. Por favor, insira um número válido.")
        continue

    # Quantidade em estoque
    try:
        stock_quantity = int(input(f"Digite a quantidade em estoque do produto '{product_name}': "))
    except ValueError:
        print("Quantidade inválida. Por favor, insira um número inteiro válido.")
        continue

    # Tipo de lanche
    product_type = input(f"Digite o tipo de lanche do produto '{product_name}': ")

    # Gera um número único para o código de barras
    barcode_number = str(barcode_counter)
    barcode_counter += 1  # Incrementa para garantir unicidade

    try:
        # Gera o código de barras com o dígito de verificação
        barcode = EAN13(barcode_number, writer=ImageWriter())
        complete_barcode_number = barcode.get_fullcode()  # Obtém o código completo com o dígito de verificação

        # Salva a imagem do código de barras
        output_file_name = f"{product_name.replace(' ', '_')}_barcode.png"
        output_file_path = os.path.join(output_dir, output_file_name)
        barcode.save(output_file_path)



        print(f"Código de barras gerado e salvo como {output_file_path} para o produto {product_name}.")
        print(f"Código de barras completo: {complete_barcode_number}")


        # Salva o produto no banco de dados
        insert_query = """
        INSERT INTO produto (nome, preco, quantidade_em_estoque, tipo_de_lanche, codigo_de_barras, imagem_codigo_de_barras)
        VALUES (%s, %s, %s, %s, %s, %s);
        """
        cursor.execute(insert_query, (product_name, product_price, stock_quantity, product_type, complete_barcode_number, output_file_name))
        conn.commit()
        print(f"Produto '{product_name}' adicionado ao banco de dados com sucesso!")

    except Exception as e:
        print(f"Erro ao processar o produto '{product_name}': {e}")
        continue

# Finaliza a conexão com o banco de dados
cursor.close()
conn.close()
print("\nTodos os produtos foram adicionados ao banco de dados com sucesso!")
