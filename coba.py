room_name = "testRoom"
email = "ch@gmail.com"
conn = "12345"
username = "chris"

dictParticipantsInRoom = {}

dictParticipantsInRoom[room_name] = {}

dictParticipantsInRoom[room_name][email] = (
    conn, username)

dictUserDiRoom = dictParticipantsInRoom[room_name]

# messageResult = "Participants in room: \n"
# for currUsername in dictUserDiRoom.items():
#     # messageResult = messageResult + currUsername + "\n"
#     print(currUsername)

print(dictParticipantsInRoom[room_name].get("halo"))
