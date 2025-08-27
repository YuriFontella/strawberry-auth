# API GraphQL - Auth

## Instalação

### Instalar Poetry

**Linux, macOS, Windows (WSL):**
```bash
curl -sSL https://install.python-poetry.org | python3 -
```

**Windows (PowerShell):**
```powershell
(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | py -
```

### Instalar dependências

Instale os pacotes necessários:

```bash
poetry install
```

### Configurar pre-commit

Configure os hooks do pre-commit:

```bash
pre-commit install --config pre-commit.yaml
```

## Execução

Execute o projeto:

```bash
python main.py
```

## Acesso

Abra no navegador:

```
http://localhost:8000/graphql
```

## Queries e Mutations

### Criar usuário

```graphql
mutation create_user ($UserInput: UserInput!) {
  create_user (data: $UserInput)
}
```

**Variáveis:**
```json
{
  "UserInput": {
    "name": "",
    "email": "",
    "password": ""
  }
}
```

### Login

```graphql
mutation auth_login {
  auth_login (email: "", password: "")
}
```

### Usuário atual

```graphql
query current_user {
  current_user {
    name
    email
    status
    role
    uuid
    fingerprint
    avatar
    date
  }
}
```

### Logout

```graphql
mutation logout {
  logout
}
```
