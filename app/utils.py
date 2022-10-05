from flask import current_app, render_template, url_for
from app import db
from app.models import (
    Post,
    Group,
    User,
    Hide,
    Vote,
    Favourite,
    Member,
    Flag
)

from urllib.parse import urlparse
from datetime import datetime, timedelta

from requests import post
import os
from app.custom_encrypt import *
from string import punctuation
import json
from collections import Counter

APP_ROOT = os.path.dirname(os.path.abspath(__file__))


class Index(object):
    
    def __init__(self):
        global APP_ROOT        
        self.json = {"ids":[],"index":{}}
        # list(stopwords.words('english')) 
        self.stop_words = list(punctuation)
        self.index_file = os.path.join(APP_ROOT, f"index.json")
        
        self.dict = {}
        
        if os.path.exists(self.index_file):
            with open(self.index_file,"r",encoding='utf-8', errors='ignore') as f:
                try:
                    self.json = json.load(f)  
                except json.decoder.JSONDecodeError as err:
                    pass
        else:
            with open(self.index_file,"w") as f:
                json.dump({"ids":[],"index":{}}, f, indent=4)
        
        self.add_to_dict()
        
    def add_to_dict(self,):
        for key in self.json["index"].keys():
            useable_key = key
            if useable_key.startswith('"') or \
                useable_key.startswith('(') or \
                useable_key.startswith('['):
                    
                useable_key = useable_key[1:]
            if useable_key.endswith('"') or \
                useable_key.endswith(')') or \
                useable_key.endswith(']'):
                useable_key = useable_key[:-1]
                
            char = useable_key[0]
            
            if char not in self.dict:
                self.dict[char] = []
            
            if key not in self.dict[char]:
                self.dict[char].append(key)
        
    def add_to_index(self,corpus):
        added = False
        for item in corpus:
            _id = item[1]
            if _id not in self.json["ids"]:
                keywords = [x.strip() for x in dc(item[0]).lower().split()]
                
                for keyword in keywords:
                    if keyword not in self.json["index"]:
                        self.json["index"][keyword] = []
                    
                    if _id not in self.json["index"][keyword]:
                        added = True
                        self.json["index"][keyword].append(_id)
                    
                    if _id not in self.json["ids"]:
                        added = True
                        self.json["ids"].append(_id)
        
        if added:
            self.add_to_dict()
            self.save()
        
    def get_related(self,keywords):
        ret = []
        for keyword in keywords:
            if keyword[0] in self.dict:
                m_relate = self.dict[keyword[0]]
                
                for x in m_relate:
                    if x.startswith(keyword):
                        ret.append(x)
        return list(set(ret))
        
    def search(self,query):
        keywords = list(set([x.strip() for x in dc(query).lower().split()]))

        keywords += self.get_related(keywords)
        
        docs = []
        for keyword in keywords:
            if keyword in self.json["index"]:
                docs += self.json["index"][keyword]
        
        counter = Counter(docs)
        items = counter.items()
        sorted_items = sorted(items,key=lambda x: x[1], reverse=True)
        return [x[0] for x in sorted_items]
    
    def load(self):
        with open(self.index_file,"r",encoding='utf-8', errors='ignore') as f:
            self.json = json.load(f)  
    
    def save(self):
        with open(self.index_file,"w") as f:
            json.dump(self.json, f,indent=4)   
            


def dc(s):
    return str(s).encode('ascii', 'ignore').decode('ascii')    

def ghv(post_id,user_id,h=True,f=False):
    vote = Vote.query.filter_by(post_id=post_id,user_id=user_id).first()
    hide,fave = None,None
    if h:
        hide = Hide.query.filter_by(post_id=post_id,user_id=user_id).first()
    if f:
        fave = Favourite.query.filter_by(post_id=post_id,user_id=user_id).first()
        flag = Flag.query.filter_by(post_id=post_id,user_id=user_id).first()
    return (vote,hide,fave,flag)

def is_mem(group_id,user_id):
    member = Member.query.filter_by(group_id=group_id,user_id=user_id).first()
    return member


def get_comments(post):
    post_id = post.id
    comments = Post.query.filter(Post.path.startswith(f"{post.path}{post.id}/")).all()
    comments.sort(key=lambda x: x.parent_id)
    comments = sort_comments(comments)
    return (comments,len(comments))


def get_path_sum(path):
    out = 0
    dirs = path.split("/")
    for x in dirs:
        try:
            out += int(x)
        except Exception as err:
            print(err)
            print("FROM GET_PATH_SUM")
    
    return out

def flatten(l):
    out = []
    for x in l:
        if type(x) == list:
            out += flatten(x)
        else:
            out.append(x)
    return out

def get_children(parent,comments,used = []):
    out = []
    used.append(parent)
    for x in comments:
        if x not in used:
            if x.parent_id == parent.id:
                g = get_children(x,comments,used)
                out.append(x)
                out += g
    return out

def sort_comments(comments):
    out = []
    used = []
    for x in comments:
        if x not in used:
            children = get_children(x,comments,used)
            out += [x] + children
        used.append(x)
    return out

def _get_indent(path):
    dirs = path.split("/")
    ind = 0
    for x in dirs:
        if x:
            ind += 1
    
    return (ind-1) * 40 if ind > 1 else 0

def get_indent(path,parent_path=None):
    ind = _get_indent(path)
    if parent_path:
        p_ind = _get_indent(parent_path)  
        return ind - p_ind
    return ind

def get_url_base(url):
    url = urlparse(url)
    return str(url.netloc)

def is_admin(user):
    if user:
        if hasattr(user,'username'):
            return user.username in ["keosariel"]
    return False

def add_posts():
    posts = [
        "Healthcare capitalism is trying to kill sick people",
        "I clean pools and run into lots of dogs. This older gentleman is always trying to show off to me even though his body is aging. I don’t even know his name, but he made my day.",
        "Pope Francis takes aim at anti-mask protestors: ‘They are incapable of moving outside of their own little world’",
        "City of El Paso hires legal counsel to help collect Trump campaign’s outstanding debt",
        "Poll: 60 percent support Biden canceling up to $50K of student loan debt per person ",
        "Jailers Interrupt Ghislaine Maxwell's Sleep Every 15 Minutes to Check If She's Still Breathing, Lawyer Says",
        "29M After 11 years of getting ripped on in the military it's impossible to hurt my feelings. Prove me wrong",
        "Elon Musk’s partner, Grimes, receives a $90,000 Canadian arts grant while living in California with the world second richest person",
        "My kitten Charlie loves the laundry hamper. He’ll meow and whine until you put upside down so he can become a kitty roomba.",
        "Do you forget your own age sometimes ?",
        "It's not painted. It took me 8 months to make this portrait from thread and nails.",
        "Received PS5 yesterday. Instead of playing games like a normal person, spent most of the day mask-taping and airbrushing it... Love the result though!",
        "Apple cuts its App Store commission from 30% to 15% — if your apps earn less than $1M",
        "Parsing Algorithms",
        "Apache Helix – Near-Realtime Rsync Replicated File System",
        "Twitter still hasn't unlocked the New York Post's account",
        "Vaccine hopes rise as Oxford jab prompts immune response among old and young",
        "Show HN: Dendron – A Hierarchical Tool for Thought",
        "No Implants Needed for Precise Control Deep into the Brain",
        "Surviving Disillusionment",
        "The Most Surveilled Cities in the World",
        "Show HN: Personal CRM: Note taking, the way it should be",
        "Unexpected, Useless, and Urgent, or What RSS Gets Right",
        "The Chaos Engineering Book",
        "25 Years In Speech Technology and I still don’t talk to my computer",
        "Why I'm Tcl-Ish",
        "UEFI-rs: Write UEFI applications in Rust",
        "Culture wars are fought by tiny minority – UK study",
        "Fastly hires entire Wasmtime team from Mozilla",
        "Rethinking Attention with Performers",
        "iPhone 12 Pro Camera Review",
        "We chose Java for our high-frequency trading application",
        "Bytecode Alliance: One year update",
        "NASA’s Sofia Discovers Water on Sunlit Surface of Moon",
        "CBP Refuses to Tell Congress How It Is Tracking Americans Without a Warrant",
        "The Physicist’s New Book of Life",
        "Digital Camera Know-Hows",
        "Otvdm/winevdm: run old Windows software in 64-bit Windows",
        "Mental model to deliver high quality software",
        "Church patriarch dies from Covid-19 after leading open-casket funeral of bishop killed by the virus",
        "Latinas for Trump founder unseated Florida Democrat after ‘shadow candidate’ with his surname entered the  race",
        "I saw my friend today a year after she got out of her relationship. When I saw her hair I had to hold back the tears.",
        "‘Knives Out’ Exposes the Veiled Prejudice of Seemingly Nice People",
        "There are sidewalks in the Cars movies but they are all cars",
        "Received PS5 yesterday. Instead of playing games like a normal person, spent most of the day mask-taping and airbrushing it... Love the result though!"
    ]
    url = "https://www.theguardian.com/society/2020/oct/24/culture-wars-are-fought-by-tiny-minority-uk-study"
    url_base = get_url_base(url)
    for x in posts:
        post = Post(
            title=x,
            url=url,
            url_base=url_base,
            body="",
            user_id=1,
            parent_id=0,
            main_parent_id=0,
            path="/",
            group_id = 1
        )
        db.session.add(post)
    db.session.commit()
    
def get_groups():
    groups = Group.query.all()
    return groups


def get_sec_diff_str(date):
    if date is None:
        return

    diff = datetime.utcnow() - date
    if diff.days > 14 or diff.days < 0:
        return date.strftime('%a %b %d, %y')        
    elif diff.days == 1:
        return '1 day ago'
    elif diff.days > 1:
        return '{0} days ago'.format(diff.days)
    elif diff.seconds <= 1:
        return 'just now'
    elif diff.seconds < 60:
        return '{0} seconds ago'.format(diff.seconds)
    elif diff.seconds < 120:
        return '1 minute ago'
    elif diff.seconds < 3600:
        return '{0} minutes ago'.format(diff.seconds // 60)
    elif diff.seconds < 7200:
        return '1 hour ago'
    else:
        return '{0} hours ago'.format(diff.seconds // 3600)

def get_post(post_id):
    post = Post.query.get(post_id)
    if post:
        return post
    return None

def send_reset_email(user):
    token = user.get_reset_password_token()
    user_email = user.email
    msg = f'''Forgot your password?
        It happens to the best of us. The good news is you can change it right now.

        To reset your password, visit the following link:
        {url_for('auth.reset_password', token=token, _external=True)}

        If you didn’t request a password reset, you don’t have to do anything.
        Just ignore this email.
    '''
    #print(dc(msg))
    try:
        _sent = post(
            "https://api.mailgun.net/v3/sandboxb8374109d6604f9292316c615c30a4cf.mailgun.org/messages",
            auth=("api", current_app.config["MAILGUN_KEY"] ),
            data={"from": "Nairagazer <noreply@nairagazer.com>",
                "to": [f"{user_email}"],
                "subject": "Request Password Reset,",
                "text": msg})
        print(_sent)
        return True
    except Exception as err:
        print('###########################3')
        print(err)
        print('Error sending mail')
        print('################################')

    return False

