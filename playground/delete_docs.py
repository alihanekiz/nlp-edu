from elasticsearch import Elasticsearch

# Verbinde mit dem Elasticsearch-Server
es = Elasticsearch()

# Definiere den Index, aus dem die Dokumente gelöscht werden sollen
index_name = "document"

# Definiere die Suchabfrage, um alle Dokumente auszuwählen
query = {
  "query": {
    "match_all": {}
  }
}

# Lösche alle Dokumente aus dem Index
es.delete_by_query(index=index_name, body=query)
