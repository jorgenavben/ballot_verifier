# Builder stage
FROM python:3.10 AS builder

WORKDIR /src

RUN curl https://sh.rustup.rs -sSf | sh -s -- -y
ENV PATH="/root/.cargo/bin:${PATH}"

COPY ./ /src
RUN pip3 install -r requirements.txt

# Runtime stage
FROM python:3.10-slim AS base

WORKDIR /src

RUN apt update -qq && \
    apt install -y libsodium23

COPY --from=builder /usr/local /usr/local

COPY ./ /src

ENV CONFIG_DIR /usr/local/var/keri
WORKDIR $CONFIG_DIR
RUN ln -s /src/scripts/start_verifier.sh /usr/local/bin/ballot-verifier

RUN chmod +x /usr/local/bin/ballot-verifier

FROM base AS ballot-verifier
ENTRYPOINT ["/usr/local/bin/ballot-verifier"]