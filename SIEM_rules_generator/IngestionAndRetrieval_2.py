from llama_index.vector_stores.postgres import PGVectorStore    # postgres
import psycopg2                                                 # postgres
import sys                                                      # postgres

from llama_index.readers.file import PyMuPDFReader          # Load Data
from llama_index.core.node_parser import SentenceSplitter   # Split Data
from llama_index.core.schema import TextNode                # For chunks to nodes

from llama_index.embeddings.huggingface import HuggingFaceEmbedding

from llama_index.core import QueryBundle                # RetrievalPipeline
from llama_index.core.retrievers import BaseRetriever   # RetrievalPipeline
from typing import Any, List                            # RetrievalPipeline

from llama_index.core.schema import NodeWithScore       # RetrievalPipeline
from typing import Optional                             # ?

from llama_index.core.query_engine import RetrieverQueryEngine  # RetrievalPipeline

# construct vector store query
from llama_index.core.vector_stores import VectorStoreQuery

from llama_index.llms.llama_cpp import LlamaCPP         # LlamaCPP


class EmbeddingsDB:
    def __init__(self, db_data):
        self.db_main_data = db_data
        self.db_conn = None
        self.vector_store = None

        # Создание подключения к БД
        try:
            self.db_conn = psycopg2.connect(
                dbname=self.db_main_data["name"],
                host="localhost",
                password=self.db_main_data["password"],
                port=self.db_main_data["port"],
                user=self.db_main_data["user"],
            )
            self.db_conn.autocommit = True
        except psycopg2.OperationalError as e:
            print('Unable to connect!\n{0}').format(e)
            sys.exit(1)
        else:
            print('DB connected!')

        # Инициализация векторного хранилища
        self.vector_store = PGVectorStore.from_params(
            database=self.db_main_data["name"],
            host="localhost",
            password=self.db_main_data["password"],
            port=self.db_main_data["port"],
            user=self.db_main_data["user"],
            table_name="llama2_paper",
            embed_dim=384,  # openai embedding dimension
        )

    # TODO: доработать эту функцию, чтобы не было ошибки "cannot drop the currently open database"
    def drop_and_create_db(self):
        with self.db_conn.cursor() as c:
            c.execute(f"DROP DATABASE IF EXISTS {self.db_main_data['name']}")
            c.execute(f"CREATE DATABASE {self.db_main_data['name']}")

    def save_nodes(self, nodes: list):
        self.vector_store.add(nodes)


class DataPreparing:
    def __init__(self, doc_path, embedding_model):
        self.loader = PyMuPDFReader()
        self.documents = self.loader.load(file_path=doc_path)
        self.text_parser = SentenceSplitter(chunk_size=1024) # separator=" ",

        self.text_chunks = []
        # TODO: понять для чего необходим doc_idxs
        # maintain relationship with source doc index, to help inject doc metadata in (3)
        self.doc_idxs = []
        self.nodes = []

        self.embed_model = embedding_model

        print("fill_chunks_and_idxs")
        self.fill_chunks_and_idxs()
        print("nodes_from_chunks")
        self.nodes_from_chunks()
        print("generate_embeddings")
        self.generate_embeddings()

    def fill_chunks_and_idxs(self):
        for doc_idx, doc in enumerate(self.documents):
            cur_text_chunks = self.text_parser.split_text(doc.text)
            self.text_chunks.extend(cur_text_chunks)
            self.doc_idxs.extend([doc_idx] * len(cur_text_chunks))

    def nodes_from_chunks(self):
        for idx, text_chunk in enumerate(self.text_chunks):
            node = TextNode(
                text=text_chunk,
            )
            src_doc = self.documents[self.doc_idxs[idx]]
            node.metadata = src_doc.metadata
            self.nodes.append(node)

    def generate_embeddings(self):
        for node in self.nodes:
            node_embedding = self.embed_model.get_text_embedding(
                node.get_content(metadata_mode="all")
            )
            node.embedding = node_embedding

    def get_nodes(self):
        return self.nodes


class VectorDBRetriever(BaseRetriever):
    """Retriever over a postgres vector store."""

    def __init__(
        self,
        vector_store: PGVectorStore,
        embed_model: Any,
        query_mode: str = "default",
        similarity_top_k: int = 2,
    ) -> None:
        """Init params."""
        self._vector_store = vector_store
        self._embed_model = embed_model
        self._query_mode = query_mode
        self._similarity_top_k = similarity_top_k
        super().__init__()

    def _retrieve(self, query_bundle: QueryBundle) -> List[NodeWithScore]:
        """Retrieve."""
        print(f"query_bundle.query_str: {query_bundle.query_str}")
        query_embedding = self._embed_model.get_query_embedding(
            query_bundle.query_str
        )
        vector_store_query = VectorStoreQuery(
            query_embedding=query_embedding,
            similarity_top_k=self._similarity_top_k,
            mode=self._query_mode,
        )
        query_result = self._vector_store.query(vector_store_query)

        nodes_with_scores = []
        for index, node in enumerate(query_result.nodes):
            score: Optional[float] = None
            if query_result.similarities is not None:
                score = query_result.similarities[index]
            nodes_with_scores.append(NodeWithScore(node=node, score=score))

        print(f"nodes_with_scores: {nodes_with_scores}")

        return nodes_with_scores


class IngestRetrieveGenerate:
    def __init__(self, embedding_model_name, db_access_data, document_path, drop_db=False):
        self.embed_model = HuggingFaceEmbedding(model_name=embedding_model_name)

        self.db_worker = EmbeddingsDB(db_data=db_access_data)
        if drop_db: self.db_worker.drop_and_create_db()

        self.data_worker = DataPreparing(doc_path=document_path, embedding_model=self.embed_model)
        self.db_worker.vector_store.add(self.data_worker.get_nodes())

        self.retriever = VectorDBRetriever(
            vector_store=self.db_worker.vector_store,
            embed_model=self.embed_model,
            query_mode="default",
            similarity_top_k=2
        )

        print("Load model")
        # model_url = "https://huggingface.co/TheBloke/Llama-2-13B-chat-GGUF/resolve/main/llama-2-13b-chat.Q4_0.gguf"

        # my_model_path = r"C:\Users\Bazzz\AppData\Local\llama_index\models\llama-2-13b-chat.Q4_0.gguf"
        # my_model_path = r"C:\Users\Bazzz\AppData\Local\llama_index\models\llama-2-7b-chat.Q4_K_M.gguf"
        my_model_path = r"C:\Users\Bazzz\AppData\Local\llama_index\models\Meta-Llama-3-8B-Instruct-Q4_K_M.gguf"
        # my_model_path = r"C:\Users\Bazzz\AppData\Local\llama_index\models\Meta-Llama-3-8B-Instruct-Q6_K.gguf"

        llm = LlamaCPP(
            # You can pass in the URL to a GGML model to download it automatically
            # model_url=model_url,
            # optionally, you can set the path to a pre-downloaded model instead of model_url
            model_path=my_model_path,
            temperature=0.1,
            max_new_tokens=256,
            # llama2 has a context window of 4096 tokens, but we set it lower to allow for some wiggle room
            context_window=3900,
            # kwargs to pass to __call__()
            generate_kwargs={},
            # kwargs to pass to __init__()
            # set to at least 1 to use GPU
            model_kwargs={"n_gpu_layers": 1},
            verbose=True,
        )

        self.query_engine = RetrieverQueryEngine.from_args(self.retriever, llm=llm)

    def rag_request(self, request_str: str) -> str:
        response = self.query_engine.query(request_str)

        print("\n\n*************************** response ***************************\n")
        print(str(response))

        print("\n\n*************************** response.source_nodes ***************************\n")
        print(response.source_nodes[0].get_content())

        return str(response)


emb_model = "BAAI/bge-small-en"
db_access = {
    "name": "llama_embeddings",
    "host": "localhost",
    "port": 5432,
    "user": "emb_superuser",
    "password": 1234
}

lets_ingest_and_retrieve = IngestRetrieveGenerate(
    embedding_model_name=emb_model,
    db_access_data=db_access,
    document_path="../data/kasper.pdf",
    # drop_db=True
)

# lets_ingest_and_retrieve.rag_request("Расскажи про резервное копирование в MaxPatrol VM")
# lets_ingest_and_retrieve.rag_request("расскажи как восстановить данные хранилища LogSpace в MaxPatrol VM")
lets_ingest_and_retrieve.rag_request("how to set up Kaspersky Anti-Virus for work as mail anti-virus")
