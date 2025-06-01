from llama_cpp import Llama

# my_model_path = r"C:\Users\Bazzz\AppData\Local\llama_index\models\llama-2-13b-chat.Q4_0.gguf"
my_model_path = r"C:\Users\Bazzz\AppData\Local\llama_index\models\llama-2-7b-chat.Q4_K_M.gguf"

llm = Llama(
    model_path=my_model_path,
    chat_format="llama-2",
    n_gpu_layers=5, # Uncomment to use GPU acceleration
    # use_mlock=True
    # seed=1337, # Uncomment to set a specific seed
    n_ctx=3078, # Uncomment to increase the context window
)


classificator_system_prompt = """
Yours function: you have to cluster the logs and write a description for each cluster of logs, you perform clustering according to the parameters from the normalized event, you should choose the parameters that most widely separate one group of logs from another (for example, such fields are often the "action" or "object" fields), between the selected fields by which you cluster events, there can be operators - “and” or “or”.

Input: The user sends you a set of logs, each log is presented in two forms - a raw form and a normalized form.

Output format:
"<yours criteria>": "<description of logs that fall under the compiled criteria, some of fields from normalized form of log can be in description, in brackets {}>" 
"""
user_example_logs = """
Yours function: you have to cluster the logs and write a description for each cluster of logs, 
    you perform clustering according to the parameters from the normalized event, 
    you should choose the parameters that most widely separate one group of logs from another 
    (for example, such fields are often the "action" or "object" fields), 
    between the selected fields by which you cluster events, there can be operators - “and” or “or”.

Input:
[{
    "raw form": "<134>1 2024-01-12T08:30:29Z ILOCZ3333H1MM #ILO4 - - - Added group tmp_group by: user_name.",
    "normalized form": "{   "subject": "account",   "action": "create",   "object": "user_group",   "status": "success",   "category.generic": "Group",   "category.high": "Users And Rights Management",   "category.low": "Manipulation",   "event_src.category": "Server management",   "event_src.title": "ilo",   "event_src.vendor": "hewlett_packard_enterprise",   "id": "PT_Hewlett_Packard_Enterprise_iLO_syslog_user_group_added_deleted",   "importance": "info",   "object.group": "tmp_group",   "subject.account.name": "user_name",   "time": "2017-03-15T05:29:00.000Z" },"
},
{
    "raw form": "<134>1 2024-01-12T08:32:34Z ILOCZ3333H1MM #ILO4 - - - Deleted group tmp_group by: user_name.",
    "normalized form": "{   "subject": "account",   "action": "remove",   "object": "user_group",   "status": "success",   "category.generic": "Group",   "category.high": "Users And Rights Management",   "category.low": "Manipulation",   "event_src.category": "Server management",   "event_src.title": "ilo",   "event_src.vendor": "hewlett_packard_enterprise",   "id": "PT_Hewlett_Packard_Enterprise_iLO_syslog_user_group_added_deleted",   "importance": "info",   "object.group": "tmp_group",   "subject.account.name": "user_name",   "time": "2017-03-14T11:26:00.000Z" },"
}]

Output format:
"<yours criteria>": "<description of logs that fall under the compiled criteria, some of fields from prompt can be in description, in brackets {}>" 
"""
as_if_ai_answer = """
"action = "create"": "User {subject.account.name} added group {object.group} on host {event_src.host}"
"action = "remove"": "User {subject.account.name} deleted group {object.group} on host {event_src.host}"
"""


user_example_logs_2 = """
Yours function: you have to cluster the logs and write a description for each cluster of logs, 
    you perform clustering according to the parameters from the normalized event, 
    you should choose the parameters that most widely separate one group of logs from another 
    (for example, such fields are often the "action" or "object" fields), 
    between the selected fields by which you cluster events, there can be operators - “and” or “or”.

Input:
[{
    "raw form": "<134> #ILO 4: 03/15/2017 05:51 XML login: epetrov8 - 247.153.128.199(DNS name not found).",
    "normalized form": "{   "subject": "account",   "action": "open",   "object": "session",   "status": "success",   "event_src.category": "Server management",   "event_src.title": "ilo",   "event_src.vendor": "hewlett_packard_enterprise",   "id": "PT_Hewlett_Packard_Enterprise_iLO_syslog_rpc_session_start_stop",   "importance": "info",   "logon_auth_method": "remote",   "logon_service": "XML API",   "src.ip": "247.153.128.199",   "subject.account.name": "epetrov8",   "subject.name": "epetrov8",   "time": "2017-03-15T05:51:00.000Z" }"
},
{
    "raw form": "<134> #ILO 4: 03/15/2017 05:51 XML logout: EPetrov8 - 247.153.128.199(DNS name not found).",
    "normalized form": "{   "subject": "account",   "action": "close",   "object": "session",   "status": "success",   "event_src.category": "Server management",   "event_src.title": "ilo",   "event_src.vendor": "hewlett_packard_enterprise",   "id": "PT_Hewlett_Packard_Enterprise_iLO_syslog_rpc_session_start_stop",   "importance": "info",   "logon_auth_method": "remote",   "logon_service": "XML API",   "src.ip": "247.153.128.199",   "subject.account.name": "epetrov8",   "subject.name": "epetrov8",   "time": "2017-03-15T05:51:00.000Z" }"
}]

Output format:
"<yours criteria>": "<description of logs that fall under the compiled criteria>" 
"""
as_if_ai_answer_2 = """
"action = "open"": "User {subject.account.name} from host {src.host} opened an RPC session on host {event_src.host}"
"action = "close"": "User {subject.account.name} from host {src.host} ended an RPC session on host {event_src.host}"
"""

real_logs_to_clustering = """
Yours function: you have to cluster the logs and write a description for each cluster of logs, 
    you perform clustering according to the parameters from the normalized event, 
    you should choose the parameters that most widely separate one group of logs from another 
    (for example, such fields are often the "action" or "object" fields), 
    between the selected fields by which you cluster events, there can be operators - “and” or “or”.

Input:
[{
    "raw form": "<134>1 2024-01-12T08:16:56Z ILOCZ3333H1MM #ILO4 - - - User Pabalobabam Peter added by EPetrov.",
    "normalized form": "{   "subject": "account",   "action": "create",   "object": "account",   "status": "success",   "category.generic": "Account",   "category.high": "Users And Rights Management",   "category.low": "Manipulation",   "event_src.category": "Server management",   "event_src.hostname": "ilocz3333h1mm",   "event_src.title": "ilo",   "event_src.vendor": "hewlett_packard_enterprise",   "id": "PT_Hewlett_Packard_Enterprise_iLO_syslog_user_added_deleted",   "importance": "info",   "object.account.name": "pabalobabam peter",   "object.name": "pabalobabam peter",   "subject.account.name": "epetrov",   "subject.name": "epetrov",   "time": "2024-01-12T08:16:56.000Z" },"
},
{
    "raw form": "<134>1 2024-01-12T08:16:56Z ILOCZ3333H1MM #ILO4 - - - User Pabalobabam Peter deleted by EPetrov.",
    "normalized form": "{   "subject": "account",   "action": "remove",   "object": "account",   "status": "success",   "category.generic": "Account",   "category.high": "Users And Rights Management",   "category.low": "Manipulation",   "event_src.category": "Server management",   "event_src.title": "ilo",   "event_src.vendor": "hewlett_packard_enterprise",   "id": "PT_Hewlett_Packard_Enterprise_iLO_syslog_user_added_deleted",   "importance": "info",   "object.account.name": "pabalobabam peter",   "object.name": "pabalobabam peter",   "subject.account.name": "epetrov",   "subject.name": "epetrov",   "time": "2017-03-15T05:29:00.000Z" }"
}]

Output format:
"<yours criteria>": "<description of logs that fall under the compiled criteria, some of fields from prompt can be in description, in brackets {}>" 
"""

response = llm.create_chat_completion(
      messages=[
          {"role": "system", "content": classificator_system_prompt},

          {"role": "user", "content": user_example_logs},
          {"role": "system", "content": as_if_ai_answer},

          {"role": "user", "content": user_example_logs_2},
          {"role": "system", "content": as_if_ai_answer_2},

          {"role": "user", "content": real_logs_to_clustering},
      ],
      temperature=0.2,
      top_p=0.2,
      max_tokens=512,
)

print(response)
print(response["choices"][0]["message"]["content"])
