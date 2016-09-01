class ImagesController < ApplicationController
  
  def index
    @images = Image.all
  end
  
  def create
    @image = Image.create(image_params)
    redirect_to action: 'index'
  end
  
  def destroy
    @image = Image.find(params[:id])
    @image.destroy
    redirect_to action: 'index'
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
  
  private

  def image_params
    params.permit(:foto)
  end

end
