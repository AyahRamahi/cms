import pymongo
import datetime
import bson
from werkzeug.security import generate_password_hash

uri = 'mongodb+srv://admin:admin@cms-nano-lab-a2j1a.mongodb.net/test?retryWrites=true&w=majority'
client = pymongo.MongoClient(uri,maxPoolSize=50, connect=False)

##############################################################################
############################# Course functions ###############################
##############################################################################

def get_courses():
    # returns all courses available on the db
    cms = client.cms
    courses = cms.courses
    courses_list = courses.find({},{'name':1, 'description':1, '_id':0})
    return list(courses_list)

def get_course_info(course_name):
    # return the content and description of a course
    cms = client.cms
    courses = cms.courses
    course_content = courses.find_one({'name': course_name},{'_id':0, 'content':1, 'description': 1})
    return course_content

def get_course_articles_count(course_name):
    # return the total number of articles in a course
    count =0
    course_content = client.cms.courses.find_one({'name': course_name}, {'_id':0, 'content':1})['content']
    for subject in course_content:
        count = count + len(subject['articles'])
    return count

def add_new_course_subject(course_name, new_subject_name):
    return client.cms.courses.update_one(
        {'name':course_name},
            {'$push': {
                'content': {
                    '$each':[{
                        'subject': new_subject_name,
                        'articles': []
                    }]
                }
            }
        }
    )

def delete_course_subject(course_name, subject):
    content = client.cms.courses.find_one({'name': course_name}, {'_id':0, 'content':1})['content']
    subject_articles = next((x for x in content if x['subject'] == subject), None)['articles']
    for article in subject_articles:
        client.cms.articles.delete_one({'course_name': course_name, 'subject': subject, 'name': article})
    return client.cms.courses.update_one(
        {'name':course_name},
            {'$pull': {
                'content':  {'subject': subject }
            }
        }
    )

##############################################################################
############################# Article functions ##############################
##############################################################################

def get_article(course_name, subject, article_name):
    # returns the content of the article with given parameters
    cms = client.cms
    articles = cms.articles
    article = articles.find_one(
        {'course_name':course_name, 'subject':subject, 'name':article_name},
        {'content':1, '_id':1}
        )
    return article

def mark_article_completed(username, id, course_name):
    # marks a specific article as completed
    client.cms.users.update_one(
        {'_id': username, 'ongoing_courses.course_name': course_name},
            {'$inc': {
                'ongoing_courses.$.finished_articles_count':  1
            }
        }
    )
    return client.cms.users.update_one(
        {'_id': username},
            {'$push': {
                'completed_articles':  id 
            }
        }
    )

def get_article_content(course_name, subject, article_name):
    return client.cms.articles.find_one(
        {'course_name':course_name, 'subject':subject, 'name':article_name},
        {'_id':0, 'content':1}
    )['content']

def edit_article_content(course_name, subject, article_name, article_content):
    return client.cms.articles.update_one(
        {'course_name': course_name, 'subject': subject, 'name': article_name},
            {'$set': {
                'content':  article_content
            }
        }
    )

def is_article_completed(username, id):
    # checks if a given article is completed
    completed_articles = client.cms.users.find_one({'_id': username}, {'_id':0, 'completed_articles':1})['completed_articles']
    return str(id) in completed_articles

def remove_article_from_completed(username, id, course_name):
    # removes an article from completed
    client.cms.users.update_one(
        {'_id': username, 'ongoing_courses.course_name': course_name},
            {'$inc': {
                'ongoing_courses.$.finished_articles_count':  -1
            }
        }
    )
    return client.cms.users.update_one(
        {'_id': username},
            {'$pull': {
                'completed_articles':  id 
            }
        }
    )


##############################################################################
############################# Comments functions #############################
##############################################################################

def get_comments(course_name, subject, article_name):
    # returns all comments posted on a specific article
    cms = client.cms
    articles = cms.articles
    article = articles.find_one(
        {'course_name':course_name, 'subject':subject, 'name':article_name},
        {'comments':1, '_id':0}
        )
    return article['comments']

def add_comment(course_name, subject, article_name, username, name, comment):
    # adds a comment on a specific article with username and name of a user and date
    return client.cms.articles.update_one(
        {'course_name':course_name, 'subject':subject, 'name':article_name},
            {'$push': {
                'comments': {
                    '$each':[{
                        '_id': bson.objectid.ObjectId(),
                        'name': name,
                        'username': username,
                        'comment': comment,
                        'date': datetime.date.today().strftime("%d/%B/%Y")
                    }],
                    '$position': 0
                }
            }
        }
    )

def delete_comment(course_name, subject, article_name, id):
    # deletes a comment from a specfic article with given id
    return client.cms.articles.update_one(
        {'course_name':course_name, 'subject':subject, 'name':article_name},
            {'$pull': {
                'comments':  {'_id': bson.objectid.ObjectId(id) }
            }
        }
    )

##############################################################################
############################# User functions #################################
##############################################################################

def find_user(username):
    # returns the user with the given username
    return client.cms.users.find_one({'_id': username})

def create_new_user(first_name, last_name, username, password):
    # creates a new user with specific info
    user = client.cms.users.insert_one({
        '_id': username,
        'password': generate_password_hash(password, method='pbkdf2:sha256'),
        'first_name': first_name,
        'last_name': last_name,
        'completed_courses':[],
        'ongoing_courses':[],
        'completed_articles':[]
    })
    return user.acknowledged

def is_user_enrolled(username, course_name):
    # checks if the user is enrolled in a course, by checking if it's in ongoing_courses
    ongoing_courses = client.cms.users.find_one({'_id': username}, {'_id':0, 'ongoing_courses':1})['ongoing_courses']
    completed_courses = client.cms.users.find_one({'_id': username}, {'_id':0, 'completed_courses':1})['completed_courses']
    return any(courses['course_name'] == course_name for courses in ongoing_courses) or any(name == course_name for name in completed_courses)

def enroll_user(username, course_name):
    # enrolls a user in a course by adding it to ongoing_courses
    return client.cms.users.update_one(
        {'_id': username},
            {'$push': {
                'ongoing_courses': {
                    '$each':[{
                        'course_name': course_name,
                        'finished_articles_count': 0
                    }],
                    '$position': 0
                }
            }
        }
    )

def get_ongoing_courses(username):
    # returns all ongoing_courses of a user
    return client.cms.users.find_one({'_id':username}, {'_id':0, 'ongoing_courses':1})['ongoing_courses']

def completed_course(username, course_name):
    # marks a course as completed by removing it from ongoing_courses and adding it
    # to completed courses
    client.cms.users.update_one(
        {'_id': username},
            {'$pull': {
                'ongoing_courses':  {'course_name': course_name}
            }
        }
    )
    return client.cms.users.update_one(
        {'_id': username},
            {'$push': {
                'completed_courses': course_name
            }
        }
    )

def get_completed_courses(username):
    # returns all completed courses of a user
    return client.cms.users.find_one({'_id':username}, {'_id':0, 'completed_courses':1})['completed_courses']

def change_name(username, first_name, last_name):
    # changes the first and last names of a user
    return client.cms.users.update_one(
        {'_id': username},
            {'$set':{
                'first_name': first_name,
                'last_name': last_name
            }
        }
    )
