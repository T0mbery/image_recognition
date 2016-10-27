# encoding: utf-8

class FotoUploader < CarrierWave::Uploader::Base
  include CarrierWave::MiniMagick

  class FaceIsNotDetected  < StandardError; end
  class DetectionAlgorithm < StandardError; end

  storage :file

  process resize_to_fit: [600, 600]
  
  def store_dir
    "uploads/#{model.class.to_s.underscore}/#{mounted_as}/#{model.id}"
  end

  # Provide a default URL as a default if there hasn't been a file uploaded:
  # def default_url
  #   # For Rails 3.1+ asset pipeline compatibility:
  #   # ActionController::Base.helpers.asset_path("fallback/" + [version_name, "default.png"].compact.join('_'))
  #
  #   "/images/fallback/" + [version_name, "default.png"].compact.join('_')
  # end
  
  version :thumb do
    process resize_to_fit: [540, 540]
    # after :store, :detect_gender_and_face
  end
  
  version :recognition, from_version: :thumb do
    process img_recognition: ['colors']
    after :store, :update_data
  end

  version :contour, from_version: :thumb do
    process img_recognition: ['contour']
  end
  
  def extension_white_list
    %w(jpg jpeg png)
  end
  
  private

  def img_recognition(contour)
    out, err, st = Open3.capture3("python #{Rails.root}/lib/tasks/image_recognition.py #{self.file.file} #{Rails.root} #{contour} #{model.foto.thumb.url} #{'http://237190c7.ngrok.io/'}")
    if out.chomp == 'face is not detected'
      raise FaceIsNotDetected
    elsif err.present?
      raise DetectionAlgorithm
    end
    @data = out.chomp
  end
  
  def update_data(file)
    model.update(data: @data)
  end


  # def detect_gender_and_face(file)
  #   raise model.foto.thumb.url.inspect
  #   #TODO для прода заменить 73b8f04f.ngrok.io на root_path
  #   request = Typhoeus::Request.get("http://mkweb.bcgsc.ca/color-summarizer/?url=73b8f04f.ngrok.io/#{foto.recognition.url}&precision=low&json=1")
  #   if request.success?
  #     response = JSON.parse(request.response_body)
  #     response.delete('pixels')
  #     update(colorizer_result: response)
  #   end
  # end

end
