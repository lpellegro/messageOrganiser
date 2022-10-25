import base64

def base64Decode(roomId):

    base64_string = roomId
    base64_bytes = base64_string.encode("ascii")

    sample_string_bytes = base64.b64decode(base64_bytes)
    sample_string = sample_string_bytes.decode("ascii")

    print(f"Decoded string: {sample_string}")
    decodedRoomId = sample_string.split("/")[-1]
    link = f"webexteams://im?space={decodedRoomId}"
    print(link)
    return link

