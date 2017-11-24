from flask import Flask, request, make_response
import json
import requests
import socket
from requests.auth import HTTPBasicAuth

app = Flask(__name__)

HEADER_APPL_JSON = {'content-type': 'application/json; charset=UTF-8'}

# A global variable to manage the hirings
HIRINGS = []
LIMIT_OF_HIRINGS = 1
GROUP_MEMBERS = [{'name': 'Arne', 'url': 'url'}, {'name': 'Jerom', 'url': 'url'}]

# TODO do a research on how to use URIs (or what's meant here)
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
    requests.post(group_url)


def check_hiring_data(request_data):
    # Are the keys given correct?
    group = request_data['group']
    quest = request_data['quest']
    message = request_data['message']
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


@app.route('/hirings', methods=['POST'])
def hiring_endpoint():
    if request.method == 'POST':
        # check wether the hero is busy (length of HIRINGS)
        amount_of_hirings = len(HIRINGS)
        if amount_of_hirings >= LIMIT_OF_HIRINGS:
            # if the hero is busy, he responds with 423-locked HTTP-Code
            too_busy_response = make_response("Sorry, I am busy", 423)
            return too_busy_response

        request_data = json.loads(request.data)

        try:
            check_hiring_data(request_data)

        except KeyError:
            return bad_request_response("group, quest, message")

        join_group(request_data['group'])

        # HIRINGS are stored as dicts
        list.append(HIRINGS, request_data)
        print("actual value of HIRINGS: " + str(HIRINGS))
        response = make_response("Hiring posted successfully, joined the group!", 200)
        return response
    else:
        return not_allowed_response()


# TODO only can perform tasks, if the method is already known
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

    else:
        return not_allowed_response()


# TODO dynamic IP
def get_ip():
    return 'http://172.19.0.63:80'


# POST delivers heroclass, capabilities, url
def register_at_tavern():
    print("register at tavern:")
    ip = get_ip()
    # TODO endpoint jaume erstellen
    # TODO IP eintragen in /users/Jaume
    url = ip + '/'
    json_data = {'heroclass': 'Catalonian Chiller', 'capabilities': '', 'url': '' + url}
    taverna_url = 'http://172.19.0.3:5000/taverna/adventurers'
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

    global DISCOVERED_PORT
    DISCOVERED_PORT = port['blackboard_port']

    sourceip, sourceport = addr

    global BLACKBOARD_IP
    BLACKBOARD_IP = sourceip

    # assemble the whole blackboard URL with port and trailing "/"
    global BLACKBOARD_URL
    BLACKBOARD_URL = BLACKBOARD_IP + ":" + DISCOVERED_PORT + "/"
    print("adress: " + str(addr))


def create_group():
    # in case of creating a group, data is empty. The hint was "watch the location header"... TODO investigate that!
    data = ""
    requests.post(BLACKBOARD_URL, data)

    #####################Bully Algorithm########################


def bully():
    send_election()


def send_election():
    # TODO: throw exception if there are no bigger ones or if nobody is answering
    for member in GROUP_MEMBERS:
        if (member['name'] > 'Jaume'):
            # TODO: Send
            print(member['name'])


            # response = requests.post("http://0.0.0.0:80/election", {'payload': 'election'})


@app.route('/election', methods=['POST'])
def election():
    data = json.loads(request.data)
    payload = data['payload']
    if payload == 'election':
        return payload


# @app.route('/hirings', methods=['POST'])
#     def post_hiring():
#         if request.method == 'POST':
#             request_data = json.loads(request.data)
#             try:
#                 check_hiring_data(request_data)
#
#             except KeyError:
#                 bad_request_response = make_response(
#                     "The body needs to exactly contain the following keys: group, quest, "
#                     "message", 400)
#                 return bad_request_response
#             # HIRINGS are stored as dicts
#             list.append(HIRINGS, request_data)
#             print("actual value of HIRINGS: " + str(HIRINGS))
#             response = make_response("Hiring posted successfully", 200)
#             return response
#         else:
#             print("There is only a POST allowed here.")
#             not_allowed_response = make_response(405)
#             return not_allowed_response


def main():
    print("HEJEHEHEHEJEHEJEH")
    # discovery()
    # global DISCOVERED_IP
    # DISCOVERED_IP = 'http://' + str(BLACKBOARD_IP) + ':' + str(DISCOVERED_PORT)
    # print(DISCOVERED_IP)
    # register_at_tavern()
    # bully()


main()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=80)
