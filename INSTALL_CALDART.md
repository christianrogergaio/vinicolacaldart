# Manual de Instalação - Vinícola Caldart

Este guia descreve como instalar e rodar o Sistema de Monitoramento de Doenças no computador da propriedade.

## 1. Pré-requisitos

No computador da Caldart, você precisará instalar:

1.  **Python 3.10+**: Baixe em [python.org](https://www.python.org/downloads/).
    *   **IMPORTANTE**: Na instalação, marque a opção **"Add Python to PATH"**.
2.  **Git**: Baixe em [git-scm.com](https://git-scm.com/downloads).
3.  **Drivers do Arduino**: Se o computador não reconhecer o Arduino, pode ser necessário instalar o driver CH340 ou CP210x (dependendo do modelo da placa).

## 2. Clonar o Repositório

Abra o terminal (PowerShell ou CMD) na pasta onde deseja instalar e rode:

```bash
git clone <URL_DO_NOVO_REPOSITORIO> sistema_monitoramento
cd sistema_monitoramento
```

*(Substitua `<URL_DO_NOVO_REPOSITORIO>` pelo link que criamos)*

## 3. Instalar Dependências

Dentro da pasta do projeto, execute os comandos abaixo para criar um ambiente isolado e instalar as bibliotecas:

```bash
# 1. Criar ambiente virtual
python -m venv venv

# 2. Ativar ambiente virtual
.\venv\Scripts\activate

# 3. Instalar bibliotecas
pip install -r requirements.txt
```

## 4. Configurar Arduino

1.  Conecte o Arduino na USB.
2.  Descubra qual porta COM foi atribuída.
    *   Você pode rodar o script auxiliar: `python list_ports.py`
    *   Ou verificar no **Gerenciador de Dispositivos** do Windows.
3.  Abra o arquivo `core/config.py` (usando Bloco de Notas ou VS Code).
4.  Edite a linha:
    ```python
    PORTA_SERIAL = 'COM4'  # <--- Mude para a porta correta (ex: COM3, COM5)
    ```

## 5. Rodar o Sistema

Basta dar dois cliques no arquivo:
**`run_system.bat`**

Isso abrirá duas janelas pretas (API e Ingestor). Não as feche enquanto quiser que o sistema funcione.
Acesse o painel em: **http://localhost:8000**
