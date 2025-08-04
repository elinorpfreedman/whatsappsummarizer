FROM python:3.11-slim

# Install dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    wget unzip curl gnupg2 ca-certificates \
    libgtk-3-0 libnss3 libx11-xcb1 libxcomposite1 libxdamage1 libxrandr2 \
    libasound2 libatk-bridge2.0-0 libatk1.0-0 libcups2 libdbus-1-3 \
    libgdk-pixbuf2.0-0 libnspr4 fonts-liberation libgbm1 libvulkan1 xdg-utils \
    && rm -rf /var/lib/apt/lists/*

# Install Chrome 137 (This part remains the same as the version is correct)
ENV CHROME_VERSION=137.0.7151.119
RUN wget -q https://dl.google.com/linux/chrome/deb/pool/main/g/google-chrome-stable/google-chrome-stable_${CHROME_VERSION}-1_amd64.deb && \
    apt install -y ./google-chrome-stable_${CHROME_VERSION}-1_amd64.deb && \
    rm google-chrome-stable_${CHROME_VERSION}-1_amd64.deb

# Install matching ChromeDriver manually
# You can remove the CHROMEDRIVER_VERSION ENV var, or keep it if you plan to use it for logging,
# but the URL now directly uses the CHROME_VERSION.
# The critical change is the URL in the wget command.
RUN wget -q -O /tmp/chromedriver.zip "https://storage.googleapis.com/chrome-for-testing-public/${CHROME_VERSION}/linux64/chromedriver-linux64.zip" && \
    unzip /tmp/chromedriver.zip -d /usr/local/bin && \
    chmod +x /usr/local/bin/chromedriver && \
    rm /tmp/chromedriver.zip

# Set workdir
WORKDIR /app

# Install Python deps
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app
COPY . .

CMD ["python", "main.py"]