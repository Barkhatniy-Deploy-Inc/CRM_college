FROM python:3.11-slim
WORKDIR /app
COPY _python_legacy/requirements.txt ./
# RUN pip install --no-cache-dir -r requirements.txt # Отключено из-за проблем с интернетом
COPY main .
COPY schema.prisma .
COPY prisma-query-engine .
COPY _python_legacy/ ./_python_legacy/
RUN chmod +x main prisma-query-engine
ENV PRISMA_QUERY_ENGINE_BINARY=/app/prisma-query-engine
CMD ["./main"]
