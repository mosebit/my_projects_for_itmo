from llama_cpp import Llama

# my_model_path = r"C:\Users\Bazzz\AppData\Local\llama_index\models\llama-2-13b-chat.Q4_0.gguf"
my_model_path = r"C:\Users\Bazzz\AppData\Local\llama_index\models\llama-2-7b-chat.Q4_K_M.gguf"

llm = Llama(
    model_path=my_model_path,
    chat_format="llama-2",
    n_gpu_layers=2, # Uncomment to use GPU acceleration
    # use_mlock=True
    # seed=1337, # Uncomment to set a specific seed
    n_ctx=4096, # Uncomment to increase the context window
)


# user_added_deleted - task
task_normalization_rule = """
TEXT = '{"<"NUMBER">"?}{NUMBER?}{time=DATETIME?} {event_src.ip=IPV4|event_src.ip=IPV6|$host=HOSTNAME|}{":"?}
        #ILO 4{":"?} {$additional_info=STRING+} 
        User {$name=STRING+} {$event="added"|$event="deleted"} by {$subject_name_raw=REST}'

subformula "get_real_time"
    TEXT = '{$month=WORD}/{$day=WORD}/{$year=WORD} {$hour=WORD}:{$min=WORD}'

    time = $year + "-" + $month + "-" + $day + "T" + $hour + ":" + $min + ":00"
endsubformula 

subject = "account"

action = switch $event
   case "added" "create"
   case "deleted" "remove"
endswitch

object = "account"
status = "success"

# Deleting the final character
$subject_name_raw = strip($subject_name_raw, "", "\\u0000")
subject.account.name = lower(strip($subject_name_raw, "", "."))

object.account.name = lower($name)

if find_substr($additional_info, ":") != null then
    submessage("TEXT", "get_real_time", $additional_info)
endif

importance = "info"

category.high = "Users And Rights Management"
category.generic = "Account"
category.low = "Manipulation"

event_src.vendor = "hewlett_packard_enterprise"
event_src.title = "ilo"
event_src.hostname = lower($host)
event_src.category = "Server management"

id = "PT_Hewlett_Packard_Enterprise_iLO_syslog_user_added_deleted"

# -- DEPRECATED --
# lines from here will be deleted in future releases

subject.name = subject.account.name
object.name = object.account.name
"""
task_raw_event_logs = """
<134>1 2024-01-12T08:16:56Z ILOCZ3333H1MM #ILO4 - - - User Pabalobabam Peter added by EPetrov.
<134>1 2024-01-12T08:16:56Z ILOCZ3333H1MM #ILO4 - - - User Pabalobabam Peter deleted by EPetrov.
"""
task_normalized_event_logs = """
  {   "subject": "account",   "action": "create",   "object": "account",   "status": "success",   "category.generic": "Account",   "category.high": "Users And Rights Management",   "category.low": "Manipulation",   "event_src.category": "Server management",   "event_src.hostname": "ilocz3333h1mm",   "event_src.title": "ilo",   "event_src.vendor": "hewlett_packard_enterprise",   "id": "PT_Hewlett_Packard_Enterprise_iLO_syslog_user_added_deleted",   "importance": "info",   "object.account.name": "pabalobabam peter",   "object.name": "pabalobabam peter",   "subject.account.name": "epetrov",   "subject.name": "epetrov",   "time": "2024-01-12T08:16:56.000Z" },
  {   "subject": "account",   "action": "remove",   "object": "account",   "status": "success",   "category.generic": "Account",   "category.high": "Users And Rights Management",   "category.low": "Manipulation",   "event_src.category": "Server management",   "event_src.title": "ilo",   "event_src.vendor": "hewlett_packard_enterprise",   "id": "PT_Hewlett_Packard_Enterprise_iLO_syslog_user_added_deleted",   "importance": "info",   "object.account.name": "pabalobabam peter",   "object.name": "pabalobabam peter",   "subject.account.name": "epetrov",   "subject.name": "epetrov",   "time": "2017-03-15T05:29:00.000Z" },
"""

# user_group_added_deleted - example
example_normalization_rule = """
TEXT = '{"<"NUMBER">"?}{NUMBER?}{time=DATETIME?} {event_src.ip=IPV4|event_src.ip=IPV6|$host=HOSTNAME|}{":"?}
        #ILO 4{":"?} {$additional_info=STRING+}
        {$event="Added"|$event="Deleted"} group {object.group=STRING+} by: {$subject_name_raw=REST}'

subformula "get_real_time"
    TEXT = '{$month=WORD}/{$day=WORD}/{$year=WORD} {$hour=WORD}:{$min=WORD}'

    time = $year + "-" + $month + "-" + $day + "T" + $hour + ":" + $min + ":00"
endsubformula 

subject = "account"

action = switch $event
   case "Added" "create"
   case "Deleted" "remove"
endswitch

object = "user_group"
status = "success"

# Deleting the final character
$subject_name_raw = strip($subject_name_raw, "", "\\u0000")
subject.account.name = lower(strip($subject_name_raw, "", "."))

if find_substr($additional_info, ":") != null then
    submessage("TEXT", "get_real_time", $additional_info)
endif

importance = "info"

category.high = "Users And Rights Management"
category.generic = "Group"
category.low = "Manipulation"

event_src.vendor = "hewlett_packard_enterprise"
event_src.title = "ilo"
event_src.hostname = lower($host)
event_src.category = "Server management"

id = "PT_Hewlett_Packard_Enterprise_iLO_syslog_user_group_added_deleted"
"""
example_raw_event_logs = """
<134>1 2024-01-12T08:30:29Z ILOCZ3333H1MM #ILO4 - - - Added group tmp_group by: user_name.
<134>1 2024-01-12T08:32:34Z ILOCZ3333H1MM #ILO4 - - - Deleted group tmp_group by: user_name.
"""
example_normalized_event_logs = """
{   "subject": "account",   "action": "create",   "object": "user_group",   "status": "success",   "category.generic": "Group",   "category.high": "Users And Rights Management",   "category.low": "Manipulation",   "event_src.category": "Server management",   "event_src.title": "ilo",   "event_src.vendor": "hewlett_packard_enterprise",   "id": "PT_Hewlett_Packard_Enterprise_iLO_syslog_user_group_added_deleted",   "importance": "info",   "object.group": "tmp_group",   "subject.account.name": "user_name",   "time": "2017-03-15T05:29:00.000Z" },
{   "subject": "account",   "action": "remove",   "object": "user_group",   "status": "success",   "category.generic": "Group",   "category.high": "Users And Rights Management",   "category.low": "Manipulation",   "event_src.category": "Server management",   "event_src.title": "ilo",   "event_src.vendor": "hewlett_packard_enterprise",   "id": "PT_Hewlett_Packard_Enterprise_iLO_syslog_user_group_added_deleted",   "importance": "info",   "object.group": "tmp_group",   "subject.account.name": "user_name",   "time": "2017-03-14T11:26:00.000Z" },

"""
example_metainfo = """
EventDescriptions:
    - Criteria: id = "PT_Hewlett_Packard_Enterprise_iLO_syslog_user_group_added_deleted" and action = "create"
      LocalizationId: PT_HPE_iLO_syslog_user_group_added
    - Criteria: id = "PT_Hewlett_Packard_Enterprise_iLO_syslog_user_group_added_deleted" and action = "remove"
      LocalizationId: PT_HPE_iLO_syslog_user_group_deleted
"""
example_localization = """
Description: 'A user group was added or deleted'
EventDescriptions:
    - LocalizationId: 'PT_HPE_iLO_syslog_user_group_added'
      EventDescription: 'User {subject.account.name} added group {object.group} on host {event_src.host}'
    - LocalizationId: 'PT_HPE_iLO_syslog_user_group_deleted'
      EventDescription: 'User {subject.account.name} deleted group {object.group} on host {event_src.host}'
"""


system_content = "You are a cybersecurity specialist and yours role is - localisation writer for event logs. " \
                 "" \
                 "The user must give you:" \
                 "1) Normalization rule" \
                 "2) Set of event logs (every log in two representations - raw and normalized), for this normalization rule" \
                 "3) Example of normalization rule, for which a localization rule has already been created" \
                 "4) Example of event logs for example normalization rule (every log in two representations - raw and normalized)" \
                 "5) Localization rule for these example event logs" \
                 "" \
                 "In EventDescription field of localization rule you can use fields from normalized log, these fields you should wrap in curly braces." \
                 "" \
                 "Other rules for writing localizations:" \
                 "1) If the value of the field is a name (e.g. the name of the process that was created in the system), then it must be enclosed in double quotes" \
                 "2) If there is more than one sentence in the localization, a period is placed between them, as well as at the end of the second one. In the case of localization from a single sentence, there is no point. Localization with dots is taken in single quotes. It also applies if special characters are included in the locale" \
                 "3) If the event contains information about the node on which (or between which) the event occurred, it must be specified in the localization, and it is customary to put it at the end, specifying the fields *.host filled in the appendix <something was on the node {event_src.host}>" \
                 "4) Localization should contain a minimum set of information and abandoned fields that allow unambiguous interpretation of the event" \
                 "" \
                 "Localization includes two types of objects:" \
                 "1) Metainfo box - is used to enter localization rule conditions as follows:" \
                 "\"" \
                 "EventDescriptions:" \
                 "    - Criteria: <localization rule condition 1>" \
                 "      LocalizationId: <localization rule key 1>" \
                 "    - Criteria: <localization rule condition 2>" \
                 "      LocalizationId: <localization rule key 2>" \
                 "..." \
                 "\"" \
                 "Example:" \
                 "\"" \
                 "Description: <rule description>" \
                 "EventDescriptions:" \
                 "    - LocalizationId: <localization rule key 1>" \
                 "      EventDescription: <event description 1>" \
                 "    - LocalizationId: <localization rule key 2>" \
                 "      EventDescription: <event description 2>" \
                 "..." \
                 "\"" \
                 "2) Localization is used to enter a rule description and descriptions of events registered according to the rule as follows:" \
                 "\"" \
                 "Description: <rule description>" \
                 "EventDescriptions:" \
                 "    - LocalizationId: <localization rule key 1>" \
                 "      EventDescription: <event description 1>" \
                 "    - LocalizationId: <localization rule key 2>" \
                 "      EventDescription: <event description 2>" \
                 "..." \
                 "\"" \
                 "" \
                 "Example:" \
                 "\"" \
                 "Description: Large number of errors during attempt to log in from host and password bruteforce detection" \
                 "EventDescriptions:" \
                 "    - LocalizationId: Bruteforce_attempt_from_src_incident" \
                 "      EventDescription: An attempt of host {src.host} to bruteforce a password is detected" \
                 "    - LocalizationId: Bruteforce_attempt_from_src_incident_event" \
                 "      EventDescription: Large number of errors is detected during attempts to log in to the system from host {src.host}" \
                 "\"" \
                 "" \
                 "Yours answer includes ONLY two types of objects - Metainfo box and Localization. No other information can be generated."
user_content = f"Example:" \
               f"" \
               f"For this normalization rule localization rule already done, you can use it ONLY HOW example:" \
               f"{example_normalization_rule}" \
               f"" \
               f"Example raw event logs - for these logs localization rule already done, you can use it ONLY HOW example:" \
               f"{example_raw_event_logs}" \
               f"" \
               f"Example normalized event logs - for these logs localization rule already done, you can use it ONLY HOW example:" \
               f"{example_normalized_event_logs}" \
               f"" \
               f"Metainfo example - you can use it ONLY HOW example:" \
               f"{example_metainfo}" \
               f"" \
               f"Localization example - you can use it ONLY HOW example::" \
               f"{example_localization}" \
               f"" \
               f"Now you can see normalization rule for event logs for which you should develop yours localization:" \
               f"{task_normalization_rule}" \
               f"" \
               f"Event logs of this normalization rule in raw representation - you should write localization rule for THIS logs:" \
               f"{task_raw_event_logs}" \
               f"" \
               f"Event logs of this normalization rule in normalized representation - you should write localization rule for THIS logs:" \
               f"{task_normalized_event_logs}" \
               f"" \



response = llm.create_chat_completion(
      messages = [
          {"role": "system", "content": system_content},
          {"role": "user", "content": user_content}
      ],
      temperature=0.9,
      top_p=0.6,
      max_tokens=1024,
)

print(response)
print(response["choices"][0]["message"]["content"])
