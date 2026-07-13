# Sistema de Arbitragem de Apostas Esportivas (SureBet)

Este projeto foi totalmente implementado, testado e está pronto para ser executado. Abaixo estão as instruções detalhadas para você abrir o projeto no **Visual Studio Code**, instalar as dependências, rodar os testes e iniciar o servidor web interativo.

---

## 🚀 Como Executar o Projeto no Visual Studio Code

### 1. Requisitos Prévios
Certifique-se de ter instalado em sua máquina:
- **Python 3.10 ou superior**
- **Git** (opcional, para clonar ou gerenciar o código)
- **Visual Studio Code**

### 2. Abrindo o Projeto no VS Code
1. Abra o VS Code.
2. Vá em **File** -> **Open Folder...** (ou **Arquivo** -> **Abrir Pasta...**).
3. Selecione a pasta raiz deste repositório (`surebet-project`).

Você verá a seguinte estrutura de arquivos no painel esquerdo:
```text
surebet-project/
├── app/
│   ├── api/
│   ├── scraper/
│   │   ├── bookmakers/
│   │   │   ├── bet365.py
│   │   │   ├── betano.py
│   │   │   ├── betfair.py
│   │   │   ├── one_xbet.py
│   │   │   ├── pinnacle.py
│   │   │   └── sportingbet.py
│   │   ├── base.py
│   │   └── engine.py
│   ├── services/
│   │   ├── analyzer.py
│   │   ├── normalization.py
│   │   ├── notifier.py
│   │   └── orchestrator.py
│   ├── static/
│   ├── templates/
│   │   └── dashboard.html
│   ├── auth.py
│   ├── config.py
│   ├── database.py
│   ├── main.py
│   └── models.py
├── tests/
│   ├── test_analyzer.py
│   ├── test_auth.py
│   ├── test_normalization.py
│   └── test_scraper.py
├── .gitignore
├── INSTRUCOES.md
├── README.md
└── requirements.txt
```

---

### 3. Criando o Ambiente Virtual e Instalando as Dependências
Abra o terminal integrado do VS Code (**Ctrl + `** ou **Terminal -> Novo Terminal**) e execute os seguintes comandos:

**No Windows:**
```bash
# Criar ambiente virtual
python -m venv venv

# Ativar ambiente virtual
venv\Scripts\activate

# Instalar dependências
pip install -r requirements.txt
```

**No Linux/macOS:**
```bash
# Criar ambiente virtual
python3 -m venv venv

# Ativar ambiente virtual
source venv/bin/activate

# Instalar dependências
pip install -r requirements.txt
```

---

### 4. 🧪 Executando os Testes Automatizados
O projeto conta com **17 testes de unidade** cobrindo todas as fórmulas matemáticas de arbitragem (ROI, distribuição de stakes), normalização de nomes de equipes por similaridade, criptografia/auth (JWT/bcrypt nativo) e os scrapers do BeautifulSoup.

Para rodar os testes, execute o seguinte comando no terminal:
```bash
python -m pytest -v
```

---

### 5. 💻 Executando o Servidor Web e Dashboard Interativo
Para rodar a aplicação em tempo real e visualizar o lindo dashboard interativo com atualizações de SureBets via WebSockets e a Calculadora integrada de Stakes:

1. No terminal do VS Code, inicie o servidor com o **Uvicorn**:
   ```bash
   uvicorn app.main:app --reload
   ```

2. Abra o seu navegador web de preferência e acesse:
   **[http://localhost:8000](http://localhost:8000)**

---

## 🎨 Funcionalidades do Dashboard que Você Pode Testar:
1. **Feed de Surebets em Tempo Real:** No centro da página, você verá eventos ativos (ex: *Real Madrid vs Barcelona*, *Carlos Alcaraz vs Jannik Sinner*) com o ROI calculado de forma precisa.
2. **Dimensionador de Stakes Interativo:** Altere o valor do "Custom Investment ($)" em qualquer card de arbitragem e veja os stakes sugeridos para cada casa de aposta atualizarem instantaneamente!
3. **Calculadora de Arbitragem Autônoma (Sidebar):** Insira qualquer cotação de duas odds personalizadas e um montante de investimento para verificar na hora se há arbitragem, qual o ROI e a divisão exata do seu dinheiro.
4. **Alertas em Tempo Real:** Novos sinais que chegam por segundo do backend são transmitidos de forma assíncrona para a interface usando **WebSockets** e aparecem piscando na tela sem precisar recarregar a página!
