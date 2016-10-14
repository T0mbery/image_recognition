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
  end
  
  version :recognition, from_version: :thumb do
    process :img_recognition
  end
  
  def extension_white_list
    %w(jpg jpeg png)
  end
  
  private

  def img_recognition
    out, err, st = Open3.capture3("python #{Rails.root}/lib/tasks/image_recognition.py #{self.file.file} #{Rails.root}")
    if out.chomp == 'face is not detected'
      raise FaceIsNotDetected
    elsif err.present?
      raise DetectionAlgorithm
    end
  end

end
