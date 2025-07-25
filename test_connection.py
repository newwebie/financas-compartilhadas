import streamlit as st
from pymongo import MongoClient
import certifi

def test_mongodb_connection():
    st.title("🔧 Teste de Conexão MongoDB")
    
    # Lendo os secrets
    try:
        URI = st.secrets["uri"]
        st.success("✅ URI carregada com sucesso")
        st.code(URI, language="text")
    except Exception as e:
        st.error(f"❌ Erro ao carregar URI: {e}")
        return
    
    # Testando conexão
    try:
        st.info("🔄 Tentando conectar ao MongoDB...")
        
        client = MongoClient(
            URI,
            tls=True,
            tlsCAFile=certifi.where(),
            serverSelectionTimeoutMS=30000,
            connectTimeoutMS=30000,
            socketTimeoutMS=30000
        )
        
        # Testa a conexão
        client.admin.command('ping')
        st.success("✅ Conexão estabelecida com sucesso!")
        
        # Lista os bancos disponíveis
        databases = client.list_database_names()
        st.info(f"📊 Bancos disponíveis: {databases}")
        
        # Se o banco 'financas' existe, lista as coleções
        if 'financas' in databases:
            db = client['financas']
            collections = db.list_collection_names()
            st.info(f"📁 Coleções no banco 'financas': {collections}")
            
            # Se a coleção 'despesas' existe, conta os documentos
            if 'despesas' in collections:
                count = db['despesas'].count_documents({})
                st.success(f"📄 Total de documentos na coleção 'despesas': {count}")
        
        client.close()
        
    except Exception as e:
        st.error(f"❌ Erro de conexão: {e}")
        st.error("Verifique se:")
        st.error("1. A URI está correta")
        st.error("2. O cluster MongoDB Atlas está ativo")
        st.error("3. O usuário e senha estão corretos")
        st.error("4. O IP está liberado no MongoDB Atlas")

if __name__ == "__main__":
    test_mongodb_connection() 