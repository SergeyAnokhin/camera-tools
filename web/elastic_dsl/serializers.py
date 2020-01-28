from django_elasticsearch_dsl_drf.serializers import DocumentSerializer

import documents as articles_documents
 
 
class ArticleDocumentSerializer(DocumentSerializer):
    class Meta:
        document = articles_documents.ArticleDocument
        fields = (
            'id',
            'title',
            'body',
            'author',
            'created',
            'modified',
            'pub_date',
        )   