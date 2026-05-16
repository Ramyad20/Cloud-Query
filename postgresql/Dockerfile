# 
# Sistema de Gestão de Dados 2024/2025
# Trabalho Prático
#
# Authors: 
#   SGD 2024 Team
#   University of Coimbra

FROM library/postgres


ENV POSTGRES_USER SGD_project
ENV POSTGRES_PASSWORD 5432
ENV POSTGRES_DB cloud_query

COPY Tabelas&Inserção.sql /docker-entrypoint-initdb.d/

EXPOSE 5432
