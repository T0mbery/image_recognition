class Image < ApplicationRecord
  mount_uploader :foto, FotoUploader

  validates :foto, presence: true
  
  # after_create :update_colorizer_json
  
  private
  
  # def update_colorizer_json
  #   #TODO для прода заменить 73b8f04f.ngrok.io на root_path
  #   request = Typhoeus::Request.get("http://mkweb.bcgsc.ca/color-summarizer/?url=73b8f04f.ngrok.io/#{foto.recognition.url}&precision=low&json=1")
  #   if request.success?
  #     response = JSON.parse(request.response_body)
  #     response.delete('pixels')
  #     update(colorizer_result: response)
  #   end
  # end
end
