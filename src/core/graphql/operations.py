"""This module contains all the graphql operations"""

GET_GRAPH_QL_DATABASE = """
query GET_GRAPH_QL_DATABASE($id: ID!) {
  getGraphDatabase(id: $id) {
    id
    status
    operations {
      items {
        id
        status
        success
        error
      }
    }
  }
}
"""

GET_PLANT_GRAPH_QL = """
query GET_PLANT_GRAPH_QL($id: ID!) {
  getPlant(id: $id) {
    graphDatabase {
      id
      UserGroup
      AdminGroup
    }
  }
}
"""

GET_DOCUMENT_GRAPH_QL_STATUS = """
query status($id: ID!) {
  getDocument(id: $id) {
    status
  }
}
"""


CREATE_GRAPH_QL_OPERATION = """
mutation Operation($input: CreateGraphOperationsInput!) {
  createGraphOperations(input: $input) {
    id
    status
    payload
  }
}
"""

UPDATE_GRAPH_QL_DATABASE = """
mutation UPDATE_GRAPH_QL_DATABASE ($id:ID!, $input: GraphDatabaseInput!) {
  updateGraphDatabase(id: $id, input: $input) {
    id
    createdBy
    status
  }
}
"""

CREATE_GRAPH_QL_DATABASE = """
mutation CREATE_GRAPH_QL_DATABASE ($id: ID!,$input: GraphDatabaseInput!) {
  createGraphDatabase(plantID: $id, input: $input) {
    id
    status
    UserGroup
    AdminGroup
  }
}
"""

UPDATE_PLANT_GRAPH_QL = """
mutation UPDATE_PLANT_GRAPH_QL($input: UpdatePlantInput!) {
  updatePlant(input: $input) {
    id
  }
}
"""
UPDATE_DOCUMENT = """
mutation UpdateDocument($input: UpdateDocumentInput!) {
  updateDocument(input: $input) {
    id
  }
}
"""

GET_DATABASE_NAME_FROM_PLANT_ID = """
  query GET_DATABASE_NAME_FROM_PLANT_ID($id: ID!) {
    getPlant(id: $id) {
      graphDatabaseUniqueId
      name
    }
  }
"""
