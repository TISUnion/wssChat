# -*- coding: utf-8 -*-


import websocket
import json
import ssl
import time

nickName = '创造服'
password = ''
serverUrl = ''

wssChatConnection = None
wssOpened = False;

def onServerStartup(server):
    wssConnection(server);

def processCommand(server, info):
    strs = info.content.split(' ');
    if(len(strs)==1):
        server.tell(info.player, "跨服聊天插件已安装");
        return;
    if(strs[1]=="help"):
        server.tell(info.player,"!!wss help 帮助界面");
        server.tell(info.player,"!!wss status 获得状态");
        server.tell(info.player,"!!wss ping ping其他服务器");
    elif(strs[1]=="status"):
        if(wssOpened):
            server.tell(info.player, "跨服聊天运行正常")
        else:
            server.tell(info.player, "跨服聊天已离线")
    elif(strs[1]=="ping"):
        wssChatConnection.send(json.dumps(
            {'action':'message', 'nickName':nickName, 'playerName':info.player, 'message':'', 'action2':'ping', 'src':nickName}
            ));

def onServerInfo(server, info):
    global wssChatTakeServer;
    if (info.isPlayer == 0):
        return
    if(info.content.startswith("!!")):
        if(info.content == "!!wss" or info.content.startswith("!!wss ")):
            processCommand(server, info);
        return
    else:
        wssChatConnection.send(json.dumps(
            {'action':'message', 'nickName':nickName, 'playerName':info.player, 'message':info.content}
            ));

def onPlayerJoin(server, player):
    wssChatConnection.send(json.dumps(
        {'action':'message', 'nickName':nickName, 'playerName':player, 'message':'h!!join', 'action2':'join'}
        ));

def onPlayerLeave(server, player):
    wssChatConnection.send(json.dumps(
        {'action': 'message', 'nickName': nickName, 'playerName': player, 'message': 'h!!leave', 'action2': 'leave'}
    ));

def login(nickNamel, password):
    wssChatConnection.send(json.dumps({'action':'login', 'nickName':nickNamel, 'password':password}));

def processMessage(server, data):
    # 浅处理unicode
    for key in data:
        # print(type(data[key]));
        if(type(data[key]).__name__=='unicode'):
            data[key] = data[key].encode('utf-8');
    if('action2' in data):
        if(data['action2'] == 'ping'):
            wssChatConnection.send(json.dumps(
                {'action': 'message', 'nickName': nickName, 'playerName': data['playerName'], 'message': '',
                 'action2': 'pong', 'dst':data['src']}
            ));
            return;
        elif(data['action2'] == 'pong'):
            if(data['dst']==nickName):
                server.tell(data['playerName'], "收到来自"+data['nickName']+"的回应");
            return;
        elif(data['action2'] == 'join'):
            msg = '['+data['nickName']+'] '+data['playerName']+'加入了'+data['nickName'];
            server.say(msg)
            return;
        elif(data['action2'] == 'leave'):
            msg = '['+data['nickName']+'] '+data['playerName']+'离开了'+data['nickName'];
            server.say(msg)
            return;
    if(data['message']==""):
        return;
    msg = '['+data['nickName']+'] <'+data['playerName']+'> '+data['message'];
    if(type(msg).__name__=='unicode'):
        msg = msg.encode('utf-8')
    if(__name__=="__main__"):
        print(msg);
    else:
        server.say(msg)

def wssConnection(server):
    global wssChatConnection;
    global wssOpened;
    while True:
        # if True:
        try:
            wssChatConnection = websocket.create_connection(serverUrl, sslopt={"cert_reqs": ssl.CERT_NONE})
            wssChatConnection.send(json.dumps({'action':'login', 'nickName':'lto server', 'password':password}))
            wssOpened=True;

            if (__name__ != "__main__"):
                server.say("跨服聊天已上线")
            else:
                print("跨服聊天已上线")
            while True:
                message = wssChatConnection.recv();

                # data = json.loads(message)
                # if (data['action'] == 'message'):
                #     processMessage(server, data);
                try:
                    data = json.loads(message)
                    if(data['action']=='message'):
                        processMessage(server, data);
                except:
                    print("[wsschat]处理通信数据失败： "+message)
                    continue;

        except Exception:
            if(wssOpened):
                wssOpened = False;
                if (__name__ != "__main__"):
                    server.say("跨服聊天已离线")
                else:
                    print("跨服聊天已离线")
            time.sleep(5);


if __name__ == "__main__":
    wssConnection(None);
