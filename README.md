# Decodificador de Código Morse

Decodificador de código morse a partir do microfone em python


## Especificações

O Decodificador é criado baseado nas seguintes regras:

- Um sinal ativo é definido a partir de 4000 (-18.2 dBFS) para os valores brutos de amostra.

- Uma unidade de tempo tem 60ms

- '.' é representado por 1 unidade de tempo

- '-' é representado por 3 unidades de tempo

- O intervalo entre sinais da mesma letra deve ser de 1 unidade de tempo

- O intervalo entre letras da mesma palavra deve ser de 3 unidades de tempo

- O intervalo entre palavras deve ser de 7 unidades de tempo


## Executando o Projeto

Clone o repositório:

```bash
git clone <link-do-repositorio>
```

Entre na pasta:

```bash
cd decodificador-morse
```

Crie e entre no ambiente virtual:

```bash
# Windows
python -m venv venv
venv\Scripts\activate.bat

# Linux
python3.14 -m venv venv
source venv/bin/activate
```

Instale as depêndencias necessárias:

```bash
pip install -r requirements.txt
```

Execute o projeto:

```bash
python main.py
```
