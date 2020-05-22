import pymongo
from werkzeug.security import generate_password_hash

uri = 'mongodb+srv://admin:admin@cms-nano-lab-a2j1a.mongodb.net/test?retryWrites=true&w=majority'
client = pymongo.MongoClient(uri,maxPoolSize=50, connect=False)

def get_courses():
    # returns all courses names and descriptions
    cms = client.cms
    courses = cms.courses
    courses_list = courses.find({},{'name':1, 'description':1, '_id':0})
    return list(courses_list)

def get_course_info(course_name):
    # return the content and description of a given course
    cms = client.cms
    courses = cms.courses
    course_content = courses.find_one({'name': course_name},{'_id':0, 'content':1, 'description': 1})
    return course_content

def get_article(course_name, subject, article_name):
    # returns an article with given course name, course subject, and article name
    cms = client.cms
    articles = cms.articles
    article = articles.find_one(
        {'course_name':course_name, 'subject':subject, 'name':article_name},
        {'content':1, '_id':0}
        )
    return article['content']

def find_user(username):
    # returns if a given username already exists or not
    return client.cms.users.find_one({'_id': username})

def create_new_user(first_name, second_name, username, password):
    # adds a new user to the database
    user = client.cms.users.insert_one({
        '_id': username,
        'password': generate_password_hash(password, method='pbkdf2:sha256')
    })
    return user.acknowledged