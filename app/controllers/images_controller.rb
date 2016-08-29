class ImagesController < ApplicationController
  
  def index
  end

  def upload
    if image = params[:image]
      @image_path = image.original_filename
      
      File.open(Rails.root.join('app', 'assets', 'images', @image_path), 'wb') do |file|
        file.write(image.read)
      end
    else
      redirect_to action: 'index'
    end
  end
  
end
