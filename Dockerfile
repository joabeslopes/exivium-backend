# Utilizar a imagem oficial do Python como base
FROM python:3.9-slim

# Definir o diretório de trabalho do container
WORKDIR /exivium

# Copiar o arquivo requirements.txt para o diretório de trabalho
COPY ./requirements.txt .

# Instalar as dependências do projeto
RUN pip install -r requirements.txt

# Copiar o código do projeto para o diretório de trabalho
COPY . .

# Expor a porta 5000 para o container
EXPOSE 5000

# Definir o comando para executar o projeto
CMD ["python", "app.py"]