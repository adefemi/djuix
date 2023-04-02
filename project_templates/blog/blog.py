from abstractions.enums import ModelFieldTypes, SerializerFieldTypes
from project_templates.interfaces.app_creation import AppCreation


class BlogControl(AppCreation):
    
    def __init__(self, *args, **kwargs):
        super(BlogControl, self).__init__(*args, **kwargs)
        
        # set up model fields
        # blog model object is made up of the model name as the key and the fields information as the value
        self.model_data = {
            "BlogTagModel": {
                "fields": [
                    {
                        "name": "title",
                        "field_type": ModelFieldTypes.CharField,
                        "field_properties": {
                            "unique": "True",
                            "max_length": 50
                        }
                    },
                ],
                "has_created_at": True, 
                # "string_representation": [
                #     "title",
                # ]
            },
            
            "BlogModel": {
                "fields": [
                    {
                        "name": "tags",
                        "field_type": ModelFieldTypes.ManyToManyField,
                        "field_properties": {
                            "related_model_name": "BlogTagModel",
                            "related_name": "blog_tags",
                        }
                    },
                    {
                        "name": "cover",
                        "field_type": ModelFieldTypes.ImageField,
                        "field_properties": {
                            "null": "True",
                            "blank": "True",
                        }
                    },
                    {
                        "name": "title",
                        "field_type": ModelFieldTypes.CharField,
                        "field_properties": {
                            "unique": "True",
                            "max_length": "255",
                        }
                    },
                    {
                        "name": "slug",
                        
                        "field_type": ModelFieldTypes.SlugField,
                        "field_properties": {
                            "field_reference": "title",
                            "default": "",
                            "max_length": "255",
                            "editable": "False"
                        }
                    },
                    {
                        "name": "author",
                        "field_type": ModelFieldTypes.CharField,
                        "field_properties": {
                            "max_length": "255",
                            "default": "Annoymous"
                        }
                    },
                    {
                        "name": "content",
                        "field_type": ModelFieldTypes.TextField,
                        "field_properties": {}
                    }
                ],
                "has_created_at": True,
                "has_updated_at": True,
                # "string_representation": [
                #     "title",
                #     "author"
                # ],
                "meta": {
                    "ordering": "('-created_at', )",
                }
            },
            
            "BlogCommentModel": {
                "fields": [
                    {
                        "name": "blog",
                        "field_type": ModelFieldTypes.ForeignKey,
                        "field_properties": {
                            "related_model_name": "BlogModel",
                            "related_name": "blog_comments",
                            "on_delete": "models.CASCADE"
                        }
                    },
                    {
                        "name": "author",
                        "field_type": ModelFieldTypes.CharField,
                        "field_properties": {
                            "max_length": "255",
                            "default": "Annoymous"
                        }
                    },
                    {
                        "name": "ip",
                        "field_type": ModelFieldTypes.CharField,
                        "field_properties": {
                            "max_length": "50",
                            "blank": "True",
                            "null": "True"
                        }
                    },
                    {
                        "name": "comment",
                        "field_type": ModelFieldTypes.TextField,
                        "field_properties": {}
                    },
                ],
                "has_created_at": True,
                "has_updated_at": True,
                # "string_representation": [
                #     "blog.title",
                #     "author",
                # ],
                "meta": {
                    "ordering": "('-created_at',)",
                }
            }
        }
        
        self.serializer_data = {
            "BlogTagSerializer": {
                "meta": {
                    "model": "BlogTagModel",
                    "fields": "['id', 'title']"
                },
                "type": "ModelSerializer",
            },
            "BlogSerializer": {
                "fields": [
                    {
                        "name": "tags",
                        "field_type": "BlogTagSerializer",
                        "is_custom_type": True,
                        "field_properties": {
                            "many": "True",
                            "read_only": "True",
                        }
                    },
                    # {
                    #     "name": "author",
                    #     "field_type": "CustomUserSerializer",
                    #     "external_serializer": {
                    #         "app_ref": "User"
                    #     },
                    #     "is_custom_type": True,
                    #     "field_properties": {
                    #         "read_only": "True",
                    #     }
                    # },
                    # {
                    #     "name": "author_id",
                    #     "field_type": SerializerFieldTypes.IntegerField,
                    #     "field_properties": {
                    #         "write_only": "True",
                    #     }
                    # },
                ],
                "meta": {
                    "model": "BlogModel",
                    "fields": "'__all__'",
                },
                "type": "ModelSerializer",
            },
            "BlogCommentSerializer": {
                "fields": [
                    {
                        "name": "blog",
                        "field_type": "BlogSerializer",
                        "is_custom_type": True,
                        "field_properties": {
                            "read_only": "True",
                        }
                    },
                    {
                        "name": "blog_id",
                        "field_type": SerializerFieldTypes.IntegerField,
                        "field_properties": {
                            "write_only": "True",
                        }
                    },
                ],
                "meta": {
                    "model": "BlogCommentModel",
                    "fields": "'__all__'",
                },
                "type": "ModelSerializer",
            }
        }
        
        self.view_data = {
            "BlogView": {
                "lookup_field": "slug",
                # "permission_classes": [
                #     "IsAuthenticatedOrReadOnly",
                # ],
                "implement_search": {
                    "search_key": "keyword",
                    "search_fields": [
                        "title",
                        "tags__title",
                    ]
                },
                "override_create": {
                    "update_data_field": [
                        {
                            "field_name": "author_id",
                            "field_from": "auth_user"
                        }
                    ],
                    "add_many_to_many": [
                        {
                            "field_name": "tags",
                            "field_body_key": "tags",
                            "field_model": "BlogTag",
                            "field_check_key": "title"
                        }
                    ]
                },
                "override_update": {
                    "update_many_to_many": [
                        {
                            "field_name": "tags",
                            "field_body_key": "tags",
                            "field_model": "BlogTag",
                            "field_check_key": "title"
                        }
                    ]
                }
            },
            "BlogCommentView": {},
            "BlogTagView": {
                # "permission_classes": [
                #     "IsAuthenticatedOrReadOnly",
                # ],
            },
            "TopBlogView": {
                "model": "Blog",
                "serializer": "BlogSerializer",
                "http_method_names": [
                    "get",
                ],
                "get_top_content": {
                    "counter_key": "blog_comments",
                    "order_key": "blog_comments_count",
                    "amount": 5
                }
            },
            "SimilarBlogView": {
                "model": "Blog",
                "serializer": "BlogSerializer",
                "http_method_names": [
                    "get",
                ],
                "get_similar_content": {
                    "search_id": "blog_id",
                    "related_key": "tags",
                    "field_to_check": "id"
                }
            }
        }
        
        self.url_data = {
            "blogs": {
                "view": "BlogView",
                "name": "blog_list",
            },
            "blogs-tags": {
                "view": "BlogTagView",
                "name": "blog_tag_list",
            },
            "blogs-comments": {
                "view": "BlogCommentView",
                "name": "blog_comment_list",
            },
            "top-blogs": {
                "view": "TopBlogView",
                "name": "top_blog_list",
            },
            "similar-blogs": {
                "view": "SimilarBlogView",
                "name": "similar_blog_list",
                "kwargs": [
                    {
                        "key": "blog_id",
                        "type": "int",
                    }
                ]
            }
        }