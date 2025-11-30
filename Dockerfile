FROM rockylinux:9

# Update and install system dependencies
# Rocky Linux 9 comes with Python 3.9 as 'python3'
RUN dnf -y update && \
    dnf -y install \
    python3 \
    python3-pip \
    python3-devel \
    gcc \
    make \
    zsh \
    git \
    shadow-utils \
    wget \
    util-linux-user \
    && dnf clean all

# Create user cjh with zsh shell
RUN useradd -m -s /bin/zsh cjh

# Change root shell to zsh
RUN usermod -s /bin/zsh root

# Install Oh My Zsh for root
RUN sh -c "$(wget https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh -O -)" "" --unattended && \
    sed -i 's/ZSH_THEME="robbyrussell"/ZSH_THEME="af-magic"/' /root/.zshrc

# Install Oh My Zsh for cjh
USER cjh
RUN sh -c "$(wget https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh -O -)" "" --unattended && \
    sed -i 's/ZSH_THEME="robbyrussell"/ZSH_THEME="af-magic"/' /home/cjh/.zshrc
USER root

WORKDIR /app

# Copy requirements
COPY requirements.txt .
COPY requirements-core.txt .
COPY requirements-ml.txt .
COPY requirements-minimal.txt .

# Install Python dependencies
RUN pip3 install --no-cache-dir --upgrade pip && \
    pip3 install --no-cache-dir -r requirements.txt && \
    pip3 install --no-cache-dir -r requirements-ml.txt

# Copy source code
COPY . .

# Set ownership for cjh
RUN chown -R cjh:cjh /app

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Keep container alive for manual interaction
CMD ["tail", "-f", "/dev/null"]
