from logger import Logger
import time
import json

from shopapp.models import *

logger = Logger('worker')

def create_update_user(full_info):

    if not full_info:
        return None
    try:
        user = InstaUser.objects.get(user_id=full_info[u'user']['id'])
    except:
        user = None


    if not user:
        logger.log('WORKER:get_follow_info: Create new User %s ' % full_info[u'user']['id'])

        user = InstaUser(user_id              = full_info[u'user']['id'],
                         user_name            = full_info[u'user']['username'],
                         user_full_name       = full_info[u'user']['full_name'],
                         followers_count      = int(full_info['user']['followed_by']['count']),
                         follow_count         = int(full_info['user']['follows']['count']),
                         profile_pic_url_hd   = full_info[u'user']['profile_pic_url_hd'],
                         user_biography       = full_info[u'user']['biography'],
                         user_external_url    = full_info[u'user']['external_url'],
                         follows_viewer       = full_info[u'user']['follows_viewer'],
                         followed_by_viewer   = full_info[u'user']['followed_by_viewer'],
                         has_requested_viewer = full_info[u'user']['has_requested_viewer'],
                         requested_by_viewer  = full_info[u'user']['requested_by_viewer'],
                         has_blocked_viewer   = full_info[u'user']['has_blocked_viewer'],
                         blocked_by_viewer    = full_info[u'user']['blocked_by_viewer'],
                         is_private           = full_info[u'user']['is_private'])
        user.save()
    else:
        #logger.log('WORKER:get_follow_info: Update old User %s ' % full_info[u'user']['id'])

        user.user_name            = full_info[u'user']['username'],
        user.user_full_name       = full_info[u'user']['full_name'],
        user.followers_count      = int(full_info['user']['followed_by']['count'])
        user.follow_count         = int(full_info['user']['follows']['count'])
        user.profile_pic_url_hd   = full_info[u'user']['profile_pic_url_hd']
        user.user_biography       = full_info[u'user']['biography']
        user.user_external_url    = full_info[u'user']['external_url']
        user.follows_viewer       = full_info[u'user']['follows_viewer']
        user.followed_by_viewer   = full_info[u'user']['followed_by_viewer']
        user.has_requested_viewer = full_info[u'user']['has_requested_viewer']
        user.requested_by_viewer  = full_info[u'user']['requested_by_viewer']
        user.has_blocked_viewer   = full_info[u'user']['has_blocked_viewer']
        user.blocked_by_viewer    = full_info[u'user']['blocked_by_viewer']
        user.is_private           = full_info[u'user']['is_private']

        user.save()

    return user

def create_relationship(user_id, followed_user_id):
    try:
        relationship = Relationship.objects.get(user_id          = user_id,
                                               followed_user_id = followed_user_id,
                                               )
        #logger.log('WORKER:get_follow_info: We already know this following rel %s %d ' % (full_info[u'user']['id'], self_user_id))

    except:
        logger.log('WORKER:get_follow_info: Create rel %s %s ' % (user_id, followed_user_id))
        relationship = Relationship(user_id          = user_id,
                                    followed_user_id = followed_user_id)

        relationship.save()



def get_user_from_database(user_id = None, user_name = None):
    try:
        if user_id:
            user = InstaUser.objects.get(user_id = user_id)
        elif user_name:
            user = InstaUser.objects.get(user_name = user_name)
    except:
        user = None
    return user


def get_users_from_database(params):

    followers_count__gte = params.get('followers_count__gte')
    followers_count__lte = params.get('followers_count__lte')
    follow_count__gte    = params.get('follow_count__gte')
    follow_count__lte    = params.get('follow_count__lte')
    follows_viewer       = params.get('follows_viewer')
    followed_by_viewer   = params.get('followed_by_viewer')
    order_by             = params.get('order_by')
    task_id              = params.get('task_id')
    followed_user        = params.get('followed_user')
    followed_by_user     = params.get('followed_by_user')

    queryset = InstaUser.objects.all()

    if followers_count__gte:
        queryset = queryset.filter(followers_count__gte=followers_count__gte)

    if followers_count__lte:
        queryset = queryset.filter(followers_count__lte=followers_count__lte)

    if follow_count__gte:
        queryset = queryset.filter(follow_count__gte=follow_count__gte)

    if follow_count__lte:
        queryset = queryset.filter(follow_count__lte=follow_count__lte)

    if follows_viewer:
        queryset = queryset.filter(follows_viewer=follows_viewer)

    if followed_by_viewer:
        queryset = queryset.filter(followed_by_viewer=followed_by_viewer)

    if task_id:
        user_ids = Task_to_user_map.objects.filter(task_id=task_id).values('user_id')
        queryset = InstaUser.objects.filter(user_id__in=user_ids)

    if followed_user:
        followers_ids = Relationship.objects.filter(followed_user_id=followed_user).values('user_id')
        queryset = InstaUser.objects.filter(user_id__in=followers_ids)

    if followed_by_user:
        following_ids = Relationship.objects.filter(user_id=followed_by_user).values('followed_user_id')
        queryset = InstaUser.objects.filter(user_id__in=following_ids)

    if order_by:
        queryset = queryset.order_by(order_by)

    return queryset


def get_task_from_database(id):
    task = InstaBotTask.objects.get(task_id = id)
    return task

def get_tasks_from_database(params):
    direction   = params.get('direction')
    username    = params.get('username')
    count       = params.get('count')
    count__gte  = params.get('count__gte')
    count__lte  = params.get('count__lte')
    create_time = params.get('create_time')

    tasks = Insta_bot_task.objects.all()

    if direction:
        tasks = tasks.filter(direction = direction)
    if username:
        tasks = tasks.filter(username = username)
    if count:
        tasks = tasks.filter(count = count)
    if count__gte:
        tasks = tasks.filter(count__gte = count__gte)
    if count__lte:
        tasks = tasks.filter(count__lte = count__lte)
    if create_time:
        tasks = tasks.filter(create_time = create_time)

    return tasks

def get_task_targets(params):
    return TaskTarget.objects.filter(**params)