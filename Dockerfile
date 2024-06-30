FROM python:3.12.4

# Define o diretório de trabalho dentro do contêiner
WORKDIR /app

# Copia o arquivo requirements.txt para o contêiner
COPY requirements.txt .

# Atualiza o pip e instala as dependências
RUN python -m venv /opt/venv \
    && . /opt/venv/bin/activate \
    && pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copia o restante da aplicação para o contêiner
COPY . .

# Define o PATH para incluir o ambiente virtual
ENV PATH="/opt/venv/bin:$PATH"

# Define o comando de inicialização padrão para o contêiner
CMD exec gunicorn a_core.wsgi:application --bind 0.0.0.0:${PORT}
