# API GraphQL - Auth

## Instalação

Instale os pacotes necessários:

```bash
pip install -r requirements.txt
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
