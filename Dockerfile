# Utilizar a imagem oficial do Python como base
FROM python:3.11-bookworm

RUN apt-get update && apt-get install ffmpeg libsm6 libxext6 -y

# Definir o diretório de trabalho do container
WORKDIR /usr/src/app

# Copiar o arquivo requirements.txt para o diretório de trabalho
COPY ./requirements.txt .

# Instalar as dependências do projeto
RUN pip install -r requirements.txt

# Copiar o código do projeto para o diretório de trabalho
COPY . .

# Expor a porta 8000 para o container
EXPOSE 8000

# Definir o comando para executar o projeto
CMD ["python", "main.py"]