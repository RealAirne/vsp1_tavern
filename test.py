import json
import socket
import requests
from requests.auth import HTTPBasicAuth

username = "Jaume"
password = "Jaume"

HEADER_APPL_JSON = {'content-type': 'application/json; charset=UTF-8'}

DISCOVERED_PORT = ""
BLACKBOARD_IP = ""
BLACKBOARD_URL = ""
JAUME_IP = ""


def find_jaume_at_tavern():
    profile_url = BLACKBOARD_URL + "taverna/adventurers/Jaume"
    jaume_profile_response = requests.get(url=profile_url, auth=HTTPBasicAuth(username=username, password=password))
    response_code = jaume_profile_response.status_code
    if response_code != 200:
        print("Sorry couldn't fetch the Profile of Jaume")
        print("The response was:")
        print(str(jaume_profile_response.json()))
        return None
    else:
        answer_json = jaume_profile_response.json()
        jaume_ip = answer_json['object']['url']
        return jaume_ip


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
    BLACKBOARD_URL = str(BLACKBOARD_IP) + ":" + str(DISCOVERED_PORT) + "/"
    print("adress: " + str(addr))
    print("blackboard_url: " + str(addr))

    global JAUME_IP
    JAUME_IP = find_jaume_at_tavern()


# {
#     "message": "Created Group",
#     "object": [
#         {
#             "_links": {
#                 "members": "/taverna/groups/55/members", TODO moegliche Verwechsungen!!
#                 "self": "/taverna/groups/55"
#             },
#             "id": 55,
#             "members": [],
#             "owner": "Jaume"
#         }
#     ],
#     "status": "success"
# }


def create_group():
    # in case of creating a group, data is empty. The hint was "watch the location header"...
    # data = ""
    group_url = "http://" + BLACKBOARD_URL + "taverna/groups"
    reply = requests.post(url=group_url, auth=HTTPBasicAuth(username=username, password=password))
    return reply


def extract_member_url(json_var):
    object_var = json_var['object'][0]
    links = object_var['_links']
    member_url = links['members']
    group_url = links['self']
    print(member_url)
    print(group_url)
    return member_url, group_url


def main():
    discovery()
    # Create a new group
    group_reply = create_group()
    group_status = group_reply.status_code
    print("group_status: " + str(group_status))

    # gather the information from the group_request to obtain the member_url and join it
    reply_as_json = group_reply.json()
    member_url, group_url = extract_member_url(reply_as_json)

    # TODO find Jaume and send him an invite (sending member_url), quest und message sind prototypen
    # TODO Tasks an die erstellte Gruppe verteilen und gelöste Quests entgegennehmen. Dort muessen dann die Token
    # TODO extrahiert und abgegeben werden (bei der Quest Anlaufstelle)

    # Take a quest

    hiring_data = {"group": member_url, "quest": "pi", "message": "many danks"}
    # hiring_data = '{"group":' + group_url + ', "quest": "pi", "message": "many danks"}'
    print(json.dumps(hiring_data))
    hiring_url = JAUME_IP + "/hirings"
    jaume_reply = requests.post(hiring_url, json.dumps(hiring_data), headers=HEADER_APPL_JSON)
    # jaume_reply = requests.post("http://172.19.0.81:80/hirings", json.dumps(hiring_data), headers=HEADER_APPL_JSON)
    jaume_status = jaume_reply.status_code
    jaume_text = jaume_reply.text
    print("Jaume Status: " + str(jaume_status))
    print(str(jaume_text))

    # Devide the quest into tasks and give all members an assignment
    # TODO /callback endpoint to receive tokens of the completed assignments


main()

# In order to test the application, post the following snippet of a Dockerfle into a real Dockerfile and upload it into
# (OwnCloud) vsp2_test/container, as well as the test.py - file

# FROM ubuntu:latest
# RUN apt-get update -y --fix-missing
# RUN apt-get install -y python3 python3-pip
# RUN pip3 install --upgrade pip
#
# #python3-dev build-essential
# COPY . /app
# WORKDIR /app
# RUN pip3 install requests
#
# # Make port 80 available to the world outside this container
# EXPOSE 80
#
# ENTRYPOINT ["python3"]
# CMD ["-u", "test.py"]
