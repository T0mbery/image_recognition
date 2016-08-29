class ImagesController < ApplicationController
  
  def index
  end

  def upload
    if image = params[:image]
      image_name           = image.original_filename
      origin_img_path      = Rails.root.join('app', 'assets', 'images', 'origin',      image_name)
      recognition_img_path = Rails.root.join('app', 'assets', 'images', 'recognition', image_name)
      
      File.open(origin_img_path, 'wb') do |file|
        file.write(image.read)
      end
      
      @img_path = 'recognition/' + image_name
      system("python #{Rails.root}/lib/tasks/image_recognition.py #{image_name} #{origin_img_path} #{recognition_img_path}")
    else
      redirect_to action: 'index'
    end
  end

end
