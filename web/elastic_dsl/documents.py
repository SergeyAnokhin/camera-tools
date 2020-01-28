from elasticsearch_dsl import analyzer
from django_elasticsearch_dsl import Document, Index, fields 
from django_elasticsearch_dsl.registries import registry
from . import models

article_index = Index('articles')
article_index.settings(
    number_of_shards=1,
    number_of_replicas=0
)

html_strip = analyzer(
    'html_strip',
    tokenizer="standard",
    filter=["standard", "lowercase", "stop", "snowball"],
    char_filter=["html_strip"]
)  

@registry.register_document
class ArticleDocument(Document):
    """Article elasticsearch document"""

    id = fields.IntegerField(attr='id')
    title = fields.TextField(
        analyzer=html_strip,
        fields={
            'raw': fields.TextField(analyzer='keyword'),
        }
    )
    body = fields.TextField(
        analyzer=html_strip,
        fields={
            'raw': fields.TextField(analyzer='keyword'),
        }
    )
    author = fields.IntegerField(attr='author_id')
    created = fields.DateField()
    modified = fields.DateField()
    pub_date = fields.DateField()

    class Meta:
        model = models.Article 

    class Django:
        model = models.Article
        # fields = [
        #     'title',
        #     'body',
        #     'author',
        #     'created',
        #     'modified',
        #     'pub_date',
        # ]
    