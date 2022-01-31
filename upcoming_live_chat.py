
import os
import time 
import regex as re 

import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors

scopes = ["https://www.googleapis.com/auth/youtube"]

#def main():
    # Disable OAuthlib's HTTPS verification when running locally.
    # *DO NOT* leave this option enabled in production.
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

#### API details

api_service_name = "youtube"
api_version = "v3"
client_secrets_file = "client_secrets_desktop.json"


#### filter function

prohibited_words = ['(c+o+v+i+d+)',"(t+e+s+t+)","🐔"]

def filter(message,*args):
    result = True
    for word in prohibited_words:
        if re.search(word,message) != None:
            print(word)
            print('prohibited word used')
            result = False
            break
    return result






def getLiveChat():
    # Get credentials and create an API client

    flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
        client_secrets_file, scopes)
    credentials = flow.run_console()
    youtube = googleapiclient.discovery.build(
        api_service_name, api_version, credentials=credentials)


    # retrieve list of upcoming broadcasts
    request = youtube.liveBroadcasts().list(
        part="snippet",
        broadcastStatus="upcoming"
    )
    broadcastUpcomingResponse = request.execute()

    #get livechat stream
    if len(broadcastUpcomingResponse['items'])!=0:
            broadcast = broadcastUpcomingResponse['items'][0]
            broadcastID = broadcast['id']
            upcomingLC = broadcast['snippet']['liveChatId']
            print('**********')
            print('upcomingbroadcastID',broadcastID,'upcomingbroadcastLC ID',upcomingLC)

            return youtube,upcomingLC
        #return livechatID

        #filter data with callback

def livechatFilter(youtube,upcomingLC,nextpagetoken=None):
    if nextpagetoken:
        livechatrequest = youtube.liveChatMessages().list(
        part='snippet',
        liveChatId=upcomingLC,
        pageToken=nextpagetoken
                            )
        livechatresponse = livechatrequest.execute()
    else:
        livechatrequest = youtube.liveChatMessages().list(
        part='snippet',
        liveChatId=upcomingLC,
                            )
        livechatresponse = livechatrequest.execute()
    #print(livechatresponse)
    #print('upcoming broadcast messages')
    nextpagetoken = livechatresponse.get('nextPageToken','')
    for item in livechatresponse['items']:
        message = item['snippet']['textMessageDetails']['messageText']
        messageID = item['id']
        #print(message,messageID)
        #filter message and send delete request
        if filter(message,prohibited_words) != True:
            try:
                deleteRequest = youtube.liveChatMessages().delete(
                                                                id=messageID
                                                            )
                deleteRequest.execute()
                print('deleted', message)
            except Exception as e:
                print(e, 'something went wrong')
            
        else:
            print('pass')

    if nextpagetoken:
        print('Active')
        time.sleep(5)
        livechatFilter(youtube,upcomingLC,nextpagetoken=nextpagetoken)
    else:
        print('Done')

if __name__ == "__main__":
    youtube, upcomingLC = getLiveChat()
    livechatFilter(youtube,upcomingLC)