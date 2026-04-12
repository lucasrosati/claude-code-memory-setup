
# MedSched

MedSched é uma aplicação para gerenciamento de consultas médicas, permitindo realizar operações CRUD (Criar, Ler, Atualizar, Excluir) em um banco de dados MySQL. A aplicação utiliza `Docker` e `Docker Compose` para gerenciar os serviços e a infraestrutura do banco de dados e da aplicação.

## Funcionalidades

- **Inserir consulta**: Adicionar uma nova consulta para um paciente e um médico específicos.
- **Atualizar consulta**: Modificar informações de uma consulta existente.
- **Consultar dados de consultas**: Listar consultas com informações detalhadas do paciente e do médico.
- **Excluir consulta**: Remover uma consulta existente do banco de dados.

## Estrutura do Banco de Dados

O banco de dados consiste em três tabelas principais:

- **Paciente**: Dados do paciente, como nome, CPF, data de nascimento, endereço e telefone.
- **Medico**: Informações do médico, incluindo nome, CPF, especialidade e telefone.
- **Consulta**: Registros de consultas, com referência ao paciente e ao médico, data e motivo.

## Pré-requisitos

- **Docker**: Certifique-se de ter o Docker instalado no seu sistema.
- **Docker Compose**: Também é necessário o Docker Compose para gerenciar os containers.

## Configuração e Execução

### Passo 1: Clonar o Repositório

Clone o repositório do projeto:

```bash
git clone https://github.com/seu-usuario/MedSched.git
cd MedSched
```

### Passo 2: Configurar e Executar o Projeto com Docker Compose

#### Subir o Banco de Dados e a Aplicação

Utilize o Docker Compose para construir e executar os containers:

```bash
docker compose up --build
```

#### Comando Especial para Interação com o Menu

Para acessar o menu interativo da aplicação diretamente e realizar operações CRUD, utilize o comando abaixo. Esse comando executa a aplicação em modo interativo:

```bash
docker compose run -it app
```

Esse comando foi essencial para permitir o funcionamento do menu interativo no ambiente Docker, possibilitando a entrada de dados pelo terminal.

### Passo 3: Comandos Adicionais do Docker Compose

- **Parar e remover os containers**:
  ```bash
  docker compose down
  ```

- **Acessar o banco de dados diretamente** (caso precise verificar dados ou realizar consultas diretas):
  ```bash
  docker exec -it medsched_db mysql -uroot -prootpassword medsched_db
  ```

### Estrutura do Projeto

- **app/**: Contém o código da aplicação em Python e o Dockerfile da aplicação.
- **db/**: Inclui o script de inicialização do banco de dados e o Dockerfile do banco de dados.
- **docker-compose.yml**: Define os serviços de aplicação e banco de dados.

## Exemplo de Uso

1. Ao executar `docker compose run -it app`, um menu interativo será exibido com as seguintes opções:
   ```
   1. Inserir consulta
   2. Atualizar consulta
   3. Consultar dados de consultas (com junção)
   4. Excluir consulta
   5. Sair
   ```

2. Escolha a opção desejada digitando o número correspondente e siga as instruções para inserir ou visualizar dados.

## Notas Importantes

- **Charset**: Para simplificar a manipulação de acentos e caracteres especiais, os acentos foram removidos dos dados de texto. Se você desejar trabalhar com caracteres acentuados, verifique a configuração de charset no banco de dados e na aplicação.
- **Docker Compose Run**: O comando `docker compose run -it app` foi a solução para permitir a interação com o menu no ambiente Docker.

## Contribuição

Para contribuir com o projeto, faça um fork, crie uma branch com suas alterações e abra um Pull Request.

## Licença

Este projeto é distribuído sob a licença MIT.
