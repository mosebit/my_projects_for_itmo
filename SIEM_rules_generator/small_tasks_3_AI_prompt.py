from llama_cpp import Llama

my_model_path = r"C:\Users\Bazzz\AppData\Local\llama_index\models\llama-2-13b-chat.Q4_0.gguf"
# my_model_path = r"C:\Users\Bazzz\AppData\Local\llama_index\models\llama-2-7b-chat.Q4_K_M.gguf"

llm = Llama(
    model_path=my_model_path,
    chat_format="llama-2",
    n_gpu_layers=5, # Uncomment to use GPU acceleration
    # use_mlock=True
    # seed=1337, # Uncomment to set a specific seed
    n_ctx=3078, # Uncomment to increase the context window
)


classificator_system_prompt = """
Your task: Analyze the provided logs and cluster them based on the field(s) that most effectively separate the logs into distinct groups. For each cluster, provide a description using the specified output format, which should include relevant details from the normalized log data.

The output format is:
"<clustering field(s)>": "Description template using relevant fields like {field1}, {field2}, etc."

You should choose the clustering field(s) that result in the most meaningful separation of the log data. The description template should be a concise summary that captures the key details of the logs in that cluster.

Input:
[{
    "raw form": "<134>1 2024-01-12T08:30:29Z ILOCZ3333H1MM #ILO4 - - - Added group tmp_group by: user_name.", 
    "normalized form": "{...}"
},
{
    "raw form": "<134>1 2024-01-12T08:32:34Z ILOCZ3333H1MM #ILO4 - - - Deleted group tmp_group by: user_name.",
    "normalized form": "{...}"  
}]

Example output:
"action = "create" and object = "user_group"": "User {subject.account.name} created group {object.group} on host {event_src.hostname}"
"action = "remove" and object = "user_group"": "User {subject.account.name} deleted group {object.group} on host {event_src.hostname}"
"""

user_example_logs = """
Your task: Analyze the provided logs and cluster them based on the field(s) that most effectively separate the logs into distinct groups. For each cluster, provide a description using the specified output format, which should include relevant details from the normalized log data.

The output format is:
"<clustering field(s)>": "Description template using relevant fields like {field1}, {field2}, etc."

You should choose the clustering field(s) that result in the most meaningful separation of the log data. The description template should be a concise summary that captures the key details of the logs in that cluster.

[{
    "raw form": "<134>1 2024-01-12T08:30:29Z ILOCZ3333H1MM #ILO4 - - - Added group tmp_group by: user_name.",
    "normalized form": "{   "subject": "account",   "action": "create",   "object": "user_group",   "status": "success",   "category.generic": "Group",   "category.high": "Users And Rights Management",   "category.low": "Manipulation",   "event_src.category": "Server management",   "event_src.title": "ilo",   "event_src.vendor": "hewlett_packard_enterprise",   "id": "PT_Hewlett_Packard_Enterprise_iLO_syslog_user_group_added_deleted",   "importance": "info",   "object.group": "tmp_group",   "subject.account.name": "user_name",   "time": "2017-03-15T05:29:00.000Z" },"
},
{
    "raw form": "<134>1 2024-01-12T08:32:34Z ILOCZ3333H1MM #ILO4 - - - Deleted group tmp_group by: user_name.",
    "normalized form": "{   "subject": "account",   "action": "remove",   "object": "user_group",   "status": "success",   "category.generic": "Group",   "category.high": "Users And Rights Management",   "category.low": "Manipulation",   "event_src.category": "Server management",   "event_src.title": "ilo",   "event_src.vendor": "hewlett_packard_enterprise",   "id": "PT_Hewlett_Packard_Enterprise_iLO_syslog_user_group_added_deleted",   "importance": "info",   "object.group": "tmp_group",   "subject.account.name": "user_name",   "time": "2017-03-14T11:26:00.000Z" },"
}]
"""

as_if_ai_answer = """
"action = "create"": "User {subject.account.name} added group {object.group} on host {event_src.host}"
"action = "remove"": "User {subject.account.name} deleted group {object.group} on host {event_src.host}"
"""


user_example_logs_2 = """
Your task: Analyze the provided logs and cluster them based on the field(s) that most effectively separate the logs into distinct groups. For each cluster, provide a description using the specified output format, which should include relevant details from the normalized log data.

The output format is:
"<clustering field(s)>": "Description template using relevant fields like {field1}, {field2}, etc."

You should choose the clustering field(s) that result in the most meaningful separation of the log data. The description template should be a concise summary that captures the key details of the logs in that cluster.

Input:
[{
    "raw form": "<134> #ILO 4: 03/15/2017 05:51 XML login: epetrov8 - 247.153.128.199(DNS name not found).",
    "normalized form": "{   "subject": "account",   "action": "open",   "object": "session",   "status": "success",   "event_src.category": "Server management",   "event_src.title": "ilo",   "event_src.vendor": "hewlett_packard_enterprise",   "id": "PT_Hewlett_Packard_Enterprise_iLO_syslog_rpc_session_start_stop",   "importance": "info",   "logon_auth_method": "remote",   "logon_service": "XML API",   "src.ip": "247.153.128.199",   "subject.account.name": "epetrov8",   "subject.name": "epetrov8",   "time": "2017-03-15T05:51:00.000Z" }"
},
{
    "raw form": "<134> #ILO 4: 03/15/2017 05:51 XML logout: EPetrov8 - 247.153.128.199(DNS name not found).",
    "normalized form": "{   "subject": "account",   "action": "close",   "object": "session",   "status": "success",   "event_src.category": "Server management",   "event_src.title": "ilo",   "event_src.vendor": "hewlett_packard_enterprise",   "id": "PT_Hewlett_Packard_Enterprise_iLO_syslog_rpc_session_start_stop",   "importance": "info",   "logon_auth_method": "remote",   "logon_service": "XML API",   "src.ip": "247.153.128.199",   "subject.account.name": "epetrov8",   "subject.name": "epetrov8",   "time": "2017-03-15T05:51:00.000Z" }"
}]
"""

as_if_ai_answer_2 = """
"action = "open"": "User {subject.account.name} from host {src.host} opened an RPC session on host {event_src.host}"
"action = "close"": "User {subject.account.name} from host {src.host} ended an RPC session on host {event_src.host}"
"""

real_logs_to_clustering = """
Your task: Analyze the provided logs and cluster them based on the field(s) that most effectively separate the logs into distinct groups. For each cluster, provide a description using the specified output format, which should include relevant details from the normalized log data.

The output format is:
"<clustering field(s)>": "Description template using relevant fields like {field1}, {field2}, etc."

You should choose the clustering field(s) that result in the most meaningful separation of the log data. The description template should be a concise summary that captures the key details of the logs in that cluster.

Input:
[{
    "raw form": "<134>1 2024-01-12T08:16:56Z ILOCZ3333H1MM #ILO4 - - - User Pabalobabam Peter added by EPetrov.",
    "normalized form": "{   "subject": "account",   "action": "create",   "object": "account",   "status": "success",   "category.generic": "Account",   "category.high": "Users And Rights Management",   "category.low": "Manipulation",   "event_src.category": "Server management",   "event_src.hostname": "ilocz3333h1mm",   "event_src.title": "ilo",   "event_src.vendor": "hewlett_packard_enterprise",   "id": "PT_Hewlett_Packard_Enterprise_iLO_syslog_user_added_deleted",   "importance": "info",   "object.account.name": "pabalobabam peter",   "object.name": "pabalobabam peter",   "subject.account.name": "epetrov",   "subject.name": "epetrov",   "time": "2024-01-12T08:16:56.000Z" },"
},
{
    "raw form": "<134>1 2024-01-12T08:16:56Z ILOCZ3333H1MM #ILO4 - - - User Pabalobabam Peter deleted by EPetrov.",
    "normalized form": "{   "subject": "account",   "action": "remove",   "object": "account",   "status": "success",   "category.generic": "Account",   "category.high": "Users And Rights Management",   "category.low": "Manipulation",   "event_src.category": "Server management",   "event_src.title": "ilo",   "event_src.vendor": "hewlett_packard_enterprise",   "id": "PT_Hewlett_Packard_Enterprise_iLO_syslog_user_added_deleted",   "importance": "info",   "object.account.name": "pabalobabam peter",   "object.name": "pabalobabam peter",   "subject.account.name": "epetrov",   "subject.name": "epetrov",   "time": "2017-03-15T05:29:00.000Z" }"
}]
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
      temperature=0.1,
      # top_p=0.7,
      max_tokens=512,
)

print(response)
print(response["choices"][0]["message"]["content"])
