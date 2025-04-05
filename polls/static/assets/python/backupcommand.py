def execute_command(host, username, password, command):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(host, username=username, password=password, look_for_keys=False)
    stdin, stdout, stderr = client.exec_command(command)
    output = stdout.read().decode()
    client.close()
    return output

def send_command(request):
    if request.method == "POST":
        data = json.loads(request.body)
        command = data.get("command")
        server_id = data.get("server_id")

        try:
            server = Server.objects.get(id=server_id)
            output = execute_command(server.host, server.username, server.password, command)
            return JsonResponse({"output": output})
        except Server.DoesNotExist:
            return JsonResponse({"output": "Server not found."})
        except Exception as e:
            return JsonResponse({"output": f"Error: {str(e)}"})

    return JsonResponse({"output": "Invalid request."})