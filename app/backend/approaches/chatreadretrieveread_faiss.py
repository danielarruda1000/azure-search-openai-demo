import os
import argparse
import openai
import pickle
from approaches.approach import Approach
from langchain.chat_models import AzureChatOpenAI
from langchain.chains import ConversationalRetrievalChain
from langchain.vectorstores import FAISS
from text import nonewlines
from langchain.prompts import PromptTemplate

from azure.identity import AzureDeveloperCliCredential
from azure.core.credentials import AzureKeyCredential
from azure.storage.blob import BlobServiceClient

os.environ['OPENAI_API_KEY'] = "5406a0f309534a008a96b43cb8511c23"#"c88828585662491f8daf1f3dcc801efc" #"5406a0f309534a008a96b43cb8511c23" # "a7cdb8b183fd46b1987a3903d2c6a97a"
os.environ['OPENAI_API_TYPE'] = 'azure'
os.environ['OPENAI_API_BASE'] = "https://cog-s6q6kio4ticqa.openai.azure.com/" #"https://cog-vjhqc4qd2qhtm.openai.azure.com/"
os.environ['OPENAI_API_VERSION'] = '2023-05-15' #'2022-12-01'

#parser = argparse.ArgumentParser(
#    description="Prepare documents by extracting content from PDFs, splitting content into sections, uploading to blob storage, and indexing in a search index.",
#    epilog="Example: prepdocs.py '..\data\*' --storageaccount myaccount --container mycontainer --searchservice mysearch --index myindex -v"
#    )
#parser.add_argument("--storageaccount", help="Azure Blob Storage account name")
#parser.add_argument("--container", help="Azure Blob Storage container name")
#parser.add_argument("--storagekey", required=False, help="Optional. Use this Azure Blob Storage account key instead of the current user identity to login (use az login to set current user for Azure)")
#args = parser.parse_args()

#azd_credential = AzureDeveloperCliCredential() if args.tenantid == None else AzureDeveloperCliCredential(tenant_id=args.tenantid, process_timeout=60)
#default_creds = azd_credential if args.searchkey == None or args.storagekey == None else None
#search_creds = default_creds if args.searchkey == None else AzureKeyCredential(args.searchkey)
#if not args.skipblobs:
#    storage_creds = default_creds if args.storagekey == None else args.storagekey

class ChatReadRetrieveReadApproachFAISS(Approach):


    def __init__(self, model_name:str, blob_service):

        self.model_name = model_name
        #self.storage_creds= "ZubfTblPdBhT2d8KDlIwg7wkh89OmVez6mYqkftGAatjwR22T/PJ/6JxwEpeS9Oun1xrsOUQ3DFD+AStQ4GkOA=="#'AD/7QMX7M13AQvo+oZXxStQOEiMO+DMMj5YEeYf3udD9mx6Xhdl4mgj/1TQyAeDaDg4fk2nLMmKl+AStQCjAlQ==' #"0qzGY3k4BcuV08WzYJ83FnTJesmHiw+JiqeItkQ8T8vo2PYiTQyBs0H+ceXIQLJPHkSBMEh2xq8o+ASt0SPnvA=="
        self.blob_service = blob_service
        self.chain = None
        self.CONDENSE_QUESTION_PROMPT = PromptTemplate.from_template("""Given the following conversation and a follow up question, rephrase the follow up question to be a standalone question.
        
    Chat History:
    {chat_history}
    Follow Up Input: {question}
    Standalone question:""")

    def load_faiss(self): #sts6q6kio4ticqa
        #blob_service = BlobServiceClient(account_url=f"https://{args.storageaccount}.blob.core.windows.net", credential=self.storage_creds)
        blob_client = self.blob_service.get_blob_client(container='content', blob='knowledge_bases/RI.pkl')

        downloader = blob_client.download_blob(0)
        b = downloader.readall()
        knowledge_base = pickle.loads(b)
        model = AzureChatOpenAI(temperature=0,
                                deployment_name='chat',
                                model_name=self.model_name)
        
        chain = ConversationalRetrievalChain.from_llm(llm=model,
                                                      #chain_type="stuff",
                                                      #condense_question_prompt=self.CONDENSE_QUESTION_PROMPT,
                                                      retriever=knowledge_base.as_retriever())#search_type="similarity",
                                                                                           #search_kwargs={"k":2}))
        self.chain = chain

    def run(self, history: list[tuple], query):
        self.load_faiss()
        question = history[-1]["user"]
        chat_history = self.get_chat_history_as_text(history)
        result = self.chain({'question':question, 'chat_history': chat_history})

        return {"data_points": [''], "answer": result['answer'], "thoughts": ''}
        #return {"data_points": [''], "answer": 'OK', "thoughts": ''}
    
    def get_chat_history_as_text(self, history, include_last_turn=True, approx_max_tokens=1000) -> str:
        history_text = ""
        for h in reversed(history if include_last_turn else history[:-1]):
            history_text = """<|im_start|>user""" +"\n" + h["user"] + "\n" + """<|im_end|>""" + "\n" + """<|im_start|>assistant""" + "\n" + (h.get("bot") + """<|im_end|>""" if h.get("bot") else "") + "\n" + history_text
            if len(history_text) > approx_max_tokens*4:
                break    
    
        history_text = [(k, v) for k, v in history[0].items()]
        return history_text