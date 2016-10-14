class ImagesController < ApplicationController
  
  def index
    @images = Image.all
  end
  
  def show
  end
  
  def create
    begin
      @image = Image.create(image_params)
    rescue FotoUploader::FaceIsNotDetected
      flash[:notice] = 'Не удалось распознать лицо'
    rescue FotoUploader::DetectionAlgorithm
      flash[:notice] = 'Не удалось распознать контур.'
    end
    redirect_to action: 'index'
  end
  
  def update
    if params[:id] = 'all'
      Image.find_each do |img|
        img.foto.recreate_versions!
      end
    end
  end
  
  def destroy
    @image = Image.find(params[:id])
    @image.destroy
    redirect_to action: 'index'
  end
  
  private

  def image_params
    params.permit(:foto)
  end

end
