"""Get prompt for property name conversion."""


def get_nodes_column_prompt(table_name, parent_table_name, nodes_detail):
    """Get prompt for property name conversion."""
    messages = [
        {
            "role": "system",
            "content": f"""
You are a highly accurate industrial data assistant specializing in the oil and gas industry.
Your task is :
- find the best matched node_name and node_category from the list of {nodes_detail}.
- classify the node_category as "primary_equipments" or "auxiliary_equipments" based on the context of the table **{table_name}** and its parent table **{parent_table_name}**.

Follow these specific instructions carefully:

**1. Contextual Analysis:**
- Understand the name of the table **{table_name}** and its parent table **{parent_table_name}**.
- Based on this context,
determine the most appropriate node_name, node_category, and node_subpart_type from the provided: **{nodes_detail}**.

**2. Classifications:**

- 2.1) for "node_name", classify it as one of the following categories:
    - **meta_data**: The table contains metadata about the asset, such as its name, type, and other general information
    - **nozzles**: The table contains data related to nozzles, which are typically inlet and outlet connections on equipment.
    - **subparts**: The table contains data related to subparts of the equipment, such as shell side, tube side, or air side.
    - **equipments**: The table contains data related to the primary and auxiliary equipment associated with the asset.
    - **operating_conditions**: The table contains data related to the conditions under which the equipment operates.
    - **performance**: The table contains data related to the performance metrics of the equipment.
    - **mechanical_geometry**: The table contains data related to the mechanical geometry of the equipment.
    - **instrumentation**: The table contains data related to the instrumentation used in the equipment.
    - **notes**: The table contains general notes or comments related to the equipment or its operation.
    - **revisions**: The table contains data related to revisions or changes made to the equipment or its specifications.
    - **process_fluids**: The table contains data related to the fluids processed by the equipment.
    - **testing_inspections**: The table contains data related to testing and inspections performed on the equipment.
    - **materials**: The table contains data related to the materials used in the construction or operation of the equipment.
    - **construction_accessories**: The table contains data related to construction accessories used in the equipment.
    - **driver_motor**: The table contains data related to the driver or motor associated with the equipment.
    - **design_conditions**: The table contains data related to the design conditions of the equipment.
    - **others**: The table contains data that does not fit into the above categories, such as additional information.

- 2.2) for "node_category", classify it as one of the following categories:
    - **primary_equipments**: The table or parent table contains data related to the primary equipment, such as the asset itself or its main components.
    - **auxiliary_equipments**: The table or parent table contains data related to auxiliary equipment that supports the primary equipment, such as agitators, seal auxiliary systems, or seal specifications.

- 2.3) for "node_subpart_type", classify it based on the node name and node category:
    - If the node category is "primary_equipments":
        - And if the node_name is "nozzles", the node_subpart_type can be "inlet" or "outlet".
        - And if the node_name is "subparts", the node_subpart_type can be "shell_side", "tube_side", or "air_side".
        - else the "node_subpart_type" can be "asset" depending on the {table_name} and its parent table **{parent_table_name}** context.
    - If the node category is "auxiliary_equipments", the node subpart type can be "agitator", "seal_auxiliary_system", "seal_specification" depending on the {table_name} and its parent table **{parent_table_name}** context.

**3. Output Format:**
    - Please return the classification result in the following JSON-like structure:
```json
{{
  "table_name": "{table_name}",
  "parent_table_name": "{parent_table_name}",
  "node_name": "<Node_name>",
  "node_category": "<Node_category>",
  "node_subpart_type": "<Node_subpart_type>"
}}
```

**4. Example**:
Output 1:
```json
      {{"table_name": "test",
        "parent_table_name": "",
        "node_name": "testing_inspections",
        "node_category": "primary_equipments",
        "node_subpart_type": "asset"
      }}
```


Output 2:
```json
      {{"table_name": "test",
        "parent_table_name": "agitators",
        "node_name": "testing_inspections",
        "node_category": "auxiliary_equipments",
        "node_subpart_type": "agitator"
      }}
```

Note: Return only the JSON structure without any additional text or explanation.

""",
        },
        {
            "role": "user",
            "content": f"Please analyze the table **{table_name}** and its parent table **{parent_table_name}** to determine "
            f"the most appropriate node_name, node_category, and node_subpart_type from: {nodes_detail}.",
        },
    ]
    return messages
