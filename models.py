import peewee
from bs4 import BeautifulSoup as BS
import requests
import json
import ast
from db import db


class CoursesList(peewee.Model):
    title = peewee.CharField()
    slug = peewee.CharField(unique=True)

    class Meta:
        database = db
        table_settings = ['ENGINE=InnoDB', 'DEFAULT CHARSET=utf8']

    @classmethod
    def parser(cls):
        url = 'https://coursive.id/api/v1/courses/'
        html = requests.get(url)
        soup = BS(html.text, 'html.parser')
        site_json = json.loads(soup.text)
        titles = [item.get('title') for item in site_json['results'] if item.get('title')]
        created = [item.get('created_at') for item in site_json['results'] if item.get('created_at')]
        slugs = [item.get('slug') for item in site_json['results'] if item.get('slug')]
        for i in range(0, len(titles)):
            CoursesList.create(title=titles[i], date_created=created[i], slug=slugs[i])


class CoursesDetails(peewee.Model):
    details_slug = peewee.ForeignKeyField(CoursesList, to_field='slug', on_delete='CASCADE')
    date_created = peewee.DateTimeField()
    title = peewee.CharField()
    name_tutor = peewee.CharField()
    description = peewee.TextField()
    learn_to = peewee.TextField()
    blocks = peewee.TextField()

    class Meta:
        database = db
        table_settings = ['ENGINE=InnoDB', 'DEFAULT CHARSET=utf8']

    @classmethod
    def parser(cls, slug):
        url = 'https://coursive.id/api/v1/courses/' + slug
        html = requests.get(url)
        soup = BS(html.text, 'html.parser')
        site_json = json.loads(soup.text)
        slug_details = site_json['slug']
        title = site_json['title']
        date_created = site_json['created_at']
        tutor_name = site_json['persons'][0].get('name')
        if slug == 'feminizm-zhonundo-kurs':
            body = site_json['body']
            body2 = json.loads(body).get('blocks')[0].get('data').get('text')
            body3 = json.loads(body).get('blocks')[1].get('data').get('items')
            body3 = '\n'.join(body3)
            body4 = json.loads(body).get('blocks')[2].get('data').get('text')
            description = body2 + '\n' + body3 + '\n' + body4
        else:
            description = ast.literal_eval(site_json['body']).get('blocks')[0].get('data').get('text')
        learn_tos = [item.get('title') for item in site_json['learn_to'] if item.get('title')]
        learn_tos = '.\n'.join(learn_tos)
        blocks = [item.get('title') for item in site_json['blocks'] if item.get('title')]
        blocks = '\n'.join(blocks)
        CoursesDetails.create(details_slug=slug_details, title=title, date_created=date_created, name_tutor=tutor_name,
                              description=description, learn_to=learn_tos, blocks=blocks)


cursor = db.cursor()
sql = "DROP TABLE IF EXISTS coursesdetails"
cursor.execute(sql)
sql = "DROP TABLE IF EXISTS courseslist"
cursor.execute(sql)

if not CoursesList.table_exists():
    CoursesList.create_table()

if not CoursesDetails.table_exists():
    CoursesDetails.create_table()