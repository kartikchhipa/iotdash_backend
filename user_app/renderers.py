from rest_framework import renderers
import json

class UserRenderer(renderers.JSONRenderer):
  charset='utf-8'
  def render(self, data, accepted_media_type='application/x-www-form-urlencoded', renderer_context=None):
    print(data)
    response = ''
    if 'ErrorDetail' in str(data):
      response = json.dumps({'errors':data})
    else:
      response = json.dumps(data)
    
    return response