# 📊 Painel Financeiro Compartilhado

## 🔧 Configuração da Conexão MongoDB

### Problemas Comuns e Soluções

#### 1. Erro de SSL Handshake
Se você está recebendo o erro `SSL handshake failed`, tente:

1. **Verificar a URI**: Certifique-se de que a URI no arquivo `.streamlit/secrets.toml` está completa:
   ```toml
   uri = "mongodb+srv://usuario:senha@cluster.net/banco?retryWrites=true&w=majority"
   ```

2. **Verificar o MongoDB Atlas**:
   - Acesse o MongoDB Atlas
   - Verifique se o cluster está ativo
   - Confirme se o usuário e senha estão corretos

3. **Configurar IP Whitelist**:
   - No MongoDB Atlas, vá em "Network Access"
   - Adicione seu IP atual ou `0.0.0.0/0` para permitir acesso de qualquer lugar

#### 2. Testando a Conexão

Execute o script de teste para verificar se a conexão está funcionando:

```bash
streamlit run test_connection.py
```

#### 3. Executando a Aplicação Principal

```bash
streamlit run package.py
```

### Estrutura do Projeto

```
financas compartilhadas/
├── package.py              # Aplicação principal
├── test_connection.py      # Script de teste de conexão
├── requirements.txt        # Dependências Python
├── .streamlit/
│   └── secrets.toml       # Configurações secretas (URI MongoDB)
└── README.md              # Este arquivo
```

### Dependências

Certifique-se de ter todas as dependências instaladas:

```bash
pip install -r requirements.txt
```

### Configuração do MongoDB Atlas

1. Crie um cluster no MongoDB Atlas
2. Crie um usuário com permissões de leitura/escrita
3. Configure a Network Access para permitir seu IP
4. Obtenha a URI de conexão
5. Adicione a URI no arquivo `.streamlit/secrets.toml`

### Estrutura do Banco de Dados

- **Banco**: `financas`
- **Coleção**: `despesas`

Cada documento na coleção `despesas` deve ter a seguinte estrutura:
```json
{
  "label": "Categoria",
  "buyer": "Susanna|Pietrah",
  "item": "Nome do item",
  "description": "Descrição",
  "quantity": 1,
  "total_value": 100.00,
  "payment_method": "VR|Débito|Crédito",
  "attachment": "link",
  "installment": 0,
  "createdAt": "2024-01-01T00:00:00Z",
  "pagamento_compartilhado": "Compra individual|Nossa|Cada uma pagou metade",
  "tem_pendencia": false,
  "devedor": null,
  "valor_pendente": null,
  "status_pendencia": null
}
``` 