# python -m src.app
# event = {
#     "queryStringParameters": {
#         "action": "EXTRACT_CAUSE_AND_EFFECT_DATA",
#         "bucket_name": "artisanbucketoregon133719-dev",
#         "plant_id": "44bbbac3-f496-4a6c-800e-808e1dec1fe8",
#         "document_id": "test-id-1234"
#     }
# }
# print(lambda_handler(event, context=None))

# event = {
#     "queryStringParameters": {
#         "action": "EXTRACT_PROCESS_NARRATIVE_DATA",
#         "type": "PROCESS_AND_CONTROL_NARRATIVE",
#         "mode": "PROCESS_AND_CONTROL_NARRATIVE",
#         "plant_id": "dfe34e6b-2b5d-47d5-98dd-8a76d74f1334",
#         "document_id": "b703723e-c15e-4881-9cc5-bcc41895d36c",
#         "bucket_name": "artisanbucketoregon133719-dev"
#     }
# }


# event = {
#     "queryStringParameters": {
#         "action": "GET_DATA_SHEET_STANDARD_DETAILS",
#         "extract_type": "DATA_SHEET_STANDARD_TABLE_NAME",
#         "plant_id": "44bbbac3-f496-4a6c-800e-808e1dec1fe8",
#         "bucket_name": "artisanbucketoregon133719-dev",
#     }
# }

# for data sheet table extraction
# event = {
#     "queryStringParameters": {
#         "action": "EXTRACT_DATA_SHEET_DATA",
#         "extract_type": "DATA_SHEET_TABLE_EXTRACTION",
#         "plant_id": "44bbbac3-f496-4a6c-800e-808e1dec1fe8",
#         "document_id": "380b4ee8-cbc9-4394-8d2f-a37fc8b4d423",
#         "bucket_name": "artisanbucketoregon133719-dev",
#     }
# }

# for process narrative extraction using rag
# event = {
#     "queryStringParameters": {
#         "action": "EXTRACT_PROCESS_NARRATIVE_RAG_DATA",
#         "plant_id": "499df0e0-5ede-4330-875a-c3e2f7881848",
#         "document_id": "8778c671-94e9-4f3f-a424-7ad80d85c6af",
#         "bucket_name": "artisanbucketoregon133719-dev"
#     }
# }

# event = {
#     "queryStringParameters": {
#         "action": "EXTRACT_PROCESS_NARRATIVE_RAG_JUNIOR_DATA",
#         "extract_type": "PROCESS_NARRATIVE_STREAM_CONDITION_EXTRACTION",
#         "plant_id": "499df0e0-5ede-4330-875a-c3e2f7881848",
#         "document_id": "8778c671-94e9-4f3f-a424-7ad80d85c6af",
#         "bucket_name": "artisanbucketoregon133719-dev"
#     }
# }

# event = {
#     "queryStringParameters": {
#         "action": "EXTRACT_PROCESS_NARRATIVE_RAG_JUNIOR_DATA",
#         "extract_type": "PROCESS_NARRATIVE_EQUIPMENT_OPERATING_CONDITION_EXTRACTION",
#         "plant_id": "499df0e0-5ede-4330-875a-c3e2f7881848",
#         "document_id": "8778c671-94e9-4f3f-a424-7ad80d85c6af",
#         "bucket_name": "artisanbucketoregon133719-dev"
#     }
# }


# event = {
#     "queryStringParameters": {
#         "action": "CHECK_DOCUMENT_STATUS",
#         "document_id": "598dc321-4cc7-4d6d-a065-a3a2e002441f",
#         "bucket_name": "artisanbucketoregon133719-dev",
#     }
# }


# event = {
#     "queryStringParameters": {
#         "action": "TRIGGERED_DATA_SHEET_DATA_ACTION",
#         "extract_type": "DATA_SHEET_TABLE_EXTRACTION",
#         "plant_id": "499df0e0-5ede-4330-875a-c3e2f7881848",
#         "document_id": "143ff74a-06ad-441a-bec8-c3abf69be2b0",
#         "bucket_name": "artisanbucketoregon133719-dev",
#     }
# }


# event = {
#     "queryStringParameters": {
#         "action": "TRIGGERED_CONTROL_NARRATIVE_DATA_ACTION",
#         "plant_id": "499df0e0-5ede-4330-875a-c3e2f7881848",
#         "document_id": "d1d1a076-f78a-4daa-bdac-5bb79fd9b807",
#         "bucket_name": "artisanbucketoregon133719-dev",
#     }
# }

# event = {
#     "queryStringParameters": {
#         "action": "EXTRACT_CONTROL_NARRATIVE_RAG_JUNIOR_DATA",
#         "plant_id": "dfe34e6b-2b5d-47d5-98dd-8a76d74f1334",
#         "document_id": "c52d1436-5937-487b-b189-6e22cdcbaa66",
#         "bucket_name": "artisanbucketoregon133719-dev",
#     }
# }


# event = {
#     "queryStringParameters": {
#         "action": "EXTRACT_DATA_SHEET_DATA_V2",
#         "extract_type": "DATA_SHEET_TABLE_EXTRACTION",
#         "plant_id": "ef2aa057-2f9c-453b-9990-dcb4459a4355",
#         "document_id": "a4dd2a67-9b3f-49c9-b306-f94f08542210",
#         "bucket_name": "artisanbucketoregon133719-dev",
#     }
# }

# event = {
#     "queryStringParameters": {
#         "action": "EXTRACT_DATA_SHEET_DATA_V2",
#         "extract_type": "DATA_SHEET_GENERATE_RAW_JSON",
#         "plant_id": "ef2aa057-2f9c-453b-9990-dcb4459a4355",
#         "document_id": "a4dd2a67-9b3f-49c9-b306-f94f08542210",
#         "bucket_name": "artisanbucketoregon133719-dev",
#     }
# }

# print(lambda_handler(event, context=None))
# # python -m src.app

# event = {
#     "queryStringParameters": {
#         "action": "EXTRACT_DATA_SHEET_DATA_V2",
#         # "extract_type": "DATA_SHEET_TABLE_EXTRACTION",
#         # "extract_type": "DATA_SHEET_SECOND_SHOT_TABLE_EXTRACTION",
#         "extract_type": "DATA_SHEET_INDIVIDUAL_TABLE_EXTRACTION",
#         "table_id": "769954bd-78a8-4dce-b1ce-3dc90c960f2f",
#         "plant_id": "6a434010-5f30-4b46-9580-e125ec26dc14",
#         "document_id": "6486aee0-9c57-4201-be39-f799dad27c74",
#         "bucket_name": "artisanbucketoregon133719-dev",
#     }
# }

# print(lambda_handler(event, context=None))
