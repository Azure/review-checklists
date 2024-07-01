FROM alpine:latest
RUN apk update \
 && apk add --no-cache jq \
 && rm -rf /var/cache/apk/*
COPY entrypoint.sh /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]
