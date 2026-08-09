FROM debian:trixie-backports

RUN apt-get update && apt-get install -y python3 pip curl

WORKDIR /app

COPY requirements.txt /app

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

RUN curl -sSL https://ngrok-agent.s3.amazonaws.com/ngrok.asc \
  | tee /etc/apt/trusted.gpg.d/ngrok.asc >/dev/null \
  && echo "deb https://ngrok-agent.s3.amazonaws.com bookworm main" \
  | tee /etc/apt/sources.list.d/ngrok.list \
  && apt update \
  && apt-get install ngrok

RUN ngrok config add-authtoken 3GupODREtLu8j8bCZU3juOa86qj_4WhBnQw3rrrWiToBGQbLa

RUN chmod +x start.sh

CMD [ "./start.sh"]