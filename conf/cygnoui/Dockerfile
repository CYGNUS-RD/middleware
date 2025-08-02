# Usar uma imagem base com rsync e ssh instalados
FROM alpine:3.14

# Instalar rsync e ssh
RUN apk add --no-cache rsync openssh

# Criar o diretório de trabalho
WORKDIR /app

# Copiar o script de sincronização para o container
COPY sync.sh /app/sync.sh

# Dar permissão de execução ao script
RUN chmod +x /app/sync.sh

# Comando de entrada
CMD ["/app/sync.sh"]

