from distutils.command.upload import upload
import requests
import json

def get_upload_url(token, person_id):

   headers = {
      "Authorization": f"Bearer {token}",
      "Content-Type": "application/json"
   }


   upload_json = """
   {
      "registerUploadRequest": {
         "recipes": [
               "urn:li:digitalmediaRecipe:feedshare-image"
         ],
         "owner": "PERSON_URN",
         "serviceRelationships": [
               {
                  "relationshipType": "OWNER",
                  "identifier": "urn:li:userGeneratedContent"
               }
         ]
      }
   }
   """

   upload_json = upload_json.replace("PERSON_URN", person_id)

   url = "https://api.linkedin.com/v2/assets?action=registerUpload"
   response = requests.post(url, upload_json, headers=headers)
   response_json = json.loads(response.text)
   upload_url = response_json.get("value").get("uploadMechanism").get("com.linkedin.digitalmedia.uploading.MediaUploadHttpRequest").get("uploadUrl")
   asset = response_json.get("value").get("asset")

   return asset, upload_url

def upload_image(filepath, upload_url, token):
   headers = {
      "Authorization": f"Bearer {token}"
   }

   resp = requests.put(upload_url, headers=headers, data=open(filepath,'rb').read())
   return resp.status_code


def post_asset(token, person_id, asset, text):
   headers = {
      "Authorization": f"Bearer {token}",
      "Content-Type": "application/json"
   }

   discard = """
   {
      "author": "PERSON_URN",
      "lifecycleState": "PUBLISHED",
      "specificContent": {
         "com.linkedin.ugc.ShareContent": {
               "shareCommentary": {
                  "text": "POST_TEXT"
               },
               "shareMediaCategory": "ARTICLE",
               "media": [
                  {
                     "status": "READY",
                     "description": {
                           "text": "Center stage!"
                     },
                     "media": "ASSET_URN",
                     "title": {
                           "text": "Where does the title go?"
                     }
                  }
               ]
         }
      },
      "visibility": {
         "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
      }
   }
   """

   post_json = """
   {
      "author": "PERSON_URN",
      "lifecycleState": "PUBLISHED",
      "specificContent": {
         "com.linkedin.ugc.ShareContent": {
               "shareCommentary": {
                  "text": "POST_TEXT"
               },
               "shareMediaCategory": "IMAGE",
               "media": [
                  {
                     "status": "READY",
                     "description": {
                           "text": "Center stage!"
                     },
                     "media": "ASSET_URN",
                     "title": {
                           "text": "Where does the title go?"
                     }
                  }

               ]
         }
      },
      "visibility": {
         "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
      }
   }
   """

   post_json = post_json.replace("PERSON_URN", person_id)
   post_json = post_json.replace("ASSET_URN", asset)
   post_json = post_json.replace("POST_TEXT", text)

   url = "https://api.linkedin.com/v2/ugcPosts"
   resp = requests.post(url, post_json, headers=headers)
   return resp.status_code


def post_linkedin_image(text, img_path):

   cfg_file = open("/home/lucasmeyer/.linkedin/config.json")
   li_cfg = json.load(cfg_file)

   person_id = li_cfg.get("urn")
   token = li_cfg.get("access_token")

   asset, upload_url = get_upload_url(token, person_id)

   resp_code = upload_image(filepath, upload_url, token)
   if resp_code == 201:
      resp_code = post_asset(token, person_id, asset, text)

   return(resp_code)

filepath = 'aiforgood.jpg'
text = "Sorry, this is just a test post. The tests should end soon, and maybe even redirect people to https://www.meyerperin.com/" 

text = text.replace("\n", "\\n")

code = post_linkedin_image(text, filepath)

if code == 201:
   print("Success")
else:
   print(code)