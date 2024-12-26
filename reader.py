# let's read a barcode like the machine (product scanner in super market )


# using packages 
# pip install opencv-python 
# pip install pydub 
# pip install pyzbar 

import cv2 
from pyzbar.pyzbar import decode
from pydub import AudioSegment
from pydub.playback import play
import mysql.connector
from datetime import datetime
import time
import tempfile


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

AudioSegment.ffmpeg = "C:/ffmpeg/bin/ffmpeg.exe"
AudioSegment.ffprobe = "C:/ffmpeg/bin/ffprobe.exe"


# Configurar caminho temporário personalizado
#tempfile.tempdir = "C:/Temp"

# Reproduzir som
beep_sound = AudioSegment.from_mp3("beep.mp3")
#beep_sound.export("C:/Temp/beep.wav", format="wav")

# Caminho para o som do beep
#beep_sound_path = "C:/Users/Windows/Documents/LeitorCodigoBarras/short-beep-tone-47916.mp3"

# Carrega o som do beep
#beep_sound = AudioSegment.from_mp3(beep_sound_path)

# capture webcam 
cap = cv2.VideoCapture(0)



# Variáveis para controlar o delay entre leituras
last_barcode = None
last_read_time = 0
delay_seconds = 3


while cap.isOpened():
    success,frame = cap.read()
    # flip the image like mirror image 
    frame  = cv2.flip(frame,1)
    # detect the barcode 
    detectedBarcode = decode(frame)


    # if no any barcode detected 
    if not detectedBarcode:
        print("No any Barcode Detected")
    
    # if barcode detected 
    else:
        # Processa os códigos de barras detectados
        for barcode in detectedBarcode:
            # Decodifica os dados do código de barras
            barcode_data = barcode.data.decode('utf-8')  # Converte de bytes para string
            current_time = time.time()

            # Verifica se o código já foi lido recentemente
            if barcode_data == last_barcode and current_time - last_read_time < delay_seconds:
                print("Código de barras já registrado recentemente. Aguardando...")
                continue

            # Atualiza as variáveis de controle
            last_barcode = barcode_data
            last_read_time = current_time

            # Reproduz o som do beep
            play(beep_sound)

            try:
                print(f"Código de barras detectado: {barcode_data}")

                # Consulta o banco de dados para obter o ID do produto
                query = "SELECT id FROM produto WHERE codigo_de_barras = %s"
                cursor.execute(query, (barcode_data,))
                result = cursor.fetchone()

                if result:
                    product_id = result[0]
                    # Insere o registro na tabela `produtosvendidos`
                    insert_query = """
                    INSERT INTO produtosvendidos (id_do_produto, data_da_operacao)
                    VALUES (%s, %s)
                    """
                    current_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    cursor.execute(insert_query, (product_id, current_date))
                    conn.commit()

                    print(f"Produto ID {product_id} registrado como vendido em {current_date}.")
                    cv2.putText(frame, f"Produto vendido: {barcode_data}", (50, 50),
                                cv2.FONT_HERSHEY_COMPLEX, 1, (0, 255, 0), 2)
                else:
                    print("Produto não encontrado no banco de dados.")
                    cv2.putText(frame, "Produto não encontrado", (50, 50),
                                cv2.FONT_HERSHEY_COMPLEX, 1, (0, 0, 255), 2)

            except Exception as e:
                print(f"Erro ao processar o código de barras: {e}")
                cv2.putText(frame, "Erro no processamento", (50, 50),
                            cv2.FONT_HERSHEY_COMPLEX, 1, (0, 0, 255), 2)


    cv2.imshow('scanner' , frame)
    if cv2.waitKey(1) == ord('q'):
        break

# Libera a câmera e fecha a janela
cap.release()
cv2.destroyAllWindows()

# Fecha a conexão com o banco de dados
cursor.close()
conn.close()