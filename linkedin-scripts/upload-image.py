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
text = "Years ago, in a tech conference, a researcher asked: Isn't it embarrassing that the conference center urinals can detect when you're done and automatically flush, but your computer can't detect that you're not using it and automatically lock?\n\n \n\nThis seemingly simple problem is harder than it looks. People don't (normally) quietly stare at urinals for several minutes, but that can happen to computer screens (e.g., watching a movie or presentation, reading a document). \n\nNewer phones and tablets use eye tracking to save battery. They can figure out whether you're looking at a screen, and if you're not, lock. It works well, but these are devices that you almost always hold close to your face, so they can keep a camera pointing at you all the time. If you cover the camera or use an external monitor, you start having problems. With computers, I have a very strong preference for using external monitors, so I'm already in the problem situation to begin with. The solution could be to add a sensor to each monitor or camera, but given the thousands of models available, that could get complicated.\n\nDuring my long career, I've seen many pranks on people that left their computers unlocked. Some places look down at the person who left the computer unlocked, but I actually prefer the places that chastise the pranksters: instead of pranking, it would be better if they locked the computer and kindly had a word with the forgetful person.\n\nIn any case, one of my favorite Windows 11 features (apparently also present in Windows 10) is the ability to lock my computer automatically when I move away from it.\n\nThe way to do that is a little convoluted: you need to pair your Bluetooth phone with your computer (which, of course, also needs to have Bluetooth), and when your computer, using Bluetooth, detects that your phone moved away from your computer, it will automatically lock.\n\nFrom my description above, you probably already appreciate how a seemingly simple problem that we can solve for a urinal can be hard to solve even if your device has a lot more features. \n\nThe people who implemented the feature still couldn't solve all problems. What to do if the user doesn't have their phone today? Current solution: just show an error message. What to do if the user moves away but leaves the phone nearby? We detect phones, not users, so it will leave it unlocked.\n\nIn any case, I'm glad to see that computers of 2020s are inching closer to the toilets of the early 2000s.\n\nYou can see my older posts and more at my blog, at www-meyerperin-com ."  
text = text.replace("\n", "\\n")

code = post_linkedin_image(text, filepath)

if code == 201:
   print("Success")