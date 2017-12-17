from flask import Flask, request, make_response, g
import json
import requests
import socket
import threading
import netifaces as ni
from requests.auth import HTTPBasicAuth
from requests.exceptions import ConnectionError, MissingSchema, InvalidURL

app = Flask(__name__)

HEADER_APPL_JSON = {'content-type': 'application/json; charset=UTF-8'}

TIMEOUTVALUE = 0.01

# Vergleiche Vorlesungsfolien ("Zeit und logische Uhren", Seite 56)
# TODO: g als global Variable über Threads hinweg?
LAMPORTCLOCK = 1

RELEASED = "released"
WANTING = "wanting"
HELD = "held"

STATE = WANTING

REQUEST = "request"
REPLYOK = "reply-ok"

REPLYOKCOUNT = 0

DISCOVERED_PORT = ""
BLACKBOARD_IP = ""
BLACKBOARD_URL_NO_TRAIL = ""
BLACKBOARD_URL = ""
DISCOVERED_IP = ""

# A global variable to manage the hirings
HIRINGS = []
LIMIT_OF_HIRINGS = 1
member1 = {'name': 'Arne', 'url': 'http://0.0.0.1/election'}
member2 = {'name': 'Jerom', 'url': 'http://172.19.0.79:80/election'}
selfmember = {'name': 'HeroService', 'url': 'http://0.0.0.0:8000/mutex'}
GROUP_MEMBERS = [member1, member2]
SELF_GROUP_MEMBER = [selfmember]

# userdata_user = "'user': '/users/Jaume',"
# userdata_idle = "'idle': False,"
# userdata_group = "'group': None,"
# userdata_hirings = "'hirings': '/hirings',"
# userdata_assignments = "'assignments': 'assignments',"
# userdata_messages = "'messages': '/messages'"
#
# userdata = {
# userdata_user + userdata_idle + userdata_group + userdata_hirings + userdata_assignments + userdata_messages}


userdata = {'user': 'link to the registered user account',
            'idle': False,
            'group': 'url to the group you are in',
            'hirings': 'uri to which one may post to hire you for a group',
            'assignments': 'uri to which one may post an assignment',
            'messages': 'ri to which one may post messages'
            }


# TODO: Daten
def create_algorithmdata(payload_string):
    return {
        "algorithm": "bully",
        "payload": "" + payload_string,
        "user": "http://172.19.0.3:5000/taverna/adventurers",
        "job": "JSON description of the job to do",
        "message": "something you want to tell the other one"
    }


# def get_login_token(user, passw):
#   response = requests.get(url=DISCOVERED_IP + '/login', auth=HTTPBasicAuth(user, passw))
#  print(response.content)
# token = response.json()['token']
# return token


# GET returns
@app.route('/')
def hello_world():
    json.dumps(userdata)
    return json.dumps(userdata)


def join_group(group_url):
    print(group_url)
    try:
        requests.get(group_url, timeout=0.1)
    except (ConnectionError, MissingSchema, InvalidURL) as ex:
        print(ex)
        print("THE URL " + group_url + "IS INVALID!!!")
        return make_response("The URL given ( " + group_url + " ) is not specified well!", 400)
    reply = requests.post(group_url)
    status = reply.status_code
    print("The status of joining the group was " + str(status))


def check_hiring_data(request_data):
    # Are the keys given correct?
    group = request_data['group']
    print("group: " + str(group))
    quest = request_data['quest']
    print("quest: " + str(quest))
    message = request_data['message']
    print("message: " + str(message))
    # how many keys are there? > 3 raises an ERROR (caught in post_hiring())
    amount_of_keys = len(dict(request_data).keys())
    if amount_of_keys > 3:
        raise KeyError


def check_assignment_data(request_data):
    # Are the keys given correct?
    id = request_data['id']
    task = request_data['task']
    resource = request_data['resource']
    method = request_data['method']
    data = request_data['data']
    callback = request_data['callback']
    message = request_data['message']
    # how many keys are there? > 7 raises an ERROR (caught in post_hiring())
    amount_of_keys = len(dict(request_data).keys())
    if amount_of_keys > 7:
        raise KeyError


def not_allowed_response():
    print("There is only a POST allowed here.")
    not_allowed_response = make_response(405)
    return not_allowed_response


def bad_request_response(keys_needed):
    bad_request_response = make_response("The body needs to exactly contain the following keys: " + keys_needed, 400)
    return bad_request_response


def incorrect_payload_response():
    print("Payload is not any of those: election, answer, coordinator")
    incorrect_payload_response = make_response("Payload is not any of those: election, answer, coordinator", 405)
    return incorrect_payload_response


@app.route('/hirings', methods=['POST'])
def hiring_endpoint():
    if request.method == 'POST':
        # check wether the hero is busy (length of HIRINGS)
        amount_of_hirings = len(HIRINGS)
        print("Amount of hirings:" + str(amount_of_hirings))
        if amount_of_hirings > LIMIT_OF_HIRINGS:
            print("oO too busy!!")
            # if the hero is busy, he responds with 423-locked HTTP-Code
            too_busy_response = make_response("Sorry, I am busy", 423)
            return too_busy_response

        # Todo string und json beidermassen verarbeiten (?)
        request_data = request.json
        print(str(request_data))

        try:
            check_hiring_data(request_data)

        except KeyError:
            return bad_request_response("group, quest, message")

        print("check completed!")
        url_to_join = "http://" + str(BLACKBOARD_URL_NO_TRAIL) + request_data['group']
        print(url_to_join)
        joined_group = join_group(url_to_join)
        if joined_group is not None:
            return joined_group
        print("joined group")
        # HIRINGS are stored as dicts
        list.append(HIRINGS, request_data)
        print("actual value of HIRINGS: " + str(HIRINGS))
        response = make_response("Hiring posted successfully, joined the group!", 200)
        return response
    else:
        return not_allowed_response()


# TODO only can perform tasks, if the method is already known --> Add Regex to filter operation at the quest-loc
# TODO how about authentication?
def take_task_and_perform(assignment_dict):
    task_uri = assignment_dict['task']
    resource = assignment_dict['resource']
    method = assignment_dict['method']
    data = assignment_dict['data']

    # TODO wie sieht eine resource aus? Annahme vollstaendige URL
    if method in ['post', 'POST', 'Post', 'pOst', 'poSt', 'posT']:
        post_request = requests.post(resource, data)
        return ['post', post_request]

    elif method in ['get', 'Get', 'GET', 'gEt', 'geT', 'GEt', 'gET', 'GeT']:
        get_request = requests.get(resource)
        return ['get', get_request]

    elif method in ['put', 'Put', 'PUT']:
        put_request = requests.put(resource, data)
        return ['put', put_request]

    elif method in ['delete', 'DELETE', 'del', 'remove', 'rm']:
        delete_request = requests.delete(resource)
        return ['delete', delete_request]


def assemble_json_answer(id, task, resource, method, data, user, message):
    dictionary = {'id': id, 'task': task, 'resource': resource, 'method': method, 'data': data, 'user': user,
                  'message': message}
    return json.dumps(dictionary)


@app.route('/assignments', methods=['POST'])
def assignment_endpoint():
    if request.method == 'POST':
        request_data = request.data
        try:
            check_assignment_data(request_data)
        except KeyError:
            return bad_request_response("id, task, resource, method, data, callback, message")

        received_id = request_data['id']
        task = request_data['task']
        resource = request_data['resource']
        callback = request_data['callback']
        message_text = "Ye boiii, we did it!"

        # After pre-checks are completed, the hero can take the task
        method_used, reply = take_task_and_perform(request_data)
        status = reply.status_code
        # Was the quest succesful?
        if status in range(start=200, stop=299, step=1):
            jaume = BLACKBOARD_URL + 'users/Jaume'
            answer = assemble_json_answer(received_id, task, resource, method_used, reply, jaume, message_text)
            requests.post(callback, answer)

            # TODO was passiert, wenn wir eine Quest nicht abschliessen koenen?
            # Produktiv selbst herausfinden, wie eine Task zu loesen ist.
            # TODO

    else:
        return not_allowed_response()


def get_ip():
    ni.ifaddresses('eth0')
    ip = ni.ifaddresses('eth0')[ni.AF_INET][0]['addr']
    return ip


# POST delivers heroclass, capabilities, url
def register_at_tavern():
    print("register at tavern:")
    ip = get_ip()
    url = ip + '/'
    json_data = {'heroclass': 'Catalonian Chiller', 'capabilities': '', 'url': '' + url}
    taverna_url = BLACKBOARD_URL + 'taverna/adventurers'
    response = requests.post(url=taverna_url, headers=HEADER_APPL_JSON, json=json_data,
                             auth=HTTPBasicAuth("Jaume", "Jaume"))
    print("response (register at tavern)" + repr(response.status_code))
    print("hello")


def discovery():
    UDP_IP = ''
    UDP_PORT = 24000

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((UDP_IP, UDP_PORT))
    # working = True
    buffersize = 1024
    # while working:
    data, addr = sock.recvfrom(buffersize)  # buffer size is 1024 bytes
    print("received message:" + str(data))  # addr ist die discvory address

    port = json.loads(data.decode())

    discovered_port = port['blackboard_port']

    sourceip, sourceport = addr

    blackboard_ip = sourceip

    # assemble the whole blackboard URL with port and trailing "/"

    blackboard_url_no_trail = str(blackboard_ip) + ":" + str(discovered_port)

    blackboard_url = str(blackboard_url_no_trail) + "/"

    print("adress: " + str(addr))

    return [discovered_port, blackboard_ip, blackboard_url_no_trail, blackboard_url]


# ####################Bully Algorithm########################

def bully():
    print('started bully')
    try:
        print('sending election 281')
        send_election()
    except ValueError:
        print('sending coordinator')
        send_coordinator()
    print('ended election')


def find_members_with_higher_id():
    stronger_members = []
    print('finding stronger members')
    for member in GROUP_MEMBERS:
        if (member['name'] > 'Jaume'):
            stronger_members.append(member)
    if not stronger_members:
        raise ValueError('No higher Members found')
    return stronger_members


def send_coordinator():
    for member in GROUP_MEMBERS:
        payload = create_algorithmdata('coordinator')
        try:
            print('sending coordinator to' + member['url'])
            requests.post(member['url'], json.dumps(payload), headers=HEADER_APPL_JSON, timeout=TIMEOUTVALUE)
        except:
            print('could not send coordinator')
            pass


def send_election():
    # Throws ValueError
    members_to_consult = find_members_with_higher_id()
    nobody_reached = True
    for member in members_to_consult:
        print('Member to consult:')
        print(member['url'])
        payload = create_algorithmdata('election')
        try:
            print('trying to contact member')
            urlstring = str(member['url'])
            response = requests.post(urlstring, data=json.dumps(payload), headers=HEADER_APPL_JSON,
                                     timeout=TIMEOUTVALUE)

            print('reached someone')

            string_response = (str(response.text))
            cleaned_string = string_response.replace("\'", "\"")
            json_object = json.loads(cleaned_string)
            print(json_object)
            if json_object['payload'] == 'answer':
                nobody_reached = False
        except:
            print('could not reach member')
    if nobody_reached:
        print('nobody reached')
        raise ValueError('Nobody reached')


## handles start of bully AFTER sending 'answer'
def after_this_request(func):
    if not hasattr(g, 'call_after_request'):
        g.call_after_request = []
    g.call_after_request.append(func)
    return func


@app.after_request
def per_request_callbacks(response):
    for func in getattr(g, 'call_after_request', ()):
        response = func(response)
    return response


@app.route('/election', methods=['POST'])
def election():
    data = request.json
    print(data['payload'])
    payload = data['payload']
    if 'election' == payload:
        print('Got election, starting own bully algorithm and responding with answer')
        algorithmdata = str(create_algorithmdata('answer'))

        @after_this_request
        def start_bully(response):
            bully()
            return response

        print("before bully send response")
        return make_response(algorithmdata, 200)
    elif 'answer' == payload:
        print('Got Answer')
        return make_response("OK", 200)
    elif 'coordinator' == payload:
        print('Got coordinator, obey the leader')
        return make_response("obeying", 200)
    else:
        return incorrect_payload_response()


##################### Distributed Mutex ############################

# TODO: waits for answer, no timeout
class SendRequestThread(threading.Thread):
    def __init__(self, *args):
        threading.Thread.__init__(self)
        self.args = args

    def run(self):
        print('Thread started')
        member = self.args[0]
        url = member['url']
        payload = create_payload(REQUEST)
        print("sending to member!: " + url)
        print("with payload" + payload)
        requests.post(url, headers=HEADER_APPL_JSON, json=payload)
        print("ending thread")


@app.route('/mutex', methods=['POST'])
def mutex():
    response = None
    # Before calculating calculate Lamportclock
    print("REQUEST IS" + str(request))
    data = request.json
    print('data: ' + str(data))
    othersLamport = data['time']
    calculateNewLamport(othersLamport)
    print("currentLamport = " + str(LAMPORTCLOCK))

    message = data['message']
    print("439 Message is" + message)
    if message == REPLYOK:
        if STATE == WANTING:
            global REPLYOKCOUNT
            REPLYOKCOUNT += 1
            # TODO: Change to GROUP_MEMBER
            if REPLYOKCOUNT >= len(SELF_GROUP_MEMBER):
                claim_mutex_if_save()
            response = make_response("OK", 200)
        else:
            response = make_response("OK", 200)
            pass
    elif message == REQUEST:
        if STATE == RELEASED:
            print("Message is request && State is Released")
            payload = create_payload(REPLYOK)
            response = make_response(payload, 200)

        elif STATE == HELD:
            store_request()

        elif STATE == WANTING:
            if othersLamport > LAMPORTCLOCK:
                store_request()
            else:
                payload = create_payload(REPLYOK)
                response = make_response(payload, 200)
        pass

    # before answer, increase lamport (for answer)
    increaseLamport()
    return response


# TODO: change arguments in calling methods
def store_request():
    pass


def claim_mutex_if_save():
    # TODO: Claim Mutex, do whatever you like
    # TODO: Release Mutex
    # TODO: change state to Released!
    print("CLAIM THE MUTEX!")
    pass


@app.route('/testmutex', methods=['GET'])
def testmutex():
    request_mutex()
    return 'OK'


# Only tells Mutexstate, but also affects lamport-clock
@app.route('/mutexstate', methods=['GET'])
def mutexstate():
    jsonResponse = json.dumps({'state': STATE, 'time': LAMPORTCLOCK})
    return make_response(jsonResponse, 200)


def increaseLamport():
    global LAMPORTCLOCK
    LAMPORTCLOCK += 1
    print("LamportClock increased: " + str(LAMPORTCLOCK))


def calculateNewLamport(othersLamport):
    global LAMPORTCLOCK
    newLamport = max([LAMPORTCLOCK, othersLamport]) + 1
    LAMPORTCLOCK = newLamport
    print("LamportClock calculated: " + str(LAMPORTCLOCK))


def request_mutex():
    # TODO: auslagern in 3 Threads, jeder Thread wartet auf ok und feuert dann signal zum betreten
    # TODO: koennte mit threaded = true kollidieren
    if not STATE == HELD:
        print("487, requesting mutex")
        change_state(WANTING)
        for member in SELF_GROUP_MEMBER:
            print('trying to start thread')
            thread = SendRequestThread(member).start()
    pass


def create_payload(request):
    # TODO: Eigene ip einkommentieren
    # payload = json.dumps({'message': 'request', 'url': url, 'reply': get_ip() + '/mutex'})
    payload = json.dumps({'message': request, 'time': LAMPORTCLOCK, 'reply': 'http://0.0.0.0:8000/mutex'})
    return payload


# TODO: If changes state to Released from Held, send first in qaiting queue request ok
def change_state(state):
    if not STATE == HELD:
        STATE == state


def main():
    print("Here we go, it's Adventure-Time!")
    # discovered_port, blackboard_ip, blackboard_url_no_trail, blackboard_url
    # global DISCOVERED_PORT
    # global BLACKBOARD_IP
    # global BLACKBOARD_URL_NO_TRAIL
    # global BLACKBOARD_URL
    # DISCOVERED_PORT, BLACKBOARD_IP, BLACKBOARD_URL_NO_TRAIL, BLACKBOARD_URL = discovery()
    #
    # global DISCOVERED_IP
    # DISCOVERED_IP = 'http://' + str(BLACKBOARD_IP) + ':' + str(DISCOVERED_PORT)
    #
    # print("Discovered_IP: " + DISCOVERED_IP)
    # print("Discovered_Port: " + str(DISCOVERED_PORT))
    # print("Blackboard_IP: " + BLACKBOARD_IP)
    # print("Blackboard_URL: " + BLACKBOARD_URL)
    # print("Blackboard_no_trail: " + BLACKBOARD_URL_NO_TRAIL)
    # register_at_tavern()
    # bully()
    # request_mutex()


main()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000, threaded=True)
